import os
os.environ['KMP_DUPLICATE_LIB_OK']='True'
import re
import pandas as pd

from haystack.utils import launch_es
launch_es()

from haystack.document_stores import ElasticsearchDocumentStore



# Get the host where Elasticsearch is running, default to localhost
host = os.environ.get("ELASTICSEARCH_HOST", "localhost")
elastic_document_store = ElasticsearchDocumentStore(host=host, username="", password="", index="document-dim-2", similarity="cosine", embedding_dim=384)



from haystack.nodes import EmbeddingRetriever

embedding_retriever = EmbeddingRetriever(
    document_store=elastic_document_store,
    embedding_model="sentence-transformers/all-MiniLM-L6-v2",
    model_format="sentence_transformers",
)

# Print number of documents
print(f"Number of documents: {elastic_document_store.get_document_count()}")


from haystack.nodes import FARMReader
model = "deepset/roberta-base-squad2"
reader = FARMReader(model, use_gpu=True)

# from haystack.pipelines import ExtractiveQAPipeline
# pipeline = ExtractiveQAPipeline(reader, bm25_retriever)

from haystack.pipelines import ExtravtiveQAPipeline
pipeline = ExtravtiveQAPipeline(reader, embedding_retriever)

query = "how to create purchase order?"
result = pipeline.run(query=query, params={"Retriever": {"top_k": 10}, "Reader": {"top_k": 10}})


from fastapi import FastAPI

app = FastAPI()


@app.get("/query")
async def root(q):
    return pipeline.run(query=q)