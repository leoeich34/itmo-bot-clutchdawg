# app/langmodel/improved_rag_pipeline.py

import os
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.llms import OpenAI
from langchain.docstore.document import Document


def chunk_text(text: str, source_url: str, chunk_size: int = 200, overlap: int = 50):
    """
    Разбивает текст на чанки фиксированного размера с перекрытием.
    Возвращает список объектов Document (из langchain.docstore.document),
    где каждый Document содержит 'page_content' и метаданные 'source'.
    """
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(Document(page_content=chunk, metadata={"source": source_url}))
        start = end - overlap  # перекрытие между чанками
    return chunks


def create_improved_rag_pipeline(documents):
    """
    Создаёт RAG-пайплайн с использованием LangChain.

    :param documents: Список объектов Document.
    :return: Настроенную RetrievalQA цепочку.
    """
    # Используем модель эмбеддингов на базе SentenceTransformer
    embedding_model_name = "sentence-transformers/all-MiniLM-L6-v2"
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)

    # Создаем FAISS векторное хранилище на основе документов
    vectorstore = FAISS.from_documents(documents, embeddings)

    # Настраиваем LLM для генерации кратких ответов (до 2 предложений)
    llm = OpenAI(
        openai_api_key=os.getenv("OPENAI_API_KEY"),
        model_name="gpt-3.5-turbo",
        temperature=0.2,
        max_tokens=100  # достаточно для краткого ответа
    )

    # Создаем цепочку RetrievalQA, которая достаёт 3 наиболее релевантных документа
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",  # можно экспериментировать с другими типами цепочек
        retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
        return_source_documents=True
    )
    return qa_chain


if __name__ == "__main__":
    sample_text = (
        "Университет ИТМО — один из ведущих технических вузов России. "
        "Главный музей Университета ИТМО хранит уникальные экспонаты, связанные с историей университета. "
        "Экспозиция музея регулярно обновляется и включает работы современных художников. "
        "Научно-исследовательская деятельность университета признана во всем мире."
    )
    source_url = "https://itmo.ru/ru/"

    # Разбиваем текст на чанки
    documents = chunk_text(sample_text, source_url, chunk_size=100, overlap=20)

    # Создаем RAG-пайплайн
    qa_chain = create_improved_rag_pipeline(documents)

    # Пример запроса
    query = "Как называется главный музей Университета ИТМО?"
    result = qa_chain({"query": query})

    print("Ответ:", result["result"])
    print("Источники:")
    for doc in result["source_documents"]:
        print("-", doc.metadata.get("source", "Нет источника"))