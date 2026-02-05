"""
Gestión de filtros para el Dashboard
"""
import streamlit as st
import pandas as pd


class DashboardFilters:
    """Manejador de filtros del dashboard"""
    
    def __init__(self):
        """Inicializa los filtros del dashboard"""
        self._inicializar_session_state()
    
    def _inicializar_session_state(self):
        """Inicializa los estados de sesión para filtros"""
        if 'fecha_inicio_filter' not in st.session_state:
            st.session_state.fecha_inicio_filter = None
        if 'fecha_fin_filter' not in st.session_state:
            st.session_state.fecha_fin_filter = None
        if 'asesor_filter' not in st.session_state:
            st.session_state.asesor_filter = "Todos"
        if 'filtros_version' not in st.session_state:
            st.session_state.filtros_version = 0
    
    def limpiar_filtros(self):
        """Limpia todos los filtros activos"""
        st.session_state.fecha_inicio_filter = None
        st.session_state.fecha_fin_filter = None
        st.session_state.asesor_filter = "Todos"
        st.session_state.filtros_version += 1
    
    def mostrar_filtros(self, asesores_opciones):
        """
        Muestra los controles de filtro en la interfaz
        
        Args:
            asesores_opciones: Lista de opciones de asesores
            
        Returns:
            tuple: (fecha_inicio, fecha_fin, asesor_seleccionado)
        """
        st.markdown("#### :material/search: Filtros")
        
        # Botón de limpiar filtros
        if st.button(":material/refresh: Limpiar Filtros"):
            self.limpiar_filtros()
            st.rerun()
        
        col_filter1, col_filter2, col_filter3 = st.columns([2, 2, 2])
        
        with col_filter1:
            fecha_inicio = st.date_input(
                "Fecha Inicio",
                value=st.session_state.fecha_inicio_filter,
                key=f"fecha_inicio_input_{st.session_state.filtros_version}",
                help="Selecciona fecha de inicio"
            )
            st.session_state.fecha_inicio_filter = fecha_inicio
        
        with col_filter2:
            fecha_fin = st.date_input(
                "Fecha Fin",
                value=st.session_state.fecha_fin_filter,
                key=f"fecha_fin_input_{st.session_state.filtros_version}",
                help="Selecciona fecha de fin"
            )
            st.session_state.fecha_fin_filter = fecha_fin
        
        with col_filter3:
            asesor_seleccionado = st.selectbox(
                "asesor",
                options=asesores_opciones,
                index=asesores_opciones.index(st.session_state.asesor_filter) 
                    if st.session_state.asesor_filter in asesores_opciones else 0,
                key=f"asesor_input_{st.session_state.filtros_version}"
            )
            st.session_state.asesor_filter = asesor_seleccionado
        
        return fecha_inicio, fecha_fin, asesor_seleccionado
    
    def aplicar_filtros(self, citas_data, prospeccion_data, proyectos_data, 
                       fecha_inicio, fecha_fin, asesor_seleccionado):
        """
        Aplica filtros a los datos
        
        Args:
            citas_data: DataFrame de citas
            prospeccion_data: DataFrame de prospección
            proyectos_data: DataFrame de proyectos
            fecha_inicio: Fecha de inicio del filtro
            fecha_fin: Fecha de fin del filtro
            asesor_seleccionado: Asesor seleccionado
            
        Returns:
            tuple: (citas_filtradas, prospeccion_filtrada, proyectos_filtrados)
        """
        citas_filtradas = citas_data.copy()
        prospeccion_filtrada = prospeccion_data.copy()
        proyectos_filtrados = proyectos_data.copy()
        
        # Convertir columnas de fecha a datetime - formato dd/mm/aaaa
        if 'fecha' in citas_filtradas.columns and len(citas_filtradas) > 0:
            citas_filtradas['fecha_dt'] = pd.to_datetime(
                citas_filtradas['fecha'], dayfirst=True, errors='coerce'
            )
        
        if 'fecha' in prospeccion_filtrada.columns and len(prospeccion_filtrada) > 0:
            prospeccion_filtrada['fecha_dt'] = pd.to_datetime(
                prospeccion_filtrada['fecha'], dayfirst=True, errors='coerce'
            )
        
        # Aplicar filtro por fecha si AMBAS fechas están definidas
        if fecha_inicio is not None and fecha_fin is not None:
            fecha_inicio_dt = pd.to_datetime(fecha_inicio)
            fecha_fin_dt = pd.to_datetime(fecha_fin)
            
            if 'fecha_dt' in citas_filtradas.columns:
                mask_citas = (
                    (citas_filtradas['fecha_dt'].notna()) &
                    (citas_filtradas['fecha_dt'] >= fecha_inicio_dt) &
                    (citas_filtradas['fecha_dt'] <= fecha_fin_dt)
                )
                citas_filtradas = citas_filtradas[mask_citas].copy()
            
            if 'fecha_dt' in prospeccion_filtrada.columns:
                mask_prospeccion = (
                    (prospeccion_filtrada['fecha_dt'].notna()) &
                    (prospeccion_filtrada['fecha_dt'] >= fecha_inicio_dt) &
                    (prospeccion_filtrada['fecha_dt'] <= fecha_fin_dt)
                )
                prospeccion_filtrada = prospeccion_filtrada[mask_prospeccion].copy()
        
        # Filtro por asesor
        if asesor_seleccionado and asesor_seleccionado != "Todos":
            if 'asesor' in citas_filtradas.columns and len(citas_filtradas) > 0:
                mask_asesor = citas_filtradas['asesor'].astype(str).str.strip() == asesor_seleccionado
                citas_filtradas = citas_filtradas[mask_asesor].copy()
            
            if 'asesor' in prospeccion_filtrada.columns and len(prospeccion_filtrada) > 0:
                mask_asesor = prospeccion_filtrada['asesor'].astype(str).str.strip() == asesor_seleccionado
                prospeccion_filtrada = prospeccion_filtrada[mask_asesor].copy()
            
            if 'asesor' in proyectos_filtrados.columns and len(proyectos_filtrados) > 0:
                mask_asesor = proyectos_filtrados['asesor'].astype(str).str.strip() == asesor_seleccionado
                proyectos_filtrados = proyectos_filtrados[mask_asesor].copy()
        
        # Limpiar columnas temporales antes de devolver
        if 'fecha_dt' in citas_filtradas.columns:
            citas_filtradas = citas_filtradas.drop(columns=['fecha_dt'])
        if 'fecha_dt' in prospeccion_filtrada.columns:
            prospeccion_filtrada = prospeccion_filtrada.drop(columns=['fecha_dt'])
        
        return citas_filtradas, prospeccion_filtrada, proyectos_filtrados
