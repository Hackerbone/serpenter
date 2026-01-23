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
        interactive_mode(debug)

@cli.command()
@click.argument('objective', nargs=-1)
@click.option('--target', '-t', help='Target subnet or host')
@click.option('--auto', is_flag=True, help='Run in autonomous mode')
@click.option('--debug', is_flag=True, help='Enable debug mode')
def run(objective, target, auto, debug):
    """Execute a pentesting objective
    
    Examples:
        serpenter run "find all SMB shares in 192.168.1.0/24"
        serpenter run -t 10.0.0.0/24 "enumerate domain users"
        serpenter run --auto "get path to domain admin"
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
    
    # Initialize agent
    config = Config(debug=debug, auto_mode=auto)
    agent = SerpenterAgent(config)
    
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

@cli.command()
@click.option('--debug', is_flag=True, help='Enable debug mode')
def interactive(debug):
    """Start interactive mode"""
    console.print(BANNER, style="bold cyan")
    interactive_mode(debug)

def interactive_mode(debug=False):
    """Interactive chat mode with the agent"""
    
    console.print("\n[bold cyan]Interactive Mode[/bold cyan]")
    console.print("[dim]Enter your pentesting objectives naturally. Type 'exit' to quit.[/dim]\n")
    
    config = Config(debug=debug, auto_mode=False)
    agent = SerpenterAgent(config)
    
    while True:
        try:
            # Get user input
            user_input = Prompt.ask("\n[bold green]serpenter>[/bold green]")
            
            if user_input.lower() in ['exit', 'quit', 'q']:
                console.print("\n[cyan]Exiting SERPENTER. Stay stealthy! 🐍[/cyan]")
                break
            
            if not user_input.strip():
                continue
            
            # Process with agent
            console.print()
            agent.execute_objective(user_input)
            
        except KeyboardInterrupt:
            console.print("\n[yellow]Use 'exit' to quit[/yellow]")
            continue
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]")
            if debug:
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

if __name__ == '__main__':
    cli()