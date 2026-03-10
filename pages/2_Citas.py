import streamlit as st
from styles.tablejs import estilo_tabla_js
from utils.opciones import ASESORES
from utils.supabase_client import get_supabase_client
import pandas as pd
from datetime import datetime, date
import math
import random
import time
from io import BytesIO

st.set_page_config(page_title="Citas", page_icon=":material/calendar_today:", layout="wide")

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

client = get_supabase_client()

# ── SESSION STATE ─────────────────────────────────────
if 'page_citas' not in st.session_state:
    st.session_state.page_citas = 0
if 'search_query_citas' not in st.session_state:
    st.session_state.search_query_citas = ""
if 'show_edit_dialog_citas' not in st.session_state:
    st.session_state.show_edit_dialog_citas = False
if 'edit_index_citas' not in st.session_state:
    st.session_state.edit_index_citas = None
if 'sort_column_citas' not in st.session_state:
    st.session_state.sort_column_citas = 'fecha'
if 'sort_ascending_citas' not in st.session_state:
    st.session_state.sort_ascending_citas = False
if 'last_search_citas' not in st.session_state:
    st.session_state.last_search_citas = ""

ITEMS_PER_PAGE = 15

# ── DATA ──────────────────────────────────────────────
@st.cache_data(ttl=5)
def load_data():
    try:
        response = client.select("citas").execute()
        if response.data:
            data = pd.DataFrame(response.data)
            data = data.rename(columns={
                'cita_id':         'ID DE CITA',
                'asesor':          'ASESOR',
                'fecha':           'FECHA',
                'prospecto':       'PROSPECTO',
                'giro':            'GIRO',
                'accion_seguir':   'ACCIÓN A SEGUIR',
                'ultimo_contacto': 'ÚLTIMO CONTACTO',
            })
            return data
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error al cargar datos: {str(e)}")
        return pd.DataFrame()

def save_data(row_data, row_id=None):
    try:
        if row_id:
            client.update("citas", row_data, {"id": row_id})
        else:
            client.insert("citas", row_data)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Error al guardar datos: {str(e)}")
        return False

def delete_data(row_id):
    try:
        client.delete("citas", {"id": row_id})
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Error al eliminar datos: {str(e)}")
        return False

def generar_id():
    numero = random.randint(1000000000000, 9999999999999)
    return f"ID-{numero}"

# ── DIALOGS ───────────────────────────────────────────
@st.dialog(":material/warning: Confirmar Eliminación")
def confirm_delete(idx):
    data = load_data()
    if idx not in data.index:
        st.error("Registro no encontrado")
        return

    row = data.loc[idx]
    st.warning("¿Estás seguro de que deseas eliminar esta cita?")
    st.info(f"**Prospecto:** {row.get('PROSPECTO', '')}\n\n**Asesor:** {row.get('ASESOR', '')}\n\n**Fecha:** {row.get('FECHA', '')}")

    col1, col2 = st.columns(2)
    with col1:
        if st.button(":material/delete: Sí, Eliminar", use_container_width=True, type="primary"):
            row_id = row.get('id', '')
            if row_id and delete_data(row_id):
                st.success(":material/check_circle: Registro eliminado exitosamente")
                time.sleep(1)
                st.rerun()
    with col2:
        if st.button(":material/cancel: Cancelar", use_container_width=True):
            st.rerun()

@st.dialog(":material/edit: Editar Cita")
def edit_dialog(idx):
    data = load_data()
    if idx not in data.index:
        st.error("Registro no encontrado")
        return

    row = data.loc[idx]
    st.info(f"**ID:** {row.get('ID DE CITA', '')}")

    with st.form("form_editar_cita"):
        col1, col2, col3 = st.columns(3)

        with col1:
            asesor_edit = st.selectbox(
                "Asesor *", ASESORES,
                index=ASESORES.index(row.get('ASESOR', '').upper()) if row.get('ASESOR', '').upper() in ASESORES else 0
            ).upper()
            try:
                fecha_edit = st.date_input("Fecha *", value=pd.to_datetime(row.get('FECHA', date.today())))
            except:
                fecha_edit = st.date_input("Fecha *", value=date.today())

        with col2:
            prospecto_edit = st.text_input("Prospecto *", value=row.get('PROSPECTO', '')).upper()
            giro_edit = st.text_input("Giro", value=row.get('GIRO', '')).upper()

        with col3:
            accion_seguir_edit = st.text_area("Acción a Seguir", value=row.get('ACCIÓN A SEGUIR', '')).upper()
            try:
                ultimo_contacto_edit = st.date_input(
                    "Último Contacto",
                    value=pd.to_datetime(row.get('ÚLTIMO CONTACTO', date.today()))
                )
            except:
                ultimo_contacto_edit = st.date_input("Último Contacto", value=date.today())

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            guardar = st.form_submit_button(":material/save: Guardar Cambios", use_container_width=True)
        with col_btn2:
            cancelar = st.form_submit_button(":material/cancel: Cancelar", use_container_width=True)

        if guardar:
            if asesor_edit and prospecto_edit:
                row_id = row.get('id', '')
                updated_data = {
                    'cita_id':         row.get('ID DE CITA', ''),
                    'asesor':          asesor_edit.upper(),
                    'fecha':           fecha_edit.strftime('%Y-%m-%d'),
                    'prospecto':       prospecto_edit.upper(),
                    'giro':            giro_edit.upper(),
                    'accion_seguir':   accion_seguir_edit.upper(),
                    'ultimo_contacto': ultimo_contacto_edit.strftime('%Y-%m-%d'),
                }
                if save_data(updated_data, row_id):
                    st.success(":material/check_circle: Cita actualizada exitosamente!")
                    st.session_state.show_edit_dialog_citas = False
                    st.session_state.edit_index_citas = None
                    st.rerun()
            else:
                st.error(":material/warning: Por favor completa los campos obligatorios (*)")

        if cancelar:
            st.session_state.show_edit_dialog_citas = False
            st.session_state.edit_index_citas = None
            st.rerun()

# ── FORMULARIO NUEVA CITA ─────────────────────────────
st.markdown("#### :material/add: Agregar Nueva Cita")

with st.container():
    col1, col2, col3 = st.columns(3)

    with col1:
        asesor = st.selectbox("Selecciona un asesor de ventas", ASESORES, key="asesor_cita").upper()
        fecha_cita = st.date_input("Fecha *", value=date.today(), key="fecha_cita")

    with col2:
        prospecto = st.text_input("Nombre de tu prospecto *", key="prospecto_cita").upper()
        giro = st.text_input("Giro de negocio", key="giro_cita").upper()

    with col3:
        accion_seguir = st.text_area("Acción a Seguir", key="accion_cita").upper()
        ultimo_contacto = st.date_input("Último Contacto", value=date.today(), key="ultimo_contacto_cita")

    if st.button(":material/save: Guardar Cita", key="guardar_cita", type="primary", use_container_width=True):
        if asesor and prospecto:
            nuevo_id = generar_id()
            nueva_cita = {
                'cita_id':         nuevo_id,
                'asesor':          asesor.upper(),
                'fecha':           fecha_cita.strftime('%Y-%m-%d'),
                'prospecto':       prospecto.upper(),
                'giro':            giro.upper(),
                'accion_seguir':   accion_seguir.upper(),
                'ultimo_contacto': ultimo_contacto.strftime('%Y-%m-%d'),
            }
            if save_data(nueva_cita):
                st.success(":material/check_circle: Cita agregada exitosamente!")
                time.sleep(1)
                st.rerun()
        else:
            st.error(":material/warning: Por favor completa los campos obligatorios (*)")

st.markdown("---")

# ── TABLA ─────────────────────────────────────────────
st.markdown("#### :material/list: Lista de Citas")

def generar_tabla(data, btnedit=None, btndelete=None):
    columnas_visibles = [col for col in data.columns if col not in ['id', 'ID DE CITA', 'created_at', 'updated_at']]
    tabla_html = '<table class="responsive-table">\n<thead>\n<tr>\n'

    for col in columnas_visibles:
        tabla_html += f'    <th>{col}</th>\n'
    tabla_html += '    <th>Acción</th>\n</tr>\n</thead>\n<tbody>\n'

    for index, row in data.iterrows():
        tabla_html += '    <tr>\n'

        for col in columnas_visibles:
            tabla_html += f'    <td>{row.get(col, "")}</td>\n'

        acciones = '    <td>'
        if btnedit:
            acciones += f'<a data-link="edit_{row["ID DE CITA"]}" class="btn-floating waves-effect waves-light btn"><i class="material-icons">edit</i></a> '
        if btndelete:
            acciones += f'<a data-link="delete_{row["ID DE CITA"]}" class="btn-floating waves-effect waves-light btn red"><i class="material-icons">delete</i></a>'
        acciones += '</td>\n'
        tabla_html += acciones
        tabla_html += '    </tr>\n'

    tabla_html += '</tbody>\n</table>'
    return tabla_html

def to_excel(data):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        export_cols = ['ID DE CITA', 'ASESOR', 'FECHA', 'PROSPECTO', 'GIRO', 'ACCIÓN A SEGUIR', 'ÚLTIMO CONTACTO']
        available_cols = [c for c in export_cols if c in data.columns]
        export_df = data[available_cols].copy()
        export_df.columns = ['ID', 'Asesor', 'Fecha', 'Prospecto', 'Giro', 'Acción a Seguir', 'Último Contacto'][:len(available_cols)]
        for col in ['ID', 'Asesor', 'Prospecto', 'Giro', 'Acción a Seguir']:
            if col in export_df.columns:
                export_df[col] = export_df[col].astype(str).str.upper()
        export_df.to_excel(writer, index=False, sheet_name='Citas')
    return output.getvalue()

styles = """
<link href="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css" rel="stylesheet">
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
"""
st.write(styles, unsafe_allow_html=True)

JS = estilo_tabla_js()

material_table = st.components.v2.component(
    name="material_table_citas",
    js=JS,
    isolate_styles=False,
)

data = load_data()

if not data.empty:
    # ── BÚSQUEDA ──────────────────────────────────────
    busqueda = st.text_input(
        ":material/search: Buscar",
        placeholder="Buscar por prospecto, asesor, fecha...",
        key="search_input_citas"
    )

    if busqueda != st.session_state.last_search_citas:
        st.session_state.page_citas = 0
        st.session_state.last_search_citas = busqueda

    if busqueda:
        data_filtrada = data[
            data['PROSPECTO'].str.contains(busqueda, case=False, na=False) |
            data['ASESOR'].str.contains(busqueda, case=False, na=False) |
            data['FECHA'].astype(str).str.contains(busqueda, case=False, na=False) |
            data['GIRO'].str.contains(busqueda, case=False, na=False)
        ]
    else:
        data_filtrada = data

    data_filtrada = data_filtrada.copy()
    data_filtrada['FECHA'] = data_filtrada['FECHA'].fillna("")
    data_filtrada['ÚLTIMO CONTACTO'] = data_filtrada['ÚLTIMO CONTACTO'].fillna("")

    # ── PAGINACIÓN ────────────────────────────────────
    total_items = len(data_filtrada)
    total_pages = max(1, math.ceil(total_items / ITEMS_PER_PAGE))

    if st.session_state.page_citas >= total_pages:
        st.session_state.page_citas = total_pages - 1

    start_idx = st.session_state.page_citas * ITEMS_PER_PAGE
    end_idx = min(start_idx + ITEMS_PER_PAGE, total_items)
    data_pagina = data_filtrada.iloc[start_idx:end_idx]

    # ── RENDER TABLA ──────────────────────────────────
    paragraph_html = generar_tabla(data_pagina, btnedit=True, btndelete=True)

    resultado = material_table(
        data=paragraph_html,
        on_clicked_change=lambda: None,
        key=f"table_citas_{st.session_state.page_citas}_{busqueda}"
    )

    # ── CONTROLES DE PAGINACIÓN ───────────────────────
    st.markdown("")
    col_prev, col_info, col_next = st.columns([1, 3, 1])

    with col_prev:
        if st.button(
            ":material/arrow_back: Anterior",
            disabled=(st.session_state.page_citas == 0),
            use_container_width=True,
            key="btn_prev_citas"
        ):
            st.session_state.page_citas -= 1
            st.rerun()

    with col_info:
        st.markdown(
            f"<div style='text-align:center; padding-top:8px; color:#666;'>"
            f"Página <b>{st.session_state.page_citas + 1}</b> de <b>{total_pages}</b>"
            f"&nbsp;·&nbsp; {total_items} registros"
            f"</div>",
            unsafe_allow_html=True
        )

    with col_next:
        if st.button(
            "Siguiente :material/arrow_forward:",
            disabled=(st.session_state.page_citas >= total_pages - 1),
            use_container_width=True,
            key="btn_next_citas"
        ):
            st.session_state.page_citas += 1
            st.rerun()

    excel_data = to_excel(data_filtrada)
    st.download_button(
        label=":material/download: Descargar Excel",
        data=excel_data,
        file_name=f"citas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        width='stretch'
    )

    # ── MANEJAR CLICKS DE BOTONES ─────────────────────
    if resultado and resultado.get("clicked"):
        clicked = resultado["clicked"]

        if clicked.startswith("edit_"):
            cita_id = clicked.replace("edit_", "")
            match = data[data['ID DE CITA'] == cita_id]
            if not match.empty:
                edit_dialog(match.index[0])

        elif clicked.startswith("delete_"):
            cita_id = clicked.replace("delete_", "")
            match = data[data['ID DE CITA'] == cita_id]
            if not match.empty:
                confirm_delete(match.index[0])

else:
    st.info(":material/note: No hay citas registradas. Agrega tu primera cita usando el formulario de arriba.")
