import streamlit as st
from styles.tablejs import estilo_tabla_js
from utils.supabase_client import get_supabase_client
import pandas as pd
from datetime import datetime, date
import math
import random
import time
from io import BytesIO
import requests
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import JsCode

from utils.opciones import ASESORES

st.set_page_config(page_title="Proyectos/Cotizaciones", page_icon=":material/folder:", layout="wide")

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

client = get_supabase_client()

# ── SESSION STATE ─────────────────────────────────────
if 'page_proyectos' not in st.session_state:
    st.session_state.page_proyectos = 0
if 'search_query_proyectos' not in st.session_state:
    st.session_state.search_query_proyectos = ""
if 'show_edit_dialog_proyectos' not in st.session_state:
    st.session_state.show_edit_dialog_proyectos = False
if 'edit_index_proyectos' not in st.session_state:
    st.session_state.edit_index_proyectos = None
if 'status_proyectos' not in st.session_state:
    st.session_state.status_proyectos = "EN PROCESO"
if 'sort_column_proyectos' not in st.session_state:
    st.session_state.sort_column_proyectos = 'fecha_cotizacion'
if 'sort_ascending_proyectos' not in st.session_state:
    st.session_state.sort_ascending_proyectos = False
if 'last_search' not in st.session_state:
    st.session_state.last_search = ""

ITEMS_PER_PAGE = 15

# ── DATA ──────────────────────────────────────────────
@st.cache_data(ttl=5)
def load_data():
    try:
        response = client.select("proyectos").execute()
        if response.data:
            data = pd.DataFrame(response.data)
            data = data.rename(columns={
                'proyecto_id': 'ID DE PROYECTO',
                'asesor': 'ASESOR',
                'cotizacion': 'COTIZACIÓN',
                'fecha_cotizacion': 'FECHA DE COTIZACIÓN',
                'proyecto': 'PROYECTO',
                'cliente': 'CLIENTE',
                'status': 'STATUS',
                'motivo_perdida': 'MOTIVO DE PÉRDIDA',
                'fecha_facturacion': 'FECHA DE FACTURACIÓN',
                'total': 'TOTAL',
                'observaciones': 'OBSERVACIONES'
            })
            return data
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error al cargar datos: {str(e)}")
        return pd.DataFrame()

def save_data(row_data, row_id=None):
    try:
        if row_id:
            client.update("proyectos", row_data, {"id": row_id})
        else:
            client.insert("proyectos", row_data)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Error al guardar datos: {str(e)}")
        return False

def delete_data(row_id):
    try:
        client.delete("proyectos", {"id": row_id})
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
    st.warning("¿Estás seguro de que deseas eliminar este proyecto?")
    st.info(f"**Proyecto:** {row.get('PROYECTO', '')}\n\n**Cliente:** {row.get('CLIENTE', '')}\n\n**Asesor:** {row.get('ASESOR', '')}")

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

@st.dialog(":material/edit: Editar Proyecto")
def edit_dialog(idx):
    data = load_data()
    if idx not in data.index:
        st.error("Registro no encontrado")
        return

    row = data.loc[idx]
    st.info(f"**ID:** {row.get('ID DE PROYECTO', '')}")

    status_options = ["PERDIDO", "GANADO", "EN PROCESO"]
    status_actual = row.get('STATUS', 'EN PROCESO')
    status_index = status_options.index(status_actual) if status_actual in status_options else 2
    status_edit = st.selectbox("Status", status_options, index=status_index, key=f"status_edit_{idx}")

    with st.form("form_editar_proyecto"):
        col1, col2, col3 = st.columns(3)

        with col1:
            asesor_edit = st.selectbox(
                "Selecciona un asesor de ventas", ASESORES,
                index=ASESORES.index(row.get('ASESOR', '')) if row.get('ASESOR', '') in ASESORES else None
            )
            cotizacion_edit = st.text_input("No. de Cotización", value=row.get('COTIZACIÓN', ''))
            fecha_cot_value = row.get('FECHA DE COTIZACIÓN', None)
            if fecha_cot_value and isinstance(fecha_cot_value, str):
                try:
                    fecha_cot_value = datetime.strptime(fecha_cot_value, '%Y-%m-%d').date()
                except:
                    fecha_cot_value = None
            fecha_cotizacion_edit = st.date_input("Fecha de Cotización", value=fecha_cot_value, key=f"fecha_edit_{idx}")

        with col2:
            proyecto_edit = st.text_input("Proyecto *", value=row.get('PROYECTO', ''))
            cliente_edit = st.text_input("Cliente *", value=row.get('CLIENTE', ''))

        with col3:
            motivo_perdida_edit = ""
            if status_edit == "PERDIDO":
                motivo_opciones = ["PRECIO", "STOCK/INVENTARIO", "OTRO"]
                motivo_actual = row.get('MOTIVO DE PÉRDIDA', '')
                motivo_index = motivo_opciones.index(motivo_actual) if motivo_actual in motivo_opciones else 0
                motivo_perdida_edit = st.selectbox("Motivo de Pérdida *", motivo_opciones, index=motivo_index)

            fecha_facturacion_edit = None
            if status_edit == "GANADO":
                fecha_fact_value = row.get('FECHA DE FACTURACIÓN', None)
                if fecha_fact_value and isinstance(fecha_fact_value, str):
                    try:
                        fecha_fact_value = datetime.strptime(fecha_fact_value, '%Y-%m-%d').date()
                    except:
                        fecha_fact_value = None
                fecha_facturacion_edit = st.date_input(
                    "Fecha de Facturación *", value=fecha_fact_value,
                    key=f"fecha_fact_edit_{idx}", help="Fecha en que se facturó el proyecto"
                )

            total_edit = st.number_input("Total ($) *", min_value=0.0, step=0.01,
                                         value=float(row.get('TOTAL', 0)))

        observaciones_edit = st.text_area("Observaciones", value=row.get('OBSERVACIONES', ''))

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            guardar = st.form_submit_button(":material/save: Guardar Cambios", use_container_width=True)
        with col_btn2:
            cancelar = st.form_submit_button(":material/cancel: Cancelar", use_container_width=True)

        if guardar:
            if asesor_edit and proyecto_edit and cliente_edit:
                if status_edit == "PERDIDO" and not motivo_perdida_edit:
                    st.error(":material/warning: Por favor selecciona el motivo de pérdida")
                elif status_edit == "GANADO" and not fecha_facturacion_edit:
                    st.error(":material/warning: Por favor selecciona la fecha de facturación")
                else:
                    row_id = row.get('id', '')
                    updated_data = {
                        'proyecto_id': row.get('ID DE PROYECTO', ''),
                        'asesor': asesor_edit,
                        'cotizacion': cotizacion_edit,
                        'fecha_cotizacion': fecha_cotizacion_edit.isoformat() if fecha_cotizacion_edit else None,
                        'proyecto': proyecto_edit,
                        'cliente': cliente_edit,
                        'status': status_edit,
                        'total': total_edit,
                        'motivo_perdida': motivo_perdida_edit if status_edit == "PERDIDO" else "",
                        'fecha_facturacion': fecha_facturacion_edit.isoformat() if status_edit == "GANADO" and fecha_facturacion_edit else None,
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

# ── FORMULARIO NUEVO PROYECTO ─────────────────────────
st.markdown("#### :material/add: Agregar Nuevo Proyecto/Cotización")

with st.container():
    col1, col2, col3 = st.columns(3)

    with col1:
        asesor = st.selectbox("Selecciona un asesor de ventas", ASESORES, key="asesor_nuevo").upper()
        cotizacion = st.text_input("No. de Cotización", key="cotizacion_nueva")
        fecha_cotizacion = st.date_input("Fecha de Cotización", value=None, key="fecha_cotizacion_nueva")

    with col2:
        proyecto = st.text_input("Proyecto *", key="proyecto_nuevo")
        cliente = st.text_input("Cliente *", key="cliente_nuevo")

    with col3:
        status = st.selectbox("Status *", ["PERDIDO", "GANADO", "EN PROCESO"], index=2, key="status_nuevo")

        motivo_perdida = ""
        if status == "PERDIDO":
            motivo_perdida = st.selectbox("Motivo de Pérdida *", ["PRECIO", "STOCK/INVENTARIO", "OTRO"], key="motivo_nuevo")

        fecha_facturacion = None
        if status == "GANADO":
            fecha_facturacion = st.date_input(
                "Fecha de Facturación *", value=None,
                key="fecha_facturacion_nueva", help="Fecha en que se facturó el proyecto"
            )

        total = st.number_input("Total ($) *", min_value=0.0, step=0.01, key="total_nuevo")

    observaciones = st.text_area("Observaciones", key="observaciones_nueva")

    if st.button(":material/save: Guardar Proyecto/Cotización", key="guardar_proyecto", type="primary", use_container_width=True):
        if asesor and proyecto and cliente:
            if status == "PERDIDO" and not motivo_perdida:
                st.error(":material/warning: Por favor selecciona el motivo de pérdida")
            elif status == "GANADO" and not fecha_facturacion:
                st.error(":material/warning: Por favor selecciona la fecha de facturación")
            else:
                nuevo_id = generar_id()
                nuevo_proyecto = {
                    'proyecto_id': nuevo_id,
                    'asesor': asesor.upper(),
                    'cotizacion': cotizacion,
                    'fecha_cotizacion': fecha_cotizacion.isoformat() if fecha_cotizacion else None,
                    'proyecto': proyecto.upper(),
                    'cliente': cliente.upper(),
                    'status': status,
                    'total': total,
                    'motivo_perdida': motivo_perdida.upper() if status == "PERDIDO" else "",
                    'fecha_facturacion': fecha_facturacion.isoformat() if status == "GANADO" and fecha_facturacion else None,
                    'observaciones': observaciones.upper() if observaciones else ""
                }
                if save_data(nuevo_proyecto):
                    st.success(":material/check_circle: Proyecto agregado exitosamente!")
                    time.sleep(1)
                    st.rerun()
        else:
            st.error(":material/warning: Por favor completa los campos obligatorios (*)")

st.markdown("---")

# ── TABLA ─────────────────────────────────────────────
st.markdown("#### :material/list: Lista de Proyectos/Cotizaciones")

def generar_tabla(data, btnselect=None, btnedit=None, btndelete=None):
    columnas_visibles = [col for col in data.columns if col not in ['id', 'OBSERVACIONES', 'ID DE PROYECTO', 'created_at', 'updated_at']]
    tabla_html = '<table class="responsive-table">\n<thead>\n<tr>\n'

    for col in columnas_visibles:
        tabla_html += f'    <th>{col}</th>\n'
    tabla_html += '    <th>Acción</th>\n</tr>\n</thead>\n<tbody>\n'

    for index, row in data.iterrows():
        tabla_html += '    <tr>\n'

        for col in columnas_visibles:
            if col == 'STATUS':
                badge_color = (
                    "#E74C3C" if row.get('STATUS', '') == 'PERDIDO' else
                    '#2ECC71' if row.get('STATUS', '') == 'GANADO' else
                    '#FFA500' if row.get('STATUS', '') == 'EN PROCESO' else
                    '#007fd6'
                )
                tabla_html += f'    <td><span style="background-color:{badge_color}; color:white; padding:5px 8px; border-radius:4px; font-size:11px; white-space:nowrap;">{row.get(col, "")}</span></td>\n'
            elif col == 'TOTAL':
                valor = row.get('TOTAL', 0) or 0
                tabla_html += f'    <td>${float(valor):,.2f}</td>\n'
            else:
                tabla_html += f'    <td>{row.get(col, "")}</td>\n'

        acciones = '    <td>'
        if btnselect:
            acciones += f'<a data-link="select_{row["ID DE PROYECTO"]}" class="btn-floating waves-effect waves-light btn"><i class="material-icons">check</i></a> '
        if btnedit:
            acciones += f'<a data-link="edit_{row["ID DE PROYECTO"]}" class="btn-floating waves-effect waves-light btn"><i class="material-icons">edit</i></a> '
        if btndelete:
            acciones += f'<a data-link="delete_{row["ID DE PROYECTO"]}" class="btn-floating waves-effect waves-light btn red"><i class="material-icons">delete</i></a>'
        acciones += '</td>\n'
        tabla_html += acciones
        tabla_html += '    </tr>\n'

    tabla_html += '</tbody>\n</table>'
    return tabla_html

styles = """
<link href="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css" rel="stylesheet">
<link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
"""
st.write(styles, unsafe_allow_html=True)

JS = estilo_tabla_js()

material_table = st.components.v2.component(
    name="material_table_with_buttons",
    js=JS,
    isolate_styles=False,
)

data = load_data()

def to_excel(data):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        export_df = data[['ID DE PROYECTO', 'ASESOR', 'PROYECTO', 'CLIENTE', 'STATUS', 'TOTAL', 'MOTIVO DE PÉRDIDA', 'FECHA DE COTIZACIÓN', 'FECHA DE FACTURACIÓN']].copy()
        export_df.columns = ['ID', 'Asesor', 'Proyecto', 'Cliente', 'Status', 'Total', 'Motivo de Pérdida', 'Fecha de Cotización', 'Fecha de Facturación']
        text_columns = ['ID', 'Asesor', 'Proyecto', 'Cliente', 'Status', 'Motivo de Pérdida']
        for col in text_columns:
            export_df[col] = export_df[col].astype(str).str.upper()
        export_df.to_excel(writer, index=False, sheet_name='Proyectos')
    return output.getvalue()


if not data.empty:
    # ── BÚSQUEDA ──────────────────────────────────────
    busqueda = st.text_input(
        ":material/search: Buscar",
        placeholder="Buscar por proyecto, cliente, asesor...",
        key="search_input_proyectos"
    )

    # Resetear página si cambia la búsqueda
    if busqueda != st.session_state.last_search:
        st.session_state.page_proyectos = 0
        st.session_state.last_search = busqueda

    if busqueda:
        data_filtrada = data[
            data['PROYECTO'].str.contains(busqueda, case=False, na=False) |
            data['CLIENTE'].str.contains(busqueda, case=False, na=False) |
            data['ASESOR'].str.contains(busqueda, case=False, na=False) |
            data['STATUS'].str.contains(busqueda, case=False, na=False)
        ]
    else:
        data_filtrada = data
        
    data_filtrada['FECHA DE FACTURACIÓN'] = data_filtrada['FECHA DE FACTURACIÓN'].fillna("")
    data_filtrada['FECHA DE COTIZACIÓN'] = data_filtrada['FECHA DE COTIZACIÓN'].fillna("")

    # ── PAGINACIÓN ────────────────────────────────────
    total_items = len(data_filtrada)
    total_pages = max(1, math.ceil(total_items / ITEMS_PER_PAGE))

    if st.session_state.page_proyectos >= total_pages:
        st.session_state.page_proyectos = total_pages - 1

    start_idx = st.session_state.page_proyectos * ITEMS_PER_PAGE
    end_idx = min(start_idx + ITEMS_PER_PAGE, total_items)
    data_pagina = data_filtrada.iloc[start_idx:end_idx]

    # ── RENDER TABLA ──────────────────────────────────
    paragraph_html = generar_tabla(data_pagina, btnedit=True, btndelete=True)

    resultado = material_table(
        data=paragraph_html,
        on_clicked_change=lambda: None,
        key=f"table_{st.session_state.page_proyectos}_{busqueda}"
    )

    # ── CONTROLES DE PAGINACIÓN ───────────────────────
    st.markdown("")
    col_prev, col_info, col_next = st.columns([1, 3, 1])

    with col_prev:
        if st.button(
            ":material/arrow_back: Anterior",
            disabled=(st.session_state.page_proyectos == 0),
            use_container_width=True,
            key="btn_prev_proy"
        ):
            st.session_state.page_proyectos -= 1
            st.rerun()

    with col_info:
        st.markdown(
            f"<div style='text-align:center; padding-top:8px; color:#666;'>"
            f"Página <b>{st.session_state.page_proyectos + 1}</b> de <b>{total_pages}</b>"
            f"&nbsp;·&nbsp; {total_items} registros"
            f"</div>",
            unsafe_allow_html=True
        )

    with col_next:
        if st.button(
            "Siguiente :material/arrow_forward:",
            disabled=(st.session_state.page_proyectos >= total_pages - 1),
            use_container_width=True,
            key="btn_next_proy"
        ):
            st.session_state.page_proyectos += 1
            st.rerun()
             
    excel_data = to_excel(data_filtrada)
    st.download_button(
        label=":material/download: Descargar Excel",
         data=excel_data,
         file_name=f"proyectos_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
         mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
         width='stretch'
    )

    # ── MANEJAR CLICKS DE BOTONES ─────────────────────
    if resultado and resultado.get("clicked"):
        clicked = resultado["clicked"]

        if clicked.startswith("edit_"):
            proyecto_id = clicked.replace("edit_", "")
            match = data[data['ID DE PROYECTO'] == proyecto_id]
            if not match.empty:
                edit_dialog(match.index[0])

        elif clicked.startswith("delete_"):
            proyecto_id = clicked.replace("delete_", "")
            match = data[data['ID DE PROYECTO'] == proyecto_id]
            if not match.empty:
                confirm_delete(match.index[0])

else:
    st.info(":material/note: No hay proyectos registrados. Agrega tu primer proyecto usando el formulario de arriba.")