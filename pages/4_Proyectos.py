import streamlit as st
from styles.tablejs import estilo_tabla_js
from styles.table_helpers import avatar_html, ASESOR_CORTO
from utils.supabase_client import get_supabase_client
import pandas as pd
from datetime import datetime, date
import random
import time
from io import BytesIO
import requests

from utils.opciones import ASESORES

st.set_page_config(page_title="Proyectos/Cotizaciones", page_icon=":material/folder:", layout="wide")

st.markdown("""
<style>
    .stDataFrame { border-radius: 10px; }
    .search-box { margin-bottom: 20px; }

    .table-card {
        border: 1px solid #e9ecef;
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    table { border-collapse: collapse; width: 100%; font-family: -apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; font-size: 0.85rem; }
    th { background-color: #f8f9fa; color: #495057; padding: 12px 14px; text-align: left; font-size: 0.78rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 2px solid #dee2e6; }
    td { padding: 10px 14px; border-bottom: 1px solid #f0f4f8; color: #212529; }
    tbody tr:nth-child(even) td { background-color: #f8f9fa; }
    tr:hover td { background-color: #eef1f4; }
    .cell-numeric { text-align: right; font-weight: 600; font-variant-numeric: tabular-nums; }

    .badge-soft { display:inline-block; padding: 3px 11px; border-radius: 999px; font-size: 0.72rem; font-weight: 600; white-space: nowrap; }
    .badge-soft-danger  { background:#f8d7da; color:#842029; }
    .badge-soft-success { background:#d1e7dd; color:#0f5132; }
    .badge-soft-warning { background:#fff3cd; color:#664d03; }
    .badge-soft-info    { background:#cff4fc; color:#055160; }

    .btn-icon {
        display:inline-flex; align-items:center; justify-content:center;
        width: 30px; height: 30px; border-radius: 6px;
        border: 1px solid #dee2e6; color: #495057; background: #fff;
        margin-right: 4px; cursor: pointer; text-decoration:none;
        transition: background .15s, border-color .15s, color .15s;
    }
    .btn-icon:hover { background:#e7f1ff; border-color:#9ec5fe; color:#0d6efd; }
    .btn-icon-danger:hover  { background:#f8d7da; border-color:#f1aeb5; color:#dc3545; }
    .btn-icon-success:hover { background:#d1e7dd; border-color:#a3cfbb; color:#198754; }
    .btn-icon svg { width:15px; height:15px; }
</style>
""", unsafe_allow_html=True)

st.title(":material/folder: Gestión de Proyectos/Cotizaciones")

client = get_supabase_client()

# ── SESSION STATE ─────────────────────────────────────
if 'search_query_proyectos' not in st.session_state:
    st.session_state.search_query_proyectos = ""
if 'show_edit_dialog_proyectos' not in st.session_state:
    st.session_state.show_edit_dialog_proyectos = False
if 'edit_index_proyectos' not in st.session_state:
    st.session_state.edit_index_proyectos = None
if 'status_proyectos' not in st.session_state:
    st.session_state.status_proyectos = "EN PROCESO"

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

    with st.container():
        col1, col2, col3 = st.columns(3)

        with col1:
            asesor_edit = st.selectbox(
                "Selecciona un asesor de ventas", ASESORES,
                index=ASESORES.index(row.get('ASESOR', '')) if row.get('ASESOR', '') in ASESORES else None,
                key=f"asesor_edit_{idx}"
            )
            cotizacion_edit = st.text_input("No. de Cotización", value=row.get('COTIZACIÓN', ''), key=f"cotizacion_edit_{idx}")
            fecha_cot_value = row.get('FECHA DE COTIZACIÓN', None)
            if fecha_cot_value and isinstance(fecha_cot_value, str):
                try:
                    fecha_cot_value = datetime.strptime(fecha_cot_value, '%Y-%m-%d').date()
                except:
                    fecha_cot_value = None
            fecha_cotizacion_edit = st.date_input("Fecha de Cotización", value=fecha_cot_value, key=f"fecha_edit_{idx}")

        with col2:
            proyecto_edit = st.text_input("Proyecto *", value=row.get('PROYECTO', ''), key=f"proyecto_edit_{idx}")
            cliente_edit = st.text_input("Cliente *", value=row.get('CLIENTE', ''), key=f"cliente_edit_{idx}")

        with col3:
            motivo_perdida_edit = ""
            if status_edit == "PERDIDO":
                motivo_opciones = ["PRECIO", "STOCK/INVENTARIO", "OTRO"]
                motivo_actual = row.get('MOTIVO DE PÉRDIDA', '')
                motivo_index = motivo_opciones.index(motivo_actual) if motivo_actual in motivo_opciones else 0
                motivo_perdida_edit = st.selectbox("Motivo de Pérdida *", motivo_opciones, index=motivo_index, key=f"motivo_edit_{idx}")

            fecha_facturacion_edit = None
            if status_edit == "GANADO":
                fecha_fact_raw = row.get('FECHA DE FACTURACIÓN', None)
                fecha_fact_value = None
                if fecha_fact_raw and not pd.isna(fecha_fact_raw) and isinstance(fecha_fact_raw, str):
                    try:
                        fecha_fact_value = datetime.strptime(fecha_fact_raw, '%Y-%m-%d').date()
                    except (ValueError, TypeError):
                        pass
                fecha_facturacion_edit = st.date_input(
                    "Fecha de Facturación *", value=fecha_fact_value or date.today(),
                    key=f"fecha_fact_edit_{idx}", help="Fecha en que se facturó el proyecto"
                )

            total_edit = st.number_input("Total ($) *", min_value=0.0, step=0.01,
                                         value=float(row.get('TOTAL', 0)), key=f"total_edit_{idx}")

        observaciones_edit = st.text_area("Observaciones", value=row.get('OBSERVACIONES', ''), key=f"obs_edit_{idx}")

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            guardar = st.button(":material/save: Guardar Cambios", use_container_width=True, type="primary", key=f"guardar_edit_{idx}")
        with col_btn2:
            cancelar = st.button(":material/cancel: Cancelar", use_container_width=True, key=f"cancelar_edit_{idx}")

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
                "Fecha de Facturación *", value=date.today(),
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

ICON_CHECK  = '<svg viewBox="0 0 16 16" fill="currentColor"><path d="M13.854 3.646a.5.5 0 0 1 0 .708l-7 7a.5.5 0 0 1-.708 0l-3.5-3.5a.5.5 0 1 1 .708-.708L6.5 10.293l6.646-6.647a.5.5 0 0 1 .708 0"/></svg>'
ICON_EDIT   = '<svg viewBox="0 0 16 16" fill="currentColor"><path d="M12.146.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1 0 .708l-10 10a.5.5 0 0 1-.168.11l-5 2a.5.5 0 0 1-.65-.65l2-5a.5.5 0 0 1 .11-.168zm.708 1.707L11.207 3.5l1.293 1.293 1.647-1.647zM10.5 4.207 3.5 11.207v.5h.5l7-7z"/></svg>'
ICON_DELETE = '<svg viewBox="0 0 16 16" fill="currentColor"><path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5m3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0z"/><path d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4zM2.5 3h11V2h-11z"/></svg>'

STATUS_BADGE = {
    'PERDIDO':    'badge-soft-danger',
    'GANADO':     'badge-soft-success',
    'EN PROCESO': 'badge-soft-warning',
}

def generar_tabla(data, btnselect=None, btnedit=None, btndelete=None):
    columnas_visibles = [col for col in data.columns if col not in ['id', 'OBSERVACIONES', 'ID DE PROYECTO', 'created_at', 'updated_at']]
    tabla_html = '<div class="table-card"><table class="responsive-table">\n<thead>\n<tr>\n'

    for col in columnas_visibles:
        tabla_html += f'    <th>{col}</th>\n'
    tabla_html += '    <th>Acción</th>\n</tr>\n</thead>\n<tbody>\n'

    for index, row in data.iterrows():
        tabla_html += '    <tr>\n'

        for col in columnas_visibles:
            if col == 'STATUS':
                badge_class = STATUS_BADGE.get(row.get('STATUS', ''), 'badge-soft-info')
                tabla_html += f'    <td data-value="{row.get(col, "")}"><span class="badge-soft {badge_class}">{row.get(col, "")}</span></td>\n'
            elif col == 'TOTAL':
                valor = row.get('TOTAL', 0) or 0
                tabla_html += f'    <td class="cell-numeric" data-value="{valor}">${float(valor):,.2f}</td>\n'
            elif col == 'ASESOR':
                nombre = ASESOR_CORTO.get(row.get('ASESOR', ''), row.get('ASESOR', ''))
                tabla_html += f'    <td data-value="{nombre}">{avatar_html(nombre)}</td>\n'
            else:
                tabla_html += f'    <td>{row.get(col, "")}</td>\n'

        acciones = '    <td>'
        if btnselect:
            acciones += f'<a data-link="select_{row["ID DE PROYECTO"]}" class="btn-icon btn-icon-success" title="Seleccionar">{ICON_CHECK}</a>'
        if btnedit:
            acciones += f'<a data-link="edit_{row["ID DE PROYECTO"]}" class="btn-icon" title="Editar">{ICON_EDIT}</a>'
        if btndelete:
            acciones += f'<a data-link="delete_{row["ID DE PROYECTO"]}" class="btn-icon btn-icon-danger" title="Eliminar">{ICON_DELETE}</a>'
        acciones += '</td>\n'
        tabla_html += acciones
        tabla_html += '    </tr>\n'

    tabla_html += '</tbody>\n</table></div>'
    return tabla_html

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
    # ── PIPELINE SUMMARY ──────────────────────────────
    en_proceso = data[data['STATUS'] == 'EN PROCESO']
    ganado     = data[data['STATUS'] == 'GANADO']
    perdido    = data[data['STATUS'] == 'PERDIDO']
    total_oport = len(en_proceso) + len(ganado)
    tasa = (len(ganado) / total_oport * 100) if total_oport > 0 else 0

    def _pipeline_card(color, label, count, total_val):
        return f"""<div style="background:#fff;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,.07);
            border:1px solid #e2e8f0;border-left:4px solid {color};padding:20px 16px;
            text-align:center;height:110px;display:flex;flex-direction:column;justify-content:center;">
            <div style="font-size:.72rem;font-weight:700;text-transform:uppercase;letter-spacing:.07em;color:#7a93a6;margin-bottom:6px;">{label}</div>
            <div style="font-size:1.6rem;font-weight:700;color:{color};line-height:1.1;">{count}</div>
            <div style="font-size:.9rem;font-weight:600;color:#64748b;margin-top:3px;">${total_val:,.0f}</div>
        </div>"""

    pc1, pc2, pc3, pc4 = st.columns(4)
    with pc1:
        st.markdown(_pipeline_card("#FFA500", "⏳ En Proceso", len(en_proceso), en_proceso['TOTAL'].fillna(0).sum()), unsafe_allow_html=True)
    with pc2:
        st.markdown(_pipeline_card("#2ECC71", "✅ Ganado", len(ganado), ganado['TOTAL'].fillna(0).sum()), unsafe_allow_html=True)
    with pc3:
        st.markdown(_pipeline_card("#E74C3C", "❌ Perdido", len(perdido), perdido['TOTAL'].fillna(0).sum()), unsafe_allow_html=True)
    with pc4:
        st.markdown(f"""<div style="background:linear-gradient(135deg,#003057 0%,#005fa3 100%);border-radius:12px;
            box-shadow:0 2px 8px rgba(0,48,87,.18);padding:20px 16px;text-align:center;color:white;
            height:110px;display:flex;flex-direction:column;justify-content:center;">
            <div style="font-size:.72rem;font-weight:700;text-transform:uppercase;letter-spacing:.07em;opacity:.75;margin-bottom:6px;">🎯 Conversión</div>
            <div style="font-size:1.8rem;font-weight:700;line-height:1.1;">{tasa:.1f}%</div>
            <div style="font-size:.8rem;opacity:.7;margin-top:3px;">{len(ganado)} ganados / {total_oport} oport.</div>
        </div>""", unsafe_allow_html=True)
    st.markdown("")

    # ── BÚSQUEDA ──────────────────────────────────────
    busqueda = st.text_input(
        ":material/search: Buscar",
        placeholder="Buscar por proyecto, cliente, asesor...",
        key="search_input_proyectos"
    )

    if busqueda:
        data_filtrada = data[
            data['PROYECTO'].str.contains(busqueda, case=False, na=False) |
            data['CLIENTE'].str.contains(busqueda, case=False, na=False) |
            data['ASESOR'].str.contains(busqueda, case=False, na=False) |
            data['STATUS'].str.contains(busqueda, case=False, na=False)
        ]
    else:
        data_filtrada = data

    data_filtrada = data_filtrada.copy()
    data_filtrada['FECHA DE FACTURACIÓN'] = data_filtrada['FECHA DE FACTURACIÓN'].fillna("")
    data_filtrada['FECHA DE COTIZACIÓN'] = data_filtrada['FECHA DE COTIZACIÓN'].fillna("")

    # ── RENDER TABLA ──────────────────────────────────
    # Se manda TODO data_filtrada: los filtros de header, el orden y la
    # paginación (Anterior/Siguiente) se calculan en el navegador sobre
    # el 100% de las filas, no solo sobre una página.
    paragraph_html = generar_tabla(data_filtrada, btnedit=True, btndelete=True)

    resultado = material_table(
        data=paragraph_html,
        on_clicked_change=lambda: None,
        key=f"table_{busqueda}"
    )

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
    st.markdown("""
    <div style="text-align:center;padding:52px 24px;border:2px dashed #cbd5e1;
                border-radius:14px;background:#f8fafc;margin:24px 0;">
        <div style="font-size:3.2rem;margin-bottom:12px;line-height:1;">📁</div>
        <div style="font-size:1.1rem;font-weight:600;color:#334155;margin-bottom:8px;">
            No hay proyectos registrados
        </div>
        <div style="font-size:.9rem;color:#94a3b8;">
            Agrega tu primer proyecto usando el formulario de arriba.
        </div>
    </div>""", unsafe_allow_html=True)