"""
Pentesting tool wrappers for SERPENTER
"""

import subprocess
from typing import Optional, List
from langchain.tools import BaseTool
from pydantic import BaseModel, Field


class NmapScanInput(BaseModel):
    """Input for Nmap scan tool"""

    target: str = Field(description="Target IP, subnet (CIDR), or hostname to scan")
    ports: Optional[str] = Field(
        default=None, description="Port specification (e.g., '80,443' or '1-1000')"
    )
    scan_type: Optional[str] = Field(
        default="quick", description="Scan type: 'quick', 'full', 'service', 'vuln'"
    )


class NmapScanTool(BaseTool):
    """Tool for running Nmap network scans"""

    name: str = "nmap_scan"
    description: str = """
    Performs network scanning using Nmap to discover hosts, open ports, and services.
    
    Use this when you need to:
    - Discover live hosts in a subnet
    - Find open ports on a target
    - Identify running services and versions
    - Perform initial reconnaissance
    
    Examples:
    - target="192.168.1.0/24", scan_type="quick" - Quick host discovery
    - target="10.0.0.5", scan_type="service" - Service version detection
    - target="192.168.1.100", ports="445,139,135" - Scan specific ports
    """
    args_schema: type[BaseModel] = NmapScanInput

    def _run(
        self, target: str, ports: Optional[str] = None, scan_type: str = "quick"
    ) -> str:
        """Execute Nmap scan"""

        # Build nmap command based on scan type
        cmd = ["nmap"]

        if scan_type == "quick":
            cmd.extend(["-sn", "-T4"])  # Ping scan, fast
        elif scan_type == "full":
            cmd.extend(["-p-", "-T4", "-A"])  # All ports, OS detection
        elif scan_type == "service":
            cmd.extend(["-sV", "-sC", "-T4"])  # Version detection, default scripts
        elif scan_type == "vuln":
            cmd.extend(["-sV", "--script", "vuln", "-T4"])  # Vulnerability scan
        else:
            cmd.extend(["-sV", "-T4"])  # Default

        # Add port specification if provided
        if ports:
            cmd.extend(["-p", ports])

        cmd.append(target)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            if result.returncode != 0:
                return f"Nmap scan failed: {result.stderr}"

            return self._parse_nmap_output(result.stdout)

        except subprocess.TimeoutExpired:
            return "Nmap scan timed out after 5 minutes"
        except FileNotFoundError:
            return "Nmap not installed. Install with: sudo apt install nmap (Linux) or brew install nmap (macOS)"
        except Exception as e:
            return f"Error running nmap: {str(e)}"

    def _parse_nmap_output(self, output: str) -> str:
        """Parse and format nmap output for the agent"""
        lines = output.split("\n")

        # Extract key information
        results = {"summary": [], "hosts": [], "ports": []}

        current_host = None
        for line in lines:
            line = line.strip()

            # Host up
            if "Nmap scan report for" in line:
                current_host = line.replace("Nmap scan report for ", "")
                results["hosts"].append(current_host)

            # Open ports
            elif "/tcp" in line or "/udp" in line:
                results["ports"].append(f"{current_host}: {line}")

            # Summary line
            elif "hosts up" in line or "done:" in line:
                results["summary"].append(line)

        # Format results
        formatted = []

        if results["summary"]:
            formatted.append("SCAN SUMMARY:")
            formatted.extend(results["summary"])
            formatted.append("")

        if results["hosts"]:
            formatted.append(f"DISCOVERED HOSTS ({len(results['hosts'])}):")
            for host in results["hosts"]:
                formatted.append(f"  • {host}")
            formatted.append("")

        if results["ports"]:
            formatted.append("OPEN PORTS:")
            for port in results["ports"]:
                formatted.append(f"  • {port}")

        return "\n".join(formatted) if formatted else output


class NetExecInput(BaseModel):
    """Input for NetExec enumeration"""

    target: str = Field(description="Target IP, subnet, or hostname")
    protocol: str = Field(
        default="smb",
        description="Protocol: 'smb', 'winrm', 'ldap', 'rdp', 'ssh', 'vnc', 'ftp', 'mssql'",
    )
    action: Optional[str] = Field(
        default=None,
        description="Action: depends on protocol (e.g., 'shares', 'users', 'sessions' for SMB)",
    )
    username: Optional[str] = Field(
        default=None, description="Username for authentication"
    )
    password: Optional[str] = Field(
        default=None, description="Password for authentication"
    )


class NetExecTool(BaseTool):
    """Generic tool for network enumeration using NetExec (previously CrackMapExec)"""

    name: str = "netexec"
    description: str = """
    Enumerate network services using NetExec across multiple protocols.
    
    Use this when you need to:
    - List SMB shares on a target or subnet (protocol='smb', action='shares')
    - Enumerate domain users (protocol='smb', action='users')
    - Test WinRM access (protocol='winrm')
    - Query LDAP services (protocol='ldap', action='users' or 'groups')
    - Check RDP access (protocol='rdp')
    - Test SSH access (protocol='ssh')
    
    Supported protocols: smb, winrm, ldap, rdp, ssh, vnc, ftp, mssql
    
    Examples:
    - target="192.168.1.0/24", protocol="smb", action="shares" - Find all SMB shares in subnet
    - target="10.0.0.5", protocol="smb", action="users" - Enumerate SMB users
    - target="10.0.0.10", protocol="winrm" - Test WinRM access
    - target="192.168.1.100", protocol="ldap", action="users" - LDAP user enumeration
    """
    args_schema: type[BaseModel] = NetExecInput

    def _run(
        self,
        target: str,
        protocol: str = "smb",
        action: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> str:
        """Execute NetExec enumeration"""

        # Validate protocol
        valid_protocols = ["smb", "winrm", "ldap", "rdp", "ssh", "vnc", "ftp", "mssql"]
        if protocol not in valid_protocols:
            return f"Invalid protocol '{protocol}'. Valid options: {', '.join(valid_protocols)}"

        # Build netexec command
        cmd = ["netexec", protocol, target]

        # Add authentication if provided
        if username:
            cmd.extend(["-u", username])
            if password:
                cmd.extend(["-p", password])
            else:
                cmd.extend(["-p", ""])  # Try null session
        else:
            # Try anonymous/null session for protocols that support it
            if protocol in ["smb", "ldap"]:
                cmd.extend(["-u", "", "-p", ""])

        # Add action-specific flags based on protocol
        if action:
            action_flag = self._get_action_flag(protocol, action)
            if action_flag:
                cmd.append(action_flag)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=180,  # 3 minute timeout
            )

            # NetExec returns output even with non-zero exit codes
            output = result.stdout + result.stderr

            if not output.strip():
                return f"No {protocol.upper()} services found or access denied"

            return self._parse_netexec_output(output, protocol, action)

        except subprocess.TimeoutExpired:
            return "NetExec scan timed out after 3 minutes"
        except FileNotFoundError:
            return "NetExec not installed. Install with: pipx install netexec"
        except Exception as e:
            return f"Error running netexec: {str(e)}"

    def _get_action_flag(self, protocol: str, action: str) -> Optional[str]:
        """Get the appropriate flag for the action based on protocol"""
        action_map = {
            "smb": {
                "shares": "--shares",
                "users": "--users",
                "sessions": "--sessions",
                "disks": "--disks",
                "groups": "--groups",
                "pass-pol": "--pass-pol",
                "rid-brute": "--rid-brute",
            },
            "ldap": {
                "users": "--users",
                "groups": "--groups",
                "computers": "--computers",
            },
            "winrm": {
                "users": "--users",
            },
        }

        protocol_actions = action_map.get(protocol, {})
        return protocol_actions.get(action)

    def _parse_netexec_output(
        self, output: str, protocol: str, action: Optional[str]
    ) -> str:
        """Parse and format NetExec output"""
        lines = output.split("\n")

        results = {"hosts": [], "shares": [], "users": [], "groups": [], "errors": []}

        for line in lines:
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Detect hosts (protocol-specific port detection)
            if any(x in line for x in ["445", "5985", "389", "3389", "22"]):
                results["hosts"].append(line)

            # Detect shares (SMB)
            if "READ" in line or "WRITE" in line:
                results["shares"].append(line)

            # Detect users
            if "User:" in line or "UserName:" in line or "\\User" in line:
                results["users"].append(line)

            # Detect groups
            if "Group:" in line or "GroupName:" in line:
                results["groups"].append(line)

            # Detect errors
            if "ERROR" in line or "DENIED" in line or "STATUS_" in line:
                results["errors"].append(line)

        # Format output
        formatted = []
        formatted.append(f"{protocol.upper()} ENUMERATION RESULTS:")
        formatted.append("")

        if results["hosts"]:
            formatted.append(f"HOSTS FOUND ({len(results['hosts'])}):")
            for host in results["hosts"][:10]:  # Limit to 10
                formatted.append(f"  • {host}")
            if len(results["hosts"]) > 10:
                formatted.append(f"  ... and {len(results['hosts']) - 10} more")
            formatted.append("")

        if results["shares"]:
            formatted.append(f"ACCESSIBLE SHARES ({len(results['shares'])}):")
            for share in results["shares"][:20]:  # Limit to 20
                formatted.append(f"  • {share}")
            if len(results["shares"]) > 20:
                formatted.append(f"  ... and {len(results['shares']) - 20} more")
            formatted.append("")

        if results["users"]:
            formatted.append(f"USERS ENUMERATED ({len(results['users'])}):")
            for user in results["users"][:15]:
                formatted.append(f"  • {user}")
            formatted.append("")

        if results["groups"]:
            formatted.append(f"GROUPS ENUMERATED ({len(results['groups'])}):")
            for group in results["groups"][:15]:
                formatted.append(f"  • {group}")

        if not any([results["hosts"], results["shares"], results["users"], results["groups"]]):
            # Return raw output if we couldn't parse anything useful
            return output[:1000]  # Limit to 1000 chars

        return "\n".join(formatted)


class BashExecutionInput(BaseModel):
    """Input for bash command execution"""

    command: str = Field(description="Bash command to execute")
    reason: str = Field(description="Explanation of why this command is needed")


class BashExecutionTool(BaseTool):
    """Tool for executing bash commands (use with caution)"""

    name: str = "bash_execute"
    description: str = """
    Execute bash commands for tasks not covered by specialized tools.
    
    Use this ONLY when:
    - You need to parse/filter output from other tools
    - You need to check if a tool is installed
    - You need to perform file operations
    
    DO NOT use for:
    - Network scanning (use nmap_scan instead)
    - SMB enumeration (use netexec_smb instead)
    
    Always provide a clear 'reason' for why the command is needed.
    """
    args_schema: type[BaseModel] = BashExecutionInput

    def _run(self, command: str, reason: str) -> str:
        """Execute bash command"""

        # Safety check - block dangerous commands
        dangerous = ["rm -rf", "dd if=", "mkfs", ":(){:|:&};:", "fork"]
        if any(d in command.lower() for d in dangerous):
            return f"BLOCKED: Command appears dangerous. Reason given: {reason}"

        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=60
            )

            output = result.stdout + result.stderr
            return f"[Command: {command}]\n[Reason: {reason}]\n\nOutput:\n{output}"

        except subprocess.TimeoutExpired:
            return "Command timed out after 60 seconds"
        except Exception as e:
            return f"Error executing command: {str(e)}"


# Tool registry
AVAILABLE_TOOLS = {
    "nmap": NmapScanTool(),
    "netexec": NetExecTool(),
    "bash": BashExecutionTool(),
}


def get_tools(tool_names: List[str]) -> List[BaseTool]:
    """Get tool instances by name"""
    return [AVAILABLE_TOOLS[name] for name in tool_names if name in AVAILABLE_TOOLS]
