import streamlit as st
from utils.supabase_client import get_supabase_client
import pandas as pd
from datetime import datetime, date
import math
import random
import time
from io import BytesIO

from utils.opciones import ASESORES

st.set_page_config(page_title="Proyectos/Cotizaciones", page_icon="📂", layout="wide")

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

st.title(":material/folder: Gestión de Proyectos/Cotizaciones")

# Conexión a Supabase
client = get_supabase_client()

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
# Nuevos estados para ordenamiento
if 'sort_column_proyectos' not in st.session_state:
    st.session_state.sort_column_proyectos = 'fecha_cotizacion'
if 'sort_ascending_proyectos' not in st.session_state:
    st.session_state.sort_ascending_proyectos = False

# Cargar datos
@st.cache_data(ttl=5)
def load_data():
    try:
        response = client.select("proyectos").execute()
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
            client.update("proyectos", row_data, {"id": row_id})
        else:
            # Insertar nuevo registro
            client.insert("proyectos", row_data)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Error al guardar datos: {str(e)}")
        return False

def delete_data(row_id):
    """Elimina un registro de Supabase"""
    try:
        client.delete("proyectos", {"id": row_id})
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
    st.warning(f"¿Estás seguro de que deseas eliminar este proyecto?")
    
    st.info(f"**Proyecto:** {row.get('proyecto', '')}\n\n**Cliente:** {row.get('cliente', '')}\n\n**Asesor:** {row.get('asesor', '')}")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button(":material/delete: Sí, Eliminar", use_container_width=True, type="primary"):
            # Obtener el ID de la base de datos
            row_id = row.get('id', '')
            if row_id and delete_data(row_id):
                st.success(":material/check_circle: Registro eliminado exitosamente")
                time.sleep(1)
                st.rerun()
    with col2:
        if st.button(":material/cancel: Cancelar", use_container_width=True):
            st.rerun()

@st.dialog(":material/edit: Editar Proyecto")
def edit_dialog(idx):
    data = load_data()
    if idx not in data.index:
        st.error("Registro no encontrado")
        return
    
    row = data.loc[idx]
    
    # Mostrar ID (no editable)
    st.info(f"**ID:** {row.get('proyecto_id', '')}")
    
    # Status fuera del formulario para permitir interactividad
    status_options = ["Perdido", "Ganado", "En Proceso"]
    status_actual = row.get('status', 'En Proceso')
    status_index = status_options.index(status_actual) if status_actual in status_options else 2
    
    status_edit = st.selectbox("Status", status_options, index=status_index, key=f"status_edit_{idx}")
    
    with st.form("form_editar_proyecto"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            asesor_edit = st.selectbox("Selecciona un asesor de ventas", ASESORES, 
                                       index=ASESORES.index(row.get('asesor', '')) if row.get('asesor', '') in ASESORES else None)
            cotizacion_edit = st.text_input("No. de Cotización", value=row.get('cotizacion', ''))
            # Fecha de cotización
            fecha_cot_value = row.get('fecha_cotizacion', None)
            if fecha_cot_value and isinstance(fecha_cot_value, str):
                try:
                    fecha_cot_value = datetime.strptime(fecha_cot_value, '%Y-%m-%d').date()
                except:
                    fecha_cot_value = None
            fecha_cotizacion_edit = st.date_input("Fecha de Cotización", value=fecha_cot_value, key=f"fecha_edit_{idx}")
        
        with col2:
            proyecto_edit = st.text_input("Proyecto *", value=row.get('proyecto', ''))
            cliente_edit = st.text_input("Cliente *", value=row.get('cliente', ''))
        
        with col3:
            # Mostrar motivo solo si status es Perdido
            motivo_perdida_edit = ""
            if status_edit == "Perdido":
                motivo_opciones = ["Precio", "Stock/Inventario", "Otro"]
                motivo_actual = row.get('motivo_perdida', '')
                motivo_index = motivo_opciones.index(motivo_actual) if motivo_actual in motivo_opciones else 0
                motivo_perdida_edit = st.selectbox("Motivo de Pérdida *", motivo_opciones, index=motivo_index)
            
            total_edit = st.number_input("Total ($) *", min_value=0.0, step=0.01, 
                                        value=float(row.get('total', 0)))
        
        observaciones_edit = st.text_area("Observaciones", value=row.get('observaciones', ''))
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            guardar = st.form_submit_button(":material/save: Guardar Cambios", use_container_width=True)
        with col_btn2:
            cancelar = st.form_submit_button(":material/cancel: Cancelar", use_container_width=True)
        
        if guardar:
            if asesor_edit and proyecto_edit and cliente_edit:
                # Validar motivo si es Perdido
                if status_edit == "Perdido" and not motivo_perdida_edit:
                    st.error(":material/warning: Por favor selecciona el motivo de pérdida")
                else:
                    row_id = row.get('id', '')
                    updated_data = {
                        'proyecto_id': row.get('proyecto_id', ''),
                        'asesor': asesor_edit,
                        'cotizacion': cotizacion_edit,
                        'fecha_cotizacion': fecha_cotizacion_edit.isoformat() if fecha_cotizacion_edit else None,
                        'proyecto': proyecto_edit,
                        'cliente': cliente_edit,
                        'status': status_edit,
                        'total': total_edit,
                        'motivo_perdida': motivo_perdida_edit if status_edit == "Perdido" else "",
                        'observaciones': observaciones_edit
                    }
                    if save_data(updated_data, row_id):
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
st.markdown("#### :material/add: Agregar Nuevo Proyecto/Cotización")

# Contenedor visual que simula un formulario pero permite interactividad
with st.container():
    col1, col2, col3 = st.columns(3)
    
    with col1:
        asesor = st.selectbox("Selecciona un asesor de ventas", ASESORES, key="asesor_nuevo").title()
        cotizacion = st.text_input("No. de Cotización", key="cotizacion_nueva")
        fecha_cotizacion = st.date_input("Fecha de Cotización", value=None, key="fecha_cotizacion_nueva")
    
    with col2:
        proyecto = st.text_input("Proyecto/Cotización *", key="proyecto_nuevo")
        cliente = st.text_input("Cliente *", key="cliente_nuevo")
    
    with col3:
        status = st.selectbox("Status *", ["Perdido", "Ganado", "En Proceso"], index=2, key="status_nuevo")
        
        # Mostrar motivo de pérdida solo si status es "Perdido"
        motivo_perdida = ""
        if status == "Perdido":
            motivo_perdida = st.selectbox("Motivo de Pérdida *", ["Precio", "Stock/Inventario", "Otro"], key="motivo_nuevo")
        
        total = st.number_input("Total ($) *", min_value=0.0, step=0.01, key="total_nuevo")
    
    observaciones = st.text_area("Observaciones", key="observaciones_nueva")
    
    if st.button(":material/save: Guardar Proyecto/Cotización", key="guardar_proyecto", type="primary", use_container_width=True):
        if asesor and proyecto and cliente:
            # Validar que si es Perdido, tenga motivo
            if status == "Perdido" and not motivo_perdida:
                st.error(":material/warning: Por favor selecciona el motivo de pérdida")
            else:
                nuevo_id = generar_id()
                nuevo_proyecto = {
                    'proyecto_id': nuevo_id,
                    'asesor': asesor,
                    'cotizacion': cotizacion,
                    'fecha_cotizacion': fecha_cotizacion.isoformat() if fecha_cotizacion else None,
                    'proyecto': proyecto,
                    'cliente': cliente,
                    'status': status,
                    'total': total,
                    'motivo_perdida': motivo_perdida if status == "Perdido" else "",
                    'observaciones': observaciones.capitalize() if observaciones else ""
                }
                if save_data(nuevo_proyecto):
                    st.success(":material/check_circle: Proyecto agregado exitosamente!")
                    time.sleep(1)
                    st.rerun()
        else:
            st.error(":material/warning: Por favor completa los campos obligatorios (*)")

st.markdown("---")

# Mostrar tabla de proyectos
st.markdown("#### :material/list: Lista de Proyectos/Cotizaciones")

data = load_data()

if len(data) > 0:
    # Búsqueda
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown("")
    with col2:
        search_query = st.text_input(":material/search: Buscar", value=st.session_state.search_query_proyectos, 
                                     placeholder="Buscar por proyecto, cliente, asesor...",
                                     key="search_input_proyectos")
        st.session_state.search_query_proyectos = search_query
    
    # Filtrar datos según búsqueda
    if search_query:
        mask = data.astype(str).apply(lambda x: x.str.contains(search_query, case=False, na=False)).any(axis=1)
        filtered_data = data[mask]
    else:
        filtered_data = data
    
    # Aplicar ordenamiento
    if st.session_state.sort_column_proyectos in filtered_data.columns:
        # Convertir fecha a datetime si es la columna de ordenamiento
        if st.session_state.sort_column_proyectos == 'fecha_cotizacion':
            filtered_data = filtered_data.copy()
            filtered_data['fecha_cotizacion'] = pd.to_datetime(filtered_data['fecha_cotizacion'])
        
        filtered_data = filtered_data.sort_values(
            by=st.session_state.sort_column_proyectos,
            ascending=st.session_state.sort_ascending_proyectos
        )
    
    # Función para convertir DataFrame a Excel
    def to_excel(df):
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Seleccionar solo las columnas relevantes para exportar
            export_df = df[['proyecto_id', 'asesor', 'cotizacion', 'fecha_cotizacion', 'proyecto', 'cliente', 'status', 'total', 'motivo_perdida', 'observaciones']].copy()
            export_df.columns = ['ID', 'Asesor', 'No. Cotización', 'Fecha Cotización', 'Proyecto', 'Cliente', 'Status', 'Total', 'Motivo Pérdida', 'Observaciones']
            # Convertir columnas de texto a mayúsculas
            text_columns = ['ID', 'Asesor', 'No. Cotización', 'Proyecto', 'Cliente', 'Status', 'Motivo Pérdida', 'Observaciones']
            for col in text_columns:
                export_df[col] = export_df[col].astype(str).str.upper()
            export_df.to_excel(writer, index=False, sheet_name='Proyectos')
        return output.getvalue()
    
    # Botón de descarga
    col1, col2 = st.columns([5, 1])
    with col2:
        excel_data = to_excel(filtered_data)
        st.download_button(
            label=":material/download: Descargar Excel",
            data=excel_data,
            file_name=f"proyectos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    
    st.markdown("")
    
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
        # Función para cambiar el ordenamiento
        def toggle_sort(column):
            if st.session_state.sort_column_proyectos == column:
                st.session_state.sort_ascending_proyectos = not st.session_state.sort_ascending_proyectos
            else:
                st.session_state.sort_column_proyectos = column
                st.session_state.sort_ascending_proyectos = True
            st.session_state.page_proyectos = 0  # Resetear a la primera página
        
        # Encabezados con botones de ordenamiento
        header_cols = st.columns([1, 2, 0.8, 1.5, 1.2, 1, 1.5, 0.7, 0.7])
        headers = [
            ('asesor', 'Asesor'),
            ('proyecto', 'Proyecto/Cotización'),
            ('cotizacion', 'Cot.'),
            ('cliente', 'Cliente'),
            ('status', 'Status'),
            ('fecha_cotizacion', 'Fecha'),
            ('total', 'Total'),
            ('', ''),
            ('', '')
        ]
        
        for idx, (col, (col_name, header)) in enumerate(zip(header_cols, headers)):
            with col:
                if header and col_name:
                    # Determinar el ícono de ordenamiento
                    if st.session_state.sort_column_proyectos == col_name:
                        icon = ":material/arrow_upward:" if st.session_state.sort_ascending_proyectos else ":material/arrow_downward:"
                    else:
                        icon = ":material/unfold_more:"
                    
                    if st.button(f"{header} {icon}", key=f"sort_{col_name}", use_container_width=True):
                        toggle_sort(col_name)
                        st.rerun()
        
        st.markdown("---")
        
        for idx, row in page_data.iterrows():
            cols = st.columns([1, 2, 0.8, 1.5, 1.2, 1, 1.5, 0.7, 0.7])
            
            with cols[0]:
                if row.get('asesor', '') == "CARLOS ORTIZ":
                    st.text("CARLOS ORTIZ")
                elif row.get('asesor', '') == "HUGO ENRIQUE PÉREZ RAMÍREZ":
                    st.text("HUGO PÉREZ")
                elif row.get('asesor', '') == "JOSÉ ALVARO MARTÍNEZ ESPEJEL":
                    st.text("ALVARO MARTÍNEZ")
                elif row.get('asesor', '') == "MAURICIO GUTIÉRREZ PÉREZ PALMA":
                    st.text("MAURICIO GUTIÉRREZ")
                else:
                    st.text(str(row.get('asesor', '')).upper())
            with cols[1]:
                proyecto = str(row.get('proyecto', '')).upper()
                st.text(proyecto[:25] + '...' if len(proyecto) > 25 else proyecto)
            with cols[2]:
                st.text(row.get('cotizacion', ''))
            with cols[3]:
                st.text(str(row.get('cliente', '')).upper())
            with cols[4]:
                status = row.get('status', '').title()
                color_map = {
                    'Vendido': '#4ac783',
                    'Ganado': '#4ac783',
                    'Perdido': '#ff715a',
                    'En Proceso': '#fdc400'
                }
                bg_color = color_map.get(status, "#007fd6")
                st.markdown(f'<div style="background-color: {bg_color}; color: white; padding: 4px 8px; border-radius: 4px; text-align: center; font-size: 12px;">{status}</div>', unsafe_allow_html=True)
            with cols[5]:
                fecha_display = row.get('fecha_cotizacion', '')
                if isinstance(fecha_display, pd.Timestamp):
                    fecha_display = fecha_display.strftime('%Y-%m-%d')
                st.text(fecha_display)
            with cols[6]:
                total_val = row.get('total', 0)
                st.text(f"${total_val:,.2f}" if pd.notna(total_val) else "$0.00")
            with cols[7]:
                if st.button(":material/edit:", key=f"edit_proy_{idx}", help="Editar", use_container_width=True):
                    edit_dialog(idx)
            with cols[8]:
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
