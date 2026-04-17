import streamlit as st
from fractions import Fraction
import math
import re
import sympy as sp
from itertools import permutations

# -------------------------------------------------------------------------
# نفس الفانكشنز زي ما هي (من غير أي تغيير)
# -------------------------------------------------------------------------

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


# ========================= METHODS (نفس الكود حرفيًا) =========================
def get_doolittle_lecture(A, b, max_iter=20, ask_fn=None):
    try:
        n = len(A)
        steps = ["--- Lecture Solution: Doolittle's Method ---"]
        
        # كتابة القوانين
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
            sum_details = " + ".join([f"({U[i][j]:.2f}*{x[j]:.2f})" for j in range(i+1, n)]) if i < n-1 else "0"
            x[i] = (v[i] - s) / U[i][i]
            steps.append(f"  x_{i+1} = (v_{i+1} - Sum(U*x)) / U_{i+1}{i+1} = ({v[i]:.4f} - [{sum_details}]) / {U[i][i]:.4f} = {x[i]:.4f}")

        return "\n".join(steps)
    except Exception as e:
        return f"Error: {str(e)}"


# -------------------------------------------------------------------------
# 2. Thomas Algorithm
# -------------------------------------------------------------------------
def get_thomas_lecture(A, b, max_iter=20, ask_fn=None):
    try:
        n = len(A)
        steps = ["--- Lecture Solution: Thomas Algorithm ---"]

        # ---- Tridiagonal Condition Check ----
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

        # كتابة القوانين
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


# -------------------------------------------------------------------------
# 3. Jacobi Method
# -------------------------------------------------------------------------
def make_diagonally_dominant(A, b):
    n = len(A)
    # بنعمل نسخة عشان منبوظش المصفوفة الأصلية
    A_new = [row[:] for row in A]
    b_new = b[:]
    
    for i in range(n):
        # بندور على السطر اللي فيه أكبر قيمة في العمود الحالي
        max_row = i
        for k in range(i + 1, n):
            if abs(A_new[k][i]) > abs(A_new[max_row][i]):
                max_row = k
        # بنبدل السطور في A و b
        A_new[i], A_new[max_row] = A_new[max_row], A_new[i]
        b_new[i], b_new[max_row] = b_new[max_row], b_new[i]
        
    return A_new, b_new

def get_jacobi_lecture(A, b, max_iter=20, ask_fn=None):
    try:
        n = len(A)
        steps = ["--- Lecture Solution: Jacobi Method ---"]
        
        # محاولة جعل المصفوفة Diagonally Dominant
        steps.append("\n[Attempting Row Swapping for Dominance...]")
        A, b = make_diagonally_dominant(A, b)
        
        # فحص الشرط بعد التبديل
        steps.append("\n[Condition Check: Diagonal Dominance]")
        dominant = True
        for i in range(n):
            diag = abs(A[i][i])
            off_diag = sum(abs(A[i][j]) for j in range(n) if i != j)
            res_str = "PASSED" if diag >= off_diag else "FAILED"
            steps.append(f"  Row {i+1}: |{A[i][i]}| >= {off_diag} -> {res_str}")
            if diag < off_diag: dominant = False
        
        if not dominant:
            steps.append("  ⚠️ Warning: Matrix still not dominant after swapping. May not converge.")
            steps.append("\n[Failed Condition Details (Fields):]")
            for i in range(n):
                diag = abs(A[i][i])
                off_diag = sum(abs(A[i][j]) for j in range(n) if i != j)
                if diag < off_diag:
                    steps.append(f"  ❌ FAILED FIELD  Row {i+1}: |{A[i][i]}| = {diag:.4f}  <  off-diag sum = {off_diag:.4f}")

            _ask = ask_fn if ask_fn is not None else messagebox.askyesno
            answer = _ask(
                "Diagonal Dominance Not Satisfied",
                "The matrix is NOT diagonally dominant.\n"
                "Do you want to try all row permutations to fix it and continue?\n\n"
                "Yes  →  Try to fix automatically\n"
                "No   →  Continue with current arrangement (may not converge)"
            )

            if answer:
                old_condition = []
                for i in range(n):
                    diag = abs(A[i][i])
                    off_diag = sum(abs(A[i][j]) for j in range(n) if i != j)
                    status = "PASSED ✅" if diag >= off_diag else "FAILED ❌"
                    old_condition.append(f"    Row {i+1}: |{A[i][i]}| vs off-diag {off_diag:.4f}  ->  {status}")

                A, b, fixed = try_all_permutations_dominant(A, b)

                steps.append("\n  [Before Fix - Condition Was:]")
                steps.extend(old_condition)

                if fixed:
                    steps.append("\n  [After Fix - Condition Is Now:]")
                    for i in range(n):
                        diag = abs(A[i][i])
                        off_diag = sum(abs(A[i][j]) for j in range(n) if i != j)
                        status = "PASSED ✅" if diag >= off_diag else "FAILED ❌"
                        steps.append(f"    Row {i+1}: |{A[i][i]}| >= {off_diag:.4f}  ->  {status}")
                    steps.append("  ✅ Matrix is now diagonally dominant after permutation!")
                else:
                    steps.append("  ❌ Could not achieve diagonal dominance by any row permutation. Continuing with warning...")
            else:
                steps.append("  ⚠️ User chose to continue without fixing. Results may not converge.")
        else:
            steps.append("  ✅ Success: Matrix is now dominant.")

        # ... (بقية كود الـ Iterations كما هو)
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
                steps.append(f"  ✅ Solution Converged at Iteration {k}!")
            x = x_new
            k += 1
        return "\n".join(steps)
    except Exception as e: return f"Error: {str(e)}"

# -------------------------------------------------------------------------
# 4. Gauss-Seidel Method
# -------------------------------------------------------------------------
def get_gauss_seidel_lecture(A, b, max_iter=20, ask_fn=None):
    try:
        n = len(A)
        steps = ["--- Lecture Solution: Gauss-Seidel Method ---"]
        
        # محاولة الترتيب
        A, b = make_diagonally_dominant(A, b)
        steps.append("\n[Rows rearranged for better convergence]")

        # ... (نفس منطق الفحص اللي فوق)
        steps.append("\n[Condition Check: Diagonal Dominance]")
        dominant = True
        for i in range(n):
            diag = abs(A[i][i])
            off_diag = sum(abs(A[i][j]) for j in range(n) if i != j)
            res_str = "PASSED" if diag >= off_diag else "FAILED"
            steps.append(f"  Row {i+1}: |{A[i][i]}| >= {off_diag} -> {res_str}")
            if diag < off_diag: dominant = False

        if not dominant:
            steps.append("  ⚠️ Warning: Matrix still not dominant after swapping. May not converge.")
            steps.append("\n[Failed Condition Details (Fields):]")
            for i in range(n):
                diag = abs(A[i][i])
                off_diag = sum(abs(A[i][j]) for j in range(n) if i != j)
                if diag < off_diag:
                    steps.append(f"  ❌ FAILED FIELD  Row {i+1}: |{A[i][i]}| = {diag:.4f}  <  off-diag sum = {off_diag:.4f}")

            _ask = ask_fn if ask_fn is not None else messagebox.askyesno
            answer = _ask(
                "Diagonal Dominance Not Satisfied",
                "The matrix is NOT diagonally dominant.\n"
                "Do you want to try all row permutations to fix it and continue?\n\n"
                "Yes  →  Try to fix automatically\n"
                "No   →  Continue with current arrangement (may not converge)"
            )

            if answer:
                old_condition = []
                for i in range(n):
                    diag = abs(A[i][i])
                    off_diag = sum(abs(A[i][j]) for j in range(n) if i != j)
                    status = "PASSED ✅" if diag >= off_diag else "FAILED ❌"
                    old_condition.append(f"    Row {i+1}: |{A[i][i]}| vs off-diag {off_diag:.4f}  ->  {status}")

                A, b, fixed = try_all_permutations_dominant(A, b)

                steps.append("\n  [Before Fix - Condition Was:]")
                steps.extend(old_condition)

                if fixed:
                    steps.append("\n  [After Fix - Condition Is Now:]")
                    for i in range(n):
                        diag = abs(A[i][i])
                        off_diag = sum(abs(A[i][j]) for j in range(n) if i != j)
                        status = "PASSED ✅" if diag >= off_diag else "FAILED ❌"
                        steps.append(f"    Row {i+1}: |{A[i][i]}| >= {off_diag:.4f}  ->  {status}")
                    steps.append("  ✅ Matrix is now diagonally dominant after permutation!")
                else:
                    steps.append("  ❌ Could not achieve diagonal dominance by any row permutation. Continuing with warning...")
            else:
                steps.append("  ⚠️ User chose to continue without fixing. Results may not converge.")
        else:
            steps.append("  ✅ Success: Matrix is now dominant.")

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
                steps.append(f"  ✅ Solution Converged at Iteration {k}!")
            k += 1
        return "\n".join(steps)
    except Exception as e: return f"Error: {str(e)}"

# -------------------------------------------------------------------------
# 5 & 6. Bisection & False Position
# -------------------------------------------------------------------------
def get_bracketing_lecture(method, func_str, a, b, max_iter=20, ask_fn=None):
    try:
        cleaned_str = clean_equation(func_str)
        x_sym = sp.symbols("x")
        sym_expr_str = cleaned_str.replace("log", "sp.log").replace("e", "E")
        parsed_expr = sp.sympify(sym_expr_str)
        f_lamb = sp.lambdify(x_sym, parsed_expr, "math")

        steps = [f"--- Lecture Solution: {method} Method ---"]
        
        # كتابة الشروط والقوانين
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


# -------------------------------------------------------------------------
# 7. Newton-Raphson Method
# -------------------------------------------------------------------------
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
        
        # كتابة القوانين
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


# -------------------------------------------------------------------------
# 8. Secant Method
# -------------------------------------------------------------------------
def get_secant_lecture(func_str, x0, x1, max_iter=20, ask_fn=None):
    try:
        cleaned_str = clean_equation(func_str)
        x_sym = sp.symbols("x")
        sym_expr_str = cleaned_str.replace("log", "sp.log").replace("e", "E")
        parsed_expr = sp.sympify(sym_expr_str)
        f_lamb = sp.lambdify(x_sym, parsed_expr, "math")

        steps = ["--- Lecture Solution: Secant Method ---"]
        
        # كتابة القوانين
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

#

# -------------------------------------------------------------------------
# Streamlit UI
# -------------------------------------------------------------------------

st.set_page_config(layout="wide", page_title="Matrix Multi-Calculator")

st.title("📊 Matrix Multi-Calculator & Numerical Methods")

# ---------------- Calculator ----------------
st.sidebar.header("🧮 Standard Calculator")

calc_input = st.sidebar.text_input("Expression")

if st.sidebar.button("Calculate"):
    try:
        st.sidebar.success(eval(calc_input))
    except:
        st.sidebar.error("Invalid Expression")

# ---------------- Main ----------------
methods = ["Doolittle", "Thomas", "Jacobi", "Gauss-Seidel",
           "Bisection", "False Position", "Newton", "Secant"]

method = st.selectbox("Select Method", methods)
max_iter = st.number_input("Max Iterations", value=20, min_value=1)

# ================= MATRIX METHODS =================
if method in ["Doolittle", "Thomas", "Jacobi", "Gauss-Seidel"]:

    n = st.selectbox("Matrix Size", [2,3,4,5])

    st.subheader("Matrix A")
    A = []
    for i in range(n):
        row = st.columns(n)
        A.append([row[j].number_input(f"A[{i+1},{j+1}]", key=f"a{i}{j}") for j in range(n)])

    st.subheader("Vector b")
    b = [st.number_input(f"b[{i+1}]", key=f"b{i}") for i in range(n)]

    if st.button("Solve System"):
        with st.spinner("Calculating..."):

            if method == "Doolittle":
                out = get_doolittle_lecture(A, b, max_iter)
            elif method == "Thomas":
                out = get_thomas_lecture(A, b, max_iter)
            elif method == "Jacobi":
                out = get_jacobi_lecture(A, b, max_iter)
            else:
                out = get_gauss_seidel_lecture(A, b, max_iter)

            st.text_area("Result", out, height=400)

# ================= EQUATION METHODS =================
else:
    func = st.text_input("f(x)")

    if method in ["Bisection", "False Position"]:
        a = st.number_input("a", value=1.0)
        b = st.number_input("b", value=2.0)

    elif method == "Newton":
        x0 = st.number_input("x0", value=1.0)

    elif method == "Secant":
        x0 = st.number_input("x0", value=1.0)
        x1 = st.number_input("x1", value=2.0)

    if st.button("Solve Equation"):
        with st.spinner("Calculating..."):
            try:
                if method in ["Bisection", "False Position"]:
                    out = get_bracketing_lecture(method, func, a, b, max_iter)
                elif method == "Newton":
                    out = get_newton_lecture(func, x0, max_iter)
                else:
                    out = get_secant_lecture(func, x0, x1, max_iter)

                st.text_area("Result", out, height=400)

            except Exception as e:
                st.error(str(e))
