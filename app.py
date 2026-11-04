import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Simulador ROV SF30k - Dinámica del Buque", layout="wide")

st.title("⚓ Simulador Dinámico del ROV SF30k (Basado en V. Berg, 2012)")
st.markdown("Traducción y adaptación del código base de MATLAB a Python / Streamlit para la tarea de Dinámica del Buque.")

# --- Barra lateral: Parámetros del modelo y corrientes ---
st.sidebar.header("🎛️ Parámetros de Simulación")
v_current = st.sidebar.slider("Velocidad de Corriente Marina ($v_c$ en m/s)", 0.0, 2.0, 0.5, 0.1)
thrust = st.sidebar.slider("Empuje de Propulsores ($T$ en N)", 500.0, 3000.0, 1200.0, 100.0)

# Parámetros físicos basados en la tesis del ROV SF30k
m_rb = 2500.0   # Masa del cuerpo rígido (kg)
m_a = 500.0     # Masa añadida en el eje longitudinal (Surge)
d_lin = 400.0   # Amortiguamiento lineal
d_quad = 350.0  # Amortiguamiento cuadrático

# --- Simulación temporal (Ecuación de movimiento en Surge / Principal) ---
time = np.linspace(0, 50, 250)
dt = time[1] - time[0]

u_rel = np.zeros_like(time)
x_pos = np.zeros_like(time)
u_current_arr = np.ones_like(time) * v_current

current_u_rel = 0.0
current_x = 0.0

for i in range(1, len(time)):
    # Fuerza de arrastre hidrodinámico basada en el modelo de dumping/amortiguamiento
    drag = (d_lin * current_u_rel) + (d_quad * current_u_rel * abs(current_u_rel))
    
    # Segunda ley de Newton: (M_rb + M_a) * a = T - Drag
    accel = (thrust - drag) / (m_rb + m_a)
    
    current_u_rel += accel * dt
    # Velocidad respecto al fondo (Inercial / NED) considerando la corriente en contra
    u_ground = current_u_rel - v_current
    current_x += u_ground * dt
    
    u_rel[i] = current_u_rel
    x_pos[i] = current_x

# --- Visualización de Gráficas (Equivalente al script plotear.mux) ---
col1, col2 = st.columns(2)

with col1:
    fig_x = go.Figure()
    fig_x.add_trace(go.Scatter(x=time, y=x_pos, mode='lines', name='Posición X', line=dict(color='royalblue', width=3)))
    fig_x.update_layout(
        title="Desplazamiento Longitudinal (Sistema NED)",
        xaxis_title="Tiempo (s)",
        yaxis_title="Posición (m)",
        template="plotly_white"
    )
    st.plotly_chart(fig_x, use_container_width=True)

with col2:
    fig_u = go.Figure()
    fig_u.add_trace(go.Scatter(x=time, y=u_rel, mode='lines', name='Velocidad Relativa', line=dict(color='firebrick', width=3)))
    fig_u.update_layout(
        title="Velocidad del ROV (Sistema Body)",
        xaxis_title="Tiempo (s)",
        yaxis_title="Velocidad (m/s)",
        template="plotly_white"
    )
    st.plotly_chart(fig_u, use_container_width=True)

# --- Sección de análisis para el reporte ---
st.subheader("📋 Resumen de Matrices y Componentes del Modelo")
st.info("""
* **Matrices Principales:** El sistema acopla la matriz de masa rígida y masa añadida ($M = M_{RB} + M_A$), los coeficientes de amortiguamiento lineal y no lineal (`Dumping.mux`), y las tasas de Euler (`eulerRates.mux`) para la cinemática rotacional y translacional.
* **Sistema de Referencia:** Las fuerzas y velocidades operan en el marco móvil (*Body*), mientras que las posiciones se proyectan al sistema fijo a la tierra (*NED*).
""")
