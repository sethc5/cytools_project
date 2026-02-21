import requests, subprocess, re, time, os, tempfile

# Load chi=6 pairs from local spec
chi6_pairs = []
with open('alltoric.spec') as f:
    for line in f:
        parts = line.split()
        if len(parts) >= 3 and int(parts[2]) == 6:
            chi6_pairs.append((int(parts[0]), int(parts[1])))

chi6_pairs = sorted(set(chi6_pairs))
print(f"Total chi=+6 (h11,h21) pairs: {len(chi6_pairs)}")

url = 'http://quark.itp.tuwien.ac.at/cgi-bin/cy/cydata.cgi'

results = []
failed = []

for h11, h21 in chi6_pairs:
    params = {'h11': h11, 'h12': h21, 'L': 50}
    try:
        r = requests.get(url, params=params, timeout=15)
        text = re.sub(r'<[^>]+>', '', r.text)
        # Find polytope blocks — each starts with "dim npoints"
        blocks = re.split(r'\n(?=\d+ \d+)', text.strip())
        pair_syms = []
        for block in blocks:
            lines = [l.strip() for l in block.strip().splitlines() if l.strip()]
            if not lines:
                continue
            # Write to temp file and run poly.x -S
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
                f.write('\n'.join(lines) + '\n')
                fname = f.name
            try:
                res = subprocess.run(['poly.x', '-S', fname],
                                     capture_output=True, text=True, timeout=5)
                out = res.stdout.strip()
                m = re.search(r'#GL\(Z,\d+\)-Symmetries=(\d+)', out)
                sym = int(m.group(1)) if m else -1
                pair_syms.append(sym)
            except subprocess.TimeoutExpired:
                pair_syms.append(-99)
            finally:
                os.unlink(fname)
        results.append((h11, h21, pair_syms))
        max_sym = max(pair_syms) if pair_syms else 0
        flag = " *** NONTRIVIAL ***" if max_sym > 1 else ""
        print(f"  ({h11},{h21}): {pair_syms}{flag}")
    except Exception as e:
        failed.append((h11, h21, str(e)))
        print(f"  ({h11},{h21}): FAILED - {e}")
    time.sleep(0.2)

print("\n=== SUMMARY ===")
print(f"Scanned: {len(results)}, Failed: {len(failed)}")
nontrivial = [(h11,h21,s) for h11,h21,s in results if max(s) > 1]
print(f"Non-trivial symmetry (GL > 1): {len(nontrivial)}")
for h11,h21,s in nontrivial:
    print(f"  (h11={h11}, h21={h21}): {s}")
if failed:
    print("Failed pairs:", failed)
