"""
Execution Simulator for Incident Response Actions
Simulates real-world remediation steps without actually modifying systems
"""

import time
import random
from typing import Dict, List, Any, Callable
from datetime import datetime


class ExecutionSimulator:
    """
    Simulates execution of incident response playbook steps
    Safe for demonstrations - no actual system changes
    """
    
    def __init__(self):
        self.execution_log = []
        self.actions_map = {
            "block": self._simulate_block_ip,
            "isolate": self._simulate_isolate_system,
            "restart": self._simulate_restart_service,
            "reset": self._simulate_reset_credentials,
            "scan": self._simulate_security_scan,
            "patch": self._simulate_apply_patch,
            "backup": self._simulate_backup_data,
            "notify": self._simulate_send_notification,
            "investigate": self._simulate_investigate,
            "validate": self._simulate_validate_fix
        }
    
    def execute_playbook(self, playbook_steps: List[Dict[str, Any]], 
                        progress_callback: Callable = None) -> List[Dict[str, Any]]:
        """
        Execute playbook steps with simulation
        Returns list of execution results
        """
        results = []
        total_steps = len(playbook_steps)
        
        for idx, step in enumerate(playbook_steps, 1):
            if progress_callback:
                progress_callback(idx, total_steps, step.get("action", "Unknown"))
            
            result = self._execute_step(step)
            results.append(result)
            
            # Small delay between steps for realism
            time.sleep(0.3)
        
        return results
    
    def _execute_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single playbook step"""
        action = step.get("action", "").lower()
        
        # Find matching action handler
        handler = None
        for key, func in self.actions_map.items():
            if key in action:
                handler = func
                break
        
        # Default handler if no match
        if not handler:
            handler = self._simulate_generic_action
        
        # Execute with random realistic delay
        start_time = datetime.now()
        time.sleep(random.uniform(0.5, 1.5))
        
        result = handler(step)
        result["execution_time"] = (datetime.now() - start_time).total_seconds()
        result["timestamp"] = datetime.now().isoformat()
        
        self.execution_log.append(result)
        return result
    
    def _simulate_block_ip(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate blocking an IP address"""
        # Extract IP from step description
        description = step.get("description", "")
        ip = self._extract_ip(description)
        
        return {
            "step": step.get("action", "Block IP"),
            "status": "success",
            "action": "block_ip",
            "target": ip or "192.168.1.100",
            "message": f"✅ Blocked IP {ip or '192.168.1.100'} on firewall (simulated)",
            "details": "Added rule to deny all traffic from source IP"
        }
    
    def _simulate_isolate_system(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate isolating a compromised system"""
        return {
            "step": step.get("action", "Isolate System"),
            "status": "success",
            "action": "isolate_system",
            "target": "web-server-01",
            "message": "✅ System isolated from network (simulated)",
            "details": "Disabled network interfaces and removed from VLAN"
        }
    
    def _simulate_restart_service(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate restarting a service"""
        service = self._extract_service_name(step.get("description", ""))
        
        return {
            "step": step.get("action", "Restart Service"),
            "status": "success",
            "action": "restart_service",
            "target": service or "apache2",
            "message": f"✅ Service '{service or 'apache2'}' restarted (simulated)",
            "details": "Service stopped, configuration reloaded, service started"
        }
    
    def _simulate_reset_credentials(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate resetting user credentials"""
        return {
            "step": step.get("action", "Reset Credentials"),
            "status": "success",
            "action": "reset_credentials",
            "target": "admin_user",
            "message": "✅ User credentials reset (simulated)",
            "details": "Generated new password, forced password change on next login"
        }
    
    def _simulate_security_scan(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate running a security scan"""
        vulnerabilities_found = random.randint(0, 3)
        
        return {
            "step": step.get("action", "Security Scan"),
            "status": "success",
            "action": "security_scan",
            "target": "affected_systems",
            "message": f"✅ Security scan completed (simulated)",
            "details": f"Scanned 47 endpoints, found {vulnerabilities_found} potential issues"
        }
    
    def _simulate_apply_patch(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate applying security patches"""
        return {
            "step": step.get("action", "Apply Patch"),
            "status": "success",
            "action": "apply_patch",
            "target": "vulnerable_software",
            "message": "✅ Security patches applied (simulated)",
            "details": "Updated 12 packages, reboot required in 24 hours"
        }
    
    def _simulate_backup_data(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate backing up data"""
        size_mb = random.randint(500, 5000)
        
        return {
            "step": step.get("action", "Backup Data"),
            "status": "success",
            "action": "backup_data",
            "target": "critical_data",
            "message": "✅ Data backup completed (simulated)",
            "details": f"Backed up {size_mb} MB to secure storage"
        }
    
    def _simulate_send_notification(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate sending notifications"""
        return {
            "step": step.get("action", "Send Notification"),
            "status": "success",
            "action": "send_notification",
            "target": "security_team",
            "message": "✅ Notifications sent (simulated)",
            "details": "Alerted 5 team members via email and Slack"
        }
    
    def _simulate_investigate(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate investigation activities"""
        return {
            "step": step.get("action", "Investigate"),
            "status": "success",
            "action": "investigate",
            "target": "incident_logs",
            "message": "✅ Investigation completed (simulated)",
            "details": "Analyzed 2,341 log entries, identified attack vector"
        }
    
    def _simulate_validate_fix(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Simulate validation of remediation"""
        return {
            "step": step.get("action", "Validate Fix"),
            "status": "success",
            "action": "validate_fix",
            "target": "remediation_steps",
            "message": "✅ Validation successful (simulated)",
            "details": "All security controls verified, no residual threats detected"
        }
    
    def _simulate_generic_action(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Generic handler for unmatched actions"""
        return {
            "step": step.get("action", "Generic Action"),
            "status": "success",
            "action": "generic",
            "target": "system",
            "message": f"✅ {step.get('action', 'Action')} completed (simulated)",
            "details": step.get("description", "Action executed successfully")
        }
    
    def _extract_ip(self, text: str) -> str:
        """Extract IP address from text (simple pattern)"""
        import re
        pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        match = re.search(pattern, text)
        return match.group(0) if match else None
    
    def _extract_service_name(self, text: str) -> str:
        """Extract service name from text"""
        services = ["apache2", "nginx", "mysql", "postgresql", "redis", "ssh", "ftp"]
        text_lower = text.lower()
        
        for service in services:
            if service in text_lower:
                return service
        
        return None
    
    def get_execution_log(self) -> List[Dict[str, Any]]:
        """Get complete execution log"""
        return self.execution_log.copy()
    
    def clear_log(self):
        """Clear execution log"""
        self.execution_log.clear()


# Example usage
if __name__ == "__main__":
    simulator = ExecutionSimulator()
    
    test_steps = [
        {"action": "Block malicious IP", "description": "Block IP 192.168.1.100"},
        {"action": "Isolate compromised system", "description": "Isolate web-server-01"},
        {"action": "Restart Apache service", "description": "Restart apache2 service"},
        {"action": "Reset admin credentials", "description": "Reset admin user password"}
    ]
    
    print("🚀 Starting execution simulation...\n")
    
    results = simulator.execute_playbook(test_steps)
    
    for result in results:
        print(f"{result['message']}")
        print(f"   Details: {result['details']}")
        print(f"   Time: {result['execution_time']:.2f}s\n")
