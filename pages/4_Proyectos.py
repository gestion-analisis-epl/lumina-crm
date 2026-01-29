import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, date
import math
import random
import time

from utils.opciones import ASESORES

st.set_page_config(page_title="Proyectos", page_icon="📂", layout="wide")

# Estilos CSS personalizados con Materialize
st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css">
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
<style>
    .stDataFrame { border-radius: 10px; }
    .edit-btn { color: #2196F3; cursor: pointer; }
    .delete-btn { color: #f44336; cursor: pointer; }
    .search-box { margin-bottom: 20px; }
    table { border-collapse: collapse; width: 100%; }
    th { background-color: #f5f5f5; padding: 12px; text-align: left; }
    td { padding: 10px; border-bottom: 1px solid #ddd; }
    tr:hover { background-color: #f9f9f9; }
</style>
""", unsafe_allow_html=True)

st.title(":material/folder: Gestión de Proyectos")

# Conexión a Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# Inicializar estados de sesión
if 'page_proyectos' not in st.session_state:
    st.session_state.page_proyectos = 0
if 'search_query_proyectos' not in st.session_state:
    st.session_state.search_query_proyectos = ""
if 'show_edit_dialog_proyectos' not in st.session_state:
    st.session_state.show_edit_dialog_proyectos = False
if 'edit_index_proyectos' not in st.session_state:
    st.session_state.edit_index_proyectos = None
if 'status_proyectos' not in st.session_state:
    st.session_state.status_proyectos = "En Proceso"

# Cargar datos
@st.cache_data(ttl=5)
def load_data():
    try:
        data = conn.read(worksheet="PROYECTOS", ttl=5)
        data = data.dropna(how="all")
        return data
    except Exception as e:
        st.error(f"Error al cargar datos: {str(e)}")
        return pd.DataFrame()

def save_data(df):
    try:
        conn.update(worksheet="PROYECTOS", data=df)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Error al guardar datos: {str(e)}")
        return False

def generar_id():
    """Genera un ID con formato ID-XXXXXXXXXXXXX"""
    numero = random.randint(1000000000000, 9999999999999)
    return f"ID-{numero}"

@st.dialog(":material/warning: Confirmar Eliminación")
def confirm_delete(idx):
    data = load_data()
    if idx not in data.index:
        st.error("Registro no encontrado")
        return
    
    row = data.loc[idx]
    st.warning(f"¿Estás seguro de que deseas eliminar este proyecto?")
    
    st.info(f"**Proyecto:** {row.get('PROYECTO', '')}\n\n**Cliente:** {row.get('CLIENTE', '')}\n\n**Asesor:** {row.get('ASESOR', '')}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button(":material/delete: Sí, Eliminar", width='stretch', type="primary"):
            data = data.drop(idx)
            if save_data(data):
                st.success(":material/check_circle: Registro eliminado exitosamente")
                time.sleep(1)
                st.rerun()
    with col2:
        if st.button(":material/cancel: Cancelar", width='stretch'):
            st.rerun()

@st.dialog(":material/edit: Editar Proyecto")
def edit_dialog(idx):
    data = load_data()
    if idx not in data.index:
        st.error("Registro no encontrado")
        return
    
    row = data.loc[idx]
    
    # Mostrar ID (no editable)
    st.info(f"**ID:** {row.get('ID', '')}")
    
    # Status fuera del formulario para permitir interactividad
    status_options = ["Perdido", "Ganado", "En Proceso"]
    status_actual = row.get('STATUS', 'En Proceso')
    status_index = status_options.index(status_actual) if status_actual in status_options else 2
    
    status_edit = st.selectbox("Status", status_options, index=status_index, key=f"status_edit_{idx}")
    
    with st.form("form_editar_proyecto"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            asesor_edit = st.selectbox("Selecciona un asesor de ventas", ASESORES, 
                                       index=ASESORES.index(row.get('ASESOR', '')) if row.get('ASESOR', '') in ASESORES else None)
            cotizacion_edit = st.text_input("Cotización", value=row.get('COTIZACIÓN', ''))
        
        with col2:
            proyecto_edit = st.text_input("Proyecto *", value=row.get('PROYECTO', ''))
            cliente_edit = st.text_input("Cliente *", value=row.get('CLIENTE', ''))
        
        with col3:
            # Mostrar motivo solo si status es Perdido
            motivo_perdida_edit = ""
            if status_edit == "Perdido":
                motivo_opciones = ["Precio", "Stock/Inventario", "Otro"]
                motivo_actual = row.get('MOTIVO PERDIDA', '')
                motivo_index = motivo_opciones.index(motivo_actual) if motivo_actual in motivo_opciones else 0
                motivo_perdida_edit = st.selectbox("Motivo de Pérdida *", motivo_opciones, index=motivo_index)
            
            total_edit = st.number_input("Total ($) *", min_value=0.0, step=0.01, 
                                        value=float(row.get('TOTAL', 0)))
        
        observaciones_edit = st.text_area("Observaciones", value=row.get('OBSERVACIONES', ''))
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            guardar = st.form_submit_button(":material/save: Guardar Cambios", width='stretch')
        with col_btn2:
            cancelar = st.form_submit_button(":material/cancel: Cancelar", width='stretch')
        
        if guardar:
            if asesor_edit and proyecto_edit and cliente_edit:
                # Validar motivo si es Perdido
                if status_edit == "Perdido" and not motivo_perdida_edit:
                    st.error(":material/warning: Por favor selecciona el motivo de pérdida")
                else:
                    data.loc[idx] = {
                        'ID': row.get('ID', ''),
                        'ASESOR': asesor_edit,
                        'COTIZACIÓN': cotizacion_edit,
                        'PROYECTO': proyecto_edit,
                        'CLIENTE': cliente_edit,
                        'STATUS': status_edit,
                        'TOTAL': total_edit,
                        'MOTIVO PERDIDA': motivo_perdida_edit if status_edit == "Perdido" else "",
                        'OBSERVACIONES': observaciones_edit
                    }
                    if save_data(data):
                        st.success(":material/check_circle: Proyecto actualizado exitosamente!")
                        st.session_state.show_edit_dialog_proyectos = False
                        st.session_state.edit_index_proyectos = None
                        st.rerun()
            else:
                st.error(":material/warning: Por favor completa los campos obligatorios (*)")
        
        if cancelar:
            st.session_state.show_edit_dialog_proyectos = False
            st.session_state.edit_index_proyectos = None
            st.rerun()

# Formulario para agregar nuevo proyecto
st.markdown("#### :material/add: Agregar Nuevo Proyecto")

# Contenedor visual que simula un formulario pero permite interactividad
with st.container():
    col1, col2, col3 = st.columns(3)
    
    with col1:
        asesor = st.selectbox("Selecciona un asesor de ventas", ASESORES, key="asesor_nuevo").title()
        cotizacion = st.text_input("Cotización", key="cotizacion_nueva")
    
    with col2:
        proyecto = st.text_input("Proyecto *", key="proyecto_nuevo")
        cliente = st.text_input("Cliente *", key="cliente_nuevo")
    
    with col3:
        status = st.selectbox("Status *", ["Perdido", "Ganado", "En Proceso"], index=2, key="status_nuevo")
        
        # Mostrar motivo de pérdida solo si status es "Perdido"
        motivo_perdida = ""
        if status == "Perdido":
            motivo_perdida = st.selectbox("Motivo de Pérdida *", ["Precio", "Stock/Inventario", "Otro"], key="motivo_nuevo")
        
        total = st.number_input("Total ($) *", min_value=0.0, step=0.01, key="total_nuevo")
    
    observaciones = st.text_area("Observaciones", key="observaciones_nueva")
    
    if st.button(":material/save: Guardar Proyecto", key="guardar_proyecto", type="primary", use_container_width=True):
        if asesor and proyecto and cliente:
            # Validar que si es Perdido, tenga motivo
            if status == "Perdido" and not motivo_perdida:
                st.error(":material/warning: Por favor selecciona el motivo de pérdida")
            else:
                data = load_data()
                nuevo_id = generar_id()
                nueva_fila = pd.DataFrame([{
                    'ID': nuevo_id,
                    'ASESOR': asesor,
                    'COTIZACIÓN': cotizacion,
                    'PROYECTO': proyecto,
                    'CLIENTE': cliente,
                    'STATUS': status,
                    'TOTAL': total,
                    'MOTIVO PERDIDA': motivo_perdida if status == "Perdido" else "",
                    'OBSERVACIONES': observaciones.capitalize() if observaciones else ""
                }])
                data = pd.concat([data, nueva_fila], ignore_index=True)
                if save_data(data):
                    st.success(":material/check_circle: Proyecto agregado exitosamente!")
                    time.sleep(1)
                    st.rerun()
        else:
            st.error(":material/warning: Por favor completa los campos obligatorios (*)")

st.markdown("---")

# Mostrar tabla de proyectos
st.markdown("#### :material/list: Lista de Proyectos")

data = load_data()

if len(data) > 0:
    # Búsqueda
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("")
    with col2:
        search_query = st.text_input(":material/search: Buscar", value=st.session_state.search_query_proyectos, 
                                     placeholder="Buscar por proyecto, cliente, responsable...",
                                     key="search_input_proyectos")
        st.session_state.search_query_proyectos = search_query
    
    # Filtrar datos según búsqueda
    if search_query:
        mask = data.astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)
        filtered_data = data[mask]
    else:
        filtered_data = data
    
    # Paginación
    items_per_page = 10
    total_items = len(filtered_data)
    total_pages = math.ceil(total_items / items_per_page)
    
    if st.session_state.page_proyectos >= total_pages:
        st.session_state.page_proyectos = max(0, total_pages - 1)
    
    start_idx = st.session_state.page_proyectos * items_per_page
    end_idx = min(start_idx + items_per_page, total_items)
    page_data = filtered_data.iloc[start_idx:end_idx]
    
    # Mostrar tabla con acciones
    if len(page_data) > 0:
        # Encabezados
        header_cols = st.columns([1.5, 2, 1.5, 1.2, 1.5, 0.7, 0.7])
        headers = ['Asesor', 'Proyecto', 'Cliente', 'Status', 'Total', '', '']
        for idx, (col, header) in enumerate(zip(header_cols, headers)):
            with col:
                if header:
                    st.markdown(f"**{header}**")
        
        st.markdown("---")
        
        for idx, row in page_data.iterrows():
            cols = st.columns([1.5, 2, 1.5, 1.2, 1.5, 0.7, 0.7])
            
            with cols[0]:
                st.text(row.get('ASESOR', ''))
            with cols[1]:
                proyecto = str(row.get('PROYECTO', ''))
                st.text(proyecto[:25] + '...' if len(proyecto) > 25 else proyecto)
            with cols[2]:
                st.text(row.get('CLIENTE', ''))
            with cols[3]:
                status = row.get('STATUS', '').title()
                color_map = {
                    'Vendido': '#4ac783',
                    'Ganado': '#4ac783',
                    'Perdido': '#ff715a',
                    'Proceso': '#fdc400'
                }
                bg_color = color_map.get(status, "#007fd6")
                st.markdown(f'<div style="background-color: {bg_color}; color: white; padding: 4px 8px; border-radius: 4px; text-align: center; font-size: 12px;">{status}</div>', unsafe_allow_html=True)
            with cols[4]:
                total_val = row.get('TOTAL', 0)
                st.text(f"${total_val:,.2f}" if pd.notna(total_val) else "$0.00")
            with cols[5]:
                if st.button(":material/edit:", key=f"edit_proy_{idx}", help="Editar", use_container_width=True):
                    edit_dialog(idx)
            with cols[6]:
                if st.button(":material/delete:", key=f"delete_proy_{idx}", help="Eliminar", use_container_width=True):
                    confirm_delete(idx)
        
        # Controles de paginación
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.button(":material/arrow_back: Anterior", disabled=(st.session_state.page_proyectos == 0), key="prev_proy"):
                st.session_state.page_proyectos -= 1
                st.rerun()
        
        with col2:
            st.markdown(f"<center>Página {st.session_state.page_proyectos + 1} de {total_pages} ({total_items} registros)</center>", 
                       unsafe_allow_html=True)
        
        with col3:
            if st.button("Siguiente :material/arrow_forward:", disabled=(st.session_state.page_proyectos >= total_pages - 1), key="next_proy"):
                st.session_state.page_proyectos += 1
                st.rerun()
    else:
        st.info("No se encontraron resultados para la búsqueda.")
else:
    st.info(":material/note: No hay proyectos registrados. Agrega tu primer proyecto usando el formulario de arriba.")
