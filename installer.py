"""
Tool installer for SERPENTER
Handles automatic installation of pentesting dependencies
"""

import subprocess
import shutil
import platform
import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt

console = Console()


class ToolInstaller:
    """Handles installation of pentesting tools"""

    def __init__(self):
        self.os_type = platform.system().lower()
        self.package_manager = self.detect_package_manager()
        self.has_sudo = self.check_sudo()
        
        # Tool definitions: name -> (description, install_method, check_command)
        self.tools = {
            "nmap": (
                "Network scanner for host and port discovery",
                self.install_nmap,
                "nmap"
            ),
            "netexec": (
                "SMB/WinRM/LDAP enumeration tool (formerly CrackMapExec)",
                self.install_netexec,
                "netexec"
            ),
            "impacket": (
                "Python AD exploitation toolkit (secretsdump, GetUserSPNs, etc.)",
                self.install_impacket,
                "secretsdump.py"
            ),
            "ldap-utils": (
                "LDAP utilities including ldapsearch",
                self.install_ldap_utils,
                "ldapsearch"
            ),
            "hashcat": (
                "Password cracking tool",
                self.install_hashcat,
                "hashcat"
            ),
        }

    def detect_package_manager(self) -> Optional[str]:
        """Detect the system package manager"""
        if self.os_type == "linux":
            if shutil.which("apt"):
                return "apt"
            elif shutil.which("dnf"):
                return "dnf"
            elif shutil.which("yum"):
                return "yum"
            elif shutil.which("pacman"):
                return "pacman"
        elif self.os_type == "darwin":
            if shutil.which("brew"):
                return "brew"
        return None

    def check_sudo(self) -> bool:
        """Check if sudo is available"""
        if self.os_type == "windows":
            return False
        
        try:
            result = subprocess.run(
                ["sudo", "-n", "true"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except Exception:
            return False

    def check_tool_installed(self, check_command: str) -> bool:
        """Check if a tool is already installed"""
        return shutil.which(check_command) is not None

    def run_command(self, cmd: List[str], use_sudo: bool = False) -> Tuple[bool, str]:
        """Run a shell command and return success status and output"""
        if use_sudo and self.os_type != "windows":
            cmd = ["sudo"] + cmd
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600  # 10 minute timeout
            )
            return result.returncode == 0, result.stdout + result.stderr
        except subprocess.TimeoutExpired:
            return False, "Command timed out"
        except Exception as e:
            return False, str(e)

    def install_system_package(self, package_name: str, use_sudo: bool = True) -> Tuple[bool, str]:
        """Install a package using the system package manager"""
        if not self.package_manager:
            return False, "No supported package manager found"
        
        console.print(f"[cyan]Installing {package_name} via {self.package_manager}...[/cyan]")
        
        if self.package_manager == "apt":
            # Update package list first
            success, _ = self.run_command(["apt", "update"], use_sudo)
            if not success:
                console.print("[yellow]Warning: apt update failed, continuing anyway[/yellow]")
            
            cmd = ["apt", "install", "-y", package_name]
        elif self.package_manager in ["dnf", "yum"]:
            cmd = [self.package_manager, "install", "-y", package_name]
        elif self.package_manager == "pacman":
            cmd = ["pacman", "-S", "--noconfirm", package_name]
        elif self.package_manager == "brew":
            cmd = ["brew", "install", package_name]
            use_sudo = False  # brew doesn't use sudo
        else:
            return False, f"Unsupported package manager: {self.package_manager}"
        
        return self.run_command(cmd, use_sudo)

    def install_python_tool(self, package_name: str, use_pipx: bool = True) -> Tuple[bool, str]:
        """Install a Python tool using pipx (preferred) or pip"""
        if use_pipx and shutil.which("pipx"):
            console.print(f"[cyan]Installing {package_name} via pipx...[/cyan]")
            return self.run_command(["pipx", "install", package_name], use_sudo=False)
        else:
            console.print(f"[cyan]Installing {package_name} via pip...[/cyan]")
            # Use pip3 with --user to avoid needing sudo
            return self.run_command(["pip3", "install", "--user", package_name], use_sudo=False)

    # Tool-specific installation methods

    def install_nmap(self) -> Tuple[bool, str]:
        """Install nmap"""
        return self.install_system_package("nmap")

    def install_ldap_utils(self) -> Tuple[bool, str]:
        """Install LDAP utilities"""
        if self.package_manager == "brew":
            return self.install_system_package("openldap")
        else:
            return self.install_system_package("ldap-utils")

    def install_hashcat(self) -> Tuple[bool, str]:
        """Install hashcat"""
        return self.install_system_package("hashcat")

    def install_netexec(self) -> Tuple[bool, str]:
        """Install NetExec"""
        console.print("[cyan]Installing NetExec from GitHub...[/cyan]")
        
        # Try pipx first
        if shutil.which("pipx"):
            console.print("[cyan]Attempting installation via pipx...[/cyan]")
            success, output = self.run_command(
                ["pipx", "install", "git+https://github.com/Pennyw0rth/NetExec"],
                use_sudo=False
            )
            if success:
                return True, "NetExec installed via pipx"
        
        # Fallback to pip
        console.print("[cyan]Attempting installation via pip...[/cyan]")
        return self.run_command(
            ["pip3", "install", "--user", "git+https://github.com/Pennyw0rth/NetExec"],
            use_sudo=False
        )

    def install_impacket(self) -> Tuple[bool, str]:
        """Install Impacket"""
        # First ensure pipx is available for better isolation
        if not shutil.which("pipx"):
            console.print("[yellow]pipx not found, installing it first...[/yellow]")
            if self.package_manager == "apt":
                self.install_system_package("pipx")
            else:
                self.run_command(["pip3", "install", "--user", "pipx"], use_sudo=False)
                self.run_command(["pipx", "ensurepath"], use_sudo=False)
        
        return self.install_python_tool("impacket", use_pipx=True)

    def get_tool_status(self) -> Dict[str, bool]:
        """Get installation status of all tools"""
        status = {}
        for tool_name, (_, _, check_cmd) in self.tools.items():
            status[tool_name] = self.check_tool_installed(check_cmd)
        return status

    def show_tool_menu(self) -> List[str]:
        """Display tool selection menu and return selected tools"""
        console.print("\n[bold cyan]🐍 SERPENTER Dependency Installer[/bold cyan]\n")
        
        # Show system info
        console.print(f"[dim]OS: {self.os_type.title()}[/dim]")
        console.print(f"[dim]Package Manager: {self.package_manager or 'None detected'}[/dim]")
        console.print(f"[dim]Sudo Available: {'Yes' if self.has_sudo else 'No'}[/dim]\n")
        
        if not self.has_sudo and self.os_type != "darwin":
            console.print("[yellow]⚠️  Warning: sudo not available. Some installations may fail.[/yellow]")
            console.print("[yellow]   Consider running: sudo -v[/yellow]\n")
        
        # Show tool table
        table = Table(title="Available Tools", show_header=True, header_style="bold cyan")
        table.add_column("#", style="dim", width=3)
        table.add_column("Tool", style="cyan")
        table.add_column("Description")
        table.add_column("Status", justify="center")
        
        status = self.get_tool_status()
        for idx, (tool_name, (description, _, _)) in enumerate(self.tools.items(), 1):
            installed = status[tool_name]
            status_text = "[green]✓ Installed[/green]" if installed else "[yellow]○ Not Installed[/yellow]"
            table.add_row(str(idx), tool_name, description, status_text)
        
        console.print(table)
        console.print()
        
        # Let user select tools
        console.print("[bold]Select tools to install:[/bold]")
        console.print("  Enter numbers separated by commas (e.g., 1,3,5)")
        console.print("  Or type 'all' to install all missing tools")
        console.print("  Or type 'none' to exit\n")
        
        selection = Prompt.ask("[green]Your selection[/green]", default="all")
        
        if selection.lower() == "none":
            return []
        
        if selection.lower() == "all":
            # Return all tools that are not installed
            return [name for name, installed in status.items() if not installed]
        
        # Parse selection
        try:
            indices = [int(x.strip()) for x in selection.split(",")]
            tool_names = list(self.tools.keys())
            selected = []
            for idx in indices:
                if 1 <= idx <= len(tool_names):
                    tool_name = tool_names[idx - 1]
                    if not status[tool_name]:
                        selected.append(tool_name)
                    else:
                        console.print(f"[dim]{tool_name} is already installed, skipping[/dim]")
            return selected
        except ValueError:
            console.print("[red]Invalid selection[/red]")
            return []

    def install_selected_tools(self, tool_names: List[str]) -> Dict[str, bool]:
        """Install selected tools and return results"""
        if not tool_names:
            console.print("[yellow]No tools selected for installation[/yellow]")
            return {}
        
        console.print(f"\n[bold]Installing {len(tool_names)} tool(s)...[/bold]\n")
        
        # Confirm with user
        tool_list = ", ".join(tool_names)
        if not Confirm.ask(f"Install these tools: {tool_list}?", default=True):
            console.print("[yellow]Installation cancelled[/yellow]")
            return {}
        
        # Check sudo if needed
        if not self.has_sudo and self.os_type == "linux":
            console.print("\n[yellow]Some tools may require sudo privileges.[/yellow]")
            console.print("[yellow]You may be prompted for your password.[/yellow]\n")
        
        results = {}
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            for tool_name in tool_names:
                task = progress.add_task(f"Installing {tool_name}...", total=None)
                
                if tool_name not in self.tools:
                    console.print(f"[red]Unknown tool: {tool_name}[/red]")
                    results[tool_name] = False
                    continue
                
                _, install_func, check_cmd = self.tools[tool_name]
                
                try:
                    success, output = install_func()
                    results[tool_name] = success
                    
                    if success:
                        # Verify installation
                        if self.check_tool_installed(check_cmd):
                            progress.update(task, description=f"[green]✓[/green] {tool_name} installed successfully")
                        else:
                            progress.update(task, description=f"[yellow]⚠[/yellow] {tool_name} installed but not in PATH")
                    else:
                        progress.update(task, description=f"[red]✗[/red] {tool_name} installation failed")
                        if output:
                            console.print(f"[dim]Error: {output[:200]}[/dim]")
                except Exception as e:
                    progress.update(task, description=f"[red]✗[/red] {tool_name} installation failed")
                    console.print(f"[red]Error installing {tool_name}: {e}[/red]")
                    results[tool_name] = False
                
                progress.remove_task(task)
        
        return results

    def show_results(self, results: Dict[str, bool]):
        """Display installation results summary"""
        if not results:
            return
        
        console.print("\n[bold cyan]Installation Summary[/bold cyan]\n")
        
        success_count = sum(1 for v in results.values() if v)
        total_count = len(results)
        
        for tool_name, success in results.items():
            status = "[green]✓ Success[/green]" if success else "[red]✗ Failed[/red]"
            console.print(f"  {status} - {tool_name}")
        
        console.print(f"\n[bold]Result: {success_count}/{total_count} tools installed successfully[/bold]\n")
        
        if success_count > 0:
            console.print("[green]✨ Installation complete! You may need to restart your shell or run:[/green]")
            console.print("[dim]   export PATH=$HOME/.local/bin:$PATH[/dim]\n")
        
        if success_count < total_count:
            console.print("[yellow]⚠️  Some tools failed to install. Check the errors above.[/yellow]")
            console.print("[yellow]   You can try installing them manually or run this installer again.[/yellow]\n")


def run_installer():
    """Main installer entry point"""
    installer = ToolInstaller()
    
    # Show menu and get selection
    selected_tools = installer.show_tool_menu()
    
    if not selected_tools:
        console.print("[cyan]No tools to install. Exiting.[/cyan]")
        return
    
    # Install selected tools
    results = installer.install_selected_tools(selected_tools)
    
    # Show results
    installer.show_results(results)


if __name__ == "__main__":
    run_installer()
