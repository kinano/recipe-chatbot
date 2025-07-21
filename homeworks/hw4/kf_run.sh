un run python

from backend import retrieval
from pathlib import Path

recipes_path = Path('homeworks/hw4/data/processed_recipes.json')
index_path = Path('homeworks/hw4/data/bm25_index.pkl')
retriever = retrieval.create_retriever(recipes_path=recipes_path, index_path=index_path)


print(retriever.retrieve_bm25("chicken"))