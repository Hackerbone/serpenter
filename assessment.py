"""
SERPENTER internal assessment runner.

This is intentionally not a clone of Bugbase's entity/submodule queue. It keeps
the output shape similar while using Serpenter's AI-first, tool-native runtime.
"""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from langchain_core.messages import HumanMessage, SystemMessage
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from config import Config
from tools import get_tools


console = Console()


COMMON_INTERNAL_PORTS = "21,22,53,88,135,139,389,445,464,593,636,1433,3306,3389,5985,5986,9389"
PUBLIC_LAB_CREDENTIAL_CANDIDATES = [
    # Intentionally empty. Serpenter must not carry lab-specific default
    # credentials; credentials must come from user input or collected evidence.
]


@dataclass
class Evidence:
    phase: str
    tool: str
    objective: str
    status: str
    output: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Entity:
    entity_type: str
    identifier: str
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Finding:
    vuln_name: str
    vuln_type: str
    severity: str
    target: str
    description: str
    evidence_refs: List[int] = field(default_factory=list)
    remediation: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AttackPath:
    name: str
    severity: str
    nodes: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    finding_index: Optional[int] = None


@dataclass
class CredentialCandidate:
    username: str
    password: str
    domain: Optional[str] = None
    source_evidence: Optional[int] = None
    source: str = "evidence"


@dataclass
class AssessmentReport:
    target: str
    started_at: str
    completed_at: str = ""
    mode: str = "ai_native_internal_assessment"
    status: str = "running"
    entities: List[Entity] = field(default_factory=list)
    findings: List[Finding] = field(default_factory=list)
    attack_paths: List[AttackPath] = field(default_factory=list)
    evidence: List[Evidence] = field(default_factory=list)
    ai_summary: str = ""
    next_steps: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class InternalAssessmentRunner:
    """Full-scale internal assessment flow using Serpenter's tool wrappers."""

    def __init__(self, config: Config):
        self.config = config
        self.console = Console()
        self.tools = {tool.name: tool for tool in get_tools(config.tools_enabled, config)}
        self.llm = None

    def run(
        self,
        target: str,
        *,
        domain: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        hashes: Optional[str] = None,
        dc_ip: Optional[str] = None,
        base_dn: Optional[str] = None,
        allow_exploits: bool = False,
        rce_target: Optional[str] = None,
        rce_command: str = "whoami",
        local_auth: bool = False,
        output_path: Optional[Path] = None,
    ) -> AssessmentReport:
        started_at = datetime.now(timezone.utc).isoformat()
        report = AssessmentReport(target=target, started_at=started_at)
        self._ensure_ai_ready()

        self.console.print(
            Panel(
                f"[bold]{target}[/bold]\n"
                f"Domain: [cyan]{domain or 'auto/unknown'}[/cyan]\n"
                f"Exploit validation: [{'yellow' if allow_exploits else 'green'}]"
                f"{'enabled' if allow_exploits else 'disabled'}[/]",
                title="Internal Assessment",
                border_style="green",
            )
        )

        resolved_dc = dc_ip or target
        resolved_base_dn = base_dn or self._domain_to_base_dn(domain)

        self._phase_discovery(report, target)
        self._phase_service_enumeration(report, target, username, password)
        self._phase_identity_and_ad(
            report,
            target=target,
            domain=domain,
            username=username,
            password=password,
            hashes=hashes,
            dc_ip=resolved_dc,
            base_dn=resolved_base_dn,
        )
        self._phase_attack_surface(
            report,
            domain=domain,
            username=username,
            password=password,
            hashes=hashes,
            dc_ip=resolved_dc,
            allow_exploits=allow_exploits,
            rce_target=rce_target,
            rce_command=rce_command,
            local_auth=local_auth,
        )

        self._derive_entities_and_findings(report)
        self._derive_ai_findings(report)
        self._build_attack_paths(report)
        self._synthesize_with_ai(report)

        report.completed_at = datetime.now(timezone.utc).isoformat()
        report.status = "completed"
        if output_path or self.config.save_results:
            self._write_report(report, output_path)
        self._print_report_summary(report)
        return report

    def _phase_discovery(self, report: AssessmentReport, target: str) -> None:
        self._record_tool(
            report,
            phase="discovery",
            tool_name="nmap_scan",
            objective="Discover live hosts",
            kwargs={"target": target, "scan_type": "quick"},
        )
        self._record_tool(
            report,
            phase="discovery",
            tool_name="nmap_scan",
            objective="Identify common internal services",
            kwargs={"target": target, "ports": COMMON_INTERNAL_PORTS, "scan_type": "service"},
        )

    def _phase_service_enumeration(
        self,
        report: AssessmentReport,
        target: str,
        username: Optional[str],
        password: Optional[str],
    ) -> None:
        for action in ("users", "shares", "pass-pol"):
            self._record_tool(
                report,
                phase="service_enumeration",
                tool_name="netexec",
                objective=f"Enumerate SMB {action}",
                kwargs={
                    "target": target,
                    "protocol": "smb",
                    "action": action,
                    "username": username,
                    "password": password,
                },
            )

        self._record_tool(
            report,
            phase="service_enumeration",
            tool_name="netexec",
            objective="Enumerate LDAP computers",
            kwargs={
                "target": target,
                "protocol": "ldap",
                "action": "computers",
                "username": username,
                "password": password,
            },
        )

    def _phase_identity_and_ad(
        self,
        report: AssessmentReport,
        *,
        target: str,
        domain: Optional[str],
        username: Optional[str],
        password: Optional[str],
        hashes: Optional[str],
        dc_ip: str,
        base_dn: Optional[str],
    ) -> None:
        if not base_dn:
            report.next_steps.append("Provide --domain or --base-dn to enable LDAP AD object queries.")
            return

        for query_type in ("users", "groups", "admins", "spns", "asrep", "trusts"):
            self._record_tool(
                report,
                phase="identity_and_ad",
                tool_name="ldapsearch",
                objective=f"LDAP query: {query_type}",
                kwargs={
                    "target": dc_ip or target,
                    "base_dn": base_dn,
                    "query_type": query_type,
                    "username": self._ldap_bind_user(domain, username),
                    "password": password,
                },
            )

        if username and (password or hashes):
            self._record_tool(
                report,
                phase="identity_and_ad",
                tool_name="impacket",
                objective="Enumerate Kerberoastable SPNs without requesting tickets",
                kwargs={
                    "script": "GetUserSPNs",
                    "target": dc_ip or target,
                    "domain": domain,
                    "username": username,
                    "password": password,
                    "hashes": hashes,
                    "dc_ip": dc_ip,
                },
            )

    def _phase_attack_surface(
        self,
        report: AssessmentReport,
        *,
        domain: Optional[str],
        username: Optional[str],
        password: Optional[str],
        hashes: Optional[str],
        dc_ip: str,
        allow_exploits: bool,
        rce_target: Optional[str],
        rce_command: str,
        local_auth: bool,
    ) -> None:
        if username and password and domain:
            self._record_tool(
                report,
                phase="adcs",
                tool_name="certipy",
                objective="Enumerate AD CS templates and vulnerable certificate paths",
                kwargs={
                    "action": "find",
                    "target": dc_ip,
                    "username": username,
                    "password": password,
                    "domain": domain,
                    "dc_ip": dc_ip,
                    "extra_args": "-vulnerable -stdout",
                },
            )

        if not allow_exploits:
            report.next_steps.append(
                "Run again with --allow-exploits to actively request roastable tickets or perform exploit validation."
            )
            return

        if username and password and rce_target:
            self._record_tool(
                report,
                phase="rce_validation",
                tool_name="netexec",
                objective=f"Validate command execution on {rce_target}",
                kwargs={
                    "target": rce_target,
                    "protocol": "smb",
                    "username": username,
                    "password": password,
                    "local_auth": local_auth,
                    "execute_command": rce_command or "whoami",
                },
            )
        elif username and password:
            report.next_steps.append(
                "Pass --rce-target with --allow-exploits to run non-destructive RCE validation."
            )
        else:
            self._phase_discovered_secret_reuse(report, report.target, rce_command or "whoami")

        if username and (password or hashes) and domain:
            self._record_tool(
                report,
                phase="exploit_validation",
                tool_name="impacket",
                objective="Request Kerberoast tickets for validated cracking workflow",
                kwargs={
                    "script": "GetUserSPNs",
                    "target": dc_ip,
                    "domain": domain,
                    "username": username,
                    "password": password,
                    "hashes": hashes,
                    "dc_ip": dc_ip,
                    "extra_args": "-request -outputfile serpenter_kerberoast.txt",
                },
            )

    def _extract_dc_candidates(self, report: AssessmentReport) -> List[str]:
        candidates = []
        dc_ports = {"88", "389", "636", "9389"}
        dc_services = {"kerberos-sec", "ldap", "ldapssl", "adws"}
        for evidence in report.evidence:
            for port, service, host in self._extract_services(evidence.output):
                if host and (port in dc_ports or service in dc_services):
                    if host not in candidates:
                        candidates.append(host)
        return candidates

    @staticmethod
    def _rank_dc_targets(discovered: List[str], hints: List[str]) -> List[str]:
        ranked = []
        for hint in hints:
            if hint not in ranked:
                ranked.append(hint)
        for item in discovered:
            if item not in ranked:
                ranked.append(item)
        return ranked[:3]

    def _phase_discovered_secret_reuse(
        self,
        report: AssessmentReport,
        target: str,
        rce_command: str,
    ) -> None:
        credentials = self._extract_credential_candidates(report)
        if not credentials:
            report.next_steps.append(
                "No credentials were supplied or discovered, so Serpenter did not attempt credentialed RCE or ADCS validation."
            )
            return

        dc_by_domain = self._extract_domain_dc_map(report)
        any_rce = False
        for credential in credentials:
            smb_username = self._format_domain_username(credential)
            audit = self._record_tool(
                report,
                phase="credential_validation",
                tool_name="netexec",
                objective=f"Validate discovered credential {smb_username} across SMB",
                kwargs={
                    "target": target,
                    "protocol": "smb",
                    "username": smb_username,
                    "password": credential.password,
                },
            )
            pwned_hosts = self._extract_pwned_hosts(audit.output)
            if pwned_hosts:
                self._record_tool(
                    report,
                    phase="rce_validation",
                    tool_name="netexec",
                    objective=f"Validate command execution on {pwned_hosts[0]} using discovered credential",
                    kwargs={
                        "target": pwned_hosts[0],
                        "protocol": "smb",
                        "username": smb_username,
                        "password": credential.password,
                        "execute_command": rce_command,
                    },
                )
                any_rce = True

            if credential.domain:
                self._record_tool(
                    report,
                    phase="credential_validation",
                    tool_name="netexec",
                    objective=f"Validate discovered credential {smb_username} against LDAP",
                    kwargs={
                        "target": target,
                        "protocol": "ldap",
                        "username": smb_username,
                        "password": credential.password,
                    },
                )

                for dc_ip in self._rank_dc_targets(dc_by_domain.get(credential.domain.lower(), []), []):
                    self._record_tool(
                        report,
                        phase="adcs",
                        tool_name="certipy",
                        objective=f"Enumerate AD CS using discovered credential {credential.username}@{credential.domain} on {dc_ip}",
                        kwargs={
                            "action": "find",
                            "target": dc_ip,
                            "username": credential.username,
                            "password": credential.password,
                            "domain": credential.domain,
                            "dc_ip": dc_ip,
                            "extra_args": "-vulnerable -stdout",
                        },
                    )

        if not any_rce:
            report.next_steps.append(
                "Discovered credentials were replayed, but none produced administrative access for RCE validation."
            )

    def _extract_credential_candidates(self, report: AssessmentReport) -> List[CredentialCandidate]:
        candidates = []
        seen = set()
        host_domains = self._extract_host_domain_map(report)
        for index, evidence in enumerate(report.evidence):
            for line in evidence.output.splitlines():
                password_match = re.search(
                    r"SMB\s+((?:\d{1,3}\.){3}\d{1,3})\s+\d+\s+\S+\s+"
                    r"(?P<username>[A-Za-z0-9_.@$-]+)\s+"
                    r"\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\s+\d+\s+.*?"
                    r"Password\s*:\s*(?P<password>[^)\s]+)",
                    line,
                    flags=re.IGNORECASE,
                )
                if not password_match:
                    continue
                host = password_match.group(1)
                username = password_match.group("username")
                password = password_match.group("password").strip()
                domain = host_domains.get(host)
                key = (domain or "", username.lower(), password)
                if key in seen:
                    continue
                seen.add(key)
                candidates.append(
                    CredentialCandidate(
                        username=username,
                        password=password,
                        domain=domain,
                        source_evidence=index,
                        source="smb_user_description",
                    )
                )
        return candidates

    @staticmethod
    def _format_domain_username(credential: CredentialCandidate) -> str:
        if credential.domain:
            return f"{credential.domain}\\{credential.username}"
        return credential.username

    def _extract_host_domain_map(self, report: AssessmentReport) -> Dict[str, str]:
        host_domains = {}
        for evidence in report.evidence:
            for line in evidence.output.splitlines():
                match = re.search(
                    r"\b((?:\d{1,3}\.){3}\d{1,3})\b.*?\(name:[^)]+?\)\s+\(domain:([^)]+)\)",
                    line,
                    flags=re.IGNORECASE,
                )
                if match:
                    host_domains[match.group(1)] = match.group(2)
        return host_domains

    def _extract_domain_dc_map(self, report: AssessmentReport) -> Dict[str, List[str]]:
        host_domains = self._extract_host_domain_map(report)
        dc_hosts = set(self._extract_dc_candidates(report))
        mapping: Dict[str, List[str]] = {}
        for host, domain in host_domains.items():
            if host in dc_hosts:
                mapping.setdefault(domain.lower(), []).append(host)
        return mapping

    def _record_tool(
        self,
        report: AssessmentReport,
        *,
        phase: str,
        tool_name: str,
        objective: str,
        kwargs: Dict[str, Any],
    ) -> Evidence:
        tool = self.tools.get(tool_name)
        if not tool:
            evidence = Evidence(
                phase=phase,
                tool=tool_name,
                objective=objective,
                status="skipped",
                output=f"Tool '{tool_name}' is not enabled in config.",
            )
            report.evidence.append(evidence)
            return evidence

        self.console.print(f"[dim]Running {phase}: {objective}[/dim]")
        try:
            cleaned_kwargs = {key: value for key, value in kwargs.items() if value is not None}
            output = tool._run(**cleaned_kwargs)
            output = self._redact_output(str(output), cleaned_kwargs)
            status = "ok"
            if self._looks_like_tool_failure(output):
                status = "failed"
        except Exception as exc:
            output = f"{type(exc).__name__}: {exc}"
            status = "failed"

        evidence = Evidence(
            phase=phase,
            tool=tool_name,
            objective=objective,
            status=status,
            output=str(output),
            metadata={"args": self._redact(cleaned_kwargs if "cleaned_kwargs" in locals() else kwargs)},
        )
        report.evidence.append(evidence)
        return evidence

    def _derive_entities_and_findings(self, report: AssessmentReport) -> None:
        seen_entities = set()
        seen_findings = set()

        def add_entity(entity_type: str, identifier: str, **properties: Any) -> None:
            key = (entity_type, identifier)
            if identifier and key not in seen_entities:
                seen_entities.add(key)
                report.entities.append(Entity(entity_type, identifier, properties))

        def add_finding(
            name: str,
            vuln_type: str,
            severity: str,
            target: str,
            description: str,
            evidence_index: int,
            remediation: str,
            **metadata: Any,
        ) -> None:
            key = (vuln_type, target, name)
            if target and key not in seen_findings:
                seen_findings.add(key)
                report.findings.append(
                    Finding(
                        vuln_name=name,
                        vuln_type=vuln_type,
                        severity=severity,
                        target=target,
                        description=description,
                        evidence_refs=[evidence_index],
                        remediation=remediation,
                        metadata=metadata,
                    )
                )

        for idx, evidence in enumerate(report.evidence):
            output = evidence.output
            for host in self._extract_hosts(output):
                add_entity("Host", host, source_phase=evidence.phase)

            for port, service, host in self._extract_services(output):
                identifier = f"{host or report.target}:{port}/{service}"
                add_entity("Service", identifier, host=host or report.target, port=port, service=service)

            if "ACCESSIBLE SHARES" in output or re.search(r"\bREAD\b|\bWRITE\b", output):
                target = self._target_from_command(output) or report.target
                add_finding(
                    "Accessible SMB share discovered",
                    "SMB_SHARE_EXPOSURE",
                    "medium",
                    target,
                    "SMB share enumeration returned readable or writable shares.",
                    idx,
                    "Restrict share permissions, remove broad read/write grants, and audit sensitive files.",
                )

            if "Pwn3d!" in output or "[ADMIN]" in output:
                target = self._target_from_command(output) or report.target
                add_finding(
                    "Administrative network access validated",
                    "PRIVILEGED_AUTH",
                    "high",
                    target,
                    "The supplied credential appears to have administrative access on at least one service.",
                    idx,
                    "Rotate the credential if unexpected, reduce local admin reach, and enforce tiered administration.",
                )

            if evidence.status == "ok" and ("Executed command" in output or "Pwn3d!" in output) and evidence.phase == "rce_validation":
                target = self._target_from_command(output) or report.target
                add_finding(
                    "Remote command execution validated",
                    "RCE_VALIDATED",
                    "critical",
                    target,
                    "A non-destructive command execution check completed on the target.",
                    idx,
                    "Remove unnecessary local administrator rights, restrict remote management, and rotate exposed credentials.",
                    command=self._redact(evidence.metadata.get("args", {})).get("execute_command", "whoami"),
                )

            if "$krb5tgs$" in output or "SERVICE PRINCIPAL NAMES" in output:
                target = self._target_from_command(output) or report.target
                add_finding(
                    "Kerberoastable service account exposure",
                    "KERBEROASTING",
                    "high",
                    target,
                    "Service principal names were found and may allow offline password cracking.",
                    idx,
                    "Use long random service account passwords or gMSA, and monitor TGS request anomalies.",
                )

            if "$krb5asrep$" in output or "DONT_REQUIRE_PREAUTH" in output:
                target = self._target_from_command(output) or report.target
                add_finding(
                    "AS-REP roastable user exposure",
                    "ASREP_ROAST",
                    "high",
                    target,
                    "One or more accounts appear to have Kerberos pre-authentication disabled.",
                    idx,
                    "Enable Kerberos pre-authentication and rotate affected account passwords.",
                )

            if "ESC" in output and "Certipy" in output or "Vulnerabilities" in output and "Certificate" in output:
                target = self._target_from_command(output) or report.target
                add_finding(
                    "Potential AD CS certificate abuse path",
                    "ADCS_MISCONFIGURATION",
                    "critical",
                    target,
                    "Certificate Services enumeration indicated potentially vulnerable template or CA settings.",
                    idx,
                    "Review template enrollment rights, EKUs, manager approval, SAN supply, and CA web enrollment exposure.",
                )

            if "Anonymous" in output or "null session" in output.lower():
                target = self._target_from_command(output) or report.target
                add_finding(
                    "Anonymous or null-session exposure",
                    "ANONYMOUS_ACCESS",
                    "medium",
                    target,
                    "Enumeration output indicates possible anonymous access.",
                    idx,
                    "Disable anonymous enumeration and verify SMB/LDAP null-session restrictions.",
                )

    def _build_attack_paths(self, report: AssessmentReport) -> None:
        for index, finding in enumerate(report.findings):
            entry = {"label": "Target", "id": report.target, "properties": {"scope": report.target}}
            vuln = {
                "label": "Vulnerability",
                "id": f"finding-{index + 1}",
                "properties": {
                    "vuln_name": finding.vuln_name,
                    "vuln_type": finding.vuln_type,
                    "severity": finding.severity,
                    "target": finding.target,
                },
            }
            evidence_nodes = [
                {
                    "label": "Evidence",
                    "id": f"evidence-{ref}",
                    "properties": {
                        "phase": report.evidence[ref].phase,
                        "tool": report.evidence[ref].tool,
                        "objective": report.evidence[ref].objective,
                    },
                }
                for ref in finding.evidence_refs
                if 0 <= ref < len(report.evidence)
            ]
            nodes = [entry] + evidence_nodes + [vuln]
            relationships = []
            previous = entry["id"]
            for node in evidence_nodes:
                relationships.append({"source": previous, "target": node["id"], "type": "OBSERVED_BY"})
                previous = node["id"]
            relationships.append({"source": previous, "target": vuln["id"], "type": finding.vuln_type})
            report.attack_paths.append(
                AttackPath(
                    name=finding.vuln_name,
                    severity=finding.severity,
                    nodes=nodes,
                    relationships=relationships,
                    finding_index=index,
                )
            )

    def _derive_ai_findings(self, report: AssessmentReport) -> None:
        if not getattr(self.config, "assessment_ai_synthesis", True):
            return

        try:
            llm = self.llm or self.config.get_llm()
            evidence_payload = [
                {
                    "index": index,
                    "phase": item.phase,
                    "tool": item.tool,
                    "objective": item.objective,
                    "status": item.status,
                    "output": item.output[:3000],
                }
                for index, item in enumerate(report.evidence)
            ]
            existing_findings = [asdict(item) for item in report.findings]
            response = llm.invoke(
                [
                    SystemMessage(
                        content=(
                            "You are SERPENTER's AD security assessment brain. "
                            "Operate like an entity-driven internal assessment orchestrator. "
                            "Extract only vulnerabilities that are directly supported by the provided tool evidence. "
                            "Do not use prior knowledge of public labs, CTFs, GOAD, default passwords, or common demo credentials. "
                            "Do not infer or invent credentials. Credentials are valid evidence only if present in tool output "
                            "or supplied as explicit run input. "
                            "When tool evidence contains a secret, credential, hash, key, or ticket, identify it as reusable evidence "
                            "and evaluate whether it was reused across hosts, services, and techniques. "
                            "Reason by entity type: subnets reveal hosts; hosts reveal services; services reveal users/secrets/misconfigs; "
                            "secrets unlock authenticated SMB/LDAP/WinRM/RDP/MSSQL/FTP/SSH/ADCS checks; valid credentials unlock deeper "
                            "domain, share, Kerberos, delegation, trust, password policy, and certificate-template enumeration. "
                            "Treat non-admin valid credentials as useful, not low value: they can expose ADCS ESC paths, Kerberoastable SPNs, "
                            "AS-REP roastable users, share data, password policy, and trust/delegation issues. "
                            "When validation evidence shows a secret was replayed successfully, create findings for both the credential exposure "
                            "and the downstream misconfiguration it enabled. "
                            "Pay special attention to Active Directory Certificate Services evidence from Certipy, "
                            "including ESC template issues, vulnerable CA settings, enrollment agent abuse, "
                            "SAN supply, weak EKUs, and NTLM relay exposure. "
                            "Return strict JSON only. Do not include markdown."
                        )
                    ),
                    HumanMessage(
                        content=json.dumps(
                            {
                                "target": report.target,
                                "evidence": evidence_payload,
                                "existing_findings": existing_findings,
                                "schema": {
                                    "findings": [
                                        {
                                            "vuln_name": "short title",
                                            "vuln_type": "stable uppercase type",
                                            "severity": "critical|high|medium|low|informational",
                                            "target": "host/ip/subnet",
                                            "description": "what was proven",
                                            "evidence_refs": [0],
                                            "remediation": "specific remediation",
                                            "confidence": "high|medium|low",
                                        }
                                    ]
                                },
                            },
                            indent=2,
                        )
                    ),
                ]
            )
            parsed = self._load_json_object(str(response.content))
            if not isinstance(parsed, dict):
                return
            ai_findings = parsed.get("findings")
            if not isinstance(ai_findings, list):
                return

            existing_keys = {
                (item.vuln_type, item.target, item.vuln_name)
                for item in report.findings
            }
            for raw in ai_findings:
                if not isinstance(raw, dict):
                    continue
                vuln_name = str(raw.get("vuln_name") or "").strip()
                vuln_type = str(raw.get("vuln_type") or "").strip().upper()
                severity = str(raw.get("severity") or "informational").strip().lower()
                target = str(raw.get("target") or report.target).strip()
                description = str(raw.get("description") or "").strip()
                remediation = str(raw.get("remediation") or "").strip()
                evidence_refs = [
                    ref for ref in raw.get("evidence_refs", [])
                    if isinstance(ref, int) and 0 <= ref < len(report.evidence)
                ]
                if not vuln_name or not vuln_type or not description or not evidence_refs:
                    continue
                if severity not in {"critical", "high", "medium", "low", "informational"}:
                    severity = "informational"

                key = (vuln_type, target, vuln_name)
                if key in existing_keys:
                    continue
                existing_keys.add(key)
                report.findings.append(
                    Finding(
                        vuln_name=vuln_name,
                        vuln_type=vuln_type,
                        severity=severity,
                        target=target,
                        description=description,
                        evidence_refs=evidence_refs,
                        remediation=remediation,
                        metadata={
                            "source": "ai_evidence_extraction",
                            "confidence": raw.get("confidence", "medium"),
                        },
                    )
                )
        except Exception as exc:
            if getattr(self.config, "assessment_require_ai", True):
                raise RuntimeError(f"AI evidence extraction failed: {exc}") from exc
            report.next_steps.append(f"AI evidence extraction unavailable: {exc}")

    def _synthesize_with_ai(self, report: AssessmentReport) -> None:
        if not getattr(self.config, "assessment_ai_synthesis", True):
            report.ai_summary = self._fallback_summary(report)
            return

        try:
            llm = self.llm or self.config.get_llm()
            evidence_preview = [
                {
                    "phase": item.phase,
                    "tool": item.tool,
                    "objective": item.objective,
                    "status": item.status,
                    "output": item.output[:1800],
                }
                for item in report.evidence[-12:]
            ]
            prompt = {
                "target": report.target,
                "entities": [asdict(item) for item in report.entities[:80]],
                "findings": [asdict(item) for item in report.findings],
                "evidence_preview": evidence_preview,
            }
            response = llm.invoke(
                [
                    SystemMessage(
                        content=(
                            "You are SERPENTER's internal assessment analyst. "
                            "Summarize impact, confidence, and prioritized next steps. "
                            "Do not use prior knowledge of public labs, GOAD, default passwords, or unstated credentials. "
                            "Explain the entity chain: which host/service/user/secret led to each follow-on check, and which validation succeeded or failed. "
                            "When a discovered secret was reused, explain where it came from, where it worked, where it failed, and what new techniques it unlocked. "
                            "Call out AD CS / Certipy evidence explicitly when present. "
                            "Do not invent findings that are not supported by evidence."
                        )
                    ),
                    HumanMessage(content=json.dumps(prompt, indent=2)),
                ]
            )
            report.ai_summary = str(response.content)
        except Exception as exc:
            if getattr(self.config, "assessment_require_ai", True):
                raise RuntimeError(f"AI synthesis failed: {exc}") from exc
            report.ai_summary = f"{self._fallback_summary(report)}\n\nAI synthesis unavailable: {exc}"

    def _ensure_ai_ready(self) -> None:
        if not getattr(self.config, "assessment_ai_synthesis", True):
            return
        try:
            self.llm = self.config.get_llm()
        except Exception as exc:
            if getattr(self.config, "assessment_require_ai", True):
                raise RuntimeError(
                    "AI is enabled but the configured LLM is unavailable. "
                    "Set the provider API key in this shell, configure assessment.ai_synthesis=false, "
                    "or run with --no-ai for offline smoke tests."
                ) from exc
            self.console.print(f"[yellow]AI unavailable, using deterministic fallback: {exc}[/yellow]")

    @staticmethod
    def _load_json_object(content: str) -> Optional[Dict[str, Any]]:
        text = content.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
            text = re.sub(r"\s*```$", "", text)
        try:
            loaded = json.loads(text)
            return loaded if isinstance(loaded, dict) else None
        except json.JSONDecodeError:
            match = re.search(r"\{.*\}", text, flags=re.DOTALL)
            if not match:
                return None
            try:
                loaded = json.loads(match.group(0))
                return loaded if isinstance(loaded, dict) else None
            except json.JSONDecodeError:
                return None


    def _write_report(self, report: AssessmentReport, output_path: Optional[Path]) -> None:
        path = output_path
        if path is None:
            self.config.results_dir.mkdir(parents=True, exist_ok=True)
            stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
            safe_target = re.sub(r"[^A-Za-z0-9_.-]+", "_", report.target)
            path = self.config.results_dir / f"serpenter_internal_{safe_target}_{stamp}.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
        self.console.print(f"[green]Report written:[/green] {path}")

    def _print_report_summary(self, report: AssessmentReport) -> None:
        table = Table(title="Internal Assessment Summary")
        table.add_column("Metric")
        table.add_column("Count", justify="right")
        table.add_row("Entities", str(len(report.entities)))
        table.add_row("Findings", str(len(report.findings)))
        table.add_row("Attack paths", str(len(report.attack_paths)))
        table.add_row("Evidence items", str(len(report.evidence)))
        self.console.print(table)
        if report.ai_summary:
            self.console.print(Panel(report.ai_summary, title="AI Summary", border_style="cyan"))

    @staticmethod
    def _domain_to_base_dn(domain: Optional[str]) -> Optional[str]:
        if not domain or "." not in domain:
            return None
        return ",".join(f"DC={part}" for part in domain.split(".") if part)

    @staticmethod
    def _ldap_bind_user(domain: Optional[str], username: Optional[str]) -> Optional[str]:
        if not username:
            return None
        if "\\" in username or "@" in username or not domain:
            return username
        return f"{domain}\\{username}"

    @staticmethod
    def _looks_like_tool_failure(output: str) -> bool:
        lowered = str(output).lower()
        failure_markers = (
            "not installed",
            "failed:",
            "error running",
            "timed out",
            "invalid ",
            "traceback",
            "could not",
            "unrecognized arguments",
        )
        return any(marker in lowered for marker in failure_markers)

    def _redact(self, data: Dict[str, Any]) -> Dict[str, Any]:
        if not getattr(self.config, "assessment_redact_evidence", False):
            return dict(data)
        redacted = dict(data)
        for key in ("password", "hashes", "aesKey"):
            if redacted.get(key):
                redacted[key] = "***"
        return redacted

    def _redact_output(self, output: str, args: Dict[str, Any]) -> str:
        if not getattr(self.config, "assessment_redact_evidence", False):
            return output
        redacted = output
        for key in ("password", "hashes", "aesKey"):
            value = args.get(key)
            if value:
                redacted = redacted.replace(str(value), "***")
        return redacted

    @staticmethod
    def _extract_hosts(output: str) -> List[str]:
        hosts = []
        patterns = [
            r"Nmap scan report for\s+([^\s()]+)",
            r"•\s+[A-Za-z0-9_.-]+\s+\(([0-9A-Fa-f:.]+)\)",
            r"\s+•\s+([0-9A-Fa-f:.]+|[A-Za-z0-9_.-]+)$",
        ]
        for line in output.splitlines():
            for pattern in patterns:
                match = re.search(pattern, line.strip())
                if match:
                    host = match.group(1)
                    if host not in hosts and not host.lower().startswith(("command", "output")):
                        hosts.append(host)
        return hosts

    @staticmethod
    def _extract_services(output: str) -> List[tuple[str, str, Optional[str]]]:
        services = []
        current_host = None
        for line in output.splitlines():
            host_match = re.search(r"Nmap scan report for\s+([^\s()]+)", line)
            if host_match:
                current_host = host_match.group(1)
            formatted_host_match = re.search(r"•\s+(.+?)\s+\(([0-9A-Fa-f:.]+)\):\s+\d+/", line)
            if formatted_host_match:
                current_host = formatted_host_match.group(2)
            port_match = re.search(r"(\d+)/(tcp|udp)\s+open\s+([A-Za-z0-9_.-]+)", line)
            if port_match:
                services.append((port_match.group(1), port_match.group(3), current_host))
        return services

    @staticmethod
    def _extract_pwned_hosts(output: str) -> List[str]:
        hosts = []
        for line in output.splitlines():
            if "Pwn3d!" not in line and "[ADMIN]" not in line:
                continue
            match = re.search(r"\b((?:\d{1,3}\.){3}\d{1,3})\b", line)
            if match and match.group(1) not in hosts:
                hosts.append(match.group(1))
        return hosts

    @staticmethod
    def _target_from_command(output: str) -> Optional[str]:
        command_match = re.search(r"Command:\s+(.+)", output)
        if not command_match:
            return None
        command = command_match.group(1)

        netexec_match = re.search(r"(?:sudo\s+)?(?:[^\s/]*/)*(?:netexec|nxc)\s+\w+\s+([0-9A-Za-z_.:/-]+)", command)
        if netexec_match:
            return netexec_match.group(1)

        nmap_match = re.search(r"(?:sudo\s+)?nmap\b.+\s([0-9A-Za-z_.:/-]+)$", command)
        if nmap_match:
            return nmap_match.group(1)

        dc_match = re.search(r"-dc-ip\s+([0-9A-Za-z_.:/-]+)", command)
        if dc_match:
            return dc_match.group(1)
        return None

    @staticmethod
    def _fallback_summary(report: AssessmentReport) -> str:
        if not report.findings:
            return "No supported findings were derived from the collected evidence. Review failed/skipped evidence for tool or credential gaps."
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "informational": 4}
        ordered = sorted(report.findings, key=lambda item: severity_order.get(item.severity.lower(), 9))
        top = ordered[:5]
        lines = ["Top findings:"]
        lines.extend(f"- {item.severity.upper()}: {item.vuln_name} on {item.target}" for item in top)
        return "\n".join(lines)
