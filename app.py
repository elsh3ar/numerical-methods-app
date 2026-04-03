from fractions import Fraction
import math
import re
import sympy as sp
import streamlit as st

# إعدادات الصفحة عشان تظهر بشكل مريح على الموبايل والكمبيوتر
st.set_page_config(page_title="Numerical Methods Calculator", layout="centered")

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
    except Exception as e:
        return f"Error: {str(e)}"

# -------------------------------------------------------------------------
# 2. Thomas Algorithm
# -------------------------------------------------------------------------
def get_thomas_lecture(A, b):
    try:
        n = len(A)
        steps = ["--- Lecture Solution: Thomas Algorithm ---"]
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
def get_jacobi_lecture(A, b):
    try:
        n = len(A)
        steps = ["--- Lecture Solution: Jacobi Method ---"]
        steps.append("\n[Condition Check: Diagonal Dominance]")
        steps.append("  Rule: |a_ii| >= Sum(|a_ij|) for all j != i")
        dominant = True
        for i in range(n):
            diag = abs(A[i][i])
            off_diag = sum(abs(A[i][j]) for j in range(n) if i != j)
            res_str = "PASSED" if diag >= off_diag else "FAILED"
            steps.append(f"  Row {i+1}: |{A[i][i]}| >= {off_diag} -> {res_str}")
            if diag < off_diag: dominant = False
        
        if not dominant:
            steps.append("  ⚠️ Warning: Matrix is not diagonally dominant. Convergence not guaranteed.")
        else:
            steps.append("  ✅ Success: Matrix is diagonally dominant.")

        steps.append("\n[Laws & Formulas]")
        steps.append("  x_i^(k) = (b_i - Sum(a_ij * x_j^(k-1))) / a_ii")

        x = [0.0] * n
        tol = 0.0001
        converged = False
        k = 1

        while not converged and k <= 20:
            steps.append(f"\n🔴 Iteration {k}:")
            x_new = [0.0] * n
            for i in range(n):
                s = sum(A[i][j] * x[j] for j in range(n) if i != j)
                sub_details = " + ".join([f"({A[i][j]}*{x[j]:.3f})" for j in range(n) if i != j])
                x_new[i] = (b[i] - s) / A[i][i]
                steps.append(f"  x_{i+1}^({k}) = ({b[i]} - [{sub_details}]) / {A[i][i]} = {x_new[i]:.4f}")

            converged = all(abs(x_new[i] - x[i]) < tol for i in range(n))
            x = x_new
            k += 1

        return "\n".join(steps)
    except Exception as e:
        return f"Error: {str(e)}"

# -------------------------------------------------------------------------
# 4. Gauss-Seidel Method
# -------------------------------------------------------------------------
def get_gauss_seidel_lecture(A, b):
    try:
        n = len(A)
        steps = ["--- Lecture Solution: Gauss-Seidel Method ---"]
        steps.append("\n[Condition Check: Diagonal Dominance]")
        steps.append("  Rule: |a_ii| >= Sum(|a_ij|) for all j != i")
        dominant = True
        for i in range(n):
            diag = abs(A[i][i])
            off_diag = sum(abs(A[i][j]) for j in range(n) if i != j)
            res_str = "PASSED" if diag >= off_diag else "FAILED"
            steps.append(f"  Row {i+1}: |{A[i][i]}| >= {off_diag} -> {res_str}")
            if diag < off_diag: dominant = False
        
        if not dominant:
            steps.append("  ⚠️ Warning: Matrix is not diagonally dominant. Convergence not guaranteed.")
        else:
            steps.append("  ✅ Success: Matrix is diagonally dominant.")

        steps.append("\n[Laws & Formulas]")
        steps.append("  x_i^(k) = (b_i - Sum(a_ij * x_j_updated)) / a_ii")

        x = [0.0] * n
        tol = 0.0001
        converged = False
        k = 1

        while not converged and k <= 20:
            steps.append(f"\n🔴 Iteration {k}:")
            x_old = x.copy()
            for i in range(n):
                s = sum(A[i][j] * x[j] for j in range(n) if i != j)
                sub_details = " + ".join([f"({A[i][j]}*{x[j]:.3f})" for j in range(n) if i != j])
                x[i] = (b[i] - s) / A[i][i]
                steps.append(f"  x_{i+1}^({k}) = ({b[i]} - [{sub_details}]) / {A[i][i]} = {x[i]:.4f}")

            converged = all(abs(x[i] - x_old[i]) < tol for i in range(n))
            k += 1

        return "\n".join(steps)
    except Exception as e:
        return f"Error: {str(e)}"

# -------------------------------------------------------------------------
# 5 & 6. Bisection & False Position
# -------------------------------------------------------------------------
def get_bracketing_lecture(method, func_str, a, b):
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

        while k <= 20:
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
                steps.append(f"\n✅ Root Found at x_r = {c:.4f}")
                break

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
def get_newton_lecture(func_str, x0):
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

        while k <= 20:
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
                steps.append(f"\n✅ Root Found at x = {x_new:.4f}")
                break
            x = x_new
            k += 1

        return "\n".join(steps)
    except Exception as e:
        return f"Error: {str(e)}"

# -------------------------------------------------------------------------
# 8. Secant Method
# -------------------------------------------------------------------------
def get_secant_lecture(func_str, x0, x1):
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

        while k <= 20:
            f0, f1 = f_lamb(x0), f_lamb(x1)
            if abs(f1 - f0) < 1e-10:
                break
            
            x_new = x1 - f1 * (x1 - x0) / (f1 - f0)
            steps.append(f"\n🔴 Iteration {k}:")
            steps.append(f"  x_0 = {x0:.4f}, f(x_0) = {f0:.4f}")
            steps.append(f"  x_1 = {x1:.4f}, f(x_1) = {f1:.4f}")
            steps.append(f"  Formula: x_new = {x1:.4f} - [{f1:.4f}*({x1:.4f} - {x0:.4f})] / [{f1:.4f} - ({f0:.4f})] = {x_new:.4f}")

            if abs(x_new - x1) < tol:
                steps.append(f"\n✅ Root Found at x = {x_new:.4f}")
                break
            x0, x1 = x1, x_new
            k += 1

        return "\n".join(steps)
    except Exception as e:
        return f"Error: {str(e)}"

# -------------------------------------------------------------------------
# واجهة الويب باستخدام Streamlit
# -------------------------------------------------------------------------
st.title("🧮 Numerical Methods Calculator")
st.markdown("This app runs perfectly on Mobile and PC.")
st.divider()

# القائمة المنسدلة لاختيار الطريقة
methods_list = ["Doolittle", "Thomas", "Jacobi", "Gauss-Seidel", "Bisection", "False Position", "Newton", "Secant"]
selected_method = st.selectbox("Select Method:", methods_list)

# 1. لو الطريقة مصفوفات (Systems)
if selected_method in ["Doolittle", "Thomas", "Jacobi", "Gauss-Seidel"]:
    size = st.selectbox("Matrix Size (n):", [2, 3, 4, 5], index=1)
    
    st.write("Enter Matrix [A] and Vector [b]:")
    
    matrix_A = []
    vector_b = []
    
    # بناء شبكة الإدخال
    for i in range(size):
        cols = st.columns(size + 2)
        row_vals = []
        for j in range(size):
            with cols[j]:
                val = st.number_input(f"A[{i+1},{j+1}]", key=f"A_{i}_{j}", format="%.2f")
                row_vals.append(val)
        matrix_A.append(row_vals)
        
        with cols[size]:
            st.markdown("<h3 style='text-align: center; margin-top: 25px;'>=</h3>", unsafe_allow_html=True)
            
        with cols[size + 1]:
            b_val = st.number_input(f"b[{i+1}]", key=f"b_{i}", format="%.2f")
            vector_b.append(b_val)
            
    if st.button("Calculate System", type="primary"):
        if selected_method == "Doolittle": out = get_doolittle_lecture(matrix_A, vector_b)
        elif selected_method == "Thomas": out = get_thomas_lecture(matrix_A, vector_b)
        elif selected_method == "Jacobi": out = get_jacobi_lecture(matrix_A, vector_b)
        else: out = get_gauss_seidel_lecture(matrix_A, vector_b)
        
        st.divider()
        st.write("### Step-by-Step Solution:")
        st.code(out, language="text")

# 2. لو الطريقة إيجاد جذور معادلات (Non-linear)
else:
    st.write("Enter Function Details:")
    func_str = st.text_input("f(x):", value="x^3 - x - 1")
    
    col1, col2 = st.columns(2)
    
    if selected_method in ["Bisection", "False Position"]:
        with col1:
            a = st.number_input("Enter a:", value=1.0)
        with col2:
            b = st.number_input("Enter b:", value=2.0)
            
    elif selected_method == "Newton":
        with col1:
            x0 = st.number_input("Enter x0:", value=1.0)
            
    elif selected_method == "Secant":
        with col1:
            x0 = st.number_input("Enter x0:", value=1.0)
        with col2:
            x1 = st.number_input("Enter x1:", value=2.0)
            
    if st.button("Calculate Root", type="primary"):
        if selected_method in ["Bisection", "False Position"]:
            out = get_bracketing_lecture(selected_method, func_str, a, b)
        elif selected_method == "Newton":
            out = get_newton_lecture(func_str, x0)
        else:
            out = get_secant_lecture(func_str, x0, x1)
            
        st.divider()
        st.write("### Step-by-Step Solution:")
        st.code(out, language="text")