import os
import torch
import cv2
import logging
from langchain_core.messages import SystemMessage
from src.models.agent_models import Orchastrator_Output
from src.llm.llm_loader import llm
from src.prompts import ORCHESTRATOR_SYSTEM_PROMPT, CHAT_LLM_PROMPT
from src.tools.data_fetcher_tool import code_runner
from src.models.agent_models import State
from src.components.vectorizing_data import Vectorizer
from src.entity.model import MyModel
from src.entity.config_entity import ModelTrainingConfig
from src.models.muti_model import ImageEncoder, TextEncoder
from src.utils.asyncHandler import asyncHandler

tools = [code_runner]

@asyncHandler
async def orchestrator(state: State) -> State:
    logging.info("orchestrator - entered node")
    system_msg = SystemMessage(content=ORCHESTRATOR_SYSTEM_PROMPT)
    messages = [system_msg] + state["messages"]
    llm_structured = llm.with_structured_output(Orchastrator_Output)
    logging.info("orchestrator - invoking LLM with structured output")
    response = await llm_structured.ainvoke(messages)
    logging.info(f"Orchestrator Output {response}")
    return {
        "redirect_to": response.redirect_to,
        "query_for_db_search": response.querie
    }

def _get_image_feat(image_path, config, device):
    if not image_path or not os.path.exists(image_path):
        return torch.zeros((1, config.image_feature_output), device=device)
    img = cv2.imread(image_path)
    if img is None:
        return torch.zeros((1, config.image_feature_output), device=device)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    from torchvision.transforms import v2
    transforms = v2.Compose([
        v2.ToImage(),
        v2.ToDtype(torch.float32, scale=True),
        v2.Resize(size=(224, 224), antialias=True),
        v2.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    img_tensor = transforms(img).unsqueeze(0).to(device)
    image_encoder = ImageEncoder(config).to(device).eval()
    with torch.no_grad():
        img_feat = image_encoder(img_tensor)
    return img_feat

def _get_text_feat(text, config, device):
    from transformers import AutoTokenizer
    text_encoder = TextEncoder(config).to(device).eval()
    tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-mpnet-base-v2")
    tokens = tokenizer(
        text,
        padding="max_length",
        max_length=config.max_len,
        truncation=True,
        return_tensors="pt"
    ).to(device)
    with torch.no_grad():
        txt_feat = text_encoder(tokens["input_ids"], tokens["attention_mask"])
    return txt_feat

@asyncHandler
async def retreiver_node(state: State):
    logging.info("Entered in the retreiver node")
    query = state.get("query_for_db_search", "")
    if not query:
        return {"db_res": []}
    config = ModelTrainingConfig()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    mymodel = MyModel(config)
    mymodel.load_model()
    img_feat = _get_image_feat(state.get("image_path"), config, device)
    txt_feat = _get_text_feat(query, config, device)
    with torch.no_grad():
        embedding = mymodel.predict_emb(img_feat, txt_feat)
    embedding_list = embedding.squeeze(0).cpu().tolist()
    try:
        vec_db = Vectorizer()
        results = await vec_db.get_similar_data(vector=embedding_list, top_k=state.get("top_k", 5))
        matches = []
        for match in results.get("matches", []):
            matches.append({
                "id": getattr(match, "id", ""),
                "score": getattr(match, "score", 0.0),
                "metadata": getattr(match, "metadata", {})
            })
        return {"db_res": matches}
    except Exception as e:
        logging.error(f"Retriever error: {e}")
        return {"db_res": []}

@asyncHandler
async def chat(state: State):
    logging.info("Chat node initiated")
    messages = state["messages"]
    db_res = state.get("db_res", [])
    if db_res:
        retreived_res = []
        for r in db_res:
            if isinstance(r, dict) and "metadata" in r:
                retreived_res.append(str(r["metadata"]))
            elif hasattr(r, "metadata"):
                retreived_res.append(str(r.metadata))
            else:
                retreived_res.append(str(r))
        system_content = f"{CHAT_LLM_PROMPT}\n\nRetrieved product metadata:\n" + "\n".join(retreived_res)
    else:
        system_content = f"{CHAT_LLM_PROMPT}"
    messages = [SystemMessage(content=system_content)] + messages
    llm_with_tools = llm.bind_tools(tools=tools)
    logging.info(f"Invoking LLM with tools")
    response = await llm_with_tools.ainvoke(messages)
    return {"messages": [response]}
