"""
Configuración y estilos para el Dashboard
"""

CUSTOM_CSS = """
<style>
    /* ── METRIC CARD ─────────────────────────────────── */
    [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(5px);
        border: 1px solid rgba(255, 255, 255, 0.3);
        height: 150px;
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center;
        padding: 16px !important;
    }

    /* Label centrado */
    [data-testid="stMetricLabel"] {
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
    }
    [data-testid="stMetricLabel"] > div,
    [data-testid="stMetricLabel"] p {
        text-align: center !important;
        justify-content: center !important;
        width: 100% !important;
    }

    /* Value centrado */
    [data-testid="stMetricValue"] {
        display: flex !important;
        justify-content: center !important;
        width: 100% !important;
    }
    [data-testid="stMetricValue"] > div,
    [data-testid="stMetricValue"] p {
        text-align: center !important;
        width: 100% !important;
    }

    /* Delta centrado — fit-content para no ocupar todo el ancho */
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
        border-radius: 16px;
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(5px);
        border: 1px solid rgba(255, 255, 255, 0.3);
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
