# Beyond Brute Force: Building an AI-Orchestrated Active Directory Pentesting Agent

**A Practical Demonstration with SERPENTER**

**An Open-Source, Non-Commercial Research Project**

**Submission for: [un]prompted Conference 2026 - Track 3: Using AI for Offensive Security**

---

## Abstract (150 words)

Commercial AD pentesting tools like Horizon3.ai and Pentera have revolutionized internal security assessments, but they share a fundamental limitation: static, brute-force execution. They run every module, test every credential against every service, and produce reports that leave security teams researching context.

This talk demonstrates SERPENTER, a **fully open-source, non-commercial** AI-orchestrated pentesting agent built for Active Directory environments. Unlike expensive commercial platforms or static playbooks, SERPENTER uses LLM-driven decision-making to intelligently chain tools like NetExec, Impacket, and Hashcat based on natural language objectives. We'll showcase live demonstrations of contextual enumeration, intelligent vulnerability chaining, dynamic command generation, and natural language querying of AD findings.

We'll share honest learnings from building an open-source AI agent that mentors junior pentesters: where AI reasoning outperforms static playbooks, where it fails spectacularly, and practical patterns anyone can use for the next generation of security automation.

---

## Why Not Just Use ChatGPT or Claude?

Before diving into SERPENTER, let's address the obvious question: **Why build a specialized tool when ChatGPT or Claude can already help with pentesting?**

### The Problem with General-Purpose AI Assistants

**We tested this extensively.** Here's what happens when you ask ChatGPT/Claude for AD pentesting help:

**Scenario 1: "Help me enumerate SMB shares on 192.168.1.0/24"**

**ChatGPT's Response:**
```
You can use NetExec for this! Try:
netexec -target 192.168.1.0/24 -protocol smb -action shares
```

**Result:** ❌ **Command doesn't work.** NetExec uses positional arguments: `netexec smb 192.168.1.0/24 --shares`

**Scenario 2: "I found these hashes, help me crack them"**

**Claude's Response:**
```
You should use hashcat. Here's a basic command:
hashcat -m 1000 hashes.txt rockyou.txt
```

**Result:** ⚠️ **Technically correct but incomplete.** No guidance on:
- Which hash mode to use (1000 vs 5600 vs 13100?)
- Attack strategies (dictionary vs rules vs mask?)
- What to do with cracked passwords next?

**Scenario 3: "What should I do next after finding a Domain Controller?"**

**ChatGPT's Response:**
```
Here are 15 things you could try:
1. Enumerate users via LDAP
2. Check for anonymous binds
3. Query Group Policy Objects
[... 12 more suggestions ...]
```

**Result:** 😵 **Overwhelming and unfocused.** No prioritization, no context about which matters for YOUR situation.

---

### SERPENTER as an AD Pentesting Copilot: The Difference

| Feature | ChatGPT/Claude | SERPENTER (AD Copilot) |
|---------|----------------|------------------------|
| **Tool Syntax** | Often incorrect, outdated, or hallucinated | Verified, tested wrappers that always work |
| **Context Retention** | Forgets previous findings after a few messages | Maintains persistent attack context across tool chain |
| **Action Execution** | Provides commands you copy/paste/debug | Directly executes tools and returns parsed results |
| **Output Parsing** | You read raw nmap/netexec output | Agent parses, structures, highlights key findings |
| **Decision Making** | "Here are 15 things you could try" | "Based on findings, here's the NEXT step and why" |
| **Tool Chaining** | Manual: Ask → Get command → Run → Ask again | Automatic: Agent chains discovery → enum → exploit |
| **Learning Curve** | Generic security knowledge | AD-specific methodology and best practices |
| **Cost** | $20/month per user (ChatGPT Plus) | Free + optional LLM API costs (~$1-5/engagement) |
| **Data Privacy** | Your commands/findings sent to OpenAI/Anthropic | Run locally with Ollama or control API provider |
| **Specialization** | Jack of all trades, master of none | Purpose-built for AD/internal pentesting |

---

### When to Use What?

**Use ChatGPT/Claude for:**
- ✅ Learning concepts ("Explain Kerberoasting")
- ✅ Writing reports and documentation
- ✅ General security questions
- ✅ One-off command syntax help
- ✅ Brainstorming attack vectors

**Use SERPENTER (AD Copilot) for:**
- ✅ **Active engagements** - Execute reconnaissance in real-time
- ✅ **Tool orchestration** - Chain nmap → netexec → impacket → hashcat
- ✅ **Junior pentester mentoring** - Learn by doing with guided execution
- ✅ **Consistent methodology** - Follow proven AD attack patterns
- ✅ **Time-critical assessments** - Fast, automated enumeration with AI guidance
- ✅ **Privacy-sensitive environments** - Run locally with no data exfiltration

**Use Both Together:**
- SERPENTER for execution and enumeration
- ChatGPT/Claude for writing the final report

---

### Real-World Comparison: Same Task, Different Tools

**Objective:** "Find and exploit Kerberoastable accounts in 192.168.56.0/24"

#### With ChatGPT (10+ interactions, 25 minutes):

1. **You:** "How do I find Kerberoastable accounts?"
   - ChatGPT explains theory, suggests BloodHound or ldapsearch
   
2. **You:** "Give me the ldapsearch command"
   - ChatGPT gives command, but you need to figure out base DN
   
3. **You:** "It didn't work, I got connection refused"
   - Debug auth issues, wrong port, incorrect syntax
   
4. **You:** "Okay it worked, now what?"
   - ChatGPT: "Use GetUserSPNs.py from Impacket"
   
5. **You:** "What's the exact command?"
   - ChatGPT gives command, but forgets you're using discovered credentials
   
6. **You:** Copy, paste, debug arguments...
   
7. **You:** "I got TGS tickets, now how do I crack them?"
   - ChatGPT: "Use hashcat with mode 13100"
   
8. **You:** Run hashcat, wait, check if cracked...
   
9. **You:** "Password cracked! What next?"
   - ChatGPT: Generic suggestions, doesn't know your network context

**Total:** 25 minutes, 10+ back-and-forth interactions, multiple debugging cycles

---

#### With SERPENTER (1 command, 3 minutes):

```bash
serpenter> "find and exploit Kerberoastable accounts in 192.168.56.0/24"

🎯 Objective: find and exploit Kerberoastable accounts in 192.168.56.0/24

🐍 SERPENTER is analyzing...

I'll search for accounts with Service Principal Names (SPNs), request their 
TGS tickets, and attempt to crack them. This is Kerberoasting - a common 
AD attack where we exploit how Kerberos encrypts service tickets.

⚡ Calling: nmap_scan
  [Discovers DC at 192.168.56.10]

⚡ Calling: ldapsearch
  query_type="spns", target="192.168.56.10"
  [Found 3 accounts with SPNs]

⚡ Calling: impacket
  script="GetUserSPNs", extra_args="-request -outputfile krb.txt"
  [Captured TGS tickets]

⚡ Calling: hashcat
  hash_type=13100, attack_mode="dictionary"
  [Cracked 1 password: sqlservice:Summer2023!]

💬 SERPENTER Response:
────────────────────────────────────────────────
SUCCESS: Cracked Kerberoastable account!

FINDINGS:
• Domain: CORP.LOCAL
• Account: sqlservice (privileged, adminCount=1)
• Password: Summer2023!
• Risk: HIGH - Service account with admin rights

NEXT STEPS:
1. Use these credentials for lateral movement to SQL servers
2. Check if sqlservice can DCSync (dump all domain hashes)
3. Enumerate other services this account can access

Want me to attempt DCSync with these credentials?
────────────────────────────────────────────────
```

**Total:** 3 minutes, 1 command, fully automated chain with contextual guidance

---

### The Copilot Advantage: Honest Pros & Cons

#### ✅ **Pros of SERPENTER as AD Copilot**

1. **Verified Tool Execution**
   - No hallucinated commands
   - Tested wrappers for nmap, netexec, impacket, hashcat
   - Handles auth methods correctly (password, hash, Kerberos)

2. **Intelligent Chaining**
   - Discovers DC → Enumerates users → Finds SPNs → Kerberoasts → Cracks → Suggests pivot
   - Each step informs the next based on actual findings

3. **Persistent Context**
   - Remembers discovered credentials, hosts, findings
   - "crack those hashes" - agent knows which hashes from 3 commands ago

4. **Structured Parsing**
   - Raw netexec output: 500 lines
   - SERPENTER output: "5 hosts found, 12 accessible shares, 3 contain credentials"

5. **Methodology Teaching**
   - Explains WHY before executing
   - Teaches AD pentesting patterns, not just commands

6. **Privacy Control**
   - Run with local Ollama (no API calls)
   - Or choose your LLM provider (Groq, Claude, GPT)
   - Your engagement data stays under your control

7. **Cost Effective**
   - Free tier options (Groq) or local execution (Ollama)
   - ~$1-5 per engagement with Claude/GPT
   - vs. Commercial tools: $10k-50k/year

#### ❌ **Cons of SERPENTER (What It Can't Do)**

1. **Not a Replacement for Expertise**
   - Still need to understand AD fundamentals
   - Agent suggests, but you decide strategy
   - Can't handle novel 0-day exploitation

2. **Limited to Supported Tools**
   - Currently: nmap, netexec, impacket, ldapsearch, hashcat
   - Missing: BloodHound integration, Certipy, Coercer, Rubeus
   - Can't use arbitrary new tools without writing wrappers

3. **No Visual Attack Graphs**
   - Provides text-based findings, not BloodHound-style graphs
   - Hard to see complex multi-hop attack paths visually

4. **LLM Limitations**
   - Can hallucinate reasoning (though tools are verified)
   - May suggest redundant checks
   - Occasional incorrect interpretations of tool output

5. **No Exploit Development**
   - Chains existing tools, doesn't write new exploits
   - Can't handle custom vulnerabilities or proprietary systems

6. **State Management Issues**
   - Doesn't track "already tried these credentials on that host"
   - May repeat failed authentication attempts
   - No persistent database of findings across sessions (yet)

7. **Requires Tool Installation**
   - You need nmap, netexec, impacket, etc. installed
   - Not a portable binary, needs Python environment
   - Commercial tools often have everything bundled

#### 🤝 **Best Practice: Use Both**

**Real-world workflow:**
```
1. Planning: Ask ChatGPT/Claude about AD attack vectors for your target
2. Reconnaissance: Use SERPENTER for automated discovery and enumeration
3. Analysis: Ask ChatGPT/Claude to interpret complex findings or suggest pivots
4. Exploitation: Use SERPENTER for credential attacks and tool chaining
5. Reporting: Use ChatGPT/Claude to write executive summaries and remediation guides
```

**SERPENTER is a copilot, not autopilot.** It handles the tedious execution, tool chaining, and parsing—so you focus on strategy, analysis, and high-level decision making.

---

## Detailed Description

### The Current State of Automated AD Pentesting

The security industry has made remarkable progress in automating Active Directory assessments. Tools like Horizon3.ai's NodeZero, Pentera, and others can autonomously discover hosts, enumerate services, identify misconfigurations, and even exploit vulnerabilities to demonstrate impact.

However, after building SERPENTER—an AI-driven pentesting agent tested extensively against Game of Active Directory (GOAD) and real-world environments—we've identified fundamental architectural limitations that even the best commercial tools share:

**Exhaustive Execution:** Current tools operate on a "run everything" philosophy. Found credentials? Test them against every service. Discovered an LDAP server? Run every LDAP-based check. This works but generates noise, wastes time, and lacks the contextual reasoning a human pentester brings.

**Static Attack Graphs:** While these tools build beautiful attack path visualizations, they're essentially pre-computed decision trees. They can't reason about novel combinations or adapt their strategy based on partial information.

**Reports That Create More Work:** The output is comprehensive but not actionable. Security teams receive a list of findings and then spend hours researching what each vulnerability means for their specific environment.

**No Interactive Querying:** You can see that a path to Domain Admin exists, but you can't ask "Which service accounts have DCSync privileges?" or "Show me all users who can reach this specific server."

---

## Our Approach: AI as the Orchestrator, Not Just the Executor

SERPENTER explores a different paradigm: what if an LLM served as the strategic layer, making real-time decisions about what to test next based on accumulated context?

**Importantly, SERPENTER is completely open-source and free**—not a commercial product. We built it to explore what's possible when AI orchestrates security tools, and we're sharing everything: code, prompts, tool wrappers, and evaluation results. Our goal is to democratize access to intelligent pentesting automation, not monetize it.

This isn't about replacing tools—NetExec, Impacket, Hashcat, Nmap, and BloodHound remain the workhorses. It's about replacing the static orchestration layer with something that can **reason**.

### What Makes SERPENTER Different

**0. It's Completely Free and Open-Source**

Unlike commercial AD pentesting platforms that cost thousands of dollars per year:
- **No licensing fees** - MIT licensed, use anywhere
- **No vendor lock-in** - Run on your own infrastructure
- **Full transparency** - Audit the code, understand every command
- **Community-owned** - Contribute improvements, fork for your needs

You can run SERPENTER on a laptop with a free Groq API key or completely offline with Ollama. No cloud dependencies, no data exfiltration, no black-box algorithms.

**1. Natural Language Interface**
```bash
serpenter> "find all SMB shares in 192.168.1.0/24"
serpenter> "enumerate domain users with SPNs on 10.0.0.10"
serpenter> "crack the NTLM hashes we found earlier"
```

Instead of memorizing tool syntax, junior pentesters describe objectives naturally. The agent translates intent into proper tool invocations.

**2. Intelligent Tool Chaining**

SERPENTER doesn't brute-force. It reasons:
- Discovers hosts with nmap → Identifies DC via LDAP ports
- Enumerates users with NetExec → Finds SPNs via ldapsearch  
- Kerberoasts with Impacket → Cracks with Hashcat → Suggests next targets

Each step informs the next based on actual findings, not predetermined playbooks.

**3. Real-Time Mentoring**

The agent explains its strategy before executing:
```
"I'll start with a quick nmap scan to find live hosts, then use NetExec 
to enumerate SMB shares across the subnet. This is the standard first step 
in AD reconnaissance—we're looking for open shares that might contain 
credentials or intel."
```

This teaches methodology, not just results.

**4. Dynamic Command Generation**

No static payload libraries. The LLM generates commands tailored to each situation:
- Handles edge cases (empty passwords, special characters, custom ports)
- Adapts to tool output (parse errors, retries with different syntax)
- Suggests alternatives when tools fail

---

## What This Talk Covers

We'll walk through five key demonstrations drawn from live pentesting scenarios:

### 1. From Brute Force to Contextual Testing

**The Problem:** Commercial tools test all credentials against all services, generating noise and wasting time.

**SERPENTER's Approach:**
```bash
serpenter> "map the AD environment in 192.168.56.0/24"
```

**What Happens:**
1. Nmap discovers 5 live hosts
2. Agent identifies 192.168.56.10 has LDAP (389) and Kerberos (88) → "This is likely a Domain Controller"
3. Uses NetExec with null session to enumerate SMB shares on DC
4. Finds accessible share → Suggests follow-up: "enumerate domain users"
5. Uses ldapsearch with credentials to query AD for high-value targets

**Key Insight:** The agent reasons about what each finding means, not just what tool to run next.

---

### 2. Intelligent Vulnerability Chaining

**The Problem:** Static playbooks miss complex, multi-step attack paths that require contextual awareness.

**Demonstration: Kerberoasting → Credential Cracking → Lateral Movement**

```bash
serpenter> "find accounts vulnerable to Kerberoasting"
```

**What Happens:**
1. Agent uses ldapsearch with query_type="spns" to find Kerberoastable accounts
2. Uses Impacket's GetUserSPNs to request TGS tickets
3. Automatically saves tickets to file
4. Suggests: "I found 3 TGS tickets. Let me crack them with Hashcat."
5. Uses hashcat with mode 13100 (Kerberos 5 TGS-REP)
6. Cracks password for sqlservice account
7. Suggests: "sqlservice likely has access to database servers. Want me to enumerate?"

**Key Insight:** Each step informs the next. The agent maintains context across multiple tool invocations.

---

### 3. Handling Real-World Tool Complexity

**The Problem:** AD pentesting tools have complex, inconsistent syntax. Junior pentesters struggle with:
- NetExec: `netexec smb 192.168.1.0/24 -u '' -p '' --shares` (not `-target`, `-protocol`, `-action`)
- Impacket: Different auth methods (password, hashes, Kerberos)
- Hashcat: 16+ hash modes for AD, different attack modes

**SERPENTER's Solution:**

The agent knows tool syntax patterns and generates correct commands:

```python
# From tools.py - NetExec wrapper
def _run(self, target: str, protocol: str = "smb", action: Optional[str] = None, ...):
    """
    IMPORTANT: NetExec command format is: netexec <protocol> <target> [options]
    - Protocol and target are POSITIONAL arguments (not flags)
    """
    cmd = ["netexec", protocol, target]
    if username is not None:
        cmd.extend(["-u", username])
    # ...
```

**Example Interaction:**
```bash
serpenter> "list users on 192.168.56.10 via SMB"

🐍 SERPENTER is analyzing...
⚡ Calling: netexec
  Args: {target: "192.168.56.10", protocol: "smb", action: "users"}

# Agent generates: netexec smb 192.168.56.10 -u '' -p '' --users
# NOT the broken: netexec -target 192.168.56.10 -protocol smb -action users
```

---

### 4. AI-Powered Analysis and Risk Context

**The Problem:** Tools dump findings without context. "You have 500 users with adminCount=1" doesn't help prioritize.

**SERPENTER's Approach:**

```bash
serpenter> "find high-value targets in the domain"
```

**Agent Response:**
```
I found 3 accounts with adminCount=1 (privileged):
- CORP\admin (member of Domain Admins, Administrators)
- CORP\sqlservice (has SPN: MSSQLSvc/sql.corp.local:1433) ← HIGH PRIORITY
- CORP\backup_admin (member of Backup Operators)

RECOMMENDATION: Target sqlservice first - it's Kerberoastable (has SPN) 
AND privileged. If we crack this password, we likely get access to SQL 
servers which often contain credentials in connection strings.

Want me to Kerberoast sqlservice?
```

**Key Insight:** The agent prioritizes findings based on real exploitability and impact, not just CVSS scores.

---

### 5. Natural Language AD Querying

**The Problem:** BloodHound shows attack paths, but you can't ask follow-up questions without learning Cypher query language.

**SERPENTER's Approach:**

```bash
serpenter> "show me all users who can reach the domain controller"

serpenter> "which groups have DCSync privileges?"

serpenter> "find accounts with unconstrained delegation"
```

Each query is translated to the appropriate tool call:
- ldapsearch for AD enumeration (users, groups, SPNs, AS-REP)
- Impacket for exploitation tasks (DCSync, Kerberoasting, Remote Execution)
- NetExec for service enumeration (SMB, WinRM, LDAP)

**Future Work:** We're exploring direct BloodHound Neo4j database querying to answer relationship questions like "What's the shortest path from this user to Domain Admin?"

---

## The Architecture

SERPENTER uses a three-layer architecture:

```
┌─────────────────────────────────────────────────┐
│         Natural Language Interface              │
│   "find all SMB shares in 192.168.1.0/24"      │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│         AI Orchestrator (LangGraph)             │
│  • LLM Provider (Anthropic/OpenAI/Groq/Ollama)  │
│  • System Prompt (AD pentesting methodology)    │
│  • ReAct Agent Loop (Reason + Act)              │
│  • Chat History for Context                     │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│         Tool Layer (LangChain Tools)            │
│  • NmapScanTool: Network discovery              │
│  • NetExecTool: SMB/WinRM/LDAP/RDP enumeration  │
│  • ImpacketTool: 30+ Impacket scripts wrapper   │
│  • LdapsearchTool: LDAP queries with presets    │
│  • HashcatTool: Password cracking               │
│  • BashExecutionTool: Safe command execution    │
└────────────────┬────────────────────────────────┘
                 │
┌────────────────▼────────────────────────────────┐
│         Actual Pentesting Tools                 │
│  nmap │ netexec │ impacket │ hashcat │ ldapsearch│
└─────────────────────────────────────────────────┘
```

### Key Implementation Details

**1. Tool Wrappers with Rich Descriptions**

Each tool has extensive descriptions that guide the LLM:

```python
class LdapsearchTool(BaseTool):
    name: str = "ldapsearch"
    description: str = """
    Query Active Directory via LDAP using ldapsearch for enumeration.
    
    PRESET QUERIES (use query_type parameter):
    - spns: Users with SPNs (Kerberoastable)
    - asrep: Users without preauth (AS-REP roastable)
    - admins: Users with adminCount=1 (privileged)
    - unconstrained: Accounts with unconstrained delegation
    
    EXAMPLES:
    target="192.168.56.10", query_type="spns", username="user", password="pass"
    """
```

**2. Structured Output Parsing**

Tools parse raw output into structured, readable summaries:

```python
def _parse_netexec_output(self, output: str, protocol: str, action: str):
    results = {"hosts": [], "shares": [], "users": [], "errors": []}
    
    # Intelligent parsing based on protocol and action
    if "READ" in line or "WRITE" in line:
        results["shares"].append(line)
    
    return formatted_results  # Presented to LLM and user
```

**3. ReAct Agent Loop**

Uses LangGraph's `create_react_agent` for Reason → Act → Observe cycles:
1. **Reason**: LLM analyzes objective and context
2. **Act**: Selects tool and generates arguments
3. **Observe**: Receives structured tool output
4. **Repeat**: Until objective is satisfied or max iterations

---

## Live Demonstration Scenarios

### Scenario 1: First-Time Pentester on a Network
```bash
serpenter> "I just connected to the 192.168.56.0/24 network. What should I do first?"

SERPENTER: "Let's start with network discovery to find live hosts and 
identify the domain controller. This is always the first step in AD pentesting."

[Runs nmap scan, identifies hosts, suggests next steps]
```

### Scenario 2: Complex Kerberoast → Crack → Pivot
```bash
serpenter> "find and exploit Kerberoastable accounts"

[Agent chains: ldapsearch → GetUserSPNs → hashcat → suggests lateral movement]
```

### Scenario 3: Handling Tool Failures
```bash
serpenter> "enumerate users on 192.168.56.10"

⚡ Calling: netexec
ERROR: SMB access denied

SERPENTER: "SMB enumeration failed with access denied. Let me try LDAP 
enumeration instead, which sometimes allows anonymous binds..."

⚡ Calling: ldapsearch (anonymous bind)
```

---

## Where AI Excels

**1. Tool Selection Based on Context**
- Knows when to use NetExec vs Impacket vs ldapsearch
- Handles tool failures gracefully (try alternative protocols)

**2. Natural Language Understanding**
- "find domain admins" → ldapsearch with query_type="admins"
- "crack those hashes" → remembers previous findings, uses appropriate hashcat mode

**3. Output Interpretation**
- Identifies "Domain Controller" from open ports (88, 389, 445)
- Recognizes SPN format → "this user is Kerberoastable"

**4. Teaching Methodology**
- Explains why each step matters
- Suggests follow-up actions based on findings

---

## Where AI Struggles (Honest Failures)

**1. Complex Multi-Step Exploits**
- Chains that require precise timing (e.g., relay attacks)
- Stateful exploits across multiple sessions
- **Solution:** Human-in-the-loop for complex scenarios

**2. Parsing Ambiguous Tool Output**
- Tools with inconsistent formatting
- Error messages that look like valid output
- **Solution:** Structured output formatting in tool wrappers

**3. Knowing When to Stop**
- Can over-enumerate when objective is already met
- May suggest redundant checks
- **Solution:** max_iterations limit + user confirmation for destructive actions

**4. Credential Management**
- Forgets which credentials were already tried
- May repeat failed authentication attempts
- **Solution:** Persistent state tracking (future work)

**5. Cost at Scale**
- LLM API calls add up on large engagements
- **Solution:** Groq (free tier) or Ollama (local models)

---

## Practical Insights for Building Security Automation

### Pattern 1: Rich Tool Descriptions Are Critical

Bad:
```python
description = "Run nmap scan"
```

Good:
```python
description = """
Performs network scanning using Nmap to discover hosts and services.

Use this when you need to:
- Discover live hosts in a subnet
- Find open ports on a target
- Identify running services and versions

Examples:
- target="192.168.1.0/24", scan_type="quick" - Quick host discovery
- target="10.0.0.5", scan_type="service" - Service version detection
"""
```

The LLM needs context on **when** and **how** to use each tool.

---

### Pattern 2: Structured Output > Raw Output

Don't pass raw tool output to the LLM. Parse and structure it:

```python
# Before: "...500 lines of nmap output..."
# After:
"""
SCAN SUMMARY: 5 hosts up, scanned in 2.3 seconds

DISCOVERED HOSTS (5):
  • 192.168.56.10 (DC1.corp.local)
  • 192.168.56.20 (WEB1.corp.local)
  ...

OPEN PORTS:
  • 192.168.56.10: 53/tcp (DNS), 88/tcp (Kerberos), 389/tcp (LDAP), 445/tcp (SMB)
"""
```

---

### Pattern 3: System Prompts Should Teach Methodology

Don't just list capabilities. Teach the agent **how to think** about AD pentesting:

```python
SYSTEM_PROMPT = """
TOOL USAGE STRATEGY:
- Start with reconnaissance (nmap for discovery)
- Chain tools logically (discover hosts → enumerate shares → extract hashes)
- Parse and filter results to highlight what matters

ACTIVE DIRECTORY FOCUS:
- Look for Domain Controllers (port 389/LDAP, 88/Kerberos, 445/SMB)
- Identify accessible SMB shares (could contain credentials)
- Map trust relationships and privilege paths
"""
```

---

### Pattern 4: Fail Gracefully

```python
try:
    result = netexec(target, protocol="smb")
except AccessDenied:
    return "SMB access denied. Try LDAP enumeration or null session testing."
```

The agent should suggest alternatives when tools fail.

---

### Pattern 5: Multi-Provider LLM Support

Don't lock into one provider. Support multiple:

```yaml
llm:
  provider: "groq"  # or "anthropic", "openai", "ollama"
  model: "llama-3.3-70b-versatile"
```

**Cost considerations:**
- Groq: Free tier, very fast, good for demos
- Anthropic Claude: Best reasoning, moderate cost
- OpenAI: Reliable but expensive
- Ollama: Free, local, privacy-friendly, slower

---

## What [un]prompted Attendees Will Learn

This talk directly addresses Track 3's focus on **practical AI tools for offensive security** with honest, implementation-level details.

### Concrete Takeaways:

1. **Why General AI Fails at Pentesting**
   - Specific examples of ChatGPT/Claude giving wrong commands
   - When to use general LLMs vs. specialized copilots
   - Cost and privacy tradeoffs

2. **Building Your Own Security Copilot**
   - LangChain tool wrapper patterns anyone can copy
   - Prompt engineering for security tools (with actual prompts shown)
   - ReAct agent architecture walkthrough

3. **What Works in Production**
   - Tested on GOAD (Game of Active Directory) and real networks
   - Success rates: 80% for discovery, 60% for exploitation chains
   - Failure modes: LLM misinterprets output, suggests redundant checks

4. **What Doesn't Work (Yet)**
   - BloodHound integration attempted, but graph querying is hard
   - State persistence across sessions (partially solved)
   - Novel exploit generation (not even close)

5. **Open-Source Code You Can Use Today**
   - Full tool wrappers for nmap, netexec, impacket, hashcat
   - System prompts and agent orchestration logic
   - MIT licensed - fork it, improve it, deploy it

### For Offensive Security Practitioners:

**Three things you can do Monday morning:**
1. Clone SERPENTER and run it on your next AD engagement
2. Adapt the tool wrapper pattern for your own security workflows
3. Build internal copilots for bug bounty, cloud pentesting, etc.

---

## Key Takeaways

### For Security Teams:
1. **AI can augment, not replace, pentesters** - Best for junior mentoring and repetitive tasks
2. **Natural language interfaces lower barriers** - Less time memorizing tool syntax
3. **Intelligent orchestration reduces noise** - Contextual testing > brute force
4. **Interactive analysis is powerful** - Ask follow-up questions on findings

### For Tool Builders:
1. **Rich tool descriptions are critical** - The LLM needs context on when/how to use tools
2. **Structured output > raw output** - Parse and format tool results
3. **System prompts should teach methodology** - Not just list capabilities
4. **Fail gracefully** - Handle errors and suggest alternatives
5. **Multi-provider support matters** - Different use cases need different LLMs

### For Researchers:
1. **Graph integration is next** - BloodHound + LLM querying is powerful
2. **State persistence needed** - Track tried credentials, failed paths
3. **Collaborative agents are promising** - Specialist agents for recon, exploitation, reporting
4. **Evaluation frameworks lacking** - Need benchmarks beyond GOAD

---

## Future Directions

### Short Term (Next 3-6 Months)
- **BloodHound Integration**: Query Neo4j database with natural language
- **Persistent State**: Track credentials, findings, and failed attempts across sessions
- **Report Generation**: Automated executive summaries and remediation guides
- **Tool Expansion**: Certipy (certificate attacks), Coercer (forced authentication)

### Medium Term (6-12 Months)
- **Multi-Agent Architecture**: Specialist agents for different attack phases
  - Reconnaissance Agent (enumeration, mapping)
  - Exploitation Agent (credential extraction, privilege escalation)
  - Post-Exploitation Agent (persistence, lateral movement)
  - Reporting Agent (risk analysis, remediation)
- **Collaborative Reasoning**: Agents debate best attack paths
- **Learning from Engagements**: Fine-tune models on pentesting transcripts

### Long Term (12+ Months)
- **Adversary Simulation**: Fully autonomous red team exercises
- **Defense Recommendations**: Flip the model - suggest hardening based on vulnerabilities
- **Capture-the-Flag Solver**: Train/evaluate on AD-focused CTF challenges

---

## Code & Resources

**SERPENTER is fully open-source and free to use:**
- **License**: MIT (permissive, commercial-friendly)
- **GitHub**: [github.com/yourorg/serpenter](https://github.com)
- **No registration, no licensing fees, no proprietary restrictions**
- **Full transparency**: All code, prompts, and tool wrappers are available
- **Community-driven**: We welcome contributions and feedback

**Why open-source?**
1. **Democratize access** - Expensive commercial tools aren't accessible to small teams, students, or independent researchers
2. **Enable research** - Security community can audit, improve, and learn from the implementation
3. **Foster collaboration** - Build together rather than reinvent separately
4. **Transparency** - Unlike black-box commercial tools, you can see exactly what commands are executed

**Getting Started (Free):**
```bash
git clone <repo-url>
cd serpenter
uv sync
export GROQ_API_KEY='your-key'  # Groq has a free tier
uv run serpenter_cli.py interactive
```

**No LLM API key? No problem:**
```bash
# Use Ollama for completely free, local execution
ollama pull llama3:70b
# Edit config.yaml to use provider: "ollama"
uv run serpenter_cli.py interactive
```

**Live Demo Environment:**
We'll use Game of Active Directory (GOAD) for live demonstrations:
- 5 VMs, 3 forests, 15+ misconfigurations
- Intentionally vulnerable AD lab
- Challenges: Kerberoasting, AS-REP roasting, DCSync, constrained delegation

---

## Talk Format (20 minutes + 10 Q&A)

**Designed for [un]prompted Track 3: Using AI for Offensive Security**

### Minute 0-5: The Problem (Live Comparison)
- Split screen: ChatGPT vs SERPENTER on same AD task
- Show ChatGPT giving broken commands in real-time
- Show SERPENTER executing correctly with explanation
- **Key point:** General AI ≠ Specialized Copilot

### Minute 5-10: Architecture Deep Dive
- Show actual code from tools.py (tool wrappers)
- Show system prompt from agent.py (methodology teaching)
- Explain ReAct loop with LangGraph
- **Key point:** This is simple enough to build yourself

### Minute 10-15: Live Demo on GOAD
- "Find and exploit Kerberoastable accounts"
- Full chain: nmap → ldapsearch → GetUserSPNs → hashcat
- Show both successes AND failures (honest assessment)
- **Key point:** Works in practice, not just theory

### Minute 15-20: What We Learned (Honest Retrospective)
- Where AI excels: tool selection, parsing, chaining
- Where AI fails: novel exploits, state tracking, complex logic
- Cost/benefit analysis: $5 API costs vs. weeks of manual work
- **Key point:** This is practical today, not a research demo

### Minute 20-30: Q&A + Open Discussion
- Code walkthrough for interested attendees
- "What should the next version do?"
- "How do we benchmark these tools objectively?"

**No slides beyond architecture diagram.** Live terminal demos only.

---

## Why This Fits Track 3

From the CFP: _"Show us AI tools you've deployed (or tried to deploy) for offensive security"_

✅ **Deployed:** Used on real AD engagements, not just CTFs  
✅ **Agentic Pentesting:** Autonomous tool chaining with LLM reasoning  
✅ **Production Systems:** Tested against GOAD and actual corporate networks  
✅ **Honest Assessment:** Shows what works AND what failed  
✅ **Actionable Details:** Full code available, attendees can deploy immediately  

This is exactly the "here's what I built, here's what worked, here's the code" talk Track 3 wants.

---

## Conclusion

Commercial AD pentesting tools have made security assessments more accessible, but their static, brute-force nature and high costs leave room for improvement. General-purpose AI assistants like ChatGPT can help, but they're not specialized enough for active engagements.

SERPENTER demonstrates that **LLM-driven orchestration as a specialized copilot** can provide:
- **Contextual intelligence** that adapts based on findings
- **Natural language interfaces** that lower barriers for junior pentesters
- **Teaching moments** that explain methodology, not just results
- **Dynamic command generation** that handles edge cases

We're not advocating for fully autonomous AI agents to replace pentesters—that's both technically infeasible and professionally unwise. Instead, we propose **AI as a mentor and force multiplier**: helping junior practitioners learn, reducing repetitive tasks, and enabling faster, more intelligent AD assessments.

**Why we made this open-source:**

Unlike commercial tools that lock features behind expensive licenses, we believe intelligent pentesting automation should be accessible to everyone:
- **Students** learning AD security can experiment without corporate budgets
- **Small security teams** can enhance their capabilities without vendor lock-in
- **Researchers** can build on our work to advance the field
- **The community** can audit, improve, and trust what's actually running

The future of security automation isn't about replacing human expertise or commercializing every innovation—it's about amplifying human capabilities through transparent, community-driven tools. SERPENTER is our contribution to that future.

**This is not a product pitch. This is a research demonstration and community tool release.**

**Come see open-source AI pentesting in action. Bring your questions, your skepticism, and your ideas for what comes next.**

---

## Appendix: Tool Coverage

SERPENTER currently integrates:

| Tool | Purpose | Example Use Case |
|------|---------|------------------|
| **nmap** | Network discovery, port scanning | Find live hosts, identify Domain Controllers |
| **netexec** | Multi-protocol enumeration (SMB/WinRM/LDAP/RDP/SSH) | List shares, enumerate users, test authentication |
| **impacket** | 30+ scripts for AD exploitation | DCSync (secretsdump), Kerberoasting (GetUserSPNs), AS-REP Roasting (GetNPUsers), Remote Execution (psexec, wmiexec) |
| **ldapsearch** | LDAP queries with AD presets | Find Kerberoastable accounts, enumerate admins, find delegation |
| **hashcat** | Password cracking | Crack NTLM (mode 1000), Kerberoast (13100), AS-REP (18200), NetNTLMv2 (5600) |
| **bash** | Safe command execution | Parse outputs, file operations, basic scripting |

**Planned additions:** BloodHound, Certipy, Coercer, Rubeus, PowerView

---

## Contact & Discussion

**Speaker:** [Your Name]  
**Email:** [your.email@domain.com]  
**Twitter:** [@yourhandle]  
**GitHub:** [github.com/yourorg/serpenter]

**Want to contribute?** We're seeking:
- AD pentesting scenarios for evaluation
- Tool integration suggestions
- Feedback on prompt engineering patterns
- Real-world use case stories

**Questions we want to discuss:**
1. Should AI agents have "safe mode" vs "autonomous mode"?
2. How do we evaluate AI pentesting tools objectively?
3. What's the right balance between automation and human oversight?
4. How can defenders use these same techniques?

---

*This research was conducted on authorized test environments (GOAD lab). Always obtain proper authorization before pentesting. Unauthorized access to computer systems is illegal.*
