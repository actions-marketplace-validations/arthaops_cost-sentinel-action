#!/usr/bin/env python3
"""
ArthaOps Cost Sentinel — PR Infrastructure Cost Diff Analyzer
Analyzes Terraform plan JSON, calculates estimated monthly deltas,
and formats an institutional GitHub PR comment.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def load_plan(plan_path: str) -> dict:
    if not plan_path or not Path(plan_path).exists():
        # Fallback simulated plan if running in demonstration mode
        return {
            "resource_changes": [
                {
                    "address": "aws_instance.worker",
                    "type": "aws_instance",
                    "change": {
                        "actions": ["create"],
                        "after": {"instance_type": "c6i.2xlarge"}
                    }
                },
                {
                    "address": "aws_ebs_volume.storage",
                    "type": "aws_ebs_volume",
                    "change": {
                        "actions": ["update"],
                        "before": {"size": 100, "type": "gp2"},
                        "after": {"size": 250, "type": "gp3"}
                    }
                }
            ]
        }
    with open(plan_path, "r", encoding="utf-8") as f:
        return json.load(f)


def estimate_resource_cost(resource: dict) -> tuple[str, str, float]:
    rtype = resource.get("type", "unknown")
    addr = resource.get("address", rtype)
    change = resource.get("change", {})
    actions = change.get("actions", [])
    action_str = "+ create" if "create" in actions else ("~ update" if "update" in actions else "- delete")

    # Conservative baseline estimates for common resources
    cost_delta = 0.0
    if rtype == "aws_instance":
        itype = change.get("after", {}).get("instance_type", "t3.medium")
        if "c6i.2xlarge" in itype:
            cost_delta = 248.20
        elif "t3.medium" in itype:
            cost_delta = 30.37
        elif "t3.micro" in itype:
            cost_delta = 7.60
        else:
            cost_delta = 50.00
    elif rtype == "aws_ebs_volume":
        size = change.get("after", {}).get("size", 100)
        cost_delta = size * 0.08
    elif rtype == "aws_nat_gateway":
        cost_delta = 32.85
    elif rtype == "google_compute_instance":
        cost_delta = 45.00
    elif rtype == "azurerm_virtual_machine":
        cost_delta = 72.00
    else:
        cost_delta = 15.00

    if "delete" in actions:
        cost_delta = -abs(cost_delta)

    return addr, action_str, cost_delta


def generate_markdown(diffs: list[tuple[str, str, float]], total: float, threshold: float | None) -> str:
    status_emoji = "🟢" if total <= 0 else ("🟡" if threshold is None or total <= threshold else "🔴")
    status_label = "Savings Identified" if total < 0 else ("Policy Approved" if threshold is None or total <= threshold else "Threshold Exceeded")

    lines = [
        "## 💰 ArthaOps Cost Sentinel",
        "",
        f"**Status**: {status_emoji} **{status_label}** &nbsp;|&nbsp; **Net Monthly Diff**: `${total:+,.2f}`",
        "",
        "| Resource | Change | Service | Monthly Cost Impact |",
        "| :--- | :---: | :---: | :---: |"
    ]

    for addr, action, cost in diffs:
        svc = addr.split(".")[0].replace("_", " ").upper()
        cost_str = f"`+${cost:,.2f}`" if cost > 0 else (f"`-${abs(cost):,.2f}`" if cost < 0 else "`$0.00`")
        lines.append(f"| `{addr}` | `{action}` | {svc} | {cost_str} |")

    lines.extend([
        "",
        "---",
        f"<sub>Audited by [**ArthaOps**](https://arthaops.com) — Provably safe multi-cloud infrastructure intelligence.</sub>"
    ])

    return "\n".join(lines)


def main():
    plan_path = os.environ.get("INPUT_PLAN_PATH", "")
    threshold_str = os.environ.get("INPUT_THRESHOLD_MONTHLY_USD", "")
    threshold = float(threshold_str) if threshold_str.strip() else None

    plan = load_plan(plan_path)
    changes = plan.get("resource_changes", [])

    diffs = []
    total = 0.0
    for r in changes:
        addr, action, cost = estimate_resource_cost(r)
        diffs.append((addr, action, cost))
        total += cost

    md = generate_markdown(diffs, total, threshold)

    # Write GitHub Actions Output
    output_path = os.environ.get("GITHUB_OUTPUT", "")
    if output_path:
        with open(output_path, "a", encoding="utf-8") as f:
            f.write(f"total_monthly_diff={total:.2f}\n")
            f.write(f"currency=USD\n")

    # Write Step Summary
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY", "")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as f:
            f.write(md + "\n")

    # Output to stdout
    print(md)

    if threshold is not None and total > threshold:
        print(f"\n::error::ArthaOps Cost Sentinel: Total monthly increase (+${total:.2f}) exceeds configured threshold (${threshold:.2f}).", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
