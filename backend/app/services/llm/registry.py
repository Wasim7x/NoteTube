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
    models: List[ModelOption]

# Provider Registry mapping
PROVIDER_METADATA: Dict[str, ProviderInfo] = {
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
    return list(PROVIDER_METADATA.values())
