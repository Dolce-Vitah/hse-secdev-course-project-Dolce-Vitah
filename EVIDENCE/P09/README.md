EVIDENCE/P09 — SBOM & SCA artifacts

**Содержимое:**
- sbom.json        — CycloneDX SBOM (Syft)
- sca_report.json  — Grype machine-readable JSON report
- sca_summary.md   — human-readable summary (counts + top findings)
- metadata.txt     — metadata: repository, commit, run_url, tag, generated_at, pinned images

**Краткая инструкция:** как получить артефакты
1) Через UI: Actions → выбрать run → скачать artifact "p09-sca" или "p09-sbom".
2) Через gh CLI:
```
   gh run list --workflow ci-sbom-sca.yml
   gh run download <run-id> --name p09-sca --dir ./downloads
   unzip ./downloads/p09-sca.zip -d ./downloads/p09-sca
```

**Как подготовить данные для DS (CSV)**
- Используйте scripts/export_sca_csv.py, он создаст файл sca_findings.csv с колонками:
  cve_id,severity,package,version,description,references,suggested_fixesб,artifact_locations

**Примеры использования в DS/отчёте**
- Для графика "кол-во High/Medium/Low по коммитам": собирайте metadata.txt + sca_findings.csv для каждого run, аггрегируйте по run_id/commit.
- Для списка приоритетов: используйте sca_findings.csv.filter(severity in [CRITICAL,HIGH]) и сортируйте по severity/epss/cvss.
- Для воспроизводимости: metadata.txt содержит commit SHA и run_url — храните эту связку рядом с артефактом в DS-схеме.
