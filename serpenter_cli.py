#!/usr/bin/env python3
"""
SERPENTER - AD Pentesting Semi-Autonomous Agent
A CLI companion for junior pentesters in Active Directory environments.
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.live import Live
from rich.spinner import Spinner
from rich.prompt import Prompt
import sys
from pathlib import Path

from agent import SerpenterAgent
from assessment import InternalAssessmentRunner
from config import Config

console = Console()

BANNER = """
╔═══════════════════════════════════════════════════════════╗
║   _____ _____ ____  ____  _____ _   _ _____ _____ ____    ║
║  / ____|  ___|  _ \\|  _ \\| ____| \\ | |_   _| ____|  _ \\   ║
║  \\___ \\| |__ | |_) | |_) |  _| |  \\| | | | |  _| | |_) |  ║
║   ___) |  __||  _ <|  __/| |___| |\\  | | | | |___|  _ <   ║
║  |____/|_|   |_| \\_\\_|   |_____|_| \\_| |_| |_____|_| \\_\\  ║
║                                                           ║
║         AD Pentesting Semi-Autonomous Agent              ║
║              Stealth • Intelligence • Precision           ║
╚═══════════════════════════════════════════════════════════╝
"""

@click.group(invoke_without_command=True)
@click.pass_context
@click.option('--debug', is_flag=True, help='Enable debug mode')
def cli(ctx, debug):
    """SERPENTER - Your AI companion for AD penetration testing"""
    
    if ctx.invoked_subcommand is None:
        console.print(BANNER, style="bold cyan")
        console.print("\n[yellow]Type 'serpenter --help' for usage information[/yellow]\n")
        interactive_mode(debug, False, False, None)

@cli.command()
@click.argument('objective', nargs=-1)
@click.option('--target', '-t', help='Target subnet or host')
@click.option('--auto', is_flag=True, help='Run in autonomous mode')
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.option('--sudo', is_flag=True, help='Run commands with sudo privileges')
@click.option('--confirm', is_flag=True, help='Ask for confirmation before executing commands')
@click.option('--config', '-c', help='Path to config file', type=click.Path(exists=True))
def run(objective, target, auto, debug, sudo, confirm, config):
    """Execute a pentesting objective
    
    Examples:
        serpenter run "find all SMB shares in 192.168.1.0/24"
        serpenter run -t 10.0.0.0/24 "enumerate domain users"
        serpenter run --auto "get path to domain admin"
        serpenter run --sudo "scan subnet for open ports"
        serpenter run --confirm "dump credentials from DC"
        serpenter run --config custom.yaml "scan subnet"
    """
    
    objective_text = ' '.join(objective) if objective else None
    
    if not objective_text:
        console.print("[red]Error: Please provide an objective[/red]")
        console.print("[yellow]Example: serpenter run \"find all SMB shares in 192.168.1.0/24\"[/yellow]")
        sys.exit(1)
    
    # Add target to objective if provided separately
    if target and target not in objective_text:
        objective_text = f"{objective_text} (target: {target})"
    
    console.print(BANNER, style="bold cyan")
    console.print(f"\n[bold green]Objective:[/bold green] {objective_text}\n")
    
    # Initialize agent with config from YAML
    agent_config = Config.from_yaml(Path(config) if config else None)
    # Override with CLI flags
    if debug:
        agent_config.debug = True
    if auto:
        agent_config.auto_mode = True
    if sudo:
        agent_config.use_sudo = True
    if confirm:
        agent_config.confirm_commands = True
    
    agent = SerpenterAgent(agent_config)
    
    # Execute
    try:
        with console.status("[bold cyan]SERPENTER is thinking...", spinner="dots"):
            agent.execute_objective(objective_text)
    except KeyboardInterrupt:
        console.print("\n[yellow]Operation cancelled by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        if debug:
            console.print_exception()
        sys.exit(1)

@cli.command("internal-assessment")
@click.argument("target")
@click.option("--domain", help="AD domain name, e.g. corp.local")
@click.option("--username", "-u", help="Username for authenticated enumeration")
@click.option("--password", "-p", help="Password for authenticated enumeration")
@click.option("--hashes", help="NTLM hashes for pass-the-hash style auth, e.g. :NT_HASH")
@click.option("--dc-ip", help="Domain Controller IP/hostname. Defaults to target.")
@click.option("--base-dn", help="LDAP base DN, e.g. DC=corp,DC=local. Derived from --domain when possible.")
@click.option("--allow-exploits", is_flag=True, help="Enable active exploit validation steps. Off by default.")
@click.option("--rce-target", help="Single host for non-destructive RCE validation when --allow-exploits is set")
@click.option("--rce-command", default="whoami", show_default=True, help="Command used for RCE validation")
@click.option("--local-auth", is_flag=True, help="Use local authentication for SMB RCE validation")
@click.option("--no-ai", is_flag=True, help="Disable LLM synthesis and use deterministic summary only.")
@click.option("--output", "-o", type=click.Path(), help="Write JSON report to this path")
@click.option("--debug", is_flag=True, help="Enable debug mode")
@click.option("--sudo", is_flag=True, help="Run configured tools with sudo privileges")
@click.option("--confirm", is_flag=True, help="Ask for confirmation before executing commands")
@click.option("--config", "-c", help="Path to config file", type=click.Path(exists=True))
def internal_assessment(
    target,
    domain,
    username,
    password,
    hashes,
    dc_ip,
    base_dn,
    allow_exploits,
    rce_target,
    rce_command,
    local_auth,
    no_ai,
    output,
    debug,
    sudo,
    confirm,
    config,
):
    """Run a full Serpenter-native internal assessment.

    The report follows Bugbase-style concepts: entities, findings, attack paths,
    evidence, and analyst summary. Exploit validation is disabled unless
    --allow-exploits is set.
    """

    console.print(BANNER, style="bold cyan")

    agent_config = Config.from_yaml(Path(config) if config else None, require_llm=False)
    if debug:
        agent_config.debug = True
    if sudo:
        agent_config.use_sudo = True
    if confirm:
        agent_config.confirm_commands = True
    if no_ai:
        agent_config.assessment_ai_synthesis = False
        agent_config.assessment_require_ai = False

    effective_allow_exploits = allow_exploits or agent_config.assessment_allow_exploits
    runner = InternalAssessmentRunner(agent_config)

    try:
        runner.run(
            target,
            domain=domain,
            username=username,
            password=password,
            hashes=hashes,
            dc_ip=dc_ip,
            base_dn=base_dn,
            allow_exploits=effective_allow_exploits,
            rce_target=rce_target,
            rce_command=rce_command,
            local_auth=local_auth,
            output_path=Path(output) if output else None,
        )
    except KeyboardInterrupt:
        console.print("\n[yellow]Internal assessment cancelled by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        if debug:
            console.print_exception()
        sys.exit(1)

@cli.command()
@click.option('--debug', is_flag=True, help='Enable debug mode')
@click.option('--sudo', is_flag=True, help='Run commands with sudo privileges')
@click.option('--confirm', is_flag=True, help='Ask for confirmation before executing commands')
@click.option('--config', '-c', help='Path to config file', type=click.Path(exists=True))
def interactive(debug, sudo, confirm, config):
    """Start interactive mode"""
    console.print(BANNER, style="bold cyan")
    interactive_mode(debug, sudo, confirm, config)

def interactive_mode(debug=False, sudo=False, confirm=False, config_path=None):
    """Interactive chat mode with the agent"""
    
    console.print("\n[bold cyan]Interactive Mode[/bold cyan]")
    console.print("[dim]Enter your pentesting objectives naturally.[/dim]")
    console.print("[dim]Commands: /help, /debug, /verbose, /quiet, /sudo, /confirm, /status, exit[/dim]\n")
    
    agent_config = Config.from_yaml(Path(config_path) if config_path else None)
    if debug:
        agent_config.debug = True
    if sudo:
        agent_config.use_sudo = True
    if confirm:
        agent_config.confirm_commands = True
    agent_config.auto_mode = False
    
    agent = SerpenterAgent(agent_config)
    
    def show_status():
        """Show current configuration status"""
        console.print("\n[bold cyan]📊 Current Settings:[/bold cyan]")
        console.print(f"  Debug Mode:   [{'green' if agent_config.debug else 'yellow'}]{'ON' if agent_config.debug else 'OFF'}[/]")
        console.print(f"  Verbose Mode: [{'green' if agent_config.verbose else 'yellow'}]{'ON' if agent_config.verbose else 'OFF'}[/]")
        console.print(f"  Sudo Mode:    [{'green' if agent_config.use_sudo else 'yellow'}]{'ON' if agent_config.use_sudo else 'OFF'}[/]")
        console.print(f"  Confirm Cmds: [{'green' if agent_config.confirm_commands else 'yellow'}]{'ON' if agent_config.confirm_commands else 'OFF'}[/]")
        console.print(f"  LLM Provider: [cyan]{agent_config.llm_provider}[/cyan]")
        console.print(f"  Model:        [cyan]{agent_config.llm_model}[/cyan]")
        console.print(f"  Max Iters:    [cyan]{agent_config.max_iterations}[/cyan]")
    
    def show_help():
        """Show interactive commands help"""
        console.print("\n[bold cyan]🐍 SERPENTER Interactive Commands:[/bold cyan]\n")
        console.print("[bold yellow]Visibility Controls:[/bold yellow]")
        console.print("  [green]/debug[/green]    - Toggle debug mode (shows detailed tool arguments)")
        console.print("  [green]/verbose[/green]  - Toggle verbose mode (shows real-time tool execution)")
        console.print("  [green]/quiet[/green]    - Quiet mode (minimal output, fastest)")
        console.print("  [green]/status[/green]   - Show current settings")
        console.print()
        console.print("[bold yellow]Security Controls:[/bold yellow]")
        console.print("  [green]/sudo[/green]     - Toggle sudo mode (run tools with elevated privileges)")
        console.print("  [green]/confirm[/green]  - Toggle command confirmation (ask before executing)")
        console.print()
        console.print("[bold yellow]Other Commands:[/bold yellow]")
        console.print("  [green]/help[/green]     - Show this help message")
        console.print("  [green]exit[/green]      - Exit SERPENTER (or: quit, q)")
        console.print()
        console.print("[bold cyan]Modes Explained:[/bold cyan]")
        console.print("  [bold]Quiet Mode[/bold]    → Minimal output, fastest execution")
        console.print("  [bold]Verbose Mode[/bold]  → Shows tool calls in real-time")
        console.print("  [bold]Debug Mode[/bold]    → Shows tool arguments + full details")
        console.print("  [bold]Sudo Mode[/bold]     → Run certain tools with sudo (nmap, netexec, hashcat)")
        console.print("  [bold]Confirm Mode[/bold]  → Ask for confirmation before each command")
        console.print()
    
    while True:
        try:
            # Get user input
            user_input = Prompt.ask("\n[bold green]serpenter>[/bold green]")
            
            # Handle commands
            if user_input.lower() in ['exit', 'quit', 'q']:
                console.print("\n[cyan]Exiting SERPENTER. Stay stealthy! 🐍[/cyan]")
                break
            
            if not user_input.strip():
                continue
            
            # Special commands
            if user_input.startswith('/'):
                cmd = user_input.lower().strip()
                
                if cmd == '/help':
                    show_help()
                elif cmd == '/status':
                    show_status()
                elif cmd == '/debug':
                    agent_config.debug = not agent_config.debug
                    status = "enabled" if agent_config.debug else "disabled"
                    console.print(f"\n[yellow]🔧 Debug mode {status}[/yellow]")
                    if agent_config.debug:
                        console.print("[dim]  → Will show detailed tool arguments and execution[/dim]")
                elif cmd == '/verbose':
                    agent_config.verbose = not agent_config.verbose
                    status = "enabled" if agent_config.verbose else "disabled"
                    console.print(f"\n[yellow]📢 Verbose mode {status}[/yellow]")
                    if agent_config.verbose:
                        console.print("[dim]  → Will show real-time tool execution[/dim]")
                elif cmd == '/quiet':
                    agent_config.verbose = False
                    agent_config.debug = False
                    console.print("\n[yellow]🔇 Quiet mode enabled (minimal output)[/yellow]")
                elif cmd == '/sudo':
                    agent_config.use_sudo = not agent_config.use_sudo
                    status = "enabled" if agent_config.use_sudo else "disabled"
                    console.print(f"\n[yellow]🔐 Sudo mode {status}[/yellow]")
                    if agent_config.use_sudo:
                        console.print("[dim]  → Tools will run with elevated privileges[/dim]")
                        console.print("[dim]  → Applies to: nmap, netexec, hashcat[/dim]")
                elif cmd == '/confirm':
                    agent_config.confirm_commands = not agent_config.confirm_commands
                    status = "enabled" if agent_config.confirm_commands else "disabled"
                    console.print(f"\n[yellow]✋ Command confirmation {status}[/yellow]")
                    if agent_config.confirm_commands:
                        console.print("[dim]  → You will be asked to confirm each command before execution[/dim]")
                else:
                    console.print(f"[red]Unknown command: {cmd}[/red]")
                    console.print("[dim]Type /help for available commands[/dim]")
                continue
            
            # Process with agent
            console.print()
            agent.execute_objective(user_input)
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Use 'exit' to quit or Ctrl+C again to force exit[/yellow]")
            continue
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]")
            if agent_config.debug:
                console.print_exception()

@cli.command()
def version():
    """Show version information"""
    console.print(BANNER, style="bold cyan")
    console.print("\n[bold]Version:[/bold] 0.1.0 (POC)")
    console.print("[bold]Author:[/bold] Your Name")
    console.print("[bold]License:[/bold] MIT\n")

@cli.command()
def tools():
    """List available pentesting tools"""
    console.print(BANNER, style="bold cyan")
    console.print("\n[bold cyan]Available Tools:[/bold cyan]\n")
    
    tools_info = [
        ("nmap", "Network discovery and port scanning", "✓"),
        ("netexec", "SMB/WinRM/LDAP enumeration and exploitation", "✓"),
        ("bloodhound", "AD relationship and attack path analysis", "○"),
        ("impacket", "Python classes for network protocols", "○"),
    ]
    
    for tool, desc, status in tools_info:
        status_color = "green" if status == "✓" else "yellow"
        console.print(f"  [{status_color}]{status}[/{status_color}] [bold]{tool}[/bold]: {desc}")
    
    console.print("\n[dim]○ = Planned  ✓ = Available[/dim]\n")

@cli.command()
def install_deps():
    """Install pentesting tool dependencies
    
    Interactive menu to install required tools:
    - nmap: Network scanner
    - netexec: SMB/WinRM/LDAP enumeration
    - impacket: AD exploitation toolkit
    - ldap-utils: LDAP search utilities
    - hashcat: Password cracking
    
    Automatically detects your system and package manager.
    """
    console.print(BANNER, style="bold cyan")
    
    try:
        from installer import run_installer
        run_installer()
    except ImportError as e:
        console.print(f"[red]Error: Could not import installer module: {e}[/red]")
        sys.exit(1)
    except KeyboardInterrupt:
        console.print("\n[yellow]Installation cancelled by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Error during installation: {e}[/red]")
        console.print_exception()
        sys.exit(1)

if __name__ == '__main__':
    cli()
