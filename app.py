import numpy as np
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Simulador y Teoría - ROV SF30k", layout="wide"
)

st.title("⚓ Simulador Dinámico y Análisis Teórico - ROV SF30k")
st.markdown(
    "Herramienta interactiva y guía teórica basada en la tesis de Viktor Berg"
    " (2012) para Dinámica del Buque."
)

# --- Menú Lateral (Sidebar) para Parámetros y Controles ---
st.sidebar.header("🎛️ Panel de Control y Propulsión")
st.sidebar.markdown(
    "Modifica individualmente el factor de operación de cada propulsor y la"
    " corriente para ver el comportamiento en tiempo real."
)

# 1. Sliders individuales para los 6 propulsores (factores de 0.0 a 1.0)
st.sidebar.subheader("Factores de Propulsores (u)")
p1 = st.sidebar.slider("Propulsor 1 (Surge / Principal)", 0.0, 1.0, 1.0, 0.05)
p2 = st.sidebar.slider("Propulsor 2 (Estribor)", 0.0, 1.0, 1.0, 0.05)
p3 = st.sidebar.slider("Propulsor 3 (Babor)", 0.0, 1.0, 1.0, 0.05)
p4 = st.sidebar.slider(
    "Propulsor 4 (Auxiliar / Contragiro)", 0.0, 1.0, 1.0, 0.05
)
p5 = st.sidebar.slider("Propulsor 5 (Heave - Vertical)", 0.0, 1.0, 1.0, 0.05)
p6 = st.sidebar.slider("Propulsor 6 (Heave - Vertical)", 0.0, 1.0, 1.0, 0.05)

# Empuje base nominal máximo y cálculo del empuje efectivo longitudinal
thrust_base = st.sidebar.slider(
    "Empuje Nominal Máximo ($T_{base}$ en N)", 500.0, 3000.0, 1200.0, 100.0
)
# El empuje longitudinal efectivo depende del balance entre propulsores principales (ej. P1 y P4)
thrust_input = thrust_base * (0.5 * p1 + 0.5 * p4)

st.sidebar.markdown("---")
st.sidebar.subheader("🌊 Entorno Ambiental (Corrientes)")
# Slider interactivo para la corriente
corriente_usuario = st.sidebar.slider(
    "Velocidad de Corriente en Contra (m/s)", 0.0, 1.5, 0.5, 0.1
)

# --- Creación de pestañas ---
tab_sim, tab_teo = st.tabs(
    ["🚀 Simulador Interactivo", "📚 Guía Teórica y Explicativa"]
)

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

  st.subheader("🌊 2. Simulación Temporal: Comparativa y Valores Clave")
  st.markdown(
      "Resultados numéricos exactos evaluando el estado actual de los"
      f" propulsores y una corriente de {corriente_usuario} m/s[cite: 1]."
  )

  m_total = 3000.0
  d_lin = 400.0
  d_quad = 350.0

  time = np.linspace(0, 50, 250)
  dt = time[1] - time[0]


  def simulate_rov(v_c, thrust_val):
    u_rel = np.zeros_like(time)
    x_pos = np.zeros_like(time)
    curr_u_rel = 0.0
    curr_x = 0.0

    for i in range(1, len(time)):
      drag = (d_lin * curr_u_rel) + (d_quad * curr_u_rel * abs(curr_u_rel))
      accel = (thrust_val - drag) / m_total
      curr_u_rel += accel * dt
      u_ground = curr_u_rel - v_c
      curr_x += u_ground * dt

      u_rel[i] = curr_u_rel
      x_pos[i] = curr_x
    return x_pos, u_rel


  # Evaluamos escenarios comparativos (incluyendo la corriente seleccionada por el usuario)
  v1, v2, v3 = 0.0, 0.5, corriente_usuario
  x1, u1 = simulate_rov(v1, thrust_input)
  x2, u2 = simulate_rov(v2, thrust_input)
  x3, u3 = simulate_rov(v3, thrust_input)

  # Tarjetas con valores numéricos exactos (Métricas)
  col_met1, col_met2, col_met3 = st.columns(3)
  col_met1.metric(
      "Posición Final (0.0 m/s)",
      f"{x1[-1]:.2f} m",
      f"Vel: {u1[-1]:.2f} m/s",
  )
  col_met2.metric(
      "Posición Final (0.5 m/s)",
      f"{x2[-1]:.2f} m",
      f"Vel: {u2[-1]:.2f} m/s",
  )
  col_met3.metric(
      f"Posición Final ({corriente_usuario} m/s)",
      f"{x3[-1]:.2f} m",
      f"Vel: {u3[-1]:.2f} m/s",
  )

  # Caja de análisis dinámico inteligente según los propulsores
  st.markdown("### 💡 Diagnóstico del Estado de Propulsión y Entorno")
  if p1 == 0.0 and p4 == 0.0:
    st.error(
        "⚠️ **Alerta:** Los propulsores longitudinales principales (1 y 4) están"
        " apagados. El ROV no tiene fuerza de avance en Surge y es arrastrado"
        " por la corriente."
    )
  elif p1 != p4:
    st.warning(
        "⚠️ **Desbalance Asimétrico:** Al tener diferentes valores en el"
        " propulsor 1 ({p1}) y el propulsor 4 ({p4}), la matriz de empuje genera"
        " un momento de giro (Yaw) además del avance, simulando un viraje en"
        " la trayectoria."
    )
  else:
    st.success(
        "✅ **Operación Simétrica Estable:** Los propulsores principales operan"
        f" en sintonía con un empuje efectivo de {thrust_input:.1f} N."
    )

  st.markdown("---")

  col_g1, col_g2 = st.columns(2)

  with col_g1:
    fig_pos = go.Figure()
    fig_pos.add_trace(
        go.Scatter(
            x=time,
            y=x1,
            mode="lines",
            name="Corriente: 0.0 m/s",
            line=dict(width=3),
        )
    )
    fig_pos.add_trace(
        go.Scatter(
            x=time,
            y=x2,
            mode="lines",
            name="Corriente: 0.5 m/s",
            line=dict(width=3),
        )
    )
    fig_pos.add_trace(
        go.Scatter(
            x=time,
            y=x3,
            mode="lines",
            name=f"Corriente: {corriente_usuario} m/s",
            line=dict(width=3, dash="dash"),
        )
    )
    fig_pos.update_layout(
        title="Desplazamiento Longitudinal (Sistema NED)",
        xaxis_title="Tiempo (s)",
        yaxis_title="Posición X (m)",
        template="plotly_white",
    )
    st.plotly_chart(fig_pos, use_container_width=True)

  with col_g2:
    fig_vel = go.Figure()
    fig_vel.add_trace(
        go.Scatter(
            x=time,
            y=u1,
            mode="lines",
            name="Corriente: 0.0 m/s",
            line=dict(width=3),
        )
    )
    fig_vel.add_trace(
        go.Scatter(
            x=time,
            y=u2,
            mode="lines",
            name="Corriente: 0.5 m/s",
            line=dict(width=3),
        )
    )
    fig_vel.add_trace(
        go.Scatter(
            x=time,
            y=u3,
            mode="lines",
            name=f"Corriente: {corriente_usuario} m/s",
            line=dict(width=3, dash="dash"),
        )
    )
    fig_vel.update_layout(
        title="Velocidad Efectiva (Sistema Body)",
        xaxis_title="Tiempo (s)",
        yaxis_title="Velocidad (m/s)",
        template="plotly_white",
    )
    st.plotly_chart(fig_vel, use_container_width=True)

# ==========================================
# PESTAÑA 2: GUÍA TEÓRICA Y EXPLICATIVA
# ==========================================
with tab_teo:
  st.header("📖 Guía Teórica y Metodológica Detallada")
  st.markdown(
      "Esta sección documenta el sustento físico, matemático y cinemático"
      " implementado en el modelo del ROV SF30k."
  )

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
    * **Matriz de Amortiguamiento ($D$):** Agrupa los efectos de resistencia hidrodinámica. Incluye componentes **lineales** (fricción cutánea a baja velocidad) y **cuadráticos** (arrastre de presión y separación de flujo).
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
    * **Gráfica de Desplazamiento Longitudinal (Sistema NED):** En esta gráfica quise representar cómo el flujo de la corriente marina en contra afecta directamente el avance espacial del ROV. Lo que muestra la curva es que, conforme aumenta la velocidad de la corriente, la pendiente de desplazamiento se reduce considerablemente, reflejando el impacto de la resistencia externa y el frenado que experimenta el vehículo en su recorrido sobre el fondo marino.
    * **Gráfica de Velocidad Efectiva (Sistema Body):** Esta curva me permite visualizar la transición dinámica del ROV desde el momento en que parte del reposo. Se aprecia claramente cómo experimenta una fase inicial de aceleración impulsada por la inercia del sistema hasta estabilizarse en su velocidad terminal constante, lo que demuestra gráficamente el punto exacto de equilibrio donde el empuje de los propulsores contrarresta por completo la resistencia hidrodinámica del agua.
    """)
