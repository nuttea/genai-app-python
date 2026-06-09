# Datadog Code Security — Jenkins Pipeline Setup

This directory contains Jenkins declarative pipeline equivalents of the GitHub Actions workflow at `.github/workflows/datadog-code-security.yml`.

**Official Datadog docs used as the basis for these pipelines:**
- SAST Generic CI: https://docs.datadoghq.com/security/code_security/static_analysis/setup/generic_ci_providers/
- SCA Generic CI: https://docs.datadoghq.com/security/code_security/software_composition_analysis/setup_static/generic_ci_providers/

| Platform | File |
|---|---|
| Linux | `linux/Jenkinsfile` |
| Windows Server | `windows/Jenkinsfile` |

> **No Docker required.** Both pipelines follow Datadog's Generic CI approach: they download the native `datadog-static-analyzer` binary for the agent's platform and install `datadog-ci` via npm.

---

## How it maps to GitHub Actions

| GitHub Actions job | Jenkins stage |
|---|---|
| `sast-quality-gate` → Run Datadog Static Analyzer | Stage 1: SAST Scan (native binary) |
| `sast-quality-gate` → Evaluate Quality Gate | Stage 2: Quality Gate (same Python script) |
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
| Python 3.9+ | On the agent's `PATH` |
| **Node.js 14+** | Required by Datadog's official guide; `npm` is used to install `datadog-ci` |
| Internet access from the agent | Downloads binaries from GitHub Releases and npm registry |

---

### Node.js Installation Guide

`datadog-ci` is installed per build via `npm install -g @datadog/datadog-ci`. Node.js must be present on the Jenkins agent before the pipeline runs.

#### Linux agent — Node.js setup

**Option A: via NodeSource (recommended for LTS)**

```bash
# As root or sudo on the Jenkins agent
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get install -y nodejs
# Verify
node --version && npm --version
```

For RPM-based systems (RHEL, Amazon Linux, CentOS):

```bash
curl -fsSL https://rpm.nodesource.com/setup_20.x | bash -
yum install -y nodejs
```

**Option B: via nvm (per-user, no root required)**

```bash
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.7/install.sh | bash
source ~/.bashrc
nvm install 20
nvm use 20
node --version && npm --version
```

> If Jenkins runs as a service user, add `source ~/.bashrc` (or the nvm init lines) to the Jenkins user's shell profile so `node` is on `PATH` in non-interactive shells.

**Option C: Jenkins NodeJS Plugin (managed by Jenkins)**

1. Install the [NodeJS plugin](https://plugins.jenkins.io/nodejs/)
2. Manage Jenkins → Tools → NodeJS installations → Add NodeJS → name it (e.g. `NodeJS-20`)
3. Add this block to the Jenkinsfile `tools {}` section:

```groovy
tools {
    nodejs 'NodeJS-20'
}
```

#### Windows Server agent — Node.js setup

**Option A: MSI installer (recommended)**

1. Download the LTS installer from https://nodejs.org/en/download
2. Run the `.msi` installer as Administrator — it adds `node` and `npm` to the system `PATH`
3. Verify in a new PowerShell session:

```powershell
node --version
npm --version
```

**Option B: winget**

```powershell
# Run in an elevated PowerShell session
winget install OpenJS.NodeJS.LTS
# Restart PowerShell / log out-in for PATH to take effect
node --version && npm --version
```

**Option C: Chocolatey**

```powershell
choco install nodejs-lts -y
node --version && npm --version
```

> After installation, restart the Jenkins Windows service so the agent picks up the updated `PATH`:
> ```powershell
> Restart-Service -Name Jenkins
> ```

---

### Linux agent — additional requirements

| Requirement | Notes |
|---|---|
| `curl` | Binary downloads |
| `unzip` | Extracting static analyzer zip |
| `gzip`, `base64` (GNU coreutils) | SARIF compression for GitHub upload |
| Agent label | Must match `linux` (or update `agent { label ... }` in the Jenkinsfile) |

### Windows Server agent — additional requirements

| Requirement | Notes |
|---|---|
| PowerShell 5.1+ | Ships with Windows Server 2016+; PowerShell 7 also works |
| Python 3.9+ on PATH as `python` | Or change to `py -3` in Stage 2 |
| Agent label | Must match `windows` (or update `agent { label ... }` in the Jenkinsfile) |

---

## Credentials Setup

Create three **Secret Text** credentials in **Manage Jenkins → Credentials → (Global) → Add Credentials**:

| Credential ID | Value | Required for |
|---|---|---|
| `dd-api-key` | Datadog API key | SAST + SCA upload to Datadog |
| `dd-app-key` | Datadog Application key (`code_analysis_read` scope) | SAST + SCA upload to Datadog |
| `github-token` | GitHub personal access token | SARIF upload to GitHub Code Scanning |

### Datadog API Key / App Key

1. **Datadog → Organization Settings → API Keys** → Create key
2. **Datadog → Organization Settings → Application Keys** → Create key, grant `code_analysis_read` scope

### GitHub Token

Required scopes: `security_events` (write), `repo` (read)

1. GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens
2. Select your repository → Code scanning alerts: **Write**

---

## Pipeline Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `DETECT_ONLY` | Boolean | `true` | `true` = virtual-fail mode (warnings only, CI passes); `false` = block mode (fails build on violations) |
| `GATE_SEVERITY_THRESHOLD` | Choice | `CRITICAL` | Lowest severity that triggers the gate: `CRITICAL`, `HIGH`, `MEDIUM`, or `LOW` |
| `UPLOAD_TO_DATADOG` | Boolean | `true` | Upload SARIF + SBOM to Datadog |
| `UPLOAD_SARIF_TO_GITHUB` | Boolean | `true` | Upload SARIF to GitHub Code Scanning |

### Equivalent to GitHub Actions repo variables

| GitHub `vars.*` | Jenkins parameter |
|---|---|
| `vars.DETECT_ONLY` | `DETECT_ONLY` |
| `vars.GATE_SEVERITY_THRESHOLD` | `GATE_SEVERITY_THRESHOLD` |

---

## Tool Versions (pinned in `environment {}`)

| Tool | Version | Env var |
|---|---|---|
| `datadog-static-analyzer` | `0.8.6` | `STATIC_ANALYZER_VERSION` |
| `@datadog/datadog-ci` (npm) | `2.45.1` | `DATADOG_CI_VERSION` |
| `datadog-sbom-generator` | `1.14.0` | `SBOM_GENERATOR_VERSION` |

Static analyzer binary selected per platform:

| Platform | Binary |
|---|---|
| Linux x86_64 | `datadog-static-analyzer-x86_64-unknown-linux-gnu.zip` |
| Windows x86_64 | `datadog-static-analyzer-x86_64-pc-windows-msvc.zip` |

All binaries are downloaded from the [datadog-static-analyzer GitHub Releases](https://github.com/DataDog/datadog-static-analyzer/releases) pinned to the exact version tag.

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
3. **Save** → **Build with Parameters** on the first run (Jenkins discovers parameters on first execution)

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

**BLOCK mode** (`DETECT_ONLY=false`): exits non-zero on violations at or above threshold. Jenkins build is **FAILED**.

**DETECT_ONLY mode** (`DETECT_ONLY=true`): always exits 0. Violations are printed to the build log. Build is **SUCCESS** even with findings. Use this to raise visibility before enforcing hard gates.

---

## Supported CI Triggers

Per the [Datadog docs](https://docs.datadoghq.com/security/code_security/static_analysis/setup/generic_ci_providers/):

> Running a Datadog Static Code Analysis job as part of your CI/CD pipeline only supports workflows triggered by **direct code commits** (for example, a `push` event). Other types of triggers, such as pull, merge, or review request events are not supported.

The upload stages (SAST → Datadog, SCA → Datadog) are therefore gated to `main`/`master` branch builds and manual triggers (`UserIdCause`) via the `when {}` condition.

---

## Troubleshooting

### `npm: command not found` / `'npm' is not recognized`

Node.js is not installed or not on `PATH`. See the **Node.js Installation Guide** section above.

### `node` found but `datadog-ci` not found after `npm install -g`

The global npm bin directory is not on `PATH`. On Linux:

```bash
npm config get prefix
# e.g. /usr/local → binaries land in /usr/local/bin
# ensure /usr/local/bin is in PATH for the jenkins user
```

On Windows, the global bin directory is usually `%APPDATA%\npm`. Add it to `PATH` system-wide and restart the Jenkins service.

### `SARIF not produced`

The static analyzer failed. Possible causes:
- Missing `static-analysis.datadog.yml` at the repository root
- Analyzer binary not executable (Linux) — the pipeline runs `chmod +x` automatically
- OOM on the agent — reduce concurrent stages or increase agent memory

### `403 Forbidden` on Datadog upload

- Verify the `dd-api-key` and `dd-app-key` credential IDs match exactly.
- Ensure the Application key has the `code_analysis_read` scope in Datadog.

### `403 Forbidden` on GitHub SARIF upload

- Verify the `github-token` credential ID matches exactly.
- Token must have `security_events: write` scope.
- GitHub Code Scanning must be enabled on the repository (Settings → Security → Code security → Code scanning).

### `python: command not found` (Windows)

Change `python` to `py -3` in `jenkins/windows/Jenkinsfile` Stage 2:

```groovy
powershell "py -3 .github/scripts/quality_gate.py ${flag}"
```

### Parallel upload stages always skipped

The SAST/SCA upload stages only run on `main`/`master` or manual triggers. Feature branch builds skip them by design — Datadog's platform tracks the default branch for dashboard accuracy.

### PowerShell execution policy (Windows)

If PowerShell scripts are blocked:

```powershell
# Run in an elevated PowerShell session on the agent
Set-ExecutionPolicy RemoteSigned -Scope LocalMachine
```

---

## Directory Structure

```
jenkins/
├── linux/
│   └── Jenkinsfile       # Linux agent pipeline (native binary + npm)
├── windows/
│   └── Jenkinsfile       # Windows agent pipeline (native binary + npm + PowerShell)
└── README.md             # This file

.github/
├── workflows/
│   └── datadog-code-security.yml
└── scripts/
    └── quality_gate.py   # Shared quality gate — used by GitHub Actions and Jenkins
```
