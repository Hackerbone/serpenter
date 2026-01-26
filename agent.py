"""
SERPENTER Agent - The core orchestration engine
"""

from typing import List, Dict, Any
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown

from config import Config
from tools import get_tools


console = Console()


SYSTEM_PROMPT = """You are SERPENTER, an elite AI pentesting agent specializing in Active Directory environments.

Your role is to assist junior penetration testers by:
1. Understanding their objectives in natural language
2. Breaking down complex tasks into actionable steps
3. Executing pentesting tools intelligently
4. Interpreting results and explaining findings
5. Suggesting next steps based on discoveries

CORE PRINCIPLES:
- Always explain your reasoning before taking action
- Prioritize stealth and OPSEC when relevant
- Identify the MOST important findings, not just everything
- Teach the user WHY you're doing each step
- Be concise but thorough

TOOL USAGE STRATEGY:
- Start with reconnaissance (nmap for discovery)
- Use netexec for SMB/WinRM/LDAP enumeration (shares, users, sessions)
- Use ldapsearch for detailed AD queries (users, groups, SPNs, AS-REP, GPOs, trusts)
- Use impacket tool for AD exploitation (secretsdump, GetUserSPNs, GetNPUsers, psexec, wmiexec, etc.)
- Use certipy for AD Certificate Services (AD CS) attacks and certificate abuse (ESC1-8, golden certificates, shadow credentials)
- Chain tools together logically (discover hosts → enumerate shares/users → extract hashes → crack passwords)
- Use hashcat for password cracking after obtaining hashes (NTLM, NetNTLMv2, Kerberoast, AS-REP)
- Parse and filter results to highlight what matters
- NEVER use bash for ldapsearch, impacket, certipy, or complex multi-line scripts

CRITICAL - NetExec Command Format:
- Correct: netexec smb 192.168.1.0/24 -u '' -p '' --users
- WRONG: netexec -target 192.168.1.0/24 -protocol smb -action users
- Protocol and target are POSITIONAL arguments, not flags
- Actions use -- prefix (--users, --shares, --groups)
- For null session, use empty strings: -u '' -p ''
- When suggesting commands to users, ALWAYS use the correct format above

ACTIVE DIRECTORY FOCUS:
- Look for Domain Controllers (port 389/LDAP, 88/Kerberos, 445/SMB)
- Identify accessible SMB shares (could contain credentials/intel)
- Find accounts with weak authentication (null sessions, guest access)
- Map trust relationships and privilege paths

LDAPSEARCH TOOL USAGE:
- Use query_type for preset queries: users, computers, groups, admins, spns, asrep, unconstrained, gpos, trusts
- Use filter for custom LDAP queries
- Requires base_dn (e.g., "DC=corp,DC=local") and credentials for most queries
- Great for finding Kerberoastable accounts (query_type="spns") and AS-REP roastable (query_type="asrep")

IMPACKET TOOL USAGE:
- Use impacket tool with script= parameter to select the Impacket script
- secretsdump: DCSync, SAM/LSA dumps (extra_args="-just-dc" for DCSync only)
- GetUserSPNs: Kerberoasting (extra_args="-request -outputfile krb.txt")
- GetNPUsers: AS-REP Roasting (extra_args="-request -outputfile asrep.txt")  
- psexec/wmiexec/smbexec: Remote execution shells
- lookupsid: Enumerate users via SID brute force
- Authentication: password OR hashes (pass-the-hash) OR kerberos=True

PASSWORD CRACKING WITH HASHCAT:
- NTLM hashes (mode 1000): From SAM dumps, NTDS.dit, secretsdump
- NetNTLMv2 (mode 5600): From Responder, LLMNR/NBT-NS poisoning
- Kerberoast (mode 13100): TGS tickets from GetUserSPNs
- AS-REP Roasting (mode 18200): From accounts without pre-auth
- Start with dictionary attacks using rockyou.txt
- Add rules (best64.rule, OneRuleToRuleThemAll) for mutations
- Use targeted wordlists (company name, city, common patterns)

CERTIFICATE ATTACKS WITH CERTIPY:
- Use certipy to enumerate and abuse Active Directory Certificate Services (AD CS)
- Find vulnerable certificate templates with action="find" and extra_args="-vulnerable"
- Common attack scenarios (ESC1-8):
  * ESC1: Request certificate with arbitrary SAN (Subject Alternative Name)
  * ESC4: Shadow credentials attack (add key credentials to accounts)
  * ESC8: NTLM relay to AD CS HTTP endpoints
- Request certificates with action="req", authenticate with action="auth"
- Shadow credentials: action="shadow" to add shadow creds, then auth
- Golden certificate: action="ca" to dump CA key (requires admin), action="forge" to create forged certs

RESPONSE FORMAT:
1. Acknowledge the objective
2. Explain your strategy (1-2 sentences)
3. Execute tools
4. Summarize key findings
5. Suggest next steps

Remember: You're a mentor, not just a tool runner. Help the user understand AD pentesting methodology.
"""


class SerpenterAgent:
    """Main agent orchestrator"""

    def __init__(self, config: Config):
        self.config = config
        self.console = Console()

        # Initialize LLM (provider-agnostic)
        self.llm = config.get_llm()

        # Get tools with config
        self.tools = get_tools(config.tools_enabled, config)

        # Create agent using LangGraph
        # The system prompt is passed via the prompt parameter
        self.agent = create_react_agent(
            self.llm, 
            self.tools,
            prompt=SystemMessage(content=SYSTEM_PROMPT)
        )

        # Chat history for context
        self.chat_history = []

    def execute_objective(self, objective: str) -> Dict[str, Any]:
        """Execute a pentesting objective"""

        try:
            # Show objective
            self.console.print(
                Panel(
                    f"[bold]{objective}[/bold]",
                    title="🎯 Objective",
                    border_style="green",
                )
            )

            # Execute with agent
            self.console.print(
                "\n[bold cyan]🐍 SERPENTER is analyzing...[/bold cyan]\n"
            )

            # Build messages for LangGraph
            messages = self.chat_history + [HumanMessage(content=objective)]

            # Stream the agent execution for real-time feedback
            output = ""
            intermediate_steps = []
            
            if self.config.verbose or self.config.debug:
                # Stream with live updates
                for event in self.agent.stream({"messages": messages}, stream_mode="updates"):
                    for node_name, node_data in event.items():
                        if node_name == "tools":
                            # Tool execution
                            messages_in_node = node_data.get("messages", [])
                            for msg in messages_in_node:
                                if hasattr(msg, 'content') and msg.content:
                                    # Show full output without truncation
                                    tool_output = str(msg.content)
                                    self.console.print(
                                        Panel(
                                            tool_output,
                                            title=f"[cyan]🔧 Tool Output[/cyan]",
                                            border_style="blue",
                                            padding=(0, 1),
                                        )
                                    )
                        elif node_name == "agent":
                            # Agent reasoning
                            messages_in_node = node_data.get("messages", [])
                            for msg in messages_in_node:
                                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                                    for tool_call in msg.tool_calls:
                                        tool_name = tool_call.get('name', 'unknown')
                                        tool_args = tool_call.get('args', {})
                                        self.console.print(
                                            f"[bold yellow]⚡ Calling:[/bold yellow] [cyan]{tool_name}[/cyan]"
                                        )
                                        if self.config.debug:
                                            self.console.print(f"[dim]  Args: {tool_args}[/dim]")
                                        intermediate_steps.append((tool_call, None))
                                if hasattr(msg, 'content') and isinstance(msg, AIMessage) and msg.content:
                                    output = msg.content
            else:
                # Non-streaming mode (faster, less output)
                # Still show minimal progress
                tool_count = 0
                for event in self.agent.stream({"messages": messages}, stream_mode="updates"):
                    for node_name, node_data in event.items():
                        if node_name == "agent":
                            messages_in_node = node_data.get("messages", [])
                            for msg in messages_in_node:
                                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                                    for tool_call in msg.tool_calls:
                                        tool_count += 1
                                        tool_name = tool_call.get('name', 'unknown')
                                        self.console.print(f"[dim]⚙ Running tool {tool_count}: {tool_name}...[/dim]")
                                        intermediate_steps.append((tool_call, None))
                                if hasattr(msg, 'content') and isinstance(msg, AIMessage) and msg.content:
                                    output = msg.content

            if not output:
                output = "No response generated"

            # Display final response
            self.console.print()  # Spacing
            self._show_response(output)

            # Update chat history
            self.chat_history.append(HumanMessage(content=objective))
            self.chat_history.append(AIMessage(content=output))

            # Keep history manageable
            if len(self.chat_history) > 10:
                self.chat_history = self.chat_history[-10:]

            return {"success": True, "output": output, "steps": intermediate_steps}

        except Exception as e:
            self.console.print(f"\n[red]❌ Error: {e}[/red]")
            if self.config.debug:
                self.console.print_exception()
            return {"success": False, "error": str(e)}

    def _show_intermediate_steps(self, steps: List[tuple]):
        """Display intermediate reasoning and tool calls"""

        self.console.print("\n[bold yellow]🔍 Agent Reasoning:[/bold yellow]\n")

        for i, (action, observation) in enumerate(steps, 1):
            # Show tool call (LangGraph format)
            if hasattr(action, 'get'):
                tool_name = action.get('name', 'unknown')
                tool_input = action.get('args', {})
            else:
                tool_name = str(action)
                tool_input = ""

            self.console.print(f"[bold cyan]Step {i}: {tool_name}[/bold cyan]")
            self.console.print(f"[dim]Input: {tool_input}[/dim]")

            # Show observation (truncated)
            if observation:
                obs_preview = str(observation)[:500]
                if len(str(observation)) > 500:
                    obs_preview += "..."

                self.console.print(
                    Panel(
                        obs_preview,
                        title="Tool Output",
                        border_style="blue",
                        padding=(0, 1),
                    )
                )
            self.console.print()

    def _show_response(self, response: str):
        """Display agent's final response"""

        self.console.print()
        self.console.print(
            Panel(
                Markdown(response),
                title="💬 SERPENTER Response",
                border_style="green",
                padding=(1, 2),
            )
        )
        self.console.print()
