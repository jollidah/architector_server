import json
import re
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_openai import ChatOpenAI
from app.core.config import OPENAI_API_KEY, FAISS_PATH, CSV_PATH
from app.core.prompts import SPEC_RECOMMEND_PROMPT, INSTANCE_MATCH_PROMPT, TERRAFORM_GEN_PROMPT
from app.services.retrieval import hybrid_retrieve, sparse_from_documents
from app.services.document_loader import load_documents_for_retrieval, load_faiss_db
from typing import Dict, Any


llm = ChatOpenAI(model="gpt-4-turbo", temperature=0.7, api_key=OPENAI_API_KEY)

def run_chain1(user_input: Dict[str, Any]):
    chain = SPEC_RECOMMEND_PROMPT | llm | StrOutputParser()
    raw_response = chain.invoke({"user_input": json.dumps(user_input, ensure_ascii=False)})
    json_blocks = re.findall(r'```json\s*([\s\S]*?)```', raw_response)
    spec = json.loads(json_blocks[0]) if len(json_blocks) > 0 else {}
    arch = json.loads(json_blocks[1]) if len(json_blocks) > 1 else {}
    return {"spec": spec, "arch": arch}

def run_chain2(llm1_result: dict):
    vector_store = load_faiss_db(FAISS_PATH, "vultr")
    documents = load_documents_for_retrieval(CSV_PATH)
    dense_retriever = vector_store
    sparse_retriever = sparse_from_documents(documents)

    db_region = ""
    storage_region = ""

    if "vultr_database" in llm1_result["arch"]["resources"] and llm1_result["arch"]["resources"]["vultr_database"]:
        db_region = llm1_result["arch"]["resources"]["vultr_database"][0].get("region", "")

    if "vultr_object_storage" in llm1_result["arch"]["resources"] and llm1_result["arch"]["resources"]["vultr_object_storage"]:
        storage_region = llm1_result["arch"]["resources"]["vultr_object_storage"][0].get("region", "")

    query = json.dumps(llm1_result["spec"], ensure_ascii=False)

    context_docs = hybrid_retrieve(query, dense_retriever, sparse_retriever)
    context = [json.dumps({
        "name": doc.metadata.get("name", ""),
        "content": json.loads(doc.page_content),
        "database_region": db_region,
        "storage_region": storage_region
    }, ensure_ascii=False) for doc in context_docs]

    chain = INSTANCE_MATCH_PROMPT | llm | JsonOutputParser()
    result = chain.invoke({
        "context": context,
        "llm1_response": llm1_result["spec"]
    })

    llm1_result["arch"]["resources"]["vultr_instance"][0]["plan"] = result["Instance_name"]
    llm1_result["arch"]["resources"]["vultr_instance"][0]["region"] = result["Region"]
    if "vultr_vpc" in llm1_result["arch"]["resources"] and llm1_result["arch"]["resources"]["vultr_vpc"]:
        llm1_result["arch"]["resources"]["vultr_vpc"][0]["region"] = result["Region"]

    return llm1_result["arch"]


def run_chain3(arch: dict) -> str:
    chain = TERRAFORM_GEN_PROMPT | llm | StrOutputParser()
    tf_code = chain.invoke({"arch_json": arch})
    return tf_code