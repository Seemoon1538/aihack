import json
import os
from datetime import datetime
from typing import List, Dict, Any
from src.core.logger import RealTimeLogger

class NeuralAutopsy:
    def __init__(self, results: List[Dict], target: str, config: Dict, logger: RealTimeLogger):
        self.results = [r for r in results if r and isinstance(r, dict)]
        self.target = target
        self.config = config
        self.logger = logger
        self.timestamp = int(datetime.now().timestamp())

    def generate(self):
        os.makedirs("reports", exist_ok=True)
        report = self._build_report()
        self._save_json(report)
        self._save_md(report)

    def _build_report(self) -> Dict:
        return {
            "header": self._header(),
            "summary": self._summary(),
            "findings": self._findings(),
            "proof_of_concept": self._poc(),
            "data_exfiltrated": self._data_exfiltrated(),
            "recommendations": self._recommendations(),
            "ai_intelligence": self._ai_stats()
        }

    def _header(self) -> Dict:
        return {
            "target": self.target,
            "scan_id": f"AIHACK-{self.timestamp}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version": "v15.7"
        }

    def _summary(self) -> Dict:
        success = sum(1 for r in self.results if r.get("success"))
        critical = sum(1 for r in self.results if r.get("success") and r.get("risk", 0) >= 8)
        return {
            "total_attacks": len(self.results),
            "exploited": success,
            "critical_vulnerabilities": critical,
            "ports_open": len(self._get_open_ports())
        }

    def _findings(self) -> List[Dict]:
        findings = []
        for res in self.results:
            finding = {
                "vulnerability": res.get("attack", "unknown").replace("_", " ").upper(),
                "status": "EXPLOITED" if res.get("success") else "FAILED",
                "risk_level": self._risk_badge(res.get("risk", 0)),
                "payloads_tested": self._get_payloads(res),
                "successful_payload": res.get("vulnerable_payload", "N/A"),
                "proof": self._format_proof(res),
                "timestamp": datetime.fromtimestamp(res.get("timestamp", self.timestamp)).strftime("%H:%M:%S")
            }
            findings.append(finding)
        return findings

    def _poc(self) -> List[Dict]:
        pocs = []
        for res in self.results:
            if not res.get("success"): continue
            param = self._get_param(res)
            payload = res.get("vulnerable_payload", "")
            excerpt = self._excerpt(res.get("data_leaked", {}))
            poc = {
                "type": res["attack"],
                "url": self.target,
                "method": "GET",
                "parameter": param,
                "payload": payload,
                "curl": f"curl \"{self.target}\" -G --data-urlencode \"{param}={payload}\"",
                "response_excerpt": excerpt if excerpt != "N/A" else "Success"
            }
            pocs.append(poc)
        return pocs

    def _data_exfiltrated(self) -> Dict:
        data = {}
        for res in self.results:
            if res.get("success") and res.get("data_leaked"):
                key = res["attack"]
                sample = str(res["data_leaked"])[:500]
                data[key] = {
                    "size_bytes": len(str(res["data_leaked"])),
                    "sample": sample
                }
        return data or {"status": "No sensitive data exfiltrated"}

    def _recommendations(self) -> List[str]:
        recs = set()
        for res in self.results:
            if not res.get("success"): continue
            a = res["attack"]
            if "sql" in a:
                recs.update(["Use prepared statements", "WAF", "Input sanitization"])
            if "bruteforce" in a:
                recs.add("Rate limiting + strong passwords")
            if a in ["xss", "csrf"]:
                recs.update(["CSP", "Anti-CSRF tokens"])
            if a == "port_scan":
                recs.add("Close unused ports")
        return list(recs) or ["Full security audit required"]

    def _ai_stats(self) -> Dict:
        try:
            from src.ai.brain import NeuralBrain
            brain = NeuralBrain.load(self.config)
            stats = brain.get_stats()
            return {
                "attacks_remembered": stats["total"],
                "successful_exploits": stats["successes"],
                "learning_efficiency": f"{stats['successes']/max(stats['total'],1)*100:.1f}%"
            }
        except:
            return {"status": "AI offline"}

    def _get_open_ports(self):
        for res in self.results:
            if res.get("attack") == "port_scan":
                return res.get("open_ports", [])
        return []

    def _get_payloads(self, res: Dict) -> str:
        payloads = res.get("tested_payloads", [])
        if not payloads: return "N/A"
        return ", ".join([f"`{p[:30]}`" for p in payloads[:3]]) + ("..." if len(payloads) > 3 else "")

    def _get_param(self, res: Dict) -> str:
        a = res["attack"]
        if a == "sql_injection": return "id"
        if a == "xss": return "q"
        if a == "rce": return "cmd"
        if a == "ssrf": return "url"
        return "unknown"

    def _excerpt(self, data: Dict) -> str:
        if not data: return "N/A"
        if "dump" in data: return data["dump"][:200]
        if "output" in data: return data["output"][:200]
        return str(data)[:200]

    def _format_proof(self, res: Dict) -> str:
        if not res.get("success"): return "Failed"
        a = res["attack"]
        if a == "port_scan":
            return f"Open: {', '.join(map(str, res.get('open_ports', [])))}"
        if "data_leaked" in res and res["data_leaked"]:
            return "Data exfiltrated"
        return res.get("vulnerable_payload", "Exploited")

    def _risk_badge(self, risk: int) -> str:
        if risk >= 9: return "CRITICAL"
        if risk >= 7: return "HIGH"
        if risk >= 5: return "MEDIUM"
        return "LOW"

    def _save_json(self, report: Dict):
        path = f"reports/autopsy_{self.timestamp}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        self.logger.critical(f"JSON: {path}")

    def _save_md(self, report: Dict):
        path = f"reports/autopsy_{self.timestamp}.md"
        with open(path, "w", encoding="utf-8") as f:
            f.write(self._render_md(report))
        self.logger.critical(f"MD: {path}")

    def _render_md(self, report: Dict) -> str:
        h = report["header"]
        s = report["summary"]
        md = f"# AIHACK AUTOPSY v15.7\n"
        md += f"**Target:** `{h['target']}` | **ID:** `{h['scan_id']}`\n\n"
        md += f"## SUMMARY\n"
        md += f"- Exploited: `{s['exploited']}/{s['total_attacks']}`\n"
        md += f"- Critical: `{s['critical_vulnerabilities']}`\n"
        md += f"- Open Ports: `{s['ports_open']}`\n\n"

        md += f"## FINDINGS\n"
        for f in report["findings"]:
            md += f"### {f['vulnerability']} — **{f['status']}** [{f['risk_level']}]\n"
            md += f"- Payload: `{f['successful_payload']}`\n"
            md += f"- Tested: {f['payloads_tested']}\n"
            md += f"- Time: `{f['timestamp']}`\n"
            md += f"- Proof: {f['proof']}\n\n"

        if report["data_exfiltrated"] != {"status": "No sensitive data exfiltrated"}:
            md += f"## EXFILTRATED DATA\n"
            for k, v in report["data_exfiltrated"].items():
                md += f"### {k.upper()}\n"
                md += f"```text\n{v['sample']}\n```\n"
                md += f"_Size: {v['size_bytes']} bytes_\n\n"

        md += f"## PROOF OF CONCEPT\n"
        for poc in report["proof_of_concept"]:
            md += f"```bash\n{poc['curl']}\n```\n"
            md += f"_Response: {poc['response_excerpt'][:150]}..._\n\n"

        md += f"## REMEDIATION\n"
        for r in report["recommendations"]:
            md += f"- {r}\n"

        ai = report["ai_intelligence"]
        md += f"\n## AI\n"
        md += f"- Memory: `{ai.get('attacks_remembered', 0)}`\n"
        md += f"- Success: `{ai.get('learning_efficiency', '0%')}`\n"

        return md