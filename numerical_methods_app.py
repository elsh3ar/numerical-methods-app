import streamlit as st
import math
import re
import sympy as sp
from itertools import permutations

# ═══════════════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Numerical Methods Solver",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════
# GLOBAL CSS – light, clean, professional
# ═══════════════════════════════════════════════════════════════════
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

/* ── Root ─────────────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
}
.main { background-color: #f5f7fa !important; }
.block-container {
    padding: 2rem 2.5rem 2rem 2.5rem !important;
    max-width: 1150px !important;
}

/* ── Sidebar ──────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
    background: linear-gradient(175deg, #ffffff 0%, #eef3fb 100%) !important;
    border-right: 1px solid #d6e0f0 !important;
}
[data-testid="stSidebar"] .block-container {
    padding: 1.5rem 1.2rem !important;
}

/* ── Title ────────────────────────────────────────────────────── */
.app-title {
    font-size: 2rem;
    font-weight: 800;
    color: #1a2f5a;
    letter-spacing: -0.03em;
    margin-bottom: 0.1rem;
}
.app-subtitle {
    font-size: 0.9rem;
    color: #7a8ba8;
    margin-bottom: 1.5rem;
    font-weight: 400;
}

/* ── Section headers ──────────────────────────────────────────── */
.section-pill {
    display: inline-block;
    background: #e8f0fe;
    color: #2d5be3;
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    margin-bottom: 1rem;
}
.section-label {
    font-size: 1rem;
    font-weight: 700;
    color: #1a2f5a;
    margin-bottom: 0.6rem;
}

/* ── Cards ────────────────────────────────────────────────────── */
.card {
    background: #ffffff;
    border: 1px solid #e4eaf4;
    border-radius: 14px;
    padding: 1.4rem 1.6rem;
    margin-bottom: 1rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}

/* ── Calculator ───────────────────────────────────────────────── */
.calc-display {
    background: #f8faff;
    border: 1.5px solid #c5d5f0;
    border-radius: 10px;
    padding: 14px 16px;
    font-family: 'DM Mono', monospace !important;
    font-size: 1.35rem;
    text-align: right;
    color: #1a2f5a;
    min-height: 54px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    margin-bottom: 12px;
    letter-spacing: -0.01em;
}
.calc-label {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #9aabcb;
    margin-bottom: 8px;
}

/* ── Matrix column labels ─────────────────────────────────────── */
.col-lbl {
    text-align: center;
    font-size: 0.78rem;
    font-weight: 700;
    padding: 5px 0;
    border-radius: 6px;
    margin-bottom: 4px;
    letter-spacing: 0.03em;
}
.lbl-a  { background: #dbeafe; color: #1d4ed8; }
.lbl-b  { background: #d1fae5; color: #047857; }
.lbl-eq { color: #b0bbd4; }

/* ── Equals sign ──────────────────────────────────────────────── */
.eq-sign {
    text-align: center;
    padding-top: 26px;
    color: #b0bbd4;
    font-size: 1.15rem;
    font-weight: 600;
}

/* ── Buttons overrides ────────────────────────────────────────── */
.stButton > button {
    border-radius: 9px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 600 !important;
    transition: all 0.15s ease !important;
    border: none !important;
}
.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.1) !important;
}
/* primary button */
button[kind="primary"] {
    background: linear-gradient(135deg, #3b6ef8, #2952d3) !important;
    color: #fff !important;
    padding: 0.55rem 2.2rem !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.01em !important;
}

/* ── Selectbox / inputs ───────────────────────────────────────── */
[data-testid="stSelectbox"] > div > div,
[data-testid="stNumberInput"] input,
[data-testid="stTextInput"] input {
    border-radius: 8px !important;
    border-color: #d6e0f0 !important;
    font-family: 'DM Sans', sans-serif !important;
}

/* ── Output text area ─────────────────────────────────────────── */
[data-testid="stTextArea"] textarea {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.83rem !important;
    background: #f8faff !important;
    border: 1.5px solid #d6e0f0 !important;
    border-radius: 12px !important;
    color: #1a2f5a !important;
    line-height: 1.65 !important;
    padding: 1rem 1.1rem !important;
}

/* ── Dividers ─────────────────────────────────────────────────── */
hr { border-color: #e4eaf4 !important; }

/* ── Info / warning boxes ─────────────────────────────────────── */
[data-testid="stAlert"] { border-radius: 10px !important; }

/* ── Spinner ──────────────────────────────────────────────────── */
.stSpinner > div { border-top-color: #3b6ef8 !important; }

/* ── Number inputs center text ────────────────────────────────── */
input[type="number"] { text-align: center !important; }

/* ── Sidebar title ────────────────────────────────────────────── */
.sidebar-title {
    font-size: 1rem;
    font-weight: 700;
    color: #1a2f5a;
    margin-bottom: 0.2rem;
    display: flex;
    align-items: center;
    gap: 6px;
}
.sidebar-divider {
    height: 1px;
    background: #d6e0f0;
    margin: 14px 0;
}

/* ── Method badge ─────────────────────────────────────────────── */
.method-badge {
    background: #f0f4ff;
    border: 1px solid #c5d5f0;
    border-radius: 8px;
    padding: 10px 16px;
    margin-bottom: 1.2rem;
    font-size: 0.88rem;
    color: #2d5be3;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 8px;
}
</style>
""",
    unsafe_allow_html=True,
)


# ═══════════════════════════════════════════════════════════════════
# MATH FUNCTIONS  (kept exactly as original)
# ═══════════════════════════════════════════════════════════════════

def clean_equation(eq_str):
    eq_str = eq_str.replace("^", "**")
    eq_str = re.sub(r"(\d)([a-zA-Z])", r"\1*\2", eq_str)
    eq_str = eq_str.replace(")(", ")*(")
    eq_str = eq_str.replace("math.e", "e").replace("math.log", "log")
    return eq_str


def try_all_permutations_dominant(A, b):
    n = len(A)
    for perm in permutations(range(n)):
        A_new = [A[i][:] for i in perm]
        b_new = [b[i] for i in perm]
        dominant = all(
            abs(A_new[i][i]) >= sum(abs(A_new[i][j]) for j in range(n) if i != j)
            for i in range(n)
        )
        if dominant:
            return A_new, b_new, True
    return A, b, False


def make_diagonally_dominant(A, b):
    n = len(A)
    A_new = [row[:] for row in A]
    b_new = b[:]
    for i in range(n):
        max_row = i
        for k in range(i + 1, n):
            if abs(A_new[k][i]) > abs(A_new[max_row][i]):
                max_row = k
        A_new[i], A_new[max_row] = A_new[max_row], A_new[i]
        b_new[i], b_new[max_row] = b_new[max_row], b_new[i]
    return A_new, b_new


def get_doolittle_lecture(A, b, max_iter=20, ask_fn=None):
    try:
        n = len(A)
        steps = ["--- Lecture Solution: Doolittle's Method ---"]
        steps.append("\n[Laws & Formulas]")
        steps.append("  [A] = [L][U]")
        steps.append("  For k=1..n: U_kj = A_kj - Sum(L_ki * U_ij)")
        steps.append("  For k=1..n: L_jk = (A_jk - Sum(L_ji * U_ik)) / U_kk")
        steps.append("  Then: Solve L*v = b  (Forward Substitution)")
        steps.append("  Then: Solve U*x = v  (Backward Substitution)")

        L = [[1 if i == j else 0 for j in range(n)] for i in range(n)]
        U = [[0 for j in range(n)] for i in range(n)]

        steps.append("\n[Step 1] Multiplying and equating to find L and U:")

        for i in range(n):
            for k in range(i, n):
                s = sum(L[i][j] * U[j][k] for j in range(i))
                sum_details = (
                    " + ".join([f"({L[i][j]}*{U[j][k]})" for j in range(i)])
                    if i > 0 else "0"
                )
                U[i][k] = A[i][k] - s
                steps.append(
                    f"  U_{i+1}{k+1} = A_{i+1}{k+1} - Sum(L*U) = "
                    f"{A[i][k]} - [{sum_details}] = {U[i][k]:.4f}"
                )

            for k in range(i + 1, n):
                s = sum(L[k][j] * U[j][i] for j in range(i))
                sum_details = (
                    " + ".join([f"({L[k][j]}*{U[j][i]})" for j in range(i)])
                    if i > 0 else "0"
                )
                L[k][i] = (A[k][i] - s) / U[i][i]
                steps.append(
                    f"  L_{k+1}{i+1} = (A_{k+1}{i+1} - Sum(L*U)) / U_{i+1}{i+1} = "
                    f"({A[k][i]} - [{sum_details}]) / {U[i][i]:.4f} = {L[k][i]:.4f}"
                )

        steps.append("\n[Step 2] Forward Substitution: Solving [L][v] = [b]")
        v = [0] * n
        for i in range(n):
            s = sum(L[i][j] * v[j] for j in range(i))
            sum_details = (
                " + ".join([f"({L[i][j]:.2f}*{v[j]:.2f})" for j in range(i)])
                if i > 0 else "0"
            )
            v[i] = b[i] - s
            steps.append(
                f"  v_{i+1} = b_{i+1} - Sum(L*v) = {b[i]} - [{sum_details}] = {v[i]:.4f}"
            )

        steps.append("\n[Step 3] Backward Substitution: Solving [U][x] = [v]")
        x = [0] * n
        for i in range(n - 1, -1, -1):
            s = sum(U[i][j] * x[j] for j in range(i + 1, n))
            sum_details = (
                " + ".join([f"({U[i][j]:.2f}*{x[j]:.2f})" for j in range(i + 1, n)])
                if i < n - 1 else "0"
            )
            x[i] = (v[i] - s) / U[i][i]
            steps.append(
                f"  x_{i+1} = (v_{i+1} - Sum(U*x)) / U_{i+1}{i+1} = "
                f"({v[i]:.4f} - [{sum_details}]) / {U[i][i]:.4f} = {x[i]:.4f}"
            )

        return "\n".join(steps)
    except Exception as e:
        return f"Error: {str(e)}"


def get_thomas_lecture(A, b, max_iter=20, ask_fn=None):
    try:
        n = len(A)
        steps = ["--- Lecture Solution: Thomas Algorithm ---"]

        steps.append("\n[Condition Check: Tridiagonal Matrix]")
        is_tri = True
        for i in range(n):
            for j in range(n):
                if abs(i - j) > 1 and abs(A[i][j]) > 1e-10:
                    is_tri = False
                    break

        if not is_tri:
            steps.append("  ❌ Failed: Matrix is NOT tridiagonal.")
            steps.append("  Rule: Only the main diagonal, sub-diagonal, and super-diagonal may be non-zero.")
            steps.append("  ➡️  Please enter a Tridiagonal matrix to use Thomas Algorithm.")
            return "\n".join(steps)
        else:
            steps.append("  ✅ Passed: Matrix is tridiagonal. Proceeding...")

        steps.append("\n[Laws & Formulas]")
        steps.append("  y_1 = d_1")
        steps.append("  y_i = d_i - (a_i * c_{i-1}) / y_{i-1}")
        steps.append("  z_1 = b_1 / y_1")
        steps.append("  z_i = (b_i - a_i * z_{i-1}) / y_i")
        steps.append("  x_n = z_n")
        steps.append("  x_i = z_i - (c_i * x_{i+1}) / y_i")

        d = [A[i][i] for i in range(n)]
        a = [0] + [A[i][i - 1] for i in range(1, n)]
        c = [A[i][i + 1] for i in range(n - 1)] + [0]

        y, z = [0] * n, [0] * n

        steps.append("\n[Step 1] Compute 'y' values:")
        y[0] = d[0]
        steps.append(f"  y_1 = d_1 = {y[0]}")
        for i in range(1, n):
            y[i] = d[i] - (a[i] * c[i - 1]) / y[i - 1]
            steps.append(
                f"  y_{i+1} = d_{i+1} - (a_{i+1} * c_{i}) / y_{i} = "
                f"{d[i]} - ({a[i]} * {c[i-1]}) / {y[i-1]:.4f} = {y[i]:.4f}"
            )

        steps.append("\n[Step 2] Compute 'z' values:")
        z[0] = b[0] / y[0]
        steps.append(f"  z_1 = b_1 / y_1 = {b[0]} / {y[0]} = {z[0]:.4f}")
        for i in range(1, n):
            z[i] = (b[i] - a[i] * z[i - 1]) / y[i]
            steps.append(
                f"  z_{i+1} = (b_{i+1} - a_{i+1} * z_{i}) / y_{i+1} = "
                f"({b[i]} - {a[i]} * {z[i-1]:.4f}) / {y[i]:.4f} = {z[i]:.4f}"
            )

        steps.append("\n[Step 3] Back Substitution for 'x' values:")
        x = [0] * n
        x[-1] = z[-1]
        steps.append(f"  x_{n} = z_{n} = {x[-1]:.4f}")
        for i in range(n - 2, -1, -1):
            x[i] = z[i] - (c[i] * x[i + 1]) / y[i]
            steps.append(
                f"  x_{i+1} = z_{i+1} - (c_{i+1} * x_{i+2}) / y_{i+1} = "
                f"{z[i]:.4f} - ({c[i]} * {x[i+1]:.4f}) / {y[i]:.4f} = {x[i]:.4f}"
            )

        return "\n".join(steps)
    except Exception as e:
        return f"Error: {str(e)}"


def _dominance_block(A, b, steps, ask_fn, method_name):
    """Shared diagonal-dominance check + optional auto-fix for Jacobi & Gauss-Seidel."""
    n = len(A)
    dominant = True
    for i in range(n):
        diag = abs(A[i][i])
        off_diag = sum(abs(A[i][j]) for j in range(n) if i != j)
        res_str = "PASSED ✅" if diag >= off_diag else "FAILED ❌"
        steps.append(f"  Row {i+1}: |{A[i][i]}| >= {off_diag:.4f}  →  {res_str}")
        if diag < off_diag:
            dominant = False

    if not dominant:
        steps.append("  ⚠️  Warning: Matrix still not dominant after initial swap. May not converge.")
        steps.append("\n[Failed Rows Detail:]")
        for i in range(n):
            diag = abs(A[i][i])
            off_diag = sum(abs(A[i][j]) for j in range(n) if i != j)
            if diag < off_diag:
                steps.append(
                    f"  ❌  Row {i+1}: |{A[i][i]}| = {diag:.4f}  <  off-diag sum = {off_diag:.4f}"
                )

        _ask = ask_fn if ask_fn is not None else (lambda t, m: True)
        answer = _ask("Diagonal Dominance Not Satisfied", "Try all permutations?")

        if answer:
            old_cond = []
            for i in range(n):
                diag = abs(A[i][i])
                off_diag = sum(abs(A[i][j]) for j in range(n) if i != j)
                status = "PASSED ✅" if diag >= off_diag else "FAILED ❌"
                old_cond.append(f"    Row {i+1}: |{A[i][i]}| vs {off_diag:.4f}  →  {status}")

            A, b, fixed = try_all_permutations_dominant(A, b)
            steps.append("\n  [Before Fix:]")
            steps.extend(old_cond)

            if fixed:
                steps.append("\n  [After Fix:]")
                for i in range(n):
                    diag = abs(A[i][i])
                    off_diag = sum(abs(A[i][j]) for j in range(n) if i != j)
                    status = "PASSED ✅" if diag >= off_diag else "FAILED ❌"
                    steps.append(f"    Row {i+1}: |{A[i][i]}| >= {off_diag:.4f}  →  {status}")
                steps.append("  ✅  Matrix is now diagonally dominant after permutation!")
            else:
                steps.append(
                    "  ❌  Could not achieve diagonal dominance by any row permutation. Continuing with warning..."
                )
        else:
            steps.append("  ⚠️  Continuing without fix. Results may not converge.")
    else:
        steps.append("  ✅  Success: Matrix is diagonally dominant.")

    return A, b


def get_jacobi_lecture(A, b, max_iter=20, ask_fn=None):
    try:
        n = len(A)
        steps = ["--- Lecture Solution: Jacobi Method ---"]

        steps.append("\n[Attempting Row Swapping for Dominance...]")
        A, b = make_diagonally_dominant(A, b)

        steps.append("\n[Condition Check: Diagonal Dominance]")
        A, b = _dominance_block(A, b, steps, ask_fn, "Jacobi")

        x = [0.0] * n
        tol = 0.0001
        k = 1
        while k <= max_iter:
            steps.append(f"\n🔴 Iteration {k}:")
            x_new = [0.0] * n
            for i in range(n):
                s = sum(A[i][j] * x[j] for j in range(n) if i != j)
                x_new[i] = (b[i] - s) / A[i][i]
                steps.append(f"  x_{i+1}^({k}) = {x_new[i]:.4f}")
            if all(abs(x_new[i] - x[i]) < tol for i in range(n)):
                steps.append(f"  ✅  Solution Converged at Iteration {k}!")
            x = x_new
            k += 1
        return "\n".join(steps)
    except Exception as e:
        return f"Error: {str(e)}"


def get_gauss_seidel_lecture(A, b, max_iter=20, ask_fn=None):
    try:
        n = len(A)
        steps = ["--- Lecture Solution: Gauss-Seidel Method ---"]

        A, b = make_diagonally_dominant(A, b)
        steps.append("\n[Rows rearranged for better convergence]")

        steps.append("\n[Condition Check: Diagonal Dominance]")
        A, b = _dominance_block(A, b, steps, ask_fn, "Gauss-Seidel")

        x = [0.0] * n
        tol = 0.0001
        k = 1
        while k <= max_iter:
            steps.append(f"\n🔴 Iteration {k}:")
            x_old = x.copy()
            for i in range(n):
                s = sum(A[i][j] * x[j] for j in range(n) if i != j)
                x[i] = (b[i] - s) / A[i][i]
                steps.append(f"  x_{i+1}^({k}) = {x[i]:.4f}")
            if all(abs(x[i] - x_old[i]) < tol for i in range(n)):
                steps.append(f"  ✅  Solution Converged at Iteration {k}!")
            k += 1
        return "\n".join(steps)
    except Exception as e:
        return f"Error: {str(e)}"


def get_bracketing_lecture(method, func_str, a, b, max_iter=20, ask_fn=None):
    try:
        cleaned_str = clean_equation(func_str)
        x_sym = sp.symbols("x")
        sym_expr_str = cleaned_str.replace("log", "sp.log").replace("e", "E")
        parsed_expr = sp.sympify(sym_expr_str)
        f_lamb = sp.lambdify(x_sym, parsed_expr, "math")

        steps = [f"--- Lecture Solution: {method} Method ---"]

        steps.append("\n[Condition Check: Intermediate Value Theorem]")
        steps.append("  Rule: f(a) * f(b) < 0")
        fa, fb = f_lamb(a), f_lamb(b)
        steps.append(f"  f({a:.4f}) = {fa:.4f}")
        steps.append(f"  f({b:.4f}) = {fb:.4f}")
        if fa * fb >= 0:
            steps.append("  ❌  Failed: f(a)*f(b) >= 0. No root guaranteed in this interval.")
        else:
            steps.append(f"  ✅  Passed: f(a)*f(b) = {fa * fb:.4f} < 0. Root exists.")

        steps.append("\n[Laws & Formulas]")
        if method == "Bisection":
            steps.append("  Rule: x_r = (a + b) / 2")
        else:
            steps.append("  Rule: x_r = [a*f(b) - b*f(a)] / [f(b) - f(a)]")

        tol = 0.0001
        k = 1
        while k <= max_iter:
            fa, fb = f_lamb(a), f_lamb(b)
            steps.append(f"\n🔴 Iteration {k}:")
            steps.append(f"  Interval: [a={a:.4f}, b={b:.4f}]")
            steps.append(f"  f(a) = {fa:.4f},  f(b) = {fb:.4f}")

            if method == "Bisection":
                c = (a + b) / 2
                steps.append(f"  Rule: x_r = ({a:.4f} + {b:.4f}) / 2 = {c:.4f}")
            else:
                c = (a * fb - b * fa) / (fb - fa)
                steps.append(
                    f"  Rule: x_r = [{a:.4f}*({fb:.4f}) - {b:.4f}*({fa:.4f})] "
                    f"/ [{fb:.4f} - ({fa:.4f})] = {c:.4f}"
                )

            fc = f_lamb(c)
            steps.append(f"  f(x_r) = {fc:.4f}")

            if abs(fc) < tol:
                steps.append(f"  ✅  Root Found at x_r = {c:.4f} (Iteration {k})")

            if fa * fc < 0:
                steps.append(f"  Since f(a)*f(x_r) < 0  →  New Interval: [a={a:.4f}, b={c:.4f}]")
                b = c
            else:
                steps.append(f"  Since f(a)*f(x_r) > 0  →  New Interval: [a={c:.4f}, b={b:.4f}]")
                a = c
            k += 1

        return "\n".join(steps)
    except Exception as e:
        return f"Error: {str(e)}"


def get_newton_lecture(func_str, x0, max_iter=20, ask_fn=None):
    try:
        cleaned_str = clean_equation(func_str)
        x_sym = sp.symbols("x")
        sym_expr_str = cleaned_str.replace("log", "sp.log").replace("e", "E")
        parsed_expr = sp.sympify(sym_expr_str)
        deriv_expr = sp.diff(parsed_expr, x_sym)

        f_lamb  = sp.lambdify(x_sym, parsed_expr, "math")
        df_lamb = sp.lambdify(x_sym, deriv_expr,  "math")

        steps = ["--- Lecture Solution: Newton-Raphson Method ---"]
        steps.append("\n[Laws & Formulas]")
        steps.append("  Rule: x_new = x_old - [f(x_old) / f'(x_old)]")
        steps.append(f"  f(x)  = {parsed_expr}")
        steps.append(f"  f'(x) = {deriv_expr}")

        x = x0
        tol = 0.0001
        k = 1
        while k <= max_iter:
            fx, dfx = f_lamb(x), df_lamb(x)
            if abs(dfx) < 1e-10:
                steps.append("\n❌  Derivative is zero. Newton-Raphson failed.")
                break

            x_new = x - fx / dfx
            steps.append(f"\n🔴 Iteration {k}:")
            steps.append(f"  f({x:.4f})  = {fx:.4f}")
            steps.append(f"  f'({x:.4f}) = {dfx:.4f}")
            steps.append(
                f"  Formula: x_new = {x:.4f} - ({fx:.4f} / {dfx:.4f}) = {x_new:.4f}"
            )

            if abs(x_new - x) < tol:
                steps.append(f"  ✅  Root Found at x = {x_new:.4f} (Iteration {k})")
            x = x_new
            k += 1

        return "\n".join(steps)
    except Exception as e:
        return f"Error: {str(e)}"


def get_secant_lecture(func_str, x0, x1, max_iter=20, ask_fn=None):
    try:
        cleaned_str = clean_equation(func_str)
        x_sym = sp.symbols("x")
        sym_expr_str = cleaned_str.replace("log", "sp.log").replace("e", "E")
        parsed_expr = sp.sympify(sym_expr_str)
        f_lamb = sp.lambdify(x_sym, parsed_expr, "math")

        steps = ["--- Lecture Solution: Secant Method ---"]
        steps.append("\n[Laws & Formulas]")
        steps.append("  Rule: x_new = x_1 - [f(x_1)*(x_1 - x_0)] / [f(x_1) - f(x_0)]")

        tol = 0.0001
        k = 1
        while k <= max_iter:
            f0, f1 = f_lamb(x0), f_lamb(x1)
            if abs(f1 - f0) < 1e-10:
                steps.append("  ⚠️  f(x_1) - f(x_0) ≈ 0. Stopping to avoid division by zero.")
                break

            x_new = x1 - f1 * (x1 - x0) / (f1 - f0)
            steps.append(f"\n🔴 Iteration {k}:")
            steps.append(f"  x_0 = {x0:.4f},  f(x_0) = {f0:.4f}")
            steps.append(f"  x_1 = {x1:.4f},  f(x_1) = {f1:.4f}")
            steps.append(
                f"  Formula: x_new = {x1:.4f} - [{f1:.4f}*({x1:.4f} - {x0:.4f})] "
                f"/ [{f1:.4f} - ({f0:.4f})] = {x_new:.4f}"
            )

            if abs(x_new - x1) < tol:
                steps.append(f"  ✅  Root Found at x = {x_new:.4f} (Iteration {k})")
            x0, x1 = x1, x_new
            k += 1

        return "\n".join(steps)
    except Exception as e:
        return f"Error: {str(e)}"


# ═══════════════════════════════════════════════════════════════════
# SESSION STATE
# ═══════════════════════════════════════════════════════════════════
if "calc_expr" not in st.session_state:
    st.session_state.calc_expr = ""
if "output" not in st.session_state:
    st.session_state.output = ""

MATRIX_METHODS = ["Doolittle", "Thomas", "Jacobi", "Gauss-Seidel"]
ALL_METHODS    = MATRIX_METHODS + ["Bisection", "False Position", "Newton", "Secant"]

METHOD_ICONS = {
    "Doolittle":      "🔷",
    "Thomas":         "🔶",
    "Jacobi":         "🟣",
    "Gauss-Seidel":   "🟢",
    "Bisection":      "📐",
    "False Position": "📏",
    "Newton":         "🔭",
    "Secant":         "🪝",
}


# ═══════════════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════════════
with st.sidebar:

    # ── Calculator ─────────────────────────────────────────────────
    st.markdown('<div class="sidebar-title">🔢 Standard Calculator</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-divider"></div>', unsafe_allow_html=True)

    display_val = st.session_state.calc_expr if st.session_state.calc_expr else "0"
    st.markdown(
        f'<div class="calc-display">{display_val}</div>',
        unsafe_allow_html=True,
    )

    btn_rows = [
        ["7", "8", "9", "÷"],
        ["4", "5", "6", "×"],
        ["1", "2", "3", "−"],
        ["C", "0", "=", "+"],
    ]

    for r_i, row in enumerate(btn_rows):
        cols = st.columns(4, gap="small")
        for c_i, lbl in enumerate(row):
            with cols[c_i]:
                if st.button(lbl, key=f"cb_{r_i}_{c_i}", use_container_width=True):
                    if lbl == "C":
                        st.session_state.calc_expr = ""
                    elif lbl == "=":
                        try:
                            expr = (
                                st.session_state.calc_expr
                                .replace("÷", "/")
                                .replace("×", "*")
                                .replace("−", "-")
                            )
                            result = eval(expr)
                            if isinstance(result, float) and result.is_integer():
                                result = int(result)
                            st.session_state.calc_expr = str(result)
                        except Exception:
                            st.session_state.calc_expr = "Error"
                    else:
                        if st.session_state.calc_expr == "Error":
                            st.session_state.calc_expr = lbl
                        else:
                            st.session_state.calc_expr += lbl
                    st.rerun()

    st.markdown('<div class="sidebar-divider" style="margin-top:18px"></div>', unsafe_allow_html=True)

    # ── Settings ───────────────────────────────────────────────────
    st.markdown('<div class="sidebar-title">⚙️ Settings</div>', unsafe_allow_html=True)
    st.markdown("")

    method = st.selectbox("Method", ALL_METHODS, key="method_sel")

    if method in MATRIX_METHODS:
        n = st.selectbox("Matrix Size  (n × n)", [2, 3, 4, 5], index=1, key="size_sel")
    else:
        n = 3  # unused for equation methods

    max_iter = st.number_input(
        "Max Iterations", min_value=1, max_value=500, value=20, step=1, key="iter_sel"
    )

    if method in ["Jacobi", "Gauss-Seidel"]:
        st.markdown("")
        auto_fix = st.checkbox(
            "Auto-fix diagonal dominance",
            value=True,
            help="When checked, the app will try all row permutations to satisfy "
                 "diagonal dominance before iterating.",
        )
    else:
        auto_fix = True

    # clear output button
    st.markdown("")
    if st.button("🗑️  Clear Output", use_container_width=True):
        st.session_state.output = ""
        st.rerun()


# ═══════════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════════
st.markdown('<div class="app-title">🧮 Numerical Methods Solver</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="app-subtitle">Step-by-step lecture-style solutions for linear systems & root-finding methods</div>',
    unsafe_allow_html=True,
)

icon = METHOD_ICONS.get(method, "🔢")
st.markdown(
    f'<div class="method-badge">{icon} &nbsp;<strong>{method}</strong> &nbsp;— selected method</div>',
    unsafe_allow_html=True,
)

# ─── Matrix Methods ────────────────────────────────────────────────
if method in MATRIX_METHODS:
    with st.container():
        st.markdown('<div class="section-pill">Matrix Input</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-label">Enter Matrix [A] and Vector [b]</div>',
            unsafe_allow_html=True,
        )

        # column ratio: n equal cols for A, tiny gap col, 1 col for b
        col_ratios = [1] * n + [0.25] + [1]
        header_cols = st.columns(col_ratios)
        for j in range(n):
            with header_cols[j]:
                st.markdown(
                    f'<div class="col-lbl lbl-a">x{j+1}</div>',
                    unsafe_allow_html=True,
                )
        with header_cols[n]:
            st.markdown('<div class="col-lbl lbl-eq"> </div>', unsafe_allow_html=True)
        with header_cols[n + 1]:
            st.markdown('<div class="col-lbl lbl-b">b</div>', unsafe_allow_html=True)

        A_vals = []
        b_vals = []

        for i in range(n):
            row_cols = st.columns(col_ratios)
            row = []
            for j in range(n):
                with row_cols[j]:
                    v = st.number_input(
                        f"A{i}{j}",
                        value=0.0,
                        key=f"A_{i}_{j}",
                        label_visibility="collapsed",
                        step=1.0,
                        format="%.2f",
                    )
                    row.append(v)
            with row_cols[n]:
                st.markdown('<div class="eq-sign">=</div>', unsafe_allow_html=True)
            with row_cols[n + 1]:
                bv = st.number_input(
                    f"B{i}",
                    value=0.0,
                    key=f"B_{i}",
                    label_visibility="collapsed",
                    step=1.0,
                    format="%.2f",
                )
            A_vals.append(row)
            b_vals.append(bv)

        st.markdown("")
        if st.button("⚡  Calculate System", type="primary"):
            ask_fn = lambda title, msg: auto_fix

            with st.spinner("Running calculation..."):
                if method == "Doolittle":
                    result = get_doolittle_lecture(A_vals, b_vals, int(max_iter), ask_fn)
                elif method == "Thomas":
                    result = get_thomas_lecture(A_vals, b_vals, int(max_iter), ask_fn)
                elif method == "Jacobi":
                    result = get_jacobi_lecture(A_vals, b_vals, int(max_iter), ask_fn)
                else:
                    result = get_gauss_seidel_lecture(A_vals, b_vals, int(max_iter), ask_fn)

            st.session_state.output = result
            st.rerun()

# ─── Equation-based Methods ────────────────────────────────────────
else:
    with st.container():
        st.markdown('<div class="section-pill">Function Input</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="section-label">Enter f(x) and Initial Values</div>',
            unsafe_allow_html=True,
        )

        func_col, params_col = st.columns([3, 2], gap="large")

        with func_col:
            func_str = st.text_input(
                "f(x)",
                placeholder="e.g.  x**3 - x - 2  or  x^3 - x - 2",
                help="Use ** or ^ for powers. Use math.log(x) for natural log, math.e for e.",
            )
            st.caption("Tip: you can write `2x` and it will be parsed as `2*x` automatically.")

        a_val, b_val = None, None
        with params_col:
            if method in ["Bisection", "False Position"]:
                pc1, pc2 = st.columns(2)
                with pc1:
                    a_val = st.number_input("a", value=1.0, format="%.4f", key="pa")
                with pc2:
                    b_val = st.number_input("b", value=2.0, format="%.4f", key="pb")

            elif method == "Newton":
                a_val = st.number_input("x₀  (initial guess)", value=1.0, format="%.4f", key="pa")

            else:  # Secant
                pc1, pc2 = st.columns(2)
                with pc1:
                    a_val = st.number_input("x₀", value=1.0, format="%.4f", key="pa")
                with pc2:
                    b_val = st.number_input("x₁", value=2.0, format="%.4f", key="pb")

        st.markdown("")
        if st.button("⚡  Calculate", type="primary"):
            if not func_str or not func_str.strip():
                st.error("⚠️  Please enter a function f(x).")
            else:
                ask_fn = lambda title, msg: True
                try:
                    with st.spinner("Running calculation..."):
                        if method in ["Bisection", "False Position"]:
                            result = get_bracketing_lecture(
                                method, func_str, a_val, b_val, int(max_iter), ask_fn
                            )
                        elif method == "Newton":
                            result = get_newton_lecture(func_str, a_val, int(max_iter), ask_fn)
                        else:
                            result = get_secant_lecture(
                                func_str, a_val, b_val, int(max_iter), ask_fn
                            )
                    st.session_state.output = result
                    st.rerun()
                except Exception as e:
                    st.session_state.output = f"Error: {str(e)}"
                    st.rerun()


# ─── Output ────────────────────────────────────────────────────────
if st.session_state.output:
    st.markdown("---")
    st.markdown('<div class="section-pill">Solution</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="section-label">📋 Step-by-Step Solution (Lecture Style)</div>',
        unsafe_allow_html=True,
    )

    st.text_area(
        label="output",
        value=st.session_state.output,
        height=480,
        disabled=True,
        label_visibility="collapsed",
    )
