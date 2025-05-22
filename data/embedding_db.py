from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from dotenv import load_dotenv

import os
import json
import pandas as pd
import openai
import ast 

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

def load_and_preprocess_csv(file_path):
    df = pd.read_csv(file_path)
    documents = []
    
    for _, row in df.iterrows():
        id = row.get("id")
        locations = row.get("locations")
        
        # spec 파싱
        spec_str = row.get("spec", "{}")
        try:
            spec_dict = ast.literal_eval(spec_str)
        except (ValueError, SyntaxError):
            spec_dict = {}

        # 개별 항목 추출
        vcpu_count = spec_dict.get("vcpu_count", "")
        ram = spec_dict.get("ram", "")
        disk = spec_dict.get("disk", "")

        # JSON 형태로 정규화
        json_doc = {
            "vcpu_count": vcpu_count,
            "ram": ram,
            "storage_size": disk,
            "numbers_of_node": row.get("numbers_of_node", "")
        }

        # JSON-like 문자열로 직렬화하여 임베딩용 텍스트 생성
        text_for_embedding = json.dumps(json_doc, ensure_ascii=False)

        metadata = {"id": id, "locations": locations, "source_file": file_path}
        documents.append({"id": id, "locations": locations, "text": text_for_embedding, "metadata": metadata})
    
    return documents


files = [
    "faiss_db/vultr/Filtered_DBaaS_Plans.csv",
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
        save_path = f'faiss_db/vultr/db'
        vector_store.save_local(save_path)
        vector_stores[file] = save_path  # 저장된 경로를 반환값에 추가
    
    return vector_stores  # 반환값 추가


file_faiss_indices = create_faiss_db_by_file(documents_by_file)