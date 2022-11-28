
import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'
import re
import pandas as pd
# import requests

from haystack.utils import launch_es
launch_es()

from haystack.document_stores import ElasticsearchDocumentStore


# Load the Dataset that has been extracted
data = pd.read_csv("data_with_text.csv")

# Most of the document contains the 'Previous  JavaScript must be enabled to correctly display this content'. So, we have removed it.
# Convert the document to lower case and remove the trailing spaces.
# Remove the HTML Tags
processed_data = []

for item in data.text_data:
  if "Previous  JavaScript must be enabled to correctly display this content" in item:
    item = item.replace("Previous  JavaScript must be enabled to correctly display this content", "")
  item = item.strip()
  item = item.lower()
  sentence = re.sub("<.*?>", " ", item)
  processed_data.append(item)

data["processed_data"] = processed_data

# Converting the data format for haystack document store.
docs = []
for _, row in data.iterrows():
  docs.append({"content" : row["processed_data"], "meta": {"name": row["name"], "tags": row["tags"]}})
# Define the elastic search document store
import os
from haystack.document_stores import ElasticsearchDocumentStore

# # Get the host where Elasticsearch is running, default to localhost
# host = os.environ.get("ELASTICSEARCH_HOST", "localhost")
# elastic_document_store = ElasticsearchDocumentStore(host=host, username="", password="", index="document-dim", similarity="cosine")



# Get the host where Elasticsearch is running, default to localhost
host = os.environ.get("ELASTICSEARCH_HOST", "localhost")
elastic_document_store = ElasticsearchDocumentStore(host=host, username="", password="", index="document-dim-2", similarity="cosine", recreate_index=True, embedding_dim=384)

elastic_document_store.write_documents(docs)
print(f"Loaded {elastic_document_store.get_document_count()} documents")


# Define the BM25 Retriever
# from haystack.nodes import BM25Retriever

# bm25_retriever = BM25Retriever(elastic_document_store)

from haystack.nodes import EmbeddingRetriever

embedding_retriever = EmbeddingRetriever(
    document_store=elastic_document_store,
    embedding_model="sentence-transformers/all-MiniLM-L6-v2",
    model_format="sentence_transformers",
)

elastic_document_store.update_embeddings(embedding_retriever)


from haystack.nodes import FARMReader
model = "deepset/roberta-base-squad2"
reader = FARMReader(model, use_gpu=True)

# from haystack.pipelines import ExtractiveQAPipeline
# pipeline = ExtractiveQAPipeline(reader, bm25_retriever)

from haystack.pipelines import ExtractiveQAPipeline
pipeline = ExtractiveQAPipeline(reader, embedding_retriever)

query = "how to create purchase order?"
result = pipeline.run(query=query, params={"Retriever": {"top_k": 10}, "Reader": {"top_k": 10}})


from fastapi import FastAPI

app = FastAPI()


@app.get("/query")
async def root(q):
    return pipeline.run(query=q)