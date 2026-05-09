import os
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

_XLSX = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "Dataset.xlsx")

_texts: list[str] = []
_vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
_matrix = None


def _load() -> None:
    global _texts, _matrix
    if _matrix is not None:
        return
    df = pd.read_excel(_XLSX)
    _texts = df["text"].dropna().astype(str).tolist()
    _matrix = _vectorizer.fit_transform(_texts)


def retrieve(query: str) -> list[str]:
    _load()
    scores = cosine_similarity(_vectorizer.transform([query]), _matrix).flatten()
    top = np.argsort(scores)[-3:][::-1]

    results = []
    for i in top:
        if scores[i] > 0.05:
            results.append(_texts[i])

    return results
