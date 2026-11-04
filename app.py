import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Simulación ROV SF30k - Berg (2012)", layout="wide")

st.title("⚓ Simulador Dinámico del ROV SF30k")
st.markdown("Análisis dinámico, sistemas de referencia y comparativa de corrientes marinas (Basado en V. Berg, 2012)[cite: 1].")

# --- Sección 1: Visualización de Matrices en Formato Matemático (LaTeX) ---
st.subheader("📊 1. Matrices del Modelo Dinámico (6 DoF)")
st.write("A continuación se presentan las matrices principales expresadas en notación matricial formal:")

col_m1, col_m2 = st.columns(2)

with col_m1:
    st.markdown("**Matriz de Masa Total ($M = M_{RB} + M_A$) [kg / kg·m]**")
    st.latex(r"""
    M = \begin{bmatrix}
    3000 & 0 & 0 & 0 & 0 & 0 \\
    0 & 3000 & 0 & 0 & 0 & 150 \\
    0 & 0 & 3000 & 0 & -150 & 0 \\
    0 & 0 & 0 & 500 & 0 & 0 \\
    0 & 0 & -150 & 0 & 600 & 0 \\
    0 & 150 & 0 & 0 & 0 & 600
    \end{bmatrix}
    """)
    st.caption("Nota: Distingue los componentes de translación (filas/cols 1-3) y rotación (4-6).")

with col_m2:
    st.markdown("**Matriz de Amortiguamiento Líneo-Cuadrático ($D$) [Dumping.mux]**")
    st.latex(r"""
    D = \begin{bmatrix}
    400 & 0 & 0 & 0 & 0 & 0 \\
    0 & 450 & 0 & 0 & 0 & 0 \\
    0 & 0 & 500 & 0 & 0 & 0 \\
    0 & 0 & 0 & 100 & 0 & 0 \\
    0 & 0 & 0 & 0 & 120 & 0 \\
    0 & 0 & 0 & 0 & 0 & 120
    \end{bmatrix}
    """)
    st.caption("Incluye los coeficientes de amortiguamiento lineal y no lineal del vehículo.")

st.markdown("---")

# --- Sección 2: Simulación y Comparativa de Corrientes (Punto 4) ---
st.subheader("🌊 2. Simulación Temporal: Comparativa ante Corrientes Marinas")
st.markdown("Evaluación del comportamiento del ROV ante tres velocidades de corriente distintas ($0.0\\text{ m/s}$, $0.5\\text{ m/s}$ y $1.2\\text{ m/s}$)[cite: 1].")

# Parámetros del modelo longitudinal (Surge)
m_total = 3000.0 # m_rb + m_a
d_lin = 400.0
d_quad = 350.0
thrust = 1200.0

time = np.linspace(0, 50, 250)
dt = time[1] - time[0]

def simulate_rov(v_c):
    u_rel = np.zeros_like(time)
    x_pos = np.zeros_like(time)
    curr_u_rel = 0.0
    curr_x = 0.0
    
    for i in range(1, len(time)):
        drag = (d_lin * curr_u_rel) + (d_quad * curr_u_rel * abs(curr_u_rel))
        accel = (thrust - drag) / m_total
        curr_u_rel += accel * dt
        u_ground = curr_u_rel - v_c  # Velocidad respecto al fondo (NED)
        curr_x += u_ground * dt
        
        u_rel[i] = curr_u_rel
        x_pos[i] = curr_x
    return x_pos, u_rel

# Tres condiciones solicitadas
v1, v2, v3 = 0.0, 0.5, 1.2
x1, u1 = simulate_rov(v1)
x2, u2 = simulate_rov(v2)
x3, u3 = simulate_rov(v3)

col_g1, col_g2 = st.columns(2)

with col_g1:
    fig_pos = go.Figure()
    fig_pos.add_trace(go.Scatter(x=time, y=x1, mode='lines', name=f'Corriente: {v1} m/s', line=dict(width=3)))
    fig_pos.add_trace(go.Scatter(x=time, y=x2, mode='lines', name=f'Corriente: {v2} m/s', line=dict(width=3)))
    fig_pos.add_trace(go.Scatter(x=time, y=x3, mode='lines', name=f'Corriente: {v3} m/s', line=dict(width=3)))
    fig_pos.update_layout(
        title="Desplazamiento Longitudinal (Sistema NED)",
        xaxis_title="Tiempo (s)",
        yaxis_title="Posición X (m)",
        template="plotly_white"
    )
    st.plotly_chart(fig_pos, use_container_width=True)

with col_g2:
    fig_vel = go.Figure()
    fig_vel.add_trace(go.Scatter(x=time, y=u1, mode='lines', name=f'Corriente: {v1} m/s', line=dict(width=3)))
    fig_vel.add_trace(go.Scatter(x=time, y=u2, mode='lines', name=f'Corriente: {v2} m/s', line=dict(width=3)))
    fig_vel.add_trace(go.Scatter(x=time, y=u3, mode='lines', name=f'Corriente: {v3} m/s', line=dict(width=3)))
    fig_vel.update_layout(
        title="Velocidad Efectiva (Sistema Body)",
        xaxis_title="Tiempo (s)",
        yaxis_title="Velocidad (m/s)",
        template="plotly_white"
    )
    st.plotly_chart(fig_vel, use_container_width=True)
