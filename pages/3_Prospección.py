import streamlit as st
from utils.supabase_client import get_supabase_client
import pandas as pd
from datetime import datetime, date
import math
import random
import time
from io import BytesIO

from utils.opciones import ASESORES

st.set_page_config(page_title="Prospección", page_icon="🎯", layout="wide")

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

st.title(":material/emoji_events: Gestión de Prospección")

# Conexión a Supabase
client = get_supabase_client()

# Inicializar estados de sesión
if 'page_prospeccion' not in st.session_state:
    st.session_state.page_prospeccion = 0
if 'search_query_prospeccion' not in st.session_state:
    st.session_state.search_query_prospeccion = ""
if 'show_edit_dialog_prospeccion' not in st.session_state:
    st.session_state.show_edit_dialog_prospeccion = False
if 'edit_index_prospeccion' not in st.session_state:
    st.session_state.edit_index_prospeccion = None

# Cargar datos
@st.cache_data(ttl=5)
def load_data():
    try:
        response = client.select("prospeccion").execute()
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
            client.update("prospeccion", row_data, {"id": row_id})
        else:
            # Insertar nuevo registro
            client.insert("prospeccion", row_data)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Error al guardar datos: {str(e)}")
        return False

def delete_data(row_id):
    """Elimina un registro de Supabase"""
    try:
        client.delete("prospeccion", {"id": row_id})
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
    st.warning(f"¿Estás seguro de que deseas eliminar este prospecto?")
    
    st.info(f"**Prospecto:** {row.get('prospecto', '')}\n\n**Asesor:** {row.get('asesor', '')}\n\n**Fecha:** {row.get('fecha', '')}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button(":material/delete: Sí, Eliminar", width='stretch', type="primary"):
            # Obtener el ID de la base de datos
            row_id = row.get('id', '')
            if row_id and delete_data(row_id):
                st.success(":material/check_circle: Registro eliminado exitosamente")
                time.sleep(1)
                st.rerun()
    with col2:
        if st.button(":material/cancel: Cancelar", width='stretch'):
            st.rerun()

@st.dialog(":material/edit: Editar Prospecto")
def edit_dialog(idx):
    data = load_data()
    if idx not in data.index:
        st.error("Registro no encontrado")
        return
    
    row = data.loc[idx]
    
    with st.form("form_editar_prospecto"):
        # Mostrar ID (no editable)
        st.info(f"**ID:** {row.get('prospecto_id', '')}")
        
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
            tipo_options = ["Venta", "Renta"]
            tipo_edit = st.selectbox("Tipo", tipo_options,
                                        index=tipo_options.index(row.get('tipo', 'Venta')) if row.get('tipo', 'Venta') in tipo_options else 0)
        
        with col3:
            accion_edit = st.text_area("Acción *", value=row.get('accion', '')).capitalize()
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            guardar = st.form_submit_button(":material/save: Guardar Cambios", width='stretch')
        with col_btn2:
            cancelar = st.form_submit_button(":material/cancel: Cancelar", width='stretch')
        
        if guardar:
            if asesor_edit and prospecto_edit and accion_edit:
                row_id = row.get('id', '')
                updated_data = {
                    'prospecto_id': row.get('prospecto_id', ''),
                    'asesor': asesor_edit,
                    'fecha': fecha_edit.strftime('%Y-%m-%d'),
                    'prospecto': prospecto_edit.upper(),
                    'tipo': tipo_edit,
                    'accion': accion_edit.upper()
                }
                if save_data(updated_data, row_id):
                    st.success(":material/check_circle: Prospecto actualizado exitosamente!")
                    st.session_state.show_edit_dialog_prospeccion = False
                    st.session_state.edit_index_prospeccion = None
                    st.rerun()
            else:
                st.error(":material/warning: Por favor completa los campos obligatorios (*)")
        
        if cancelar:
            st.session_state.show_edit_dialog_prospeccion = False
            st.session_state.edit_index_prospeccion = None
            st.rerun()

# Formulario para agregar nuevo prospecto
st.markdown("#### :material/add: Agregar Nuevo Prospecto")
with st.container():
    col1, col2, col3 = st.columns(3)
    
    with col1:
        asesor = st.selectbox("Asesor *", ASESORES, key="asesor_prospecto").title()
        fecha = st.date_input("Fecha *", value=date.today(), key="fecha_prospecto")
    
    with col2:
        prospecto = st.text_input("Prospecto *", key="nombre_prospecto").title()
        tipo = st.selectbox("Tipo", ["Venta", "Renta"], key="tipo_prospecto")
    
    with col3:
        accion = st.text_area("Acción *", key="accion_prospecto").capitalize()
    
    if st.button(":material/save: Guardar Prospecto", key="guardar_prospecto", type="primary", width='stretch'):
        if asesor and prospecto and accion:
            nuevo_id = generar_id()
            nuevo_prospecto = {
                'prospecto_id': nuevo_id,
                'asesor': asesor.upper(),
                'fecha': fecha.strftime('%Y-%m-%d'),
                'prospecto': prospecto.upper(),
                'tipo': tipo,
                'accion': accion.upper()
            }
            if save_data(nuevo_prospecto):
                st.success(":material/check_circle: Prospecto agregado exitosamente!")
                time.sleep(1)
                st.rerun()
        else:
            st.error(":material/warning: Por favor completa los campos obligatorios (*)")

st.markdown("---")

# Mostrar tabla de prospectos
st.markdown("#### :material/list: Lista de Prospectos")

data = load_data()

if len(data) > 0:
    # Búsqueda
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("")
    with col2:
        search_query = st.text_input(":material/search: Buscar", value=st.session_state.search_query_prospeccion, 
                                     placeholder="Buscar por nombre, empresa, asesor...",
                                     key="search_input_prospeccion")
        st.session_state.search_query_prospeccion = search_query
    
    # Filtrar datos según búsqueda
    if search_query:
        mask = data.astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)
        filtered_data = data[mask]
    else:
        filtered_data = data
    
    # Función para convertir DataFrame a Excel
    def to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Seleccionar solo las columnas relevantes para exportar
            export_df = df[['prospecto_id', 'fecha', 'asesor', 'prospecto', 'tipo', 'accion']].copy()
            export_df.columns = ['ID', 'Fecha', 'Asesor', 'Prospecto', 'Tipo', 'Acción']
            # Convertir columnas de texto a mayúsculas
            text_columns = ['ID', 'Asesor', 'Prospecto', 'Tipo', 'Acción']
            for col in text_columns:
                export_df[col] = export_df[col].astype(str).str.upper()
            export_df.to_excel(writer, index=False, sheet_name='Prospección')
        return output.getvalue()
    
    # Botón de descarga
    col1, col2 = st.columns([5, 1])
    with col2:
        excel_data = to_excel(filtered_data)
        st.download_button(
            label=":material/download: Descargar Excel",
            data=excel_data,
            file_name=f"prospeccion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    st.markdown("")
    
    # Paginación
    items_per_page = 10
    total_items = len(filtered_data)
    total_pages = math.ceil(total_items / items_per_page)
    
    if st.session_state.page_prospeccion >= total_pages:
        st.session_state.page_prospeccion = max(0, total_pages - 1)
    
    start_idx = st.session_state.page_prospeccion * items_per_page
    end_idx = min(start_idx + items_per_page, total_items)
    page_data = filtered_data.iloc[start_idx:end_idx]
    
    # Mostrar tabla con acciones
    if len(page_data) > 0:
        # Encabezados
        header_cols = st.columns([1, 1.5, 2, 1.5, 2.5, 0.7, 0.7])
        headers = ['Fecha', 'Asesor', 'Prospecto', 'Tipo', 'Acción', '', '']
        for idx, (col, header) in enumerate(zip(header_cols, headers)):
            with col:
                if header:
                    st.markdown(f"**{header}**")
        
        st.markdown("---")
        
        for idx, row in page_data.iterrows():
            cols = st.columns([1, 1.5, 2, 1.5, 2.5, 0.7, 0.7])
            
            with cols[0]:
                st.text(row.get('fecha', ''))
            with cols[1]:
                st.text(str(row.get('asesor', '')).upper())
            with cols[2]:
                st.text(str(row.get('prospecto', '')).upper())
            with cols[3]:
                st.text(str(row.get('tipo', '')).upper())
            with cols[4]:
                accion = str(row.get('accion', '')).upper()
                st.text(accion[:35] + '...' if len(accion) > 35 else accion)
            with cols[5]:
                if st.button(":material/edit:", key=f"edit_prosp_{idx}", help="Editar", width='stretch'):
                    edit_dialog(idx)
            with cols[6]:
                if st.button(":material/delete:", key=f"delete_prosp_{idx}", help="Eliminar", width='stretch'):
                    confirm_delete(idx)
        
        # Controles de paginación
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.button(":material/arrow_back: Anterior", disabled=(st.session_state.page_prospeccion == 0), key="prev_prosp"):
                st.session_state.page_prospeccion -= 1
                st.rerun()
        
        with col2:
            st.markdown(f"<center>Página {st.session_state.page_prospeccion + 1} de {total_pages} ({total_items} registros)</center>", 
                       unsafe_allow_html=True)
        
        with col3:
            if st.button("Siguiente :material/arrow_forward:", disabled=(st.session_state.page_prospeccion >= total_pages - 1), key="next_prosp"):
                st.session_state.page_prospeccion += 1
                st.rerun()
    else:
        st.info("No se encontraron resultados para la búsqueda.")
else:
    st.info(":material/note: No hay prospectos registrados. Agrega tu primer prospecto usando el formulario de arriba.")
