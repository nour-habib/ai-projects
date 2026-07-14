
from pathlib import Path

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

load_dotenv()

BASE_DIR = Path(__file__).parent
DOCS_DIR = BASE_DIR / "corpus"
INDEX_DIR = str(BASE_DIR / "storage" / "clinic_ops_faiss")

#chunk
#split at headers makred by #

headers_to_split_on = [
    ("#", "title"),
    ("##", "section"),
    ("###", "subsection"),
]

markdown_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=headers_to_split_on
)

chunk_splitter = RecursiveCharacterTextSplitter(
    chunk_size=700,
    chunk_overlap=120,
)

if __name__ == "__main__":
    docs = []

    for path in DOCS_DIR.glob("*.md"):
        markdown_text = path.read_text(encoding="utf-8")

        header_docs = markdown_splitter.split_text(markdown_text)

        for doc in header_docs:
            doc.metadata["source"] = path.name
            doc.metadata["category"] = path.stem
            doc.metadata["doc_query"] = "clinic_ops"

        docs.extend(header_docs)

    chunks = chunk_splitter.split_documents(docs)

    # vectorize
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vector_store = FAISS.from_documents(chunks, embeddings)
    vector_store.save_local(INDEX_DIR)
    print(f"Built FAISS index with {len(chunks)} chunks at {INDEX_DIR}")