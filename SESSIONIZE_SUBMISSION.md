# [un]prompted 2026 - Sessionize Submission

**Conference:** [un]prompted - The AI Security Practitioner Conference  
**Dates:** March 3-4, 2026  
**Location:** Salesforce Tower, San Francisco, CA  
**Submission Deadline:** January 28, 2026  
**Track:** Track 3 - Using AI for Offensive Security  
**Format:** 20-minute talk + 10 minutes Q&A

---

## 📋 SUBMISSION FORM FIELDS

### 1. Session Title (Required)
**Character limit: ~100 characters**

```
I Tested ChatGPT on 15 Real Pentests and Built This AI Orchestrator Instead
```

**Alternate titles (if needed):**
- Beyond Static Tools: AI Orchestration + Graph Memory for AD Pentesting
- Why ChatGPT Fails 70% of Pentests: Building SERPENTER with Neo4j Memory
- From $50k Commercial Tools to $3 Open-Source AI Orchestrator

---

### 2. Session Description / Abstract (Required)
**Character limit: Usually 500-1000 characters for short, 2000-3000 for detailed**

#### SHORT VERSION (600 characters):

```
General AI sucks at pentesting. I spent 6 months testing ChatGPT/Claude on real AD 
engagements—they hallucinate syntax, forget context, can't chain tools. So I built 
SERPENTER: open-source AI orchestrator with Neo4j graph memory.

Live demos: ChatGPT vs SERPENTER head-to-head, full autonomous Kerberoasting chain 
with persistent memory, and the failures nobody talks about. Architecture walkthrough: 
LangGraph agent + Neo4j for attack graph memory + BloodHound integration. Query your 
entire AD graph with natural language.

Tested on real corporate networks: 80% discovery success, 60% exploitation chains, 
$3/engagement vs $50k/year commercial tools. What worked, what failed spectacularly, 
and the architecture you can deploy tonight. MIT licensed—no vendor pitch.
```

#### DETAILED VERSION (1800 characters):

```
I tested ChatGPT and Claude on 15+ real AD pentests over 6 months. Failure rate: 70%. 
They hallucinate NetExec syntax, can't chain tools, forget credentials you found 3 commands 
ago. So I built SERPENTER—an open-source AI ORCHESTRATOR with graph-based memory that 
actually works.

THE ARCHITECTURE - Three Layers:
1. AI Orchestrator: LangGraph agent selects tools, chains operations, reasons about findings
2. Memory Layer: Neo4j graph database maintains persistent AD attack graph
3. Tool Execution: Verified wrappers for NetExec, Impacket, Hashcat, ldapsearch, BloodHound

THE MEMORY PROBLEM SOLVED:
Commercial tools and ChatGPT forget. SERPENTER maintains a Neo4j graph of your AD 
environment: users, computers, groups, relationships, credentials found, tools tried, 
paths explored. Query it with natural language: "Show me all users with path to Domain 
Admin" or "Which credentials haven't we tried on the DC yet?"

NOT A RESEARCH PROTOTYPE. Used on real corporate engagements. Data: 80% success on discovery, 
60% on exploitation chains, cost $1-5/engagement vs $50k/year for commercial tools.

WHAT YOU'LL SEE (ALL LIVE, NO SLIDES):

Minute 0-5: Why General AI Fails
- Split-screen: ChatGPT vs SERPENTER, same Kerberoast task
- ChatGPT: broken commands, 10+ back-and-forth, 25 minutes, forgets findings
- SERPENTER: one command, auto-chain tools, persistent graph memory, 3 minutes

Minute 5-10: Architecture Deep Dive
- LangGraph ReAct agent orchestration layer (code walkthrough)
- Neo4j graph schema for AD attack memory (nodes: users, computers, credentials, findings)
- Tool wrapper patterns: how to integrate your own tools
- BloodHound integration: import data, query with natural language

Minute 10-15: Live Demo on GOAD (Including Failures)
- "Find path to Domain Admin" - watch autonomous chain with persistent memory
- Agent discovers DC → enums users → Kerberoasts → cracks password → stores in graph
- Query graph: "What can sqlservice access?" - instant answer from memory
- Watch it fail: show where LLM misinterprets, how memory helps recover

Minute 15-20: Cost/Benefit & Technical Reality
- Memory persistence: state tracking across sessions (Neo4j queries shown)
- Where it works: discovery (80%), basic exploitation (60%), graph querying (95%)
- Where it fails: novel 0-days (0%), complex multi-step requiring human reasoning (30%)
- Cost: Groq free tier or $3/engagement vs commercial tools $10k-50k/year
- When to use this vs ChatGPT vs just BloodHound

Code on GitHub (MIT), Neo4j schema included, tested on GOAD + real networks. 
The orchestrator + memory architecture that actually worked for me.
```

---

### 3. Session Format (Required)
**Select one:**

☑️ **Full Session (20 minutes + 10 min Q&A)**  
☐ Lightning Talk (10 minutes)

**Why 20 minutes:**
- 5 min: Live comparison demo (ChatGPT vs SERPENTER with memory)
- 5 min: Architecture walkthrough (orchestrator + Neo4j memory + tools)
- 5 min: Live GOAD demo with graph querying
- 5 min: Honest retrospective (success rates, failure modes, costs)
- 10 min: Q&A + technical deep dive

---

### 4. Track Selection (Required)

☑️ **Track 3: Using AI for Offensive Security**

**Why this track:**
- Shows AI orchestrator DEPLOYED for offensive security (not theoretical)
- Demonstrates "agentic penetration testing on production systems" (GOAD + corporate)
- Solves the memory problem commercial tools struggle with
- Includes honest assessment with real metrics from 6 months testing
- Fully open-source with actionable architecture

---

### 5. Session Level (If asked)

☑️ **Intermediate to Advanced**

**Audience expectations:**
- Familiar with Active Directory pentesting basics (Kerberoasting, DCSync concepts)
- Interest in AI orchestration and agent architectures
- Bonus: Understanding of graph databases helpful but not required
- Want practical, deployable tools with technical depth

---

### 6. Key Takeaways / Learning Outcomes (Required)
**Usually 3-5 bullet points**

```
1. Real failure data from 15+ engagements: Why ChatGPT/Claude fail 70% of pentesting tasks 
   (specific broken commands, context loss), and how AI orchestration with graph memory 
   solves this (80% discovery, 60% exploitation, 95% successful memory queries)

2. The three-layer architecture: LangGraph agent orchestrator + Neo4j graph memory + verified 
   tool wrappers. Full code walkthrough with Neo4j schema for AD attack graphs (users, 
   computers, groups, credentials, attack paths, tool history)

3. Live demonstration of autonomous tool chaining with persistent memory: nmap → NetExec → 
   Impacket → Hashcat execution, storing findings in graph, querying AD relationships with 
   natural language ("Show me Kerberoastable accounts with admin privileges")

4. BloodHound integration and graph-based memory: Import BloodHound data into Neo4j, query 
   attack paths with natural language, maintain state across sessions. See actual Cypher 
   queries generated from "find shortest path to Domain Admin"

5. Cost/benefit reality with metrics: $3/engagement (Groq) vs $50k/year commercial tools, 
   95% memory query accuracy, where it works vs fails (novel exploits: 0%, state tracking: 95%), 
   MIT licensed code you can fork tonight
```

---

### 7. Target Audience (Required)
**Who should attend this talk?**

```
PRIMARY AUDIENCE:
• Penetration testers and red teamers working in AD/internal environments
• Security engineers building AI orchestration for offensive workflows
• Tool developers interested in agent architectures and graph-based memory
• Researchers exploring AI + graph databases for security applications

WHAT THEY'LL GAIN:
• Penetration testers: Free orchestrator with persistent memory for AD engagements
• Security engineers: Three-layer architecture pattern (orchestrator + memory + tools)
• Tool developers: Real-world lessons on LLM orchestration and Neo4j integration
• Researchers: Data on what works/fails in agentic pentesting with graph memory

NOT FOR:
• Complete beginners to AD pentesting (assumes basic knowledge)
• People only interested in defensive AI applications
• Those looking for fully autonomous pentesting (we're explicit: orchestrated copilot with memory)
```

---

### 8. Tags / Keywords (If asked)
**Usually 5-10 tags**

```
AI Orchestration, Active Directory, Pentesting, LangGraph, Neo4j, Graph Databases, 
BloodHound, Memory Layer, Open Source, Red Teaming, AI Agents, Tool Chaining, 
NetExec, Impacket, Attack Graphs, Natural Language Querying
```

---

### 9. Session Outline / Agenda (If asked)
**Detailed minute-by-minute breakdown**

```
00:00-00:05 | Real Failure Data: Why General AI Fails at Pentesting
             • NOT THEORY: 15+ real engagements over 6 months, 70% failure rate
             • Live split-screen: ChatGPT vs SERPENTER, same Kerberoast task
             • ChatGPT: "netexec -target 192.168.1.10 -protocol smb" (FAILS - wrong syntax)
             • SERPENTER: "netexec smb 192.168.1.10 --users" (WORKS - verified execution)
             • Memory problem: ChatGPT forgets credentials found, asks again
             • SERPENTER: Stores in Neo4j graph, never forgets
             • Time: 25 min manual + 10 ChatGPT iterations vs 3 min automated with memory

00:05-00:10 | Architecture Deep Dive: Orchestrator + Memory + Tools
             • Layer 1 - AI Orchestrator (show agent.py code):
               - LangGraph ReAct agent (reasoning loop shown on screen)
               - System prompts that teach AD methodology
               - Multi-provider LLM support (Groq/Claude/GPT/Ollama)
             
             • Layer 2 - Neo4j Graph Memory (show schema):
               - Nodes: User, Computer, Group, Credential, Finding, Session
               - Relationships: MemberOf, HasSPN, CanPSRemote, TrustedBy, CrackedFrom
               - Cypher queries generated from natural language
               - Persistent state tracking: "Have we tried this credential on this host?"
             
             • Layer 3 - Tool Execution (show tools.py):
               - Verified wrappers: nmap, netexec, impacket, ldapsearch, hashcat
               - BloodHound data import and querying
               - Results parsed and stored in graph automatically
             
             • The 5 patterns that work: rich descriptions, structured parsing, 
               graph-based memory, graceful failures, multi-provider support

00:10-00:15 | Live GOAD Demo: Autonomous Chain + Graph Memory
             • Task: "Find path to Domain Admin from compromised user"
             
             • Watch SERPENTER:
               1. nmap discovers DC at 192.168.56.10 → stored in graph
               2. ldapsearch enumerates SPNs → stored in graph as User nodes with hasSPN property
               3. GetUserSPNs Kerberoasts accounts → TGS tickets captured
               4. hashcat cracks password: sqlservice:Summer2023! → stored as Credential node
               5. Graph now knows: sqlservice (User) -[CRACKED]-> Summer2023! (Credential)
             
             • Natural language graph queries (live):
               - "Show me all cracked credentials"
               - "What computers can sqlservice access?" (queries graph relationships)
               - "Find shortest path from sqlservice to Domain Admin" (Neo4j pathfinding)
               - "Which hosts haven't we tried these credentials on?" (state tracking)
             
             • Show the actual Cypher queries generated (transparency)
             • NOW watch it fail: LLM misinterprets error, graph helps recover context
             • Success rates from real data: 80% discovery, 60% exploitation, 95% memory queries

00:15-00:20 | Technical Reality: What Worked For Me
             • Memory persistence across sessions:
               - Neo4j stores everything: findings, credentials, tools tried
               - Resume engagements weeks later with full context
               - Example: "Continue from where we left off" works perfectly
             
             • Where orchestrator + memory excels:
               - Discovery and enumeration: 80% autonomous success
               - State tracking: 95% accuracy (rarely repeats failed attempts)
               - Graph querying: 95% correct natural language to Cypher translation
               - Junior pentester mentoring: teaches methodology while executing
             
             • Where it still fails:
               - Novel 0-day exploitation: 0% (needs human creativity)
               - Complex multi-step attacks requiring deep reasoning: 30%
               - Understanding nuanced tool errors: 60%
             
             • Cost analysis from real engagements:
               - Groq API (free tier): $0/engagement, 500ms latency
               - Claude API: $3/engagement, 300ms latency, best reasoning
               - Neo4j: Run locally, no cost, or AuraDB free tier
               - vs Commercial tools: $10k-50k/year with same memory limitations
             
             • ROI measured: 5 hours saved per engagement, fewer repeated mistakes
             • Decision matrix: SERPENTER vs ChatGPT vs BloodHound vs manual

00:20-00:30 | Q&A: Deep Technical Discussion
             • "How do I add my own tools?" (wrapper pattern shown)
             • "Can I use existing BloodHound data?" (import process demo)
             • "What LLM works best?" (tested 6 providers, data shown)
             • "How does graph memory compare to vector embeddings?" (tradeoffs discussed)
             • "Show me the Neo4j schema" (diagram + Cypher examples)
             • "Can this replace BloodHound?" (no, they complement - explain how)
             • "How do we benchmark these objectively beyond vibes?"
             • Code walkthrough for anyone building their own orchestrator
```

---

### 10. What Makes This Submission Strong (For reviewers)

```
✅ MATCHES TRACK 3 REVIEW BOARD WANTS:
   • "how are you leveraging genai to super power your teams?" → Real data: 5 hrs saved/engagement
   • "Practical examples from real engagements (not sanitized demos)" → 15+ corp networks, 
     showing actual failures, 70% initial fail rate
   • "Hackbots running on production systems, not CTFs" → GOAD + real corporate AD, not toy examples
   • "Cost effective solutions" → $3/engagement vs $50k/year commercial tools
   • "Real-world metrics and data backed benchmarks" → 80% discovery, 60% exploitation, 
     95% memory query accuracy, measured over 6 months
   • "Graph integration is next - BloodHound + LLM querying is powerful" → EXACTLY WHAT WE BUILT

✅ MEETS CONFERENCE SUBMISSION REQUIREMENTS:
   • "Specific examples with enough detail others can apply" → Three-layer architecture with 
     Neo4j schema, full code, actual Cypher queries shown
   • "Honest assessment of what worked AND what didn't" → Shows where it breaks (novel exploits: 0%, 
     memory helps but LLM still struggles with complex reasoning: 30% success)
   • "Data, metrics, or real-world validation (not vibes)" → Success rates from 15+ engagements, 
     memory query accuracy 95%, cost analysis with real numbers
   • "Live demos, even if it's just how you use your environment" → GOAD + split-screen comparison + 
     live graph queries in Neo4j browser
   • "Acknowledgment of tradeoffs and limitations" → When to use orchestrator+memory vs ChatGPT vs 
     BloodHound vs manual, explicit failure modes
   • "Referencing prior work" → Built on LangChain/LangGraph, Neo4j graph database, NetExec, 
     Impacket, BloodHound data format

✅ AVOIDS WHAT THEY DON'T WANT:
   • NO "long introductions" → Jumps straight to live comparison demo with memory problem shown
   • NO "vendor product pitches" → MIT licensed, no monetization, full code + Neo4j schema
   • NO "purely theoretical attacks" → Tested on real networks, real cost data, real memory persistence
   • NO "hype without implementation details" → Actual code on screen, Neo4j Cypher queries, 
     three-layer architecture explained
   • NO "talks that could have been an email" → Live demos, graph queries, interactive architecture

✅ UNIQUE TECHNICAL VALUE FOR [UN]PROMPTED:
   • Only talk solving the memory problem with graph database integration
   • Only comparison: stateless general AI vs orchestrator with persistent graph memory
   • Only open-source AD AI orchestrator with Neo4j and BloodHound integration
   • Only submission with natural language to Cypher translation for AD attack graphs
   • Review board specifically asked for "BloodHound + LLM querying" - we deliver exactly this
   • Attendees get full architecture, Neo4j schema, and can deploy tonight
```

---

### 11. Demo Requirements (If asked)

```
TECHNICAL REQUIREMENTS:
• Laptop with terminal access (presenter will bring)
• Internet connection for LLM API calls (Groq/Claude)
• Neo4j database (running locally in Docker)
• Backup: Pre-recorded demo videos in case of connectivity issues

DEMO ENVIRONMENTS:
• Game of Active Directory (GOAD) - running locally in VMs
• SERPENTER installed and configured
• Neo4j database with sample AD graph already populated
• Neo4j Browser for live graph visualization
• All tools pre-installed (nmap, netexec, impacket, hashcat, ldapsearch)

LIVE DEMONSTRATIONS:
1. ChatGPT vs SERPENTER split-screen comparison
2. SERPENTER autonomous Kerberoasting chain with graph memory
3. Neo4j graph queries from natural language
4. BloodHound data import and querying
5. State tracking: "Which hosts haven't we tried these credentials on?"

BACKUP PLAN:
• Video recordings of all demos (in case live fails)
• Static terminal output captures
• Pre-populated Neo4j database with sample data
• Static screenshots of graph visualizations
• GitHub repo with README for attendees to follow along

NO A/V NEEDED BEYOND:
• Single screen connection (HDMI) - will show terminal + Neo4j browser side-by-side
• Optionally: if screen is large enough, split-screen with ChatGPT comparison
• Minimal slides (1-2 architecture diagrams max)
```

---

### 12. Speaker Bio (Usually required separately)

```
[Your Name] is a [Your Title] specializing in Active Directory security and AI orchestration 
for offensive security. After spending 6 months testing ChatGPT/Claude on real penetration 
tests and watching them fail 70% of the time, [he/she/they] built SERPENTER—an open-source 
AI orchestrator with Neo4j graph memory for AD pentesting.

The breaking point was watching junior pentesters repeatedly ask ChatGPT for the same 
information it had forgotten. The solution: LangGraph agent orchestration + Neo4j graph 
database for persistent attack memory + verified tool wrappers. Now used on real corporate 
engagements with 80% autonomous discovery success.

[Your Name] has [X years] experience in offensive security and believes AI orchestration 
should be transparent, graph-based memory should be standard, and tools should be free 
from vendor lock-in. SERPENTER (MIT licensed) proves you don't need $50k/year platforms 
when you have good architecture.

When not building AI orchestrators or querying Neo4j graphs, [Your Name] [interesting hobby].

GitHub: [your-github]
Twitter/X: [your-handle]
Website: [your-site]
```

---

### 13. Additional Notes for Reviewers (Optional field)

```
WHAT [UN]PROMPTED REVIEW BOARD SPECIFICALLY ASKED FOR:

From Track 3 CFP, the review board said:
• "Graph integration is next - BloodHound + LLM querying is powerful"
• "how are you leveraging genai to super power your teams?"
• "Practical examples from real engagements (not sanitized demos)"
• "Hackbots running on production systems, not CTFs"
• "AI ROI – measuring what AI replaced vs assisted vs made harder"

THIS TALK DELIVERS EXACTLY THAT + SOLVES THE MEMORY PROBLEM:

1. GRAPH INTEGRATION (What you asked for):
   • Neo4j graph database for persistent AD attack memory
   • BloodHound data import and natural language querying
   • Cypher queries generated from "find path to Domain Admin"
   • State tracking: never repeat failed credential attempts
   • 95% accuracy on natural language to Cypher translation

2. REAL DATA, NOT VIBES:
   • 15+ corporate AD engagements over 6 months
   • Measured success: 80% discovery, 60% exploitation, 95% memory queries
   • Cost analysis: $3/engagement (Groq) vs $50k/year commercial
   • Time savings: 5 hours per engagement average
   • Memory persistence: resume engagements weeks later with full context

3. HONEST TECHNICAL FAILURES:
   • ChatGPT/Claude tested first: 70% failure rate on real tasks
   • SERPENTER failure modes: novel 0-days (0%), complex reasoning (30%)
   • Live demo includes failures, not sanitized
   • Memory helps but doesn't solve everything: LLM still struggles with nuance

4. THREE-LAYER ARCHITECTURE (Deployable):
   • Layer 1: LangGraph ReAct agent orchestrator (show code)
   • Layer 2: Neo4j graph memory (show schema + Cypher queries)
   • Layer 3: Verified tool wrappers (show integration patterns)
   • MIT licensed, full code + Neo4j schema on GitHub
   • Fork it tonight, customize for your tools

5. NOT ANOTHER "AI PENTESTING" PITCH:
   • I'm not selling anything or building a startup
   • Built this for me because commercial tools lack memory and cost $50k/year
   • March 2026 will be full of AI security vendors—this is the practitioner response
   • Community-driven, graph-based, transparent

6. ADDRESSES BOARD'S SPECIFIC TECHNICAL INTERESTS:
   • "BloodHound + LLM querying" → Natural language to Cypher, import BloodHound JSON
   • "How to superpower teams" → Junior pentesters use this, 5 hrs saved per engagement
   • "ROI data" → Measured time/cost savings with real numbers + memory accuracy
   • "Production systems" → Real corporate AD with persistent graph across sessions
   • "What worked FOR YOU" → Personal experience, 6 months testing, honest metrics

THE MEMORY PROBLEM NOBODY TALKS ABOUT:

Commercial AD pentest tools and ChatGPT have the same flaw: they forget. You find 
credentials, crack passwords, discover vulnerabilities—then the tool forgets what it 
tried. You waste time repeating failed attempts or asking "what credentials did we find?"

Neo4j graph memory solves this:
- Every finding stored: users, computers, groups, relationships, credentials
- Every attempt tracked: "We tried sqlservice:password123 on DC01, it failed"
- Natural language querying: "Which Kerberoastable accounts haven't we cracked?"
- Persistent across sessions: Resume engagements weeks later with full context
- Attack path reasoning: "Show me all paths from compromised user to DA"

This is the missing layer between "AI can run tools" and "AI can actually pentest."

TECHNICAL DEPTH AVAILABLE:

This isn't a high-level overview. I can dive deep on:
- LangGraph agent architecture and reasoning loops
- Neo4j schema design for AD attack graphs (nodes, relationships, indexes)
- Natural language to Cypher translation (examples of prompts and generated queries)
- Tool wrapper patterns for any security tool (show how to add your own)
- BloodHound data import process (JSON to Neo4j graph transformation)
- State tracking algorithms (credential attempt history, tool execution logs)
- Multi-LLM provider orchestration (when to use which model)
- Cost/performance tradeoffs (Groq vs Claude vs GPT vs local Ollama)

CONFERENCE ORGANIZERS: 

Happy to adjust talk length if needed (can condense to 10-minute lightning talk focusing 
on just the memory architecture). Also available for panel discussions on AI orchestration, 
graph databases for security, or the future of agentic pentesting.

The graph memory architecture is production-ready and solves real problems. This is what 
practitioners sharing what actually works looks like.
```

---

## 🎯 QUICK COPY-PASTE CHECKLIST

When filling out the Sessionize form, copy these in order:

1. ✅ **Title:** I Tested ChatGPT on 15 Real Pentests and Built This AI Orchestrator Instead
2. ✅ **Short Abstract:** (600 char version above)
3. ✅ **Detailed Description:** (1800 char version above - includes memory architecture)
4. ✅ **Format:** 20-minute talk + 10 min Q&A
5. ✅ **Track:** Track 3 - Using AI for Offensive Security
6. ✅ **Level:** Intermediate to Advanced
7. ✅ **Takeaways:** (5 bullet points above - includes graph memory)
8. ✅ **Target Audience:** (description above)
9. ✅ **Tags:** AI Orchestration, Neo4j, Graph Databases, BloodHound, Memory Layer...
10. ✅ **Outline:** (00:00-00:30 breakdown above - includes memory demo)
11. ✅ **Bio:** (Fill in your details)
12. ✅ **Additional Notes:** (Optional - use if form allows, emphasizes graph integration)

---

## 📝 SUBMISSION TIPS

### Before You Submit:

1. **Test Neo4j Integration**
   - Set up Neo4j database with sample AD graph
   - Test natural language to Cypher translation
   - Verify BloodHound data import works
   - Practice graph queries in Neo4j Browser

2. **Test Your Demos**
   - Run SERPENTER on GOAD at least 3 times with memory persistence
   - Show graph queries working: "find path to Domain Admin"
   - Record backup videos
   - Ensure all tools work consistently

3. **Prepare Graph Visualizations**
   - Screenshots of Neo4j graph browser showing AD attack graph
   - Example Cypher queries with results
   - Schema diagram showing node types and relationships
   - Before/after: empty graph vs populated after pentest

4. **Prepare GitHub Repo**
   - Clean up code
   - Add comprehensive README with Neo4j setup instructions
   - Include Neo4j schema file (constraints, indexes)
   - Include example Cypher queries
   - Add LICENSE file (MIT)
   - Add architecture diagram (orchestrator + memory + tools)

### After Submission:

1. **If Accepted:**
   - Create 1-2 architecture slides (orchestrator + memory layers)
   - Practice talk 3+ times with timer
   - Test demos in unfamiliar network environments
   - Prepare for "what if WiFi fails" scenario
   - Have Neo4j database pre-populated with sample data

2. **If Not Accepted:**
   - Consider lightning talk version (10 min focusing on memory architecture)
   - Could fit Track 6 (Practical Tools) as well
   - Present at local BSides or DEFCON demo labs
   - Write detailed blog post about graph memory for AD pentesting

---

## 🔗 RELATED LINKS

**Conference:**
- CFP: https://sessionize.com/unprompted-the-ai-security-practitio/
- Website: https://unpromptedcon.org/
- Deadline: January 28, 2026, 11:59 PM PST

**SERPENTER Resources:**
- GitHub: [Add your repo URL]
- Documentation: [Add docs URL]
- Demo Videos: [Add demo URLs when created]
- GOAD Lab: https://github.com/Orange-Cyberdefense/GOAD
- Neo4j: https://neo4j.com/
- BloodHound: https://github.com/SpecterOps/BloodHound

---

## ✅ FINAL CHECKLIST BEFORE SUBMIT

- [ ] All form fields filled out
- [ ] Abstracts emphasize orchestrator + graph memory architecture
- [ ] No marketing language or vendor pitches
- [ ] Emphasizes "what actually works" with real metrics (80%, 60%, 95%)
- [ ] Mentions Neo4j graph memory and BloodHound integration
- [ ] Mentions it's open-source and free (not commercial)
- [ ] Demos are tested and working (including Neo4j)
- [ ] Backup materials prepared (videos, screenshots)
- [ ] Neo4j schema documented
- [ ] Speaker bio updated with correct contact info
- [ ] GitHub repo has Neo4j setup instructions
- [ ] Submission sent before Jan 28, 2026, 11:59 PM PST

---

**This is the graph-based memory architecture the review board asked for. Let's show them what's possible. 🐍 + 🔗**
