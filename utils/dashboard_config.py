"""
Configuración y estilos para el Dashboard
"""

CUSTOM_CSS = """
<style>
    .stMetric { 
        background: rgba(255, 255, 255, 0.1); 
        border-radius: 16px; 
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1); 
        backdrop-filter: blur(5px);
        border: 1px solid rgba(255, 255, 255, 0.3); 
        text-align: center; 
        height: 100px;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    .stMetric > div {
        width: 100%;
    }
    .stMetric label {
        justify-content: center !important;
        display: flex !important;
    }
    .stMetric label > div {
        justify-content: center !important;
    }
    .stMetric [data-testid="stMetricLabel"] {
        justify-content: center !important;
    }
    .stMetric [data-testid="stMetricLabel"] > div {
        justify-content: center !important;
    }
    
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
