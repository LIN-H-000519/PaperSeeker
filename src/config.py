"""
Configuration Management Module
Loads settings from config.yaml and prompts.yaml
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from dotenv import load_dotenv


class Config:
    """Configuration management class"""

    def __init__(self, config_path: Optional[str] = None, prompts_path: Optional[str] = None):
        """
        Initialize configuration

        Args:
            config_path: config.yaml path, defaults to project root
            prompts_path: prompts.yaml path, defaults to project root
        """
        # Load .env file
        env_path = Path(__file__).parent.parent / ".env"
        if env_path.exists():
            load_dotenv(str(env_path))

        if config_path is None:
            config_path = self._find_file("config.yaml")
        if prompts_path is None:
            prompts_path = self._find_file("prompts.yaml")

        self.config_path = config_path
        self.prompts_path = prompts_path

        self._config: Dict[str, Any] = {}
        self._prompts: Dict[str, Any] = {}

        self.load()

    def _find_file(self, filename: str) -> str:
        """Find file path"""
        possible_paths = [
            Path.cwd() / filename,
            Path(__file__).parent.parent / filename,
            Path(__file__).parent.parent.parent / filename,
        ]

        for path in possible_paths:
            if path.exists():
                return str(path)

        raise FileNotFoundError(f"Cannot find {filename} in any of: {[str(p) for p in possible_paths]}")

    def _resolve_env_vars(self, value: Any) -> Any:
        """Resolve environment variables in ${VAR_NAME} format"""
        if isinstance(value, str) and value.startswith("${") and value.endswith("}"):
            env_var = value[2:-1]
            return os.environ.get(env_var, value)
        return value

    def _load_yaml(self, path: str) -> Dict[str, Any]:
        """Load YAML file and resolve environment variables"""
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        # Resolve environment variables
        import re
        for match in re.finditer(r'\$\{(\w+)\}', content):
            env_var = match.group(1)
            env_value = os.environ.get(env_var, "")
            content = content.replace(match.group(0), env_value)

        return yaml.safe_load(content)

    def load(self) -> None:
        """Load configuration files"""
        # Load config.yaml
        if self.config_path and Path(self.config_path).exists():
            self._config = self._load_yaml(self.config_path)

        # Load prompts.yaml
        if self.prompts_path and Path(self.prompts_path).exists():
            self._prompts = self._load_yaml(self.prompts_path)

    # === Email Configuration ===
    @property
    def email(self) -> Dict[str, Any]:
        return self._config.get("email", {})

    @property
    def smtp_server(self) -> str:
        return self.email.get("smtp_server", "smtp.gmail.com")

    @property
    def smtp_port(self) -> int:
        return self.email.get("smtp_port", 587)

    @property
    def sender_email(self) -> str:
        return self.email.get("sender_email", "")

    @property
    def sender_password(self) -> str:
        return self.email.get("sender_password", "")

    @property
    def recipient_email(self) -> str:
        return self.email.get("recipient_email", "")

    # === OpenAlex Configuration ===
    @property
    def openalex(self) -> Dict[str, Any]:
        return self._config.get("openalex", {})

    @property
    def openalex_api_url(self) -> str:
        return self.openalex.get("api_url", "https://api.openalex.org")

    # === LLM Configuration ===
    @property
    def llm(self) -> Dict[str, Any]:
        return self._config.get("llm", {})

    @property
    def llm_provider(self) -> str:
        return self.llm.get("provider", "anthropic")

    @property
    def llm_model(self) -> str:
        return self.llm.get("model", "claude-sonnet-4-20250514")

    @property
    def llm_api_key(self) -> str:
        return self.llm.get("api_key", "")

    @property
    def llm_base_url(self) -> str:
        return self.llm.get("base_url", "")

    # === Search Configuration ===
    @property
    def search(self) -> Dict[str, Any]:
        return self._config.get("search", {})

    @property
    def max_results(self) -> int:
        return self.search.get("max_results", 20)

    @property
    def days_back(self) -> int:
        return self.search.get("days_back", 1)

    @property
    def relevance_threshold(self) -> int:
        return self.search.get("relevance_threshold", 3)

    @property
    def from_date(self) -> Optional[str]:
        """Start date (YYYY-MM-DD), takes priority over days_back"""
        return self.search.get("from_date", None)

    @property
    def to_date(self) -> Optional[str]:
        """End date (YYYY-MM-DD), defaults to today"""
        return self.search.get("to_date", None)

    # === Scheduler Configuration ===
    @property
    def scheduler(self) -> Dict[str, Any]:
        return self._config.get("scheduler", {})

    @property
    def trigger_time(self) -> str:
        return self.scheduler.get("trigger_time", "21:00")

    @property
    def scheduler_enabled(self) -> bool:
        return self.scheduler.get("enabled", True)

    # === Prompts Configuration ===
    @property
    def research_keywords(self) -> List[str]:
        return self._prompts.get("research_keywords", [])

    @property
    def exclude_keywords(self) -> List[str]:
        return self._prompts.get("exclude_keywords", [])

    @property
    def filter_prompt(self) -> str:
        return self._prompts.get("filter_prompt", "")

    @property
    def summarize_prompt(self) -> str:
        return self._prompts.get("summarize_prompt", "")

    @property
    def email_subject(self) -> str:
        return self._prompts.get("email", {}).get("subject", "PaperSeeker: {date} Papers ({count})")

    @property
    def email_greeting(self) -> str:
        return self._prompts.get("email", {}).get("greeting", "Hello, here are today's paper recommendations.")

    @property
    def email_footer(self) -> str:
        return self._prompts.get("email", {}).get("footer", "")

    @property
    def summarize_threshold(self) -> int:
        """Summary generation threshold"""
        return self._prompts.get("summarize_threshold", 4)

    def reload(self) -> None:
        """Reload configuration"""
        self.load()


# Global configuration instance
_config: Optional[Config] = None


def get_config(config_path: Optional[str] = None, prompts_path: Optional[str] = None) -> Config:
    """Get configuration singleton"""
    global _config
    if _config is None:
        _config = Config(config_path, prompts_path)
    return _config


def reload_config() -> None:
    """Reload configuration"""
    global _config
    if _config is not None:
        _config.reload()
