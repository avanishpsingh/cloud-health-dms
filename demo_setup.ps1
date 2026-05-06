# ─────────────────────────────────────────────────────────────────────────────
# demo_setup.ps1  —  One-shot local demo setup for Windows PowerShell
# Run:  .\demo_setup.ps1
# ─────────────────────────────────────────────────────────────────────────────

$ErrorActionPreference = "Stop"
$PORT = 8000

Write-Host ""
Write-Host "╔══════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║   Cloud-Native Healthcare DMS  —  Local Demo Setup       ║" -ForegroundColor Cyan
Write-Host "╚══════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

# ── 1. Python check ───────────────────────────────────────────────────────────
Write-Host "▶ Checking Python..." -ForegroundColor Yellow
python --version

# ── 2. Virtual environment ────────────────────────────────────────────────────
if (-not (Test-Path "venv")) {
    Write-Host "▶ Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
} else {
    Write-Host "▶ Virtual environment already exists — skipping creation." -ForegroundColor Green
}

Write-Host "▶ Activating virtual environment..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# ── 3. Install dependencies ───────────────────────────────────────────────────
Write-Host "▶ Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt -q

# ── 4. Seed the database ──────────────────────────────────────────────────────
Write-Host "▶ Seeding demo database..." -ForegroundColor Yellow
python scripts/seed.py

# ── 5. Run tests (sanity check) ───────────────────────────────────────────────
Write-Host "▶ Running test suite..." -ForegroundColor Yellow
python -m pytest tests/ -q

Write-Host ""
Write-Host "──────────────────────────────────────────────────────────" -ForegroundColor Cyan
Write-Host "  Setup complete!" -ForegroundColor Green
Write-Host ""
Write-Host "  Start the server:"
Write-Host "    .\venv\Scripts\Activate.ps1"
Write-Host "    uvicorn app.main:app --reload --port $PORT"
Write-Host ""
Write-Host "  Then open in browser:"
Write-Host "    http://localhost:$PORT/dashboard   <- Main UI"
Write-Host "    http://localhost:$PORT/docs        <- Swagger API docs"
Write-Host ""
Write-Host "  Demo credentials:"
Write-Host "    admin       / admin123   (full access)"
Write-Host "    dr_sharma   / doctor123  (doctor — add medical records)"
Write-Host "    reception1  / recep123   (receptionist — book appointments)"
Write-Host "──────────────────────────────────────────────────────────" -ForegroundColor Cyan
Write-Host ""
