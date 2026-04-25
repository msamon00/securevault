# SecureVault Threat Model

## Assets Being Protected

1. **Vault entries** — stored passwords, usernames, URLs, and notes
2. **Master password** — the single credential that unlocks everything
3. **Encryption key** — derived from the master password, used to decrypt vault entries
4. **Session tokens** — JWTs that grant temporary access to the API

## Trust Boundaries

- **Browser ↔ Nginx:** Public-facing. Encrypted with TLS.
- **Nginx ↔ Backend:** Internal Docker network. Not exposed externally.
- **Backend ↔ Database:** Internal Docker network. Not exposed externally.

## Threat Analysis (STRIDE)

### Spoofing
| Threat | Mitigation |
|---|---|
| Attacker impersonates legitimate user | Argon2id master password hash; JWT signature validation |
| Session token stolen and replayed | 30-minute token expiry; HTTPS-only transport |

### Tampering
| Threat | Mitigation |
|---|---|
| Attacker modifies encrypted vault entries in database | AES-256-GCM authentication tag detects any tampering |
| Attacker modifies JWT token claims | HS256 signature invalidated on any modification |

### Repudiation
| Threat | Mitigation |
|---|---|
| User denies performing vault operations | Structured audit log records all events with timestamp and IP |

### Information Disclosure
| Threat | Mitigation |
|---|---|
| Database stolen | All vault data AES-256-GCM encrypted; useless without master password |
| Network traffic intercepted | TLS 1.2/1.3 with strong cipher suites |
| Master password enumerated from hash | Argon2id with 64MB memory cost makes GPU attacks expensive |
| Server version disclosure | Nginx server_tokens off |

### Denial of Service
| Threat | Mitigation |
|---|---|
| Brute force login attack | Rate limiting: 5 attempts per IP per 5 minutes |
| Resource exhaustion | Docker container isolation limits blast radius |

### Elevation of Privilege
| Threat | Mitigation |
|---|---|
| Attacker accesses another user's vault entries | All queries filter by user_id from validated JWT |
| Attacker registers a second account | Single-user enforcement in registration endpoint |

## Residual Risks

1. **Self-signed TLS certificate** — browser will show a warning. Acceptable for home use. Mitigated in production by using a CA-signed certificate (e.g. Let's Encrypt).
2. **JWT secret in .env** — if the .env file is compromised, session tokens can be forged. Mitigated by keeping .env out of version control and restricting file permissions.
3. **In-memory rate limiting** — resets on container restart. A persistent rate limiter (e.g. Redis) would be more robust.
4. **Single-factor authentication** — no MFA currently implemented. A TOTP second factor would significantly raise the bar for attackers.

## What This Project Does Not Protect Against

- Physical access to the host machine
- Compromise of the host operating system
- Malicious browser extensions with access to page content
- Master password disclosure by the user themselves