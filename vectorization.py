import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

try:
    # Load all PDF documents
    files = [f for f in os.listdir('Files') if f.endswith('.pdf')]
    documents = []
    for file in files:
        file_name = os.path.join('Files', file)
        loader = PyPDFLoader(file_name)
        documents.extend(loader.load())
    print('Documents Loaded!\nStarting Text-Splitting....')

    # Split the documents into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True
    )
    documentsChunk = text_splitter.split_documents(documents)
    print('Text-Splitting Completed!\nStarting Vectorization....')

    # Create vector store with embeddings
    embedding = OllamaEmbeddings(model='llama3.2')
    vector_store_name = 'knowledge_base_db'
    vector_store = Chroma.from_documents(
        documents=documentsChunk,
        embedding=embedding,
        persist_directory=vector_store_name
    )
    print(f'Vectorization Completed!\nVector Store: {vector_store_name} created.')

except Exception as e:
    print('Error: ', str(e))
