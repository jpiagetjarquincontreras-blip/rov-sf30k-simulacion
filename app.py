import streamlit as st
import numpy as np
import plotly.graph_objects as go

st.set_page_config(page_title="Simulador y Teoría - ROV SF30k", layout="wide")

st.title("⚓ Simulador Dinámico y Análisis Teórico - ROV SF30k")
st.markdown("Herramienta interactiva y guía teórica basada en la tesis de Viktor Berg (2012) para Dinámica del Buque.")

# --- Creación de pestañas ---
tab_sim, tab_teo = st.tabs(["🚀 Simulador Interactivo", "📚 Guía Teórica y Explicativa"])

# ==========================================
# PESTAÑA 1: SIMULADOR INTERACTIVO
# ==========================================
with tab_sim:
    st.subheader("📊 1. Matrices del Modelo Dinámico (6 DoF)")
    col_m1, col_m2 = st.columns(2)

    with col_m1:
        st.markdown("**Matriz de Masa Total ($M = M_{RB} + M_A$)**")
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

    with col_m2:
        st.markdown("**Matriz de Amortiguamiento ($D$)**")
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

    st.markdown("---")

    st.subheader("🌊 2. Simulación Temporal: Comparativa ante Corrientes Marinas")
    st.markdown("Evaluación del comportamiento del ROV ante tres velocidades de corriente distintas ($0.0\\text{ m/s}$, $0.5\\text{ m/s}$ y $1.2\\text{ m/s}$)[cite: 1].")

    m_total = 3000.0 
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
            u_ground = curr_u_rel - v_c  
            curr_x += u_ground * dt
            
            u_rel[i] = curr_u_rel
            x_pos[i] = curr_x
        return x_pos, u_rel

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
        fig_pos.update_layout(title="Desplazamiento Longitudinal (Sistema NED)", xaxis_title="Tiempo (s)", yaxis_title="Posición X (m)", template="plotly_white")
        st.plotly_chart(fig_pos, use_container_width=True)

    with col_g2:
        fig_vel = go.Figure()
        fig_vel.add_trace(go.Scatter(x=time, y=u1, mode='lines', name=f'Corriente: {v1} m/s', line=dict(width=3)))
        fig_vel.add_trace(go.Scatter(x=time, y=u2, mode='lines', name=f'Corriente: {v2} m/s', line=dict(width=3)))
        fig_vel.add_trace(go.Scatter(x=time, y=u3, mode='lines', name=f'Corriente: {v3} m/s', line=dict(width=3)))
        fig_vel.update_layout(title="Velocidad Efectiva (Sistema Body)", xaxis_title="Tiempo (s)", yaxis_title="Velocidad (m/s)", template="plotly_white")
        st.plotly_chart(fig_vel, use_container_width=True)

# ==========================================
# PESTAÑA 2: GUÍA TEÓRICA Y EXPLICATIVA
# ==========================================
with tab_teo:
    st.header("📖 Guía Teórica y Metodológica Detallada")
    st.markdown("Esta sección documenta el sustento físico, matemático y cinemático implementado en el modelo del ROV SF30k.")

    st.markdown("---")
    st.subheader("1. 🛠️ Simplificación del Modelo Original")
    st.write("""
    En la tesis de Viktor Berg (2012), el modelo dinámico completo de un vehículo submarino se somete a ciertas simplificaciones prácticas para facilitar su análisis computacional y control[cite: 1]:
    * **Desacoplamiento estructural:** Se desprecian o minimizan los acoplamientos cruzados de bajo impacto entre ciertos grados de libertad (por ejemplo, interacciones menores entre *Roll* y *Sway*).
    * **Planos de simetría:** Se asume simetría geométrica y hidrodinámica bivalente (puerto-estribor), lo que anula diversos términos fuera de la diagonal principal en las matrices de inercia y amortiguamiento.
    * **Tratamiento del umbilical:** Las fuerzas hidrodinámicas y la tensión ejercida por el cable umbilical se omiten o se consideran perturbaciones externas independientes, permitiendo aislar la respuesta pura del vehículo ante el medio.
    """)

    st.markdown("---")
    st.subheader("2. 📐 Matrices de Movimiento (6 Grados de Libertad)")
    st.write("""
    El movimiento tridimensional de la embarcación o vehículo sumergido se rige por la ecuación matricial general de Fossen:
    """)
    st.latex(r"M \dot{\nu} + C(\nu)\nu + D(\nu)\nu + g(\eta) = \tau")
    st.write("""
    * **Matriz de Masa Total ($M = M_{RB} + M_A$):** Combina la matriz de cuerpo rígido ($M_{RB}$) y la masa añadida ($M_A$), la cual representa la inercia del fluido circundante que el ROV debe acelerar junto con su propia masa. Se divide conceptualmente en:
      * **Movimientos Traslacionales (Filas/Columnas 1 a 3):** *Surge* (avance/retroceso), *Sway* (deriva lateral) y *Heave* (ascenso/descenso).
      * **Movimientos Rotacionales (Filas/Columnas 4 a 6):** *Roll* (balanceo), *Pitch* (cabeceo) y *Yaw* (guiñada).
    * **Matriz de Amortiguamiento ($D$):** Agrupa los efectos de resistencia hidrodinámica. Incluye componentes **lineales** (fricción cutánea a baja velocidad) y **cuadráticos** (arrastre de presión y separación de flujo, característicos de `Dumping.mux`).
    """)

    st.markdown("---")
    st.subheader("3. 🌐 Sistemas de Referencia (Body vs. NED)")
    st.write("""
    Para describir correctamente la física del vehículo, se emplean dos marcos coordenados distintos:
    * **Sistema Fijo al Cuerpo (Body Frame):** Sistema móvil solidario al centro de gravedad del ROV. Las velocidades ($\nu$) y las fuerzas de empuje de los propulsores ($\tau$) se calculan en este marco porque la orientación de los propulsores no cambia respecto al chasis del vehículo.
    * **Sistema Fijo a la Tierra (NED - North-East-Down):** Sistema inercial utilizado para rastrear la posición global ($\eta$) y la trayectoria real del ROV sobre el fondo marino[cite: 1]. La conversión de velocidades del sistema *Body* al sistema *NED* se realiza mediante matrices de rotación de Euler.
    """)

    st.markdown("---")
    st.subheader("4. 📈 Interpretación de las Gráficas y Resultados")
    st.write("""
    * **Gráfica de Desplazamiento Longitudinal (Sistema NED):** Muestra cómo avanza la posición en el eje $X$ con respecto al tiempo. 
      * Cuando la corriente marina es cero ($0.0\\text{ m/s}$), el avance es constante tras superar la aceleración inicial.
      * A medida que la velocidad de la corriente en contra aumenta ($0.5\\text{ m/s}$ y $1.2\\text{ m/s}$), la pendiente de la línea disminuye drásticamente, reflejando cómo el flujo marino frena el avance efectivo del vehículo sobre el fondo.
    * **Gráfica de Velocidad Efectiva (Sistema Body):** Ilustra la transición transitoria del vehículo. Comienza en cero, experimenta una curva ascendente debido a la inercia (masa total) y se estabiliza al alcanzar su velocidad terminal, punto exacto donde la fuerza de empuje de los propulsores equilibra por completo a la resistencia hidrodinámica (*drag*).
    """)
