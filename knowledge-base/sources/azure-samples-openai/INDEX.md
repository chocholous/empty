# Azure OpenAI Samples

Oficialni Microsoft repository s praktickymi ukazkami pro Azure OpenAI Service, Azure AI Foundry a agent-based architektury -- od zakladnich API volani po kompletni enterprise reseni.

## Use Cases

### Zakladni vzory (Basic_Samples)

| Use case | Cesta | Typ | Jazyk |
|----------|-------|-----|-------|
| Chat completions -- zakladni volani Azure OpenAI SDK | Basic_Samples/Chat/basic_chatcompletions_example_sdk.ipynb | notebook | Python |
| Sprava konverzace a historie zprav (ChatGPT) | Basic_Samples/Chat/chatGPT_managing_conversation.ipynb | notebook | Python |
| Chat s vlastnimi daty (RAG zaklad) | Basic_Samples/Chat/chat_with_your_own_data.ipynb | notebook | Python |
| Chat completions v C# | Basic_Samples/Chat/dotnet/csharp/chat.ipynb | notebook | C# |
| Chat s vlastnimi daty v C# | Basic_Samples/Chat/dotnet/csharp/Chat_with_your_own_data.ipynb | notebook | C# |
| Extrakce entit z dlouhych dokumentu v C# | Basic_Samples/Chat/dotnet/csharp/Entity_extraction_for_long_documents.ipynb | notebook | C# |
| Completions pres REST API | Basic_Samples/Completions/basic_completions_example_restapi.ipynb | notebook | Python |
| Completions pres SDK | Basic_Samples/Completions/basic_completions_example_sdk.ipynb | notebook | Python |
| Completions s dynamickym promptem | Basic_Samples/Completions/completions_with_dynamic_prompt.ipynb | notebook | Python |
| Embeddings pres REST API | Basic_Samples/Embeddings/basic_embeddings_example_restapi.ipynb | notebook | Python |
| Embeddings pres SDK | Basic_Samples/Embeddings/basic_embeddings_example_sdk.ipynb | notebook | Python |
| Ziskani embeddings v C# | Basic_Samples/Embeddings/dotnet/csharp/Get_embeddings.ipynb | notebook | C# |
| Embeddings z datasetu v C# | Basic_Samples/Embeddings/dotnet/csharp/Get_embeddings_from_dataset.ipynb | notebook | C# |
| Porovnavani embeddings v C# | Basic_Samples/Embeddings/dotnet/csharp/Comparing_embeddings.ipynb | notebook | C# |
| Embedding dlouhych vstupu v C# | Basic_Samples/Embeddings/dotnet/csharp/Embedding_long_inputs.ipynb | notebook | C# |
| Embedding Wikipedia clanku pro vyhledavani v C# | Basic_Samples/Embeddings/dotnet/csharp/Embedding_Wikipedia_articles_for_search.ipynb | notebook | C# |
| Semanticke textove vyhledavani pomoci embeddings v C# | Basic_Samples/Embeddings/dotnet/csharp/Semantic_text_search_using_embeddings.ipynb | notebook | C# |
| Q&A pomoci embeddings v C# | Basic_Samples/Embeddings/dotnet/csharp/Question_answering_using_embeddings.ipynb | notebook | C# |
| Q&A s fusion retriever architekturou v C# | Basic_Samples/Embeddings/dotnet/csharp/Question_answering_using_fusion_retriever_architecture.ipynb | notebook | C# |
| Q&A pomoci LlamaIndex v C# | Basic_Samples/Embeddings/dotnet/csharp/Question_answering_using_llamaindex.ipynb | notebook | C# |
| Zero-shot klasifikace s embeddings v C# | Basic_Samples/Embeddings/dotnet/csharp/Zero-shot_classification_with_embeddings.ipynb | notebook | C# |
| Clustering s embeddings v C# | Basic_Samples/Embeddings/dotnet/csharp/Clustering.ipynb | notebook | C# |
| Labelovani GitHub issues pomoci embeddings v C# | Basic_Samples/Embeddings/dotnet/csharp/Labelling_github_issues_with_embeddings.ipynb | notebook | C# |
| Function calling v Azure OpenAI | Basic_Samples/Functions/working_with_functions.ipynb | notebook | Python |
| Function calling s Azure Cognitive Search | Basic_Samples/Functions/functions_with_azure_search.ipynb | notebook | Python |
| Function calling s Bing Search | Basic_Samples/Functions/functions_with_bing_search.ipynb | notebook | Python |
| Function calling -- hledani blizkych mist v C# | Basic_Samples/Functions/dotnet/csharp/Function_calling_finding_nearby_places.ipynb | notebook | C# |
| Generovani obrazku DALL-E v C# | Basic_Samples/DALL-E/dotnet/csharp/DALL-E.ipynb | notebook | C# |
| Whisper -- zpracovani audia v C# | Basic_Samples/Whisper/dotnet/csharp/Whisper_processing_guide.ipynb | notebook | C# |
| Whisper -- prompting guide v C# | Basic_Samples/Whisper/dotnet/csharp/Whisper_prompting_guide.ipynb | notebook | C# |
| AAD/Entra ID autentizace pres REST API | Basic_Samples/AAD_Integration/aad_integration_example_restapi.ipynb | notebook | Python |
| AAD/Entra ID autentizace pres SDK | Basic_Samples/AAD_Integration/aad_integration_example_sdk.ipynb | notebook | Python |
| LangChain s Azure OpenAI -- zaciname | Basic_Samples/LangChain/azure_openai_getting_started.ipynb | notebook | Python |
| LangChain s Azure OpenAI -- pokrocile | Basic_Samples/LangChain/working_with_langchain.ipynb | notebook | Python |
| Vector store s Milvus v C# | Basic_Samples/Datastores/dotnet/csharp/Getting-Started-Milvus.ipynb | notebook | C# |
| Ingest GitHub issues do Qdrant v C# | Basic_Samples/Datastores/dotnet/csharp/Ingest_Github_Issues_Qdrant.ipynb | notebook | C# |
| Q&A pres vector store (Milvus) v C# | Basic_Samples/Datastores/dotnet/csharp/Question_answering_using_vector_store_search_milvus.ipynb | notebook | C# |
| Q&A pres vector store (Qdrant) v C# | Basic_Samples/Datastores/dotnet/csharp/Question_answering_using_vector_store_search_qdrant.ipynb | notebook | C# |

### Agent-based reseni (Agent_Based_Samples)

| Use case | Cesta | Typ | Jazyk |
|----------|-------|-----|-------|
| Multi-agent zakaznicka podpora (Semantic Kernel Process Framework) | Agent_Based_Samples/customer_assist/ | aplikace | Python |
| Release management s AI agenty (Azure DevOps, GitHub integrace) | Agent_Based_Samples/release_manager/ | aplikace | Python |
| Sales analyst agent s enterprise security (Databricks, Bing) | Agent_Based_Samples/sales_analyst/ | aplikace | Python |
| Market research analyst -- automatizovany pruzkum trhu | Agent_Based_Samples/market_research_analyst/ | aplikace | Python |
| Document generator pres MCP servery (SharePoint, DevOps, AI Foundry) | Agent_Based_Samples/document_generator/ | aplikace | Python |

### Solution Accelerators

| Use case | Cesta | Typ | Jazyk |
|----------|-------|-----|-------|
| Advanced RAG pro financni reporty (multimodal, evaluace) | Solution_Accelerators/Advanced_RAG/ | aplikace | Python + TypeScript |
| Ingestion notebook pro financni data (Advanced RAG) | Solution_Accelerators/Advanced_RAG/data/rag/microsoft_data_ingestion.ipynb | notebook | Python |
| E-commerce copilot s multimodalnim vyhledavanim | Solution_Accelerators/Retail/ | aplikace | Python + TypeScript |
| Retail ingestion notebook | Solution_Accelerators/Retail/samples/retail/retail_ingestion.ipynb | notebook | Python |

### End-to-End reseni (End_to_end_Solutions)

| Use case | Cesta | Typ | Jazyk |
|----------|-------|-----|-------|
| Enterprise ChatGPT s Cognitive Search + SQL (RAG, RBAC, klasifikace) | End_to_end_Solutions/AOAISearchDemo/ | aplikace | Python + TypeScript |
| RAG notebook: chat-read-retrieve-read pattern | End_to_end_Solutions/AOAISearchDemo/notebooks/chat-read-retrieve-read.ipynb | notebook | Python |
| RAG notebook: read-decompose-ask pattern | End_to_end_Solutions/AOAISearchDemo/notebooks/read-decompose-ask.ipynb | notebook | Python |
| NL-to-SQL dotazovani nad strukturovanymi daty | End_to_end_Solutions/AOAISearchDemo/notebooks/structured_data_retreival_nltosql.ipynb | notebook | Python |
| Virtual Assistant pro pojistovnu (multi-turn, prompt injection, personalizace) | End_to_end_Solutions/AOAIVirtualAssistant/ | aplikace | Python + C# |
| GitHub Repo Assistant v Teams (Semantic Kernel + Qdrant) | End_to_end_Solutions/GithubRepoAssistant/ | aplikace | C# |
| Insights Generator -- analyza recenzi a sentimentu | End_to_end_Solutions/InsightsGenerator/ | aplikace + notebook | Python |

## Klicove patterny

### RAG (Retrieval-Augmented Generation)
- **Chat-Read-Retrieve-Read**: Iterativni RAG pattern, kde se odpoved zpresni dalsim retrieval krokem (`End_to_end_Solutions/AOAISearchDemo/notebooks/chat-read-retrieve-read.ipynb`)
- **Read-Decompose-Ask**: Rozlozeni sloziteho dotazu na poddotazy (`End_to_end_Solutions/AOAISearchDemo/notebooks/read-decompose-ask.ipynb`)
- **Advanced RAG**: Pokrocily parsing, indexing a querying nestrukturovanych dat vcetne multimodalnich vstupu (`Solution_Accelerators/Advanced_RAG/`)
- **NL-to-SQL**: Prevod prirozeneho jazyka na SQL dotazy (`End_to_end_Solutions/AOAISearchDemo/notebooks/structured_data_retreival_nltosql.ipynb`)

### Multi-Agent orchestrace
- **Semantic Kernel Process Framework**: Orchestrace vice agentu pro customer assist scenare (`Agent_Based_Samples/customer_assist/`)
- **Agent s tools**: Sales analyst a market research pouzivaji Bing Search, code interpreter a dalsich tools (`Agent_Based_Samples/sales_analyst/`, `Agent_Based_Samples/market_research_analyst/`)

### Autentizace a bezpecnost
- **AAD/Entra ID integrace**: Autentizace vuci Azure OpenAI pres Azure AD (`Basic_Samples/AAD_Integration/`)
- **RBAC simulace**: Pristupova prava k datum v RAG scenari (`End_to_end_Solutions/AOAISearchDemo/app/backend/utilities/access_management.py`)
- **Enterprise security**: Content Safety integrace v agent scenarech (`Agent_Based_Samples/sales_analyst/`)

### Function calling
- **Zakladni function calling**: Definice a volani funkci (`Basic_Samples/Functions/working_with_functions.ipynb`)
- **Function calling + Search**: Integrace s Azure Cognitive Search a Bing (`Basic_Samples/Functions/functions_with_azure_search.ipynb`, `functions_with_bing_search.ipynb`)

### MCP (Model Context Protocol)
- **Document Generator**: Vyuziva MCP servery pro pristup k SharePoint, Azure DevOps, AI Foundry a Microsoft Learn (`Agent_Based_Samples/document_generator/`)

### Multimodalni AI
- **E-commerce copilot**: Obrazkove vyhledavani a doporuceni produktu (`Solution_Accelerators/Retail/`)
- **Whisper**: Zpracovani a transkripce audia (`Basic_Samples/Whisper/`)
- **DALL-E**: Generovani obrazku (`Basic_Samples/DALL-E/`)

## Prerequisites

### Azure sluzby
- **Azure OpenAI Service** -- zaklad pro vsechny vzorky (GPT-4, GPT-3.5 Turbo, embeddings modely)
- **Azure AI Foundry** -- pro agent-based reseni (Agent_Based_Samples)
- **Azure Cognitive Search / AI Search** -- pro RAG scenare (AOAISearchDemo, Advanced_RAG, Retail, Functions)
- **Azure Cosmos DB** -- session management a ukladani dat (AOAISearchDemo, Advanced_RAG, Retail)
- **Azure SQL Server** -- pro strukturovana data v RAG (AOAISearchDemo)
- **Azure Blob Storage** -- ukladani dokumentu pro indexaci
- **Azure Redis Cache** -- caching v agent a RAG scenarech
- **Azure Content Safety** -- Responsible AI filtry (sales_analyst)
- **Bing Search API** -- grounding pro agenty (sales_analyst, market_research_analyst)
- **Azure Databricks** -- datova analyza (sales_analyst)
- **Azure Bot Service** -- pro chatbot scenare (AOAIVirtualAssistant)

### SDK a nastroje
- **Python 3.10+** s `openai`, `langchain`, `semantic-kernel` balicky
- **.NET 7+** pro C# vzorky a GithubRepoAssistant
- **Node.js** pro frontend aplikace (TypeScript/React)
- **Docker** pro vector store scenare (Milvus, Qdrant)
- **Azure CLI** pro deployment

### Modely
- **GPT-4 / GPT-4o** -- chat completions, agent orchestrace
- **GPT-3.5 Turbo** -- lehci scenare, klasifikace
- **text-embedding-ada-002** -- embeddings pro vyhledavani
- **DALL-E** -- generovani obrazku
- **Whisper** -- transkripce audia
