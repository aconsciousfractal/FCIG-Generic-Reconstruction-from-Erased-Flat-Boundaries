#!/usr/bin/env python3
"""P43 S122 / E-A69 - exact closure of branch 3 of the exchange-graph bound.

Statement proved (conditional only on the checks in this file, all exact):

    No non-degenerate tetrahedron inscribed in the unit sphere has all four
    face planes at distance 1/2 from the circumcentre.

This closes branch 3 (centre outside), and re-proves branches 1 and 2 in
passing, because the argument never splits on the position of the centre.

Architecture - the machine contributes only polynomial identities, each
verified here by exact expansion in sympy; the geometry is hand-proved:

  A. Gram formulation. For vertices d_1..d_4 on the unit sphere with Gram
     matrix G (unit diagonal, entries x_ij), "face i lies at distance h from
     the origin" is, when the face triple is linearly independent,

         e_i := 1^T adj(G_i) 1 - (1/h^2) det(G_i) = 0        (here h = 1/2)

     and four vectors in R^3 force e_0 := det G = 0. Non-degeneracy (nonzero
     volume) forces s_i := 1^T adj(G_i) r_i - det(G_i) != 0, where s_i is the
     numerator of c_i = n_i.d_i - h (vertex-side indicator), and det(G_i) != 0
     (a face triple with linearly dependent vertex vectors would put the face
     plane through the origin, at distance 0 != 1/2).

  B. Certificates (found by a Groebner search, verified here independently):
     for each of the four linear forms
         l in { x12-x34, x13-x24, x14-x23, x23+x24+x34+1 }
     there are explicit cofactors q_0..q_4 with

         l * s_1 * s_2  =  q_0 e_0 + q_1 e_1 + q_2 e_2 + q_3 e_3 + q_4 e_4.

     At any solution the right side vanishes and s_1 s_2 != 0, hence l = 0:
     the tetrahedron is ISOSCELES-PATTERNED (opposite edges equal) with
     a + b + c = -1, where (a, b, c) = (x34, x24, x14) = (x12, x13, x23).

  C. Reduction on the pattern. Substituting the pattern into the face
     equation e_1 leaves a constant multiple of

         F(b, a) = 2ab^2 + 2a^2b + b^2 + 3ab + a^2 + b + a + 1,

     so F(b, a) = 0 at any solution.

  D. Box positivity. G positive semidefinite forces |x_ij| <= 1. On the open
     box (-1,1)^2 the cubic F is strictly positive: its four interior critical
     points carry values 20/27, 3/4, 3/4, 3/4, and its restrictions to the
     four edges are 3(b+1)^2, 1-b^2, 3(a+1)^2, 1-a^2, vanishing only at the
     three corners (a,b) = (-1,1), (1,-1), (-1,-1), each of which forces two
     coincident vertices (x24 = 1, x34 = 1, x14 = 1 respectively), i.e. a
     degenerate datum. Contradiction. QED.

Standing positive controls (the S121 lesson - a pipeline must find the
solutions that exist):

  P1. The regular tetrahedron at h = 1/3 satisfies the h = 1/3 system exactly.
  P2. An isosceles witness (u = -1/5, v = -1/3, w = -7/15) satisfies the
      system at its own h = 2/sqrt(37) < 1/3, with all four faces agreeing.
  P3. The same saturation pipeline at h = 1/3 keeps the regular point on the
      saturated variety (checked in the Singular run; recorded here).

Provenance of the searched objects (Singular 4.3.2, WSL Ubuntu-24.04): the
saturated ideal at h = 1/2 has Groebner basis

    x23+x24+x34+1,  x14+x24+x34+1,  x13-x24,  x12-x34,  F(x24, x34)

and the built-in sat() of that Singular build was found to return a wrong
ideal on this input; the saturation was recomputed by iterated ideal
quotients with in-run stability and containment certificates. None of that
is trusted here: this file re-verifies every identity from scratch.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import sympy as sp

ROOT = Path(__file__).resolve().parents[1]
CERT_DIR = ROOT / "certificates"
DEFAULT_OUTPUT = ROOT / "results" / "P43_S122_E_A69_BRANCH3_EXACT_CLOSURE.json"

X12, X13, X14, X23, X24, X34 = sp.symbols("x12 x13 x14 x23 x24 x34")
VARS = (X12, X13, X14, X23, X24, X34)
H = sp.Symbol("h")

G = sp.Matrix(
    [
        [1, X12, X13, X14],
        [X12, 1, X23, X24],
        [X13, X23, 1, X34],
        [X14, X24, X34, 1],
    ]
)

CERT_FILES = {
    "x12-x34": "P43_S122_E_A69_COFACTORS_L12_34.txt",
    "x13-x24": "P43_S122_E_A69_COFACTORS_L13_24.txt",
    "x14-x23": "P43_S122_E_A69_COFACTORS_L14_23.txt",
    "x23+x24+x34+1": "P43_S122_E_A69_COFACTORS_G1.txt",
}

CHECKS: list[tuple[str, bool]] = []


def require(condition: bool, message: str) -> None:
    """Hard failure that survives ``python -O`` (asserts do not)."""
    if not condition:
        raise RuntimeError(message)


def check(label: str, condition: bool) -> None:
    CHECKS.append((label, bool(condition)))
    print(f"[{'PASS' if condition else 'FAIL'}] {label}")


def canonical_hash(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()


def face_polys(hval):
    """e_0..e_4 and s_1..s_4 for centre-to-face distance hval, integer-cleared."""
    ones = sp.Matrix([1, 1, 1])
    e_list = [sp.expand(G.det())]
    s_list = []
    inv_h2 = sp.Rational(1) / hval**2
    for i in range(4):
        keep = [k for k in range(4) if k != i]
        Gi = G[keep, keep]
        ri = sp.Matrix([G[k, i] for k in keep])
        det_i = Gi.det()
        adj_i = Gi.adjugate()
        e_i = sp.expand((ones.T * adj_i * ones)[0, 0] - inv_h2 * det_i)
        poly = sp.Poly(e_i, *VARS)
        _, cleared = poly.clear_denoms()
        e_list.append(cleared.as_expr())
        s_list.append(sp.expand((ones.T * adj_i * ri)[0, 0] - det_i))
    return e_list, s_list


# ---------------------------------------------------------------- controls
print("== standing positive controls ==")
reg = dict(zip(VARS, [sp.Rational(-1, 3)] * 6))
e13, s13 = face_polys(sp.Rational(1, 3))
check("P1 regular tetrahedron solves the h=1/3 system", all(e.subs(reg) == 0 for e in e13))
check("P1 regular tetrahedron is non-degenerate (s_i != 0)", all(s.subs(reg) != 0 for s in s13))

u0, v0 = sp.Rational(-1, 5), sp.Rational(-1, 3)
w0 = -1 - u0 - v0
iso = dict(zip(VARS, [u0, v0, w0, w0, v0, u0]))
h_iso_sq = sp.Rational(4, 37)  # r^2/R^2 of this witness, from the S121-style control
e_iso, s_iso = face_polys(sp.sqrt(h_iso_sq))
check("P2 isosceles witness solves the system at its own h", all(sp.simplify(e.subs(iso)) == 0 for e in e_iso))
check("P2 its h is below the inside bound 1/3", h_iso_sq < sp.Rational(1, 9))
eigs = G.subs(iso).eigenvals()
check(
    "P2 witness Gram is PSD of rank 3",
    all(sp.simplify(e) >= 0 for e in eigs) and sum(1 for e, m in eigs.items() if sp.simplify(e) == 0 for _ in range(m)) == 1,
)

# ---------------------------------------------------------------- the system at h = 1/2
print("\n== the h = 1/2 system ==")
E, S = face_polys(sp.Rational(1, 2))
check("e_0..e_4 derived (degrees 4,3,3,3,3)", [sp.Poly(e, *VARS).total_degree() for e in E] == [4, 3, 3, 3, 3])

# ---------------------------------------------------------------- B: certificates
print("\n== B: the four certificates, verified by exact expansion ==")
m_sat = sp.expand(S[0] * S[1])
cert_hashes = {}
for l_str, fname in CERT_FILES.items():
    path = CERT_DIR / fname
    raw = path.read_bytes()
    cert_hashes[fname] = hashlib.sha256(raw).hexdigest().upper()
    text = raw.decode("utf-8")
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    require(len(lines) == 5, f"{fname}: expected 5 cofactors, found {len(lines)}")
    cofs = [sp.sympify(ln.replace("^", "**"), locals={str(v): v for v in VARS}) for ln in lines]
    ell = sp.sympify(l_str, locals={str(v): v for v in VARS})
    residue = sp.expand(ell * m_sat - sum(q * e for q, e in zip(cofs, E)))
    check(f"identity ({l_str}) * s1 * s2 = sum q_i e_i", residue == 0)

# ---------------------------------------------------------------- C: reduction on the pattern
print("\n== C: reduction of the face equation on the certified pattern ==")
a, b = sp.symbols("a b")
c = -1 - a - b
pattern = {X12: a, X34: a, X13: b, X24: b, X14: c, X23: c}
F = sp.expand(2 * a * b**2 + 2 * a**2 * b + b**2 + 3 * a * b + a**2 + b + a + 1)
reduced = [sp.expand(e.subs(pattern)) for e in E]
check("e_0 vanishes identically on the pattern", reduced[0] == 0)
quotients = [sp.simplify(sp.cancel(r / F)) for r in reduced[1:]]
check(
    "each face equation reduces to a nonzero constant times F",
    all(q.is_constant() and q != 0 for q in quotients),
)
print("   quotients e_i|pattern / F =", quotients)

# ---------------------------------------------------------------- D: box positivity of F
print("\n== D: F > 0 on the open box (-1,1)^2 ==")
Fu = sp.expand(sp.diff(F, a))
Fv = sp.expand(sp.diff(F, b))
crit = sp.solve([Fu, Fv], [a, b], dict=True)
crit_real = [p for p in crit if all(val.is_real for val in p.values())]
check("critical system solved completely (4 real points)", len(crit) == 4 and len(crit_real) == 4)
gb_crit = sp.groebner([Fu, Fv], a, b, order="lex")
leading_exponents = {
    tuple(poly.LM(order=gb_crit.order).exponents) for poly in gb_crit.polys
}
check(
    "critical ideal is zero-dimensional with vdim 4 (list is complete)",
    gb_crit.is_zero_dimensional
    and leading_exponents == {(2, 0), (1, 1), (0, 3)},
)
crit_vals = []
interior_ok = True
for p in crit_real:
    val = sp.nsimplify(F.subs(p))
    crit_vals.append(str(val))
    inside = abs(p[a]) < 1 and abs(p[b]) < 1
    if inside and not val > 0:
        interior_ok = False
check("every interior critical value is > 0 (values 20/27, 3/4, 3/4, 3/4)", interior_ok and sorted(crit_vals) == sorted(["20/27", "3/4", "3/4", "3/4"]))

edges = {
    "a=1": sp.expand(F.subs(a, 1)),
    "a=-1": sp.expand(F.subs(a, -1)),
    "b=1": sp.expand(F.subs(b, 1)),
    "b=-1": sp.expand(F.subs(b, -1)),
}
expected_edges = {
    "a=1": sp.expand(3 * (b + 1) ** 2),
    "a=-1": sp.expand(1 - b**2),
    "b=1": sp.expand(3 * (a + 1) ** 2),
    "b=-1": sp.expand(1 - a**2),
}
check("edge restrictions are 3(b+1)^2, 1-b^2, 3(a+1)^2, 1-a^2", edges == expected_edges)
corners = [(sp.Integer(-1), sp.Integer(1)), (sp.Integer(1), sp.Integer(-1)), (sp.Integer(-1), sp.Integer(-1))]
check("boundary zeros are exactly the three degenerate corners", all(F.subs({a: ca, b: cb}) == 0 for ca, cb in corners) and F.subs({a: 1, b: 1}) == 12)
# each corner forces coincident vertices: x24=1, x34=1, x14=1 respectively
corner_coincidence = [
    pattern[X24].subs({a: -1, b: 1}) == 1,
    pattern[X34].subs({a: 1, b: -1}) == 1,
    pattern[X14].subs({a: -1, b: -1}) == 1,
]
check("each boundary zero forces two coincident vertices", all(corner_coincidence))

# ---------------------------------------------------------------- verdict
print()
all_pass = all(ok for _, ok in CHECKS)
verdict = "BRANCH3_CLOSED_NO_NONDEGENERATE_SOLUTION_AT_H_ONE_HALF" if all_pass else "CHECKS_FAILED"
print("VERDICT:", verdict)

payload = {
    "experiment": "E-A69",
    "session": "S122",
    "statement": (
        "No non-degenerate tetrahedron inscribed in the unit sphere has all four "
        "face planes at distance 1/2 from the circumcentre; hence branch 3 of the "
        "exchange-graph bound is closed, and with it branches 1-3."
    ),
    "method": "Nullstellensatz certificates verified by exact expansion + exact box positivity",
    "certificate_files": cert_hashes,
    "saturator": "s1*s2 (numerators of c_1, c_2)",
    "checks": [{"label": lbl, "pass": ok} for lbl, ok in CHECKS],
    "face_quotients_on_pattern": [str(q) for q in quotients],
    "critical_values": crit_vals,
    "verdict": verdict,
}
payload_hash = canonical_hash(payload)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--verify-existing", action="store_true")
    args = parser.parse_args()
    if args.verify_existing:
        require(
            sp.__version__.startswith("1.14"),
            f"SymPy 1.14 is pinned for this replay; found {sp.__version__}",
        )
        frozen = json.loads(args.output.read_text(encoding="utf-8"))
        require(all_pass, "a verification check failed on recomputation")
        require(
            frozen.get("payload_sha256") == payload_hash,
            f"payload mismatch: frozen {frozen.get('payload_sha256')}, "
            f"recomputed {payload_hash}",
        )
        require(
            canonical_hash(frozen.get("payload")) == canonical_hash(payload),
            "frozen payload body differs from recomputation",
        )
        print(f"PASS_E_A69_CERTIFICATE_CLOSURE payload={payload_hash}")
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps({"payload": payload, "payload_sha256": payload_hash}, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(f"\npayload {payload_hash}")
        print(f"written {args.output}")
