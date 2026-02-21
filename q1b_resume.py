import requests, subprocess, re, time, os, tempfile, json

chi6_pairs = []
with open('alltoric.spec') as f:
    for line in f:
        parts = line.split()
        if len(parts) >= 3 and int(parts[2]) == 6:
            chi6_pairs.append((int(parts[0]), int(parts[1])))
chi6_pairs = sorted(set(chi6_pairs))

# Partial results from first run
saved = {
    (16,13): [-1, 1, 1, 1],
    (17,14): [-1, 1, 1, 1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 2, 1, 1, 1, 1, 2, 2, 2, 2, 1],
    (18,15): [-1, 2, 2, 1, 2, 2, 1, 1, 4, 2, 2, 1, 2, 4, 1, 1, 2, 1, 2, 4, 1, 1, 1, 1, 1, 1, 1, 1, 2, 1, 2, 2, 2, 1, 1, 1, 2, 1, 1, 1, 1, 2, 1, 1, 1, 1, 2, 2, 1, 1, 1],
    (19,16): [-1, 8, 4, 2, 2, 2, 2, 1, 1, 1, 1, 4, 1, 1, 1, 1, 2, 4, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 2, 1, 2, 1, 2, 2, 2, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    (20,17): [-1, 4, 2, 2, 2, 2, 2, 1, 2, 1, 2, 2, 1, 1, 1, 1, 2, 1, 1, 2, 1, 1, 1, 1, 2, 2, 2, 2, 1, 1, 2, 2, 1, 1, 4, 1, 1, 1, 12, 2, 2, 1, 1, 2, 2, 2, 2, 1, 1, 1, 2],
}

url = 'http://quark.itp.tuwien.ac.at/cgi-bin/cy/cydata.cgi'
results = dict(saved)
failed = []

already_done = set(saved.keys())
remaining = [(h11,h21) for h11,h21 in chi6_pairs if (h11,h21) not in already_done]
print(f"Pairs to scan: {len(remaining)}")

for h11, h21 in remaining:
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
            # Validate: first line should be "dim npts" (two small ints)
            first = lines[0].split()
            if len(first) != 2 or not all(x.lstrip('-').isdigit() for x in first):
                continue
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
        results[(h11,h21)] = pair_syms
        max_sym = max((s for s in pair_syms if s > 0), default=0)
        flag = f" *** MAX={max_sym} ***" if max_sym > 1 else ""
        print(f"  ({h11},{h21}): valid={len(pair_syms)} max_sym={max_sym}{flag}")
    except Exception as e:
        failed.append((h11, h21, str(e)))
        print(f"  ({h11},{h21}): FAILED - {e}")
    time.sleep(0.3)

# Save results
with open('q1b_results.json', 'w') as f:
    json.dump({f"{k[0]},{k[1]}": v for k,v in results.items()}, f, indent=2)

print("\n=== Q1b SUMMARY ===")
print(f"Total pairs: {len(results)}, Failed: {len(failed)}")
print("\nNon-trivial GL(Z,4) symmetry (order > 1):")
for (h11,h21), syms in sorted(results.items()):
    valid = [s for s in syms if s > 0]
    if max(valid, default=0) > 1:
        max_s = max(valid)
        n_nontrivial = sum(1 for s in valid if s > 1)
        print(f"  (h11={h11}, h21={h21}): {n_nontrivial}/{len(valid)} polytopes non-trivial, max GL={max_s}")
