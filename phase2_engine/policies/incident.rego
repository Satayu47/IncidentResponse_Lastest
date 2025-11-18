package incident

# Policy for incident classification and automation decisions
default can_automate = false

# Allow automation for high-confidence classifications
can_automate {
    input.confidence >= 0.85
    input.severity == "high"
    input.owasp_category != ""
}

# Allow automation for medium severity with high confidence
can_automate {
    input.confidence >= 0.90
    input.severity == "medium"
    input.owasp_category != ""
}

# Require approval for low confidence
require_approval {
    input.confidence < 0.70
}

# Set severity based on OWASP category
severity = "high" {
    input.owasp_category == "A01:2021-Broken Access Control"
}

severity = "high" {
    input.owasp_category == "A03:2021-Injection"
}

severity = "high" {
    input.owasp_category == "A07:2021-Identification and Authentication Failures"
}

severity = "medium" {
    input.owasp_category == "A05:2021-Security Misconfiguration"
}

severity = "medium" {
    input.owasp_category == "A06:2021-Vulnerable and Outdated Components"
}

severity = "low" {
    input.owasp_category == "A09:2021-Security Logging and Monitoring Failures"
}

# Default severity
severity = "medium" {
    true
}

# Policy result
result = {
    "can_automate": can_automate,
    "require_approval": require_approval,
    "severity": severity,
    "reason": reason
}

reason = "High confidence classification allows automation" {
    can_automate
}

reason = "Low confidence requires human review" {
    require_approval
}

reason = "Standard policy check" {
    true
}

