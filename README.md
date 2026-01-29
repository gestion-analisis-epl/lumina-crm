# 📊 Lumina - Sistema de Gestión de Ventas

Sistema integral de gestión comercial desarrollado con Streamlit, diseñado para administrar citas, prospección y proyectos de ventas con integración a Google Sheets.

## 🚀 Características

### � Dashboard Ejecutivo
- **Vista estratégica de 30 segundos**: Responde "¿Cómo está mi negocio HOY?"
- **Métricas críticas del mes**: Meta, Ventas actuales (con delta), Total de cartera
- **Indicadores de actividad**: Citas, Prospectos, Proyectos, Ticket promedio
- **Estado del pipeline**: Visualización de proyectos por estado (En proceso, Ganados, Perdidos)
- **Últimos proyectos**: Vista rápida de los 5 proyectos más recientes
- **Filtros dinámicos**: Por rango de fechas y asesor con actualización en tiempo real

### 📈 Analytics
Análisis profundo dividido en dos áreas especializadas:

#### 💰 Ventas
- **Performance mensual**: Meta, Ventas actuales, Cotizaciones con indicadores de cumplimiento
- **Performance trimestral**: Metas por trimestre (Q1-Q4) con ventas acumuladas
- **Análisis de proyectos**: Dinero en proceso, ganado y perdido
- **Calidad de ventas**: Ticket promedio y análisis de cartera

#### 📞 Actividad Comercial
- **Cumplimiento de citas**: Promedio semanal con meta de 5 citas/asesor o 20 citas/equipo
- **Pipeline de oportunidades**: Total de citas, prospectos y proyectos activos
- **Embudo comercial**: Gráficos comparativos de distribución
- **Actividad reciente**: Tablas detalladas de últimas citas, prospectos y proyectos

### 📅 Gestión de Citas
- Registro y seguimiento de citas con prospectos
- Campos: ID, Asesor, Fecha, Prospecto, Giro, Acción a Seguir, Último Contacto
- Búsqueda avanzada con paginación (10 registros por página)
- Diseño responsive optimizado para móviles y tablets
- Edición y eliminación con confirmación mediante diálogos modales

### 🎯 Prospección
- Control completo de actividades de prospección
- Campos: ID, Asesor, Fecha, Prospecto, Tipo (Venta/Renta), Acción
- Interfaz responsive con íconos Material Design
- Gestión completa de registros con búsqueda y paginación

### 📂 Proyectos
- Administración integral de proyectos y cotizaciones
- Campos: ID, Asesor, Cotización, Proyecto, Cliente, Status, Total, Motivo Perdida, Observaciones
- Status con códigos de color: En Proceso (amarillo), Ganado (verde), Perdido (rojo)
- Motivo de pérdida condicional (Precio, Stock/Inventario, Otro)
- Seguimiento de ventas cerradas y análisis de cartera

## 🛠️ Tecnologías

- **Streamlit**: Framework principal de la aplicación
- **streamlit-gsheets**: Integración con Google Sheets
- **Pandas**: Manipulación y análisis de datos
- **Plotly**: Visualización de datos (gráficos interactivos)
- **Python 3.8+**: Lenguaje de programación

## 📋 Requisitos Previos

- Python 3.8 o superior
- Cuenta de Google con acceso a Google Sheets
- Credenciales de Google Sheets API

## ⚙️ Instalación

1. **Clonar el repositorio**
```bash
git clone <url-del-repositorio>
cd Lumina_V0.2
```

2. **Crear entorno virtual (recomendado)**
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias**
```bash
pip install -r requirements.txt
```

4. **Configurar Google Sheets**
   - Crear un proyecto en Google Cloud Console
   - Habilitar Google Sheets API
   - Descargar credenciales JSON
   - Configurar en `.streamlit/secrets.toml`:

```toml
[connections.gsheets]
spreadsheet = "URL_DE_TU_GOOGLE_SHEET"
type = "service_account"
project_id = "tu-project-id"
private_key_id = "tu-private-key-id"
private_key = "-----BEGIN PRIVATE KEY-----\ntu-private-key\n-----END PRIVATE KEY-----\n"
client_email = "tu-service-account@project-id.iam.gserviceaccount.com"
client_id = "tu-client-id"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "tu-cert-url"
```

5. **Estructura de Google Sheets**

Crear las siguientes hojas en tu Google Sheet:

- **CITAS**: ID, ASESOR, FECHA, PROSPECTO, GIRO, ACCION A SEGUIR, ULTIMO CONTACTO
- **PROSPECCION**: ID, ASESOR, FECHA, PROSPECTO, TIPO, ACCION
- **PROYECTOS**: ID, ASESOR, COTIZACIÓN, PROYECTO, CLIENTE, STATUS, TOTAL, MOTIVO PERDIDA, OBSERVACIONES
- **METAS**: Asesor, Mes, Año, Meta

## 🚀 Uso

Ejecutar la aplicación:

```bash
streamlit run app.py
```

La aplicación se abrirá en tu navegador en `http://localhost:8501`

## 📁 Estructura del Proyecto

```
Lumina_V0.2/
├── app.py                          # Página principal
├── pages/
│   ├── 1_Dashboard.py              # Dashboard ejecutivo
│   ├── 2_Citas.py                  # Gestión de citas
│   ├── 3_Prospección.py            # Gestión de prospección
│   ├── 4_Proyectos.py              # Gestión de proyectos
│   └── 5_Analytics.py              # Analytics (Ventas y Actividad)
├── utils/
│   ├── dashboard_config.py         # Configuración general
│   ├── dashboard_filters.py        # Filtros interactivos
│   ├── dashboard_metrics.py        # Cálculo de métricas
│   ├── dashboard_charts.py         # Visualizaciones
│   ├── data_loader.py              # Carga de datos
│   └── opciones.py                 # Constantes (asesores, giros)
├── .streamlit/
│   └── secrets.toml                # Configuración (no incluir en git)
├── static/                         # Archivos estáticos
├── img/                            # Imágenes
├── requirements.txt                # Dependencias
├── .gitignore                      # Archivos a ignorar
└── README.md                       # Este archivo
```

## 🎨 Características de UI/UX

- **Arquitectura de información**: Separación clara entre Dashboard ejecutivo y Analytics profundo
- **Storytelling visual**: Cada página responde una pregunta específica del negocio
- **Diseño responsive**: Tablas optimizadas para móviles, tablets y desktop
- **Material Design**: Íconos y componentes profesionales con Material Icons
- **Interactividad**: Filtros dinámicos que actualizan todas las métricas en tiempo real
- **Confirmaciones modales**: Diálogos para acciones críticas (edición/eliminación)
- **Feedback visual**: Mensajes de éxito/error con delays apropiados
- **Codificación por colores**: Estados visuales claros con sistema semáforo
- **Modularidad**: Código organizado en utilidades reutilizables

## 📊 Métricas y KPIs

### Dashboard Ejecutivo
- **Ventas vs Meta mensual**: Con delta dinámico (faltante/superado)
- **Total de cartera**: Valor total de proyectos activos
- **Ticket promedio**: Calidad de ventas por proyecto cerrado
- **Indicadores de actividad**: Citas, Prospectos, Proyectos (números clave)

### Analytics - Ventas
- **Performance mensual**: Meta, Ventas, Cotizaciones con objetivos 10x
- **Performance trimestral**: Metas Q1-Q4 con acumulados y % de cumplimiento
- **Análisis de proyectos**: Distribución de dinero por estado (Proceso/Ganado/Perdido)
- **Calidad de ventas**: Ticket promedio y total de cartera

### Analytics - Actividad Comercial
- **Citas semanales**: 
  - Meta individual: 5 citas/semana por asesor
  - Meta general: 20 citas/semana para el equipo
  - Codificación por colores:
    - 🔴 < 60% cumplimiento
    - 🟡 60-99% cumplimiento
    - 🟢 100-119% cumplimiento
    - 🟢 ≥ 120% cumplimiento
- **Pipeline de oportunidades**: Embudo completo de citas → prospectos → proyectos
- **Actividad reciente**: Últimas acciones por módulo

### Filtros Inteligentes
- **Por fechas**: Ajusta automáticamente metas y ventas al rango seleccionado
- **Por asesor**: Vista individual o consolidada del equipo
- **Actualización en tiempo real**: Todas las métricas responden a los filtros aplicados

## 🔐 Seguridad

- Las credenciales de Google Sheets deben mantenerse en `secrets.toml`
- No incluir `secrets.toml` en el repositorio
- Usar variables de entorno en producción

## 🤝 Contribución

Para contribuir al proyecto:

1. Fork el repositorio
2. Crear una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir un Pull Request

## 📝 Notas de Versión

### v0.2.1 (Actual)
- ✅ **Reestructuración de Dashboard**: Enfoque ejecutivo de 30 segundos
- ✅ **Nueva página Analytics**: Separación en Ventas y Actividad Comercial
- ✅ **Métricas trimestrales**: Seguimiento Q1-Q4 con acumulados
- ✅ **Filtros inteligentes**: Las metas se ajustan al rango de fechas seleccionado
- ✅ **Diseño responsive mejorado**: Tablas optimizadas para móviles
- ✅ **Arquitectura modular**: Código organizado en utilidades reutilizables
- ✅ **Storytelling visual**: Cada página responde una pregunta específica del negocio

### v0.2 (Anterior)
- ✅ Dashboard con métricas avanzadas
- ✅ Filtros interactivos por fecha y asesor
- ✅ Métricas de citas semanales con cumplimiento
- ✅ Tracking de ventas y cotizaciones
- ✅ Interfaz unificada sin formularios estáticos
- ✅ Campo condicional de motivo de pérdida en proyectos
- ✅ Integración completa con Google Sheets

## 📧 Soporte

Para reportar problemas o solicitar nuevas funcionalidades, crear un issue en el repositorio.

## 📄 Licencia

Este proyecto es de uso interno de Lumina.

---

Desarrollado con ❤️ para optimizar la gestión comercial de Lumina
# lumina-crm
