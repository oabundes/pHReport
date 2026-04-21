import streamlit as st
from supabase import create_client, Client
import pandas as pd
import plotly.graph_objects as go
from datetime import date, timedelta
import base64
import io
import os
from dotenv import load_dotenv

load_dotenv()

# ─── PAGE CONFIG ──────────────────────────────────────────
st.set_page_config(
    page_title="Solenis – Reporte pH Descarga",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── SUPABASE ─────────────────────────────────────────────
@st.cache_resource
def get_supabase() -> Client:
    url = os.getenv("SUPABASE_URL", st.secrets.get("SUPABASE_URL", ""))
    key = os.getenv("SUPABASE_KEY", st.secrets.get("SUPABASE_KEY", ""))
    
    
    
    return create_client(url, key)

supabase = get_supabase()

# ─── STYLES ───────────────────────────────────────────────
def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Mono:wght@400;500&display=swap');

    /* ── Global ── */
    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif !important;
    }
    .stApp {
        background-color: #f5f7f9;
    }
    #MainMenu, footer, header { visibility: hidden; }
    .block-container {
        padding: 0 !important;
        max-width: 100% !important;
    }

    /* ── Top header bar ── */
    .sol-header {
        background: #ffffff;
        border-bottom: 2.5px solid #2ec4a0;
        box-shadow: 0 2px 12px rgba(26,46,68,0.10);
        padding: 10px 32px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0;
    }
    .sol-header-left { display: flex; align-items: center; gap: 20px; }
    .sol-header-divider {
        width: 1px; height: 36px;
        background: #c5cfd9;
        display: inline-block;
    }
    .sol-header-label {
        font-family: 'DM Mono', monospace;
        font-size: 9px; letter-spacing: 3px;
        color: #2ec4a0; text-transform: uppercase;
        margin-bottom: 2px;
    }
    .sol-header-title {
        font-size: 15px; font-weight: 700;
        color: #1a2e44; letter-spacing: 0.5px;
        margin: 0;
    }
    .sol-status {
        display: flex; align-items: center; gap: 8px;
        font-family: 'DM Mono', monospace;
        font-size: 11px; color: #22a085;
        letter-spacing: 2px; font-weight: 500;
    }
    .sol-status-dot {
        width: 8px; height: 8px; border-radius: 50%;
        background: #2ec4a0;
        display: inline-block;
        box-shadow: 0 0 0 3px rgba(46,196,160,0.2);
    }

    /* ── Main layout padding ── */
    .sol-main { padding: 18px 24px; }

    /* ── Cards ── */
    .sol-card {
        background: #ffffff;
        border: 1px solid #dde3eb;
        border-radius: 10px;
        box-shadow: 0 1px 4px rgba(26,46,68,0.08);
        overflow: hidden;
        margin-bottom: 16px;
    }
    .sol-card-header {
        background: #f5f7f9;
        border-bottom: 1px solid #dde3eb;
        padding: 9px 16px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .sol-card-title {
        font-size: 11px; font-weight: 700;
        letter-spacing: 2px; color: #344a5e;
        text-transform: uppercase; margin: 0;
    }
    .sol-card-body { padding: 14px 16px; }

    /* ── Min/Max bar ── */
    .sol-minmax {
        background: #ffffff;
        border-bottom: 1px solid #dde3eb;
        display: flex; align-items: center;
    }
    .sol-minmax-item {
        flex: 1; padding: 10px 22px;
        display: flex; align-items: center; gap: 12px;
    }
    .sol-minmax-label {
        font-family: 'DM Mono', monospace;
        font-size: 10px; letter-spacing: 2px;
        color: #5c7389; text-transform: uppercase;
    }
    .sol-minmax-val-min {
        font-size: 24px; font-weight: 700;
        color: #d63a4a; letter-spacing: -0.5px;
    }
    .sol-minmax-val-max {
        font-size: 24px; font-weight: 700;
        color: #e07b00; letter-spacing: -0.5px;
    }
    .sol-minmax-div {
        width: 1px; height: 36px;
        background: #dde3eb;
    }

    /* ── Streamlit widget overrides ── */
    div[data-testid="stDateInput"] label,
    div[data-testid="stButton"] { width: 100%; }

    .stDateInput > div > div > input {
        background: #f5f7f9 !important;
        border: 1.5px solid #dde3eb !important;
        border-radius: 6px !important;
        color: #1a2e44 !important;
        font-family: 'DM Mono', monospace !important;
        font-size: 13px !important;
        padding: 7px 11px !important;
    }
    .stDateInput > div > div > input:focus {
        border-color: #2ec4a0 !important;
        box-shadow: 0 0 0 3px rgba(46,196,160,0.15) !important;
    }

    /* Consultar button */
    div[data-testid="stButton"]:has(button[kind="primary"]) button {
        background: #1a2e44 !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 700 !important;
        letter-spacing: 2px !important;
        text-transform: uppercase !important;
        width: 100% !important;
        transition: background 0.2s !important;
    }
    div[data-testid="stButton"]:has(button[kind="primary"]) button:hover {
        background: #2e4d6a !important;
    }

    /* Limpiar / secondary button */
    div[data-testid="stButton"]:has(button[kind="secondary"]) button {
        background: transparent !important;
        color: #5c7389 !important;
        border: 1.5px solid #dde3eb !important;
        border-radius: 6px !important;
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 600 !important;
        letter-spacing: 1px !important;
        text-transform: uppercase !important;
        width: 100% !important;
    }
    div[data-testid="stButton"]:has(button[kind="secondary"]) button:hover {
        border-color: #2ec4a0 !important;
        color: #22a085 !important;
    }

    /* Export button */
    .btn-export-wrap a {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 9px 20px;
        background: #2ec4a0;
        color: white !important;
        border-radius: 6px;
        font-family: 'DM Sans', sans-serif;
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 1px;
        text-transform: uppercase;
        text-decoration: none !important;
        transition: background 0.2s;
        white-space: nowrap;
    }
    .btn-export-wrap a:hover { background: #22a085; }

    /* Dataframe table */
    div[data-testid="stDataFrame"] {
        border: 1px solid #dde3eb !important;
        border-radius: 8px !important;
        overflow: hidden !important;
    }

    /* Section label override */
    .sol-field-label {
        font-family: 'DM Mono', monospace;
        font-size: 10px; letter-spacing: 2px;
        color: #5c7389; text-transform: uppercase;
        margin-bottom: 4px;
        display: block;
    }

    /* Record count badge */
    .sol-badge {
        background: rgba(46,196,160,0.1);
        color: #22a085;
        font-family: 'DM Mono', monospace;
        font-size: 10px; font-weight: 600;
        padding: 2px 10px; border-radius: 20px;
        display: inline-block;
    }
    </style>
    """, unsafe_allow_html=True)

# ─── HEADER ───────────────────────────────────────────────
def render_header(logo_b64: str):
    st.markdown(f"""
    <div class="sol-header">
      <div class="sol-header-left">
        <img src="data:image/png;base64,{logo_b64}" style="height:38px;width:auto;" />
        <div class="sol-header-divider"></div>
        <div>
          <div class="sol-header-label">Sistema de Monitoreo</div>
          <p class="sol-header-title">Reporte de Lectura de pH a la Descarga</p>
        </div>
      </div>
      <div class="sol-status">
        <span class="sol-status-dot"></span>
        EN LÍNEA
      </div>
    </div>
    """, unsafe_allow_html=True)

# ─── DATA FETCH ───────────────────────────────────────────
def fetch_data(date_from: date, date_to: date) -> pd.DataFrame:
    try:
        query = (supabase.table("PhLogg")
                 .select("timestamp, PH")
                 .gte("timestamp", date_from.isoformat() + "T00:00:00+00:00")
                 .lte("timestamp", date_to.isoformat()   + "T23:59:59+00:00")
                 .order("timestamp", desc=True))
        response = query.execute()
        if not response.data:
            return pd.DataFrame(columns=["timestamp", "PH"])
        df = pd.DataFrame(response.data)
        df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
        df["timestamp"] = df["timestamp"].dt.tz_convert("America/Mexico_City")
        df["PH"] = df["PH"].astype(float)
        return df
    except Exception as e:
        st.error(f"Error al consultar datos: {e}")
        return pd.DataFrame(columns=["timestamp", "PH"])

# ─── CHART ────────────────────────────────────────────────
def build_chart(df: pd.DataFrame) -> go.Figure:
    df_asc = df.sort_values("timestamp")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_asc["timestamp"],
        y=df_asc["PH"],
        mode="lines+markers",
        line=dict(color="#1a2e44", width=2, shape="linear"),
        marker=dict(color="#2ec4a0", size=5, line=dict(color="#1a2e44", width=1)),
        hovertemplate="<b>%{x|%d/%m/%Y %H:%M:%S}</b><br>pH: <b>%{y:.3f}</b><extra></extra>",
        fill="tozeroy",
        fillcolor="rgba(46,196,160,0.08)",
    ))
    fig.update_layout(
        margin=dict(l=12, r=12, t=12, b=12),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="DM Mono, monospace", color="#5c7389", size=11),
        xaxis=dict(
            title="Fecha / Hora",
            titlefont=dict(size=11, color="#5c7389"),
            gridcolor="rgba(26,46,68,0.07)",
            linecolor="rgba(26,46,68,0.15)",
            tickformat="%d/%m %H:%M",
        ),
        yaxis=dict(
            title="Valor de pH",
            titlefont=dict(size=11, color="#5c7389"),
            gridcolor="rgba(26,46,68,0.07)",
            linecolor="rgba(26,46,68,0.15)",
            tickformat=".1f",
        ),
        hoverlabel=dict(
            bgcolor="white", bordercolor="#2ec4a0",
            font=dict(family="DM Mono, monospace", size=12, color="#1a2e44"),
        ),
        height=420,
    )
    return fig

# ─── EXPORT CSV ───────────────────────────────────────────
def make_csv_link(df: pd.DataFrame) -> str:
    df_exp = df.copy()
    df_exp["timestamp"] = df_exp["timestamp"].dt.strftime("%d/%m/%Y %H:%M:%S")
    df_exp.columns = ["Timestamp", "PH"]
    csv_bytes = df_exp.to_csv(index=False).encode("utf-8-sig")
    b64 = base64.b64encode(csv_bytes).decode()
    filename = f"reporte_ph_{date.today().isoformat()}.csv"
    return f'<a href="data:text/csv;base64,{b64}" download="{filename}">⬇ Exportar CSV</a>'

# ─── PH COLOR ─────────────────────────────────────────────
def ph_color(val):
    if val < 6:    return "color: #d63a4a; font-weight:700"
    if val <= 8.5: return "color: #22a085; font-weight:700"
    return "color: #e07b00; font-weight:700"

# ─── MAIN ─────────────────────────────────────────────────
def main():
    inject_css()

    # Logo base64
    logo_b64 = ""
    logo_path = os.path.join(os.path.dirname(__file__), "solenis_logo.png")
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as f:
            logo_b64 = base64.b64encode(f.read()).decode()

    render_header(logo_b64)

    # Session state
    if "df" not in st.session_state:
        st.session_state.df = pd.DataFrame()
    if "queried" not in st.session_state:
        st.session_state.queried = False

    st.markdown('<div class="sol-main">', unsafe_allow_html=True)

    col_left, col_right = st.columns([1, 2.4], gap="medium")

    # ── LEFT PANEL ─────────────────────────────────────────
    with col_left:

        # Filter card
        st.markdown("""
        <div class="sol-card">
          <div class="sol-card-header">
            <span style="color:#2ec4a0">◈</span>
            <p class="sol-card-title">Filtro de Consulta</p>
          </div>
        </div>
        """, unsafe_allow_html=True)

        with st.container():
            st.markdown('<span class="sol-field-label">Fecha Inicio</span>', unsafe_allow_html=True)
            date_from = st.date_input("##from", value=date.today() - timedelta(days=7),
                                      max_value=date.today(), label_visibility="collapsed")
            st.markdown('<span class="sol-field-label">Fecha Fin</span>', unsafe_allow_html=True)
            date_to = st.date_input("##to", value=date.today(),
                                    max_value=date.today(), label_visibility="collapsed")

            c1, c2 = st.columns(2)
            with c2:
                if st.button("Consultar →", type="primary", use_container_width=True):
                    with st.spinner("Consultando…"):
                        st.session_state.df = fetch_data(date_from, date_to)
                        st.session_state.queried = True
            with c1:
                if st.button("Limpiar", type="secondary", use_container_width=True):
                    st.session_state.df = pd.DataFrame()
                    st.session_state.queried = False

        # Table card
        df = st.session_state.df
        count = len(df)

        st.markdown(f"""
        <div class="sol-card" style="margin-top:16px">
          <div class="sol-card-header" style="justify-content:space-between">
            <div style="display:flex;align-items:center;gap:8px">
              <span style="color:#2ec4a0">◈</span>
              <p class="sol-card-title">Resultados</p>
            </div>
            <span class="sol-badge">{count} registros</span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        if not df.empty:
            df_display = df.copy()
            df_display.insert(0, "#", range(1, len(df_display) + 1))
            df_display["Timestamp"] = df_display["timestamp"].dt.strftime("%d/%m/%Y %H:%M:%S")
            df_display["pH"] = df_display["PH"].round(2)
            df_show = df_display[["#", "Timestamp", "pH"]]

            st.dataframe(
                df_show.style.map(lambda v: ph_color(v), subset=["pH"]),
                use_container_width=True,
                height=360,
                hide_index=True,
            )
        else:
            st.markdown("""
            <div style="text-align:center;padding:28px;color:#9aaab8;
                        font-style:italic;background:white;border-radius:8px;
                        border:1px solid #dde3eb;">
              Realice una consulta para ver resultados
            </div>""", unsafe_allow_html=True)

    # ── RIGHT PANEL ────────────────────────────────────────
    with col_right:
        df = st.session_state.df

        # Min/Max + Export bar
        if not df.empty:
            ph_min = df["PH"].min()
            ph_max = df["PH"].max()
            csv_link = make_csv_link(df)
        else:
            ph_min = ph_max = None
            csv_link = ""

        min_str = f"{ph_min:.2f}" if ph_min is not None else "—"
        max_str = f"{ph_max:.2f}" if ph_max is not None else "—"
        export_html = f'<div class="btn-export-wrap">{csv_link}</div>' if csv_link else \
                      '<div class="btn-export-wrap"><span style="color:#9aaab8;font-size:12px;font-family:\'DM Mono\',monospace;">Sin datos</span></div>'

        st.markdown(f"""
        <div class="sol-card">
          <div class="sol-card-header">
            <span style="color:#2ec4a0">◈</span>
            <p class="sol-card-title">Gráfica de pH vs. Tiempo</p>
          </div>
          <div class="sol-minmax">
            <div class="sol-minmax-item">
              <span class="sol-minmax-label">pH Mínimo</span>
              <span class="sol-minmax-val-min">{min_str}</span>
            </div>
            <div class="sol-minmax-div"></div>
            <div class="sol-minmax-item">
              <span class="sol-minmax-label">pH Máximo</span>
              <span class="sol-minmax-val-max">{max_str}</span>
            </div>
            <div class="sol-minmax-div"></div>
            <div class="sol-minmax-item" style="flex:0 0 auto;padding:10px 22px;">
              {export_html}
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Chart
        if not df.empty:
            fig = build_chart(df)
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.markdown("""
            <div style="display:flex;flex-direction:column;align-items:center;
                        justify-content:center;height:380px;background:white;
                        border-radius:10px;border:1px solid #dde3eb;
                        color:#9aaab8;gap:12px;">
              <div style="font-size:42px;opacity:0.25">◈</div>
              <div style="font-family:'DM Sans',sans-serif;font-size:14px;letter-spacing:1px;">
                Realice una consulta para visualizar datos
              </div>
            </div>""", unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
