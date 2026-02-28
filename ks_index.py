#!/usr/bin/env python3
"""Extract and index χ=−6 polytopes from raw KS static files.

Reads the downloaded v{05..22}.gz files (indexed by n_vertices), filters
for χ=−6, and writes per-h11 files in KS format that CYTools can read
directly via `ct.read_polytopes(file, format='ks')`.

Usage:
    python3 ks_index.py                     # index all files
    python3 ks_index.py --status            # show index status
    python3 ks_index.py --h11-range 13 40   # only extract h11=13..40

Output:
    ks_raw/chi6/h11_13.txt, h11_14.txt, ... h11_119.txt
    ks_raw/chi6/index.json   (h11 → polytope count mapping)
"""
import argparse
import gzip
import json
import os
import re
import sys
import time

RAW_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ks_raw')
OUT_DIR = os.path.join(RAW_DIR, 'chi6')

# KS header pattern: "4 N  M:X N N:Y N H:h11,h21 [chi]"
HEADER_RE = re.compile(
    r'^(\d+)\s+(\d+)\s+M:(\d+)\s+(\d+)\s+N:(\d+)\s+(\d+)\s+H:(\d+),(\d+)\s+\[(-?\d+)\]'
)


def parse_and_filter(gz_path, chi_target=-6, h11_min=None, h11_max=None):
    """Parse a KS .gz file and yield (h11, block_text) for matching polytopes.

    block_text includes the header line and all coordinate lines.
    """
    with gzip.open(gz_path, 'rt', encoding='ascii', errors='replace') as f:
        current_block = []
        current_h11 = None
        current_chi = None

        for line in f:
            m = HEADER_RE.match(line)
            if m:
                # Emit previous block if it matched
                if current_block and current_chi == chi_target:
                    if (h11_min is None or current_h11 >= h11_min) and \
                       (h11_max is None or current_h11 <= h11_max):
                        yield current_h11, ''.join(current_block)

                # Start new block
                current_h11 = int(m.group(7))
                current_chi = int(m.group(9))
                current_block = [line]
            else:
                if current_block is not None:
                    current_block.append(line)

        # Emit last block
        if current_block and current_chi == chi_target:
            if (h11_min is None or current_h11 >= h11_min) and \
               (h11_max is None or current_h11 <= h11_max):
                yield current_h11, ''.join(current_block)


def index_all(h11_min=None, h11_max=None):
    """Extract χ=−6 polytopes from all v*.gz files into per-h11 text files."""
    os.makedirs(OUT_DIR, exist_ok=True)

    # Find all raw gz files
    gz_files = sorted([
        f for f in os.listdir(RAW_DIR)
        if f.startswith('v') and f.endswith('.gz')
    ])

    if not gz_files:
        print(f"No .gz files found in {RAW_DIR}")
        return

    # Collect polytopes per h11
    h11_counts = {}
    h11_files = {}  # h11 -> open file handle
    total = 0
    t0 = time.time()

    for gz_name in gz_files:
        gz_path = os.path.join(RAW_DIR, gz_name)
        gz_size_mb = os.path.getsize(gz_path) / 1024 / 1024
        print(f"  {gz_name} ({gz_size_mb:.0f} MB)...", end='', flush=True)
        n_found = 0

        for h11, block in parse_and_filter(gz_path, chi_target=-6,
                                            h11_min=h11_min, h11_max=h11_max):
            if h11 not in h11_files:
                out_path = os.path.join(OUT_DIR, f'h11_{h11:03d}.txt')
                h11_files[h11] = open(out_path, 'w')
                h11_counts[h11] = 0

            h11_files[h11].write(block)
            h11_counts[h11] += 1
            n_found += 1
            total += 1

        elapsed = time.time() - t0
        print(f" {n_found:,} χ=−6 ({total:,} cumulative, {elapsed:.0f}s)")

    # Close all files
    for fh in h11_files.values():
        fh.close()

    # Write index
    index_path = os.path.join(OUT_DIR, 'index.json')
    index_data = {
        'chi': -6,
        'h11_range': [min(h11_counts.keys()), max(h11_counts.keys())],
        'total_polytopes': total,
        'h11_counts': {str(k): v for k, v in sorted(h11_counts.items())},
        'indexed_at': time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime()),
        'source_files': gz_files,
    }
    with open(index_path, 'w') as f:
        json.dump(index_data, f, indent=2)

    elapsed = time.time() - t0
    print(f"\nDone: {total:,} χ=−6 polytopes across {len(h11_counts)} h11 levels")
    print(f"  Time: {elapsed:.0f}s")
    print(f"  Output: {OUT_DIR}/h11_*.txt")
    print(f"  Index: {index_path}")

    # Show h11 distribution
    print(f"\n  {'h11':>5}  {'count':>8}")
    print(f"  {'---':>5}  {'---':>8}")
    for h11 in sorted(h11_counts.keys()):
        print(f"  {h11:5d}  {h11_counts[h11]:8,}")


def show_status():
    """Show index status."""
    index_path = os.path.join(OUT_DIR, 'index.json')
    if not os.path.exists(index_path):
        print("No index found. Run: python3 ks_index.py")
        return

    with open(index_path) as f:
        idx = json.load(f)

    print(f"χ=−6 KS Index")
    print(f"  Total: {idx['total_polytopes']:,} polytopes")
    print(f"  h11 range: {idx['h11_range'][0]}–{idx['h11_range'][1]}")
    print(f"  Levels: {len(idx['h11_counts'])}")
    print(f"  Indexed: {idx['indexed_at']}")
    print()

    # Check files exist
    missing = 0
    total_size = 0
    for h11_str, count in sorted(idx['h11_counts'].items(), key=lambda x: int(x[0])):
        h11 = int(h11_str)
        fpath = os.path.join(OUT_DIR, f'h11_{h11:03d}.txt')
        if os.path.exists(fpath):
            sz = os.path.getsize(fpath) / 1024 / 1024
            total_size += sz
            print(f"  h11={h11:3d}: {count:>8,} polytopes  ({sz:.1f} MB)")
        else:
            print(f"  h11={h11:3d}: {count:>8,} polytopes  [MISSING]")
            missing += 1

    print(f"\n  Total size: {total_size:.1f} MB")
    if missing:
        print(f"  WARNING: {missing} files missing!")


def load_h11_polytopes(h11, limit=None):
    """Load χ=−6 polytopes for a given h11 from the local index.

    Returns a generator of CYTools Polytope objects.
    This is the function the pipeline should call instead of
    ct.fetch_polytopes().
    """
    import cytools as ct

    fpath = os.path.join(OUT_DIR, f'h11_{h11:03d}.txt')
    if not os.path.exists(fpath):
        raise FileNotFoundError(
            f"No indexed file for h11={h11}. Run: python3 ks_index.py")

    return ct.read_polytopes(fpath, format='ks', as_list=True, limit=limit)


def main():
    parser = argparse.ArgumentParser(
        description='Index χ=−6 polytopes from raw KS files')
    parser.add_argument('--status', action='store_true',
                        help='Show index status')
    parser.add_argument('--h11-range', type=int, nargs=2, default=None,
                        metavar=('MIN', 'MAX'),
                        help='Only extract h11 in [MIN, MAX]')
    args = parser.parse_args()

    if args.status:
        show_status()
        return

    h11_min = args.h11_range[0] if args.h11_range else None
    h11_max = args.h11_range[1] if args.h11_range else None

    print(f"KS χ=−6 Indexer")
    print(f"  Raw dir: {RAW_DIR}")
    print(f"  Output:  {OUT_DIR}")
    if h11_min is not None:
        print(f"  h11 range: {h11_min}–{h11_max}")
    print()

    index_all(h11_min=h11_min, h11_max=h11_max)


if __name__ == '__main__':
    main()
