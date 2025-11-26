# SCA summary

## Counts by severity
{"High":3,"Medium":1}

## Top findings (sorted by severity)

- **GHSA-cxww-7g56-2vh6**
  - severity: High
  - package: actions/download-artifact@v4
  - description: @actions/download-artifact has an Arbitrary File Write via artifact extraction
  - references: https://github.com/advisories/GHSA-cxww-7g56-2vh6
  - suggested action: consider upgrade to: 4.1.3

- **GHSA-f96h-pmfr-66vw**
  - severity: High
  - package: starlette@0.38.6
  - description: Starlette Denial of service (DoS) via multipart/form-data
  - references: https://github.com/advisories/GHSA-f96h-pmfr-66vw; https://nvd.nist.gov/vuln/detail/CVE-2024-47874
  - suggested action: consider upgrade to: 0.40.0

- **GHSA-wj6h-64fc-37mp**
  - severity: High
  - package: ecdsa@0.19.1
  - description: Minerva timing attack on P-256 in python-ecdsa
  - references: https://github.com/advisories/GHSA-wj6h-64fc-37mp; https://nvd.nist.gov/vuln/detail/CVE-2024-23342
  - suggested action: investigate / consider waiver

- **GHSA-2c2j-9gv5-cj73**
  - severity: Medium
  - package: starlette@0.38.6
  - description: Starlette has possible denial-of-service vector when parsing large files in multipart forms
  - references: https://github.com/advisories/GHSA-2c2j-9gv5-cj73; https://nvd.nist.gov/vuln/detail/CVE-2025-54121
  - suggested action: consider upgrade to: 0.47.2
