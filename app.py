import numpy as np
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(
    page_title="Simulador y Animación 3D - ROV SF30k", layout="wide"
)

st.title("⚓ Simulador Dinámico, Animación 3D y Análisis - ROV SF30k")
st.markdown(
    "Visualizador interactivo 3D y modelo de 6 grados de libertad basado en la"
    " tesis de Viktor Berg (2012)."
)

# --- Menú Lateral (Sidebar) para Parámetros y Controles ---
st.sidebar.header("🎛️ Control de Propulsores y Entorno")
st.sidebar.markdown(
    "Ajusta los 6 propulsores para ver los vectores de fuerza en el modelo 3D y"
    " la trayectoria."
)

# Sliders individuales para los 6 propulsores
st.sidebar.subheader("🕹️ Factores de Empuje (0.0 a 1.0)")
p1 = st.sidebar.slider("Propulsor 1 (Surge / Avance)", 0.0, 1.0, 1.0, 0.05)
p2 = st.sidebar.slider("Propulsor 2 (Surge / Avance)", 0.0, 1.0, 1.0, 0.05)
p3 = st.sidebar.slider("Propulsor 3 (Sway / Lateral)", 0.0, 1.0, 0.5, 0.05)
p4 = st.sidebar.slider("Propulsor 4 (Sway / Lateral)", 0.0, 1.0, 0.5, 0.05)
p5 = st.sidebar.slider("Propulsor 5 (Heave / Vertical)", 0.0, 1.0, 1.0, 0.05)
p6 = st.sidebar.slider("Propulsor 6 (Heave / Vertical)", 0.0, 1.0, 1.0, 0.05)

thrust_max = st.sidebar.slider(
    "Empuje Máximo Nominal (N)", 500.0, 3000.0, 1200.0, 100.0
)

st.sidebar.markdown("---")
st.sidebar.subheader("🌊 Corriente Marina")
corriente_usuario = st.sidebar.slider(
    "Velocidad de Corriente en Contra (m/s)", 0.0, 2.0, 0.5, 0.1
)

# Empuje neto estimado en el eje longitudinal (Surge)
thrust_surge = thrust_max * (0.5 * p1 + 0.5 * p2)

# --- Pestañas de la Aplicación ---
tab_sim, tab_teo = st.tabs(
    ["🚀 Animación 3D y Simulador", "📚 Guía Teórica y Metodología"]
)

with tab_sim:
  st.subheader("🧊 1. Animación y Configuración 3D de Propulsores (Body Frame)")

  # Definición del chasis 3D del ROV (Paralelepípedo)
  dx, dy, dz = 1.2, 0.8, 0.6  # Dimensiones aproximadas en metros
  x_box = [
      -dx / 2,
      dx / 2,
      dx / 2,
      -dx / 2,
      -dx / 2,
      dx / 2,
      dx / 2,
      -dx / 2,
  ]
  y_box = [
      -dy / 2,
      -dy / 2,
      dy / 2,
      dy / 2,
      -dy / 2,
      -dy / 2,
      dy / 2,
      dy / 2,
  ]
  z_box = [
      -dz / 2,
      -dz / 2,
      -dz / 2,
      -dz / 2,
      dz / 2,
      dz / 2,
      dz / 2,
      dz / 2,
  ]

  fig_3d = go.Figure()

  # Dibujar Estructura/Chasis del ROV
  fig_3d.add_trace(
      go.Mesh3d(
          x=x_box,
          y=y_box,
          z=z_box,
          i=[7, 0, 0, 0, 4, 4, 6, 6, 4, 0, 3, 2],
          j=[3, 4, 1, 2, 5, 6, 5, 2, 0, 1, 6, 3],
          k=[0, 7, 2, 3, 6, 7, 1, 1, 5, 5, 7, 6],
          opacity=0.3,
          color="cyan",
          name="Chasis ROV SF30k",
      )
  )

  # Posiciones y Vectores de Fuerza de los 6 Propulsores
  prop_pos = [
      (-dx / 2, -dy / 2, 0, p1, 1, 0, 0, "Prop 1 (Surge)"),
      (-dx / 2, dy / 2, 0, p2, 1, 0, 0, "Prop 2 (Surge)"),
      (0, -dy / 2, 0, p3, 0, 1, 0, "Prop 3 (Sway)"),
      (0, dy / 2, 0, p4, 0, 1, 0, "Prop 4 (Sway)"),
      (-dx / 4, 0, dz / 2, p5, 0, 0, 1, "Prop 5 (Heave)"),
      (dx / 4, 0, dz / 2, p6, 0, 0, 1, "Prop 6 (Heave)"),
  ]

  colors = ["red", "blue", "green", "orange", "purple", "magenta"]

  for idx, (px, py, pz, val, vx, vy, vz, name) in enumerate(prop_pos):
    scale = val * 0.8  # Magnitud visual de la flecha
    # Punto del propulsor
    fig_3d.add_trace(
        go.Scatter3d(
            x=[px],
            y=[py],
            z=[pz],
            mode="markers+text",
            marker=dict(size=8, color=colors[idx]),
            text=[f"P{idx+1}: {val*100:.0f}%"],
            textposition="top center",
            name=name,
        )
    )
    # Vector de fuerza del empuje
    if scale > 0:
      fig_3d.add_trace(
          go.Scatter3d(
              x=[px, px + vx * scale],
              y=[py, py + vy * scale],
              z=[pz, pz + vz * scale],
              mode="lines",
              line=dict(color=colors[idx], width=6),
              showlegend=False,
          )
      )

  fig_3d.update_layout(
      scene=dict(
          xaxis=dict(range=[-1.5, 1.5], title="X (Surge)"),
          yaxis=dict(range=[-1.5, 1.5], title="Y (Sway)"),
          zaxis=dict(range=[-1.5, 1.5], title="Z (Heave)"),
          aspectmode="cube",
      ),
      margin=dict(l=0, r=0, b=0, t=30),
      height=450,
  )

  st.plotly_chart(fig_3d, use_container_width=True)

  st.markdown("---")

  # --- SIMULACIÓN Y GRÁFICAS MEJORADAS ---
  st.subheader("📈 2. Resultados Numéricos y Respuesta Dinámica")

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

  x1, u1 = simulate_rov(0.0, thrust_surge)
  x2, u2 = simulate_rov(0.5, thrust_surge)
  x3, u3 = simulate_rov(corriente_usuario, thrust_surge)

  # Métricas numéricas atractivas
  col_m1, col_m2, col_m3 = st.columns(3)
  col_m1.metric(
      "Posición Final (0.0 m/s)",
      f"{x1[-1]:.2f} m",
      f"Vel. Terminal: {u1[-1]:.2f} m/s",
  )
  col_m2.metric(
      "Posición Final (0.5 m/s)",
      f"{x2[-1]:.2f} m",
      f"Vel. Terminal: {u2[-1]:.2f} m/s",
  )
  col_m3.metric(
      f"Posición Final ({corriente_usuario} m/s)",
      f"{x3[-1]:.2f} m",
      f"Vel. Terminal: {u3[-1]:.2f} m/s",
  )

  # Diagnóstico en tiempo real
  if p1 == 0 and p2 == 0:
    st.error(
        "🚨 **Propulsores Longitudinales Apagados:** El ROV no genera empuje en"
        " el eje X y es arrastrado por la corriente."
    )
  elif p1 != p2:
    st.warning(
        "⚠️ **Desbalance Longitudinal:** La diferencia entre P1 y P2 generará"
        " un par de guiñada (Yaw) haciendo girar al ROV."
    )
  else:
    st.success(
        f"✅ **Avance Simétrico:** Empuje longitudinal efectivo de"
        f" {thrust_surge:.1f} N."
    )

  col_g1, col_g2 = st.columns(2)

  with col_g1:
    fig_pos = go.Figure()
    fig_pos.add_trace(
        go.Scatter(
            x=time,
            y=x1,
            mode="lines",
            name="Corriente: 0.0 m/s",
            line=dict(color="#1f77b4", width=3),
        )
    )
    fig_pos.add_trace(
        go.Scatter(
            x=time,
            y=x2,
            mode="lines",
            name="Corriente: 0.5 m/s",
            line=dict(color="#ff7f0e", width=3),
        )
    )
    fig_pos.add_trace(
        go.Scatter(
            x=time,
            y=x3,
            mode="lines",
            name=f"Corriente: {corriente_usuario} m/s",
            line=dict(color="#2ca02c", width=3, dash="dash"),
        )
    )
    fig_pos.update_layout(
        title="Desplazamiento Longitudinal (Sistema NED)",
        xaxis_title="Tiempo (s)",
        yaxis_title="Posición X (m)",
        template="plotly_white",
        hovermode="x unified",
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
            line=dict(color="#1f77b4", width=3),
        )
    )
    fig_vel.add_trace(
        go.Scatter(
            x=time,
            y=u2,
            mode="lines",
            name="Corriente: 0.5 m/s",
            line=dict(color="#ff7f0e", width=3),
        )
    )
    fig_vel.add_trace(
        go.Scatter(
            x=time,
            y=u3,
            mode="lines",
            name=f"Corriente: {corriente_usuario} m/s",
            line=dict(color="#2ca02c", width=3, dash="dash"),
        )
    )
    fig_vel.update_layout(
        title="Velocidad Efectiva (Sistema Body)",
        xaxis_title="Tiempo (s)",
        yaxis_title="Velocidad (m/s)",
        template="plotly_white",
        hovermode="x unified",
    )
    st.plotly_chart(fig_vel, use_container_width=True)

# Pestaña 2: Contenido teórico
with tab_teo:
  st.header("📖 Sustento Teórico y Físico del ROV SF30k")
  st.markdown(
      "Información basada en el modelo dinámico de Fossen y la tesis de Viktor"
      " Berg (2012)."
  )

  st.write("""
    ### 1. Ecuación General de Fossen
    El movimiento en 6 Grados de Libertad (6 DoF) se rige por:
    $$M\\dot{\\nu} + C(\\nu)\\nu + D(\\nu)\\nu + g(\\eta) = \\tau$$
    
    * **Masa Total ($M$):** Combina la masa del cuerpo rígido ($M_{RB}$) y la masa añadida hidrodinámica ($M_A$).
    * **Amortiguamiento ($D$):** Suma los componentes lineales ($DL$) por fricción cutánea y no lineales ($DNL$) por arrastre de presión.
    * **Sistemas de Referencia:** Las velocidades y fuerzas del empuje se expresan en el sistema fijo al cuerpo (**Body Frame**), mientras que la trayectoria global y avance $X$ se traducen al sistema fijo a la tierra (**NED Frame**).
    """)
