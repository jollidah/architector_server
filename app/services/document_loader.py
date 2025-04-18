import pandas as pd
import json
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

def load_faiss_db(folder_path: str, index_name: str):
    embedding_model = OpenAIEmbeddings()
    vector_store = FAISS.load_local(
        f"{folder_path}/{index_name}",
        embeddings=embedding_model,
        allow_dangerous_deserialization=True
    )
    return vector_store

def load_documents_for_retrieval(csv_path: str):
    df = pd.read_csv(csv_path)
    documents = []

    for _, row in df.iterrows():
        json_doc = {
            "Processor / vCPU": row.get("Processor / Cores", ""),
            "GPU": row.get("GPU", ""),
            "GPU type": row.get("GPU type", ""),
            "Memory": row.get("Memory", ""),
            "Storage": row.get("Storage", ""),
            "Bandwidth": row.get("Bandwidth", "")
        }
        page_content = json.dumps(json_doc, ensure_ascii=False)
        metadata = {"name": row.get("Name", "Unknown")}
        documents.append(Document(page_content=page_content, metadata=metadata))

    return documents
