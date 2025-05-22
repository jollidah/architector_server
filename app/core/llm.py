import json
import re
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_openai import ChatOpenAI
from app.core.config import OPENAI_API_KEY, INSTANCE_FAISS_PATH, INSTANCE_CSV_PATH, DB_FAISS_PATH, DB_CSV_PATH, OBJECT_STORAGE_FAISS_PATH, OBJECT_STORAGE_CSV_PATH
from app.core.prompts import SPEC_RECOMMEND_PROMPT, INSTANCE_MATCH_PROMPT, DB_MATCH_PROMPT, ARCH_PROMPT
from app.services.retrieval import hybrid_retrieve, sparse_from_documents
from app.services.document_loader import  load_faiss_db, load_documents_for_retrieval_instance, load_documents_for_retrieval_db, load_documents_for_retrieval_object_storage
from typing import Dict, Any
from app.models.schemas import FinalArchitectureResponse


llm = ChatOpenAI(model="gpt-4-turbo", temperature=0.7, api_key=OPENAI_API_KEY)

def clean_json_string(json_str: str) -> str:
    cleaned = re.sub(r',\s*(?=[}\]])', '', json_str)
    return cleaned


def run_chain1(user_input: Dict[str, Any], retries: int = 3):
    chain = SPEC_RECOMMEND_PROMPT | llm | StrOutputParser()
    raw_response = chain.invoke({"user_input": json.dumps(user_input, ensure_ascii=False)})
    json_blocks = re.findall(r'```json\s*([\s\S]*?)```', raw_response)

    
    spec, db_spec, object_storage_spec = {}, {}, {}

    if len(json_blocks) > 0:
        try:
            spec = json.loads(clean_json_string(json_blocks[0]))
        except json.JSONDecodeError as e:
            print("spec JSON 파싱 오류:", e)

    if len(json_blocks) > 1:
        try:
            db_spec = json.loads(clean_json_string(json_blocks[1]))
        except json.JSONDecodeError as e:
            print("db_spec JSON 파싱 오류:", e)
    
    if len(json_blocks) > 2:
        try:
            object_storage_spec = json.loads(clean_json_string(json_blocks[2]))
        except json.JSONDecodeError as e:
            print("object_storage_spec JSON 파싱 오류:", e)

    if not isinstance(spec, list):
        spec = [spec]
    
    return {"spec": spec, "db_spec": db_spec, "object_storage_spec": object_storage_spec}


def process_instance_specifications(instance_specs: list, location: str,
                                    dense_retriever, sparse_retriever) -> list:
    all_top3_per_spec = []

    for instance_spec in instance_specs:
        parsed_instance_spec = {
            k: int(v) if k in {"vcpu_count", "ram", "storage_size", "bandwidth", "storage_type"} and isinstance(v, str) and v.isdigit() else v
            for k, v in instance_spec.items()
        }

        instance_query = json.dumps(parsed_instance_spec, ensure_ascii=False)
        instance_context_docs = hybrid_retrieve(instance_query, dense_retriever, sparse_retriever, user_location=location)

        context = [json.dumps({
            "id": doc.metadata.get("id", ""),
            "content": json.loads(doc.page_content)
        }, ensure_ascii=False) for doc in instance_context_docs]

        chain = INSTANCE_MATCH_PROMPT | llm | JsonOutputParser()
        raw_response = chain.invoke({
            "context": context,
            "llm1_response": instance_spec
        })

        top3 = raw_response["Recommended_Instances"]
        all_top3_per_spec.append(top3)

    return all_top3_per_spec


def run_chain2(llm1_result: dict, location: str) -> dict:
    # 로드
    instance_vector_store = load_faiss_db(INSTANCE_FAISS_PATH)
    instance_documents = load_documents_for_retrieval_instance(INSTANCE_CSV_PATH)
    instance_dense_retriever = instance_vector_store
    instance_sparse_retriever = sparse_from_documents(instance_documents, location)

    db_vector_store = load_faiss_db(DB_FAISS_PATH)
    db_documents = load_documents_for_retrieval_db(DB_CSV_PATH)
    db_dense_retriever = db_vector_store
    db_sparse_retriever = sparse_from_documents(db_documents, location)

    all_top3_per_spec = []
    
    
    if "instance_specifications" in llm1_result.get("spec", {}):
        # 각 스펙별로 context → LLM 호출 → top 3 추천
        instance_specs = llm1_result.get("spec", {}).get("instance_specifications", {})
        all_top3_per_spec = process_instance_specifications(
            instance_specs, location,
            instance_dense_retriever, instance_sparse_retriever
        )
    else:
        instance_specs = llm1_result.get("spec", [])
        all_top3_per_spec = process_instance_specifications(
            instance_specs, location,
            instance_dense_retriever, instance_sparse_retriever
        )
    
    transposed_plans = list(zip(*all_top3_per_spec))    
    
    # db
    db_spec_items = [v for k, v in llm1_result.get("db_spec", {}).items() if k.startswith("db_spec")]
    db_plans = []

    for db_spec in db_spec_items:
        parsed_db_spec = {
            k: int(v) if k in {"vcpu_count", "ram", "storage_size", "number_of_node"} and isinstance(v, str) and v.isdigit() else v
            for k, v in db_spec.items()
        }

        db_query = json.dumps(parsed_db_spec, ensure_ascii=False)
        db_context_docs = hybrid_retrieve(db_query, db_dense_retriever, db_sparse_retriever, user_location=location)

        context = [json.dumps({
            "id": doc.metadata.get("id", ""),
            "content": json.loads(doc.page_content)
        }, ensure_ascii=False) for doc in db_context_docs]

        chain = DB_MATCH_PROMPT | llm | JsonOutputParser()
        raw_response = chain.invoke({
            "context": context,
            "llm1_response": db_spec
        })

        db_rec = raw_response["DB_plan"]
        db_plans.append(db_rec)

    return {
        "instance_plans": transposed_plans,
        "db_plans": db_plans
    }


def run_chain3(user_input: Dict[str, Any], llm1_result: dict, llm2_result: dict, location: str) -> FinalArchitectureResponse:
    
    object_storage_vector_store = load_faiss_db(OBJECT_STORAGE_FAISS_PATH)
    object_storage_documents = load_documents_for_retrieval_object_storage(OBJECT_STORAGE_CSV_PATH)
    object_storage_dense_retriever = object_storage_vector_store
    object_storage_sparse_retriever = sparse_from_documents(object_storage_documents, location)
    arch_chain = ARCH_PROMPT | llm | JsonOutputParser()
    
    parsed_db_spec = {
        k: int(v) if k in {"ratelimit_ops_secs", "ratelimit_ops_bytes"} and isinstance(v, str) and v.isdigit() else v
        for k, v in llm1_result.get("object_storage_spec", {}).items()
    }

    object_storage_query = json.dumps(parsed_db_spec, ensure_ascii=False)
    object_storage_context_docs = hybrid_retrieve(object_storage_query, object_storage_dense_retriever, object_storage_sparse_retriever, k=9, user_location=None)

    arch_chain = ARCH_PROMPT | llm | JsonOutputParser()

    context = [json.dumps({
        "cluster_id": doc.metadata.get("cluster_id", ""),
        "tier_id": doc.metadata.get("tier_id", ""),
        "location": doc.metadata.get("location", ""),
        "content": json.loads(doc.page_content)
    }, ensure_ascii=False) for doc in object_storage_context_docs]    
    
    recs = []

    for i in range(3):
        llm2_subset = {
            "Instance_plan": llm2_result["instance_plans"][i],
            "DB_plan": llm2_result["db_plans"]
        }

        raw_response = arch_chain.invoke({
            "object_storage_spec": context,
            "user_input": user_input,
            "user_location": location,
            "llm2_result": llm2_subset
        })
        
        print(raw_response)
        recs.append(raw_response)

    return FinalArchitectureResponse(
        rec1=recs[0],
        rec2=recs[1],
        rec3=recs[2]
    )