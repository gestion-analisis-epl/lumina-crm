import streamlit as st
from styles.tablejs import estilo_tabla_js
from styles.table_helpers import avatar_html, ASESOR_CORTO, dataframe_to_excel
from utils.opciones import ASESORES
from utils.supabase_client import get_supabase_client
import pandas as pd
from datetime import datetime, date
import random
import time

st.set_page_config(page_title="Citas", page_icon=":material/calendar_today:", layout="wide")

st.markdown("""
<style>
    .stDataFrame { border-radius: 10px; }
    .stDateInput { text-align: center; }
    .search-box { margin-bottom: 20px; }

    .table-card {
        border: 1px solid #e9ecef;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    table { border-collapse: collapse; width: 100%; font-family: 'Inter',sans-serif; font-size: 0.85rem; }
    th { background-color: #f8f9fa; color: #495057; padding: 12px 14px; text-align: left; font-size: 0.78rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 2px solid #dee2e6; }
    td { padding: 10px 14px; border-bottom: 1px solid #f0f4f8; color: #212529; }
    tbody tr:nth-child(even) td { background-color: #f8f9fa; }
    tr:hover td { background-color: #eef1f4; }

    .badge-soft { display:inline-block; padding: 3px 11px; border-radius: 999px; font-size: 0.72rem; font-weight: 600; white-space: nowrap; }

    .btn-icon {
        display:inline-flex; align-items:center; justify-content:center;
        width: 30px; height: 30px; border-radius: 6px;
        border: 1px solid #dee2e6; color: #495057; background: #fff;
        margin-right: 4px; cursor: pointer; text-decoration:none;
        transition: background .15s, border-color .15s, color .15s;
    }
    .btn-icon:hover { background:#e7f1ff; border-color:#9ec5fe; color:#0d6efd; }
    .btn-icon-danger:hover { background:#f8d7da; border-color:#f1aeb5; color:#dc3545; }
    .btn-icon svg { width:15px; height:15px; }
</style>
""", unsafe_allow_html=True)

st.title(":material/calendar_today: Gestión de Citas")

client = get_supabase_client()

# ── SESSION STATE ─────────────────────────────────────
if 'search_query_citas' not in st.session_state:
    st.session_state.search_query_citas = ""
if 'show_edit_dialog_citas' not in st.session_state:
    st.session_state.show_edit_dialog_citas = False
if 'edit_index_citas' not in st.session_state:
    st.session_state.edit_index_citas = None

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

ICON_EDIT = '<svg viewBox="0 0 16 16" fill="currentColor"><path d="M12.146.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1 0 .708l-10 10a.5.5 0 0 1-.168.11l-5 2a.5.5 0 0 1-.65-.65l2-5a.5.5 0 0 1 .11-.168zm.708 1.707L11.207 3.5l1.293 1.293 1.647-1.647zM10.5 4.207 3.5 11.207v.5h.5l7-7z"/></svg>'
ICON_DELETE = '<svg viewBox="0 0 16 16" fill="currentColor"><path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0z"/><path d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4zM2.5 3h11V2h-11z"/></svg>'

def generar_tabla(data, btnedit=None, btndelete=None):
    columnas_visibles = [col for col in data.columns if col not in ['id', 'ID DE CITA', 'created_at', 'updated_at']]
    tabla_html = '<div class="table-card"><table class="responsive-table">\n<thead>\n<tr>\n'

    for col in columnas_visibles:
        tabla_html += f'    <th>{col}</th>\n'
    tabla_html += '    <th>Acción</th>\n</tr>\n</thead>\n<tbody>\n'

    for index, row in data.iterrows():
        tabla_html += '    <tr>\n'

        for col in columnas_visibles:
            if col == 'ASESOR':
                nombre = ASESOR_CORTO.get(row.get('ASESOR', ''), row.get('ASESOR', ''))
                tabla_html += f'    <td data-value="{nombre}">{avatar_html(nombre)}</td>\n'
            else:
                tabla_html += f'    <td>{row.get(col, "")}</td>\n'

        acciones = '    <td>'
        if btnedit:
            acciones += f'<a data-link="edit_{row["ID DE CITA"]}" class="btn-icon" title="Editar">{ICON_EDIT}</a>'
        if btndelete:
            acciones += f'<a data-link="delete_{row["ID DE CITA"]}" class="btn-icon btn-icon-danger" title="Eliminar">{ICON_DELETE}</a>'
        acciones += '</td>\n'
        tabla_html += acciones
        tabla_html += '    </tr>\n'

    tabla_html += '</tbody>\n</table></div>'
    return tabla_html

def to_excel(data):
    export_cols = ['ID DE CITA', 'ASESOR', 'FECHA', 'PROSPECTO', 'GIRO', 'ACCIÓN A SEGUIR', 'ÚLTIMO CONTACTO']
    available_cols = [c for c in export_cols if c in data.columns]
    export_df = data[available_cols].copy()
    export_df.columns = ['ID', 'Asesor', 'Fecha', 'Prospecto', 'Giro', 'Acción a Seguir', 'Último Contacto'][:len(available_cols)]
    for col in ['ID', 'Asesor', 'Prospecto', 'Giro', 'Acción a Seguir']:
        if col in export_df.columns:
            export_df[col] = export_df[col].astype(str).str.upper()
    return dataframe_to_excel(export_df, sheet_name='Citas')

JS = estilo_tabla_js()

material_table = st.components.v2.component(
    name="material_table_citas",
    js=JS,
    isolate_styles=False,
)

data = load_data()

if not data.empty:
    # ── BÚSQUEDA + DESCARGA ────────────────────────────
    col_search, col_download = st.columns([5, 1], vertical_alignment="bottom")
    with col_search:
        busqueda = st.text_input(
            ":material/search: Buscar",
            placeholder="Buscar por prospecto, asesor, fecha...",
            key="search_input_citas"
        )

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

    with col_download:
        excel_data = to_excel(data_filtrada)
        st.download_button(
            label=":material/download: Excel",
            data=excel_data,
            file_name=f"citas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            width='stretch'
        )

    # ── RENDER TABLA ──────────────────────────────────
    # Se manda TODO data_filtrada: los filtros de header, el orden y la
    # paginación (Anterior/Siguiente) se calculan en el navegador sobre
    # el 100% de las filas, no solo sobre una página.
    paragraph_html = generar_tabla(data_filtrada, btnedit=True, btndelete=True)

    resultado = material_table(
        data=paragraph_html,
        on_clicked_change=lambda: None,
        key=f"table_citas_{busqueda}"
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
    st.markdown("""
    <div style="text-align:center;padding:52px 24px;border:2px dashed #cbd5e1;
                border-radius:14px;background:#f8fafc;margin:24px 0;">
        <div style="font-size:3.2rem;margin-bottom:12px;line-height:1;">📅</div>
        <div style="font-size:1.1rem;font-weight:600;color:#334155;margin-bottom:8px;">
            No hay citas registradas
        </div>
        <div style="font-size:.9rem;color:#94a3b8;">
            Agrega tu primera cita usando el formulario de arriba.
        </div>
    </div>""", unsafe_allow_html=True)
