"""
Visualizaciones y gráficos para el Dashboard
"""
import streamlit as st
import pandas as pd
import plotly.express as px


def mostrar_metricas_principales(metricas):
    """
    Muestra las métricas principales en columnas
    
    Args:
        metricas: Diccionario con las métricas a mostrar
    """
    st.markdown("#### :material/insights: Métricas Principales")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric(label="Total Citas", value=metricas['total_citas'])
    
    with col2:
        st.metric(label="Total Prospectos", value=metricas['total_prospectos'])
    
    with col3:
        st.metric(label="Total Proyectos", value=metricas['total_proyectos'])
    
    with col4:
        st.metric(
            label="Ticket Promedio ($)",
            value=f"${metricas['ticket_promedio']:,.2f}"
        )
    
    with col5:
        st.metric(
            label="Total Cartera ($)",
            value=f"${metricas['total_cartera']:,.2f}"
        )


def mostrar_metricas_citas_semanales(metricas_citas):
    """
    Muestra las métricas de citas semanales
    
    Args:
        metricas_citas: Diccionario con las métricas de citas semanales
    """
    if metricas_citas:
        st.markdown("#### :material/calendar_today: Cumplimiento de Citas Semanales")
        
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


def mostrar_metricas_proyectos_estado(metricas_estado):
    """
    Muestra las métricas de proyectos por estado
    
    Args:
        metricas_estado: Diccionario con métricas por estado
    """
    st.markdown("#### :material/monetization_on: Métricas de Proyectos por Estado")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label=":material/build: Proyectos en Proceso ($)",
            value=f"${metricas_estado['proyectos_proceso']:,.2f}"
        )
    
    with col2:
        st.metric(
            label=":material/emoji_events: Proyectos Ganados ($)",
            value=f"${metricas_estado['proyectos_ganados']:,.2f}"
        )
    
    with col3:
        st.metric(
            label=":material/cancel: Proyectos Perdidos ($)",
            value=f"${metricas_estado['proyectos_perdidos']:,.2f}"
        )


def mostrar_metricas_ventas_cotizaciones(metricas_ventas):
    """
    Muestra las métricas de ventas y cotizaciones
    
    Args:
        metricas_ventas: Diccionario con métricas de ventas y cotizaciones
    """
    st.markdown("#### :material/monetization_on: Ventas y Cotizaciones")
    
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


def mostrar_metricas_ventas_trimestrales(metricas_trimestre):
    """
    Muestra las métricas de ventas trimestrales
    
    Args:
        metricas_trimestre: Diccionario con métricas de ventas trimestrales
    """
    st.markdown(f"#### :material/calendar_month: Ventas Trimestrales - Q{metricas_trimestre['trimestre_actual']}")
    
    col_t1, col_t2 = st.columns(2)
    
    with col_t1:
        st.metric(
            label=f":material/flag: Meta Q{metricas_trimestre['trimestre_actual']}",
            value=f"${metricas_trimestre['meta_trimestre_total']:,.2f}"
        )
    
    with col_t2:
        st.metric(
            label=":material/trending_up: Ventas Acumuladas del Trimestre",
            value=f"${metricas_trimestre['ventas_trimestre_total']:,.2f}",
            delta=metricas_trimestre['delta_ventas'],
            delta_color=metricas_trimestre['color_ventas']
        )


def mostrar_graficos(total_citas, total_prospectos, total_proyectos):
    """
    Muestra los gráficos de distribución y comparativa
    
    Args:
        total_citas: Total de citas
        total_prospectos: Total de prospectos
        total_proyectos: Total de proyectos
    """
    col1, col2 = st.columns(2)
    
    datos_dist = pd.DataFrame({
        'Categoría': ['Citas', 'Prospectos', 'Proyectos'],
        'Cantidad': [total_citas, total_prospectos, total_proyectos]
    })
    
    with col1:
        st.markdown("#### :material/pie_chart: Distribución de Registros")
        fig = px.pie(
            datos_dist,
            values='Cantidad',
            names='Categoría',
            color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### :material/trending_up: Comparativa de Módulos")
        fig = px.bar(
            datos_dist,
            x='Categoría',
            y='Cantidad',
            color='Categoría',
            color_discrete_sequence=['#FF6B6B', '#4ECDC4', '#45B7D1']
        )
        st.plotly_chart(fig, use_container_width=True)


def mostrar_grafico_proyectos_estado(proyectos_filtrados):
    """
    Muestra un gráfico de pie con la distribución de proyectos por estado
    
    Args:
        proyectos_filtrados: DataFrame de proyectos filtrados
    """
    if len(proyectos_filtrados) > 0 and 'status' in proyectos_filtrados.columns:
        # Contar proyectos por estado
        proyectos_por_estado = proyectos_filtrados.groupby('status').size().reset_index(name='Cantidad')
        
        st.markdown("#### :material/donut_small: Distribución de Proyectos por Estado")
        
        # Definir colores según el estado
        color_map = {
            'En Proceso': '#FFA500',  # Naranja
            'Vendido': '#2ECC71',  # Verde
            'Ganado': '#2ECC71',   # Verde
            'Perdido': '#E74C3C'   # Rojo
        }
        
        # Crear lista de colores basada en los estados presentes
        colores = [color_map.get(estado, '#95A5A6') for estado in proyectos_por_estado['status']]
        
        fig = px.pie(
            proyectos_por_estado,
            values='Cantidad',
            names='status',
            color='status',
            color_discrete_map=color_map,
            hole=0.4  # Hacer un donut chart
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay proyectos para mostrar la distribución por estado")


def mostrar_grafico_citas_por_mes(citas_filtradas):
    """
    Muestra un gráfico de área con el número de citas por mes
    
    Args:
        citas_filtradas: DataFrame de citas filtradas
    """
    if len(citas_filtradas) > 0 and 'fecha' in citas_filtradas.columns:
        # Crear una copia para no modificar el DataFrame original
        df_temp = citas_filtradas.copy()
        
        # Convertir la columna de fecha a datetime con formato específico
        df_temp['fecha'] = pd.to_datetime(df_temp['fecha'], errors='coerce', dayfirst=True)
        
        # Filtrar fechas válidas
        citas_con_fecha = df_temp[df_temp['fecha'].notna()].copy()
        
        if len(citas_con_fecha) > 0:
            # Diccionario de meses en español
            meses_es = {
                1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
                5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
                9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
            }
            
            # Extraer año y mes
            citas_con_fecha['ano'] = citas_con_fecha['fecha'].dt.year
            citas_con_fecha['Mes_Num'] = citas_con_fecha['fecha'].dt.month
            citas_con_fecha['ano_mes'] = citas_con_fecha['fecha'].dt.to_period('M')
            
            # Contar citas por mes
            citas_por_mes = citas_con_fecha.groupby(['ano_mes', 'ano', 'Mes_Num']).size().reset_index(name='Cantidad')
            
            # Crear etiqueta en español
            citas_por_mes['mes'] = citas_por_mes.apply(
                lambda row: f"{meses_es[row['Mes_Num']]} {int(row['ano'])}", 
                axis=1
            )
            
            # Ordenar por fecha
            citas_por_mes = citas_por_mes.sort_values('ano_mes')
            
            # Crear el gráfico de área
            fig = px.area(
                citas_por_mes,
                x='mes',
                y='Cantidad',
                title='Evolución de Citas por Mes',
                labels={'mes': 'mes', 'Cantidad': 'Número de Citas'},
                color_discrete_sequence=['#4ECDC4']
            )
            
            # Personalizar el gráfico con líneas suavizadas y degradado
            fig.update_traces(
                line_shape='spline',  # Líneas suavizadas
                fillgradient=dict(
                    type='vertical',
                    colorscale=[
                        [0, 'rgba(78, 205, 196, 0.1)'],  # Color más transparente en la parte inferior
                        [1, 'rgba(78, 205, 196, 0.6)']   # Color más opaco en la parte superior
                    ]
                ),
                line=dict(width=3, color='#4ECDC4')
            )
            
            # Personalizar el layout
            fig.update_layout(
                xaxis_title='mes',
                yaxis_title='Número de Citas',
                hovermode='x unified',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12),
                margin=dict(l=20, r=20, t=40, b=20)
            )
            
            # Personalizar los ejes
            fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
            fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='rgba(128,128,128,0.2)')
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No hay citas con fechas válidas para mostrar la evolución mensual")
    else:
        st.info("No hay citas disponibles para mostrar la evolución mensual")


def mostrar_actividad_reciente(citas_filtradas, prospeccion_filtrada, proyectos_filtrados):
    """
    Muestra las tablas de actividad reciente
    
    Args:
        citas_filtradas: DataFrame de citas filtradas
        prospeccion_filtrada: DataFrame de prospección filtrada
        proyectos_filtrados: DataFrame de proyectos filtrados
    """
    st.markdown("---")
    st.markdown("#### :material/description: Actividad Reciente")
    
    tab1, tab2, tab3 = st.tabs(["Últimas Citas", "Últimos Prospectos", "Últimos Proyectos"])
    
    with tab1:
        if len(citas_filtradas) > 0:
            # Seleccionar solo columnas relevantes para vista móvil
            columnas_mostrar = []
            for col in ['fecha', 'asesor', 'cliente', 'empresa', 'status']:
                if col in citas_filtradas.columns:
                    columnas_mostrar.append(col)
            
            if columnas_mostrar:
                st.dataframe(
                    citas_filtradas[columnas_mostrar].head(5), 
                    width='stretch',
                    hide_index=True
                )
            else:
                st.dataframe(citas_filtradas.head(5), width='stretch', hide_index=True)
        else:
            st.info("No hay citas registradas")
    
    with tab2:
        if len(prospeccion_filtrada) > 0:
            # Seleccionar solo columnas relevantes para vista móvil
            columnas_mostrar = []
            for col in ['fecha', 'asesor', 'prospecto', 'empresa', 'status']:
                if col in prospeccion_filtrada.columns:
                    columnas_mostrar.append(col)
            
            if columnas_mostrar:
                st.dataframe(
                    prospeccion_filtrada[columnas_mostrar].head(5), 
                    width='stretch',
                    hide_index=True
                )
            else:
                st.dataframe(prospeccion_filtrada.head(5), width='stretch', hide_index=True)
        else:
            st.info("No hay prospectos registrados")
    
    with tab3:
        if len(proyectos_filtrados) > 0:
            # Seleccionar solo columnas relevantes para vista móvil
            columnas_mostrar = []
            for col in ['fecha', 'asesor', 'cliente', 'total', 'status']:
                if col in proyectos_filtrados.columns:
                    columnas_mostrar.append(col)
            
            if columnas_mostrar:
                st.dataframe(
                    proyectos_filtrados[columnas_mostrar].head(5), 
                    width='stretch',
                    hide_index=True
                )
            else:
                st.dataframe(proyectos_filtrados.head(5), width='stretch', hide_index=True)
        else:
            st.info("No hay proyectos registrados")

