import requests, subprocess, re, time, os, tempfile, json

chi6_pairs = []
with open('alltoric.spec') as f:
    for line in f:
        parts = line.split()
        if len(parts) >= 3 and int(parts[2]) == 6:
            chi6_pairs.append((int(parts[0]), int(parts[1])))
chi6_pairs = sorted(set(chi6_pairs))
print(f"Total chi=+6 pairs: {len(chi6_pairs)}")

url = 'http://quark.itp.tuwien.ac.at/cgi-bin/cy/cydata.cgi'
results = {}
failed = []

for h11, h21 in chi6_pairs:
    params = {'h11': h11, 'h12': h21, 'L': 50}
    try:
        r = requests.get(url, params=params, timeout=20)
        text = re.sub(r'<[^>]+>', '', r.text)
        blocks = re.split(r'\n(?=\d+ \d+)', text.strip())
        pair_syms = []
        for block in blocks:
            lines = [l.strip() for l in block.strip().splitlines() if l.strip()]
            if not lines:
                continue
            first_parts = lines[0].split()
            # Need at least two integer tokens at start
            if len(first_parts) < 2:
                continue
            try:
                dim = int(first_parts[0])
                npts = int(first_parts[1])
            except ValueError:
                continue
            # Normalize header line to just "dim npts"
            lines[0] = f"{dim} {npts}"
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write('\n'.join(lines) + '\n')
                fname = f.name
            try:
                res = subprocess.run(['poly.x', '-S', fname],
                                     capture_output=True, text=True, timeout=5)
                out = res.stdout.strip()
                m = re.search(r'#GL\(Z,\d+\)-Symmetries=(\d+)', out)
                sym = int(m.group(1)) if m else -1
                if sym >= 0:
                    pair_syms.append(sym)
            except subprocess.TimeoutExpired:
                pair_syms.append(-99)
            finally:
                os.unlink(fname)
        results[(h11,h21)] = pair_syms
        max_sym = max(pair_syms, default=0)
        flag = f" *** MAX={max_sym} ***" if max_sym > 1 else ""
        print(f"  ({h11},{h21}): n={len(pair_syms)} max={max_sym}{flag}")
    except Exception as e:
        failed.append((h11, h21, str(e)))
        print(f"  ({h11},{h21}): FAILED - {e}")
    time.sleep(0.25)

with open('q1b_results_full.json', 'w') as f:
    json.dump({f"{k[0]},{k[1]}": v for k,v in results.items()}, f, indent=2)

print("\n=== Q1b FINAL SUMMARY ===")
print(f"Pairs scanned: {len(results)}, Failed: {len(failed)}")
print("\nNon-trivial GL(Z,4) symmetry (max > 1):")
for (h11,h21), syms in sorted(results.items()):
    valid = [s for s in syms if s >= 0]
    mx = max(valid, default=0)
    if mx > 1:
        n_nt = sum(1 for s in valid if s > 1)
        print(f"  (h11={h11}, h21={h21}): {n_nt}/{len(valid)} non-trivial, max GL={mx}")
print("\nAll trivial (max=1):")
count_trivial = sum(1 for syms in results.values() if max((s for s in syms if s>=0), default=0) <= 1)
print(f"  {count_trivial} pairs all-trivial")
