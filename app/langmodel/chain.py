# app/langmodel/chain.py

from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from langchain.vectorstores import FAISS
from app.rag.vector_db import VectorDB
from app.langmodel.llm import _call_chatgpt

def get_chain():
    vector_db = VectorDB()
    # Предполагаем, что индекс уже построен и сохранен
    faiss_index = FAISS(vector_db.embed_model, vector_db.texts)
    llm = OpenAI(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        model_name=os.getenv("MODEL_NAME"),
        temperature=0.2,
        max_tokens=100
    )
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=faiss_index.as_retriever(),
        return_source_documents=True
    )
    return qa_chain

qa_chain = get_chain()

def generate_response_with_langchain(query: str, request_id: int) -> ResponseModel:
    result = qa_chain.run(query)
    answer = result['result']
    sources = [doc.metadata['source'] for doc in result['source_documents'][:3]]

    return ResponseModel(
        id=request_id,
        answer=answer,
        reasoning="Ответ сгенерирован на основе предоставленных источников.",
        sources=sources
    )