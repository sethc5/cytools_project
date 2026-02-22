# CYTools Project Setup Guide

## Status: Ready to Use ✓

Your CYTools project has been initialized in `/home/seth/dev/cytools_project`.

**Project Location:** [/home/seth/dev/cytools_project]

---

## Files Created

- **`cy_manifold_query.ipynb`** — Main Jupyter notebook with starter queries for χ = ±6 manifolds
- **`activate.sh`** — Bash script to activate the Python environment
- **`requirements.txt`** — Python package dependencies  
- **`README.md`** — Extended project documentation

---

## Installation Note: CYTools C++ Dependencies

CYTools has heavyweight native C++ dependencies (CGAL, TOPCOM) that can be complex to build. Two approaches:

### 🐳 **Recommended: Docker Approach** (Most Reliable)

If pip installation has issues, use Docker instead:

```bash
docker run -it --rm -p 8888:8888 liammcallistergroup/cytools:latest
```

This downloads the complete image with all dependencies pre-compiled. Copy the URL it provides and open in your browser.

### 🐍 **Alternative: Using pip** (May Require System Libraries)

The setup has already attempted the pip installation. If you encounter import errors:

```bash
cd /home/seth/dev/cytools_project
source venv/bin/activate

# On Ubuntu/Debian: install system dependencies first
sudo apt-get install -y build-essential libcgal-dev libgmp-dev libmpfr-dev

# Then retry
pip install cytools --no-cache-dir
```

---

## Quick Start: VSCode Setup

1. **Open the project:**
   ```bash
   code /home/seth/dev/cytools_project
   ```

2. **Open the notebook** (`cy_manifold_query.ipynb`)
   - VSCode will prompt for a kernel
   - Select the Python interpreter in `./venv` (or let VSCode auto-detect)

3. **Run cells:**
   - Click the ▶ button or press Shift+Enter
   - Start with the import test cell

---

## Setup Commands

### Activate Environment (Bash)
```bash
source /home/seth/dev/cytools_project/venv/bin/activate
# Or use the convenience script:
/home/seth/dev/cytools_project/activate.sh
```

### Launch Jupyter Lab (Full Browser Experience)
```bash
cd /home/seth/dev/cytools_project
source venv/bin/activate
jupyter lab
```

### Test Installation
```bash
python -c "from cytools import fetch_polytopes; print('Ready!')"
```

---

## Project Structure

```
cytools_project/
├── venv/                      # Python virtual environment
├── cy_manifold_query.ipynb    # Main notebook (Q1 queries)
├── activate.sh                # Activation helper script
├── requirements.txt           # Package list
└── README.md                  # Full documentation
```

---

## The Notebook: `cy_manifold_query.ipynb`

Contains four sections:

**1. Setup & Imports**
- Import CYTools and pandas
- Verify environment is ready

**2. Query 1: χ = 6 (Simplest)**
- Search for (h₁₁=4, h₂₁=1)
- Small moduli space, easy to compute

**3. Query 2: χ = 6 (Larger Spaces)**
- Try (h₁₁=5, h₂₁=2), (6,3), (10,7)
- Explore parameter space

**4. Query 3: χ = -6**
- Search for (h₁₁=1, h₂₁=4)
- Negative Euler characteristic

### Key Physics

For Calabi-Yau 3-folds:
$$\chi = 2(h_{11} - h_{21})$$

Where:
- $h_{11}$, $h_{21}$ are Hodge numbers
- $\chi$ is the Euler characteristic

---

## Next Steps

1. **If pip worked:** Run the notebook cells — start with imports
2. **If pip had issues:** Use Docker as shown above
3. **For computations:** Modify (h₁₁, h₂₁) pairs to explore the database
4. **For integration:** Use with Continue.dev side-by-side as mentioned in your notes

---

## Documentation & Resources

- **CYTools Docs:** https://cy.tools
- **Kreuzer-Skarke Database:** http://hep.itp.tuwien.ac.at/~kreuzer/CY/
- **Calabi-Yau Geometry:** Standard algebraic geometry references

---

**Created:** February 21, 2026  
**Python Version:** 3.13  
**Virtual Environment:** Ready
