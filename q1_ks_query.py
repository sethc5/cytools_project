"""
Q1: Find all CY3 manifolds with chi = 6 (and chi = -6)
Direct query to Kreuzer-Skarke database via HTTP
No CYTools or Docker required.
"""

import requests
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE = "http://hep.itp.tuwien.ac.at/cgi-bin/cy/SearchHo.cgi"

def ks_session():
    s = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    s.mount("http://", HTTPAdapter(max_retries=retries))
    return s

def query(h11, h21, session, timeout=12):
    try:
        r = session.get(BASE, params={"h11": h11, "h12": h21}, timeout=timeout)
        text = r.text
        if "None found" in text or r.status_code != 200:
            return None
        # Extract the data line
        lines = [l.strip() for l in text.split("\n") if l.strip()
                 and "<" not in l and "Search" not in l]
        return lines if lines else None
    except Exception as e:
        return f"ERROR: {e}"

def search_chi(target_chi, max_h=300):
    """Search for all (h11,h21) pairs where 2*(h11-h21) == target_chi"""
    if target_chi % 2 != 0:
        print(f"chi={target_chi} is odd — not possible for CY3")
        return []
    diff = target_chi // 2  # h11 - h21 = diff
    found = []
    session = ks_session()
    print(f"\nSearching chi={target_chi} (h11-h21={diff}), scanning h21=0..{max_h}")
    for h21 in range(0, max_h + 1):
        h11 = h21 + diff
        if h11 < 0 or h11 > 500:
            continue
        result = query(h11, h21, session)
        if result and not str(result).startswith("ERROR"):
            print(f"  ✓ FOUND (h11={h11}, h21={h21}): {result}")
            found.append({"h11": h11, "h21": h21, "chi": target_chi, "data": result})
        elif str(result).startswith("ERROR"):
            print(f"  ! (h11={h11}, h21={h21}): {result}")
        time.sleep(0.1)
    print(f"  → {len(found)} polytopes found with chi={target_chi}")
    return found

if __name__ == "__main__":
    print("=" * 60)
    print("Q1: Kreuzer-Skarke Search for chi = ±6")
    print("=" * 60)

    results_pos = search_chi(+6, max_h=250)
    results_neg = search_chi(-6, max_h=250)

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    all_results = results_pos + results_neg
    if all_results:
        for r in all_results:
            print(f"  chi={r['chi']:+4d}  h11={r['h11']:3d}  h21={r['h21']:3d}  {r['data']}")
    else:
        print("  No chi=±6 polytopes found in KS database (h21 = 0..250)")
        print()
        print("  Interpretation: The framework's claim that N_gen = chi(CY6)/2 = 3")
        print("  uses chi(CY6) = 6, NOT chi(CY3) = 6.")
        print("  CY6 = CY3 x CY3 products: need chi(M1) * chi(M2) = 6.")
        print()
        print("  Integer factorizations of 6: 1×6, 2×3, 3×2, 6×1")
        print("  (and negatives: -1×-6, -2×-3, etc.)")
        print()
        print("  Checking chi(CY3) = 2 (h11-h21=1), chi(CY3) = 6 (h11-h21=3)...")
