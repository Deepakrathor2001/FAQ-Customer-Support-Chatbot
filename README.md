# Multi-Domain RAG Customer Support Chatbot

Developed an FAQ'S Customer Support Chatbot designed for e-commerce platforms and food delivery applications. 
The chatbot integrates with databases and APIs to provide real-time assistance for customer queries related to order status, live tracking, cancellations, payment issues, product availability, pricing, discounts, delivery estimates, and other support-related requests. 
By leveraging Retrieval-Augmented Generation (RAG) and Large Language Models (LLMs), the system delivers accurate, context-aware, and conversational responses, enhancing customer experience while reducing manual support workload.

## Project Motivation

The motivation behind this project was to build an intelligent AI-powered customer support assistant capable of providing instant and accurate responses to common customer queries. 
By combining Retrieval-Augmented Generation (RAG), Large Language Models (LLMs), and domain-specific knowledge bases, the chatbot can retrieve relevant information and generate context-aware responses in real time.

This project was also developed to gain practical experience in Generative AI, information retrieval, prompt engineering, API integration, and end-to-end AI application development while addressing a real-world business problem.

## Features

* Multi-domain customer support chatbot
* Retrieval-Augmented Generation (RAG)
* Claude API integration
* Custom TF-IDF retrieval engine
* Semantic document matching
* Conversation memory
* Interactive Streamlit interface
* Real-time source retrieval display
* Knowledge base built from multiple datasets
* Modular and scalable architecture

## Supported Domains

The chatbot can answer questions from multiple domains, including:

* E-Commerce Support
* Banking Services
* Financial Services
* Medical FAQs
* IT Customer Support
* Educational Support Tickets
* General Knowledge and Reference QA

## Tech Stack

### Programming Language

* Python

### Frontend

* Streamlit

### Large Language Model

Retrieval-Augmented Generation (RAG)
LLM API'S

### Retrieval System

* Custom TF-IDF Engine
* Cosine Similarity Search

### Data Processing

* JSON
* CSV
* Text Datasets

## System Workflow

1. User submits a question.
2. The query is tokenized and processed.
3. TF-IDF similarity search retrieves the most relevant FAQ entries.
4. Retrieved information is converted into a structured context.
5. Context is injected into a system prompt.
6. Claude generates a response using only the retrieved information.
7. The final answer is displayed along with matching sources.

## Architecture

```text
User Query
     │
     ▼
Query Processing
     │
     ▼
TF-IDF Retrieval Engine
     │
     ▼
Top Relevant Documents
     │
     ▼
Context Builder
     │
     ▼
LLM API's
     │
     ▼
Generated Response
     │
     ▼
Streamlit Interface
```

## Project Structure

```text
multi-domain-rag-chatbot/
│
├── app.py
├── requirements.txt
├── README.md
│
├── data/
│   ├── custom_faq_dataset.json
│   ├── banking_data
│   ├── medical_data
│   └── faq_files
│
├── datasets/
│
└── assets/
```

## Key Components

- Knowledge Base Builder

The application loads data from multiple JSON, CSV, and text-based datasets and converts them into a unified knowledge base structure.

- Retrieval Engine

A custom retrieval system calculates TF-IDF vectors and ranks documents using cosine similarity to identify the most relevant information for a user query.

- Prompt Construction

Retrieved information is transformed into structured context and injected into the Claude system prompt.

- Response Generation

Claude generates responses using only the retrieved information, helping reduce hallucinations and improve answer accuracy.

## Challenges Faced

One of the biggest challenges was combining datasets from multiple domains while maintaining consistent retrieval quality.

Another challenge was designing a retrieval system capable of efficiently finding relevant information without relying on external vector databases.

Balancing retrieval quality, response accuracy, and application performance required several iterations of testing and refinement.

## What I Learned

This project helped me gain practical experience in:

* Retrieval-Augmented Generation (RAG)
* Large Language Model Integration
* Prompt Engineering
* Information Retrieval
* TF-IDF Vectorization
* Cosine Similarity
* Streamlit Application Development
* Dataset Processing
* End-to-End AI System Design

## Future Improvements

* Vector database integration (FAISS/ChromaDB)
* Hybrid search architecture
* Multi-language support
* User authentication
* Persistent chat memory
* Source citation generation
* Document upload support
* Cloud deployment
* Analytics dashboard

## Installation

Clone the repository:

```bash
git clone https://github.com/your-username/multi-domain-rag-chatbot.git
```

Navigate to the project folder:

```bash
cd multi-domain-rag-chatbot
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure your Anthropic API key:

```bash
ANTHROPIC_API_KEY=your_api_key
```

Run the application:

```bash
streamlit run app.py
```

## Disclaimer

This project is intended for educational and research purposes. Responses are generated based on retrieved knowledge base content and should not be considered professional financial, medical, or legal advice.

## Author

Deepak Rathor

AI/ML Engineer | Machine Learning | NLP | Generative AI | Retrieval-Augmented Generation
