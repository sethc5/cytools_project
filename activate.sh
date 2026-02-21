#!/bin/bash

# CYTools Project Activation Script
# Quick launch script for activating the virtual environment

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "🔬 CYTools Project Environment"
echo "=============================="
echo "Location: $SCRIPT_DIR"
echo ""
echo "Activating virtual environment..."
source "$SCRIPT_DIR/venv/bin/activate"

echo "✓ Environment activated!"
echo ""
echo "You can now:"
echo "  • Run: jupyter lab (to launch Jupyter)"
echo "  • Run: python -c \"from cytools import fetch_polytopes; print('Ready!')\" (test import)"
echo "  • Edit and run: cy_manifold_query.ipynb"
echo ""
