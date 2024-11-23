import os
import sys
from langchain.chat_models import ChatGoogleGenerativeAI
from langchain.retrievers import FAISSRetriever
from langchain.chains import RetrievalQA

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)),".."))

from model.prompt_templates import get_system_prompt

# Initialize the chat model
def initialize_chat_model():
    return ChatGoogleGenerativeAI(model="gemini-1.5-flash", temperature=0.1, max_output_tokens=8192)

# Function to create the retrieval QA chain
def create_retrieval_qa(retriever):
    chat_model = initialize_chat_model()
    system_prompt = get_system_prompt()
    
    # Use LangChain's RetrievalQA to handle the response generation
    qa_chain = RetrievalQA(
        model=chat_model,
        retriever=retriever,
        system_prompt=system_prompt
    )
    return qa_chain

# Function to handle querying
def query_tender(question):
    # Load the retriever based on FAISS database
    retriever = FAISSRetriever.load_local("data/vector_store")
    
    # Create the QA chain
    qa_chain = create_retrieval_qa(retriever)
    
    # Query the model
    response = qa_chain.run({"user_query": question})
    return response
