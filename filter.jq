# jq filter to generate human-readable SCA summary
# Usage: jq -r -f filter.jq sca_report.json > EVIDENCE/P09/sca_summary.md

def counts:
  try ([.matches[].vulnerability.severity] | group_by(.) | map({(.[0]): length}) | add) catch {};

def sevscore($s):
  if ($s|ascii_upcase) == "CRITICAL" then 6
  elif ($s|ascii_upcase) == "HIGH" then 5
  elif ($s|ascii_upcase) == "MEDIUM" then 4
  elif ($s|ascii_upcase) == "LOW" then 3
  else 1 end;

def fixes_of($m):
  (
    ($m.vulnerability.fix?.versions // $m.vulnerability.fix_versions // [])
    + ([$m.matchDetails[]?.fix?.suggestedVersion // empty])
    + ([$m.matchDetails[]?.found?.fixed_in // empty])
  ) | map(select(. != null and . != "")) | unique;

(
  "# SCA summary\n\n## Counts by severity\n"
  +
  ((counts | tojson) // "{}")
  +
  "\n\n## Top findings (sorted by severity)\n\n"
  +
  (
    if (.matches | length) == 0 then
      "- No matches\n"
    else
      (
        .matches
        | map( . as $m
            | {
                id: ($m.vulnerability.id // ($m.relatedVulnerabilities[0].id // "N/A")),
                severity: ($m.vulnerability.severity // "UNKNOWN"),
                pkg: ($m.artifact.name // ($m.artifact.purl // "unknown")),
                ver: ($m.artifact.version // "unknown"),
                desc: ($m.vulnerability.description // ""),
                refs: (($m.vulnerability.dataSource // "") + (if ($m.relatedVulnerabilities|length>0) then ("; " + ($m.relatedVulnerabilities[0].dataSource // "")) else "" end)),
                fixes: fixes_of($m)
              }
          )
        | map(. + { score: sevscore(.severity) })
        | sort_by(.score) | reverse
        | map(
            "- **" + (.id // "N/A") + "**\n" +
            "  - severity: " + (.severity // "N/A") + "\n" +
            "  - package: " + (.pkg // "N/A") + "@" + (.ver // "N/A") + "\n" +
            "  - description: " + ((.desc | gsub("\n"; " ") | .[0:400]) // "") + (if (.desc|length) > 400 then "..." else "" end) + "\n" +
            "  - references: " + (.refs // "none") + "\n" +
            "  - suggested action: " + (if (.fixes | length > 0) then ("consider upgrade to: " + (.fixes | join(", "))) else "investigate / consider waiver" end)
          )
        | join("\n\n")
      )
    end
  )
)
