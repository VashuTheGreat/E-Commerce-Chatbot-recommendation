import os
import torch
import cv2
import logging
from warnings import deprecated
from langchain_core.messages import SystemMessage, AIMessage, HumanMessage
from src.models.agent_models import Orchastrator_Output
from src.llm.llm_loader import llm
from src.prompts import ORCHESTRATOR_SYSTEM_PROMPT, CHAT_LLM_PROMPT
from src.tools.data_fetcher_tool import code_runner
from src.models.agent_models import State
from src.entity.config_entity import ModelTrainingConfig
from src.utils.asyncHandler import asyncHandler
from src.core.dependencies import get_img_transformer, image_encoder_eval
from src.core.dependencies import text_encoder_eval, text_tokenizer
from src.core.dependencies import my_model, vectorizer, df_schema
from src.prompts import ORCHESTRATOR_SYSTEM_PROMPT, CHAT_LLM_PROMPT, COLUMN_DESCRIPTIONS, CATEGORY_COLUMN_HINT
from src.utils.main_utils import analyse_image
tools = [code_runner]

@asyncHandler
async def orchestrator(state: State) -> State:
    logging.info("orchestrator - entered node")
    logging.info(f"orchestrator - input state keys: {list(state.keys())}")
    system_msg = SystemMessage(content=ORCHESTRATOR_SYSTEM_PROMPT)
    image_uploaded = bool(state.get("image_path"))
    img_caption = state.get('img_caption') or ''

    # Build a dedicated context message so the LLM sees image info clearly
    image_context_lines = [f"image_uploaded: {image_uploaded}"]
    if img_caption:
        image_context_lines.append(
            f"image_caption: {img_caption}\n\n"
            "IMPORTANT: An image caption is available. Use EVERY product attribute "
            "(type, color, brand, gender, category, material, style, season, etc.) "
            "from the caption to build a detailed, attribute-rich search query. "
            "Do NOT produce vague queries like 'similar item'."
        )
    image_context_msg = HumanMessage(content="\n".join(image_context_lines))

    messages = [system_msg] + state["messages"] + [image_context_msg]
    logging.info(f"orchestrator - total messages to invoke: {len(messages)}")
    llm_structured = llm.with_structured_output(Orchastrator_Output)
    logging.info("orchestrator - invoking LLM with structured output")
    response = await llm_structured.ainvoke(messages)
    logging.info(f"orchestrator - structured response: {response}")
    output = {
        "redirect_to": response.redirect_to,
        "query_for_db_search": response.querie
    }
    logging.info(f"orchestrator - exiting with output: {output}")
    return output


def _get_image_feat(image_path, config, device):
    logging.info(f"entering _get_image_feat with image_path: {image_path}, device: {device}")
    if not image_path or not os.path.exists(image_path):
        logging.warning(f"image path not provided or does not exist: {image_path}. returning zero features.")
        feat = torch.zeros((1, config.image_feature_output), device=device)
        logging.info(f"exiting _get_image_feat with zero features tensor shape: {feat.shape}")
        return feat
    img = cv2.imread(image_path)
    if img is None:
        logging.warning(f"failed to read image at path: {image_path}. returning zero features.")
        feat = torch.zeros((1, config.image_feature_output), device=device)
        logging.info(f"exiting _get_image_feat with zero features tensor shape: {feat.shape}")
        return feat
    logging.info(f"successfully loaded image from path: {image_path}. image shape: {img.shape}")
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    transforms = get_img_transformer()
    img_tensor = transforms(img).unsqueeze(0).to(device)
    logging.info(f"transformed image into tensor. shape: {img_tensor.shape}, device: {img_tensor.device}")
    image_encoder = image_encoder_eval()
    logging.info("running image encoder forward pass")
    with torch.no_grad():
        img_feat = image_encoder(img_tensor)
    logging.info(f"exiting _get_image_feat with shape: {img_feat.shape}")
    return img_feat

def _get_text_feat(text, config, device):
    logging.info(f"entering _get_text_feat with text: {text}, device: {device}")
    
    text_encoder = text_encoder_eval()
    tokenizer = text_tokenizer()
    tokens = tokenizer(
        text,
        padding="max_length",
        max_length=config.max_len,
        truncation=True,
        return_tensors="pt"
    ).to(device)
    logging.info(f"tokenized text. tokens shape: {tokens['input_ids'].shape}")
    with torch.no_grad():
        txt_feat = text_encoder(tokens["input_ids"], tokens["attention_mask"])
    logging.info(f"exiting _get_text_feat with shape: {txt_feat.shape}")
    return txt_feat



@asyncHandler
async def analyse_image_node(state: State):
    logging.info("entering analyse_image_node")
    image_path = state['image_path']
    logging.info(f"analyse_image_node - current message history length: {len(state['messages'])}")
    caption = await analyse_image(image_path=image_path)
    logging.info(f"analyse_image_node - LLM response received: {caption}")
    # Append caption as an AIMessage so it lives in conversation history.
    # This ensures orchestrator AND chat node always know what image was uploaded,
    # even in follow-up turns where image_path is no longer sent.
    caption_msg = AIMessage(content=f"[Image Analysis] The user uploaded an image. Here is the detailed analysis:\n{caption}")
    return {
        "img_caption": caption,
        "messages": [caption_msg],
    }

@asyncHandler
@deprecated(
    "retreiver_node is deprecated — it uses MyModel.predict_emb which merges image+text into a "
    "single 512-d embedding against a unified index. Use retriever_node_v2 instead, which "
    "queries the dual (image + text) Pinecone indexes separately and fuses with RRF."
)
async def retreiver_node(state: State):
    logging.info("[DEPRECATED] entering retreiver_node")
    query = state.get("query_for_db_search", "")
    logging.info(f"retreiver_node - query for db search: {query}")
    if not query:
        logging.warning("retreiver_node - empty search query. returning empty list.")
        return {"db_res": []}
    config = ModelTrainingConfig()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logging.info(f"retreiver_node - using device: {device}")
    mymodel = my_model()
    logging.info("retreiver_node - loading model checkpoints")
    mymodel.load_model()
    image_path = state.get("image_path")
    logging.info(f"retreiver_node - getting image features for path: {image_path}")
    img_feat = _get_image_feat(image_path, config, device)
    logging.info("retreiver_node - getting text features")
    txt_feat = _get_text_feat(query, config, device)
    logging.info("retreiver_node - predicting multimodal embeddings")
    with torch.no_grad():
        embedding = mymodel.predict_emb(img_feat, txt_feat)
    embedding_list = embedding.squeeze(0).cpu().tolist()
    logging.info(f"retreiver_node - embedding list length: {len(embedding_list)}")
    try:
        logging.info("retreiver_node - initializing vector database connection")
        vec_db = vectorizer()
        top_k = state.get("top_k", 5)
        logging.info(f"retreiver_node - querying vector database for top_k: {top_k}")
        results = await vec_db.get_similar_data(vector=embedding_list, top_k=top_k)
        matches = []
        raw_matches = results.get("matches", [])
        logging.info(f"retreiver_node - found {len(raw_matches)} matches in vector search")
        for match in raw_matches:
            matches.append({
                "id": getattr(match, "id", ""),
                "score": getattr(match, "score", 0.0),
                "metadata": getattr(match, "metadata", {})
            })
        logging.info(f"retreiver_node - returning structured db_res: {matches}")
        return {"db_res": matches}
    except Exception as e:
        logging.error(f"retreiver_node - error during vector query: {e}")
        return {"db_res": []}


@asyncHandler
async def retriever_node_v2(state: State):
    """New dual-index retriever node.

    Uses ``ImageEncoder`` and ``TextEncoder`` directly to obtain separate
    image and text query vectors, then calls ``Vectorizer.invoke()`` which
    internally runs Pinecone queries against the two independent indexes and
    fuses the results with Reciprocal Rank Fusion (RRF).

    If the user has not uploaded an image ``img_vec`` is passed as ``None``
    and the retriever falls back to a text-only search.
    """
    logging.info("entering retriever_node_v2")
    query = state.get("query_for_db_search", "")
    logging.info(f"retriever_node_v2 - query: {query}")
    if not query:
        logging.warning("retriever_node_v2 - empty search query. returning empty list.")
        return {"db_res": []}

    config = ModelTrainingConfig()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    logging.info(f"retriever_node_v2 - using device: {device}")

    # ── text vector (always present) ────────────────────────────────────
    txt_feat = _get_text_feat(query, config, device)  # (1, 768)
    txt_vec: list = txt_feat.squeeze(0).cpu().tolist()
    logging.info(f"retriever_node_v2 - text vector length: {len(txt_vec)}")

    # ── image vector (None when no image uploaded) ──────────────────────
    image_path = state.get("image_path")
    img_vec = None
    if image_path and os.path.exists(image_path):
        img_feat = _get_image_feat(image_path, config, device)  # (1, 2048)
        img_vec = img_feat.squeeze(0).cpu().tolist()
        logging.info(f"retriever_node_v2 - image vector length: {len(img_vec)}")
    else:
        logging.info("retriever_node_v2 - no image provided; img_vec=None (text-only search)")

    try:
        vec_db = vectorizer()
        top_k = state.get("top_k", 5)
        logging.info(f"retriever_node_v2 - querying dual Pinecone indexes. top_k: {top_k}")
        # invoke() -> vec_db.query(img_vec, text_vec, top_k)
        # If img_vec is None  -> text-only query on the text index
        # If both are given   -> RRF fusion of image + text results
        results = await vec_db.invoke(img_vec=img_vec, text_vec=txt_vec, top_k=top_k)
        matches = []
        for match in (results or []):
            if isinstance(match, dict):
                matches.append(match)
            else:
                matches.append({
                    "id": getattr(match, "id", ""),
                    "score": getattr(match, "score", 0.0),
                    "metadata": getattr(match, "metadata", {})
                })
        logging.info(f"retriever_node_v2 - returning {len(matches)} matches")
        return {"db_res": matches}
    except Exception as e:
        logging.error(f"retriever_node_v2 - error during vector query: {e}")
        return {"db_res": []}

@asyncHandler
async def chat(state: State):
    logging.info("entering chat node")
    messages = state["messages"]
    logging.info(f"chat - current message history length: {len(messages)}")
    db_res = state.get("db_res", [])
    logging.info(f"chat - db_res count: {len(db_res)}")
    schema = df_schema()
    schema_block = (
        "\n\nDataset Schema (use these EXACT column names in code_runner):\n"
        f"columns: {schema['columns']}\n"
        f"dtypes: {schema['dtypes']}\n"
        f"shape: {schema['shape']}\n"
        f"sample row: {schema['sample']}\n"
        "Per-column semantics:\n"
        + "\n".join(f"- {col}: {desc}" for col, desc in COLUMN_DESCRIPTIONS.items())
        + "\n"
        "DO NOT guess column names. If a name you expect is absent, "
        "use one of the columns listed above."
        + CATEGORY_COLUMN_HINT
    )
    if db_res:
        retreived_res = []
        for r in db_res:
            if isinstance(r, dict) and "metadata" in r:
                retreived_res.append(str(r["metadata"]))
            elif hasattr(r, "metadata"):
                retreived_res.append(str(r.metadata))
            else:
                retreived_res.append(str(r))
        system_content = (
            f"{CHAT_LLM_PROMPT}{schema_block}\n\nRetrieved product metadata:\n"
            + "\n".join(retreived_res)
        )
        logging.info(f"chat - constructed system prompt with metadata. length: {len(system_content)}")
    else:
        system_content = f"{CHAT_LLM_PROMPT}{schema_block}"
        logging.info("chat - using standard system prompt with dataset schema")

    messages = [SystemMessage(content=system_content)] + messages
    llm_with_tools = llm.bind_tools(tools=tools)
    logging.info("chat - invoking LLM with bound tools")
    response = await llm_with_tools.ainvoke(messages)
    logging.info(f"chat - LLM response received: {response}")
    return {"messages": [response]}
