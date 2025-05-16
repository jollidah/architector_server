from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

import os
import json
import pandas as pd
import openai

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

def load_and_preprocess_csv(file_path):
    df = pd.read_csv(file_path)
    documents = []
    
    for _, row in df.iterrows():
        cluster_id = row.get("cluster_id")
        tier_id = row.get("tier_id")
        location = row.get("city")

        # 개별 항목 추출
        vcpu_count = df.get("vcpu_count", "")
        ram = df.get("ram", "")
        disk = df.get("disk", "")

        # JSON 형태로 정규화
        json_doc = {
            "ratelimit_ops_secs": row.get("ratelimit_ops_secs", ""),
            "ratelimit_ops_bytes": row.get("ratelimit_ops_bytes", "")
        }

        # JSON-like 문자열로 직렬화하여 임베딩용 텍스트 생성
        text_for_embedding = json.dumps(json_doc, ensure_ascii=False)

        metadata = {"cluster_id": cluster_id ,"tier_id": tier_id, "location": location, "source_file": file_path}
        documents.append({"cluster_id": cluster_id ,"tier_id": tier_id, "location": location, "text": text_for_embedding, "metadata": metadata})
    
    return documents


files = [
    "faiss_db/vultr/cluster_tier_mappings_with_city.csv",
]

documents_by_file = {file: load_and_preprocess_csv(file) for file in files}

def create_faiss_db_by_file(documents_by_file):
    embedding_model = OpenAIEmbeddings()
    vector_stores = {}

    for file, docs in documents_by_file.items():
        vector_store = FAISS.from_texts(
            [doc["text"] for doc in docs],
            embedding_model,
            metadatas=[doc["metadata"] for doc in docs]
        )
        save_path = f'faiss_db/vultr/object_storage'
        vector_store.save_local(save_path)
        vector_stores[file] = save_path  # 저장된 경로를 반환값에 추가
    
    return vector_stores  # 반환값 추가


file_faiss_indices = create_faiss_db_by_file(documents_by_file)