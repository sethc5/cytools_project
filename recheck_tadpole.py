"""
Corrected D3-tadpole check for champion monad LP candidates.

Bug in original: linear formula always cancels (c1(B)=c1(C)), giving n_D3=66 constant.
Correct formula: ch2(O(beta))_k = (1/2) kappa_{kab} beta^a beta^b  (quadratic)
With c1(V)=0: c2(V) = -ch2(V) = -(ch2(B) - ch2(C))
"""
import sys, time, json
import numpy as np

sys.path.insert(0, "/workspaces/cytools_project/v6")
sys.path.insert(0, "/workspaces/cytools_project")

H11      = 26
POLY_IDX = 11670
RESULTS_IN  = "/workspaces/cytools_project/v6/results/champion_monads_lp.json"
RESULTS_OUT = "/workspaces/cytools_project/v6/results/champion_monads_lp_rechk.json"
REPORT_OUT  = "/workspaces/cytools_project/v6/results/champion_monads_lp_rechk.txt"
LOG_OUT     = "/workspaces/cytools_project/v6/results/recheck_tadpole.log"


def build_kappa_tensor(intnums, h11_eff):
    K = np.zeros((h11_eff, h11_eff, h11_eff), dtype=float)
    for (a, b, c), v in intnums.items():
        if 0 <= a < h11_eff and 0 <= b < h11_eff and 0 <= c < h11_eff:
            for aa, bb, cc in ((a, b, c), (a, c, b), (b, a, c),
                               (b, c, a), (c, a, b), (c, b, a)):
                K[aa, bb, cc] = v
    return K


def check_tadpole_correct(Bs, Cs, c2_X, K):
    """
    Correct D3-tadpole.
    ch2(O(beta))_k = (1/2) kappa_{kab} beta^a beta^b  [quadratic]
    ch2(B)_k = sum_i ch2(O(beta^i))_k
    c2(V)_k  = -(ch2(B)_k - ch2(C)_k)  [since c1(V)=0]
    tadpole_ok iff c2(V)_k <= c2(TX)_k for all k
    n_D3 = sum_k (c2(TX)_k - c2(V)_k)
    """
    Bs = np.asarray(Bs, dtype=float)
    Cs = np.asarray(Cs, dtype=float)
    ch2_B = 0.5 * np.einsum("kab,ia,ib->k", K, Bs, Bs)
    ch2_C = 0.5 * np.einsum("kab,ja,jb->k", K, Cs, Cs)
    ch2_V = ch2_B - ch2_C
    c2_V  = -ch2_V
    tadpole_ok = bool(np.all(c2_V <= c2_X + 0.5))
    n_D3 = float(np.sum(c2_X - c2_V))
    return tadpole_ok, n_D3, float(c2_V.min()), float(c2_V.max())


def load_cy():
    from cytools.config import enable_experimental_features
    enable_experimental_features()
    from ks_index import load_h11_polytopes
    print("Loading h%d/P%d..." % (H11, POLY_IDX), flush=True)
    t0 = time.time()
    polys = load_h11_polytopes(H11, limit=POLY_IDX + 1)
    p     = polys[POLY_IDX]
    tri   = p.triangulate()
    cy    = tri.get_cy()
    c2    = np.array(cy.second_chern_class(in_basis=True), dtype=float)
    intnums = dict(cy.intersection_numbers(in_basis=True))
    h11_eff = len(c2)
    K = build_kappa_tensor(intnums, h11_eff)
    print("  h11_eff=%d, |c2|=[%.0f,%.0f], done in %.1fs" % (
        h11_eff, c2.min(), c2.max(), time.time()-t0), flush=True)
    return c2, K, h11_eff


def main():
    c2_X, K, h11_eff = load_cy()

    with open(RESULTS_IN) as f:
        data = json.load(f)
    candidates = data["candidates"]
    print("Loaded %d slope-feasible candidates" % len(candidates), flush=True)

    valid = [c for c in candidates if c.get("vol_J", -1) > 0]
    print("vol>0 candidates: %d" % len(valid), flush=True)

    results = []
    n_ok = 0
    for i, c in enumerate(valid):
        Bs = np.array(c["B"], dtype=float)
        Cs = np.array(c["C"], dtype=float)
        ok, n_D3, c2v_min, c2v_max = check_tadpole_correct(Bs, Cs, c2_X, K)
        rec = dict(c)
        rec["tadpole_ok_v2"]   = ok
        rec["n_D3_correct"]    = n_D3
        rec["c2V_min_correct"] = c2v_min
        rec["c2V_max_correct"] = c2v_max
        results.append(rec)
        if ok:
            n_ok += 1
            print("  [TADPOLE OK] #%d: config=%s chi=%s margin=%.4f vol=%.3f "
                  "n_D3=%.1f c2V=[%.1f,%.1f]" % (
                      i+1, c["config"], c["chi_V"], c["slope_margin"], c["vol_J"],
                      n_D3, c2v_min, c2v_max), flush=True)
        elif i % 50 == 0:
            print("  [%d/%d] n_D3=%.1f c2V=[%.1f,%.1f] ok=%s" % (
                i+1, len(valid), n_D3, c2v_min, c2v_max, ok), flush=True)

    sep = "=" * 60
    print("\n" + sep)
    print("CORRECTED TADPOLE RESULTS")
    print("  vol>0 candidates checked: %d" % len(valid))
    print("  Tadpole OK (corrected):   %d" % n_ok)

    n_D3s = [r["n_D3_correct"] for r in results]
    c2v_maxs = [r["c2V_max_correct"] for r in results]
    print("  n_D3 range: [%.1f, %.1f], mean=%.1f" % (
        min(n_D3s), max(n_D3s), float(np.mean(n_D3s))))
    print("  c2V_max range: [%.2f, %.2f]" % (min(c2v_maxs), max(c2v_maxs)))
    print(sep)

    out_data = dict(data)
    out_data["candidates_valid"] = results
    out_data["n_tadpole_ok_v2"] = n_ok
    out_data["recheck_note"] = ("Corrected ch2 formula: (1/2)*kappa_{kab}*beta^a*beta^b; "
                                "original was linear (bug).")
    with open(RESULTS_OUT, "w") as f:
        json.dump(out_data, f, indent=2)
    print("Saved JSON: " + RESULTS_OUT)

    with open(REPORT_OUT, "w") as f:
        f.write("Champion Monad LP -- Corrected D3-Tadpole Re-check\n")
        f.write(sep + "\n")
        f.write("vol>0 candidates: %d\n" % len(valid))
        f.write("Tadpole OK (corrected): %d\n\n" % n_ok)
        ok_cands = [r for r in results if r.get("tadpole_ok_v2")]
        for r in ok_cands:
            f.write("config=%s chi=%s margin=%.4f vol=%.3f n_D3=%.1f\n" % (
                r["config"], r["chi_V"], r["slope_margin"], r["vol_J"], r["n_D3_correct"]))
            f.write("  B=%s\n  C=%s\n\n" % (r["B"], r["C"]))
    print("Report: " + REPORT_OUT)


if __name__ == "__main__":
    main()
