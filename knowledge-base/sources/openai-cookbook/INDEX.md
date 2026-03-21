# OpenAI Cookbook - Index

Oficiální sbírka příkladů a návodů pro OpenAI API — function calling, agents, RAG, embeddings, vision, voice, fine-tuning, evals a integrace s vector databases.

## Use cases

| Use case | Cesta | Typ |
|----------|-------|-----|
| **Function calling** — základy | `examples/How_to_call_functions_with_chat_models.ipynb` | notebook |
| Function calling — nearby places | `examples/Function_calling_finding_nearby_places.ipynb` | notebook |
| Function calling — z OpenAPI spec | `examples/Function_calling_with_an_OpenAPI_spec.ipynb` | notebook |
| Function calling — knowledge retrieval | `examples/How_to_call_functions_for_knowledge_retrieval.ipynb` | notebook |
| Function calling — fine-tuning | `examples/Fine_tuning_for_function_calling.ipynb` | notebook |
| Reasoning + function calls (o-series) | `examples/reasoning_function_calls.ipynb` | notebook |
| **Agents SDK** — dispute agent, parallel agents, session memory | `examples/agents_sdk/` | adresář |
| Agents SDK — voice agents (audio, knowledge) | `examples/agents_sdk/voice_agents_audio/`, `voice_agents_knowledge/` | adresář |
| Agents SDK — evaluace agentů | `examples/agents_sdk/evaluate_agents.ipynb` | notebook |
| AgentKit walkthrough | `examples/agentkit/` | adresář |
| Multi-agent orchestrace | `examples/Orchestrating_agents.ipynb` | notebook |
| Structured outputs — multi-agent | `examples/Structured_outputs_multi_agent.ipynb` | notebook |
| Object-oriented agentic approach | `examples/object_oriented_agentic_approach/` | adresář |
| **MCP** — tool guide | `examples/mcp/mcp_tool_guide.ipynb` | notebook |
| MCP — Databricks supply chain copilot | `examples/mcp/building-a-supply-chain-copilot-with-agent-sdk-and-databricks-mcp/` | adresář |
| MCP — Deep Research server | `examples/deep_research_api/how_to_build_a_deep_research_mcp_server/` | adresář |
| MCP — voice agents (partners) | `examples/partners/mcp_powered_voice_agents/` | adresář |
| **RAG** — embeddings + search | `examples/Question_answering_using_embeddings.ipynb` | notebook |
| RAG — PDF parsing | `examples/Parse_PDF_docs_for_RAG.ipynb` | notebook |
| RAG — graph database | `examples/RAG_with_graph_db.ipynb` | notebook |
| RAG — GPT-4o outfit assistant | `examples/How_to_combine_GPT4o_with_RAG_Outfit_Assistant.ipynb` | notebook |
| RAG — image understanding | `examples/multimodal/image_understanding_with_rag.ipynb` | notebook |
| RAG — SharePoint quickstart | `examples/chatgpt/rag-quickstart/` | adresář |
| **Embeddings** — úvod, clustering, klasifikace | `examples/Using_embeddings.ipynb`, `Clustering.ipynb`, `Classification_using_embeddings.ipynb` | notebook |
| Embeddings — semantic search | `examples/Semantic_text_search_using_embeddings.ipynb` | notebook |
| Embeddings — customization | `examples/Customizing_embeddings.ipynb` | notebook |
| Embeddings — vizualizace 2D/3D | `examples/Visualizing_embeddings_in_2D.ipynb`, `Visualizing_embeddings_in_3D.ipynb` | notebook |
| Embeddings — Wikipedia articles | `examples/Embedding_Wikipedia_articles_for_search.ipynb` | notebook |
| Embeddings — recommendation, regression | `examples/Recommendation_using_embeddings.ipynb`, `Regression_using_embeddings.ipynb` | notebook |
| **GPT Actions** — knihovna 27 integrací (Jira, Salesforce, Confluence, Snowflake, BigQuery, Gmail, Outlook...) | `examples/chatgpt/gpt_actions_library/` | adresář |
| GPT Actions — SharePoint + Azure Function | `examples/chatgpt/sharepoint_azure_function/` | adresář |
| **Voice / Realtime API** — překlad, TTS steering, Realtime prompting | `examples/voice_solutions/` | adresář |
| Realtime API — context summarization | `examples/Context_summarization_with_realtime_api.ipynb` | notebook |
| Realtime API — eval guide | `examples/Realtime_eval_guide.ipynb` | notebook |
| Realtime API — building with rt mini | `examples/building_w_rt_mini/` | adresář |
| Whisper — transcription, prompting, korekce | `examples/Whisper_prompting_guide.ipynb`, `Whisper_processing_guide.ipynb`, `Whisper_correct_misspelling.ipynb` | notebook |
| Speech transcription methods | `examples/Speech_transcription_methods.ipynb` | notebook |
| **Vision / Multimodal** — GPT-4o intro | `examples/gpt4o/introduction_to_gpt4o.ipynb` | notebook |
| Vision — function calling | `examples/multimodal/Using_GPT4_Vision_With_Function_Calling.ipynb` | notebook |
| Vision — document understanding | `examples/multimodal/document_and_multimodal_understanding_tips.ipynb` | notebook |
| Vision — video understanding | `examples/GPT_with_vision_for_video_understanding.ipynb` | notebook |
| Vision — fine-tuning VQA | `examples/multimodal/Vision_Fine_tuning_on_GPT4o_for_Visual_Question_Answering.ipynb` | notebook |
| Image generation — GPT Image, DALL-E | `examples/Generate_Images_With_GPT_Image.ipynb`, `examples/dalle/` | adresář |
| Image generation — prompting guide 1.5 | `examples/multimodal/image-gen-1.5-prompting_guide.ipynb` | notebook |
| Sora — video generation prompting | `examples/sora/sora2_prompting_guide.ipynb` | notebook |
| **Fine-tuning** — chat models | `examples/How_to_finetune_chat_models.ipynb` | notebook |
| Fine-tuning — DPO (preference optimization) | `examples/Fine_tuning_direct_preference_optimization_guide.ipynb` | notebook |
| Fine-tuning — data prep | `examples/Chat_finetuning_data_prep.ipynb` | notebook |
| Fine-tuning — klasifikace | `examples/Fine-tuned_classification.ipynb` | notebook |
| Fine-tuning — model distillation | `examples/Leveraging_model_distillation_to_fine-tune_a_model.ipynb` | notebook |
| Reinforcement fine-tuning | `examples/Reinforcement_Fine_Tuning.ipynb` | notebook |
| **Evals** — OpenAI Evals getting started | `examples/evaluation/Getting_Started_with_OpenAI_Evals.ipynb` | notebook |
| Evals — RAG (LlamaIndex) | `examples/evaluation/Evaluate_RAG_with_LlamaIndex.ipynb` | notebook |
| Evals — SQL generation | `examples/evaluation/How_to_evaluate_LLMs_for_SQL_generation.ipynb` | notebook |
| Evals — summarization | `examples/evaluation/How_to_eval_abstractive_summarization.ipynb` | notebook |
| Evals — image evals | `examples/multimodal/image_evals.ipynb` | notebook |
| Evals — realtime evals framework | `examples/evals/realtime_evals/` | adresář |
| Evals — custom LLM-as-a-Judge | `examples/Custom-LLM-as-a-Judge.ipynb` | notebook |
| Evals — guardrails (hallucination, moderation) | `examples/Developing_hallucination_guardrails.ipynb`, `How_to_use_guardrails.ipynb` | notebook |
| **Vector databases** — 20+ integrací (Pinecone, Weaviate, Qdrant, Chroma, Milvus, Redis, Elasticsearch, pgvector...) | `examples/vector_databases/` | adresář |
| **Responses API** — tool orchestration, reasoning items | `examples/responses_api/` | adresář |
| **o-series reasoning** — o1 structured outputs, data validation, routine generation | `examples/o1/` | adresář |
| o3/o4-mini prompting guide | `examples/o-series/o3o4-mini_prompting_guide.ipynb` | notebook |
| **GPT-5** — prompting, troubleshooting, frontend, new params, prompt optimization | `examples/gpt-5/` | adresář |
| **Deep Research API** — intro, agents | `examples/deep_research_api/` | adresář |
| **Codex** — prompting, code review, MCP agents SDK | `examples/codex/` | adresář |
| Skills in API | `examples/skills_in_api.ipynb` | notebook |
| Structured Outputs — intro | `examples/Structured_Outputs_Intro.ipynb` | notebook |
| Data extraction & transformation | `examples/Data_extraction_transformation.ipynb` | notebook |
| Prompt caching (101 + 201) | `examples/Prompt_Caching101.ipynb`, `Prompt_Caching_201.ipynb` | notebook |
| Meta prompting | `examples/Enhance_your_prompts_with_meta_prompting.ipynb` | notebook |
| Batch processing | `examples/batch_processing.ipynb` | notebook |
| Token counting (tiktoken) | `examples/How_to_count_tokens_with_tiktoken.ipynb` | notebook |
| Rate limits handling | `examples/How_to_handle_rate_limits.ipynb` | notebook |
| Parallel API requests | `examples/api_request_parallel_processor.py` | script |

## Klíčové patterny

- **Function calling** — definice tools jako JSON Schema, model vrací structured JSON s argumenty, aplikace volá funkci a vrací výsledek
- **Agents SDK** — orchestrace multi-agent workflows s handoff, guardrails a tool use; podpora voice agents
- **MCP (Model Context Protocol)** — standardní protokol pro připojení externích tools a data sources k modelům
- **RAG pipeline** — embeddings → vector DB → retrieval → context injection → completion
- **Evals loop** — systematické hodnocení kvality (LLM-as-a-Judge, metriky, guardrails) → iterativní vylepšování promptů
- **Structured Outputs** — JSON mode se schématem pro spolehlivý parsovatelný výstup
- **Responses API** — nové API s nativní tool orchestrací a reasoning items (náhrada za Chat Completions pro agentic use cases)
- **Prompt caching** — opakované volání se sdíleným prefixem pro úsporu tokenů a latence

## Prerekvizity

- **Python 3.9+** a `pip` (většina příkladů jsou Jupyter notebooky)
- **OpenAI API klíč** — nastavit jako `OPENAI_API_KEY` env variable
- **Jupyter** — `pip install jupyter` nebo `jupyter lab`
- Pro vector database příklady: příslušný DB klient (Pinecone, Weaviate, Qdrant atd.)
- Pro Azure příklady: Azure subscription + Azure OpenAI resource
- Pro voice/realtime příklady: podpora WebSocket, audio knihovny
- Závislosti per příklad: `pip install -r examples/<topic>/requirements.txt`
