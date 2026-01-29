import streamlit as st

st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css">
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">

<style>
/* Fondo del sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #003057, #001b33);
    border-right: 1px solid rgba(255,255,255,0.1);
}

/* Texto del sidebar */
section[data-testid="stSidebar"] * {
    color: #ffffff !important;
}

/* Inputs del sidebar */
section[data-testid="stSidebar"] input,
section[data-testid="stSidebar"] textarea,
section[data-testid="stSidebar"] select {
    color: #ffffff !important;
}

/* Labels */
section[data-testid="stSidebar"] label {
    color: #cfd8dc !important;
}
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    img = st.image("img/logo lumina blanco.png", width='stretch')

dashboard_page = st.Page(
    page="pages/1_Dashboard.py",
    title="Dashboard",
    icon=":material/dashboard:"
    )

citas_page = st.Page(
    page="pages/2_Citas.py",
    title="Citas",
    icon=":material/calendar_today:"
    )

prospeccion_page = st.Page(
    page="pages/3_Prospección.py",
    title="Prospección",
    icon=":material/track_changes:"
    )

proyectos_page = st.Page(
    page="pages/4_Proyectos.py",
    title="Proyectos",
    icon=":material/folder:"
    )

analytics_page = st.Page(
    page="pages/5_Analytics.py",
    title="Analytics",
    icon=":material/insights:"
    )

pg = st.navigation(
    {
        "Analytics": [dashboard_page, analytics_page],
        "Gestión de Relaciones": [citas_page, prospeccion_page],
        "Gestión de Proyectos": [proyectos_page]
    }
)
pg.run()