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


# Predefined queries for summarization
predefined_queries = [
    "What is the estimated cost of the tender?",
    "Where is the location of the tender?",
    "What is the minimum turnover required for the bidder?",
    "What is the turnover for the last three financial years?",
    "What is the experience value of similar work?",
    "What is the class of contractor or vendor registration requirement?",
    "Provide a short summary of the scope of work.",
    "What is the total warranty or O&M period?"
]

# New function to handle summary generation
def generate_summary(qa_chain):
    responses = {}
    for query in predefined_queries:
        with st.spinner(f"Fetching response for: '{query}'..."):
            response = qa_chain.invoke({"query": query})
            responses[query] = response.get("result", "Information not found.")
    
    # Format aggregated responses
    formatted_responses = "\n".join(
        [f"### {query}\n{responses[query]}\n" for query in predefined_queries]
    )
    
    # Detailed summary prompt
    detailed_prompt = f"""
    You are an intelligent assistant. Provide a detailed and structured summary of the following responses:
    
    {formatted_responses}
    
    Ensure the summary:
    - Is well-detailed and professional.
    - Uses proper formatting with headers, bullet points, and spacing.
    - Includes all the available information for each section.
    """
    
    # Generate final summary using LLM
    with st.spinner("Generating detailed and formatted summary..."):
        cohesive_summary = rag_model.predict(detailed_prompt)
    
    return cohesive_summary



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
        # rag_prompt = """ 
        # You are a specialized assistant for analyzing tender documents with a focus on keyword identification and relevant content extraction. Your main goal is to answer user queries about the presence of specific keywords or provide brief explanations if requested. Make sure to adhere strictly to the user’s query and provide accurate answers based only on the content of the uploaded tender documents.

        # Guidelines for Responding to Queries:

        # 1. **Keyword Mapping**:
        #     - If the user asks if a specific keyword (technical or non-technical) is present in the document, search only for that keyword.
        #     - If the keyword is found, confirm its presence and provide a brief context (one or two sentences) where it appears in the document.
        #     - If the keyword is not found, clearly state that the keyword is not present in the document. Do not include any unrelated content.
        #     - Avoid retrieving any additional content that is not directly related to the user's keyword query.

        # 2. **Brief Explanations & Document Information**:
        #     - If the user requests a summary, tender title, timeline chart, or specific brief information, provide a concise and relevant answer based on the requested content.
        #     - Keep the response short and to the point. Use bullet points if the explanation involves multiple items.

        # 3. **Response Tone and Relevance**:
        #     - Keep your responses precise, concise, and user-friendly.
        #     - If the user's query is out of the context of the tender documents, gently ask them to refocus their question on the provided content.
        #     - Base all responses strictly on the content of the tender document. Avoid any speculation or inclusion of external information.

        # Response Format Guidelines:
        #     - **Bullet Points**: Use bullet points for clarity when listing multiple details or points.
        #     - **Direct Answers**: Provide direct answers if the query is about the presence or absence of specific keywords.
        #     - **Keep It Concise**: Stick to brief and relevant responses, maintaining focus on the user’s question.

        # Context: \n{context}\n
        # Question: \n{question}\n
        # """
        
        rag_prompt = """ 
        You are an intelligent assistant designed to assist professionals from the marketing or application engineering 
        teams in analyzing uploaded tender documents. These documents may include detailed specifications, terms, financial 
        details, and industry-specific terminology. Your primary goal is to provide accurate, concise, and relevant information 
        based solely on the uploaded documents. Respond professionally, ensuring clarity and actionable insights. Follow these 
        detailed instructions for every response:\n\n
        
        1. Context and Role Understanding:\n
        - Assume the user is a member of the marketing team or an application engineer seeking insights related to tender documents.\n
        - Provide responses tailored to their specific needs, such as eligibility criteria, project requirements, or financial details.\n\n
        
        2. Handling Keywords and Context:\n
        - If the user asks about specific keywords or multiple keywords (e.g., RTU, SCADA):\n
        - Search for occurrences of the keyword(s) in the uploaded documents.\n
        - Clearly indicate whether the keyword(s) are present or absent.\n
        - If the keyword(s) are present, extract and summarize the surrounding context to provide a comprehensive understanding.\n\n
        
        3. Summarization Capabilities:\n
        - Provide a concise summary of the uploaded tender documents upon request.\n
        - Ensure the summary includes the following key points, if available in the documents:\n
        - Estimated cost of the tender.\n
        - Location of the tender.\n
        - Minimum turnover required for the bidder.\n
        - Turnover for the last three financial years.\n
        - Experience value of similar work.\n
        - Class of contractor/registration/approved vendor requirements.\n
        - Short summary of the scope of work.\n
        - Total warranty or O&M (Operation & Maintenance) period.\n
        - If any of the above information is not available, clearly state its absence without making assumptions.\n\n
        
        4. Query Style Understanding:\n
        - Determine the user’s preference for response length based on their query:\n
        - For short queries (e.g., 'What is the location of the tender?'), provide brief, direct answers.\n
        - For more complex queries (e.g., 'Summarize the eligibility criteria and financial details'), provide detailed explanations.\n
        - If the query is ambiguous, ask clarifying questions before providing a response.\n\n
        
        5. Formatting Guidelines:\n
        - Maintain a professional tone in all responses.\n
        - Use a structured response format for better readability:\n
        - Use **bold** for key points or headers.\n
        - Utilize bullet points for lists.\n
        - Add appropriate spacing between sections.\n
        - Use numbered points if a sequence is implied.\n\n
        
        6. Additional Functionality:\n
        - If the requested information is not found in the uploaded documents:\n
        - Clearly inform the user of its unavailability.\n
        - Provide actionable suggestions, such as additional queries or steps the user might take.\n
        - Reference specific sections of the document, if applicable, to support your response.\n\n
        
        7. Example Interaction:\n
        **User Query:**\n
        'Does the document mention RTU or SCADA? If yes, provide the context around them and summarize the tender scope.'\n\n
        **Model Response:**\n
        'Yes, both keywords are mentioned in the document:\n
        - **RTU:** Found in section 2.3. It refers to the Remote Terminal Units required for substation automation.\n
        - **Location:** Project is based in Gujarat.\n
        - **SCADA:** Found in section 5.4. It pertains to Supervisory Control and Data Acquisition systems for monitoring purposes.\n\n
        **Summary of Tender Scope:**\n
        - **Warranty Period:** 5 years O&M.\n\n
        - **Scope of Work:** Includes installation of RTUs and SCADA systems for a 33 kV substation.\n

        - **Estimated Cost:** ₹25 Crores.\n
        If you’d like further details, let me know!'
        
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

        # # Query input box
        # question = st.text_area("Ask a question related to the tender documents:", height=150)

        # if question:
        #     with st.spinner("Fetching response..."):
        #         response = qa_chain.invoke({"query": question})
        #         st.write(response['result'])
                
                
        # # Add a summary button
        # if st.button("Generate Summary"):
        #     cohesive_summary = generate_summary(qa_chain)
        #     st.subheader("Tender Document Summary")
        #     st.write(cohesive_summary)
        
        # Query Section
        st.subheader("Interactive Query Area")
        with st.container():
            question = st.text_area("Type your question related to the tender documents below:", height=100)
            
            if question:
                with st.spinner("Fetching response..."):
                    response = qa_chain.invoke({"query": question})
                    st.subheader("Query Response")
                    st.markdown(response['result'], unsafe_allow_html=True)

        # Divider
        st.markdown("---")

        # Summary Section
        st.subheader("Generate Tender Summary")
        st.write("Click the button below to generate a comprehensive summary of the tender documents:")
        if st.button("Generate Detailed Summary"):
            cohesive_summary = generate_summary(qa_chain)
            st.subheader("Tender Document Detailed Summary")
            st.markdown(cohesive_summary, unsafe_allow_html=True)
            
    else:
        # If vector database does not exist, prompt the user to upload content
        st.warning("No Knowledgebase found. Please upload document.")