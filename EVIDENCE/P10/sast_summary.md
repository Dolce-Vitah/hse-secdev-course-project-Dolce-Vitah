# SAST & Secrets Summary (P10)

## Semgrep Findings
**Total Findings:** 1

| Severity | Rule ID | File | Message |
|--- |--- |--- |--- |
| warning | security.semgrep.python-hardcoded-secret-assignment | src/wishlist_api/domain/schemas.py:35 | Возможно, жестко закодированный секрет в переменной 'token_type'. Используйте os.getenv(). |

## Gitleaks Findings
**Total Secrets:** 0

No secrets found.

---
*Full reports available in artifacts: semgrep.sarif, gitleaks.json*
