# Setup — What to Install on a Fresh Device

Everything below is native Windows. No WSL2, no Docker, no compilers.

## Required (manual installs — only 3 things)

| Tool | Why | Get it |
|---|---|---|
| **Git for Windows** | Version control; includes Git Bash | <https://git-scm.com/download/win> |
| **Miniforge** (conda) | Manages the Python scientific environment. Required because **Psi4 only ships via conda-forge** — a plain `pip install` cannot provide it. Do NOT use full Anaconda; Miniforge defaults to conda-forge, which is exactly what we need | <https://conda-forge.org/download/> |
| **Node.js LTS** | Builds the TypeScript/WebGL browser frontend (`npm`) | <https://nodejs.org/> (choose LTS) |

A modern browser with WebGL2 is also required — Edge (preinstalled on Windows 11) or Chrome both work.

## Everything else installs itself

You do **not** manually install Python, NumPy, SciPy, FastAPI, pytest, Psi4, or (later) QuTiP.
They are pinned in the project's `environment.yml` and created in one step:

```powershell
conda env create -f environment.yml   # one command, one isolated env
conda activate atom_sim
```

Frontend dependencies likewise come from `package.json`:

```powershell
npm install
```

> A system-wide Python (e.g., 3.14 from python.org) can coexist harmlessly — the
> project never uses it. The conda env pins its own Python version compatible
> with Psi4.

## Optional (nice to have)

| Tool | Why |
|---|---|
| **VS Code** | Recommended editor — <https://code.visualstudio.com/> |
| **GitHub CLI (`gh`)** | Easier repo publishing, PRs, CI checks from the terminal — <https://cli.github.com/> |

## Status of the current dev machine (checked 2026-07-04)

- ✅ Git 2.54, VS Code, system Python 3.14
- ❌ **Miniforge — install this**
- ❌ **Node.js LTS — install this**
- ⬜ GitHub CLI — optional, install when we publish to GitHub

## Phase 0 verification step

After installing Miniforge, the first project task verifies that `psi4` installs
cleanly from conda-forge on Windows (`conda install -c conda-forge psi4` inside the
env). If the Windows build turns out to be broken/unavailable, the spec's fallback
applies (custom solvers stay primary; Psi4 cross-checks deferred) — see
`docs/superpowers/specs/2026-07-04-atom-sim-requirements-design.md`, open item 5.
