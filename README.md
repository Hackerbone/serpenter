# 🐍 SERPENTER

**S**emi-Autonomous **E**numeration and **R**econnaissance **P**entesting **E**ngine with **N**atural **T**ask **E**xecution via **R**easoning

An AI-powered pentesting agent specialized in Active Directory environments. SERPENTER intelligently executes reconnaissance and enumeration tasks using natural language commands.

## ✨ Features

- 🤖 **Natural Language Interface** - Describe your pentesting objectives in plain English
- 🔧 **Multi-Provider LLM Support** - Choose from Anthropic Claude, OpenAI GPT, Groq, or local Ollama models
- 🛠️ **Intelligent Tool Orchestration** - Automatically chains tools (nmap, netexec, etc.) to accomplish tasks
- 📺 **Real-Time Progress Monitoring** - See tool execution in real-time with streaming output
- 🎛️ **Interactive Visibility Controls** - Toggle debug/verbose/quiet modes on the fly
- 🎯 **AD Pentesting Focus** - Specialized in Active Directory enumeration and reconnaissance
- ⚙️ **Flexible Configuration** - YAML-based config for easy customization
- 📊 **Rich Terminal Output** - Beautiful, informative command-line interface

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd serpenter

# Install dependencies with uv
uv sync

# Set up configuration
cp config.yaml my-config.yaml
# Edit my-config.yaml with your settings
```

### Configure Your LLM Provider

SERPENTER supports multiple LLM providers. Choose one:

**Option 1: Groq (Recommended - Fast & Free Tier)**
```bash
export GROQ_API_KEY='your-groq-api-key'
```
Get your key at: https://console.groq.com/keys

**Option 2: Anthropic Claude**
```bash
export ANTHROPIC_API_KEY='your-anthropic-key'
```

**Option 3: OpenAI**
```bash
export OPENAI_API_KEY='your-openai-key'
```

**Option 4: Ollama (Local, No API Key)**
```bash
ollama pull llama3:70b
# No API key needed!
```

Edit `config.yaml` to select your provider:
```yaml
llm:
  provider: "groq"  # or "anthropic", "openai", "ollama"
  model: "llama-3.3-70b-versatile"
  temperature: 0.1
  max_tokens: 4096
```

### Run SERPENTER

```bash
# One-shot command
uv run serpenter_cli.py run "list all SMB services in 192.168.1.0/24"

# Interactive mode (recommended)
uv run serpenter_cli.py interactive

# With custom config
uv run serpenter_cli.py --config my-config.yaml run "enumerate domain controllers"

# Debug mode (shows detailed tool execution)
uv run serpenter_cli.py --debug run "find accessible shares on 10.0.0.5"
```

### Interactive Mode Commands

```bash
serpenter> /help     # Show all commands
serpenter> /verbose  # Toggle real-time progress (default: ON)
serpenter> /debug    # Toggle detailed debug output
serpenter> /quiet    # Minimal output, fastest execution
serpenter> /status   # Show current settings
serpenter> exit      # Exit SERPENTER
```

See [INTERACTIVE_GUIDE.md](INTERACTIVE_GUIDE.md) for detailed usage.

## 📖 Usage Examples

### Network Discovery
```bash
serpenter run "discover live hosts in 192.168.1.0/24"
serpenter run "find all domain controllers in the subnet"
serpenter run "scan for open SMB ports on 10.0.0.0/24"
```

### SMB Enumeration
```bash
serpenter run "list all SMB shares in 192.168.1.0/24"
serpenter run "enumerate users on 10.0.0.5 via SMB"
serpenter run "find accessible shares with guest access"
```

### Multi-Protocol Enumeration
```bash
serpenter run "test WinRM access on 192.168.1.100"
serpenter run "enumerate LDAP users on domain controller 10.0.0.10"
serpenter run "check RDP access across 192.168.1.0/24"
```

### Complex Tasks
```bash
serpenter run "map the AD environment in 10.0.0.0/24"
serpenter run "find potential privilege escalation paths"
serpenter run "identify misconfigured shares containing credentials"
```

### Certificate Attacks (AD CS)
```bash
serpenter run "enumerate vulnerable certificate templates on 10.0.0.10"
serpenter run "perform ESC1 attack using vulnerable template"
serpenter run "add shadow credentials to target account"
serpenter run "find all AD CS misconfigurations in the domain"
```

## 🔧 Configuration

SERPENTER uses a YAML configuration file for flexibility. See [config.examples.md](config.examples.md) for detailed examples.

### Configuration Structure

```yaml
# LLM Provider
llm:
  provider: "groq"
  model: "llama-3.3-70b-versatile"
  temperature: 0.1
  max_tokens: 4096

# Agent Behavior
agent:
  debug: false
  max_iterations: 10
  auto_mode: false
  verbose: true

# Tools
tools:
  enabled:
    - nmap
    - netexec
    - bash
  
  nmap:
    default_timeout: 300
  
  netexec:
    default_timeout: 180

# Output
output:
  log_file: null
  save_results: false
  results_dir: "./results"
```

### Available LLM Providers

| Provider | Models | Speed | Cost | Best For |
|----------|--------|-------|------|----------|
| **Groq** | llama-3.3-70b, mixtral-8x7b | ⚡⚡⚡ | 💰 Free tier | General use |
| **Anthropic** | claude-sonnet-4 | ⚡⚡ | 💰💰 | Complex reasoning |
| **OpenAI** | gpt-4, gpt-3.5 | ⚡⚡ | 💰💰💰 | Reliable performance |
| **Ollama** | llama3:70b, mixtral | ⚡ | 💰 Free | Privacy, offline |

## 🛠️ Tools

SERPENTER includes the following pentesting tools:

### nmap_scan
Network discovery and port scanning
- Quick host discovery
- Service version detection
- Vulnerability scanning

### netexec (Generic)
Multi-protocol enumeration supporting:
- **SMB**: shares, users, groups, sessions
- **WinRM**: user enumeration, command execution
- **LDAP**: users, groups, computers
- **RDP**: access testing
- **SSH**: authentication testing
- And more...

### impacket
Python-based AD exploitation toolkit:
- **secretsdump**: Extract credentials from SAM/NTDS
- **GetUserSPNs**: Kerberoasting attacks
- **GetNPUsers**: AS-REP roasting
- **psexec/wmiexec**: Remote code execution
- And many more Impacket scripts

### ldapsearch
LDAP enumeration for Active Directory:
- Enumerate users, computers, groups
- Find privileged accounts
- Discover Kerberoastable accounts
- Identify AS-REP roastable users
- Query GPOs and domain trusts

### hashcat
Password cracking:
- NTLM hashes
- NetNTLMv2
- Kerberoast tickets
- AS-REP hashes

### certipy
Active Directory Certificate Services (AD CS) attacks:
- **find**: Enumerate certificate templates and identify vulnerabilities (ESC1-8)
- **req**: Request certificates from templates
- **auth**: Authenticate using certificates to obtain NTLM hashes/TGT
- **shadow**: Shadow credentials attacks
- **ca**: Dump CA certificates and keys
- **forge**: Create golden certificates
- Support for all major AD CS attack scenarios

### bash_execute
Execute custom bash commands (with safety checks)

## 🏗️ Architecture

```
User Input (Natural Language)
    ↓
SERPENTER CLI
    ↓
Config (YAML) → Agent (LangGraph)
    ↓
LLM Provider (Groq/Claude/GPT/Ollama)
    ↓
Tool Selection & Execution
    ↓
    ├→ nmap_scan
    ├→ netexec (smb/winrm/ldap/rdp/ssh)
    └→ bash_execute
    ↓
Results & Analysis
    ↓
User Output (Rich Terminal)
```

## 🔐 Security Considerations

- **Dangerous commands are blocked** by default in bash_execute
- **API keys should never be committed** to version control
- **Use responsibly** - Only scan networks you have permission to test
- **Debug mode may expose sensitive data** - Use cautiously in production

## 📚 Documentation

- [Interactive Mode Guide](INTERACTIVE_GUIDE.md) - Real-time monitoring and visibility controls
- [Configuration Guide](CONFIGURATION_GUIDE.md) - Complete configuration reference
- [Configuration Examples](config.examples.md) - Provider-specific examples
- [Tool Documentation](tools.py) - Tool implementation details

## 🧪 Development

```bash
# Install development dependencies
uv sync

# Run tests
uv run pytest

# Format code
uv run black .

# Lint
uv run ruff check .
```

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📝 License

MIT License - See LICENSE file for details

## ⚠️ Disclaimer

This tool is for authorized security testing only. Users are responsible for complying with all applicable laws and regulations. Unauthorized access to computer systems is illegal.

## 🙏 Acknowledgments

Built with:
- [LangChain](https://github.com/langchain-ai/langchain) & [LangGraph](https://github.com/langchain-ai/langgraph)
- [Anthropic Claude](https://www.anthropic.com/) / [Groq](https://groq.com/) / [OpenAI](https://openai.com/)
- [Rich](https://github.com/Textualize/rich) for beautiful terminal output
- [Click](https://click.palletsprojects.com/) for CLI
- Security tools: nmap, netexec, impacket, certipy, hashcat, ldapsearch

---

**Made with 🐍 for the pentesting community**
