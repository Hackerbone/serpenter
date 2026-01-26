# [un]prompted 2026 - Final CFP Submission

**Conference:** [un]prompted - The AI Security Practitioner Conference  
**Submission Deadline:** January 28, 2026, 11:59 PM PST  
**Track:** Track 3 - Using AI for Offensive Security  
**Format:** 20-minute talk + 10 minutes Q&A

---

## 1. SESSION TITLE

```
SERPENTER: An Autonomous Pentesting Assistant for Active Directory Engagements
```

---

## 2. DESCRIPTION
**A short paragraph describing your talk for the conference website**

Manual AD pentesting is tedious - enumerate users, Kerberoast accounts, crack hashes, hunt ESC certificates, spray credentials, pivot laterally. Each step requires context from the previous one. What if an autonomous assistant could execute this entire workflow while you observe?

SERPENTER is an LLM orchestrator designed to streamline AD pentesting workflows. It uses persistent memory, chains tools through structured schemas (not hallucinated syntax), auto-detects failures and retries with corrected commands, and most importantly, executes complete attack chains, not just suggestions. Feed it discovered credentials or start from scratch; it handles the rest.

Live demo on GOAD showing end-to-end autonomous AD testing: user enumeration → Kerberoasting → hash cracking → ESC certificate hunting → lateral movement. Watch the tool chain operations, recover from errors, and adapt its approach in real-time. Open source, MIT licensed, built for real-world pentesting workflows.

---

## 3. TALK OUTLINE
**A detailed abstract and description of the talk flow for the CFP review committee. This content will not be published on the website.**

### THE TOOL & WHAT IT DOES

SERPENTER is an autonomous assistant designed to streamline AD pentesting workflows. It's not a chatbot that gives you suggestions, it's an orchestrator that executes complete attack chains while you observe and guide.

**What makes SERPENTER different:**
- **Intuitive thinking:** The LLM reasons about attack context, what's been discovered, what's been tried, what paths remain unexplored.
- **Smart chaining:** Output from one tool feeds directly into the next. Kerberoasted hash → hashcat → cracked credential → lateral movement. No manual copy-pasting.
- **Schema-enforced accuracy:** Commands are built programmatically through Pydantic schemas, not generated as raw strings. The LLM selects parameters; the tool wrapper builds the correct syntax.
- **Auto-recovery from failures:** When a command fails, structured error output feeds back to the LLM, which analyzes the failure and generates a corrected approach.
- **Flexible entry points:** Start from scratch with just an IP range, or provide discovered credentials and continue from there.
- **In-built memory:** A graph database designed to maintain the complete attack state, every finding, every attempt, every relationship. Resume weeks later with full context.

This talk showcases SERPENTER as a practical autonomous assistant for AD pentesters and security engineers, demonstrating how structured LLM orchestration with persistent memory transforms pentesting workflows.

### SERPENTER ARCHITECTURE

**Layer 1: LLM Orchestrator which uses ReAct**
- Reasoning about attack context and next steps
- Automatic tool chaining, output flows seamlessly between operations
- Streaming execution with real-time feedback
- Multi-provider LLM support: Groq, Claude, GPT-4, and local LLMs like Ollama

**Layer 2: Stateful Graph Memory**
- Persistent storage of complete AD attack state
- Nodes: User, Computer, Group, Credential, Certificate, Finding, Session
- Relationships: MemberOf, HasSPN, AdminTo, CanPSRemote, TrustedBy, CrackedFrom, TriedOn, VulnerableTo
- Feeds context back into LLM for informed decision-making
- Session persistence: pick up exactly where you left off

**Layer 3: Schema-Enforced Tools for the AI Agent (Anti-Hallucination)**
- **Pydantic input schemas** for every tool, LLM can only provide valid parameters
- **Programmatic command building**, not string concatenation from LLM output
- **Preset query patterns**, LDAP filters, action maps, script variants are hardcoded
- **Structured output parsing**, tool output is parsed and formatted for LLM consumption
- **Error classification**, failures return structured messages the LLM can act on

**How Hallucination is Prevented:**

The LLM selects *what* to do (protocol, action, target). The tool wrapper builds *how* to do it correctly.

Essentially giving the model an understanding of the tool makes it return deterministic outputs.

### TALK FLOW (20 minutes + 10 min Q&A)

**Minutes 0-3: The Problem with Current AI Tools**
- Current AI assistants (ChatGPT, Claude) can suggest pentesting steps but can't execute them
- When they do have tool access, they hallucinate syntax, forget context, can't chain operations
- What pentesters need: an assistant that executes complete workflows with correct syntax
- *Quick setup to show why SERPENTER exists*

**Minutes 3-8: SERPENTER Tool Showcase - Anti-Hallucination Architecture**
- **Architecture overview:** LLM orchestrator + In-built memory + schema-enforced tool wrappers
  
- **How we prevent hallucination (live code walkthrough):**
  - **Pydantic schemas:** LLM provides structured parameters, not raw command strings
  - **Programmatic command building:** Tool wrappers construct correct syntax from parameters
  - **Preset patterns:** LDAP filters, action flags, script names are hardcoded lookups
  - **Validation:** Invalid protocols/actions rejected before execution
  
- **Updated tool integrations:**
  - NetExec (SMB, LDAP, WinRM enumeration and exploitation)
  - Impacket suite (GetUserSPNs, getTGT, secretsdump)
  - Certipy (ESC1-ESC8 certificate abuse)
  - BloodHound integration, Hashcat, nmap, ldapsearch
  
- **Neo4j as memory:** Quick view of attack state graph, users, credentials, relationships all tracked

**Minutes 8-16: Live Demo - End-to-End AD Pentest on GOAD**
- **Scenario 1: Starting from scratch**
  - Give SERPENTER only a target IP range
  - Watch autonomous execution: network scan → enumeration → inital access → privilege escalation
  - Each step chains automatically, no manual intervention
  
- **Scenario 2: Starting with user-driven input (flexible entry point)**
  - Provide discovered credentials/tickets or any nudge to move forward as an entry point
  - SERPENTER continues from there: lateral movement, privilege escalation, further enumeration
  
- **Scenario 3: ESC Certificate Hunting**
  - "Find vulnerable AD CS templates"
  - Certipy enumeration → identifies ESC1/ESC8 → generates exploitation commands

**Minutes 16-18: Error Recovery Demo (Key Differentiator)**
- **Deliberately trigger failures to show auto-recovery:**
  - Wrong credentials → tool returns structured error → LLM analyzes → tries alternative approach
  - Timeout on slow scan → LLM receives timeout message → adjusts parameters and retries
  - Missing tool → clear error message → LLM suggests installation or alternative
  
- **How error feedback works:**
  ```
  Tool returns: "NetExec scan failed: STATUS_ACCESS_DENIED"
  LLM observes: "Access denied with null session"
  LLM decides: "Try anonymous LDAP bind instead"
  LLM executes: ldapsearch with anonymous=True
  ```
  
- **Key point:** Errors don't halt execution, they inform the next decision

**Minutes 18-20: Practical Use Cases & Limitations**
- **Who this helps:**
  - AD pentesters: automate tedious enumeration and chaining
  - Security engineers: validate AD hardening with real attack paths
  - Junior testers: learn attack methodology by watching and querying
  
- **What it's good at:**
  - Multi-step workflows with persistent state
  - Discovery, enumeration, credential attacks, lateral movement
  - Recovering from common errors automatically
  
- **What it's not:**
  - Not a replacement for pentester expertise
  - Not for novel exploitation requiring creative problem-solving
  - Assistant, not autopilot

**Minutes 20-30: Q&A - Deep Dives**
- Schema design and anti-hallucination patterns
- Adding custom tools with Pydantic schemas
- Neo4j schema and graph query patterns
- LLM provider comparison (Groq, Claude, GPT-4, Ollama)
- Error handling edge cases

### WHAT MAKES THIS TALK VALUABLE

**A practical tool, not a research concept:**

This isn't a theoretical framework or proof-of-concept. SERPENTER is a working tool that AD pentesters can use today to streamline their workflows. The talk demonstrates real-world utility through live demos.

**Engineering that solves real problems:**
- **Execution over advice:** LLMs that suggest steps are common. LLMs that execute multi-step attack chains are rare.
- **Anti-hallucination by design:** Pydantic schemas + programmatic command building = correct syntax every time.
- **Auto-recovery:** Structured error feedback enables the LLM to adapt and retry with corrected approaches.
- **Persistent memory:** A stateful memory ensures nothing is forgotten across sessions.

**Why pentesters should care:**
- Automates the tedious parts of AD testing (enumeration, spraying, hash collection)
- Commands are built correctly, no more fixing hallucinated tool syntax
- Failures don't stop execution, they inform the next decision
- Start anywhere: from scratch or from at any point while conducting pentesting

**Addressing the "LLMs hallucinate syntax" concern:**
- LLM never generates raw command strings
- Tool wrappers use hardcoded command patterns with LLM-provided parameters
- Every tool has a Pydantic schema defining valid inputs
- Invalid inputs rejected before execution
- *Demo will show this working, not just assert it*

**Technically transparent:**
- Full architecture explained with code examples
- Anti-hallucination patterns shown in action
- Error recovery demonstrated live
- Honest about limitations
- MIT licensed, use it, extend it, contribute back

### KEY TAKEAWAYS

Attendees will leave with:
1. Understanding how LLM orchestration can automate end-to-end AD pentesting workflows
2. **Anti-hallucination patterns:** Pydantic schemas + programmatic command building to ensure correct syntax
3. **Error recovery techniques:** Structured error feedback that enables LLM to adapt and retry
4. Live demonstration of tool chaining: user enumeration → Kerberoasting → hash cracking → lateral movement
5. How Neo4j graph memory enables intelligent decision-making and session persistence
6. Practical integration patterns for NetExec, Impacket, Certipy, ldapsearch, and other AD tools
7. How to add custom tools with schema enforcement
8. Honest assessment of what autonomous pentesting can and cannot do
9. MIT licensed tool they can use, extend, and contribute to

### DEMONSTRATION REQUIREMENTS

All demos are live with backup recordings:
- SERPENTER on GOAD (Game of Active Directory) lab
- End-to-end attack scenarios: enumeration → Kerberoasting → cracking → ESC certificates → lateral movement
- Neo4j visualization showing attack state graph
- Multiple entry point demos: from scratch + with provided credentials
- Real tool execution with actual output
- Pre-populated fallback database if network fails
- Requires: laptop, internet for LLM API, Neo4j + GOAD running locally

### THE BOTTOM LINE

AD pentesting involves tedious, repetitive workflows: enumerate users, find Kerberoastable accounts, crack hashes, hunt vulnerable certificates, spray credentials, move laterally. SERPENTER automates these chains with an LLM orchestrator that executes, not just advises.

The tool features schema-enforced command building (no hallucinated syntax), automatic error recovery, intelligent chaining, and Neo4j-backed memory. Start from scratch or provide credentials; it handles the rest.

Tested on GOAD. Open-source (MIT licensed). Working tool for real AD pentesting workflows.

**Note to committee:** This is a tool showcase talk demonstrating practical LLM orchestration engineering. Key technical content: how Pydantic schemas and programmatic command building prevent hallucination, how structured error feedback enables auto-recovery. 5 minutes on architecture with code examples. 10 minutes of live demos including deliberate error triggering to show recovery. Prepared for deep technical Q&A on AD attack paths, Kerberos abuse, LDAP queries, and tool wrapper patterns.

---

## 4. ADDITIONAL NOTES
**Any relevant context, requirements, or comments you'd like the review committee to consider**

### SPEAKER BACKGROUND

**Sitaraman Subramanian**  
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

**Kathan Desai**  
<insert blurb>

### SERPENTER: HOW IT WORKS

**The Orchestration Loop:**

SERPENTER's power comes from its ability to chain operations intelligently while maintaining complete attack context, and recovering from failures automatically.

**How tool chaining works:**
1. User provides goal: "Find path to Domain Admin" or "Kerberoast and crack accounts"
2. LLM reasons about current state and selects appropriate tool + parameters
3. **Tool wrapper validates input** via Pydantic schema
4. **Tool wrapper builds command** programmatically (not from LLM-generated strings)
5. Command executes with timeout handling
6. **Output parser extracts structured results** for LLM consumption
7. LLM evaluates results, feeds output into next decision
8. Repeat until goal achieved or manual intervention needed

**How error recovery works (key differentiator):**
```python
# Tool execution returns structured error:
if result.returncode != 0:
    return f"NetExec scan failed: {result.stderr}"

# Error flows back to LLM as observation
# LLM sees: "NetExec scan failed: STATUS_ACCESS_DENIED"
# LLM reasons: "Null session failed, trying authenticated scan"
# LLM selects: ldapsearch tool with credentials
# Execution continues with alternative approach
```

**Anti-hallucination through schema enforcement:**
```python
class ImpacketInput(BaseModel):
    script: str = Field(description="secretsdump, GetUserSPNs, psexec...")
    target: str
    username: Optional[str]
    domain: Optional[str]
    # LLM fills these fields; wrapper builds: secretsdump.py domain/user@target

# Script names resolved via lookup table, no typos possible:
SCRIPT_VARIANTS = {
    "secretsdump": "secretsdump.py",
    "getuserspns": "GetUserSPNs.py",  # Correct casing
    "getnpusers": "GetNPUsers.py",
    ...
}
```

**Neo4j as persistent memory:**
- Every finding stored with relationships: (User)-[HasSPN]->(True), (Credential)-[CrackedFrom]->(Hash)
- Every attempt tracked: prevents repeating failed attacks
- Flexible queries: "What Kerberoastable accounts haven't we cracked?"
- Persistent across sessions: pick up exactly where you left off

**Flexible entry points:**
- **From scratch:** Provide IP range, SERPENTER handles discovery through exploitation
- **With credentials:** Provide domain\user:password, continue from authenticated enumeration
- **Mid-engagement:** Import BloodHound data, continue with context

This is what makes SERPENTER an autonomous assistant, not just another AI chatbot, it works alongside pentesters, handling execution while they guide strategy.

### TECHNICAL DEPTH AVAILABLE

The talk provides detailed coverage of:
- **Anti-hallucination architecture:** Pydantic schemas, programmatic command building, validation patterns
- **Error handling and recovery:** Structured error feedback, timeout handling, retry logic
- **Tool wrapper design:** How each tool (NetExec, Impacket, Certipy, ldapsearch) is wrapped with schemas
- **Preset query patterns:** LDAP `QUERY_PRESETS` dict, action maps, script variant lookups
- **Output parsing:** Extracting structured data from tool output for LLM consumption
- **Neo4j schema:** Attack state storage, relationships, and query patterns
- **Chaining mechanics:** How parsed output feeds context into next decision
- **Adding custom tools:** Pattern for creating new tool wrappers with Pydantic schemas
- **Multi-LLM support:** Groq (free), Claude, GPT-4, Ollama, comparative observations

**Prepared to demonstrate and discuss:**
- Why LLM never generates raw command strings
- How schema validation catches bad inputs before execution
- How error messages are structured for LLM consumption
- Real code walkthrough of tool wrapper patterns

Q&A available for deeper technical discussion and implementation details.

### DEMONSTRATION ON GOAD

All demos use GOAD (Game of Active Directory) - realistic 5-domain AD forest.

**End-to-end attack scenarios:**
- **From scratch:** Network discovery → user enumeration → Kerberoasting → hash cracking → lateral movement
- **With credentials:** Authenticated enumeration → privilege escalation paths → ESC certificate hunting
- **ESC certificates:** Certipy enumeration → vulnerable template identification → exploitation commands

**Error recovery demonstration (addressing skepticism about LLM reliability):**
- Deliberately trigger authentication failures → watch LLM analyze and adapt
- Show timeout handling → LLM adjusts approach
- Demonstrate schema validation catching bad inputs
- **Key message:** Failures become feedback, not dead ends

**What attendees will see:**
- Real tool execution with actual output (not simulated)
- Intelligent chaining: watch output flow into next decision
- Schema-enforced command building (no hallucinated syntax)
- Error recovery in action: watch the tool adapt to failures
- Neo4j graph showing attack state building in real-time
- Session continuity: close and reopen with full context preserved

**Focus on practical utility:**
- How this helps real pentesting workflows
- Proving the anti-hallucination claims through live demo, not just assertions

### OPEN SOURCE COMMITMENT

SERPENTER is MIT licensed with full code available on GitHub:
- Complete implementation including Neo4j schema
- Tool wrapper examples for customization
- Documentation for setup and deployment
- No vendor lock-in or commercial agenda
- Community can extend and adapt for their tools

### TECHNICAL REQUIREMENTS

What I'll bring:
- Laptop with SERPENTER, Neo4j, and GOAD configured
- Internet connection for LLM APIs (with phone hotspot backup)
- Pre-recorded backup videos of all demos
- Pre-populated Neo4j database (fallback if time-constrained)

What I need:
- Screen connection (HDMI) for terminal + Neo4j Browser display
- Stable internet access

No slide deck needed - this is live terminal, code, and graph visualization.

---

**An autonomous pentesting assistant for AD. Schema-enforced accuracy. Auto-recovers from failures. Open source. Tested on GOAD. 🐍**
