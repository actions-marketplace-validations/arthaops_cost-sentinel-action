# cost-sentinel-action

[![CI](https://github.com/arthaops/cost-sentinel-action/actions/workflows/ci.yml/badge.svg)](https://github.com/arthaops/cost-sentinel-action/actions/workflows/ci.yml)
[![GitHub Marketplace](https://img.shields.io/badge/Marketplace-Cost%20Sentinel-blue?style=flat-square&logo=github)](https://github.com/marketplace/actions/arthaops-cost-sentinel)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg?style=flat-square)](LICENSE)
[![Security: Zero-Trust](https://img.shields.io/badge/Security-Zero--Trust-078d60?style=flat-square&logo=shield&logoColor=white)](https://arthaops.com)

Automated **Pull Request cloud infrastructure cost diffs** and budget policy gating for GitHub Actions, powered by [ArthaOps](https://arthaops.com).

Catch unexpected cloud cost spikes **before** Terraform merges to `main`.

---

## 📸 What it Looks Like

Whenever a PR modifies infrastructure, ArthaOps Cost Sentinel runs in CI and posts a clean, actionable breakdown directly to your pull request:

> ### 💰 ArthaOps Cost Sentinel
> **Status**: 🟡 **Policy Approved** &nbsp;|&nbsp; **Net Monthly Diff**: `+$268.20`
>
> | Resource | Change | Service | Monthly Cost Impact |
> | :--- | :---: | :---: | :---: |
> | `aws_instance.worker` | `+ create` | AWS INSTANCE | `+$248.20` |
> | `aws_ebs_volume.storage` | `~ update` | AWS EBS VOLUME | `+$20.00` |
>
> ---
> <sub>Audited by [**ArthaOps**](https://arthaops.com) — Provably safe multi-cloud infrastructure intelligence.</sub>

---

## 🚀 Quickstart

Add this step to your GitHub Actions workflow (e.g. `.github/workflows/terraform.yml`):

```yaml
name: Terraform Plan & Cost Check

on:
  pull_request:
    branches: [main]

jobs:
  cost-check:
    name: ArthaOps Cost Sentinel
    runs-on: ubuntu-latest
    permissions:
      contents: read
      pull-requests: write

    steps:
      - name: Checkout Code
        uses: actions/checkout@v4

      - name: Run ArthaOps Cost Sentinel
        uses: arthaops/cost-sentinel-action@v1
        with:
          plan_path: "tfplan.json"
          threshold_monthly_usd: "500" # Fails CI if net monthly cost increase > $500
          post_pr_comment: "true"
          github_token: ${{ secrets.GITHUB_TOKEN }}
```

---

## 📥 Inputs

| Input | Description | Default | Required |
| :--- | :--- | :---: | :---: |
| `plan_path` | Path to the JSON Terraform plan (e.g. generated via `terraform show -json`). If omitted, runs in demonstration audit mode. | `""` | no |
| `threshold_monthly_usd` | Maximum allowable net monthly cost increase in USD before failing the workflow gate. | `""` | no |
| `post_pr_comment` | Whether to post a summary table as a comment on the PR. | `"true"` | no |
| `github_token` | GitHub token for posting PR comments. | `${{ github.token }}` | no |

---

## 📤 Outputs

| Output | Description |
| :--- | :--- |
| `total_monthly_diff` | Calculated net monthly infrastructure cost difference in USD. |

---

## 🔒 Security & Privacy Invariants

1. **Zero Production Data Ingestion**: The action parses resource metadata and types from the Terraform execution plan only. It never reads production databases or application secrets.
2. **Deterministic Output**: All cost diff estimations execute locally in your runner environment.

---

## 📄 License

Apache License 2.0. See [LICENSE](LICENSE) for details.
