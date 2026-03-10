import streamlit as st
from styles.tablejs import estilo_tabla_js
from utils.supabase_client import get_supabase_client
import pandas as pd
from datetime import datetime, date
import math
import random
import time
from io import BytesIO

from utils.opciones import ASESORES

st.set_page_config(page_title="Prospección", page_icon="🎯", layout="wide")

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

client = get_supabase_client()

# ── SESSION STATE ─────────────────────────────────────
if 'page_prospeccion' not in st.session_state:
    st.session_state.page_prospeccion = 0
if 'search_query_prospeccion' not in st.session_state:
    st.session_state.search_query_prospeccion = ""
if 'show_edit_dialog_prospeccion' not in st.session_state:
    st.session_state.show_edit_dialog_prospeccion = False
if 'edit_index_prospeccion' not in st.session_state:
    st.session_state.edit_index_prospeccion = None
if 'sort_column_prospeccion' not in st.session_state:
    st.session_state.sort_column_prospeccion = 'fecha'
if 'sort_ascending_prospeccion' not in st.session_state:
    st.session_state.sort_ascending_prospeccion = False
if 'last_search_prospeccion' not in st.session_state:
    st.session_state.last_search_prospeccion = ""

ITEMS_PER_PAGE = 15

# ── DATA ──────────────────────────────────────────────
@st.cache_data(ttl=5)
def load_data():
    try:
        response = client.select("prospeccion").execute()
        if response.data:
            data = pd.DataFrame(response.data)
            data = data.rename(columns={
                'prospecto_id': 'ID DE PROSPECTO',
                'asesor':       'ASESOR',
                'fecha':        'FECHA',
                'prospecto':    'PROSPECTO',
                'tipo':         'TIPO',
                'accion':       'ACCIÓN',
            })
            return data
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error al cargar datos: {str(e)}")
        return pd.DataFrame()

def save_data(row_data, row_id=None):
    try:
        if row_id:
            client.update("prospeccion", row_data, {"id": row_id})
        else:
            client.insert("prospeccion", row_data)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Error al guardar datos: {str(e)}")
        return False

def delete_data(row_id):
    try:
        client.delete("prospeccion", {"id": row_id})
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
    st.warning("¿Estás seguro de que deseas eliminar este prospecto?")
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

@st.dialog(":material/edit: Editar Prospecto")
def edit_dialog(idx):
    data = load_data()
    if idx not in data.index:
        st.error("Registro no encontrado")
        return

    row = data.loc[idx]
    st.info(f"**ID:** {row.get('ID DE PROSPECTO', '')}")

    with st.form("form_editar_prospecto"):
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
            tipo_options = ["VENTA", "RENTA"]
            tipo_edit = st.selectbox(
                "Tipo", tipo_options,
                index=tipo_options.index(row.get('TIPO', 'VENTA')) if row.get('TIPO', 'VENTA') in tipo_options else 0
            )

        with col3:
            accion_edit = st.text_area("Acción *", value=row.get('ACCIÓN', '')).upper()

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            guardar = st.form_submit_button(":material/save: Guardar Cambios", use_container_width=True)
        with col_btn2:
            cancelar = st.form_submit_button(":material/cancel: Cancelar", use_container_width=True)

        if guardar:
            if asesor_edit and prospecto_edit and accion_edit:
                row_id = row.get('id', '')
                updated_data = {
                    'prospecto_id': row.get('ID DE PROSPECTO', ''),
                    'asesor':       asesor_edit.upper(),
                    'fecha':        fecha_edit.strftime('%Y-%m-%d'),
                    'prospecto':    prospecto_edit.upper(),
                    'tipo':         tipo_edit,
                    'accion':       accion_edit.upper(),
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

# ── FORMULARIO NUEVO PROSPECTO ────────────────────────
st.markdown("#### :material/add: Agregar Nuevo Prospecto")

with st.container():
    col1, col2, col3 = st.columns(3)

    with col1:
        asesor = st.selectbox("Asesor *", ASESORES, key="asesor_prospecto").upper()
        fecha = st.date_input("Fecha *", value=date.today(), key="fecha_prospecto")

    with col2:
        prospecto = st.text_input("Prospecto *", key="nombre_prospecto").upper()
        tipo = st.selectbox("Tipo", ["VENTA", "RENTA"], key="tipo_prospecto")

    with col3:
        accion = st.text_area("Acción *", key="accion_prospecto").upper()

    if st.button(":material/save: Guardar Prospecto", key="guardar_prospecto", type="primary", use_container_width=True):
        if asesor and prospecto and accion:
            nuevo_id = generar_id()
            nuevo_prospecto = {
                'prospecto_id': nuevo_id,
                'asesor':       asesor.upper(),
                'fecha':        fecha.strftime('%Y-%m-%d'),
                'prospecto':    prospecto.upper(),
                'tipo':         tipo,
                'accion':       accion.upper(),
            }
            if save_data(nuevo_prospecto):
                st.success(":material/check_circle: Prospecto agregado exitosamente!")
                time.sleep(1)
                st.rerun()
        else:
            st.error(":material/warning: Por favor completa los campos obligatorios (*)")

st.markdown("---")

# ── TABLA ─────────────────────────────────────────────
st.markdown("#### :material/list: Lista de Prospectos")

def generar_tabla(data, btnedit=None, btndelete=None):
    columnas_visibles = [col for col in data.columns if col not in ['id', 'ID DE PROSPECTO', 'created_at', 'updated_at']]
    tabla_html = '<table class="responsive-table">\n<thead>\n<tr>\n'

    for col in columnas_visibles:
        tabla_html += f'    <th>{col}</th>\n'
    tabla_html += '    <th>Acción</th>\n</tr>\n</thead>\n<tbody>\n'

    for index, row in data.iterrows():
        tabla_html += '    <tr>\n'

        for col in columnas_visibles:
            if col == 'TIPO':
                badge_color = "#2196F3" if row.get('TIPO', '') == 'VENTA' else "#9C27B0"
                tabla_html += f'    <td><span style="background-color:{badge_color}; color:white; padding:5px 8px; border-radius:4px; font-size:11px; white-space:nowrap;">{row.get(col, "")}</span></td>\n'
            else:
                tabla_html += f'    <td>{row.get(col, "")}</td>\n'

        acciones = '    <td>'
        if btnedit:
            acciones += f'<a data-link="edit_{row["ID DE PROSPECTO"]}" class="btn-floating waves-effect waves-light btn"><i class="material-icons">edit</i></a> '
        if btndelete:
            acciones += f'<a data-link="delete_{row["ID DE PROSPECTO"]}" class="btn-floating waves-effect waves-light btn red"><i class="material-icons">delete</i></a>'
        acciones += '</td>\n'
        tabla_html += acciones
        tabla_html += '    </tr>\n'

    tabla_html += '</tbody>\n</table>'
    return tabla_html

def to_excel(data):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        export_cols = ['ID DE PROSPECTO', 'ASESOR', 'FECHA', 'PROSPECTO', 'TIPO', 'ACCIÓN']
        available_cols = [c for c in export_cols if c in data.columns]
        export_df = data[available_cols].copy()
        export_df.columns = ['ID', 'Asesor', 'Fecha', 'Prospecto', 'Tipo', 'Acción'][:len(available_cols)]
        for col in ['ID', 'Asesor', 'Prospecto', 'Tipo', 'Acción']:
            if col in export_df.columns:
                export_df[col] = export_df[col].astype(str).str.upper()
        export_df.to_excel(writer, index=False, sheet_name='Prospección')
    return output.getvalue()

styles = """
<link href="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css" rel="stylesheet">
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
"""
st.write(styles, unsafe_allow_html=True)

JS = estilo_tabla_js()

material_table = st.components.v2.component(
    name="material_table_prospeccion",
    js=JS,
    isolate_styles=False,
)

data = load_data()

if not data.empty:
    # ── BÚSQUEDA ──────────────────────────────────────
    busqueda = st.text_input(
        ":material/search: Buscar",
        placeholder="Buscar por prospecto, asesor, tipo...",
        key="search_input_prospeccion"
    )

    if busqueda != st.session_state.last_search_prospeccion:
        st.session_state.page_prospeccion = 0
        st.session_state.last_search_prospeccion = busqueda

    if busqueda:
        data_filtrada = data[
            data['PROSPECTO'].str.contains(busqueda, case=False, na=False) |
            data['ASESOR'].str.contains(busqueda, case=False, na=False) |
            data['FECHA'].astype(str).str.contains(busqueda, case=False, na=False) |
            data['TIPO'].str.contains(busqueda, case=False, na=False) |
            data['ACCIÓN'].str.contains(busqueda, case=False, na=False)
        ]
    else:
        data_filtrada = data

    data_filtrada = data_filtrada.copy()
    data_filtrada['FECHA'] = data_filtrada['FECHA'].fillna("")

    # ── PAGINACIÓN ────────────────────────────────────
    total_items = len(data_filtrada)
    total_pages = max(1, math.ceil(total_items / ITEMS_PER_PAGE))

    if st.session_state.page_prospeccion >= total_pages:
        st.session_state.page_prospeccion = total_pages - 1

    start_idx = st.session_state.page_prospeccion * ITEMS_PER_PAGE
    end_idx = min(start_idx + ITEMS_PER_PAGE, total_items)
    data_pagina = data_filtrada.iloc[start_idx:end_idx]

    # ── RENDER TABLA ──────────────────────────────────
    paragraph_html = generar_tabla(data_pagina, btnedit=True, btndelete=True)

    resultado = material_table(
        data=paragraph_html,
        on_clicked_change=lambda: None,
        key=f"table_prospeccion_{st.session_state.page_prospeccion}_{busqueda}"
    )

    # ── CONTROLES DE PAGINACIÓN ───────────────────────
    st.markdown("")
    col_prev, col_info, col_next = st.columns([1, 3, 1])

    with col_prev:
        if st.button(
            ":material/arrow_back: Anterior",
            disabled=(st.session_state.page_prospeccion == 0),
            use_container_width=True,
            key="btn_prev_prosp"
        ):
            st.session_state.page_prospeccion -= 1
            st.rerun()

    with col_info:
        st.markdown(
            f"<div style='text-align:center; padding-top:8px; color:#666;'>"
            f"Página <b>{st.session_state.page_prospeccion + 1}</b> de <b>{total_pages}</b>"
            f"&nbsp;·&nbsp; {total_items} registros"
            f"</div>",
            unsafe_allow_html=True
        )

    with col_next:
        if st.button(
            "Siguiente :material/arrow_forward:",
            disabled=(st.session_state.page_prospeccion >= total_pages - 1),
            use_container_width=True,
            key="btn_next_prosp"
        ):
            st.session_state.page_prospeccion += 1
            st.rerun()

    excel_data = to_excel(data_filtrada)
    st.download_button(
        label=":material/download: Descargar Excel",
        data=excel_data,
        file_name=f"prospeccion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        width='stretch'
    )

    # ── MANEJAR CLICKS DE BOTONES ─────────────────────
    if resultado and resultado.get("clicked"):
        clicked = resultado["clicked"]

        if clicked.startswith("edit_"):
            prospecto_id = clicked.replace("edit_", "")
            match = data[data['ID DE PROSPECTO'] == prospecto_id]
            if not match.empty:
                edit_dialog(match.index[0])

        elif clicked.startswith("delete_"):
            prospecto_id = clicked.replace("delete_", "")
            match = data[data['ID DE PROSPECTO'] == prospecto_id]
            if not match.empty:
                confirm_delete(match.index[0])

else:
    st.info(":material/note: No hay prospectos registrados. Agrega tu primer prospecto usando el formulario de arriba.")
