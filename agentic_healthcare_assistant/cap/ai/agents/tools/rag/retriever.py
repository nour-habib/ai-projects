from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from .rag import INDEX_DIR

_embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

_store = FAISS.load_local(INDEX_DIR, _embeddings, allow_dangerous_deserialization=True)
_retriever = _store.as_retriever(search_kwargs={"k": 4})

def search_clinic_docs(query: str) -> str:
    docs = _retriever.invoke(query)
    return "\n\n".join(d.page_content for d in docs)

