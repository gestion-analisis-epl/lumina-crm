"""
Configuración y estilos para el Dashboard
"""

CUSTOM_CSS = """
<style>
    /* ── METRIC CARDS ────────────────────────────────── */
    [data-testid="stMetric"] {
        background: #ffffff;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 48, 87, 0.08);
        border: 1px solid #e2e8f0;
        border-left: 4px solid #003057;
        height: 150px;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center;
        padding: 20px 16px !important;
        transition: box-shadow 0.2s ease, transform 0.15s ease;
    }

    [data-testid="stMetric"]:hover {
        box-shadow: 0 6px 20px rgba(0, 48, 87, 0.14);
        transform: translateY(-2px);
    }

    /* Label */
    [data-testid="stMetricLabel"] {
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
    }
    [data-testid="stMetricLabel"] > div,
    [data-testid="stMetricLabel"] p {
        text-align: center !important;
        color: #5a7184 !important;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
        line-height: 1.4 !important;
    }

    /* Value */
    [data-testid="stMetricValue"] {
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
    }
    [data-testid="stMetricValue"] > div,
    [data-testid="stMetricValue"] p {
        text-align: center !important;
        color: #003057 !important;
        font-weight: 700 !important;
        font-size: 1.55rem !important;
        line-height: 1.2 !important;
    }

    /* Delta */
    [data-testid="stMetricDelta"] {
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
    }
    [data-testid="stMetricDelta"] > div {
        width: fit-content !important;
        margin: 0 auto !important;
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
