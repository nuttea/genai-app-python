"""
SAST Quality Gate — parses a Datadog SARIF file, applies a severity threshold,
prints a structured report, and exits non-zero if blocking violations are found.

Modes:
    BLOCK (default)  Exit non-zero when violations at or above threshold exist.
    DETECT_ONLY      Always exit 0. Emit GitHub ::warning:: annotations for each
                     violation so they appear inline on the PR, but never fail CI.
                     Useful for raising visibility on HIGH findings without yet
                     enforcing them as a hard gate.

Usage:
    python3 quality_gate.py [--sarif PATH] [--threshold SEVERITY] [--detect-only]

Environment (fallbacks when flags are omitted):
    SARIF_PATH                path to SARIF file       (default: static-analysis-results.sarif)
    GATE_SEVERITY_THRESHOLD   blocking/detect threshold (default: CRITICAL in BLOCK, HIGH in DETECT_ONLY)
    DETECT_ONLY               set to "true" to activate detect-only mode

Severity model:
    CRITICAL  = DATADOG_CATEGORY:SECURITY  + level error/none
    HIGH      = DATADOG_CATEGORY:SECURITY  + level warning
              | any category               + level error
    MEDIUM    = level warning (non-security)
    LOW       = level note
    INFO      = level none (non-security)
"""

import argparse
import json
import os
import sys
from collections import Counter

SEVERITY_ORDER = ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]


def resolve_severity(result: dict, sarif_level: str) -> str:
    r_tags = result.get("properties", {}).get("tags", [])
    is_security = "DATADOG_CATEGORY:SECURITY" in r_tags
    level = sarif_level.lower()

    if is_security:
        if level in ("error", "none"):
            return "CRITICAL"
        if level == "warning":
            return "HIGH"
        return "MEDIUM"

    if level == "error":
        return "HIGH"
    if level == "warning":
        return "MEDIUM"
    if level == "note":
        return "LOW"
    return "INFO"


def get_category(result: dict) -> str:
    for tag in result.get("properties", {}).get("tags", []):
        if tag.startswith("DATADOG_CATEGORY:"):
            return tag.split(":", 1)[1]
    return "UNCATEGORIZED"


def parse_findings(sarif: dict) -> list[dict]:
    findings = []
    for run in sarif.get("runs", []):
        rules = {
            r["id"]: r
            for r in run.get("tool", {}).get("driver", {}).get("rules", [])
        }
        for result in run.get("results", []):
            sarif_level = result.get("level", "none")
            rule_id = result.get("ruleId", "unknown")
            rule = rules.get(rule_id, {})
            rule_tags = rule.get("properties", {}).get("tags", [])
            cwe = next((t for t in rule_tags if t.startswith("CWE:")), "")
            msg = result.get("message", {}).get("text", "").strip()
            locs = result.get("locations", [])
            phys = locs[0].get("physicalLocation", {}) if locs else {}
            uri = phys.get("artifactLocation", {}).get("uri", "unknown")
            line = phys.get("region", {}).get("startLine", "?")
            findings.append(
                {
                    "severity": resolve_severity(result, sarif_level),
                    "sarif_level": sarif_level,
                    "category": get_category(result),
                    "cwe": cwe,
                    "rule_id": rule_id,
                    "uri": uri,
                    "line": line,
                    "msg": msg[:160],
                }
            )
    return findings


def emit_annotations(violations: list[dict]) -> None:
    """Emit GitHub Actions warning annotations for each violation."""
    for f in violations:
        cwe = f" [{f['cwe']}]" if f["cwe"] else ""
        title = f"[{f['severity']}] {f['rule_id']}{cwe}"
        msg = f"{f['msg']} (category: {f['category']})"
        # file and line let GitHub pin the annotation to the exact source location
        print(f"::warning file={f['uri']},line={f['line']},title={title}::{msg}")


def print_report(
    findings: list[dict],
    threshold: str,
    blocking_severities: set,
    detect_only: bool,
) -> None:
    violations = [f for f in findings if f["severity"] in blocking_severities]
    informational = [f for f in findings if f["severity"] not in blocking_severities]

    mode_label = "DETECT ONLY" if detect_only else "BLOCK"
    SEP = "─" * 66
    SEP2 = "═" * 66

    print()
    print(SEP2)
    print(f"  SAST Quality Gate Report  [{mode_label}]")
    print(SEP2)
    bl_str = " › ".join(SEVERITY_ORDER[: SEVERITY_ORDER.index(threshold) + 1])
    print(f"  Mode       : {mode_label}")
    print(f"  Threshold  : {threshold}  (flagged: {bl_str})")
    print(
        f"  Total      : {len(findings)} finding(s)  |  "
        f"{'Detected' if detect_only else 'Blocking'}: {len(violations)}  |  "
        f"Non-{'detected' if detect_only else 'blocking'}: {len(informational)}"
    )
    print(
        f"  Files      : {len(set(f['uri'] for f in findings))}  |  "
        f"Unique rules: {len(set(f['rule_id'] for f in findings))}"
    )
    print()

    print(SEP)
    print("  Severity Breakdown")
    print(SEP)
    sev_counts = Counter(f["severity"] for f in findings)
    for sev in SEVERITY_ORDER:
        count = sev_counts.get(sev, 0)
        bar = "█" * min(count, 36)
        if sev in blocking_severities and count > 0:
            flag = "  ◄ DETECTED (would block)" if detect_only else "  ◄ BLOCKING"
        else:
            flag = ""
        print(f"  {sev:<10} {count:>4}  {bar}{flag}")
    print()

    print(SEP)
    print("  Category Breakdown  (DATADOG_CATEGORY)")
    print(SEP)
    cat_counts = Counter(f["category"] for f in findings)
    for cat, count in cat_counts.most_common():
        flagged_in_cat = sum(
            1
            for f in findings
            if f["category"] == cat and f["severity"] in blocking_severities
        )
        flag_word = "detected" if detect_only else "blocking"
        flag = f"  ({flagged_in_cat} {flag_word})" if flagged_in_cat else ""
        print(f"  {cat:<20} {count:>4}{flag}")
    print()

    print(SEP)
    print("  Top Violation Rules")
    print(f"  {'COUNT':>5}  {'SEVERITY':<10}  {'CATEGORY':<16}  RULE")
    print(SEP)
    rule_meta = {}
    for f in findings:
        if f["rule_id"] not in rule_meta:
            rule_meta[f["rule_id"]] = {
                "severity": f["severity"],
                "category": f["category"],
                "cwe": f["cwe"],
            }
    rule_counts = Counter(f["rule_id"] for f in findings)
    for rule_id, count in rule_counts.most_common(15):
        m = rule_meta[rule_id]
        cwe = f"  {m['cwe']}" if m["cwe"] else ""
        print(
            f"  {count:>5}  {m['severity']:<10}  {m['category']:<16}  {rule_id}{cwe}"
        )
    if len(rule_counts) > 15:
        print(f"         … and {len(rule_counts) - 15} more rule(s)")
    print()

    print(SEP)
    print("  Most Affected Files")
    print(SEP)
    file_counts = Counter(f["uri"] for f in findings)
    for uri, count in file_counts.most_common(10):
        has_flagged = any(
            f["uri"] == uri and f["severity"] in blocking_severities for f in findings
        )
        flag = "  ◄ has detected" if (detect_only and has_flagged) else (
            "  ◄ has blocking" if has_flagged else ""
        )
        print(f"  {count:>4}  {uri}{flag}")
    if len(file_counts) > 10:
        print(f"         … and {len(file_counts) - 10} more file(s)")
    print()

    if informational:
        print(SEP)
        label = "Non-Detected" if detect_only else "Non-Blocking"
        print(f"  {label} Findings  ({len(informational)} total — below {threshold})")
        print(SEP)
        shown: dict[str, int] = {}
        printed = 0
        for f in informational:
            shown.setdefault(f["rule_id"], 0)
            if shown[f["rule_id"]] < 2 and printed < 10:
                print(f"  [{f['severity']:<10}] [{f['category']:<16}] {f['rule_id']}")
                print(f"               {f['uri']}:{f['line']}")
                shown[f["rule_id"]] += 1
                printed += 1
        if len(informational) > printed:
            print(f"  … and {len(informational) - printed} more non-detected finding(s)")
        print()

    if violations:
        label = "Detected Violations" if detect_only else "BLOCKING Violations"
        print(SEP)
        print(f"  {label}  ({len(violations)} total — severity >= {threshold})")
        print(SEP)
        for f in violations[:20]:
            cwe = f"  {f['cwe']}" if f["cwe"] else ""
            print(f"  [{f['severity']:<10}] [{f['category']:<16}]{cwe}")
            print(f"    Rule : {f['rule_id']}")
            print(f"    File : {f['uri']}:{f['line']}")
            print(f"    Msg  : {f['msg']}")
            print()
        if len(violations) > 20:
            print(f"  … and {len(violations) - 20} more violation(s)")

        if detect_only:
            # Emit inline GitHub annotations so violations appear on the PR diff
            emit_annotations(violations)
            print(SEP2)
            print(
                f"  ⚠️  DETECT ONLY — {len(violations)} violation(s) at severity >= {threshold}"
            )
            print(f"  ℹ️  CI not failed. Resolve these before enabling BLOCK mode.")
            print(SEP2)
            print()
            # exit 0 — intentionally no sys.exit(1)
        else:
            print(SEP2)
            print(f"  ❌ Quality Gate FAILED — {len(violations)} violation(s) at severity >= {threshold}")
            print(SEP2)
            print()
            sys.exit(1)
    else:
        verdict = "✅ PASSED" if not detect_only else "✅ PASSED"
        print(SEP2)
        print(f"  {verdict} — no violations at severity >= {threshold}")
        print(SEP2)
        print()


def main() -> None:
    detect_only_env = os.environ.get("DETECT_ONLY", "").lower() in ("1", "true", "yes")
    default_threshold = "HIGH" if detect_only_env else "CRITICAL"

    parser = argparse.ArgumentParser(description="SAST Quality Gate")
    parser.add_argument(
        "--sarif",
        default=os.environ.get("SARIF_PATH", "static-analysis-results.sarif"),
    )
    parser.add_argument(
        "--threshold",
        default=os.environ.get("GATE_SEVERITY_THRESHOLD", default_threshold).upper(),
    )
    parser.add_argument(
        "--detect-only",
        action="store_true",
        default=detect_only_env,
        help="Report violations as warnings but always exit 0",
    )
    args = parser.parse_args()

    threshold = args.threshold.upper()
    if threshold not in SEVERITY_ORDER:
        print(f"::warning::Unknown threshold '{threshold}', defaulting to {'HIGH' if args.detect_only else 'CRITICAL'}")
        threshold = "HIGH" if args.detect_only else "CRITICAL"

    if not os.path.exists(args.sarif):
        print("::error::SARIF file not found — static analyzer may have failed")
        sys.exit(1)

    with open(args.sarif) as f:
        sarif = json.load(f)

    findings = parse_findings(sarif)
    blocking_severities = set(SEVERITY_ORDER[: SEVERITY_ORDER.index(threshold) + 1])
    print_report(findings, threshold, blocking_severities, detect_only=args.detect_only)


if __name__ == "__main__":
    main()
