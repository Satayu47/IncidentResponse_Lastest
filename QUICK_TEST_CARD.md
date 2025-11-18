# Quick Test Card - Copy & Paste

## Test 1: A01 - Broken Access Control
```
User from marketing department somehow got into the HR system and downloaded employee salary data. They shouldn't have access to that system at all.
```

## Test 1: A04 - Insecure Design
```
Our payment API doesn't check how many times someone can try to pay. A customer accidentally triggered 10,000 payment attempts in 5 minutes and crashed the system.
```

## Test 1: A05 - Security Misconfiguration
```
Found out our production database is still using the default admin password "admin123". Also, error messages are showing full stack traces to users.
```

## Test 1: A07 - Authentication Failures
```
Seeing hundreds of failed login attempts from the same IP address. Our password policy is too weak - people are using "Password123" and it's being accepted.
```

---

## Test 2: Multiple Incidents (A01, A04, A05, A07)
```
We had a major security incident yesterday. Here's what happened:

1. Someone without proper permissions accessed our customer database and exported personal information. They weren't supposed to have that access.

2. Our API has no rate limiting, so an attacker was able to send thousands of requests per second and caused a denial of service.

3. We discovered our staging server is using default admin credentials and it's accessible from the internet. Debug mode is also enabled.

4. Our login system is being hit with brute force attacks. We're seeing 500+ failed attempts per hour from the same IP. Also, our password requirements are too weak - "password" is still being accepted.

Need immediate response plan for all of these.
```

---

## Test 3: A02 - Cryptographic Failures
```
Our database is storing user passwords in plain text. No hashing, no encryption. Also, we're sending credit card numbers over HTTP instead of HTTPS.
```

## Test 3: A03 - Injection
```
Security team found SQL injection in our login form. An attacker was able to run database queries and extract user email addresses. The login form isn't sanitizing input properly.
```

## Test 3: A06 - Vulnerable Components
```
Our application uses an old version of Apache Struts that has a known vulnerability (CVE-2023-50164). It's been flagged by our security scanner. We need to patch it but don't know what else might break.
```

## Test 3: A10 - SSRF
```
An attacker found a way to make our server make requests to internal services. They tried to access our internal admin panel at 192.168.1.100 through our API endpoint. The API doesn't validate URLs before making requests.
```

---

## Test 4: Automated Playbook
```
URGENT: We just discovered an unauthorized admin account was created and used to access our production database. Customer data including credit card numbers may have been exfiltrated. We need an immediate response plan.
```

---

App: http://localhost:8501

