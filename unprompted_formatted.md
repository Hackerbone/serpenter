# Session Submission: SERPENTER

## Session Title

**SERPENTER: An Open Sourced Autonomous Pentesting Assistant for Active Directory Engagements**

---

## Description

SERPENTER is an open source AI assistant that automates Active Directory pentesting from start to finish. Unlike ChatGPT that only suggests commands, SERPENTER actually executes them without hallucinating syntax, remembers all findings, chains attacks automatically, and recovers from failures. This talk demonstrates live autonomous attacks on a lab environment.

---

## Talk Outline

### Abstract

This talk demonstrates how SERPENTER automates complex Active Directory pentesting workflows using LLM orchestration with schema-enforced tool execution and persistent graph memory. The session includes live demonstrations on the GOAD lab environment showing autonomous execution from initial reconnaissance to privilege escalation.

Regular AI assistants like ChatGPT can suggest pentesting steps, but they can't execute them. When they do have tool access, they hallucinate syntax, forget context between commands, and can't chain operations together. You end up copy-pasting commands, fixing typos, and manually connecting the dots. SERPENTER solves these problems by actually executing commands instead of just suggesting them, never hallucinating syntax through Pydantic schema validation, remembering everything with a Neo4j graph database that tracks users, credentials, findings, and relationships, chaining operations automatically so Kerberoasted hashes flow into hashcat and cracked credentials flow into lateral movement, and recovering from errors by analyzing structured failure messages and adapting its approach.

SERPENTER employs a three-layer architecture. Layer 1 is the LLM Orchestrator using the ReAct pattern, which reasons about attack context and next steps, uses multiple LLM providers (Groq, Claude, GPT-4, Ollama), streams execution with real-time feedback, and chains tools automatically based on output. Layer 2 is Graph Memory using Neo4j for persistent storage of complete AD attack state, tracking entities (User, Computer, Group, Credential, Certificate, Finding) and relationships (MemberOf, HasSPN, AdminTo, CanPSRemote, CrackedFrom, TriedOn) with session persistence so you can pick up exactly where you left off. Layer 3 is Schema-Enforced Tools designed to prevent hallucination - every tool has a Pydantic input schema, the LLM provides parameters (not raw command strings), tool wrappers build commands programmatically with hardcoded patterns, LDAP filters and action flags are lookup tables, and structured error output enables the LLM to analyze and act on failures.

The anti-hallucination design is central: The LLM decides **what** to do (which protocol, which action, which target) while the tool wrapper decides **how** to do it correctly (exact syntax, flags, formatting). For example, the LLM says "use GetUserSPNs on domain.local with these credentials" and the tool wrapper looks up the correct script path, builds the command with proper escaping, validates all parameters through Pydantic, then executes. The LLM never generates raw strings like "GetUserSPNs.py domain/user@target".

SERPENTER wraps industry-standard tools with schema-enforced interfaces: NetExec (SMB, LDAP, WinRM enumeration and exploitation), Impacket suite (GetUserSPNs, getTGT, secretsdump, psexec), Certipy (ESC1-ESC8 certificate vulnerability hunting), BloodHound integration, Hashcat for hash cracking, and nmap/ldapsearch/custom tools. Each tool includes Pydantic schema for valid inputs, hardcoded command patterns (no string generation), preset query patterns for complex operations, structured output parsers, and error classification for recovery.

You can start SERPENTER from anywhere in your workflow: from scratch (provide IP range, it does network discovery through exploitation), with credentials (provide domain\user:password, continues from authenticated enumeration), or mid-engagement (import BloodHound data, continue with full context). The execution loop operates continuously: user provides a goal, LLM queries Neo4j and selects next tool + parameters, tool wrapper validates via Pydantic, command executes with timeout handling, output parser extracts results, results stored in Neo4j and fed back to LLM, LLM evaluates and selects next action, loop continues until goal achieved.

### Outline of the Talk

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

## Additional Notes

### Conference & Format

- **Conference:** [un]prompted 2026
- **Track:** Track 3 - Using AI for Offensive Security
- **Format:** 20-minute talk + 10 minutes Q&A

### Speaker Information

**Sitaraman Subramanian** - Leading Product Development, Security & Compliance

Conference Presentations:
- BlackHat USA Arsenal Presenter 2025
- Microsoft BlueHat Presenter 2024

Certifications & Recognition:
- eJPT Certified
- C-AI/MLPentester holder
- Google Code-in 2019 winner

Experience:
- 10+ years building products and security solutions
- Expertise spanning Fullstack Development, DevSecOps, Cloud Solutions, and offensive security
- Built BugBase (Bug Bounty Platform) from ground up
- Active open-source contributor

**Kathan Desai** - [To be filled]

### Technical Requirements

**What we'll bring:**
- Laptop with SERPENTER, Neo4j, and GOAD configured
- Internet connection for LLM APIs (phone hotspot backup)
- Pre-recorded backup videos of all demos
- Pre-populated Neo4j database as fallback

**What we need:**
- Screen connection (HDMI) for terminal + Neo4j Browser
- Stable internet access

No slide deck needed - this is live terminal, code, and graph visualization.

### Future Roadmap

Future development includes post-exploitation automation (persistence mechanisms, golden tickets, DCSync, GPO abuse), cloud AD integration for hybrid attack paths between on-premises and Azure/Entra ID environments, defensive capabilities for blue team attack simulation and security posture validation, extended tool support for Rubeus, PowerView, custom exploits and C2 framework connectors, and multi-domain forest enumeration with trust relationship exploitation and cross-domain privilege escalation chains.

### Project Status

Open source. Tested on GOAD (Game of Active Directory). An autonomous pentesting assistant for AD with schema-enforced accuracy that auto-recovers from failures.
