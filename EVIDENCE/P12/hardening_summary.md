# P12 Hardening Summary

## Dockerfile
- Pinned runtime APK packages to fixed versions (`libpq`, `wget`, `sqlite`) to remove DL3018 warning from hadolint.
- Image already non-root (`app` user) with healthcheck and no embedded secrets/config.

## Kubernetes IaC
- Added dedicated namespace `wishlist`; serviceaccount with `automountServiceAccountToken: false`.
- Deployment now uses non-root UID/GID 10001, seccomp RuntimeDefault, drop ALL caps, read-only root FS.
- Added CPU/Memory requests+limits and `imagePullPolicy: Always`.
- Added NetworkPolicy allowing ingress to wishlist-api only on TCP/8000 from namespace pods.
- Service moved to `wishlist` namespace.

## Open findings to address next
- Checkov: remaining items include image digest (skipped via config for app:local), consider adding digest once registry image is published.
- Trivy: High `CVE-2024-23342` (ecdsa 0.19.1, no patch yet), Medium `filelock` (<3.20.1) and `pip` (<25.3) — plan to bump deps when available.
