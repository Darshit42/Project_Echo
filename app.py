from flask import Flask, jsonify, request, render_template
import os
import requests
from langchain_openai.embeddings import AzureOpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Initialize Flask app
app = Flask(__name__)

# Set up environment variables
os.environ["AZURE_ENDPOINT"] = "endpoint"
os.environ["AZURE_DEPLOYMENT"] = "text-embedding-3-large"
os.environ["OPENAI_API_VERSION"] = "2023-05-15"
api_key = "api"

# Define functions before Flask routes
embeddings = AzureOpenAIEmbeddings(
    azure_endpoint=os.environ["AZURE_ENDPOINT"],
    azure_deployment=os.environ["AZURE_DEPLOYMENT"],
    openai_api_version=os.environ["OPENAI_API_VERSION"],
    api_key=api_key,
)

pdf_path = "./templates/PST.pdf"
loader = PyPDFLoader(pdf_path)
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
all_splits = text_splitter.split_documents(docs)

vector_store = Chroma.from_documents(documents=all_splits, embedding=embeddings)
retriever_ = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})

# Function to call the Azure API
def Azure_API_Call(prompt):
    API_KEY = "80667380fac648cda0b315db8effcd5b"
    headers = {
        "Content-Type": "application/json",
        "api-key": API_KEY,
    }

    payload = {
        "messages": [
            {"role": "system", "content": "Your name is PST Buddy. You are supposed to answer all student queries related to Polaris School of Technology."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 4000
    }

    ENDPOINT = "https://open-ai-end-point.openai.azure.com/openai/deployments/open_ai_21aug/chat/completions?api-version=2024-02-15-preview"

    try:
        response = requests.post(ENDPOINT, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content'].strip()
    except requests.exceptions.RequestException as e:
        print(f"An error occurred during the Azure OpenAI API call: {e}")
        return "Oops! Something went wrong. Please try again later."

# Main Chatbot Function
def pst_buddy(question, context_from_docs, tone):
    tone = """
    You are a friendly and approachable assistant with a warm, conversational tone. Respond in a professional but engaging manner, using clear and concise language. Avoid slang or excessive emojis, and focus on being empathetic, helpful, and polite. Ensure your responses sound natural and human-like, as if you were talking to a friend or colleague, while maintaining a professional attitude. Be informative and polite, addressing the user's query to the best of your ability with a warm tone.

    Important: Always respond in the same language as the user's question. If the user asks in English, reply in English. If the question is in another language, respond accordingly.
    """
    context_from_docs = ""
    for doc in retriever_.get_relevant_documents(question):
        content = doc.page_content.replace('\n', ' ')
        context_from_docs += ' ' + content

    prompt = f"""
    Use the following retrieved documents to answer the question clearly, concisely, and accurately. Always give the output in the same language of question asked. 
    Give the output in the {tone} tone and engaging manner. 

    Retrieved Context:
    {context_from_docs}

    Question: 
    {question}
    
    Important:  
    1. Avoid saying "I don't know," "The retrieved documents do not explicitly state," or similar uncertain phrases.
    2. If the information is unclear, provide a best possible answer based on what is available, without indicating a lack of knowledge.
    3. Focus on giving a precise and useful answer, even if it's not 100% complete. 
    """
    
    response = Azure_API_Call(prompt)
    return response

# Flask Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_response', methods=['POST'])
def get_response():
    user_message = request.json.get('message')
    context_from_docs = ""  # You can use the logic to retrieve context from docs if needed
    tone = "Your preferred tone here"
    
    response = pst_buddy(user_message, context_from_docs, tone)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)
