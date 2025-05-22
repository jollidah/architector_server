import pandas as pd
import json
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

def load_faiss_db(folder_path: str):
    embedding_model = OpenAIEmbeddings()
    vector_store = FAISS.load_local(
        f"{folder_path}",
        embeddings=embedding_model,
        allow_dangerous_deserialization=True
    )
    return vector_store

def load_documents_for_retrieval_instance(csv_path: str):
    df = pd.read_csv(csv_path)
    documents = []

    for _, row in df.iterrows():
        json_doc = {
            "vcpu_count": row.get("vcpu_count", ""),
            "ram": row.get("ram", ""),
            "storage": row.get("disk", ""),
            "bandwidth": row.get("bandwidth", ""),
            "storage_type": row.get("storage_type", "")
        }
        page_content = json.dumps(json_doc, ensure_ascii=False)
        metadata = {"id": row.get("id"), "locations": row.get("locations")}
        documents.append(Document(page_content=page_content, metadata=metadata))

    return documents

def load_documents_for_retrieval_db(csv_path: str):
    df = pd.read_csv(csv_path)
    documents = []

    for _, row in df.iterrows():
        json_doc = {
            "vcpu_count": row.get("vcpu_count", ""),
            "ram": row.get("ram", ""),
            "storage": row.get("disk", ""),
            "number_of_node": row.get("number_of_node", "")
        }
        page_content = json.dumps(json_doc, ensure_ascii=False)
        metadata = {"id": row.get("id"), "locations": row.get("locations")}
        documents.append(Document(page_content=page_content, metadata=metadata))

    return documents

def load_documents_for_retrieval_object_storage(csv_path: str):
    df = pd.read_csv(csv_path)
    documents = []

    for _, row in df.iterrows():
        json_doc = {
            "ratelimit_ops_secs": row.get("ratelimit_ops_secs", ""),
            "ratelimit_ops_bytes": row.get("ratelimit_ops_bytes", "")
        }
        page_content = json.dumps(json_doc, ensure_ascii=False)
        metadata = {"cluster_id": row.get("cluster_id"),"tier_id": row.get("tier_id"), "location": row.get("city")}
        documents.append(Document(page_content=page_content, metadata=metadata))

    return documents
