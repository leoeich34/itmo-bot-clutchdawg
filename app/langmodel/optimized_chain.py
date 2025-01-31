# app/langmodel/optimized_chain.py

from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from langchain.vectorstores import FAISS
from app.rag.vector_db import VectorDB
import os

def create_optimized_chain():
    vector_db = VectorDB()
    # Предполагаем, что индекс уже построен
    faiss_index = FAISS.from_embeddings(vector_db.texts, vector_db.embed_model)
    llm = OpenAI(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        model_name=os.getenv("MODEL_NAME"),
        temperature=0.2,
        max_tokens=100,
        request_timeout=30  # Увеличиваем таймаут при необходимости
    )
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=faiss_index.as_retriever(search_kwargs={"k": 5}),
        return_source_documents=True
    )
    return qa

qa_chain = create_optimized_chain()

def generate_response_with_langchain_optimized(query: str, request_id: int) -> ResponseModel:
    result = qa_chain.run(query)
    answer = result['result']
    sources = [doc.metadata['source'] for doc in result['source_documents'][:3]]

    return ResponseModel(
        id=request_id,
        answer=answer,
        reasoning="Ответ сгенерирован на основе предоставленных источников.",
        sources=sources
    )