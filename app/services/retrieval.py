from collections import defaultdict
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from typing import List

def sparse_from_documents(documents: List[Document], k: int = 5):
    retriever = BM25Retriever.from_documents(documents)
    retriever.k = k
    return retriever

def hybrid_retrieve(query: str, dense_retriever, sparse_retriever, alpha=0.5, k=3):
    dense_results = dense_retriever.similarity_search_with_score(query, k=k)
    sparse_results = sparse_retriever.invoke(query)

    combined_scores = defaultdict(float)
    doc_map = {}

    for doc, score in dense_results:
        key = doc.page_content
        combined_scores[key] += alpha * (1 - score)
        doc_map[key] = doc

    for doc in sparse_results:
        key = doc.page_content
        combined_scores[key] += (1 - alpha)
        doc_map[key] = doc

    top_docs = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)[:k]
    return [doc_map[doc_text] for doc_text, _ in top_docs]
