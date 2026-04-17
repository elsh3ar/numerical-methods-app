import streamlit as st
import sympy as sp
import math
import re
from itertools import permutations

# إعدادات الصفحة
st.set_page_config(page_title="Matrix Multi-Calculator", layout="wide")

# -------------------------------------------------------------------------
# دالة تنظيف وقراءة المعادلات الرياضية
# -------------------------------------------------------------------------
def clean_equation(eq_str):
    eq_str = eq_str.replace("^", "**")
    eq_str = re.sub(r"(\d)([a-zA-Z])", r"\1*\2", eq_str)
    eq_str = eq_str.replace(")(", ")*(")
    eq_str = eq_str.replace("math.e", "e").replace("math.log", "log")
    return eq_str

# -------------------------------------------------------------------------
# helper: try all row permutations to achieve diagonal dominance
# -------------------------------------------------------------------------
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

# -------------------------------------------------------------------------
# 1. Doolittle's Method
# -------------------------------------------------------------------------
def get_doolittle_lecture(A, b):
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
            sum_details = " + ".join([f"({U[i][j]:.2f}*{x[j]:.2f})" for j in range(i+1, n)]) if i < n-1 else "0"
            x[i] = (v[i] - s) / U[i][i]
            steps.append(f"  x_{i+1} = (v_{i+1} - Sum(U*x)) / U_{i+1}{i+1} = ({v[i]:.4f} - [{sum_details}]) / {U[i][i]:.4f} = {x[i]:.4f}")

        return "\n".join(steps)
    except Exception as e: return f"Error: {str(e)}"

# -------------------------------------------------------------------------
# 2. Thomas Algorithm
# -------------------------------------------------------------------------
def get_thomas_lecture(A, b):
    try:
        n = len(A)
        steps = ["--- Lecture Solution: Thomas Algorithm ---"]
        is_tri = True
        for i in range(n):
            for j in range(n):
                if abs(i - j) > 1 and abs(A[i][j]) > 1e-10:
                    is_tri = False
        if not is_tri:
            return "❌ Failed: Matrix is NOT tridiagonal."

        d = [A[i][i] for i in range(n)]
        a = [0] + [A[i][i - 1] for i in range(1, n)]
        c = [A[i][i + 1] for i in range(n - 1)] + [0]
        y, z = [0] * n, [0] * n

        y[0] = d[0]
        steps.append(f"y_1 = {y[0]}")
        for i in range(1, n):
            y[i] = d[i] - (a[i] * c[i - 1]) / y[i - 1]
            steps.append(f"y_{i+1} = {y[i]:.4f}")

        z[0] = b[0] / y[0]
        for i in range(1, n):
            z[i] = (b[i] - a[i] * z[i - 1]) / y[i]
            steps.append(f"z_{i+1} = {z[i]:.4f}")

        x = [0] * n
        x[-1] = z[-1]
        for i in range(n - 2, -1, -1):
            x[i] = z[i] - (c[i] * x[i + 1]) / y[i]
            steps.append(f"x_{i+1} = {x[i]:.4f}")
        return "\n".join(steps)
    except Exception as e: return f"Error: {str(e)}"

# -------------------------------------------------------------------------
# 3. Jacobi Method
# -------------------------------------------------------------------------
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

def get_jacobi_lecture(A, b, max_iter=20):
    try:
        n = len(A)
        steps = ["--- Lecture Solution: Jacobi Method ---"]
        A, b = make_diagonally_dominant(A, b)
        
        x = [0.0] * n
        tol = 0.0001
        for k in range(1, max_iter + 1):
            steps.append(f"\n🔴 Iteration {k}:")
            x_new = [0.0] * n
            for i in range(n):
                s = sum(A[i][j] * x[j] for j in range(n) if i != j)
                x_new[i] = (b[i] - s) / A[i][i]
                steps.append(f"  x_{i+1}^({k}) = {x_new[i]:.4f}")
            if all(abs(x_new[i] - x[i]) < tol for i in range(n)):
                steps.append(f"✅ Solution Converged!")
                break
            x = x_new
        return "\n".join(steps)
    except Exception as e: return f"Error: {str(e)}"

# -------------------------------------------------------------------------
# 4. Gauss-Seidel Method
# -------------------------------------------------------------------------
def get_gauss_seidel_lecture(A, b, max_iter=20):
    try:
        n = len(A)
        steps = ["--- Lecture Solution: Gauss-Seidel ---"]
        A, b = make_diagonally_dominant(A, b)
        x = [0.0] * n
        tol = 0.0001
        for k in range(1, max_iter + 1):
            steps.append(f"\n🔴 Iteration {k}:")
            x_old = x.copy()
            for i in range(n):
                s = sum(A[i][j] * x[j] for j in range(n) if i != j)
                x[i] = (b[i] - s) / A[i][i]
                steps.append(f"  x_{i+1}^({k}) = {x[i]:.4f}")
            if all(abs(x[i] - x_old[i]) < tol for i in range(n)):
                steps.append("✅ Converged!")
                break
        return "\n".join(steps)
    except Exception as e: return f"Error: {str(e)}"

# -------------------------------------------------------------------------
# 5 & 6. Bisection & False Position
# -------------------------------------------------------------------------
def get_bracketing_lecture(method, func_str, a, b, max_iter=20):
    try:
        cleaned_str = clean_equation(func_str)
        x_sym = sp.symbols("x")
        sym_expr_str = cleaned_str.replace("log", "sp.log").replace("e", "E")
        parsed_expr = sp.sympify(sym_expr_str)
        f_lamb = sp.lambdify(x_sym, parsed_expr, "math")

        steps = [f"--- Lecture Solution: {method} Method ---"]
        fa, fb = f_lamb(a), f_lamb(b)
        if fa * fb >= 0: return "❌ Failed: f(a)*f(b) >= 0."

        for k in range(1, max_iter + 1):
            fa, fb = f_lamb(a), f_lamb(b)
            if method == "Bisection": c = (a + b) / 2
            else: c = (a * fb - b * fa) / (fb - fa)
            fc = f_lamb(c)
            steps.append(f"Iter {k}: x_r={c:.4f}, f(x_r)={fc:.4f}")
            if abs(fc) < 0.0001: break
            if fa * fc < 0: b = c
            else: a = c
        return "\n".join(steps)
    except Exception as e: return f"Error: {str(e)}"

# -------------------------------------------------------------------------
# Streamlit UI
# -------------------------------------------------------------------------
st.title("🔢 Matrix Multi-Calculator & Methods (Ahmed Elshaar)")

# Sidebar for Standard Calculator
with st.sidebar:
    st.header("🧮 Standard Calc")
    if 'calc_val' not in st.session_state: st.session_state.calc_val = ""
    
    def update_calc(val):
        if val == "=":
            try: st.session_state.calc_val = str(eval(st.session_state.calc_val))
            except: st.session_state.calc_val = "Error"
        elif val == "C": st.session_state.calc_val = ""
        else: st.session_state.calc_val += val

    st.text_input("Display", value=st.session_state.calc_val, key="disp")
    cols = st.columns(4)
    btns = ["7","8","9","/","4","5","6","*","1","2","3","-","C","0","=","+"]
    for i, b in enumerate(btns):
        if cols[i%4].button(b, key=f"btn_{b}_{i}"): update_calc(b); st.rerun()

# Main Interface
col_ctrl1, col_ctrl2, col_ctrl3 = st.columns(3)
method = col_ctrl1.selectbox("Select Method", ["Doolittle", "Thomas", "Jacobi", "Gauss-Seidel", "Bisection", "False Position", "Newton", "Secant"])
n_size = col_ctrl2.number_input("Matrix Size (n)", min_value=2, max_value=10, value=3)
max_iters = col_ctrl3.number_input("Max Iterations", value=20)

if method in ["Doolittle", "Thomas", "Jacobi", "Gauss-Seidel"]:
    st.subheader(f"Enter Matrix [A] and Vector [b]")
    matrix_a = []
    vector_b = []
    
    cols = st.columns(n_size + 1)
    for i in range(n_size):
        row = []
        for j in range(n_size):
            val = cols[j].number_input(f"A[{i+1},{j+1}]", key=f"a_{i}_{j}", format="%.2f")
            row.append(val)
        matrix_a.append(row)
        val_b = cols[n_size].number_input(f"b[{i+1}]", key=f"b_{i}", format="%.2f")
        vector_b.append(val_b)

    if st.button("Calculate System"):
        if method == "Doolittle": res = get_doolittle_lecture(matrix_a, vector_b)
        elif method == "Thomas": res = get_thomas_lecture(matrix_a, vector_b)
        elif method == "Jacobi": res = get_jacobi_lecture(matrix_a, vector_b, max_iters)
        else: res = get_gauss_seidel_lecture(matrix_a, vector_b, max_iters)
        st.text_area("Solution Steps", res, height=400)

else:
    st.subheader("Equation Solver")
    func_input = st.text_input("f(x)", "x**2 - 4")
    c1, c2 = st.columns(2)
    if method in ["Bisection", "False Position", "Secant"]:
        p1 = c1.number_input("Point 1 (a/x0)", value=0.0)
        p2 = c2.number_input("Point 2 (b/x1)", value=2.0)
    else:
        p1 = c1.number_input("Initial Guess (x0)", value=1.0)
        p2 = 0

    if st.button("Solve Equation"):
        if method in ["Bisection", "False Position"]:
            res = get_bracketing_lecture(method, func_input, p1, p2, max_iters)
        # مكنك إضافة دوال Newton و Secant هنا بنفس النمط
        st.text_area("Solution Steps", res, height=400)
