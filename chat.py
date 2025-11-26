from main import get_response
from langchain_community.vectorstores.faiss import FAISS
from langgraph.graph import StateGraph, START, END
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from typing import Annotated, List, Any
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
import pickle

conn = sqlite3.connect("checkpoint1.db", check_same_thread=False)
cursor = conn.cursor()



conn.commit()

memory = SqliteSaver(conn)

class State(BaseModel):
    user_query: str = Field(default=None)
    image_json_summary: dict = Field(default=None)
    llm_query: str = Field(default=None)
    db_res: List[dict] = Field(default_factory=list)
    summary: str = Field(default=None)

def image_json(state: State, config):
    thread_id = config["configurable"]["thread_id"]
    r = None
    try:
        with open(f"./tempImage/{thread_id}.pkl", "rb") as f:
            r = pickle.load(f)
    except:
        try:
            with open(f"./tempImage/{thread_id}.jpg", "rb") as f:
                image_bytes = f.read()
            r = get_response(image_bytes)
            
            with open(f"./tempImage/{thread_id}.pkl", "wb") as f:
                pickle.dump(r, f)
        except FileNotFoundError:
             r = {"error": "Image not found"}

    return {"image_json_summary": r}

def chat_llm(state: State):
    parser = StrOutputParser()
    llm = ChatGroq(model="llama-3.1-8b-instant")
    prompt = PromptTemplate(
        template="""
You are an expert product-query generator for a fashion search engine.

Given:
1. user_query
2. image_json_summary with attributes: name, color, pattern, type_style, gender

Generate a structured search query in this format:
name: ... | color: ... | type_style: ... | category_or_gender: ...

Ignore attributes that do not exist.
Output only the search query.

User Query: {user_query}
Image JSON: {image_json_summary}
""",
        input_variables=["user_query", "image_json_summary"]
    )
    chain = prompt | llm | parser
    r = chain.invoke({"user_query": state.user_query, "image_json_summary": state.image_json_summary})
    return {"llm_query": r}

def llm_q_db(state: State):
    try:
        vector_db = pickle.load(open("./data/db.pkl", "rb"))
        results = vector_db.similarity_search(state.llm_query, k=3)

        clean = []
        for item in results:
            clean.append({
                "page_content": item.page_content,
                "metadata": item.metadata
            })

        return {"db_res": clean}
    except Exception as e:
        print(f"Error querying DB: {e}")
        return {"db_res": []}
    

def summary(state:State):
    prompt="you are a selling assisten you are given with a json type of data summerise the content in natural language and ask the user that do you need any other thing i can help you with"

    parser = StrOutputParser()
    llm = ChatGroq(model="llama-3.1-8b-instant")
    chain=llm|parser
    r=chain.invoke(f"{prompt} state data: {str(state)}")
    return {"summary":r}
graph = StateGraph(State)
graph.add_node("image_json", image_json)
graph.add_node("chat_llm", chat_llm)
graph.add_node("llm_q_db", llm_q_db)
graph.add_node("summary", summary)


graph.add_edge(START, "image_json")
graph.add_edge("image_json", "chat_llm")
graph.add_edge("chat_llm", "llm_q_db")
graph.add_edge("llm_q_db", "summary")
graph.add_edge("summary", END)


graph = graph.compile(checkpointer=memory)

import ormsgpack

def get_thread_history(thread_id):
    cursor = conn.cursor()
    cursor.execute("""
        SELECT checkpoint, type
        FROM checkpoints
        WHERE thread_id = ?
        ORDER BY checkpoint_id ASC;
    """, (thread_id,))
    rows = cursor.fetchall()

    history = []
    for row in rows:
        try:
            blob, type_ = row
            if type_ == "msgpack":
                ckpt = ormsgpack.unpackb(blob)
            elif type_ == "pickle":
                ckpt = pickle.loads(blob)
            else:
                ckpt = pickle.loads(blob)

            if "channel_values" in ckpt:
                history.append(ckpt["channel_values"])
            elif "state" in ckpt:
                history.append(ckpt["state"])
            else:
                history.append(ckpt)
        except Exception as e:
            print(f"Error loading history checkpoint: {e}")
            pass
    return history

def response(thread_id, query):
    r = graph.invoke(
        {"user_query": query},
        config={"configurable": {"thread_id": thread_id}}
    )
    return r

if __name__ == "__main__":
    r=response("1", "show me the similar products")
    print(r)
    pass
