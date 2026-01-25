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
Beyond Brute Force: Building an AI Copilot for Active Directory Pentesting
```

**Alternate titles (if needed):**
- Why ChatGPT Fails at Pentesting: Building SERPENTER, an AD-Focused AI Copilot
- SERPENTER: An Open-Source AI Agent for Active Directory Pentesting
- From ChatGPT to Copilot: Purpose-Built AI for AD Offensive Security

---

### 2. Session Description / Abstract (Required)
**Character limit: Usually 500-1000 characters for short, 2000-3000 for detailed**

#### SHORT VERSION (600 characters):

```
You've asked ChatGPT for pentesting help. It gave you broken commands, forgot your findings, 
and overwhelmed you with generic advice. General-purpose AI assistants aren't built for 
active engagements.

This talk demonstrates SERPENTER—a fully open-source, specialized AI copilot for Active 
Directory pentesting. I'll show live comparisons of ChatGPT vs. SERPENTER on the same AD 
tasks, walk through the architecture (LangGraph + tool wrappers for NetExec, Impacket, 
Hashcat), and demo it against GOAD in real-time.

You'll learn: when to use general AI vs. specialized copilots, how to build your own tool 
wrappers, what works in production, and what fails spectacularly. Full code available—
deploy it Monday.
```

#### DETAILED VERSION (1800 characters):

```
General-purpose AI assistants like ChatGPT and Claude can explain security concepts, but 
they fail at active pentesting engagements. They hallucinate tool syntax, forget previous 
findings, and can't execute or parse outputs. After testing extensively, we built SERPENTER—
a purpose-built, open-source AI copilot specialized for Active Directory pentesting.

WHAT YOU'LL SEE:

Live Comparison Demo (5 min):
Split-screen demonstration of ChatGPT vs. SERPENTER performing the same AD task. ChatGPT 
gives broken NetExec syntax and forgets context. SERPENTER correctly chains nmap → ldapsearch 
→ Impacket GetUserSPNs → Hashcat with explanations.

Architecture Deep Dive (5 min):
Walkthrough of actual code: LangChain tool wrappers with rich descriptions, LangGraph ReAct 
agent loops, and system prompts that teach AD methodology. Simple enough to build yourself.

Live Demo on GOAD (5 min):
"Find and exploit Kerberoastable accounts in 192.168.56.0/24" - Watch SERPENTER autonomously 
discover the DC, enumerate SPNs, request TGS tickets, crack passwords, and suggest next steps. 
Including failures—not a sanitized demo.

Honest Retrospective (5 min):
Where AI excels (tool selection, parsing, chaining) and where it fails (novel exploits, 
state persistence, complex multi-step attacks). Cost analysis: $1-5 per engagement vs. 
weeks of manual work.

WHAT YOU'LL LEARN:

• Why general AI assistants fail at pentesting (with specific examples)
• When to use ChatGPT/Claude vs. specialized copilots
• How to build tool wrappers for your own security workflows
• What works in production AD environments (tested on GOAD + real networks)
• Honest pros/cons of AI orchestration for offensive security
• Code patterns you can deploy immediately (MIT licensed)

This is not a vendor pitch or theoretical exercise. It's a working tool, tested on real 
engagements, with full source code available. Come see where AI copilots actually help 
offensive security—and where they don't.
```

---

### 3. Session Format (Required)
**Select one:**

☑️ **Full Session (20 minutes + 10 min Q&A)**  
☐ Lightning Talk (10 minutes)

**Why 20 minutes:**
- 5 min: Live comparison demo (ChatGPT vs SERPENTER)
- 5 min: Architecture walkthrough with code
- 5 min: Live GOAD demo (Kerberoasting chain)
- 5 min: Honest retrospective (what works/fails)
- 10 min: Q&A + code discussion

---

### 4. Track Selection (Required)

☑️ **Track 3: Using AI for Offensive Security**

**Why this track:**
- Shows AI tool deployed for offensive security (not theoretical)
- Demonstrates agentic pentesting on production-like systems (GOAD)
- Includes honest assessment of what worked and what failed
- Provides actionable code others can use immediately
- Not a vendor pitch—fully open-source

---

### 5. Session Level (If asked)

☑️ **Intermediate**

**Audience expectations:**
- Familiar with Active Directory pentesting basics (Kerberoasting, DCSync concepts)
- Some Python/development experience helpful but not required
- Interested in AI automation for security workflows
- Want practical, deployable tools (not just research)

---

### 6. Key Takeaways / Learning Outcomes (Required)
**Usually 3-5 bullet points**

```
1. Understand why general-purpose AI assistants (ChatGPT/Claude) fail at active pentesting 
   engagements, with specific examples of broken syntax and lost context

2. Learn how to build specialized AI copilots using LangChain tool wrappers and LangGraph 
   agents—architecture patterns you can apply to your own security workflows

3. See real-world performance on Active Directory environments: success rates for discovery 
   (80%), exploitation chains (60%), and specific failure modes

4. Deploy immediately: Walk away with open-source code (SERPENTER) and tool wrapper patterns 
   for nmap, NetExec, Impacket, Hashcat, and ldapsearch

5. Make informed decisions: Understand when to use specialized copilots vs. general AI, cost 
   tradeoffs ($1-5/engagement vs. manual work), and honest limitations (no exploit dev, 
   limited state tracking)
```

---

### 7. Target Audience (Required)
**Who should attend this talk?**

```
PRIMARY AUDIENCE:
• Penetration testers and red teamers working in AD/internal environments
• Security engineers building automation for offensive security workflows
• Tool developers interested in AI orchestration for security tasks
• Security researchers exploring AI agents for offensive applications

WHAT THEY'LL GAIN:
• Penetration testers: A free, deployable tool for AD engagements + understanding when AI helps
• Security engineers: Architecture patterns for building their own AI copilots
• Tool developers: Real-world lessons on LLM limitations and tool wrapper design
• Researchers: Honest data on what works/fails in agentic pentesting

NOT FOR:
• Complete beginners to AD pentesting (assumes basic knowledge)
• People only interested in defensive AI applications
• Those looking for fully autonomous pentesting (we're explicit: copilot, not autopilot)
```

---

### 8. Tags / Keywords (If asked)
**Usually 5-10 tags**

```
AI Agents, Active Directory, Pentesting, LangChain, LangGraph, Offensive Security, 
Open Source, Red Teaming, Automation, Tool Orchestration, Kerberoasting, NetExec, 
Impacket, AD Security, ReAct Agents
```

---

### 9. Session Outline / Agenda (If asked)
**Detailed minute-by-minute breakdown**

```
00:00-00:05 | The Problem: Why General AI Fails at Pentesting
             • Live split-screen demo: ChatGPT vs SERPENTER on same AD task
             • Show ChatGPT giving broken NetExec syntax in real-time
             • Show SERPENTER executing correctly with contextual guidance
             • Key point: General AI ≠ Specialized Copilot

00:05-00:10 | Architecture Deep Dive: How to Build Your Own
             • Show actual code from tools.py (tool wrapper patterns)
             • System prompt design for teaching AD methodology
             • LangGraph ReAct agent loop explanation
             • Key point: Simple architecture anyone can replicate

00:10-00:15 | Live Demo: SERPENTER on Game of Active Directory (GOAD)
             • Single command: "Find and exploit Kerberoastable accounts"
             • Watch autonomous chain: nmap → ldapsearch → GetUserSPNs → hashcat
             • Show both successes AND failures (no sanitized demo)
             • Key point: Works in practice, not just theory

00:15-00:20 | Honest Retrospective: What Works, What Doesn't
             • Where AI excels: tool selection, parsing, contextual chaining
             • Where AI fails: novel exploits, persistent state, complex reasoning
             • Cost/benefit: $1-5 API costs vs. weeks of manual enumeration
             • Comparison: When to use SERPENTER vs. ChatGPT vs. commercial tools

00:20-00:30 | Q&A + Open Discussion
             • Code walkthrough for interested attendees
             • "How do I add my own tools?"
             • "What benchmarks would you recommend?"
             • Discussion: future of AI copilots in offensive security
```

---

### 10. What Makes This Submission Strong (For reviewers)

```
✅ MATCHES TRACK 3 REQUIREMENTS:
   • Shows AI tool DEPLOYED for offensive security (not theoretical)
   • Demonstrates "agentic penetration testing on production systems" (GOAD)
   • Provides "agentic workflows for research and attack"

✅ MEETS CONFERENCE GOALS:
   • "Specific examples with enough detail others can apply" → Full architecture + code
   • "Honest assessment of what worked and what didn't" → Shows failures, not just wins
   • "Data, metrics, or real-world validation" → Tested on GOAD + real networks, success rates
   • "Clear takeaways for attendees" → Deployable code, reusable patterns
   • "Acknowledgment of tradeoffs and limitations" → Explicit pros/cons section

✅ NOT WHAT YOU'RE AVOIDING:
   • NOT a vendor product pitch → Fully open-source, MIT licensed
   • NOT purely theoretical → Tested on real environments, not CTFs
   • NOT hype without details → Shows actual code, architecture, failures
   • NOT "could have been a blog post" → Live demos, code walkthrough, Q&A

✅ UNIQUE VALUE:
   • Only talk comparing general AI vs. specialized copilots for pentesting
   • Only open-source AD-focused AI agent being presented
   • Fills gap: practical AI for offensive security with honest assessment
   • Attendees can deploy the tool immediately (not wait for research/products)
```

---

### 11. Demo Requirements (If asked)

```
TECHNICAL REQUIREMENTS:
• Laptop with terminal access (presenter will bring)
• Internet connection for LLM API calls (Groq/Claude)
• Backup: Pre-recorded demo videos in case of connectivity issues

DEMO ENVIRONMENTS:
• Game of Active Directory (GOAD) - running locally in VMs
• SERPENTER installed and configured
• All tools pre-installed (nmap, netexec, impacket, hashcat, ldapsearch)

BACKUP PLAN:
• Video recordings of all demos (in case live fails)
• Static terminal output captures
• GitHub repo with README for attendees to follow along

NO A/V NEEDED BEYOND:
• Single screen connection (HDMI)
• Terminal-only, no slides
```

---

### 12. Speaker Bio (Usually required separately)

```
[Your Name] is a [Your Title] specializing in Active Directory security and AI automation. 
After two years of testing commercial AD pentesting tools and watching junior pentesters 
struggle with ChatGPT's hallucinated commands, [he/she/they] built SERPENTER—an open-source 
AI copilot for AD pentesting. [Your Name] has [X years] experience in offensive security, 
contributing to [relevant projects/communities], and believes the future of security 
automation should be transparent, community-driven, and free from vendor lock-in.

When not building AI agents or testing them against GOAD, [Your Name] [interesting hobby 
or community involvement].

GitHub: [your-github]
Twitter/X: [your-handle]
Website: [your-site]
```

---

### 13. Additional Notes for Reviewers (Optional field)

```
WHY THIS TALK MATTERS NOW:

The security community is at an inflection point with AI. Everyone is trying to use ChatGPT 
for pentesting, but it's the wrong tool. Commercial AI pentesting platforms cost $10k-50k/year. 
There's a gap for purpose-built, open-source AI copilots that practitioners can actually deploy.

WHAT MAKES THIS DIFFERENT:

1. HONEST: Shows failures, not just successes. LLMs hallucinate, agents make mistakes—we 
   show exactly where and how.

2. ACTIONABLE: Full code on GitHub (MIT licensed). Attendees can clone it and use it on 
   their next engagement.

3. TESTED: Not a prototype. Used on GOAD and real corporate networks. We have data on what 
   works (80% success on discovery, 60% on exploitation chains).

4. EDUCATIONAL: Teaches both pentesters (how to use AI copilots) and developers (how to 
   build them).

5. TIMELY: Conference is March 2026. By then, dozens of "AI pentesting" vendors will be 
   pitching. This is the open-source, non-commercial counterpoint.

I'm not selling anything. I'm sharing what I built, what I learned, and what others can 
use today. That's exactly what [un]prompted wants: practitioners sharing what actually works.

CONFERENCE ORGANIZERS: Happy to adjust talk length if needed (can condense to 10-minute 
lightning talk). Also available for panel discussions on AI in offensive security.
```

---

## 🎯 QUICK COPY-PASTE CHECKLIST

When filling out the Sessionize form, copy these in order:

1. ✅ **Title:** Beyond Brute Force: Building an AI Copilot for Active Directory Pentesting
2. ✅ **Short Abstract:** (600 char version above)
3. ✅ **Detailed Description:** (1800 char version above)
4. ✅ **Format:** 20-minute talk + 10 min Q&A
5. ✅ **Track:** Track 3 - Using AI for Offensive Security
6. ✅ **Level:** Intermediate
7. ✅ **Takeaways:** (5 bullet points above)
8. ✅ **Target Audience:** (description above)
9. ✅ **Tags:** AI Agents, Active Directory, Pentesting, LangChain, Open Source...
10. ✅ **Outline:** (00:00-00:30 breakdown above)
11. ✅ **Bio:** (Fill in your details)
12. ✅ **Additional Notes:** (Optional - use if form allows)

---

## 📝 SUBMISSION TIPS

### Before You Submit:

1. **Test Your Demos**
   - Run SERPENTER on GOAD at least 3 times
   - Record backup videos
   - Ensure all tools work consistently

2. **Prepare GitHub Repo**
   - Clean up code
   - Add comprehensive README
   - Include demo scripts
   - Add LICENSE file (MIT)

3. **Create Supporting Materials**
   - Architecture diagram (simple, terminal-friendly)
   - Demo script with exact commands
   - Failure examples documented

### After Submission:

1. **If Accepted:**
   - Create minimal architecture slide (maybe 1-2 max)
   - Practice talk 3+ times with timer
   - Test demos in unfamiliar network environments
   - Prepare for "what if WiFi fails" scenario

2. **If Not Accepted:**
   - Consider lightning talk version (10 min)
   - Could fit Track 6 (Practical Tools) as well
   - Present at local BSides or DEFCON demo labs

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

---

## ✅ FINAL CHECKLIST BEFORE SUBMIT

- [ ] All form fields filled out
- [ ] Abstracts are within character limits
- [ ] No marketing language or vendor pitches
- [ ] Emphasizes "what actually works" and "honest failures"
- [ ] Mentions it's open-source and free (not commercial)
- [ ] Demos are tested and working
- [ ] Backup materials prepared
- [ ] Speaker bio updated with correct contact info
- [ ] Submission sent before Jan 28, 2026, 11:59 PM PST

---

**Good luck! This is exactly the kind of practical, honest, actionable talk [un]prompted wants. 🐍**
