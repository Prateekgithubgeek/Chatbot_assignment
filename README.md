# 🤖 Intelligent Customer Support Chatbot with RAG

A comprehensive AI-powered customer support chatbot built with LangChain, Flask, and FAISS. This system uses Retrieval-Augmented Generation (RAG) to provide accurate, context-aware responses to customer queries.

## 📋 Table of Contents
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Testing Examples](#testing-examples)
- [Analytics Dashboard](#analytics-dashboard)
- [API Endpoints](#api-endpoints)


## ✨ Features

### Part 1: Intent Classification
- **Multi-intent recognition**: Billing, Technical, Account, Complaints, General
- **Entity extraction**: Account numbers, dates, emails, product names
- **Confidence scoring**: Provides confidence levels for each classification
- **Multi-intent handling**: Detects and handles multiple intents in single message

### Part 2: Knowledge Base Integration (RAG)
- **FAISS vector store**: Fast similarity search for document retrieval
- **Semantic search**: Understanding context beyond keyword matching
- **Document chunking**: Efficient text splitting for better retrieval
- **Source attribution**: Shows which documents were used for answers
- **Multiple knowledge domains**: Billing, Technical, Account, General FAQs

### Part 3: Conversation Management
- **Multi-turn conversations**: Maintains context across messages
- **Session management**: Separate conversation history per user
- **Memory integration**: Uses LangChain's ConversationBufferMemory
- **Clarifying questions**: Asks for clarification when needed
- **Graceful fallbacks**: Offers human agent connection when uncertain

### Part 4: Analytics & Improvement
- **Real-time metrics**: Query count, response times, satisfaction scores
- **Intent distribution**: Tracks which intents are most common
- **User feedback**: Star rating system for responses
- **Performance monitoring**: Response time analytics
- **Continuous learning**: Data collection for model improvement

## 🏗️ Architecture

```
┌─────────────┐
│   User UI   │
│  (Browser)  │
└──────┬──────┘
       │
       ↓
┌──────────────────────────────────────┐
│         Flask Application            │
│  ┌────────────────────────────────┐  │
│  │  Intent Classification         │  │
│  │  - Pattern Matching            │  │
│  │  - Entity Extraction           │  │
│  │  - Confidence Scoring          │  │
│  └────────────────────────────────┘  │
│                                       │
│  ┌────────────────────────────────┐  │
│  │  RAG Pipeline (LangChain)      │  │
│  │  ┌──────────────────────────┐  │  │
│  │  │ Query Processing         │  │  │
│  │  └──────────────────────────┘  │  │
│  │  ┌──────────────────────────┐  │  │
│  │  │ Vector Search (FAISS)    │  │  │
│  │  │ - Semantic Retrieval     │  │  │
│  │  │ - Top-K Documents        │  │  │
│  │  └──────────────────────────┘  │  │
│  │  ┌──────────────────────────┐  │  │
│  │  │ LLM Generation           │  │  │
│  │  │ - OpenAI / Gemini        │  │  │
│  │  │         │  │  │
│  │  └──────────────────────────┘  │  │
│  └────────────────────────────────┘  │
│                                       │
│  ┌────────────────────────────────┐  │
│  │  Conversation Memory           │  │
│  │  - Session Management          │  │
│  │  - Context Tracking            │  │
│  └────────────────────────────────┘  │
│                                       │
│  ┌────────────────────────────────┐  │
│  │  Analytics Engine              │  │
│  │  - Metrics Collection          │  │
│  │  - Performance Tracking        │  │
│  └────────────────────────────────┘  │
└───────────────────────────────────────┘
         │              │
         ↓              ↓
┌────────────────┐  ┌──────────────┐
│  FAISS Index   │  │  Analytics   │
│  (Vector DB)   │  │  JSON Store  │
└────────────────┘  └──────────────┘
```

## 🛠️ Tech Stack

- **Backend**: Flask (Python web framework)
- **LLM Framework**: LangChain (Orchestration)
- **Vector Database**: FAISS (Facebook AI Similarity Search)
- **Embeddings**: HuggingFace Sentence Transformers
- **LLM Options**:
  
  - Google Gemini Pro (Free tier available)

- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Session Management**: Flask Sessions

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip package manager
- Git

### Step 1: Clone the Repository
```bash
git clone <your-repository-url>
cd customer-support-chatbot
```

### Step 2: Create Virtual Environment
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Create Required Directories
```bash
mkdir -p knowledge_base templates
```

### Step 5: Add Knowledge Base Documents
Create `.txt` files in the `knowledge_base/` directory:
- `billing.txt`
- `technical.txt`
- `account.txt`
- `general.txt`

(Sample documents are provided in the repository)

### Step 6: Create FAISS Index
```bash
python ingest_documents.py
```

This will:
- Load all documents from `knowledge_base/`
- Split them into chunks
- Create embeddings
- Build and save FAISS vector store

Expected output:
```
Loading documents...
Loaded: billing.txt
Loaded: technical.txt
Loaded: account.txt
Loaded: general.txt
Loaded 4 documents
Splitting documents into chunks...
Created 152 chunks
Creating embeddings (this may take a few minutes)...
Creating FAISS vector store...
Saving vector store...
✓ Vector store created and saved successfully!
```

## ⚙️ Configuration

### Environment Variables

Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

Edit `.env` with your configuration:


#### Option 2: Using Google Gemini (Free)
```bash
MODEL_TYPE=gemini
GOOGLE_API_KEY=your-google-api-key-here
GEMINI_MODEL=gemini-pro
SECRET_KEY=your-random-secret-key
```

Get free API key: https://makersuite.google.com/app/apikey



## 🚀 Usage

### Start the Application
```bash
python app.py
```

The server will start at `http://localhost:5000`

### Access the Chatbot
Open your browser and navigate to:
```
http://localhost:5000
```

## 📁 Project Structure

```
customer-support-chatbot/
├── app.py                      # Main Flask application
├── ingest_documents.py         # Knowledge base ingestion script
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── .env                       # Your environment variables (create this)
├── README.md                  # This file
├── analytics.json             # Analytics data storage
├── templates/
│   └── index.html            # Frontend UI
├── knowledge_base/           # Knowledge base documents
│   ├── billing.txt
│   ├── technical.txt
│   ├── account.txt
│   └── general.txt
└── faiss_index/              # FAISS vector store (generated)
    ├── index.faiss
    └── index.pkl
```

## 🧪 Testing Examples

### Example 1: Billing Query
**User Input:**
```
I was charged twice for my subscription on account 123456789
```

**Expected Response:**
- Intent: `billing` (high confidence)
- Entities: Account number `123456789`
- Answer: Information about duplicate charges and refund process
- Sources: Billing FAQ documents

### Example 2: Technical Issue
**User Input:**
```
The app keeps crashing when I try to login and I'm getting an error message
```

**Expected Response:**
- Intent: `technical` (high confidence)
- Multiple topics detected: crashes, login, errors
- Answer: Troubleshooting steps for login and crash issues
- Sources: Technical support documents

### Example 3: Account Management
**User Input:**
```
How do I reset my password and enable two-factor authentication?
```

**Expected Response:**
- Intent: `account` (high confidence)
- Multiple intents: password reset, 2FA setup
- Answer: Step-by-step instructions for both tasks
- Sources: Account management documents

### Example 4: Multiple Intents
**User Input:**
```
I'm very frustrated because my payment failed and now the app won't open
```

**Expected Response:**
- Primary intent: `complaints`
- Secondary intents: `billing`, `technical`
- Answer: Empathetic response addressing both issues
- Sources: Multiple document categories

### Example 5: General Query
**User Input:**
```
What integrations do you support?
```

**Expected Response:**
- Intent: `general`
- Answer: List of supported integrations
- Sources: General information documents

## 📊 Analytics Dashboard

### Access Analytics
Click the "📈 Analytics" button in the chat interface or navigate to:
```
http://localhost:5000/analytics
```

### Metrics Tracked
1. **Total Queries**: Number of questions asked
2. **Average Response Time**: Mean time to generate responses
3. **Satisfaction Score**: Average user ratings (1-5 scale)
4. **Intent Distribution**: Breakdown of query categories

### Analytics Storage
Analytics are stored in `analytics.json`:
```json
{
  "total_queries": 45,
  "intent_accuracy": [],
  "response_times": [1.2, 0.8, 1.5, ...],
  "satisfaction_scores": [5, 4, 5, 3, ...],
  "intent_distribution": {
    "billing": 12,
    "technical": 18,
    "account": 10,
    "complaints": 3,
    "general": 2
  }
}
```

## 🔌 API Endpoints

### POST /chat
Send a message to the chatbot

**Request:**
```json
{
  "message": "How do I reset my password?"
}
```

**Response:**
```json
{
  "response": "To reset your password: 1. Go to login page...",
  "intent": {
    "primary_intent": "account",
    "confidence": 0.95,
    "all_intents": ["account"]
  },
  "entities": {},
  "response_time": 1.23,
  "sources": [
    {"content": "Password reset process..."}
  ]
}
```

### POST /feedback
Submit user feedback

**Request:**
```json
{
  "rating": 5
}
```

**Response:**
```json
{
  "status": "success"
}
```

### GET /analytics
Get analytics summary

**Response:**
```json
{
  "total_queries": 45,
  "avg_response_time": 1.15,
  "avg_satisfaction": 4.2,
  "intent_distribution": {
    "billing": 12,
    "technical": 18,
    "account": 10,
    "complaints": 3,
    "general": 2
  }
}
```

### POST /clear
Clear conversation history

**Response:**
```json
{
  "status": "success"
}
```






---

Built with ❤️ using LangChain, Flask, and FAISS
