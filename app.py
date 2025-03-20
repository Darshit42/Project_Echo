import os
import requests
import asyncio
import httpx
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from langchain_openai.embeddings import AzureOpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()

app = Flask(__name__)

AZURE_ENDPOINT = os.getenv("AZURE_ENDPOINT")
AZURE_DEPLOYMENT = os.getenv("AZURE_DEPLOYMENT")
OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION")
AZURE_API_KEY = os.getenv("AZURE_API_KEY")
AZURE_CHAT_ENDPOINT = os.getenv("AZURE_CHAT_ENDPOINT")

embeddings = AzureOpenAIEmbeddings(
    azure_endpoint=AZURE_ENDPOINT,
    azure_deployment=AZURE_DEPLOYMENT,
    openai_api_version=OPENAI_API_VERSION,
    api_key=AZURE_API_KEY,
)

try:
    pdf_path = "./templates/PST.pdf"
    loader = PyPDFLoader(pdf_path)
    docs = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=20)
    all_splits = text_splitter.split_documents(docs)

    vector_store = Chroma.from_documents(documents=all_splits, embedding=embeddings)
    retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 2})

except Exception as e:
    raise RuntimeError(f"Error loading documents: {e}")

async def azure_api_call(prompt):
    """
    Asynchronous API call to Azure OpenAI to reduce blocking time.
    """
    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_API_KEY,
    }

    payload = {
        "messages": [
            {"role": "system", "content": "Your name is PST Buddy. You assist students with queries related to Polaris School of Technology."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.5,  
        "max_tokens": 1500 
    }

    try:
        response = await client.post(AZURE_CHAT_ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content'].strip()
    except httpx.RequestError as e:
        print(f"Azure API call failed: {e}")
        return "Oops! Something went wrong. Please try again later."

async def pst_buddy(question):
    """
    Retrieves relevant document context and generates a response using Azure API.
    """
    retrieved_context = " ".join([doc.page_content.replace("\n", " ") for doc in retriever.get_relevant_documents(question)])

    prompt = f"""
    Use the retrieved documents below to answer the question clearly and accurately.
    Maintain a warm, professional tone.

    Retrieved Context:
    {retrieved_context}

    Question: 
    {question}

    Important:
    1. Avoid saying "I don't know" or "The retrieved documents do not explicitly state."
    2. If information is unclear, provide the best possible answer based on available data.
    3. Focus on precision and usefulness, even if the answer is incomplete.
    """

    return await azure_api_call(prompt)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
async def get_response():
    user_message = request.json.get('message')
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400

    response = await pst_buddy(user_message)
    return jsonify({'response': response})

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
