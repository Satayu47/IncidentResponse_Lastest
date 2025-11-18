package playbook

# Default: deny all actions unless explicitly allowed
default allow = false

# Allow low-risk actions for any severity
allow {
    input.action.risk_level == "low"
    input.action.type != "destructive"
}

# Allow medium-risk actions for medium/high severity incidents
allow {
    input.incident.severity == "high"
    input.action.risk_level == "medium"
    input.action.type != "destructive"
}

allow {
    input.incident.severity == "medium"
    input.action.risk_level == "medium"
    input.action.type == "send_alert"
}

# Allow high-risk actions only for high severity with approval
allow {
    input.incident.severity == "high"
    input.action.risk_level == "high"
    input.action.requires_approval == true
}

# Always allow informational/read-only actions
allow {
    input.action.type == "send_alert"
}

allow {
    input.action.type == "create_ticket"
}

allow {
    input.action.type == "log_event"
}

# Deny destructive actions without explicit approval
deny {
    input.action.risk_level == "destructive"
    not input.action.approved
}

# Return policy decision
result = "ALLOW" {
    allow
}

result = "DENY" {
    deny
}

result = "REQUIRE_APPROVAL" {
    input.action.risk_level == "high"
    not allow
    not deny
}

