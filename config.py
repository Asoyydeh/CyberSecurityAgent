# ============================================================
#  AI DevTools - Configuration
# ============================================================

import os
from pathlib import Path

# ── Load .env jika ada ──────────────────────────────────────
_env_file = Path(__file__).parent / ".env"
if _env_file.exists():
    for line in _env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

# ── API Key (wajib diset di .env atau environment variable) ─
API_KEY = os.environ.get("AI_API_KEY", "")
if not API_KEY:
    print("[ERROR] AI_API_KEY belum diset!")
    print("Salin .env.example menjadi .env lalu isi API key Anda.")
    import sys; sys.exit(1)

BASE_URL = ""

APP_NAME  = "AI DevTools"
VERSION   = "1.0.0"
AUTHOR    = ""

# Default model (bisa diganti saat runtime)
DEFAULT_MODEL = ""

AVAILABLE_MODELS = {

}

# Warna tema
THEME = {
    "primary":   "#00d4ff",
    "secondary": "#7c3aed",
    "success":   "#22c55e",
    "warning":   "#f59e0b",
    "danger":    "#ef4444",
    "dim":       "#6b7280",
}
