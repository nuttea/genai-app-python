# Datadog Code Security — Jenkins Pipeline Setup

This directory contains Jenkins declarative pipeline equivalents of the GitHub Actions workflow at `.github/workflows/datadog-code-security.yml`.

| Platform | File |
|---|---|
| Linux (Docker Engine) | `linux/Jenkinsfile` |
| Windows Server (Docker Desktop) | `windows/Jenkinsfile` |

---

## How it maps to GitHub Actions

| GitHub Actions job | Jenkins stage |
|---|---|
| `sast-quality-gate` → Run Datadog Static Analyzer | Stage 1: SAST Scan |
| `sast-quality-gate` → Evaluate Quality Gate | Stage 2: Quality Gate |
| `sast-quality-gate` → Upload SARIF to GitHub Code Scanning | Stage 3 (parallel): SARIF → GitHub Code Scanning |
| `datadog-sast` | Stage 4 (parallel): SAST → Datadog Upload |
| `datadog-sca` | Stage 5 (parallel): SCA → Datadog Upload |

The quality gate uses the same Python script (`.github/scripts/quality_gate.py`) on both platforms — no duplication of gate logic.

---

## Prerequisites

### Common (both platforms)

| Requirement | Notes |
|---|---|
| Jenkins 2.387+ | Declarative Pipeline support |
| [Pipeline plugin](https://plugins.jenkins.io/workflow-aggregator/) | Bundled in most distributions |
| [Credentials Binding plugin](https://plugins.jenkins.io/credentials-binding/) | For `withCredentials {}` |
| [Git plugin](https://plugins.jenkins.io/git/) | For `git remote get-url origin` |
| Python 3.9+ | Must be on the agent's `PATH` |
| Internet access from the agent | Pulls Docker images and downloads binaries from GitHub Releases |

### Linux agent

| Requirement | Notes |
|---|---|
| Docker Engine 20.10+ | `docker` CLI must be on `PATH` |
| Jenkins user in the `docker` group | `sudo usermod -aG docker jenkins && systemctl restart jenkins` |
| `curl` | For binary downloads and SARIF upload |
| `gzip`, `base64` (GNU coreutils) | For SARIF compression before GitHub upload |
| Agent label | Must match `linux && docker` (or update the `agent { label ... }` line) |

### Windows Server agent

| Requirement | Notes |
|---|---|
| Docker Desktop 4.x+ in **Linux containers** mode | The static analyzer is a Linux container |
| PowerShell 5.1+ | Ships with Windows Server 2016+; PowerShell 7 also works |
| Python 3 on `PATH` as `python` | Or change `python` to `py -3` in the Jenkinsfile |
| Agent label | Must match `windows && docker` (or update the `agent { label ... }` line) |

> **Docker Desktop Linux containers mode**: Open Docker Desktop → Settings → General → "Use the WSL 2 based engine" OR Settings → "Switch to Linux containers". The static analyzer image (`ghcr.io/datadog/datadog-static-analyzer`) is Linux-only.

---

## Credentials Setup

Create three **Secret Text** credentials in **Manage Jenkins → Credentials → (Global) → Add Credentials**:

| Credential ID | Value | Required for |
|---|---|---|
| `dd-api-key` | Datadog API key | SAST + SCA upload to Datadog |
| `dd-app-key` | Datadog Application key | SAST + SCA upload to Datadog |
| `github-token` | GitHub personal access token | SARIF upload to GitHub Code Scanning |

### Datadog API Key / App Key

1. Go to **Datadog → Organization Settings → API Keys** → Create key
2. Go to **Datadog → Organization Settings → Application Keys** → Create key (scope: `code_analysis`)

### GitHub Token

Required scopes: `security_events` (write), `repo` (read)

1. GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens
2. Select your repository, grant **Code scanning alerts** write access

---

## Pipeline Parameters

Each build exposes these parameters (configurable at build time via **Build with Parameters**):

| Parameter | Type | Default | Description |
|---|---|---|---|
| `DETECT_ONLY` | Boolean | `true` | `true` = virtual-fail mode (warnings, CI never fails); `false` = block mode (fails build on violations) |
| `GATE_SEVERITY_THRESHOLD` | Choice | `CRITICAL` | Lowest severity that triggers the gate: `CRITICAL`, `HIGH`, `MEDIUM`, or `LOW` |
| `UPLOAD_TO_DATADOG` | Boolean | `true` | Upload SARIF + SBOM to Datadog dashboard |
| `UPLOAD_SARIF_TO_GITHUB` | Boolean | `true` | Upload SARIF to GitHub Code Scanning |

### Equivalent to GitHub Actions repo variables

| GitHub `vars.*` | Jenkins parameter |
|---|---|
| `vars.DETECT_ONLY` | `DETECT_ONLY` |
| `vars.GATE_SEVERITY_THRESHOLD` | `GATE_SEVERITY_THRESHOLD` |

In Jenkins, these defaults live in the Jenkinsfile itself. To persist them across all builds without editing the file, use [Jenkins Configuration as Code](https://www.jenkins.io/projects/jcasc/) or a shared library with defaults.

---

## Creating the Jenkins Pipeline Job

1. **New Item** → Enter a name → Select **Pipeline** → OK
2. Under **Pipeline**:
   - Definition: `Pipeline script from SCM`
   - SCM: `Git`
   - Repository URL: your repo URL
   - Credentials: your Git credentials
   - Branch: `*/main`
   - Script Path:
     - Linux: `jenkins/linux/Jenkinsfile`
     - Windows: `jenkins/windows/Jenkinsfile`
3. **Save** → **Build with Parameters** on the first run (Jenkins auto-discovers parameters on first execution)

---

## Tool Versions (pinned)

| Tool | Version | Env var |
|---|---|---|
| `datadog-static-analyzer` container | `0.8.6` | `STATIC_ANALYZER_VERSION` |
| `datadog-ci` CLI | `2.45.1` | `DATADOG_CI_VERSION` |
| `datadog-sbom-generator` | `1.14.0` | `SBOM_GENERATOR_VERSION` |

To update a version, change the corresponding `environment {}` variable in the Jenkinsfile.

---

## Quality Gate Logic

The gate is implemented in `.github/scripts/quality_gate.py` (shared between GitHub Actions and Jenkins).

### Severity mapping (Datadog SARIF)

| Severity | Condition |
|---|---|
| CRITICAL | `DATADOG_CATEGORY:SECURITY` tag + SARIF level `error` or `none` |
| HIGH | `DATADOG_CATEGORY:SECURITY` + level `warning`; OR any category + level `error` |
| MEDIUM | level `warning` (non-security) |
| LOW | level `note` |
| INFO | level `none` (non-security) |

### Modes

**BLOCK mode** (`DETECT_ONLY=false`): exits non-zero when violations at or above the threshold exist. The Jenkins build is marked **FAILED**.

**DETECT_ONLY mode** (`DETECT_ONLY=true`): always exits 0. Violations are printed to the build log with a summary report. The Jenkins build is marked **SUCCESS** even if violations are found. Use this to raise visibility before enforcing hard gates.

---

## Troubleshooting

### `docker: command not found`

- Linux: Add the Jenkins user to the `docker` group and restart the service.
- Windows: Ensure Docker Desktop is running and `docker` is on the system `PATH`.

### `cannot exec in a stopped state: unknown`

Docker Desktop is not running or is in Windows containers mode. Switch to Linux containers mode.

### `SARIF not produced`

The static analyzer failed (e.g., OOM, missing `static-analysis.datadog.yml`). Check the Stage 1 console output. Ensure `static-analysis.datadog.yml` exists at the repository root.

### `403 Forbidden` on Datadog upload

- Verify `dd-api-key` and `dd-app-key` credential IDs match exactly.
- Ensure the API key has the `code_analysis` scope in Datadog.

### `403 Forbidden` on GitHub SARIF upload

- Verify `github-token` credential ID matches exactly.
- The token must have `security_events: write` scope on the target repository.
- GitHub Code Scanning must be enabled on the repository (Settings → Security → Code security → Code scanning).

### `python: command not found` (Windows)

Change `python` to `py -3` in `jenkins/windows/Jenkinsfile` Stage 2:

```groovy
powershell "py -3 .github/scripts/quality_gate.py ${flag}"
```

### Parallel upload stages skipped

The SAST/SCA upload stages only run on `main`/`master` branches or manual triggers (`UserIdCause`). Branch builds skip them intentionally — Datadog's platform tracks the default branch for dashboard accuracy.

### PowerShell execution policy (Windows)

If PowerShell scripts are blocked by execution policy, either:

1. Set policy on the agent: `Set-ExecutionPolicy RemoteSigned -Scope LocalMachine`
2. Or replace `powershell "..."` with `bat "..."` and rewrite commands as `cmd` equivalents.

---

## Directory Structure

```
jenkins/
├── linux/
│   └── Jenkinsfile       # Linux agent pipeline (Docker Engine + sh)
├── windows/
│   └── Jenkinsfile       # Windows agent pipeline (Docker Desktop + PowerShell)
└── README.md             # This file
```

The quality gate script lives alongside the GitHub Actions workflow so both pipelines share the same implementation:

```
.github/
├── workflows/
│   └── datadog-code-security.yml
└── scripts/
    └── quality_gate.py   # Used by both GitHub Actions and Jenkins
```
