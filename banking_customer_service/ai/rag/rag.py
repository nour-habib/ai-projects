import os
from dotenv import load_dotenv
from pathlib import Path
import numpy as np
from openai import OpenAI

load_dotenv()

client = OpenAI()
doc_dir = Path(__file__).parent / "documents"


class RAGApi():
    def __init__(self):
        self.model = os.getenv("EMBEDDING_MODEL", "text-embedding-3-small")
        self.files = sorted(doc_dir.glob("*.md"))
        self.texts = [f.read_text() for f in self.files]
        self.names = [f.stem for f in self.files]
        self.vectors_array = None
        self.vectorize()

    def vectorize(self):
        resp = client.embeddings.create(model=self.model, input=self.texts)
        self.vectors_array = np.array([d.embedding for d in resp.data])

    def retrieval(self, query: str, k: int):
        if self.vectors_array is None:
            raise RuntimeError("Call vectorize() first")

        resp = client.embeddings.create(model=self.model, input=[query])
        q = np.array(resp.data[0].embedding)

        sims = (self.vectors_array @ q) / (
            np.linalg.norm(self.vectors_array, axis=1) * np.linalg.norm(q)
        )

        top_k = np.argsort(sims)[::-1][:k]
        if sims[top_k[0]] < 0.3:
            return []
        return [self.texts[i] for i in top_k]
