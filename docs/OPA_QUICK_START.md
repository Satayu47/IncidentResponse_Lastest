# OPA Quick Start Guide

## What is OPA?

OPA (Open Policy Agent) is a policy engine that enforces security policies for automated actions. It's integrated into your incident response system to ensure playbook steps comply with organizational policies.

## Quick Setup (5 minutes)

### Step 1: Start OPA Server

**Windows:**
```powershell
.\scripts\setup_opa.ps1
```

**Linux/Mac:**
```bash
chmod +x scripts/setup_opa.sh
./scripts/setup_opa.sh
```

**Manual (if scripts don't work):**
```bash
docker run -d -p 8181:8181 --name opa-server openpolicyagent/opa run --server
```

### Step 2: Load Policies

Policies are automatically loaded by the setup script. If you need to load manually:

```bash
# Load playbook policy
curl -X PUT http://localhost:8181/v1/policies/playbook \
  --data-binary @phase2_engine/policies/playbook.rego

# Load incident policy
curl -X PUT http://localhost:8181/v1/policies/incident \
  --data-binary @phase2_engine/policies/incident.rego
```

### Step 3: Configure Environment

Add to your `.env` file:
```bash
OPA_URL=http://localhost:8181/v1/data/playbook/result
```

### Step 4: Test Connection

```bash
python scripts/test_opa_connection.py
```

You should see:
```
✓ OPA server is healthy
✓ Policy working correctly
```

## How It Works

1. **When a playbook step is executed**, the system calls OPA with step metadata
2. **OPA evaluates the policy** and returns:
   - `ALLOW` - Step can proceed
   - `DENY` - Step is blocked
   - `REQUIRE_APPROVAL` - Needs human approval
3. **System enforces the decision** (or defaults to ALLOW if OPA unavailable)

## Policy Files

### `playbook.rego`
Controls which playbook actions are allowed based on:
- Action risk level (low/medium/high/destructive)
- Incident severity
- Action type

### `incident.rego`
Controls automation decisions based on:
- Classification confidence
- Incident severity
- OWASP category

## Testing

Test OPA is working:
```bash
python scripts/test_opa_connection.py
```

Test in your app:
1. Start Streamlit: `streamlit run app.py`
2. Classify an incident
3. Generate a response plan
4. Check if policy decisions appear in the UI

## Troubleshooting

**OPA server not starting?**
- Check Docker is running: `docker ps`
- Check port 8181 is free: `netstat -an | findstr 8181` (Windows) or `lsof -i :8181` (Linux/Mac)

**Policies not loading?**
- Check OPA logs: `docker logs opa-server`
- Verify policy files exist: `ls phase2_engine/policies/`

**Connection errors?**
- Wait a few seconds after starting OPA (it needs time to initialize)
- Test health: `curl http://localhost:8181/health`

**System works without OPA?**
- Yes! OPA is optional. System defaults to ALLOW if OPA unavailable.

## Stopping OPA

```bash
docker stop opa-server
docker rm opa-server
```

## Next Steps

- Customize policies in `phase2_engine/policies/*.rego`
- Add more policy rules for your organization
- See `docs/OPA_STATUS.md` for detailed information

