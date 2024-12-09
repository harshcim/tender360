import os
import sys
import streamlit as st  # type: ignore
from langchain_google_genai import ChatGoogleGenerativeAI # type: ignore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import google.generativeai as genai # type: ignore
from dotenv import load_dotenv # type: ignore
from langchain.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS # type: ignore
from langchain.chains import RetrievalQA

sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

# from model.query_system import query_tender
from utils.data_utils import load_data, split_data, save_embeddings
from utils.file_utils import save_uploaded_file, list_uploaded_files



# Load environment variables0
load_dotenv()   
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    
rag_model = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0.5, max_output_tokens=8192)


from log.logger import setup_logger
from core.processor import process_tender_document





# Define LLM and RAG components
def load_embeddings_data(index_embedding):
    
    embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")
    
    db = FAISS.load_local(index_embedding, embeddings, allow_dangerous_deserialization=True)
    
    return db




def chat_with_tender_interface(base_dir, uploaded_file):

    # Display currently uploaded files
    st.subheader("Uploaded Files")
    uploaded_files = list_uploaded_files()

    if uploaded_files:
        st.write("Currently available files in the directory:")
        for file in uploaded_files:
            st.write(f"- {file}")
    else:
        st.write("No files currently uploaded.")

    
    index_embedding = os.path.join(base_dir, "..", "data", "vector_store.faiss")

    index_path = os.path.join(base_dir, "..", "data", "vector_store.faiss", "index.faiss")
    

    # File upload handling
    if uploaded_file:
        save_uploaded_file(uploaded_file)
        st.success(f"File '{uploaded_file.name}' has been uploaded and stored.")

        # Trigger background processing if embeddings don't already exist
        if not os.path.exists(index_path):
            with st.spinner("Processing your files..."):
                documents = load_data()
                if documents:
                    text_chunks = split_data(documents)
                    save_embeddings(text_chunks)
                    st.success("You can now query the data.")
                else:
                    st.warning("No valid documents found to process.")
    else:
        st.write("Upload a file to create a knowledge base.")


    

    if os.path.exists(index_path):
        # If vector database exists, proceed with querying
        rag_prompt = """ 
        You are a specialized assistant for analyzing tender documents with a focus on keyword identification and relevant content extraction. Your main goal is to answer user queries about the presence of specific keywords or provide brief explanations if requested. Make sure to adhere strictly to the user’s query and provide accurate answers based only on the content of the uploaded tender documents.

        Guidelines for Responding to Queries:

        1. **Keyword Mapping**:
            - If the user asks if a specific keyword (technical or non-technical) is present in the document, search only for that keyword.
            - If the keyword is found, confirm its presence and provide a brief context (one or two sentences) where it appears in the document.
            - If the keyword is not found, clearly state that the keyword is not present in the document. Do not include any unrelated content.
            - Avoid retrieving any additional content that is not directly related to the user's keyword query.

        2. **Brief Explanations & Document Information**:
            - If the user requests a summary, tender title, timeline chart, or specific brief information, provide a concise and relevant answer based on the requested content.
            - Keep the response short and to the point. Use bullet points if the explanation involves multiple items.

        3. **Response Tone and Relevance**:
            - Keep your responses precise, concise, and user-friendly.
            - If the user's query is out of the context of the tender documents, gently ask them to refocus their question on the provided content.
            - Base all responses strictly on the content of the tender document. Avoid any speculation or inclusion of external information.

        Response Format Guidelines:
            - **Bullet Points**: Use bullet points for clarity when listing multiple details or points.
            - **Direct Answers**: Provide direct answers if the query is about the presence or absence of specific keywords.
            - **Keep It Concise**: Stick to brief and relevant responses, maintaining focus on the user’s question.

        Context: \n{context}\n
        Question: \n{question}\n
        """
        
        prompt = PromptTemplate(template=rag_prompt, input_variables=["context", "question"])

        
        db = load_embeddings_data(index_embedding)
        
        
        qa_chain = RetrievalQA.from_chain_type(
            llm=rag_model,
            chain_type="stuff",
            retriever=db.as_retriever(search_kwargs={"k": 5}),
            return_source_documents=True,
            chain_type_kwargs={"prompt": prompt},
        )

        # Query input box
        question = st.text_input("Ask a question related to the tender documents:")

        if question:
            with st.spinner("Fetching response..."):
                response = qa_chain.invoke({"query": question})
                st.write(response['result'])
    else:
        # If vector database does not exist, prompt the user to upload content
        st.warning("No Knowledgebase found. Please upload document.")