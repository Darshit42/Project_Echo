import os
import json
import requests
from langchain_openai.embeddings import AzureOpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import gradio as gr
import os
from dotenv import load_dotenv

load_dotenv()

os.environ["AZURE_ENDPOINT"] = os.getenv("AZURE_ENDPOINT")
os.environ["AZURE_DEPLOYMENT"] = os.getenv("AZURE_DEPLOYMENT")
os.environ["OPENAI_API_VERSION"] = os.getenv("OPENAI_API_VERSION")
api_key = os.getenv("AZURE_API_KEY")

embeddings = AzureOpenAIEmbeddings(
    azure_endpoint=os.environ["AZURE_ENDPOINT"],
    azure_deployment=os.environ["AZURE_DEPLOYMENT"],
    openai_api_version=os.environ["OPENAI_API_VERSION"],
    api_key=api_key,
)

pdf_path = "/Users/classplus/Desktop/ChatBot/PST Overview.pdf"
loader = PyPDFLoader(pdf_path)
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
all_splits = text_splitter.split_documents(docs)

vector_store = Chroma.from_documents(documents=all_splits, embedding=embeddings)
retriever_ = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})

def Azure_API_Call(prompt):
    API_KEY = os.getenv("AZURE_API_KEY")
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
    
    Special Handling for Short User Responses:
    
    • If the user responds with:
    
    "Hi" , "Hello", "Hlw", "Hey"  respond naturally by:
    
    1. Hey! How can I help you today?
    
    • "Okay," "Thank you," "thik hai," "Or," "And," or similar brief acknowledgments, respond naturally by:
    
    1. Acknowledging politely ("You're welcome! Let me know if you need anything else.")
    2. Offering further assistance ("Would you like another example?")
    3. Keeping the conversation engaging ("Great! What's next?")
    4. Following up contextually based on the topic of discussion
    
    • Avoid robotic or repetitive responses. Adapt based on the user's intent.
    
    • About PST :
        PST = "Polaris School of Technology"
        who are you = "PST Buddy"
    
    Note : Respond based on the user's language. If the user asks in Hinlish, reply in Hinlish only."""

    response = Azure_API_Call(prompt)
    return response

chat = []

def respond(user_message, context_from_docs, tone):
    bot_reply = pst_buddy(user_message, context_from_docs, tone)
    chat.append((user_message, bot_reply))
    return "", chat 

def clear_chat():
    global chat
    chat = []
    return "", []

with gr.Blocks() as demo:
    gr.Markdown('<div style="text-align:center; font-size:25px; font-weight:bold;">PST Buddy</div>')
    gr.Markdown('<div style="text-align:left; font-size:17px;">Ask me anything about PST.</div>')

    chatbot = gr.Chatbot(height=500)
    
    message = gr.Textbox(placeholder="Type your question here...", label="Your Message")

    send_button = gr.Button("Send")
    clear_button = gr.Button("Clear Chat")

    send_button.click(respond, [message, chatbot], [message, chatbot])  
    message.submit(respond, [message, chatbot], [message, chatbot]) 

    clear_button.click(clear_chat, [], [message, chatbot])

demo.launch(share=True)