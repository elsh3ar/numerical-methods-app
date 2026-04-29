import streamlit as st
import math
import re
import sympy as sp
from itertools import permutations

st.set_page_config(
    page_title="Matrix Multi-Calculator & Methods",
    page_icon="🧮",
    layout="wide"
)

st.markdown("""
<style>
    .main .block-container { padding-top: 1.2rem; padding-bottom: 1rem; }
    [data-testid="stTextArea"] textarea {
        font-family: 'Courier New', monospace !important;
        font-size: 11px !important;
        background: #0f172a !important;
        color: #94a3b8 !important;
        border: 1px solid #334155 !important;
    }
    .calc-screen {
        background: #0f172a;
        color: #38bdf8;
        font-family: 'Courier New', monospace;
        font-size: 22px;
        font-weight: bold;
        padding: 12px 16px;
        border-radius: 10px;
        text-align: right;
        min-height: 55px;
        margin-bottom: 10px;
        border: 2px solid #1e40af;
        word-break: break-all;
        letter-spacing: 1px;
    }
    div.stButton > button {
        border-radius: 8px;
        font-size: 15px;
        font-weight: bold;
        padding: 7px 0;
        transition: 0.15s;
    }
    div.stButton > button:hover {
        transform: scale(1.06);
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    h1, h2, h3 { margin-top: 0 !important; }
    .section-title {
        font-size: 13px;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 6px 0 4px 0;
    }
    @media (max-width: 768px) {
        [data-testid="column"] { min-width: 100% !important; }
        .calc-screen { font-size: 18px; min-height: 46px; }
        div.stButton > button { font-size: 13px; padding: 6px 0; }
    }
</style>
""", unsafe_allow_html=True)

# ── Session State ──────────────────────────────────────────────────────────
if 'calc_expr' not in st.session_state:
    st.session_state.calc_expr = ''
if 'output' not in st.session_state:
    st.session_state.output = ''


# =========================================================================
# MATH FUNCTIONS — identical to original Tkinter version
# =========================================================================

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


def get_doolittle_lecture(A, b, max_iter=20, ask_fn=None):
    try:
        n = len(A)
        steps = ["--- Lecture Solution: Doolittle's Method ---"]
        steps.append("\n[Laws & Formulas]")
        steps.append("  [A] = [L][U]")
        steps.append("  For k=1..n: U_kj = A_kj - Sum(L_ki * U_ij)")
        steps.append("  For k=1..n: L_jk = (A_jk - Sum(L_ji * U_ik)) / U_kk")
        steps.append("  Then: Solve L*v = b  (Forward)")
        steps.append("  Then: Solve U*x = v  (Backward)")

        L = [[1 if i == j else 0 for j in range(n)] for i in range(n)]
        U = [[0 for j in range(n)] for i in range(n)]

        steps.append("\n[Step 1] Multiplying and equating to find L and U:")

        for i in range(n):
            for k in range(i, n):
                s = sum(L[i][j] * U[j][k] for j in range(i))
                sum_details = " + ".join([f"({L[i][j]}*{U[j][k]})" for j in range(i)]) if i > 0 else "0"
                U[i][k] = A[i][k] - s
                steps.append(f"  U_{i+1}{k+1} = A_{i+1}{k+1} - Sum(L*U) = {A[i][k]} - [{sum_details}] = {U[i][k]:.4f}")

            for k in range(i + 1, n):
                s = sum(L[k][j] * U[j][i] for j in range(i))
                sum_details = " + ".join([f"({L[k][j]}*{U[j][i]})" for j in range(i)]) if i > 0 else "0"
                L[k][i] = (A[k][i] - s) / U[i][i]
                steps.append(f"  L_{k+1}{i+1} = (A_{k+1}{i+1} - Sum(L*U)) / U_{i+1}{i+1} = ({A[k][i]} - [{sum_details}]) / {U[i][i]:.4f} = {L[k][i]:.4f}")

        steps.append("\n[Step 2] Forward Substitution: Solving [L][v] = [b]")
        v = [0] * n
        for i in range(n):
            s = sum(L[i][j] * v[j] for j in range(i))
            sum_details = " + ".join([f"({L[i][j]:.2f}*{v[j]:.2f})" for j in range(i)]) if i > 0 else "0"
            v[i] = b[i] - s
            steps.append(f"  v_{i+1} = b_{i+1} - Sum(L*v) = {b[i]} - [{sum_details}] = {v[i]:.4f}")

        steps.append("\n[Step 3] Backward Substitution: Solving [U][x] = [v]")
        x = [0] * n
        for i in range(n - 1, -1, -1):
            s = sum(U[i][j] * x[j] for j in range(i + 1, n))
            sum_details = " + ".join([f"({U[i][j]:.2f}*{x[j]:.2f})" for j in range(i + 1, n)]) if i < n - 1 else "0"
            x[i] = (v[i] - s) / U[i][i]
            steps.append(f"  x_{i+1} = (v_{i+1} - Sum(U*x)) / U_{i+1}{i+1} = ({v[i]:.4f} - [{sum_details}]) / {U[i][i]:.4f} = {x[i]:.4f}")

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
            steps.append(f"  y_{i+1} = d_{i+1} - (a_{i+1} * c_{i}) / y_{i} = {d[i]} - ({a[i]} * {c[i-1]}) / {y[i-1]:.4f} = {y[i]:.4f}")

        steps.append("\n[Step 2] Compute 'z' values:")
        z[0] = b[0] / y[0]
        steps.append(f"  z_1 = b_1 / y_1 = {b[0]} / {y[0]} = {z[0]:.4f}")
        for i in range(1, n):
            z[i] = (b[i] - a[i] * z[i - 1]) / y[i]
            steps.append(f"  z_{i+1} = (b_{i+1} - a_{i+1} * z_{i}) / y_{i+1} = ({b[i]} - {a[i]} * {z[i-1]:.4f}) / {y[i]:.4f} = {z[i]:.4f}")

        steps.append("\n[Step 3] Back Substitution for 'x' values:")
        x = [0] * n
        x[-1] = z[-1]
        steps.append(f"  x_{n} = z_{n} = {x[-1]:.4f}")
        for i in range(n - 2, -1, -1):
            x[i] = z[i] - (c[i] * x[i + 1]) / y[i]
            steps.append(f"  x_{i+1} = z_{i+1} - (c_{i+1} * x_{i+2}) / y_{i+1} = {z[i]:.4f} - ({c[i]} * {x[i+1]:.4f}) / {y[i]:.4f} = {x[i]:.4f}")

        return "\n".join(steps)
    except Exception as e:
        return f"Error: {str(e)}"


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


def _dominance_check_lines(A):
    n = len(A)
    lines = []
    is_dom = True
    for i in range(n):
        diag = abs(A[i][i])
        off_diag = sum(abs(A[i][j]) for j in range(n) if i != j)
        row_str = "  |  ".join(f"{A[i][j]:>8.4f}" for j in range(n))
        if diag >= off_diag:
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
            is_dom = False
        lines.append(
            f"    Row {i+1}:  [ {row_str} ]"
            f"  →  |{A[i][i]:.4f}| = {diag:.4f}  ≥  Σ off-diag = {off_diag:.4f}  →  {status}"
        )
    return is_dom, lines


def _handle_dominance(A_in, b_in, steps, ask_fn):
    A = [row[:] for row in A_in]
    b = b_in[:]

    orig_dom, orig_lines = _dominance_check_lines(A)

    steps.append("\n[Condition Check: Diagonal Dominance]")
    steps.append("  Rule: |a_ii|  ≥  Σ |a_ij|  for all j ≠ i")
    steps.append("\n  [Original Matrix — As Entered:]")
    steps.extend(orig_lines)

    if orig_dom:
        steps.append("\n  ✅ Matrix is already Diagonally Dominant.")
        steps.append("     No rearranging needed. Proceeding directly to iterations.\n")
        return A, b

    steps.append("\n  ❌ Matrix is NOT Diagonally Dominant as entered.")
    steps.append("     Attempting automatic row rearrangement...\n")

    A_try, b_try = make_diagonally_dominant(A, b)
    try_dom, _ = _dominance_check_lines(A_try)

    if not try_dom:
        A_try, b_try, try_dom = try_all_permutations_dominant(A, b)

    if try_dom:
        steps.append("  [Before Rearranging:]")
        _, before_lines = _dominance_check_lines(A)
        steps.extend(before_lines)
        steps.append("\n  [After Rearranging:]")
        _, after_lines = _dominance_check_lines(A_try)
        steps.extend(after_lines)
        steps.append("\n  ✅ Matrix is now Diagonally Dominant after rearranging.")
        steps.append("     Proceeding with the rearranged matrix.\n")
        return A_try, b_try

    else:
        steps.append("  [Before Rearranging:]")
        _, before_lines = _dominance_check_lines(A)
        steps.extend(before_lines)
        steps.append("\n  ⚠️  Could not achieve Diagonal Dominance by any row permutation.")

        _ask = ask_fn if ask_fn is not None else lambda t, m: True
        answer = _ask(
            "Cannot Fix Diagonal Dominance",
            "No row arrangement can make the matrix diagonally dominant.\n\n"
            "Do you want to continue anyway?\n"
            "(The method may not converge.)\n\n"
            "Yes  →  Continue with warning\n"
            "No   →  Stop"
        )
        if answer:
            steps.append("  ⚠️  User chose to continue. Results may NOT converge.\n")
        else:
            steps.append("  🛑 User chose to stop. No solution computed.\n")
            raise StopIteration("User stopped due to non-dominant matrix.")
        return A, b


def get_jacobi_lecture(A, b, max_iter=20, ask_fn=None):
    try:
        n = len(A)
        steps = ["--- Lecture Solution: Jacobi Method ---"]

        steps.append("\n[Laws & Formulas]")
        steps.append("  x_i^(k+1) = ( b_i - Σ a_ij · x_j^(k) ) / a_ii   for all j ≠ i")
        steps.append("  Start: x^(0) = [0, 0, ..., 0]")
        steps.append("  Stop:  when |x_i^(k+1) - x_i^(k)| < tolerance for all i")

        A, b = _handle_dominance(A, b, steps, ask_fn)

        x = [0.0] * n
        tol = 0.0001
        k = 1
        while k <= max_iter:
            steps.append(f"\n🔴 Iteration {k}:")
            steps.append(f"  {'─'*40}")
            x_new = [0.0] * n
            for i in range(n):
                s = sum(A[i][j] * x[j] for j in range(n) if i != j)
                s_str = " + ".join(
                    f"({A[i][j]:.4f}×{x[j]:.4f})"
                    for j in range(n) if i != j
                )
                x_new[i] = (b[i] - s) / A[i][i]
                steps.append(f"  x_{i+1}^({k}) = ({b[i]:.4f} - [{s_str}]) / {A[i][i]:.4f}")
                steps.append(f"           = ({b[i]:.4f} - {s:.4f}) / {A[i][i]:.4f}")
                steps.append(f"           = {x_new[i]:.4f}")

            diffs = [abs(x_new[i] - x[i]) for i in range(n)]
            steps.append(f"\n  Error check: max|Δx| = {max(diffs):.6f}  (tol = {tol})")
            if all(d < tol for d in diffs):
                steps.append(f"  ✅ Converged at Iteration {k}!")
                steps.append(f"  Solution: " + ",  ".join(
                    f"x_{i+1} = {x_new[i]:.4f}" for i in range(n)))
            x = x_new
            k += 1

        return "\n".join(steps)
    except StopIteration:
        return "\n".join(steps)
    except Exception as e:
        return f"Error: {str(e)}"


def get_gauss_seidel_lecture(A, b, max_iter=20, ask_fn=None):
    try:
        n = len(A)
        steps = ["--- Lecture Solution: Gauss-Seidel Method ---"]

        steps.append("\n[Laws & Formulas]")
        steps.append("  x_i^(k+1) = ( b_i - Σ a_ij · x_j^(new) - Σ a_ij · x_j^(old) ) / a_ii")
        steps.append("  Unlike Jacobi: uses LATEST updated values immediately within each iteration")
        steps.append("  Start: x^(0) = [0, 0, ..., 0]")
        steps.append("  Stop:  when |x_i^(k+1) - x_i^(k)| < tolerance for all i")

        A, b = _handle_dominance(A, b, steps, ask_fn)

        x = [0.0] * n
        tol = 0.0001
        k = 1
        while k <= max_iter:
            steps.append(f"\n🔴 Iteration {k}:")
            steps.append(f"  {'─'*40}")
            x_old = x[:]
            for i in range(n):
                s = sum(A[i][j] * x[j] for j in range(n) if i != j)
                s_str = " + ".join(
                    f"({A[i][j]:.4f}×{x[j]:.4f})"
                    for j in range(n) if i != j
                )
                x[i] = (b[i] - s) / A[i][i]
                steps.append(f"  x_{i+1}^({k}) = ({b[i]:.4f} - [{s_str}]) / {A[i][i]:.4f}")
                steps.append(f"           = ({b[i]:.4f} - {s:.4f}) / {A[i][i]:.4f}")
                steps.append(f"           = {x[i]:.4f}")

            diffs = [abs(x[i] - x_old[i]) for i in range(n)]
            steps.append(f"\n  Error check: max|Δx| = {max(diffs):.6f}  (tol = {tol})")
            if all(d < tol for d in diffs):
                steps.append(f"  ✅ Converged at Iteration {k}!")
                steps.append(f"  Solution: " + ",  ".join(
                    f"x_{i+1} = {x[i]:.4f}" for i in range(n)))
            k += 1

        return "\n".join(steps)
    except StopIteration:
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
        steps.append(f"  f({a:.2f}) = {fa:.4f}")
        steps.append(f"  f({b:.2f}) = {fb:.4f}")
        if fa * fb >= 0:
            steps.append("  ❌ Failed: f(a)*f(b) >= 0. No root guaranteed in this interval.")
        else:
            steps.append(f"  ✅ Passed: f(a)*f(b) = {fa*fb:.4f} < 0. Root exists.")

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
            steps.append(f"  f(a) = {fa:.4f}, f(b) = {fb:.4f}")

            if method == "Bisection":
                c = (a + b) / 2
                steps.append(f"  Rule: x_r = ({a:.4f} + {b:.4f}) / 2 = {c:.4f}")
            else:
                c = (a * fb - b * fa) / (fb - fa)
                steps.append(f"  Rule: x_r = [{a:.4f}*({fb:.4f}) - {b:.4f}*({fa:.4f})] / [{fb:.4f} - ({fa:.4f})] = {c:.4f}")

            fc = f_lamb(c)
            steps.append(f"  f(x_r) = {fc:.4f}")

            if abs(fc) < tol:
                steps.append(f"  ✅ Root Found at x_r = {c:.4f} (Iteration {k})")

            if fa * fc < 0:
                steps.append(f"  Since f(a)*f(x_r) < 0 -> New Interval: [a={a:.4f}, b={c:.4f}]")
                b = c
            else:
                steps.append(f"  Since f(a)*f(x_r) > 0 -> New Interval: [a={c:.4f}, b={b:.4f}]")
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

        f_lamb = sp.lambdify(x_sym, parsed_expr, "math")
        df_lamb = sp.lambdify(x_sym, deriv_expr, "math")

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
                steps.append("\n❌ Derivative is zero. Newton failed.")
                break

            x_new = x - fx / dfx
            steps.append(f"\n🔴 Iteration {k}:")
            steps.append(f"  f({x:.4f}) = {fx:.4f}")
            steps.append(f"  f'({x:.4f}) = {dfx:.4f}")
            steps.append(f"  Formula: x_new = {x:.4f} - ({fx:.4f} / {dfx:.4f}) = {x_new:.4f}")

            if abs(x_new - x) < tol:
                steps.append(f"  ✅ Root Found at x = {x_new:.4f} (Iteration {k})")
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
                break

            x_new = x1 - f1 * (x1 - x0) / (f1 - f0)
            steps.append(f"\n🔴 Iteration {k}:")
            steps.append(f"  x_0 = {x0:.4f}, f(x_0) = {f0:.4f}")
            steps.append(f"  x_1 = {x1:.4f}, f(x_1) = {f1:.4f}")
            steps.append(f"  Formula: x_new = {x1:.4f} - [{f1:.4f}*({x1:.4f} - {x0:.4f})] / [{f1:.4f} - ({f0:.4f})] = {x_new:.4f}")

            if abs(x_new - x1) < tol:
                steps.append(f"  ✅ Root Found at x = {x_new:.4f} (Iteration {k})")
            x0, x1 = x1, x_new
            k += 1

        return "\n".join(steps)
    except Exception as e:
        return f"Error: {str(e)}"


def build_forward_diff_table(y_vals):
    n = len(y_vals)
    table = [[round(v, 8) for v in y_vals]]
    for k in range(1, n):
        col = []
        for i in range(n - k):
            col.append(round(table[k - 1][i + 1] - table[k - 1][i], 8))
        table.append(col)
    return table


def format_staggered_table(x_vals, table, symbol='Δ', highlights=None):
    if highlights is None:
        highlights = set()

    n = len(x_vals)
    xw = 12
    vw = 10
    EMPTY = ' ' * (vw + 2)

    def cell(k, idx):
        if k >= len(table) or idx < 0 or idx >= len(table[k]):
            return EMPTY
        val = table[k][idx]
        mark = ' ←' if (k, idx) in highlights else '  '
        return f"{val:>{vw}.4f}{mark}"

    col_titles = ['y'] + [f'{symbol}^{k}y' for k in range(1, n)]
    hdr = f"  {'x':>{xw}}  " + '  '.join(f"{t:>{vw+2}}" for t in col_titles)
    sep = '  ' + '─' * (xw + 2 + (vw + 4) * n)
    lines = [hdr, sep]

    for i in range(n):
        row = f"  {x_vals[i]:>{xw}g}  " + cell(0, i)
        for k in range(1, n):
            row += '  ' + (cell(k, i - k // 2) if k % 2 == 0 else EMPTY)
        lines.append(row)

        if i < n - 1:
            hrow = f"  {' ' * xw}  " + EMPTY
            for k in range(1, n):
                hrow += '  ' + (cell(k, i - (k - 1) // 2) if k % 2 == 1 else EMPTY)
            lines.append(hrow)

    return '\n'.join(lines)


def get_newton_forward_lecture(x_vals, y_vals, x_target, ask_fn=None):
    try:
        n = len(x_vals)
        steps = ["--- Lecture Solution: Newton's Forward Interpolation ---"]

        h = round(x_vals[1] - x_vals[0], 10)
        steps.append("\n[Condition Check: Equal Intervals]")
        steps.append(f"  h = {h}")
        equal = all(abs(round(x_vals[i + 1] - x_vals[i], 10) - h) < 1e-6 for i in range(n - 1))
        if equal:
            steps.append("  ✅ Passed: All intervals are equal.")
        else:
            steps.append("  ❌ Failed: Intervals are NOT equal. Use Lagrange's formula instead.")
            return "\n".join(steps)

        steps.append("\n[Laws & Formulas]")
        steps.append("  f(x) = y0 + p·Δy0 + p(p-1)/2!·Δ²y0 + p(p-1)(p-2)/3!·Δ³y0 + ...")
        steps.append("  Where: p = (x - x0) / h     (x0 = first value in table)")

        table = build_forward_diff_table(y_vals)
        highlights = {(k, 0) for k in range(n)}

        steps.append("\n[Forward Difference Table]")
        steps.append("  (← marks the top diagonal used in Newton's Forward formula)")
        steps.append(format_staggered_table(x_vals, table, symbol='Δ', highlights=highlights))

        x0 = x_vals[0]
        p = (x_target - x0) / h
        steps.append(f"\n[Calculate p]")
        steps.append(f"  p = (x - x0) / h = ({x_target} - {x0}) / {h} = {p:.4f}")

        steps.append(f"\n[Applying Newton's Forward Formula for x = {x_target}]")
        steps.append("  " + "─" * 55)
        result = table[0][0]
        steps.append(f"  Term 0:  y0  =  {table[0][0]:.6f}")
        steps.append(f"           ∑ = {result:.6f}")

        for k in range(1, n):
            if not table[k]:
                break
            delta_k = table[k][0]
            factors = [p - j for j in range(k)]
            num = 1.0
            for f_ in factors:
                num *= f_
            denom = math.factorial(k)
            coeff = num / denom
            contrib = coeff * delta_k

            f_str = " · ".join(f"({v:.4f})" for v in factors)
            sym_parts = ["p"] + [f"(p-{j})" for j in range(1, k)]
            sym_str = " · ".join(sym_parts)

            steps.append(f"\n  Term {k}:  [{sym_str}] / {k}!  ·  Δ^{k}y0")
            steps.append(f"           = [{f_str}] / {denom}  ·  {delta_k:.6f}")
            steps.append(f"           = {num:.6f} / {denom}  ·  {delta_k:.6f}")
            steps.append(f"           = {coeff:.6f}  ·  {delta_k:.6f}")
            steps.append(f"           = {contrib:.6f}")
            result += contrib
            steps.append(f"           ∑ = {result:.6f}")

        steps.append("\n  " + "─" * 55)
        steps.append(f"  ✅ f({x_target}) ≈ {result:.4f}")
        return "\n".join(steps)
    except Exception as e:
        return f"Error: {str(e)}"


def get_newton_forward_from_eq_lecture(func_str, x_start, h, n_points, x_target, ask_fn=None):
    try:
        cleaned = clean_equation(func_str)
        x_sym = sp.symbols("x")
        expr_str = cleaned.replace("log", "sp.log").replace("e", "E")
        parsed = sp.sympify(expr_str)
        f_lamb = sp.lambdify(x_sym, parsed, "math")

        steps = ["--- Lecture Solution: Newton's Forward Interpolation (from Equation) ---"]
        steps.append(f"\n[Given]  f(x) = {func_str}")
        steps.append(f"         x0 = {x_start},  h = {h},  n = {n_points} points,  x_target = {x_target}")

        x_vals = [round(x_start + i * h, 10) for i in range(n_points)]
        y_vals = []
        steps.append("\n[Generated Table from Equation]")
        steps.append(f"  {'x':>12}  {'f(x)':>14}")
        steps.append("  " + "─" * 28)
        for xv in x_vals:
            yv = f_lamb(xv)
            y_vals.append(yv)
            steps.append(f"  {xv:>12g}  {yv:>14.6f}")

        rest = get_newton_forward_lecture(x_vals, y_vals, x_target, ask_fn=ask_fn)
        rest_lines = rest.split("\n")
        rest_lines = [l for l in rest_lines if not l.startswith("--- Lecture Solution: Newton's Forward")]
        steps.append("\n" + "\n".join(rest_lines))
        return "\n".join(steps)
    except Exception as e:
        return f"Error: {str(e)}"


def get_newton_backward_lecture(x_vals, y_vals, x_target, ask_fn=None):
    try:
        n = len(x_vals)
        steps = ["--- Lecture Solution: Newton's Backward Interpolation ---"]

        h = round(x_vals[1] - x_vals[0], 10)
        steps.append("\n[Condition Check: Equal Intervals]")
        steps.append(f"  h = {h}")
        equal = all(abs(round(x_vals[i + 1] - x_vals[i], 10) - h) < 1e-6 for i in range(n - 1))
        if equal:
            steps.append("  ✅ Passed: All intervals are equal.")
        else:
            steps.append("  ❌ Failed: Intervals are NOT equal. Use Lagrange's formula instead.")
            return "\n".join(steps)

        steps.append("\n[Laws & Formulas]")
        steps.append("  f(x) = yn + p·∇yn + p(p+1)/2!·∇²yn + p(p+1)(p+2)/3!·∇³yn + ...")
        steps.append("  Where: p = (x - xn) / h     (xn = last value in table)")

        table = build_forward_diff_table(y_vals)
        highlights = {(k, n - 1 - k) for k in range(n)}

        steps.append("\n[Backward Difference Table  (Horizontal Table)]")
        steps.append("  (← marks the bottom diagonal used in Newton's Backward formula)")
        steps.append(format_staggered_table(x_vals, table, symbol='∇', highlights=highlights))

        steps.append("\n[Reading ∇^k yn  (bottom diagonal values):]")
        for k in range(n):
            idx = n - 1 - k
            if k < len(table) and 0 <= idx < len(table[k]):
                arrow = " ←" if k > 0 else ""
                steps.append(f"  ∇^{k} y_n  =  table[{k}][{idx}]  =  {table[k][idx]:.4f}{arrow}")

        xn = x_vals[-1]
        p = (x_target - xn) / h
        steps.append(f"\n[Calculate p]")
        steps.append(f"  p = (x - xn) / h = ({x_target} - {xn}) / {h} = {p:.4f}")

        steps.append(f"\n[Applying Newton's Backward Formula for x = {x_target}]")
        steps.append("  " + "─" * 55)
        yn = table[0][n - 1]
        result = yn
        steps.append(f"  Term 0:  yn  =  {yn:.6f}")
        steps.append(f"           ∑ = {result:.6f}")

        for k in range(1, n):
            idx = n - 1 - k
            if idx < 0 or k >= len(table) or idx >= len(table[k]):
                break
            nabla_k = table[k][idx]
            factors = [p + j for j in range(k)]
            num = 1.0
            for f_ in factors:
                num *= f_
            denom = math.factorial(k)
            coeff = num / denom
            contrib = coeff * nabla_k

            f_str = " · ".join(f"({v:.4f})" for v in factors)
            sym_parts = ["p"] + [f"(p+{j})" for j in range(1, k)]
            sym_str = " · ".join(sym_parts)

            steps.append(f"\n  Term {k}:  [{sym_str}] / {k}!  ·  ∇^{k}yn")
            steps.append(f"           = [{f_str}] / {denom}  ·  {nabla_k:.6f}")
            steps.append(f"           = {num:.6f} / {denom}  ·  {nabla_k:.6f}")
            steps.append(f"           = {coeff:.6f}  ·  {nabla_k:.6f}")
            steps.append(f"           = {contrib:.6f}")
            result += contrib
            steps.append(f"           ∑ = {result:.6f}")

        steps.append("\n  " + "─" * 55)
        steps.append(f"  ✅ f({x_target}) ≈ {result:.4f}")
        return "\n".join(steps)
    except Exception as e:
        return f"Error: {str(e)}"


def get_stirling_lecture(x_vals, y_vals, x_target, ask_fn=None):
    try:
        n = len(x_vals)
        steps = ["--- Lecture Solution: Stirling's Interpolation Formula ---"]

        h = round(x_vals[1] - x_vals[0], 10)
        steps.append("\n[Condition Check: Equal Intervals]")
        steps.append(f"  h = {h}")
        equal = all(abs(round(x_vals[i + 1] - x_vals[i], 10) - h) < 1e-6 for i in range(n - 1))
        if equal:
            steps.append("  ✅ Passed: All intervals are equal.")
        else:
            steps.append("  ❌ Failed: Intervals are NOT equal. Use Lagrange's formula instead.")
            return "\n".join(steps)

        if n < 3:
            steps.append("  ❌ Need at least 3 data points for Stirling's formula.")
            return "\n".join(steps)

        steps.append("\n[Laws & Formulas]")
        steps.append("  f(x) = y0")
        steps.append("       + p · (Δy0 + Δy_{-1}) / 2")
        steps.append("       + p² / 2! · Δ²y_{-1}")
        steps.append("       + p(p²-1) / 3! · (Δ³y_{-1} + Δ³y_{-2}) / 2")
        steps.append("       + p²(p²-1) / 4! · Δ⁴y_{-2}  + ...")
        steps.append("  Where: p = (x - x0) / h     (x0 = CENTRAL value of table)")

        mid = n // 2
        x0 = x_vals[mid]
        steps.append(f"\n[Central Point Selected: x0 = {x0}  (index {mid})]")

        table = build_forward_diff_table(y_vals)

        hl = set()
        hl.add((0, mid))
        if mid < len(table[1]):
            hl.add((1, mid))
        if mid - 1 >= 0:
            hl.add((1, mid - 1))
        if 2 < len(table) and mid - 1 >= 0 and mid - 1 < len(table[2]):
            hl.add((2, mid - 1))
        if 3 < len(table) and mid - 1 >= 0 and mid - 1 < len(table[3]):
            hl.add((3, mid - 1))
        if 3 < len(table) and mid - 2 >= 0 and mid - 2 < len(table[3]):
            hl.add((3, mid - 2))
        if 4 < len(table) and mid - 2 >= 0 and mid - 2 < len(table[4]):
            hl.add((4, mid - 2))

        steps.append("\n[Central Difference Table]")
        steps.append("  (← marks values used in Stirling's formula, centered at x0)")
        steps.append(format_staggered_table(x_vals, table, symbol='Δ', highlights=hl))

        p = (x_target - x0) / h
        steps.append(f"\n[Calculate p]")
        steps.append(f"  p = (x - x0) / h = ({x_target} - {x0}) / {h} = {p:.4f}")

        steps.append(f"\n[Applying Stirling's Formula for x = {x_target}]")
        y0_val = table[0][mid]
        result = y0_val
        steps.append(f"  Term 0:  y0 = {y0_val:.4f}")
        steps.append(f"           Running total = {result:.4f}")

        if (len(table) > 1 and mid < len(table[1])
                and mid - 1 >= 0 and mid - 1 < len(table[1])):
            dy0 = table[1][mid]
            dy_m1 = table[1][mid - 1]
            t1 = p * (dy0 + dy_m1) / 2.0
            result += t1
            steps.append(f"\n  Term 1:  p · (Δy0 + Δy_{{-1}}) / 2")
            steps.append(f"           = {p:.4f} · ({dy0:.4f} + {dy_m1:.4f}) / 2")
            steps.append(f"           = {p:.4f} · {(dy0+dy_m1)/2:.4f}  =  {t1:.4f}")
            steps.append(f"           Running total = {result:.4f}")

        if (len(table) > 2 and mid - 1 >= 0 and mid - 1 < len(table[2])):
            d2 = table[2][mid - 1]
            t2 = (p ** 2 / math.factorial(2)) * d2
            result += t2
            steps.append(f"\n  Term 2:  p² / 2! · Δ²y_{{-1}}")
            steps.append(f"           = ({p:.4f})² / 2 · {d2:.4f}")
            steps.append(f"           = {p**2:.4f} / 2 · {d2:.4f}  =  {t2:.4f}")
            steps.append(f"           Running total = {result:.4f}")

        if (len(table) > 3 and mid - 1 >= 0 and mid - 1 < len(table[3])
                and mid - 2 >= 0 and mid - 2 < len(table[3])):
            d3a = table[3][mid - 1]
            d3b = table[3][mid - 2]
            t3 = (p * (p ** 2 - 1) / math.factorial(3)) * (d3a + d3b) / 2.0
            result += t3
            steps.append(f"\n  Term 3:  p(p²-1) / 3! · (Δ³y_{{-1}} + Δ³y_{{-2}}) / 2")
            steps.append(f"           = {p:.4f}·(({p:.4f})²-1) / 6 · ({d3a:.4f} + {d3b:.4f}) / 2")
            steps.append(f"           = {p*(p**2-1)/6:.6f} · {(d3a+d3b)/2:.4f}  =  {t3:.4f}")
            steps.append(f"           Running total = {result:.4f}")

        if (len(table) > 4 and mid - 2 >= 0 and mid - 2 < len(table[4])):
            d4 = table[4][mid - 2]
            t4 = (p ** 2 * (p ** 2 - 1) / math.factorial(4)) * d4
            result += t4
            steps.append(f"\n  Term 4:  p²(p²-1) / 4! · Δ⁴y_{{-2}}")
            steps.append(f"           = ({p:.4f})²·(({p:.4f})²-1) / 24 · {d4:.4f}")
            steps.append(f"           = {p**2*(p**2-1)/24:.6f} · {d4:.4f}  =  {t4:.4f}")
            steps.append(f"           Running total = {result:.4f}")

        steps.append(f"\n  ✅ f({x_target}) ≈ {result:.4f}")
        return "\n".join(steps)
    except Exception as e:
        return f"Error: {str(e)}"


def get_lagrange_lecture(x_vals, y_vals, x_target, ask_fn=None):
    try:
        n = len(x_vals)
        steps = ["--- Lecture Solution: Lagrange's Interpolation Formula ---"]

        steps.append("\n[Laws & Formulas]")
        steps.append("  f(x) = Σ  L_i(x) · y_i     for i = 0, 1, ..., n")
        steps.append("  L_i(x) = Π (x - x_j) / (x_i - x_j)   for all j ≠ i")

        steps.append(f"\n[Given Data Points]")
        steps.append(f"  {'i':>3}  {'x_i':>10}  {'y_i':>14}")
        steps.append("  " + "─" * 32)
        for i in range(n):
            steps.append(f"  {i:>3}  {x_vals[i]:>10g}  {y_vals[i]:>14.6f}")

        steps.append(f"\n[Calculating f({x_target})]")
        steps.append("  " + "─" * 55)
        result = 0.0

        for i in range(n):
            num = 1.0
            den = 1.0
            num_parts = []
            den_parts = []
            for j in range(n):
                if i != j:
                    num_parts.append(f"({x_target}-{x_vals[j]})")
                    den_parts.append(f"({x_vals[i]}-{x_vals[j]})")
                    num *= (x_target - x_vals[j])
                    den *= (x_vals[i] - x_vals[j])
            Li = num / den
            contrib = Li * y_vals[i]
            result += contrib

            steps.append(f"\n  L_{i}(x):")
            steps.append(f"    Numerator   = {' · '.join(num_parts)}")
            steps.append(f"                = {num:.6f}")
            steps.append(f"    Denominator = {' · '.join(den_parts)}")
            steps.append(f"                = {den:.6f}")
            steps.append(f"    L_{i} = {num:.6f} / {den:.6f} = {Li:.6f}")
            steps.append(f"    L_{i} · y_{i} = {Li:.6f} · {y_vals[i]:.6f} = {contrib:.6f}")
            steps.append(f"    ∑ = {result:.6f}")

        steps.append("\n  " + "─" * 55)
        steps.append(f"  ✅ f({x_target}) ≈ {result:.4f}")
        return "\n".join(steps)
    except Exception as e:
        return f"Error: {str(e)}"


def get_lagrange_polynomial_lecture(x_vals, y_vals, ask_fn=None):
    try:
        n = len(x_vals)
        xs = sp.Symbol('x')
        steps = ["--- Lecture Solution: Lagrange's Interpolation — Polynomial Form ---"]

        steps.append("\n[Laws & Formulas]")
        steps.append("  f(x) = Σ  L_i(x) · y_i     for i = 0, 1, ..., n")
        steps.append("  L_i(x) = Π (x - x_j) / (x_i - x_j)   for all j ≠ i")

        steps.append(f"\n[Given Data Points]")
        steps.append(f"  {'i':>3}  {'x_i':>10}  {'y_i':>14}")
        steps.append("  " + "─" * 32)
        for i in range(n):
            steps.append(f"  {i:>3}  {x_vals[i]:>10g}  {y_vals[i]:>14.6f}")

        steps.append("\n[Building Each Basis Polynomial L_i(x)]")
        steps.append("  " + "─" * 55)

        poly_total = sp.Integer(0)

        for i in range(n):
            Li_expr = sp.Integer(1)
            num_factors = []
            den_factors = []
            for j in range(n):
                if i != j:
                    num_factors.append(f"(x - {x_vals[j]})")
                    den_factors.append(f"({x_vals[i]} - {x_vals[j]})")
                    Li_expr *= (xs - x_vals[j]) / (x_vals[i] - x_vals[j])

            Li_expanded = sp.expand(Li_expr)
            contrib_expr = sp.expand(Li_expr * y_vals[i])

            steps.append(f"\n  L_{i}(x):")
            steps.append(f"    = [{' · '.join(num_factors)}]")
            steps.append(f"      / [{' · '.join(den_factors)}]")
            steps.append(f"    = {Li_expanded}")
            steps.append(f"\n  L_{i}(x) · y_{i}  =  ({Li_expanded}) · {y_vals[i]}")
            steps.append(f"                    =  {contrib_expr}")

            poly_total += Li_expr * y_vals[i]

        poly_expanded = sp.expand(poly_total)

        steps.append("\n\n[Final Polynomial f(x)]")
        steps.append("  " + "─" * 55)
        steps.append(f"  f(x) = sum of all terms")
        steps.append(f"\n  Expanded:")
        steps.append(f"  f(x) = {poly_expanded}")

        try:
            poly_simplified = sp.nsimplify(poly_expanded, rational=True)
            steps.append(f"\n  Simplified:")
            steps.append(f"  f(x) = {poly_simplified}")
        except Exception:
            pass

        try:
            poly_obj = sp.Poly(poly_expanded, xs)
            coeffs = poly_obj.all_coeffs()
            deg = len(coeffs) - 1
            terms = []
            for pw, c in enumerate(coeffs):
                power = deg - pw
                c_val = float(c)
                if abs(c_val) < 1e-9:
                    continue
                c_fmt = f"{c_val:.4f}"
                if power == 0:
                    terms.append(c_fmt)
                elif power == 1:
                    terms.append(f"{c_fmt}·x")
                else:
                    terms.append(f"{c_fmt}·x^{power}")
            poly_str = "  f(x) = " + " + ".join(terms).replace("+ -", "- ")
            steps.append(f"\n  Standard form:")
            steps.append(poly_str)
        except Exception:
            pass

        steps.append("\n  " + "─" * 55)
        steps.append("  ✅ Polynomial constructed successfully.")
        return "\n".join(steps)
    except Exception as e:
        return f"Error: {str(e)}"


def get_lagrange_inverse_lecture(x_vals, y_vals, y_target, ask_fn=None):
    try:
        n = len(x_vals)
        steps = ["--- Lecture Solution: Lagrange's Inverse Interpolation ---"]

        steps.append("\n[Laws & Formulas]")
        steps.append("  x = Σ  L_i(y) · x_i     for i = 0, 1, ..., n")
        steps.append("  L_i(y) = Π (y - y_j) / (y_i - y_j)   for all j ≠ i")
        steps.append("  (Same as Lagrange but with x and y roles swapped)")

        steps.append(f"\n[Given Data Points]")
        steps.append(f"  {'i':>3}  {'x_i':>10}  {'y_i':>14}")
        steps.append("  " + "─" * 32)
        for i in range(n):
            steps.append(f"  {i:>3}  {x_vals[i]:>10g}  {y_vals[i]:>14.6f}")

        steps.append(f"\n[Calculating x for y = {y_target}]")
        steps.append("  " + "─" * 55)
        result = 0.0

        for i in range(n):
            num = 1.0
            den = 1.0
            num_parts = []
            den_parts = []
            for j in range(n):
                if i != j:
                    num_parts.append(f"({y_target}-{y_vals[j]})")
                    den_parts.append(f"({y_vals[i]}-{y_vals[j]})")
                    num *= (y_target - y_vals[j])
                    den *= (y_vals[i] - y_vals[j])
            Li = num / den
            contrib = Li * x_vals[i]
            result += contrib

            steps.append(f"\n  L_{i}(y):")
            steps.append(f"    Numerator   = {' · '.join(num_parts)}")
            steps.append(f"                = {num:.6f}")
            steps.append(f"    Denominator = {' · '.join(den_parts)}")
            steps.append(f"                = {den:.6f}")
            steps.append(f"    L_{i} = {num:.6f} / {den:.6f} = {Li:.6f}")
            steps.append(f"    L_{i} · x_{i} = {Li:.6f} · {x_vals[i]:.6f} = {contrib:.6f}")
            steps.append(f"    ∑ = {result:.6f}")

        steps.append("\n  " + "─" * 55)
        steps.append(f"  ✅ x ≈ {result:.4f}  (for y = {y_target})")
        return "\n".join(steps)
    except Exception as e:
        return f"Error: {str(e)}"


def get_finite_difference_lecture(x_vals, y_vals, ask_fn=None):
    try:
        n = len(x_vals)
        steps = ["--- Lecture Solution: Finite Difference Operators ---"]

        steps.append("\n[Laws & Definitions]")
        steps.append("")
        steps.append("  ▶ Forward Difference Operator  (Δ):")
        steps.append("      Δf(x)  =  f(x + h) - f(x)")
        steps.append("      Δy_i   =  y_{i+1} - y_i       i = 0, 1, 2, ..., n-1")
        steps.append("")
        steps.append("      Second differences:")
        steps.append("      Δ²y_0  =  Δ(Δy_0)  =  Δy_1 - Δy_0  =  y_2 - 2·y_1 + y_0")
        steps.append("      Δ²y_1  =  Δ(Δy_1)  =  Δy_2 - Δy_1  =  y_3 - 2·y_2 + y_1")
        steps.append("")
        steps.append("  ▶ Backward Difference Operator  (∇):")
        steps.append("      ∇f(x)  =  f(x) - f(x - h)")
        steps.append("      ∇y_i   =  y_i - y_{i-1}        i = n, n-1, ..., 1")
        steps.append("")
        steps.append("      Second differences:")
        steps.append("      ∇²y_2  =  ∇(∇y_2)  =  ∇y_2 - ∇y_1  =  y_2 - 2·y_1 + y_0")
        steps.append("      ∇²y_3  =  ∇(∇y_3)  =  ∇y_3 - ∇y_2  =  y_3 - 2·y_2 + y_1")

        steps.append(f"\n[Given Data Points]")
        steps.append(f"  {'x':>8}  " + "  ".join(f"{v:>8g}" for v in x_vals))
        steps.append(f"  {'y':>8}  " + "  ".join(f"{v:>8.4f}" for v in y_vals))

        table = build_forward_diff_table(y_vals)

        steps.append("\n" + "=" * 62)
        steps.append("  PART 1 — Forward Difference Table")
        steps.append("=" * 62)

        steps.append("\n[Step 1: Compute First Forward Differences  Δy_i = y_{i+1} - y_i]")
        for i in range(n - 1):
            val = table[1][i]
            steps.append(f"  Δy_{i} = y_{i+1} - y_{i}"
                         f"  =  {y_vals[i+1]:.4f} - {y_vals[i]:.4f}"
                         f"  =  {val:.4f}")

        for order in range(2, n):
            steps.append(f"\n[Step {order}: Compute {order}-th Order Differences"
                         f"  Δ^{order}y_i = Δ^{order-1}y_{{i+1}} - Δ^{order-1}y_i]")
            for i in range(n - order):
                prev_next = table[order - 1][i + 1]
                prev_curr = table[order - 1][i]
                val = table[order][i]
                steps.append(f"  Δ^{order}y_{i} = Δ^{order-1}y_{i+1} - Δ^{order-1}y_{i}"
                             f"  =  {prev_next:.4f} - {prev_curr:.4f}"
                             f"  =  {val:.4f}")

        steps.append("\n[Forward Difference Table  (staggered — top diagonal ← used by Newton Forward)]")
        steps.append(format_staggered_table(x_vals, table, symbol='Δ',
                                            highlights={(k, 0) for k in range(n)}))

        steps.append("\n" + "=" * 62)
        steps.append("  PART 2 — Backward Difference Table  (Horizontal Table)")
        steps.append("=" * 62)

        steps.append("\n[Step 1: Compute First Backward Differences  ∇y_i = y_i - y_{i-1}]")
        for i in range(1, n):
            val = table[1][i - 1]
            steps.append(f"  ∇y_{i} = y_{i} - y_{i-1}"
                         f"  =  {y_vals[i]:.4f} - {y_vals[i-1]:.4f}"
                         f"  =  {val:.4f}")

        for order in range(2, n):
            steps.append(f"\n[Step {order}: Compute {order}-th Order Backward Differences"
                         f"  ∇^{order}y_i = ∇^{order-1}y_i - ∇^{order-1}y_{{i-1}}]")
            for i in range(order, n):
                prev_curr2 = table[order - 1][i - order + 1]
                prev_prev = table[order - 1][i - order]
                val = table[order][i - order]
                steps.append(f"  ∇^{order}y_{i} = ∇^{order-1}y_{i} - ∇^{order-1}y_{i-1}"
                             f"  =  {prev_curr2:.4f} - {prev_prev:.4f}"
                             f"  =  {val:.4f}")

        steps.append("\n[Backward Difference Table  (staggered — bottom diagonal ← used by Newton Backward)]")
        steps.append(format_staggered_table(x_vals, table, symbol='∇',
                                            highlights={(k, n - 1 - k) for k in range(n)}))

        steps.append("\n" + "=" * 62)
        steps.append("  SUMMARY  —  Key Diagonal Values")
        steps.append("=" * 62)
        steps.append(f"\n  Top diagonal  (Newton Forward uses these):")
        for k in range(n):
            if table[k]:
                steps.append(f"    Δ^{k}y_0  =  {table[k][0]:.4f}")

        steps.append(f"\n  Bottom diagonal  (Newton Backward uses these):")
        for k in range(n):
            idx = n - 1 - k
            if 0 <= idx < len(table[k]):
                steps.append(f"    ∇^{k}y_{n-1}  =  {table[k][idx]:.4f}")

        steps.append("\n  ✅ Finite Difference Tables completed.")
        return "\n".join(steps)
    except Exception as e:
        return f"Error: {str(e)}"


# =========================================================================
# STREAMLIT UI
# =========================================================================

st.markdown("## 🧮 Matrix Multi-Calculator & Methods")

left_col, right_col = st.columns([1, 3])

# ── LEFT: Standard Calculator ──────────────────────────────────────────────
with left_col:
    st.markdown("### 🖩 Standard Calc")

    display_val = st.session_state.calc_expr if st.session_state.calc_expr else "0"
    st.markdown(f'<div class="calc-screen">{display_val}</div>', unsafe_allow_html=True)

    btn_layout = [
        ["7", "8", "9", "/"],
        ["4", "5", "6", "*"],
        ["1", "2", "3", "-"],
        ["C", "0", "=", "+"],
    ]
    key_map = {"/": "div", "*": "mul", "-": "minus", "+": "plus", "=": "eq", "C": "clr"}

    for r, row in enumerate(btn_layout):
        cols = st.columns(4)
        for c, char in enumerate(row):
            safe = key_map.get(char, char)
            with cols[c]:
                if st.button(char, key=f"calc_{safe}_{r}", use_container_width=True):
                    if char == "C":
                        st.session_state.calc_expr = ""
                    elif char == "=":
                        try:
                            st.session_state.calc_expr = str(eval(st.session_state.calc_expr))
                        except:
                            st.session_state.calc_expr = "Error"
                    else:
                        if st.session_state.calc_expr == "Error":
                            st.session_state.calc_expr = ""
                        st.session_state.calc_expr += char
                    st.rerun()

# ── RIGHT: Methods ─────────────────────────────────────────────────────────
with right_col:
    methods_list = [
        "Doolittle", "Thomas", "Jacobi", "Gauss-Seidel",
        "Bisection", "False Position", "Newton", "Secant",
        "Finite Difference",
        "Newton Forward", "Newton Backward", "Stirling",
        "Lagrange", "Lagrange Inverse"
    ]

    matrix_methods = ["Doolittle", "Thomas", "Jacobi", "Gauss-Seidel"]
    eq_methods     = ["Bisection", "False Position", "Newton", "Secant"]
    interp_methods = ["Finite Difference", "Newton Forward", "Newton Backward",
                      "Stirling", "Lagrange", "Lagrange Inverse"]

    ctrl1, ctrl2, ctrl3 = st.columns([3, 1, 1])
    with ctrl1:
        method = st.selectbox("Select Method", methods_list, key="method_sel")
    with ctrl2:
        if method in interp_methods:
            size_opts = [2, 3, 4, 5, 6, 7, 8]
            size_lbl  = "Points (n)"
        else:
            size_opts = [2, 3, 4, 5]
            size_lbl  = "Size (n)"
        n = st.selectbox(size_lbl, size_opts, index=1, key="n_sel")
    with ctrl3:
        max_iter = st.number_input("Max Iter", min_value=1, max_value=1000, value=20, key="max_iter_inp")

    # auto_ask: in Streamlit we cannot block mid-computation for a dialog,
    # so we auto-continue and the warning already appears in the steps output.
    def auto_ask(title, msg):
        return True

    st.markdown("---")

    # ── MATRIX METHODS ────────────────────────────────────────────────────
    if method in matrix_methods:
        st.markdown(f"**Matrix [A] and Vector [b] — {n}×{n}**")

        A_vals = []
        b_vals = []

        for i in range(n):
            row_cols = st.columns(n + 2)
            row = []
            for j in range(n):
                with row_cols[j]:
                    v = st.text_input(f"A[{i+1}][{j+1}]", value="0",
                                      key=f"m_{i}_{j}_{n}_{method}",
                                      label_visibility="collapsed")
                    try:
                        row.append(float(v))
                    except:
                        row.append(0.0)
            with row_cols[n]:
                st.markdown("<div style='padding-top:8px;text-align:center;font-weight:bold;font-size:18px'>=</div>",
                            unsafe_allow_html=True)
            with row_cols[n + 1]:
                bv = st.text_input(f"b[{i+1}]", value="0",
                                   key=f"b_{i}_{n}_{method}",
                                   label_visibility="collapsed")
                try:
                    b_vals.append(float(bv))
                except:
                    b_vals.append(0.0)
            A_vals.append(row)

        if st.button(f"🔢 Calculate ({method})", type="primary", use_container_width=True):
            with st.spinner("⏳ Calculating..."):
                mi = int(max_iter)
                if method == "Doolittle":
                    st.session_state.output = get_doolittle_lecture(A_vals, b_vals, mi, ask_fn=auto_ask)
                elif method == "Thomas":
                    st.session_state.output = get_thomas_lecture(A_vals, b_vals, mi, ask_fn=auto_ask)
                elif method == "Jacobi":
                    st.session_state.output = get_jacobi_lecture(A_vals, b_vals, mi, ask_fn=auto_ask)
                else:
                    st.session_state.output = get_gauss_seidel_lecture(A_vals, b_vals, mi, ask_fn=auto_ask)

    # ── EQUATION METHODS ──────────────────────────────────────────────────
    elif method in eq_methods:
        st.markdown("**ℹ️ Supported syntax:** `x**3 - x - 2` or `x^3 - x - 2` &nbsp;|&nbsp; `math.sin(x)`, `math.log(x)`, `math.e`")
        func_str = st.text_input("f(x) =", placeholder="e.g.  x**3 - x - 2",
                                 key="func_input")

        if method in ["Bisection", "False Position"]:
            ec1, ec2 = st.columns(2)
            with ec1:
                a_str = st.text_input("a", value="1.0", key="ea")
            with ec2:
                b_str = st.text_input("b", value="2.0", key="eb")
        elif method == "Newton":
            a_str = st.text_input("x₀  (initial guess)", value="1.0", key="ea")
            b_str = None
        else:  # Secant
            ec1, ec2 = st.columns(2)
            with ec1:
                a_str = st.text_input("x₀", value="1.0", key="ea")
            with ec2:
                b_str = st.text_input("x₁", value="2.0", key="eb")

        if st.button(f"🔢 Calculate ({method})", type="primary", use_container_width=True):
            with st.spinner("⏳ Calculating..."):
                try:
                    mi = int(max_iter)
                    if method in ["Bisection", "False Position"]:
                        st.session_state.output = get_bracketing_lecture(
                            method, func_str, float(a_str), float(b_str), mi, ask_fn=auto_ask)
                    elif method == "Newton":
                        st.session_state.output = get_newton_lecture(
                            func_str, float(a_str), mi, ask_fn=auto_ask)
                    else:
                        st.session_state.output = get_secant_lecture(
                            func_str, float(a_str), float(b_str), mi, ask_fn=auto_ask)
                except Exception as e:
                    st.session_state.output = f"Error: {str(e)}"

    # ── INTERPOLATION METHODS ─────────────────────────────────────────────
    elif method in interp_methods:

        nf_mode  = None
        lag_mode = None

        if method == "Newton Forward":
            nf_mode = st.radio("Input mode",
                               ["Enter Table", "Enter Equation  f(x)"],
                               horizontal=True, key="nf_mode_r")

        if method == "Lagrange":
            lag_mode = st.radio(
                "Mode",
                ["Find f(x) — enter table + target",
                 "Get Polynomial — enter table only (no target)"],
                horizontal=True, key="lag_mode_r"
            )

        # Newton Forward — equation mode
        if method == "Newton Forward" and nf_mode == "Enter Equation  f(x)":
            st.markdown("**ℹ️ Supported syntax:** `math.sin(x)`, `math.cos(x)`, `math.log(x)`, `math.e`, `x**2`")
            nf_f = st.text_input("f(x) =", placeholder="e.g. math.sin(x) or x**2", key="nf_f")

            nc1, nc2, nc3, nc4 = st.columns(4)
            with nc1:
                nf_x0 = st.text_input("x₀", value="0",    key="nf_x0")
            with nc2:
                nf_h  = st.text_input("h",  value="0.1",  key="nf_h")
            with nc3:
                nf_n  = st.text_input("n points", value="5", key="nf_n")
            with nc4:
                nf_xt = st.text_input("x target", value="0.05", key="nf_xt")

            if st.button("🔢 Calculate (Newton Forward)", type="primary", use_container_width=True):
                with st.spinner("⏳ Calculating..."):
                    try:
                        st.session_state.output = get_newton_forward_from_eq_lecture(
                            nf_f, float(nf_x0), float(nf_h), int(nf_n), float(nf_xt),
                            ask_fn=auto_ask)
                    except Exception as e:
                        st.session_state.output = f"Error: {str(e)}"

        else:
            # Standard table input
            st.markdown("**x values:**")
            x_cols = st.columns(n)
            x_vals = []
            for j in range(n):
                with x_cols[j]:
                    v = st.text_input(f"x{j}", value=str(j),
                                      key=f"xi_{j}_{n}_{method}",
                                      label_visibility="collapsed")
                    try:
                        x_vals.append(float(v))
                    except:
                        x_vals.append(float(j))

            st.markdown("**y values:**")
            y_cols = st.columns(n)
            y_vals = []
            for j in range(n):
                with y_cols[j]:
                    v = st.text_input(f"y{j}", value="0",
                                      key=f"yi_{j}_{n}_{method}",
                                      label_visibility="collapsed")
                    try:
                        y_vals.append(float(v))
                    except:
                        y_vals.append(0.0)

            # Target
            show_target = True
            if method == "Finite Difference":
                show_target = False
            if method == "Lagrange" and lag_mode and "Polynomial" in lag_mode:
                show_target = False

            target = None
            if show_target:
                t_label = "Target y  (find x):" if method == "Lagrange Inverse" \
                          else "Target x  (find y):"
                t_str = st.text_input(t_label, value="0", key=f"tgt_{method}")
                try:
                    target = float(t_str)
                except:
                    target = 0.0

            if method == "Stirling":
                st.info(f"ℹ️  x₀ (center) = x[{n // 2}]  (auto-selected as the central point)")

            if method == "Lagrange" and not show_target:
                st.info("ℹ️  Will output the full interpolating polynomial")

            btn_label = "🔢 Get Polynomial" if (method == "Lagrange" and not show_target) \
                        else f"🔢 Calculate ({method})"

            if st.button(btn_label, type="primary", use_container_width=True):
                with st.spinner("⏳ Calculating..."):
                    try:
                        if method == "Finite Difference":
                            st.session_state.output = get_finite_difference_lecture(
                                x_vals, y_vals, ask_fn=auto_ask)
                        elif method == "Newton Forward":
                            st.session_state.output = get_newton_forward_lecture(
                                x_vals, y_vals, target, ask_fn=auto_ask)
                        elif method == "Newton Backward":
                            st.session_state.output = get_newton_backward_lecture(
                                x_vals, y_vals, target, ask_fn=auto_ask)
                        elif method == "Stirling":
                            st.session_state.output = get_stirling_lecture(
                                x_vals, y_vals, target, ask_fn=auto_ask)
                        elif method == "Lagrange":
                            if show_target:
                                st.session_state.output = get_lagrange_lecture(
                                    x_vals, y_vals, target, ask_fn=auto_ask)
                            else:
                                st.session_state.output = get_lagrange_polynomial_lecture(
                                    x_vals, y_vals, ask_fn=auto_ask)
                        elif method == "Lagrange Inverse":
                            st.session_state.output = get_lagrange_inverse_lecture(
                                x_vals, y_vals, target, ask_fn=auto_ask)
                    except Exception as e:
                        st.session_state.output = f"Error: {str(e)}"

    # ── OUTPUT ────────────────────────────────────────────────────────────
    if st.session_state.output:
        st.markdown("---")
        st.markdown("**📋 Step-by-Step Solution (Lecture Style):**")
        st.text_area("", value=st.session_state.output, height=450,
                     key="out_area", label_visibility="collapsed")
