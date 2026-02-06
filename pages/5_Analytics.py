"""
Analytics - Análisis Profundo
Análisis detallado de ventas y actividad comercial
"""
import streamlit as st

# Importar módulos personalizados
from utils.dashboard_config import setup_page_config, apply_custom_styles
from utils.data_loader import inicializar_conexion
from utils.dashboard_filters import DashboardFilters
from utils.dashboard_metrics import MetricsCalculator
from utils import dashboard_charts as charts


# Configuración inicial
st.set_page_config(page_title="Analytics", page_icon=":material/analytics:", layout="wide")
apply_custom_styles()

st.title(":material/analytics: Analytics")

# Conexión a Supabase y carga de datos
try:
    data_loader = inicializar_conexion()
    
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
    
    # ========== CALCULADOR ==========
    calculator = MetricsCalculator(citas_data, prospeccion_data, proyectos_data, metas_data)
    
    # ========== TABS DE ANALYTICS ==========
    tab1, tab2 = st.tabs([
        ":material/attach_money: Ventas", 
        ":material/trending_up: Actividad Comercial"
    ])
    
    # ==================== TAB 1: VENTAS ====================
    with tab1:
        st.markdown("### :material/monetization_on: Análisis de Ventas")
        st.caption("¿Estoy cumpliendo mis metas comerciales?")
        
        st.markdown("---")
        
        # Performance Mensual
        st.markdown("#### :material/calendar_today: Performance Mensual")
        
        metricas_ventas = calculator.metricas_ventas_cotizaciones(
            proyectos_filtrados, asesor_seleccionado, todos_asesores, fecha_inicio, fecha_fin
        )
        
        col_v1, col_v2, col_v3 = st.columns(3)
        
        with col_v1:
            st.metric(
                label=":material/emoji_events: Meta Total de Ventas",
                value=f"${metricas_ventas['meta_total']:,.2f}"
            )
        
        with col_v2:
            st.metric(
                label=":material/attach_money: Ventas Actuales",
                value=f"${metricas_ventas['ventas_totales']:,.2f}",
                delta=metricas_ventas['delta_ventas'],
                delta_color=metricas_ventas['color_ventas']
            )
        
        with col_v3:
            st.metric(
                label=":material/description: Cotizaciones Totales",
                value=f"${metricas_ventas['cotizaciones_totales']:,.2f}",
                delta=metricas_ventas['delta_cot'],
                delta_color=metricas_ventas['color_cot']
            )
        
        st.markdown("---")
        
        # Performance Trimestral
        st.markdown("#### :material/calendar_month: Performance Trimestral")
        
        metricas_trimestre = calculator.metricas_ventas_trimestrales(proyectos_filtrados)
        charts.mostrar_metricas_ventas_trimestrales(metricas_trimestre)
        
        st.markdown("---")
        
        # Análisis de Proyectos
        st.markdown("#### :material/assessment: Análisis de Proyectos/Cotizaciones")
        
        metricas_estado = calculator.metricas_proyectos_por_estado(proyectos_filtrados)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label=":material/build: Proyectos/Cotizaciones en Proceso ($)",
                value=f"${metricas_estado['proyectos_proceso']:,.2f}"
            )
        
        with col2:
            st.metric(
                label=":material/emoji_events: Proyectos/Cotizaciones Ganados ($)",
                value=f"${metricas_estado['proyectos_ganados']:,.2f}"
            )
        
        with col3:
            st.metric(
                label=":material/cancel: Proyectos/Cotizaciones Perdidos ($)",
                value=f"${metricas_estado['proyectos_perdidos']:,.2f}"
            )
        
        st.markdown("---")
        
        # Contexto: Ticket Promedio
        st.markdown("#### :material/paid: Calidad de Ventas")
        
        metricas = calculator.metricas_principales(
            citas_filtradas, prospeccion_filtrada, proyectos_filtrados
        )
        
        col_t1, col_t2 = st.columns(2)
        
        with col_t1:
            st.metric(
                label="Ticket Promedio",
                value=f"${metricas['ticket_promedio']:,.2f}"
            )
        
        with col_t2:
            st.metric(
                label="Total Cartera",
                value=f"${metricas['total_cartera']:,.2f}"
            )
    
    # ==================== TAB 2: ACTIVIDAD COMERCIAL ====================
    with tab2:
        st.markdown("### :material/trending_up: Actividad Comercial")
        st.caption("¿Mi equipo está ejecutando bien?")
        
        st.markdown("---")
        
        # Cumplimiento de Citas
        st.markdown("#### :material/calendar_today: Cumplimiento de Citas")
        
        metricas_citas = calculator.metricas_citas_semanales(
            fecha_inicio, fecha_fin, asesor_seleccionado
        )
        
        if metricas_citas:
            col_c1, col_c2 = st.columns(2)
            
            with col_c1:
                st.metric(
                    label=":material/call: Promedio de Citas Semanales",
                    value=f"{metricas_citas['promedio_general']:.1f} citas/semana",
                    delta=metricas_citas['delta_text'],
                    delta_color=metricas_citas['delta_color']
                )
            
            with col_c2:
                st.metric(
                    label=":material/event: Semanas Analizadas",
                    value=metricas_citas['total_semanas']
                )
        
        st.markdown("---")
        
        # Pipeline de Oportunidades
        st.markdown("#### :material/filter_list: Pipeline de Oportunidades")
        
        metricas = calculator.metricas_principales(
            citas_filtradas, prospeccion_filtrada, proyectos_filtrados
        )
        
        col_p1, col_p2, col_p3 = st.columns(3)
        
        with col_p1:
            st.metric(
                label="Total Citas",
                value=metricas['total_citas']
            )
        
        with col_p2:
            st.metric(
                label="Total Prospectos",
                value=metricas['total_prospectos']
            )
        
        with col_p3:
            st.metric(
                label="Total Proyectos/Cotizaciones",
                value=metricas['total_proyectos']
            )
        
        st.markdown("---")
        
        # Comparativa de Módulos (Embudo)
        st.markdown("#### :material/insights: Embudo Comercial")
        
        charts.mostrar_graficos(
            metricas['total_citas'],
            metricas['total_prospectos'],
            metricas['total_proyectos']
        )
        
        st.markdown("---")
        
        # Actividad Reciente
        st.markdown("#### :material/description: Actividad Reciente")
        
        tab_citas, tab_prosp, tab_proy = st.tabs([
            "Últimas Citas", 
            "Últimos Prospectos", 
            "Últimos Proyectos/Cotizaciones"
        ])
        
        with tab_citas:
            if len(citas_filtradas) > 0:
                columnas_mostrar = []
                for col in ['FECHA', 'ASESOR', 'CLIENTE', 'EMPRESA', 'STATUS']:
                    if col in citas_filtradas.columns:
                        columnas_mostrar.append(col)
                
                if columnas_mostrar:
                    st.dataframe(
                        citas_filtradas[columnas_mostrar].head(5), 
                        width='stretch',
                        hide_index=True
                    )
                else:
                    st.dataframe(citas_filtradas.head(5), width='stretch', hide_index=True,
                                 column_config={
                                     "id": None,
                                     "cita_id": "ID Cita",
                                     "asesor": "Asesor",
                                     "fecha": "Fecha",
                                     "prospecto": "Prospecto",
                                     "giro": "Giro",
                                     "accion_seguir": "Acción a Seguir",
                                     "ultimo_contacto": "Último Contacto",
                                     "created_at": None,
                                     "updated_at": None
                                 })
            else:
                st.info("No hay citas registradas")
        
        with tab_prosp:
            if len(prospeccion_filtrada) > 0:
                columnas_mostrar = []
                for col in ['FECHA', 'ASESOR', 'PROSPECTO', 'EMPRESA', 'STATUS']:
                    if col in prospeccion_filtrada.columns:
                        columnas_mostrar.append(col)
                
                if columnas_mostrar:
                    st.dataframe(
                        prospeccion_filtrada[columnas_mostrar].head(5), width='stretch', hide_index=True)
                else:
                    st.dataframe(prospeccion_filtrada.head(5), width='stretch', hide_index=True,
                                 column_config={
                                     "id": None,
                                     "prospecto_id": "ID Prospecto",
                                     "asesor": "Asesor",
                                     "fecha": "Fecha",
                                     "prospecto": "Prospecto",
                                     "tipo": "Tipo",
                                     "accion": "Acción",
                                     "created_at": None,
                                     "updated_at": None
                        })
            else:
                st.info("No hay prospectos registrados")
        
        with tab_proy:
            if len(proyectos_filtrados) > 0:
                columnas_mostrar = []
                for col in ['FECHA', 'ASESOR', 'CLIENTE', 'TOTAL', 'STATUS']:
                    if col in proyectos_filtrados.columns:
                        columnas_mostrar.append(col)
                
                if columnas_mostrar:
                    st.dataframe(
                        proyectos_filtrados[columnas_mostrar].head(5), 
                        width='stretch',
                        hide_index=True
                    )
                else:
                    st.dataframe(proyectos_filtrados.head(5), width='stretch', hide_index=True,
                                 column_config={
                                     "id": None,
                                     "proyecto_id": "ID Proyecto",
                                     "asesor": "Asesor",
                                     "cotizacion": "# de Cotización",
                                     "proyecto": "Proyecto/Cotización",
                                     "cliente": "Cliente",
                                     "status": "Status",
                                     "total": st.column_config.NumberColumn("Total MXN", format="$ %.2f"),
                                     "motivo_perdida": "Motivo de Pérdida",
                                     "observaciones": "Observaciones",
                                     "created_at": None,
                                     "updated_at": None
                                 })
            else:
                st.info("No hay proyectos registrados")

except Exception as e:
    st.error(f"Error al cargar datos: {str(e)}")
    st.info("Asegúrate de que las tablas CITAS, PROSPECCION, PROYECTOS y METAS existan en tu base de datos.")
