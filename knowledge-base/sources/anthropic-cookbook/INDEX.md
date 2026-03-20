# Anthropic Cookbook - INDEX

Oficialni sbirka prikladu a receptu pro praci s Claude API (tool use, agenti, RAG, multimodal, skills, extended thinking).

## Use Cases

### Tool Use - volani nastroju

| Use case | Cesta | Typ | Jazyk |
|----------|-------|-----|-------|
| Tool use - kalkulacka (zaklady) | tool_use/calculator_tool.ipynb | notebook | Python |
| Tool use - extrakce strukturovaneho JSON | tool_use/extracting_structured_json.ipynb | notebook | Python |
| Tool use - vyber nastroje (tool_choice) | tool_use/tool_choice.ipynb | notebook | Python |
| Tool use - paralelni volani | tool_use/parallel_tools.ipynb | notebook | Python |
| Tool use - programaticke volani (PTC) | tool_use/programmatic_tool_calling_ptc.ipynb | notebook | Python |
| Tool use + vision (multimodalni nastroje) | tool_use/vision_with_tools.ipynb | notebook | Python |
| Tool use - customer service agent | tool_use/customer_service_agent.ipynb | notebook | Python |
| Tool use - vyhledavani nastroju (embeddings) | tool_use/tool_search_with_embeddings.ipynb | notebook | Python |
| Tool use - vyhledavani nastroju (alternativy) | tool_use/tool_search_alternate_approaches.ipynb | notebook | Python |
| Tool use - Pydantic integrace | tool_use/tool_use_with_pydantic.ipynb | notebook | Python |
| Tool use - automaticka kompakce kontextu | tool_use/automatic-context-compaction.ipynb | notebook | Python |
| Tool use - pamet pro agenta | tool_use/memory_cookbook.ipynb | notebook | Python |
| Tool use - memory tool implementace | tool_use/memory_tool.py | script | Python |
| Tool evaluation - hodnoceni kvality | tool_evaluation/tool_evaluation.ipynb | notebook | Python |

### Claude Agent SDK

| Use case | Cesta | Typ | Jazyk |
|----------|-------|-----|-------|
| Agent SDK - jednoradkovy research agent | claude_agent_sdk/00_The_one_liner_research_agent.ipynb | notebook | Python |
| Agent SDK - chief of staff agent (multi-agent) | claude_agent_sdk/01_The_chief_of_staff_agent.ipynb | notebook | Python |
| Agent SDK - observability agent | claude_agent_sdk/02_The_observability_agent.ipynb | notebook | Python |
| Agent SDK - site reliability agent (SRE + MCP) | claude_agent_sdk/03_The_site_reliability_agent.ipynb | notebook | Python |
| Agent SDK - migrace z OpenAI Agents SDK | claude_agent_sdk/04_migrating_from_openai_agents_sdk.ipynb | notebook | Python |
| Agent SDK - research agent implementace | claude_agent_sdk/research_agent/agent.py | script | Python |
| Agent SDK - chief of staff implementace | claude_agent_sdk/chief_of_staff_agent/agent.py | script | Python |
| Agent SDK - observability agent implementace | claude_agent_sdk/observability_agent/agent.py | script | Python |
| Agent SDK - SRE MCP server | claude_agent_sdk/site_reliability_agent/sre_mcp_server.py | script | Python |

### Agentic Patterns (workflow vzory)

| Use case | Cesta | Typ | Jazyk |
|----------|-------|-----|-------|
| Zakladni agentic workflows (chaining, routing, parallelizace) | patterns/agents/basic_workflows.ipynb | notebook | Python |
| Evaluator-optimizer pattern | patterns/agents/evaluator_optimizer.ipynb | notebook | Python |
| Orchestrator-workers pattern | patterns/agents/orchestrator_workers.ipynb | notebook | Python |

### Skills (SKILL.md standard)

| Use case | Cesta | Typ | Jazyk |
|----------|-------|-----|-------|
| Skills - uvod a zaklady | skills/notebooks/01_skills_introduction.ipynb | notebook | Python |
| Skills - financni aplikace | skills/notebooks/02_skills_financial_applications.ipynb | notebook | Python |
| Skills - vlastni vyvoj skills | skills/notebooks/03_skills_custom_development.ipynb | notebook | Python |
| Priklad SKILL.md - financni analyza | skills/custom_skills/analyzing-financial-statements/SKILL.md | SKILL.md | - |
| Priklad SKILL.md - brand guidelines | skills/custom_skills/applying-brand-guidelines/SKILL.md | SKILL.md | - |
| Priklad SKILL.md - financni modely | skills/custom_skills/creating-financial-models/SKILL.md | SKILL.md | - |

### RAG a Embeddings

| Use case | Cesta | Typ | Jazyk |
|----------|-------|-----|-------|
| RAG - zakladni implementace | capabilities/retrieval_augmented_generation/guide.ipynb | notebook | Python |
| Contextual embeddings (Contextual RAG) | capabilities/contextual-embeddings/guide.ipynb | notebook | Python |
| Contextual RAG - AWS Lambda funkce | capabilities/contextual-embeddings/contextual-rag-lambda-function/ | projekt | Python |
| RAG s MongoDB | third_party/MongoDB/rag_using_mongodb.ipynb | notebook | Python |
| RAG s Pinecone | third_party/Pinecone/rag_using_pinecone.ipynb | notebook | Python |
| RAG s LlamaIndex | third_party/LlamaIndex/Basic_RAG_With_LlamaIndex.ipynb | notebook | Python |

### Capabilities (klasifikace, sumarizace, SQL)

| Use case | Cesta | Typ | Jazyk |
|----------|-------|-----|-------|
| Klasifikace textu | capabilities/classification/guide.ipynb | notebook | Python |
| Sumarizace dokumentu | capabilities/summarization/guide.ipynb | notebook | Python |
| Text-to-SQL generovani | capabilities/text_to_sql/guide.ipynb | notebook | Python |
| SQL dotazy (jednodussi pristup) | misc/how_to_make_sql_queries.ipynb | notebook | Python |

### Multimodal (vision, PDF, audio)

| Use case | Cesta | Typ | Jazyk |
|----------|-------|-----|-------|
| Vision - zaklady | multimodal/getting_started_with_vision.ipynb | notebook | Python |
| Vision - best practices | multimodal/best_practices_for_vision.ipynb | notebook | Python |
| Vision - orezavani obrazku (crop tool) | multimodal/crop_tool.ipynb | notebook | Python |
| Cteni grafu, chartu a PowerPointu | multimodal/reading_charts_graphs_powerpoints.ipynb | notebook | Python |
| Transkripce textu z obrazku | multimodal/how_to_transcribe_text.ipynb | notebook | Python |
| Sub-agenti pro multimodalni ulohy | multimodal/using_sub_agents.ipynb | notebook | Python |
| PDF upload a sumarizace | misc/pdf_upload_summarization.ipynb | notebook | Python |
| Audio transkripce (Deepgram) | third_party/Deepgram/prerecorded_audio.ipynb | notebook | Python |

### Extended Thinking

| Use case | Cesta | Typ | Jazyk |
|----------|-------|-----|-------|
| Extended thinking - zaklady | extended_thinking/extended_thinking.ipynb | notebook | Python |
| Extended thinking + tool use | extended_thinking/extended_thinking_with_tool_use.ipynb | notebook | Python |

### Misc - API techniky a utility

| Use case | Cesta | Typ | Jazyk |
|----------|-------|-----|-------|
| Prompt caching | misc/prompt_caching.ipynb | notebook | Python |
| Spekulativni prompt caching | misc/speculative_prompt_caching.ipynb | notebook | Python |
| Batch processing (davkove zpracovani) | misc/batch_processing.ipynb | notebook | Python |
| JSON mode | misc/how_to_enable_json_mode.ipynb | notebook | Python |
| Citations (citace ze zdroju) | misc/using_citations.ipynb | notebook | Python |
| Metaprompt (generovani promptu) | misc/metaprompt.ipynb | notebook | Python |
| Moderation filter | misc/building_moderation_filter.ipynb | notebook | Python |
| Generovani testovacich pripadu | misc/generate_test_cases.ipynb | notebook | Python |
| Building evals (hodnoceni kvality) | misc/building_evals.ipynb | notebook | Python |
| Sampling past max tokens | misc/sampling_past_max_tokens.ipynb | notebook | Python |
| Cteni webovych stranek (Haiku) | misc/read_web_pages_with_haiku.ipynb | notebook | Python |
| Session memory compaction | misc/session_memory_compaction.ipynb | notebook | Python |
| Usage & cost API | observability/usage_cost_api.ipynb | notebook | Python |

### Coding

| Use case | Cesta | Typ | Jazyk |
|----------|-------|-----|-------|
| Prompting pro frontend estetiku | coding/prompting_for_frontend_aesthetics.ipynb | notebook | Python |

### Fine-tuning

| Use case | Cesta | Typ | Jazyk |
|----------|-------|-----|-------|
| Fine-tuning na AWS Bedrock | finetuning/finetuning_on_bedrock.ipynb | notebook | Python |

### Third-party integrace

| Use case | Cesta | Typ | Jazyk |
|----------|-------|-----|-------|
| LlamaIndex - multi-document agenti | third_party/LlamaIndex/Multi_Document_Agents.ipynb | notebook | Python |
| LlamaIndex - multimodalni | third_party/LlamaIndex/Multi_Modal.ipynb | notebook | Python |
| LlamaIndex - ReAct agent | third_party/LlamaIndex/ReAct_Agent.ipynb | notebook | Python |
| LlamaIndex - Router Query Engine | third_party/LlamaIndex/Router_Query_Engine.ipynb | notebook | Python |
| LlamaIndex - SubQuestion Query Engine | third_party/LlamaIndex/SubQuestion_Query_Engine.ipynb | notebook | Python |
| ElevenLabs - hlasovy asistent (streaming) | third_party/ElevenLabs/stream_voice_assistant_websocket.py | script | Python |
| WolframAlpha - LLM integrace | third_party/WolframAlpha/using_llm_api.ipynb | notebook | Python |
| Wikipedia - vyhledavani | third_party/Wikipedia/wikipedia-search-cookbook.ipynb | notebook | Python |
| VoyageAI - embeddings | third_party/VoyageAI/how_to_create_embeddings.md | guide | Python |

## Key Patterns

- **Tool use**: Definice JSON schemat pro nastroje, zpracovani `tool_use` bloku v odpovedi, iterativni volani (agentic loop)
- **Agentic workflows**: Chaining (retezeni), routing (smerovani), paralelizace, orchestrator-workers, evaluator-optimizer
- **SKILL.md standard**: Deklarativni popis schopnosti agenta - vstup, vystup, kroky, reference soubory
- **RAG pipeline**: Chunking -> embedding -> retrieval -> context injection -> generation
- **Contextual RAG**: Pridani kontextu ke kazdemu chunku pred embedovanim (lepsi retrieval)
- **Extended thinking**: Zapnuti `thinking` parametru pro slozite ulohy vyzadujici reasoning
- **Prompt caching**: Cachovani system promptu a dlouhych kontextu pro snizeni nakladu
- **Memory tool**: Perzistentni pamet agenta pomoci tool_use (ukladani/nacitani poznatku)
- **Agent SDK**: Claude Code jako runtime pro autonomni agenty s MCP tools, hooks a sub-agenty

## Prerequisites

- **Python**: >= 3.10
- **anthropic**: `pip install anthropic` (hlavni SDK)
- **claude-agent-sdk**: `pip install claude-agent-sdk` (pro Agent SDK priklady)
- **API klic**: `ANTHROPIC_API_KEY` environment variable
- **Volitelne**: `voyageai`, `pinecone-client`, `pymongo`, `llama-index`, `deepgram-sdk` (pro third-party integrace)
- **Volitelne**: Docker (pro observability agent, SRE agent)
