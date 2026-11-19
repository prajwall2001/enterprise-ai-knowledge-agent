@'

\# Enterprise AI Knowledge Agent



An AI-powered document question-answering application built using Retrieval-Augmented Generation (RAG). Upload PDF documents and ask questions to receive context-based answers with document source references.



\## Features



\- Upload and process PDF documents.

\- Extract text while preserving page numbers.

\- Split documents into overlapping text chunks.

\- Generate embeddings using Sentence Transformers.

\- Store and retrieve document embeddings using ChromaDB.

\- Ask natural-language questions about uploaded documents.

\- Generate answers using a locally running Ollama LLM.

\- Display source document names and page numbers.

\- Interactive Streamlit chatbot interface.

\- FastAPI backend with REST API endpoints.



\## Technology Stack



| Technology | Purpose |

|---|---|

| Python | Backend programming |

| FastAPI | REST API |

| Streamlit | Chatbot user interface |

| ChromaDB | Vector database |

| Sentence Transformers | Text embeddings |

| all-MiniLM-L6-v2 | Embedding model |

| Ollama | Local LLM execution |

| Qwen2.5:0.5b | Language model |

| PyPDF | PDF text extraction |

| Requests | API communication |



\## Architecture



```mermaid

flowchart TD

&#x20;   A\[User] --> B\[Streamlit Chat Interface]

&#x20;   B --> C\[FastAPI Backend]

&#x20;   C --> D\[PDF Text Extraction]

&#x20;   D --> E\[Text Chunking]

&#x20;   E --> F\[Sentence Transformer Embeddings]

&#x20;   F --> G\[(ChromaDB Vector Store)]

&#x20;   B -->|User Question| C

&#x20;   C --> H\[Query Embedding]

&#x20;   H --> I\[Semantic Search]

&#x20;   I --> G

&#x20;   G --> J\[Retrieved Document Context]

&#x20;   J --> K\[Prompt Construction]

&#x20;   K --> L\[Ollama - Qwen2.5]

&#x20;   L --> C

&#x20;   C --> B

