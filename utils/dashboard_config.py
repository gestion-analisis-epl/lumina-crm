"""
Configuración y estilos para el Dashboard
"""

CUSTOM_CSS = """
<style>
    /* ── METRIC CARDS ────────────────────────────────── */
    [data-testid="stMetric"] {
        position: relative;
        overflow: hidden;
        background: linear-gradient(135deg, #0F3B66 0%, #1E6FB8 100%);
        border-radius: 16px;
        border: none;
        box-shadow: 0 10px 24px rgba(15, 59, 102, 0.18);
        min-height: 152px;
        display: flex !important;
        flex-direction: column !important;
        align-items: stretch !important;
        justify-content: space-between !important;
        text-align: left;
        padding: 20px 20px 18px 20px !important;
        transition: box-shadow 0.2s ease, transform 0.15s ease;
    }

    [data-testid="stMetric"]::before {
        content: "";
        position: absolute;
        width: 130px; height: 130px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.12);
        top: -46px; right: -34px;
    }
    [data-testid="stMetric"]::after {
        content: "";
        position: absolute;
        width: 86px; height: 86px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.09);
        bottom: -28px; right: 28px;
    }

    [data-testid="stMetric"]:hover {
        box-shadow: 0 14px 30px rgba(15, 59, 102, 0.26);
        transform: translateY(-3px);
    }

    /* Rotación de color por posición dentro de cada fila de columnas */
    [data-testid="stHorizontalBlock"] [data-testid="stColumn"]:nth-of-type(3n+2) [data-testid="stMetric"] {
        background: linear-gradient(135deg, #0E9F8E 0%, #38C6B4 100%);
        box-shadow: 0 10px 24px rgba(14, 159, 142, 0.18);
    }
    [data-testid="stHorizontalBlock"] [data-testid="stColumn"]:nth-of-type(3n) [data-testid="stMetric"] {
        background: linear-gradient(135deg, #7C3AED 0%, #A78BFA 100%);
        box-shadow: 0 10px 24px rgba(124, 58, 237, 0.18);
    }

    /* Label (+ ícono en círculo, alineado a la derecha) */
    [data-testid="stMetricLabel"] {
        position: relative;
        z-index: 1;
    }
    [data-testid="stMetricLabel"] p {
        color: rgba(255, 255, 255, 0.92) !important;
        font-size: 0.85rem !important;
        font-weight: 600 !important;
        letter-spacing: 0.01em !important;
        line-height: 1.3 !important;
        margin: 0 44px 0 0 !important;
    }
    [data-testid="stMetricLabel"] p > span:first-child {
        position: absolute;
        top: 20px;
        right: 20px;
        z-index: 2;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 34px; height: 34px;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.18);
        font-size: 18px !important;
    }

    /* Value */
    [data-testid="stMetricValue"] {
        position: relative;
        z-index: 1;
    }
    [data-testid="stMetricValue"] p {
        text-align: left !important;
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1.75rem !important;
        line-height: 1.2 !important;
        margin: 12px 0 0 0 !important;
    }

    /* Delta (caption inferior, tipo "Increased by X%") */
    [data-testid="stMetricDelta"] {
        position: relative;
        z-index: 1;
        margin-top: 8px;
    }
    [data-testid="stMetricDelta"] svg {
        fill: rgba(255, 255, 255, 0.9) !important;
    }
    [data-testid="stMetricDelta"] p {
        color: rgba(255, 255, 255, 0.9) !important;
        font-size: 0.8rem !important;
        font-weight: 600 !important;
        margin: 0 !important;
    }

    /* ── DATE INPUT ──────────────────────────────────── */
    .stDateInput {
        background: white;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0, 48, 87, 0.08);
        border: 1px solid #e2e8f0;
        text-align: center;
        height: 90px;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
</style>
"""

def setup_page_config():
    """Configura la página del dashboard"""
    import streamlit as st
    st.set_page_config(
        page_title="Dashboard",
        page_icon=":material/dashboard:",
        layout="wide"
    )

def apply_custom_styles():
    """Aplica los estilos personalizados"""
    import streamlit as st
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
