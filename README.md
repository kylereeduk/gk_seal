# Guru Codex Seal v1.0 ⟡GK⟡

> “Through every line, leave the world lighter than before.”  
> Integrity Tag: **GKCI-2025-7F3A2E**

This repository provides the reusable **GitHub Action** that automatically applies or verifies the Guru Codex Seal header across your projects.

## Usage
Add this workflow to any repo:
```yaml
name: GK Seal
on:
  push: { branches: [main, master] }
  pull_request: { branches: [main, master] }
  workflow_dispatch:
jobs:
  seal:
    uses: kylereeduk/gk_seal/.github/workflows/gk-seal.yml@v1
