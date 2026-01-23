"""
Configuration management for SERPENTER
"""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class Config:
    """Configuration for SERPENTER agent"""

    # Agent behavior
    debug: bool = False
    auto_mode: bool = False
    max_iterations: int = 10

    # API configuration
    anthropic_api_key: Optional[str] = None
    model: str = "claude-sonnet-4-20250514"

    # Tool configuration
    tools_enabled: list = None

    # Output configuration
    verbose: bool = True
    log_file: Optional[Path] = None

    def __post_init__(self):
        # Get API key from environment
        if not self.anthropic_api_key:
            self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

        if not self.anthropic_api_key:
            raise ValueError(
                "ANTHROPIC_API_KEY not found. "
                "Set it via environment variable or pass to Config()"
            )

        # Default tools
        if self.tools_enabled is None:
            self.tools_enabled = ["nmap", "netexec", "bash"]

    @property
    def model_kwargs(self):
        """Get kwargs for LangChain model initialization"""
        return {
            "model": self.model,
            "anthropic_api_key": self.anthropic_api_key,
            "temperature": 0.1,  # Low temperature for precise tool usage
            "max_tokens": 4096,
        }
