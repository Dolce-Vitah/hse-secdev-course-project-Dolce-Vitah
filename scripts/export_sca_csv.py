#!/usr/bin/env python3
import csv
import json
import sys
from pathlib import Path

"""
Usage:
  python scripts/export_sca_csv.py EVIDENCE/P09/sca_report.json EVIDENCE/P09/sca_findings.csv

Output columns:
  cve_id,severity,package,version,description,references,suggested_fixes,artifact_locations
"""


def normalize_list(x):
    if isinstance(x, list):
        return ";".join([str(i) for i in x if i])
    if x:
        return str(x)
    return ""


def gather_fixes(vuln, match_details):
    fixes = []
    fix_obj = vuln.get("fix")
    if isinstance(fix_obj, dict):
        fv = fix_obj.get("versions")
        if isinstance(fv, list):
            fixes.extend(fv)
    fv2 = vuln.get("fix_versions")
    if isinstance(fv2, list):
        fixes.extend(fv2)
    for md in match_details or []:
        if not isinstance(md, dict):
            continue
        fix = md.get("fix")
        if isinstance(fix, dict):
            sv = fix.get("suggestedVersion")
            if sv:
                fixes.append(sv)
        found = md.get("found")
        if isinstance(found, dict):
            fi = found.get("fixed_in")
            if fi:
                fixes.append(fi)
    seen = set()
    uniq = []
    for f in fixes:
        if not f:
            continue
        if f not in seen:
            seen.add(f)
            uniq.append(f)
    return uniq


def main(inp, out):
    inp = Path(inp)
    out = Path(out)
    if not inp.exists():
        print(f"Input file not found: {inp}", file=sys.stderr)
        sys.exit(2)
    try:
        data = json.loads(inp.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"Failed to read/parse JSON: {e}", file=sys.stderr)
        sys.exit(2)

    rows = []
    for m in data.get("matches", []):
        vuln = m.get("vulnerability", {}) or {}
        artifact = m.get("artifact", {}) or {}
        match_details = m.get("matchDetails", []) or []
        cve_id = vuln.get("id") or (m.get("relatedVulnerabilities", [{}])[0].get("id"))
        severity = vuln.get("severity") or ""
        package = artifact.get("name", "")
        version = artifact.get("version", "")
        desc = (vuln.get("description") or "").replace("\n", " ").strip()
        refs = vuln.get("dataSource") or ""
        fixes = gather_fixes(vuln, match_details)
        locations = normalize_list(artifact.get("locations", []))
        rows.append(
            {
                "cve_id": cve_id,
                "severity": severity,
                "package": package,
                "version": version,
                "description": desc,
                "references": refs,
                "suggested_fixes": ";".join(fixes),
                "artifact_locations": locations,
            }
        )

    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=[
                "cve_id",
                "severity",
                "package",
                "version",
                "description",
                "references",
                "suggested_fixes",
                "artifact_locations",
            ],
        )
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(
            "Usage: python scripts/export_sca_csv.py <sca_report.json> <out.csv>",
            file=sys.stderr,
        )
        sys.exit(2)
    main(sys.argv[1], sys.argv[2])
