#!/bin/bash
cd /workspaces/cytools_project
mkdir -p receipts results
echo "Starting pipeline_v2.py h17 at $(date)"
echo "Host: $(hostname), CPUs: $(nproc), Memory: $(free -h | awk '/Mem:/{print $2}')"
python3 pipeline_v2.py --h11 17 -w 3 --top 0
echo ""
echo "Pipeline finished at $(date)"
echo ""
echo "=== Receipt files ==="
ls -la receipts/
