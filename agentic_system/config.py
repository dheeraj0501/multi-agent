import os
from typing import Optional

from dotenv import find_dotenv, load_dotenv
from pydantic import BaseModel, Field


load_dotenv(find_dotenv(usecwd=True), override=False)


class Settings(BaseModel):
    use_llm: bool = Field(default_factory=lambda: os.getenv("USE_LLM", "false").lower() in {"1", "true", "yes"})
    model: str = Field(default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-2.5-flash"))
    api_key: Optional[str] = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY"))
    base_url: Optional[str] = Field(default_factory=lambda: os.getenv("GEMINI_BASE_URL"))
    temperature: float = Field(default_factory=lambda: float(os.getenv("GEMINI_TEMPERATURE", "0.1")))


settings = Settings()
