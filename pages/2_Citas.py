import streamlit as st
from utils.opciones import ASESORES, GIROS_NEGOCIO
from utils.supabase_client import get_supabase_client
import pandas as pd
from datetime import datetime, date
import math
import random
import time

st.set_page_config(page_title="Citas", page_icon=":material/calendar_today:", layout="wide")

# Estilos CSS personalizados con Materialize
st.markdown("""
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css">
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
<style>
    .stDataFrame { border-radius: 10px; }
    .stDateInput { text-align: center; }
    .edit-btn { color: #2196F3; cursor: pointer; }
    .delete-btn { color: #f44336; cursor: pointer; }
    .search-box { margin-bottom: 20px; }
    table { border-collapse: collapse; width: 100%; }
    th { background-color: #f5f5f5; padding: 12px; text-align: left; }
    td { padding: 10px; border-bottom: 1px solid #ddd; }
    tr:hover { background-color: #f9f9f9; }
</style>
""", unsafe_allow_html=True)

st.title(":material/calendar_today: Gestión de Citas")

# Conexión a Supabase
client = get_supabase_client()

# Inicializar estados de sesión
if 'page' not in st.session_state:
    st.session_state.page = 0
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""
if 'show_edit_dialog' not in st.session_state:
    st.session_state.show_edit_dialog = False
if 'edit_index' not in st.session_state:
    st.session_state.edit_index = None

# Cargar datos
@st.cache_data(ttl=5)
def load_data():
    try:
        response = client.select("citas").execute()
        if response.data:
            data = pd.DataFrame(response.data)
            return data
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error al cargar datos: {str(e)}")
        return pd.DataFrame()

def save_data(row_data, row_id=None):
    """Guarda o actualiza un registro en Supabase"""
    try:
        if row_id:
            # Actualizar registro existente
            client.update("citas", row_data, {"id": row_id})
        else:
            # Insertar nuevo registro
            client.insert("citas", row_data)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Error al guardar datos: {str(e)}")
        return False

def delete_data(row_id):
    """Elimina un registro de Supabase"""
    try:
        client.delete("citas", {"id": row_id})
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Error al eliminar datos: {str(e)}")
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
    st.warning(f"¿Estás seguro de que deseas eliminar esta cita?")
    
    st.info(f"**Prospecto:** {row.get('prospecto', '')}\n\n**Asesor:** {row.get('asesor', '')}\n\n**Fecha:** {row.get('fecha', '')}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button(":material/delete: Sí, Eliminar", width='stretch', type="primary"):
            # Obtener el ID de la base de datos (no el índice del DataFrame)
            row_id = row.get('id', '')
            if row_id and delete_data(row_id):
                st.success(":material/check_circle: Registro eliminado exitosamente")
                time.sleep(1)
                st.rerun()
    with col2:
        if st.button(":material/cancel: Cancelar", width='stretch'):
            st.rerun()

@st.dialog(":material/edit: Editar Cita")
def edit_dialog(idx):
    data = load_data()
    if idx not in data.index:
        st.error("Registro no encontrado")
        return
    
    row = data.loc[idx]
    
    with st.form("form_editar_cita"):
        # Mostrar ID (no editable)
        st.info(f"**ID:** {row.get('cita_id', '')}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            asesor_edit = st.selectbox("Asesor *", ASESORES, index=ASESORES.index(row.get('asesor', '').title()) if row.get('asesor', '').title() in ASESORES else 0).title()
            try:
                fecha_edit = st.date_input("Fecha *", 
                                          value=pd.to_datetime(row.get('fecha', date.today())))
            except:
                fecha_edit = st.date_input("Fecha *", value=date.today())
        
        with col2:
            prospecto_edit = st.text_input("Prospecto *", value=row.get('prospecto', '')).title()
            giro_edit = st.selectbox("Giro", GIROS_NEGOCIO, index=GIROS_NEGOCIO.index(row.get('giro', '').title()) if row.get('giro', '').title() in GIROS_NEGOCIO else 0).title()
        
        with col3:
            accion_seguir_edit = st.text_area("Acción a Seguir", value=row.get('accion_seguir', '')).capitalize()
            try:
                ultimo_contacto_edit = st.date_input("Último Contacto", 
                                                    value=pd.to_datetime(row.get('ultimo_contacto', date.today())))
            except:
                ultimo_contacto_edit = st.date_input("Último Contacto", value=date.today())
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            guardar = st.form_submit_button(":material/save: Guardar Cambios", width='stretch')
        with col_btn2:
            cancelar = st.form_submit_button(":material/cancel: Cancelar", width='stretch')
        
        if guardar:
            if asesor_edit and prospecto_edit:
                row_id = row.get('id', '')
                updated_data = {
                    'cita_id': row.get('cita_id', ''),
                    'asesor': asesor_edit,
                    'fecha': fecha_edit.strftime('%Y-%m-%d'),
                    'prospecto': prospecto_edit,
                    'giro': giro_edit,
                    'accion_seguir': accion_seguir_edit,
                    'ultimo_contacto': ultimo_contacto_edit.strftime('%Y-%m-%d')
                }
                if save_data(updated_data, row_id):
                    st.success(":material/check_circle: Cita actualizada exitosamente!")
                    st.session_state.show_edit_dialog = False
                    st.session_state.edit_index = None
                    st.rerun()
            else:
                st.error(":material/warning: Por favor completa los campos obligatorios (*)")
        
        if cancelar:
            st.session_state.show_edit_dialog = False
            st.session_state.edit_index = None
            st.rerun()

# Formulario para agregar nueva cita
st.markdown("#### :material/add: Agregar Nueva Cita")
with st.container():
    col1, col2, col3 = st.columns(3)
    
    with col1:
        asesor = st.selectbox("Selecciona un asesor de ventas", ASESORES, key="asesor_cita").title()
        fecha_cita = st.date_input("Fecha *", value=date.today(), key="fecha_cita")
    
    with col2:
        prospecto = st.text_input("Nombre de tu prospecto *", key="prospecto_cita").title()
        giro = st.selectbox("Selecciona un giro de negocio", GIROS_NEGOCIO, key="giro_cita").title()
        if giro == "Otro":
            giro = st.text_input("Especifica el giro de negocio", key="giro_otro_cita").title()
    
    with col3:
        accion_seguir = st.text_area("Acción a Seguir", key="accion_cita").capitalize()
        ultimo_contacto = st.date_input("Último Contacto", value=date.today(), key="ultimo_contacto_cita")
    
    if st.button(":material/save: Guardar Cita", key="guardar_cita", type="primary", use_container_width=True):
        if asesor and prospecto:
            nuevo_id = generar_id()
            nueva_cita = {
                'cita_id': nuevo_id,
                'asesor': asesor,
                'fecha': fecha_cita.strftime('%Y-%m-%d'),
                'prospecto': prospecto,
                'giro': giro,
                'accion_seguir': accion_seguir,
                'ultimo_contacto': ultimo_contacto.strftime('%Y-%m-%d')
            }
            if save_data(nueva_cita):
                st.success(":material/check_circle: Cita agregada exitosamente!")
                time.sleep(1)
                st.rerun()
        else:
            st.error(":material/warning: Por favor completa los campos obligatorios (*)")

st.markdown("---")

# Mostrar tabla de citas
st.markdown("#### :material/list: Lista de Citas")

data = load_data()

if len(data) > 0:
    # Búsqueda
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("")
    with col2:
        search_query = st.text_input(":material/search: Buscar", value=st.session_state.search_query, 
                                     placeholder="Buscar por nombre, asesor, fecha...",
                                     key="search_input")
        st.session_state.search_query = search_query
    
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
    
    if st.session_state.page >= total_pages:
        st.session_state.page = max(0, total_pages - 1)
    
    start_idx = st.session_state.page * items_per_page
    end_idx = min(start_idx + items_per_page, total_items)
    page_data = filtered_data.iloc[start_idx:end_idx]
    
    # Mostrar tabla con acciones
    if len(page_data) > 0:
        # Encabezados
        header_cols = st.columns([1, 1.5, 1, 2, 2, 0.7, 0.7])
        headers = ['Fecha', 'Asesor', 'Giro', 'Prospecto', 'Acción', '', '']
        for idx, (col, header) in enumerate(zip(header_cols, headers)):
            with col:
                if header:
                    st.markdown(f"**{header}**")
        
        st.markdown("---")
        
        for idx, row in page_data.iterrows():
            cols = st.columns([1, 1.5, 1, 2, 2, 0.7, 0.7])
            
            with cols[0]:
                st.text(row.get('fecha', ''))
            with cols[1]:
                st.text(row.get('asesor', ''))
            with cols[2]:
                giro = str(row.get('giro', ''))
                st.text(giro[:15] + '...' if len(giro) > 15 else giro)
            with cols[3]:
                st.text(row.get('prospecto', ''))
            with cols[4]:
                accion = str(row.get('accion_seguir', ''))
                st.text(accion[:30] + '...' if len(accion) > 30 else accion)
            with cols[5]:
                if st.button(":material/edit:", key=f"edit_{idx}", help="Editar", use_container_width=True):
                    edit_dialog(idx)
            with cols[6]:
                if st.button(":material/delete:", key=f"delete_{idx}", help="Eliminar", use_container_width=True):
                    confirm_delete(idx)
        
        # Controles de paginación
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.button(":material/arrow_back: Anterior", disabled=(st.session_state.page == 0)):
                st.session_state.page -= 1
                st.rerun()
        
        with col2:
            st.markdown(f"<center>Página {st.session_state.page + 1} de {total_pages} ({total_items} registros)</center>", 
                       unsafe_allow_html=True)
        
        with col3:
            if st.button("Siguiente :material/arrow_forward:", disabled=(st.session_state.page >= total_pages - 1)):
                st.session_state.page += 1
                st.rerun()
    else:
        st.info("No se encontraron resultados para la búsqueda.")
else:
    st.info(":material/note: No hay citas registradas. Agrega tu primera cita usando el formulario de arriba.")
