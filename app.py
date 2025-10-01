from flask import Flask, render_template, request, jsonify, session
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_community.chat_models import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from datetime import datetime
import json
import re
from dotenv import load_dotenv
import uuid

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Analytics storage
analytics_file = 'analytics.json'

def load_analytics():
    if os.path.exists(analytics_file):
        with open(analytics_file, 'r') as f:
            return json.load(f)
    return {
        'total_queries': 0,
        'intent_accuracy': [],
        'response_times': [],
        'satisfaction_scores': [],
        'intent_distribution': {
            'billing': 0,
            'technical': 0,
            'account': 0,
            'complaints': 0,
            'general': 0
        }
    }

def save_analytics(analytics_data):
    with open(analytics_file, 'w') as f:
        json.dump(analytics_data, f, indent=2)

# Intent classification patterns
INTENT_PATTERNS = {
    'billing': [
        r'\b(bill|invoice|payment|charge|refund|cost|price|fee|subscription)\b',
        r'\b(paid|pay|owe|balance|credit)\b'
    ],
    'technical': [
        r'\b(not working|error|bug|issue|problem|fix|broken|crash|slow)\b',
        r'\b(install|setup|configure|update|download)\b'
    ],
    'account': [
        r'\b(account|profile|password|login|username|settings|email|security)\b',
        r'\b(reset|change|update|modify|access)\b'
    ],
    'complaints': [
        r'\b(complaint|unhappy|dissatisfied|angry|frustrated|disappointed)\b',
        r'\b(terrible|awful|worst|bad experience|poor service)\b'
    ]
}

def classify_intent(query):
    """Classify user intent with confidence scoring"""
    query_lower = query.lower()
    intent_scores = {}
    
    for intent, patterns in INTENT_PATTERNS.items():
        score = 0
        for pattern in patterns:
            matches = len(re.findall(pattern, query_lower))
            score += matches
        intent_scores[intent] = score
    
    # Get primary intent
    if max(intent_scores.values()) > 0:
        primary_intent = max(intent_scores, key=intent_scores.get)
        confidence = min(intent_scores[primary_intent] / 3.0, 1.0)
    else:
        primary_intent = 'general'
        confidence = 0.5
    
    # Get all intents with score > 0
    detected_intents = [intent for intent, score in intent_scores.items() if score > 0]
    
    return {
        'primary_intent': primary_intent,
        'confidence': round(confidence, 2),
        'all_intents': detected_intents if detected_intents else ['general']
    }

def extract_entities(query):
    """Extract entities from query"""
    entities = {
        'account_numbers': re.findall(r'\b\d{6,12}\b', query),
        'dates': re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', query),
        'emails': re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', query),
        'product_names': re.findall(r'\b(Premium|Basic|Pro|Enterprise|Starter)\b', query, re.IGNORECASE)
    }
    return {k: v for k, v in entities.items() if v}

def get_llm_model():
    """Initialize LLM based on environment configuration"""
    model_type = os.getenv('MODEL_TYPE', 'openai').lower()
    
   
    
    if model_type == 'gemini':
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        return ChatGoogleGenerativeAI(
            model=os.getenv('GEMINI_MODEL', 'gemini-pro'),
            google_api_key=api_key,
            temperature=0.7
        )
    
    elif model_type == 'ollama':
        return ChatOllama(
            model=os.getenv('OLLAMA_MODEL', 'llama2'),
            temperature=0.7,
            base_url=os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
        )
    
    else:
        raise ValueError(f"Unknown MODEL_TYPE: {model_type}")

# Initialize components
try:
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    
    # Load FAISS vector store
    if os.path.exists("faiss_index"):
        vectorstore = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
    else:
        raise FileNotFoundError("FAISS index not found. Please run ingest_documents.py first.")
    
    # Initialize LLM
    llm = get_llm_model()
    
    # Custom prompt template
    custom_prompt = PromptTemplate(
        template="""You are a helpful customer support assistant. Use the following context to answer the question.
        If you don't know the answer, say so politely and offer to connect them with a human agent.
        
        Context: {context}
        
        Chat History: {chat_history}
        
        Question: {question}
        
        Provide a clear, concise, and helpful answer. If the question involves multiple topics, address each one.
        
        Answer:""",
        input_variables=["context", "chat_history", "question"]
    )
    
except Exception as e:
    print(f"Initialization error: {e}")
    vectorstore = None
    llm = None

@app.route('/')
def index():
    # Initialize session
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        session['conversation_history'] = []
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    start_time = datetime.now()
    
    try:
        data = request.json
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Classify intent and extract entities
        intent_info = classify_intent(user_message)
        entities = extract_entities(user_message)
        
        # Initialize memory for this session
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True,
            output_key="answer"
        )
        
        # Load conversation history from session
        if 'conversation_history' in session:
            for msg in session['conversation_history']:
                if msg['role'] == 'user':
                    memory.chat_memory.add_user_message(msg['content'])
                else:
                    memory.chat_memory.add_ai_message(msg['content'])
        
        # Create conversational chain
        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
            memory=memory,
            return_source_documents=True,
            verbose=False
        )
        
        # Get response
        result = qa_chain({"question": user_message})
        bot_response = result['answer']
        source_docs = result.get('source_documents', [])
        
        # Calculate response time
        response_time = (datetime.now() - start_time).total_seconds()
        
        # Update conversation history
        if 'conversation_history' not in session:
            session['conversation_history'] = []
        
        session['conversation_history'].append({
            'role': 'user',
            'content': user_message
        })
        session['conversation_history'].append({
            'role': 'assistant',
            'content': bot_response
        })
        session.modified = True
        
        # Update analytics
        analytics = load_analytics()
        analytics['total_queries'] += 1
        analytics['response_times'].append(response_time)
        analytics['intent_distribution'][intent_info['primary_intent']] += 1
        save_analytics(analytics)
        
        # Prepare response
        response_data = {
            'response': bot_response,
            'intent': intent_info,
            'entities': entities,
            'response_time': round(response_time, 2),
            'sources': [{'content': doc.page_content[:200]} for doc in source_docs[:2]]
        }
        
        return jsonify(response_data)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/feedback', methods=['POST'])
def feedback():
    try:
        data = request.json
        rating = data.get('rating', 0)
        
        analytics = load_analytics()
        analytics['satisfaction_scores'].append(rating)
        save_analytics(analytics)
        
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/analytics')
def analytics():
    try:
        analytics_data = load_analytics()
        
        # Calculate averages
        avg_response_time = sum(analytics_data['response_times']) / len(analytics_data['response_times']) if analytics_data['response_times'] else 0
        avg_satisfaction = sum(analytics_data['satisfaction_scores']) / len(analytics_data['satisfaction_scores']) if analytics_data['satisfaction_scores'] else 0
        
        summary = {
            'total_queries': analytics_data['total_queries'],
            'avg_response_time': round(avg_response_time, 2),
            'avg_satisfaction': round(avg_satisfaction, 2),
            'intent_distribution': analytics_data['intent_distribution']
        }
        
        return jsonify(summary)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/clear', methods=['POST'])
def clear_conversation():
    session['conversation_history'] = []
    session.modified = True
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)