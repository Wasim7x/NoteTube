from typing import Dict, List, Type
from pydantic import BaseModel
from app.services.llm.base import LLMProvider

class ModelOption(BaseModel):
    id: str
    name: str
    description: str = ""
    is_recommended: bool = False

class ProviderInfo(BaseModel):
    id: str
    name: str
    description: str
    default_model: str
    key_placeholder: str
    help_url: str
    requires_api_key: bool = True
    models: List[ModelOption]

# Provider Registry mapping
PROVIDER_METADATA: Dict[str, ProviderInfo] = {
    "ollama": ProviderInfo(
        id="ollama",
        name="Ollama (Local)",
        description="Run local models directly on your hardware without cloud API keys or subscriptions.",
        default_model="qwen3:1.7b",
        key_placeholder="Not required (Local)",
        help_url="https://ollama.com",
        requires_api_key=False,
        models=[
            ModelOption(id="qwen3:1.7b", name="Qwen 3 (1.7B)", description="Fast & lightweight local model (Installed)", is_recommended=True),
            ModelOption(id="qwen3.5:latest", name="Qwen 3.5 (9.7B)", description="High capability local model (Installed)"),
            ModelOption(id="llama3.2:3b", name="Llama 3.2 (3B)", description="Lightweight Meta model"),
            ModelOption(id="mistral:7b", name="Mistral (7B)", description="Balanced general purpose model"),
        ]
    ),
    "gemini": ProviderInfo(
        id="gemini",
        name="Google Gemini",
        description="Google's multimodal Gemini models with high speed and large context windows.",
        default_model="gemini-2.5-flash",
        key_placeholder="AIzaSy...",
        help_url="https://aistudio.google.com/app/apikey",
        models=[
            ModelOption(id="gemini-2.5-flash", name="Gemini 2.5 Flash", description="Fastest and highly capable for note generation", is_recommended=True),
            ModelOption(id="gemini-2.5-pro", name="Gemini 2.5 Pro", description="Highest quality reasoning and detailed synthesis"),
            ModelOption(id="gemini-2.0-flash", name="Gemini 2.0 Flash", description="Balanced speed and structured output"),
            ModelOption(id="gemini-1.5-flash", name="Gemini 1.5 Flash", description="Reliable lightweight model"),
            ModelOption(id="gemini-1.5-pro", name="Gemini 1.5 Pro", description="Deep analysis for long transcripts"),
        ]
    ),
    "openai": ProviderInfo(
        id="openai",
        name="OpenAI",
        description="Flagship OpenAI GPT and reasoning models.",
        default_model="gpt-4o-mini",
        key_placeholder="sk-...",
        help_url="https://platform.openai.com/api-keys",
        models=[
            ModelOption(id="gpt-4o-mini", name="GPT-4o Mini", description="Fast, cost-effective, high quality notes", is_recommended=True),
            ModelOption(id="gpt-4o", name="GPT-4o", description="Flagship intelligent multimodal model"),
            ModelOption(id="gpt-4.5-preview", name="GPT-4.5 Preview", description="Advanced reasoning and rich formatting"),
            ModelOption(id="o3-mini", name="o3 Mini", description="High-speed reasoning model"),
            ModelOption(id="o1-mini", name="o1 Mini", description="STEM and deep reasoning"),
        ]
    ),
    "anthropic": ProviderInfo(
        id="anthropic",
        name="Anthropic Claude",
        description="Anthropic's Claude models with superior writing style and nuanced summarization.",
        default_model="claude-3-7-sonnet-latest",
        key_placeholder="sk-ant-...",
        help_url="https://console.anthropic.com/settings/keys",
        models=[
            ModelOption(id="claude-3-7-sonnet-latest", name="Claude 3.7 Sonnet", description="Hybrid reasoning & top-tier note synthesis", is_recommended=True),
            ModelOption(id="claude-3-5-sonnet-latest", name="Claude 3.5 Sonnet", description="Exceptional writing quality and structure"),
            ModelOption(id="claude-3-5-haiku-latest", name="Claude 3.5 Haiku", description="Fastest Claude model for quick summaries"),
            ModelOption(id="claude-3-opus-latest", name="Claude 3 Opus", description="Deep, comprehensive long-form synthesis"),
        ]
    ),
    "groq": ProviderInfo(
        id="groq",
        name="Groq",
        description="Ultra-fast LPU inference hosting leading open-source models.",
        default_model="openai/gpt-oss-20b",
        key_placeholder="gsk_...",
        help_url="https://console.groq.com/keys",
        models=[
            ModelOption(id="openai/gpt-oss-20b", name="GPT-OSS 20B", description="Fast & highly capable on Groq LPUs", is_recommended=True),
            ModelOption(id="openai/gpt-oss-120b", name="GPT-OSS 120B", description="Large 120B parameter model on Groq"),
            ModelOption(id="qwen/qwen3.6-27b", name="Qwen 3.6 27B", description="Advanced multimodal/reasoning capabilities"),
            ModelOption(id="llama-3.3-70b-versatile", name="Llama 3.3 70B Versatile", description="State-of-the-art open-source intelligence"),
            ModelOption(id="llama-3.1-8b-instant", name="Llama 3.1 8B Instant", description="Blazing fast generation"),
        ]
    ),
    "openrouter": ProviderInfo(
        id="openrouter",
        name="OpenRouter",
        description="Universal gateway to hundreds of open-source and proprietary models.",
        default_model="deepseek/deepseek-chat",
        key_placeholder="sk-or-...",
        help_url="https://openrouter.ai/keys",
        models=[
            ModelOption(id="deepseek/deepseek-chat", name="DeepSeek V3 (Chat)", description="Extremely cost-effective, high quality", is_recommended=True),
            ModelOption(id="deepseek/deepseek-r1", name="DeepSeek R1", description="Deep reasoning and chain-of-thought"),
            ModelOption(id="meta-llama/llama-3.3-70b-instruct", name="Meta Llama 3.3 70B", description="Open-weights flagship via OpenRouter"),
            ModelOption(id="anthropic/claude-3.5-sonnet", name="Claude 3.5 Sonnet", description="Via OpenRouter API key"),
            ModelOption(id="google/gemini-2.0-flash-001", name="Gemini 2.0 Flash", description="Via OpenRouter API key"),
        ]
    ),
}

# Provider class registry
_PROVIDER_CLASSES: Dict[str, Type[LLMProvider]] = {}

def register_provider(provider_id: str, provider_cls: Type[LLMProvider]):
    _PROVIDER_CLASSES[provider_id.lower()] = provider_cls

def get_registered_provider_class(provider_id: str) -> Type[LLMProvider]:
    pid = provider_id.lower().strip()
    if pid not in _PROVIDER_CLASSES:
        supported = ", ".join(list(PROVIDER_METADATA.keys()))
        raise ValueError(f"Unsupported provider '{provider_id}'. Supported providers are: {supported}")
    return _PROVIDER_CLASSES[pid]

def get_all_providers_info() -> List[ProviderInfo]:
    from app.config import settings
    from app.services.llm.ollama import get_installed_models

    providers_copy = [p.model_copy(deep=True) for p in PROVIDER_METADATA.values()]

    # If ollama provider is present, enrich its model list with locally installed models
    ollama_prov = next((p for p in providers_copy if p.id == "ollama"), None)
    if ollama_prov:
        installed = get_installed_models(base_url=settings.OLLAMA_BASE_URL, timeout=1.0)
        if installed:
            installed_set = set(m.lower() for m in installed)
            new_models: List[ModelOption] = []
            
            cfg_model = settings.OLLAMA_MODEL
            # Default to configured model if installed, otherwise first installed
            if any(cfg_model.lower() == m.lower() for m in installed):
                ollama_prov.default_model = cfg_model
            else:
                ollama_prov.default_model = installed[0]

            for inst_name in installed:
                is_rec = (inst_name.lower() == cfg_model.lower())
                desc = "Installed locally on your machine"
                if is_rec:
                    desc += " (Configured default)"
                new_models.append(
                    ModelOption(
                        id=inst_name,
                        name=inst_name,
                        description=desc,
                        is_recommended=is_rec
                    )
                )

            # Also keep non-installed popular presets
            for existing in PROVIDER_METADATA["ollama"].models:
                if existing.id.lower() not in installed_set:
                    new_models.append(
                        ModelOption(
                            id=existing.id,
                            name=existing.name,
                            description=f"{existing.description} (Not installed - will pull if selected)",
                            is_recommended=False
                        )
                    )
            ollama_prov.models = new_models

    # Reorder so active provider in settings.LLM_PROVIDER appears first
    target_lead = settings.LLM_PROVIDER.lower().strip()
    providers_copy.sort(key=lambda p: 0 if p.id.lower() == target_lead else 1)
    return providers_copy
