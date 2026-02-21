# CYTools Project: Finding Calabi-Yau Manifolds with χ = ±6

A Jupyter notebook-based project for querying Calabi-Yau 3-fold polytopes from the Kreuzer-Skarke database.

## Setup

### Quick Start (Already Done)

The project has been initialized with:
- Python virtual environment (`venv/`)
- CYTools installed
- Jupyter Lab/Notebook support
- Starter notebook with example queries

### Using in VSCode

1. **Open the project in VSCode:**
   ```bash
   code /home/seth/dev/cytools_project
   ```

2. **Open the notebook:**
   - Open `cy_manifold_query.ipynb` in VSCode
   - VSCode will prompt you to select a kernel
   - Choose the Python interpreter in `./venv` (if not auto-detected, click "Select Another Kernel" → "Python Environments" → choose the venv path)

3. **Run cells:**
   - Click the play button on each cell to execute
   - Or use Shift+Enter to run and move to next cell

### Alternative: Launch Jupyter Lab

If you prefer the full Jupyter Lab interface:

```bash
cd /home/seth/dev/cytools_project
source venv/bin/activate
jupyter lab
```

Then open `cy_manifold_query.ipynb` from the file browser.

## Project Structure

```
cytools_project/
├── venv/                          # Python virtual environment
├── cy_manifold_query.ipynb        # Main notebook for Q1 queries
├── requirements.txt               # Package dependencies
└── README.md                      # This file
```

## Main Notebook: `cy_manifold_query.ipynb`

The notebook contains queries for finding Calabi-Yau 3-fold polytopes with specific Euler characteristics:

- **Query 1:** χ = 6 with simplest case (h₁₁=4, h₂₁=1)
- **Query 2:** χ = 6 with larger moduli spaces ((h₁₁=5, h₂₁=2), etc.)
- **Query 3:** χ = -6 with (h₁₁=1, h₂₁=4)

### Key Formula

For Calabi-Yau 3-folds, the Euler characteristic relates to Hodge numbers:

$$χ = 2(h_{11} - h_{21})$$

## Dependencies

- **cytools** - Computational algebraic geometry for polytopes and Calabi-Yau calculations
- **jupyter** - Interactive notebook environment
- **pandas** - Data manipulation and display
- **ipykernel** - Jupyter kernel for notebooks

See `requirements.txt` for exact versions.

## Documentation

- [CYTools Official Docs](https://cy.tools) - Full tutorials and API reference
- [Kreuzer-Skarke Database](http://hep.itp.tuwien.ac.at/~kreuzer/CY/) - Original polytope database

## Next Steps

1. Run the notebook cells to explore the database
2. Modify (h₁₁, h₂₁) pairs to search different topological regions
3. Extract polytope properties and analyze geometric invariants
4. Use results for further modeling or integration with Continue.dev

---

Created: February 2026
