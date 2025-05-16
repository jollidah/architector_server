from collections import defaultdict
from langchain_community.retrievers import BM25Retriever
from langchain_core.documents import Document
from typing import List

def sparse_from_documents(documents: List[Document], user_location=None, k: int = 9):
    if user_location:
        filtered_documents = []
        for doc in documents:
            locations_str = doc.metadata.get("locations") or ""
            location_list = [loc.strip() for loc in locations_str.split(",") if loc.strip()]
            if user_location in location_list:
                filtered_documents.append(doc)
        
        # fallback: 아무 문서도 없으면 전체 문서 사용
        if not filtered_documents:
            print(f"[WARN] No documents matched user_location='{user_location}'. Using all documents.")
            filtered_documents = documents
    else:
        filtered_documents = documents

    retriever = BM25Retriever.from_documents(filtered_documents)
    retriever.k = k
    return retriever



# def hybrid_retrieve(query: str, query_location: str, dense_retriever, sparse_retriever, alpha=0.5, k=3):    
#     dense_results = dense_retriever.similarity_search_with_score(query, k=k)
#     sparse_results = sparse_retriever.invoke(query)

#     combined_scores = defaultdict(float)
#     doc_map = {}

#     for doc, score in dense_results:
#         key = doc.page_content
#         combined_scores[key] += alpha * (1 - score)
#         doc_map[key] = doc

#     for doc in sparse_results:
#         key = doc.page_content
#         combined_scores[key] += (1 - alpha)
#         doc_map[key] = doc

#     top_docs = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)[:k]
#     return [doc_map[doc_text] for doc_text, _ in top_docs]


def hybrid_retrieve(query: str, dense_retriever, sparse_retriever, user_location=None, alpha=0.5, k=3):
    def is_location_matched(doc):
        if user_location is None:
            return True
        locations = doc.metadata.get("locations", "") or ""
        return user_location in [loc.strip() for loc in locations.split(",")]

    # Initial dense retrieval
    dense_results = dense_retriever.similarity_search_with_score(query, k=10)
    sparse_results = sparse_retriever.invoke(query)

    # Filter location-matched dense results
    matching_dense_docs = [doc for doc, _ in dense_results if is_location_matched(doc)]

    # Fallback: increase dense k if needed
    if len(matching_dense_docs) < 3:
        dense_results = dense_retriever.similarity_search_with_score(query, k=k * 2)

    combined_scores = defaultdict(float)
    doc_map = {}

    # Score dense results with unique keys
    for i, (doc, score) in enumerate(dense_results):
        if not is_location_matched(doc):
            continue
        key = f"dense_{i}"
        combined_scores[key] += alpha * (1 - score)
        doc_map[key] = doc

    # Score sparse results with unique keys
    for i, doc in enumerate(sparse_results):
        if not is_location_matched(doc):
            continue
        key = f"sparse_{i}"
        combined_scores[key] += (1 - alpha)
        doc_map[key] = doc

    # Get top k by combined score
    top_docs = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)[:k]
    return [doc_map[key] for key, _ in top_docs]