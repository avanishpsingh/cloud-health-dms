#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# demo_setup.sh  —  One-shot local demo setup for macOS / Linux
# Run:  bash demo_setup.sh
# ─────────────────────────────────────────────────────────────────────────────
set -e

PYTHON=${PYTHON:-python3}
PORT=${PORT:-8000}

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║   Cloud-Native Healthcare DMS  —  Local Demo Setup       ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# ── 1. Python check ───────────────────────────────────────────────────────────
echo "▶ Checking Python..."
$PYTHON --version

# ── 2. Virtual environment ────────────────────────────────────────────────────
if [ ! -d "venv" ]; then
    echo "▶ Creating virtual environment..."
    $PYTHON -m venv venv
else
    echo "▶ Virtual environment already exists — skipping creation."
fi

echo "▶ Activating virtual environment..."
source venv/bin/activate

# ── 3. Install dependencies ───────────────────────────────────────────────────
echo "▶ Installing dependencies..."
pip install -r requirements.txt -q

# ── 4. Seed the database ──────────────────────────────────────────────────────
echo "▶ Seeding demo database..."
python scripts/seed.py

# ── 5. Run tests (sanity check) ───────────────────────────────────────────────
echo "▶ Running test suite..."
python -m pytest tests/ -q

echo ""
echo "──────────────────────────────────────────────────────────"
echo "  ✅  Setup complete!"
echo ""
echo "  Start the server:"
echo "    source venv/bin/activate"
echo "    uvicorn app.main:app --reload --port $PORT"
echo ""
echo "  Then open in browser:"
echo "    http://localhost:$PORT/dashboard   ← Main UI"
echo "    http://localhost:$PORT/docs        ← Swagger API docs"
echo ""
echo "  Demo credentials:"
echo "    admin       / admin123   (full access)"
echo "    dr_sharma   / doctor123  (doctor — add medical records)"
echo "    reception1  / recep123   (receptionist — book appointments)"
echo "──────────────────────────────────────────────────────────"
echo ""
