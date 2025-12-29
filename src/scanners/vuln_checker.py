import json

class VulnChecker:
    OWASP_CHECKLIST = {  
        'xss': {'check': lambda resp: '<script>' in resp.text, 'score': 8.0},
        
    }

    def check_standards(self, result: dict) -> dict:
        scores = {}
        for vuln, checker in self.OWASP_CHECKLIST.items():
            scores[vuln] = checker['check'](result)
        return {'owasp_compliance': sum(scores.values()) / len(scores), 'details': scores}