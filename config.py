"""
Configuration management for SERPENTER
"""

import os
import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Any, List
from langchain_core.language_models.chat_models import BaseChatModel


@dataclass
class Config:
    """Configuration for SERPENTER agent"""

    # LLM configuration
    llm_provider: str = "groq"
    llm_model: str = "llama-3.3-70b-versatile"
    llm_temperature: float = 0.1
    llm_max_tokens: int = 4096
    llm_api_key: Optional[str] = None
    require_llm_api_key: bool = True

    # Agent behavior
    debug: bool = False
    auto_mode: bool = False
    max_iterations: int = 10
    verbose: bool = True
    confirm_commands: bool = False

    # Tool configuration
    tools_enabled: List[str] = field(default_factory=lambda: ["nmap", "netexec", "bash"])
    tool_settings: Dict[str, Any] = field(default_factory=dict)
    use_sudo: bool = False
    sudo_tools: List[str] = field(default_factory=lambda: ["nmap", "netexec", "hashcat"])

    # Output configuration
    log_file: Optional[Path] = None
    save_results: bool = False
    results_dir: Path = Path("./results")

    # Internal assessment configuration
    assessment_ai_synthesis: bool = True
    assessment_require_ai: bool = True
    assessment_redact_evidence: bool = False
    assessment_allow_exploits: bool = False

    # Config file path
    config_file: Optional[Path] = None

    @classmethod
    def from_yaml(cls, config_path: Optional[Path] = None, require_llm: bool = True) -> "Config":
        """Load configuration from YAML file"""
        
        # Default config locations
        if config_path is None:
            possible_paths = [
                Path("config.yaml"),
                Path("serpenter_config.yaml"),
                Path.home() / ".serpenter" / "config.yaml",
                Path("/etc/serpenter/config.yaml"),
            ]
            
            for path in possible_paths:
                if path.exists():
                    config_path = path
                    break
        
        if config_path is None or not config_path.exists():
            # Return default config if no file found
            return cls(require_llm_api_key=require_llm)
        
        # Load YAML
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f) or {}
        
        # Extract LLM settings
        llm_config = config_data.get('llm', {})
        agent_config = config_data.get('agent', {})
        tools_config = config_data.get('tools', {})
        output_config = config_data.get('output', {})
        assessment_config = config_data.get('assessment', {})
        
        return cls(
            # LLM settings
            llm_provider=llm_config.get('provider', 'groq'),
            llm_model=llm_config.get('model', 'llama-3.3-70b-versatile'),
            llm_temperature=llm_config.get('temperature', 0.1),
            llm_max_tokens=llm_config.get('max_tokens', 4096),
            llm_api_key=llm_config.get('api_key'),
            require_llm_api_key=require_llm,
            
            # Agent settings
            debug=agent_config.get('debug', False),
            auto_mode=agent_config.get('auto_mode', False),
            max_iterations=agent_config.get('max_iterations', 10),
            verbose=agent_config.get('verbose', True),
            confirm_commands=agent_config.get('confirm_commands', False),
            
            # Tool settings
            tools_enabled=tools_config.get('enabled', ['nmap', 'netexec', 'bash']),
            tool_settings=tools_config,
            use_sudo=tools_config.get('use_sudo', False),
            sudo_tools=tools_config.get('sudo_tools', ['nmap', 'netexec', 'hashcat']),
            
            # Output settings
            log_file=Path(output_config['log_file']) if output_config.get('log_file') else None,
            save_results=output_config.get('save_results', False),
            results_dir=Path(output_config.get('results_dir', './results')),

            # Internal assessment settings
            assessment_ai_synthesis=assessment_config.get('ai_synthesis', True),
            assessment_require_ai=assessment_config.get('require_ai', True),
            assessment_redact_evidence=assessment_config.get('redact_evidence', False),
            assessment_allow_exploits=assessment_config.get('allow_exploits', False),
            
            config_file=config_path,
        )

    def __post_init__(self):
        """Post-initialization to resolve API keys from environment"""
        
        # Resolve API key from environment if not set
        if not self.llm_api_key:
            env_key_map = {
                'anthropic': 'ANTHROPIC_API_KEY',
                'openai': 'OPENAI_API_KEY',
                'groq': 'GROQ_API_KEY',
                'ollama': None,  # Ollama doesn't need API key for local
            }
            
            env_var = env_key_map.get(self.llm_provider.lower())
            if env_var:
                self.llm_api_key = os.getenv(env_var)
                
                if not self.llm_api_key and self.require_llm_api_key:
                    raise ValueError(
                        f"{env_var} not found. "
                        f"Set it via environment variable or in config.yaml"
                    )

    def get_llm(self) -> BaseChatModel:
        """Get the configured LLM instance"""
        provider = self.llm_provider.lower()
        
        if provider == 'anthropic':
            from langchain_anthropic import ChatAnthropic
            return ChatAnthropic(
                model=self.llm_model,
                anthropic_api_key=self.llm_api_key,
                temperature=self.llm_temperature,
                max_tokens=self.llm_max_tokens,
            )
        
        elif provider == 'openai':
            from langchain_openai import ChatOpenAI
            return ChatOpenAI(
                model=self.llm_model,
                openai_api_key=self.llm_api_key,
                temperature=self.llm_temperature,
                max_tokens=self.llm_max_tokens,
            )
        
        elif provider == 'groq':
            from langchain_groq import ChatGroq
            return ChatGroq(
                model=self.llm_model,
                groq_api_key=self.llm_api_key,
                temperature=self.llm_temperature,
                max_tokens=self.llm_max_tokens,
            )
        
        elif provider == 'ollama':
            from langchain_community.chat_models import ChatOllama
            return ChatOllama(
                model=self.llm_model,
                temperature=self.llm_temperature,
            )
        
        else:
            raise ValueError(
                f"Unsupported LLM provider: {provider}. "
                f"Supported: anthropic, openai, groq, ollama"
            )

    @property
    def model_kwargs(self):
        """Get kwargs for LangChain model initialization (deprecated, use get_llm())"""
        # Keep for backwards compatibility
        return {
            "model": self.llm_model,
            "temperature": self.llm_temperature,
            "max_tokens": self.llm_max_tokens,
        }
