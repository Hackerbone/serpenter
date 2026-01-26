# SERPENTER: An Autonomous Pentesting Assistant for Active Directory Engagements

**Conference:** [un]prompted 2026  
**Track:** Track 3 - Using AI for Offensive Security  
**Format:** 20-minute talk + 10 minutes Q&A

---

## Abstract

Manual AD pentesting is tedious. Enumerate users, Kerberoast accounts, crack hashes, hunt ESC certificates, spray credentials, pivot laterally. Each step requires context from the previous one. What if an autonomous assistant could execute this entire workflow while you observe?

SERPENTER is an LLM orchestrator designed to streamline AD pentesting workflows. It uses persistent memory, chains tools through structured schemas (not hallucinated syntax), auto-detects failures and retries with corrected commands, and most importantly, executes complete attack chains, not just suggestions. Feed it discovered credentials or start from scratch - it handles the rest.

### Why SERPENTER vs ChatGPT/Claude?

Regular AI assistants like ChatGPT or Claude can suggest pentesting steps, but they can't execute them. When they do have tool access, they hallucinate syntax, forget context between commands, and can't chain operations together. You end up copy-pasting commands, fixing typos, and manually connecting the dots.

SERPENTER is different:
- **Actually executes commands** instead of just suggesting them
- **Never hallucinates syntax** because it uses Pydantic schemas and programmatic command building
- **Remembers everything** with a Neo4j graph database that tracks users, credentials, findings, and relationships
- **Chains operations automatically** so Kerberoasted hashes flow into hashcat, cracked credentials flow into lateral movement
- **Recovers from errors** by analyzing structured failure messages and adapting its approach

### Architecture Overview

**Layer 1: LLM Orchestrator (ReAct Pattern)**
- Reasons about attack context and next steps
- Uses multiple LLM providers: Groq, Claude, GPT-4, Ollama
- Streams execution with real-time feedback
- Chains tools automatically based on output

**Layer 2: Graph Memory (Neo4j)**
- Persistent storage of complete AD attack state
- Tracks entities: User, Computer, Group, Credential, Certificate, Finding
- Tracks relationships: MemberOf, HasSPN, AdminTo, CanPSRemote, CrackedFrom, TriedOn
- Session persistence so you can pick up exactly where you left off

**Layer 3: Schema-Enforced Tools (Anti-Hallucination)**
- Every tool has a Pydantic input schema
- LLM provides parameters, not raw command strings
- Tool wrappers build commands programmatically with hardcoded patterns
- LDAP filters, action flags, script names are all lookup tables
- Structured error output that LLM can analyze and act on

**How We Prevent Hallucination:**

The LLM decides **what** to do (which protocol, which action, which target). The tool wrapper decides **how** to do it correctly (exact syntax, flags, formatting).

Example: LLM says "use GetUserSPNs on domain.local with these credentials". Tool wrapper looks up the correct script path, builds the command with proper escaping, validates all parameters through Pydantic, then executes. The LLM never generates raw strings like "GetUserSPNs.py domain/user@target".

---

## Description

### How SERPENTER Works

**The Execution Loop:**

1. User provides a goal: "Find path to Domain Admin" or "Kerberoast and crack accounts"
2. LLM reasons about current state (queries Neo4j) and selects next tool + parameters
3. Tool wrapper validates input via Pydantic schema
4. Tool wrapper builds command programmatically (not from LLM strings)
5. Command executes with timeout handling
6. Output parser extracts structured results
7. Results stored in Neo4j and fed back to LLM
8. LLM evaluates and selects next action
9. Loop continues until goal achieved

**Error Recovery (Key Differentiator):**

When a command fails, the tool returns structured error messages:

```
Tool returns: "NetExec scan failed: STATUS_ACCESS_DENIED"
LLM observes: "Access denied with null session"
LLM decides: "Try anonymous LDAP bind instead"
LLM executes: ldapsearch with anonymous=True
```

Failures don't halt execution. They inform the next decision.

**Tool Integration:**

SERPENTER wraps these tools with schema-enforced interfaces:
- NetExec (SMB, LDAP, WinRM enumeration and exploitation)
- Impacket suite (GetUserSPNs, getTGT, secretsdump, psexec)
- Certipy (ESC1-ESC8 certificate vulnerability hunting)
- BloodHound integration
- Hashcat for hash cracking
- nmap, ldapsearch, and custom tools

Each tool has:
- Pydantic schema defining valid inputs
- Hardcoded command patterns (no string generation)
- Preset query patterns for complex operations
- Structured output parsers
- Error classification for recovery

**Anti-Hallucination Example:**

```python
class ImpacketInput(BaseModel):
    script: str  # LLM picks: "secretsdump"
    target: str
    username: Optional[str]
    domain: Optional[str]

# Wrapper resolves via lookup:
SCRIPT_VARIANTS = {
    "secretsdump": "secretsdump.py",
    "getuserspns": "GetUserSPNs.py",  # Correct casing
    "getnpusers": "GetNPUsers.py",
}

# Builds: secretsdump.py DOMAIN/USER@TARGET
# LLM never sees or generates this string
```

**Flexible Entry Points:**

You can start SERPENTER from anywhere in your workflow:
- From scratch: provide IP range, it does network discovery through exploitation
- With credentials: provide domain\user:password, continues from authenticated enumeration
- Mid-engagement: import BloodHound data, continue with full context

### Future Use Cases (Planned)

**Post-Exploitation Automation:**
- Automated persistence mechanism deployment
- Golden ticket generation and usage
- DCSync attack chains
- GPO abuse detection and exploitation

**Cloud AD Integration:**
- Azure AD enumeration via AzureHound
- Hybrid AD attack paths (on-prem to cloud)
- Entra ID privilege escalation chains

**Defensive Capabilities:**
- Attack simulation for blue team testing
- Automated detection of misconfigurations
- Security posture validation

**Extended Tool Support:**
- Rubeus integration for Kerberos attacks
- PowerView operations through PowerShell
- Custom exploit module integration
- Red team C2 framework connectors

**Multi-Domain Forests:**
- Trust relationship enumeration
- Cross-domain attack path discovery
- Forest privilege escalation chains

---

## Talk Outline

**Minutes 0-3: The Problem with Current AI Tools**
- ChatGPT and Claude suggest steps but can't execute them
- When they have tool access, they hallucinate syntax and forget context
- Pentesters need an assistant that executes complete workflows correctly
- Quick setup showing why SERPENTER exists

**Minutes 3-8: SERPENTER Architecture Deep Dive**
- Three-layer architecture: orchestrator + memory + schema-enforced tools
- Live code walkthrough of anti-hallucination design:
  - Pydantic schemas ensure valid parameters only
  - Programmatic command building (not string concatenation)
  - Preset patterns: LDAP filters, action flags, script lookups are hardcoded
  - Validation catches bad inputs before execution
- Tool integrations: NetExec, Impacket, Certipy, BloodHound, hashcat
- Neo4j memory: visualize the attack state graph

**Minutes 8-16: Live Demo on GOAD**

*Scenario 1: Starting from scratch*
- Provide only target IP range
- Watch autonomous execution: scan → enumerate → initial access → privilege escalation
- Each step chains automatically

*Scenario 2: Starting with credentials*
- Provide discovered credentials as entry point
- SERPENTER continues: lateral movement → privilege escalation → further enumeration

*Scenario 3: ESC Certificate Hunting*
- "Find vulnerable AD CS templates"
- Certipy enumeration → identifies ESC1/ESC8 → generates exploitation commands

**Minutes 16-18: Error Recovery Demo**

Deliberately trigger failures to show auto-recovery:
- Wrong credentials → structured error → LLM analyzes → tries alternative
- Timeout on slow scan → LLM adjusts parameters and retries
- Missing tool → clear error → LLM suggests installation or alternative

Key point: errors become feedback, not dead ends.

**Minutes 18-20: Practical Use Cases & Limitations**

Who this helps:
- AD pentesters: automate tedious enumeration and chaining
- Security engineers: validate AD hardening with real attack paths
- Junior testers: learn attack methodology by watching

What it's good at:
- Multi-step workflows with persistent state
- Discovery, enumeration, credential attacks, lateral movement
- Recovering from common errors automatically

What it's not:
- Not a replacement for pentester expertise
- Not for novel exploitation requiring creative thinking
- Assistant, not autopilot

**Minutes 20-30: Q&A**
- Schema design and anti-hallucination patterns
- Adding custom tools with Pydantic schemas
- Neo4j schema and graph query patterns
- LLM provider comparison
- Error handling edge cases

---

## Speaker Descriptions

### Sitaraman Subramanian

Leading Product Development, Security & Compliance

**Conference Presentations:**
- BlackHat USA Arsenal Presenter 2025
- Microsoft BlueHat Presenter 2024

**Certifications & Recognition:**
- eJPT Certified
- C-AI/MLPentester holder
- Google Code-in 2019 winner

**Experience:**
- 10+ years building products and security solutions
- Expertise spanning Fullstack Development, DevSecOps, Cloud Solutions, and offensive security
- Built BugBase (Bug Bounty Platform) from ground up
- Active open-source contributor

### Kathan Desai

[To be filled]

---

## Technical Requirements

**What we'll bring:**
- Laptop with SERPENTER, Neo4j, and GOAD configured
- Internet connection for LLM APIs (phone hotspot backup)
- Pre-recorded backup videos of all demos
- Pre-populated Neo4j database as fallback

**What we need:**
- Screen connection (HDMI) for terminal + Neo4j Browser
- Stable internet access

No slide deck needed - this is live terminal, code, and graph visualization.

---

**An autonomous pentesting assistant for AD. Schema-enforced accuracy. Auto-recovers from failures. Open source. Tested on GOAD.**
