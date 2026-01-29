"""
Dashboard - Vista Ejecutiva
¿Cómo está mi negocio HOY? - Vista de 30 segundos
"""
import streamlit as st
from streamlit_gsheets import GSheetsConnection

# Importar módulos personalizados
from utils.dashboard_config import setup_page_config, apply_custom_styles
from utils.data_loader import inicializar_conexion
from utils.dashboard_filters import DashboardFilters
from utils.dashboard_metrics import MetricsCalculator
from utils import dashboard_charts as charts


# Configuración inicial
setup_page_config()
apply_custom_styles()

st.title(":material/dashboard: Dashboard Ejecutivo")

# Conexión a Google Sheets y carga de datos
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
    data_loader = inicializar_conexion(conn)
    
    citas_data = data_loader.citas_data
    prospeccion_data = data_loader.prospeccion_data
    proyectos_data = data_loader.proyectos_data
    metas_data = data_loader.metas_data
    
    # Obtener lista de asesores
    todos_asesores = data_loader.obtener_lista_asesores()
    asesores_opciones = ["Todos"] + todos_asesores
    
    # ========== FILTROS ==========
    filtros = DashboardFilters()
    fecha_inicio, fecha_fin, asesor_seleccionado = filtros.mostrar_filtros(asesores_opciones)
    
    # Aplicar filtros a los datos
    citas_filtradas, prospeccion_filtrada, proyectos_filtrados = filtros.aplicar_filtros(
        citas_data, prospeccion_data, proyectos_data,
        fecha_inicio, fecha_fin, asesor_seleccionado
    )
    
    st.markdown("---")
    
    # ========== MÉTRICAS CRÍTICAS ==========
    calculator = MetricsCalculator(citas_data, prospeccion_data, proyectos_data, metas_data)
    
    st.markdown("#### :material/trending_up: Métricas Críticas del Mes")
    
    # Ventas actuales vs Meta
    metricas_ventas = calculator.metricas_ventas_cotizaciones(
        proyectos_filtrados, asesor_seleccionado, todos_asesores, fecha_inicio, fecha_fin
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label=":material/flag: Meta de Ventas",
            value=f"${metricas_ventas['meta_total']:,.2f}"
        )
    
    with col2:
        st.metric(
            label=":material/attach_money: Ventas Actuales",
            value=f"${metricas_ventas['ventas_totales']:,.2f}",
            delta=metricas_ventas['delta_ventas'],
            delta_color=metricas_ventas['color_ventas']
        )
    
    with col3:
        metricas = calculator.metricas_principales(
            citas_filtradas, prospeccion_filtrada, proyectos_filtrados
        )
        st.metric(
            label=":material/account_balance_wallet: Total Cartera",
            value=f"${metricas['total_cartera']:,.2f}"
        )
    
    st.markdown("---")
    
    # ========== INDICADORES DE ACTIVIDAD ==========
    st.markdown("#### :material/insights: Actividad General")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Citas",
            value=metricas['total_citas']
        )
    
    with col2:
        st.metric(
            label="Prospectos",
            value=metricas['total_prospectos']
        )
    
    with col3:
        st.metric(
            label="Proyectos",
            value=metricas['total_proyectos']
        )
    
    with col4:
        st.metric(
            label="Ticket Promedio",
            value=f"${metricas['ticket_promedio']:,.2f}"
        )
    
    st.markdown("---")
    
    # ========== EVOLUCIÓN DE CITAS ==========
    st.markdown("#### :material/show_chart: Evolución de Citas por Mes")
    
    # Gráfico de área de citas por mes
    charts.mostrar_grafico_citas_por_mes(citas_filtradas)
    
    st.markdown("---")
    
    # ========== ESTADO DEL PIPELINE ==========
    st.markdown("#### :material/donut_small: Estado del Pipeline")
    
    # Gráfico de distribución de proyectos por estado
    charts.mostrar_grafico_proyectos_estado(proyectos_filtrados)
    
    st.markdown("---")
    
    # ========== PROYECTOS CRÍTICOS ==========
    st.markdown("#### :material/priority_high: Últimos Proyectos")
    
    if len(proyectos_filtrados) > 0:
        # Seleccionar columnas importantes
        columnas_mostrar = []
        for col in ['FECHA', 'ASESOR', 'PROYECTO', 'CLIENTE', 'TOTAL', 'STATUS']:
            if col in proyectos_filtrados.columns:
                columnas_mostrar.append(col)
        df = proyectos_filtrados[columnas_mostrar]
        if columnas_mostrar:
            st.dataframe(
                df.head(5).style.format({"TOTAL": "${:,.2f}"}), 
                use_container_width=True,
                hide_index=True
            )
        else:
            st.dataframe(proyectos_filtrados.head(5), use_container_width=True, hide_index=True)
    else:
        st.info("No hay proyectos para mostrar")

except Exception as e:
    st.error(f"Error al cargar datos: {str(e)}")
    st.info("Asegúrate de que las hojas CITAS, PROSPECCION, PROYECTOS y METAS existan en tu Google Sheets.")
