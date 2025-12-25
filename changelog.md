# AnimeFlix Change Log

## 🟢 Current Status: Stable (v3.1)
- **URL**: http://localhost:8501
- **State**: Running, Auto-Reload Safe
- **Browser**: Accessible (Brave/Chrome)

---

## 📅 Phase 3: Recovery & Stabilization (Current Session)
*The system was recovered from a "hot-reload death spiral" caused by external font imports.*

### 🔧 Core System
- **Revert**: Rolled back `app.py` code to match the stable `app_backup.py`.
- **Cache Clear**: Deleted `__pycache__` to remove stale bytecode.
- **Process Reset**: Hard-killed `streamlit.exe` to free the port.

### 🎨 UI/CSS Corrections
- **Font Fix**: Removed `@import url(...)` for Google Fonts (caused the crash).
- **Body Styling**: Reverted to safe system fonts (`-apple-system`, `sans-serif`) to ensure performance.
- **Logo Design**: Re-implemented the "AnimeFlix" logo using pure CSS transformations instead of a custom font file:
  - Font: `Arial Black` / `Impact`
  - Effect: `transform: skewX(-12deg)` (Dynamic Action Look)
  - Styling: `italic`, `900` weight, Gradient Overlay.

---

## 📅 Phase 2: Branding & Experience (Previous Session)
*Focus on transforming the generic Streamlit UI into "AnimeFlix".*

### 🖌️ Visual Overhaul
- **Dark Mode**: Enforced pure black (`#000000`) background.
- **Hero Section**: Added "Apple TV" style immersive hero banner with vignette.
- **Card Design**: Implemented hover-scaling cards with glassmorphism overlays.
- **Navigation**: Customized pills for "Browse Categories" vs "Search".

### ✨ Features
- **Dynamic Quotes**: Added anime quotes loader (`Power comes in response to a need...`).
- **Jikan API**: Integrated specialized fetch logic for high-res anime covers.

---

## 📅 Phase 1: Infrastructure & Performance (Initial Fixes)
*Focus on resolving the `numpy.MemoryError` and `DLL load failed` preventing startup.*

### 🧠 Memory Optimization (`anime_upgrade.py`)
- **Data Types**: Enforced `int32`/`float32` instead of default 64-bit types (50% RAM reduction).
- **Filtering**:
  - Dropped users with <50 ratings.
  - Removed incomplete rating entries immediately on load.
- **Algorithms**:
  - Switched from dense matrices to `scipy.sparse.csr_matrix`.
  - Implemented logic to "lazy load" heavy sklearn libraries (`NearestNeighbors`, `TfidfVectorizer`) only when needed.

### 🐛 Bug Fixes
- **Import Error**: Solved `ImportError: DLL load failed` by adjusting environment/paging file assumptions (handled via optimization).
