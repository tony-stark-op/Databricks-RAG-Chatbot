import os
from dotenv import load_dotenv
from langchain_ollama import OllamaEmbeddings, ChatOllama
# from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate, \
    MessagesPlaceholder
from langchain_core.runnables import RunnableWithMessageHistory
from langchain_community.chat_message_histories import SQLChatMessageHistory
from sqlalchemy import create_engine
import uuid

# Load ENV file
load_dotenv(dotenv_path='.env', override=True)

# Create LLM object
llm = ChatOllama(
    base_url='http://localhost:11434',
    model='qwen2.5:7b',
    temperature=0.7,
    max_tokens=5000
)

'''llm = ChatGoogleGenerativeAI(
    model='gemini-2.0-flash',
    api_key=os.getenv('GEMINI_API_KEY'),
    temperature=0.7,
    max_tokens=5000
)'''

# Defile embedding function
embeddings = OllamaEmbeddings(
    model='llama3.2'
)

# Define the path of vector store
vector_store = Chroma(
    persist_directory='./knowledge_base_db',
    embedding_function=embeddings
)

# Create SQL DB to store ChatMessageHistory
engine = create_engine(os.getenv('DATABASE_URL'))


# Function to retrieve session history
def getSessionHistory(session_id):
    return SQLChatMessageHistory(
        session_id=session_id,
        connection=engine
    )


# Get session id for new session
def getSessionID():
    return str(uuid.uuid4())


def generateResponse(input_query,
                     session_id,
                     vector_store_details=vector_store,
                     model=llm):
    # Setup retriever and get the relevant information to user query
    try:
        retriever = vector_store_details.as_retriever(
            search_type='similarity',
            search_kwargs={'k': 5}
        )
        ragResponseDocs = retriever.get_relevant_documents(input_query)
        ragResponse = '\n\n'.join([doc.page_content for doc in ragResponseDocs])

        # Create prompt template
        systemMessage = SystemMessagePromptTemplate.from_template("""
        You are a helpful and professional Storage Admin Engineer.

        Your job is to assist users with technical issues specifically related to the Enterprise Storage domain, 
        including but not limited to: 
        - SAN (Storage Area Network) 
        - NAS (Network Attached Storage) 
        - Storage provisioning, performance, and troubleshooting

        Use the provided incident history and internal KB articles to solve the user's problem. If relevant data is 
        unavailable, politely guide the user to contact IT support.

        📧 IT Support Email: itsupport@xyz.com

        ❗ Important: 
        - If the question is unrelated to enterprise storage or the Storage Admin role, politely decline 
        to answer and kindly request the user to ask questions relevant to this domain. 
        ❗ Important:
        - Format your answer in the following 4 stages:
            1. **Explanation of the Issue**
            2. **Reason Behind the Issue**
            3. **Proposed Solution**
            4. **Future Enhancements or Best Practices**
        - Maintain a concise, clear, and respectful tone in all responses.
        """)

        humanMessage = HumanMessagePromptTemplate.from_template("""
        Here is the context gathered to help answer the user's question:
        {ragResponse}
        Now, here is the user's question:
        {input_query}
        """)

        promptTemplate = ChatPromptTemplate.from_messages([
            systemMessage,
            MessagesPlaceholder('history'),
            humanMessage
        ])

        # Create chain to run the model with RAG
        chain = promptTemplate | model | StrOutputParser()

        # Create Runnable to store history
        history = RunnableWithMessageHistory(
            chain,
            getSessionHistory,
            input_messages_key='input_query',
            history_messages_key='history'
        )

        # Invoke the chain and evaluate response

        # response = history.invoke({'ragResponse': ragResponse, 'input_query': input_query},
        #                          config={'configurable': {'session_id': session_id}})
        # return response

        for response in history.stream({'ragResponse': ragResponse, 'input_query': input_query},
                                       config={'configurable': {'session_id': session_id}}):
            yield response

    except Exception as e:
        print('Error in generateResponse: ', e)
        return str(e)
