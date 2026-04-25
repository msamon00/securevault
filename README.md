# SecureVault

A self-hosted, end-to-end encrypted password manager built as a cybersecurity portfolio project. Designed with defense-in-depth principles throughout.

## Architecture

[Browser] → [Nginx TLS] → [FastAPI Backend] → [PostgreSQL]
↑
WireGuard VPN (Phase 7 - in progress)

## Security Design

### Cryptography
- **Master password hashing:** Argon2id with time_cost=3, memory_cost=64MB, parallelism=2
- **Vault encryption:** AES-256-GCM (authenticated encryption)
- **Key derivation:** PBKDF2-HMAC-SHA256 with 600,000 iterations (OWASP 2023 recommendation)
- **Key storage:** Encryption key is never stored — derived fresh from master password on every login and embedded in the JWT session token only
- **Salt:** Unique 256-bit salt per user generated at registration

### Authentication
- JWT tokens (HS256) with 30-minute expiry
- Rate limiting: 5 failed attempts per IP per 5 minutes
- Single-user enforcement: registration endpoint permanently closes after first use
- Timing-safe error responses (same message for wrong username and wrong password)

### Transport Security
- TLS 1.2/1.3 only via Nginx reverse proxy
- Strong cipher suites (ECDHE + AES-GCM + CHACHA20)
- HSTS with 2-year max-age
- Security headers: X-Frame-Options, X-Content-Type-Options, CSP, Referrer-Policy

### Infrastructure
- All services run in isolated Docker containers on a private network
- Database not exposed outside the Docker network
- Backend not exposed outside the Docker network (Nginx only entry point)
- Secrets managed via .env file, never committed to version control

### Audit Logging
- All authentication events logged in structured JSON
- All vault operations logged with timestamp, username, and IP
- Log format compatible with Splunk and Elastic ingest

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.12, FastAPI |
| Database | PostgreSQL 16 |
| Frontend | React 18, Vite |
| Proxy | Nginx (Alpine) |
| Containerization | Docker, Docker Compose |
| Cryptography | argon2-cffi, Python cryptography library |
| Auth | python-jose (JWT) |

## Running Locally

```bash
git clone https://github.com/msamon00/securevault.git
cd securevault
cp .env.example .env  # fill in your values
docker compose up --build -d
```

Visit `https://localhost` and register your vault account. Registration closes permanently after first use.

## Project Phases

- [x] Phase 1: Docker Compose infrastructure
- [x] Phase 2: Authentication with Argon2id hashing
- [x] Phase 3: AES-256-GCM encryption + PBKDF2 key derivation
- [x] Phase 4: Encrypted vault CRUD API
- [x] Phase 5: React frontend
- [x] Phase 6: Nginx reverse proxy with TLS
- [ ] Phase 7: WireGuard VPN (in progress)
- [x] Phase 8: Audit logging + threat model