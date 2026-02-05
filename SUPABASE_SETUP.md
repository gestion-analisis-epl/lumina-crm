# Migración a Supabase - Lumina V0.2

## Configuración Inicial

### 1. Crear tablas en Supabase

Ejecuta los siguientes comandos SQL en el editor SQL de Supabase:

#### Tabla CITAS
```sql
CREATE TABLE citas (
  id BIGSERIAL PRIMARY KEY,
  cita_id TEXT UNIQUE NOT NULL,
  asesor TEXT NOT NULL,
  fecha DATE NOT NULL,
  prospecto TEXT NOT NULL,
  giro TEXT,
  accion_seguir TEXT,
  ultimo_contacto DATE,
  created_at DATE DEFAULT CURRENT_DATE,
  updated_at DATE DEFAULT CURRENT_DATE
);

-- Índices para mejorar el rendimiento
CREATE INDEX idx_citas_asesor ON citas(asesor);
CREATE INDEX idx_citas_fecha ON citas(fecha);
CREATE INDEX idx_citas_prospecto ON citas(prospecto);
```

#### Tabla PROSPECCION
```sql
CREATE TABLE prospeccion (
  id BIGSERIAL PRIMARY KEY,
  prospecto_id TEXT UNIQUE NOT NULL,
  asesor TEXT NOT NULL,
  fecha DATE NOT NULL,
  prospecto TEXT NOT NULL,
  tipo TEXT,
  accion TEXT NOT NULL,
  created_at DATE DEFAULT CURRENT_DATE,
  updated_at DATE DEFAULT CURRENT_DATE
);

-- Índices
CREATE INDEX idx_prospeccion_asesor ON prospeccion(asesor);
CREATE INDEX idx_prospeccion_fecha ON prospeccion(fecha);
CREATE INDEX idx_prospeccion_prospecto ON prospeccion(prospecto);
```

#### Tabla PROYECTOS
```sql
CREATE TABLE proyectos (
  id BIGSERIAL PRIMARY KEY,
  proyecto_id TEXT UNIQUE NOT NULL,
  asesor TEXT NOT NULL,
  cotizacion TEXT,
  proyecto TEXT NOT NULL,
  cliente TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'En Proceso',
  total DECIMAL(15, 2) DEFAULT 0,
  motivo_perdida TEXT,
  observaciones TEXT,
  created_at DATE DEFAULT CURRENT_DATE,
  updated_at DATE DEFAULT CURRENT_DATE
);

-- Índices
CREATE INDEX idx_proyectos_asesor ON proyectos(asesor);
CREATE INDEX idx_proyectos_status ON proyectos(status);
CREATE INDEX idx_proyectos_cliente ON proyectos(cliente);
```

#### Tabla METAS
```sql
CREATE TABLE metas (
  id BIGSERIAL PRIMARY KEY,
  asesor TEXT NOT NULL,
  mes INTEGER NOT NULL,
  ano INTEGER NOT NULL,
  meta DECIMAL(15, 2) NOT NULL,
  created_at DATE DEFAULT CURRENT_DATE,
  updated_at DATE DEFAULT CURRENT_DATE,
  UNIQUE(asesor, mes, ano)
);

-- Índices
CREATE INDEX idx_metas_asesor ON metas(asesor);
CREATE INDEX idx_metas_periodo ON metas(mes, ano);
```

#### Triggers para actualizar `updated_at` automáticamente

```sql
-- Función para actualizar updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_DATE;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Aplicar trigger a cada tabla
CREATE TRIGGER update_citas_updated_at BEFORE UPDATE ON citas
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_prospeccion_updated_at BEFORE UPDATE ON prospeccion
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_proyectos_updated_at BEFORE UPDATE ON proyectos
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_metas_updated_at BEFORE UPDATE ON metas
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

### 2. Habilitar Row Level Security (Opcional pero recomendado)

Si quieres seguridad adicional:

```sql
-- Habilitar RLS en todas las tablas
ALTER TABLE citas ENABLE ROW LEVEL SECURITY;
ALTER TABLE prospeccion ENABLE ROW LEVEL SECURITY;
ALTER TABLE proyectos ENABLE ROW LEVEL SECURITY;
ALTER TABLE metas ENABLE ROW LEVEL SECURITY;

-- Política para permitir todas las operaciones (ajusta según tus necesidades)
CREATE POLICY "Permitir todas las operaciones" ON citas FOR ALL USING (true);
CREATE POLICY "Permitir todas las operaciones" ON prospeccion FOR ALL USING (true);
CREATE POLICY "Permitir todas las operaciones" ON proyectos FOR ALL USING (true);
CREATE POLICY "Permitir todas las operaciones" ON metas FOR ALL USING (true);
```

### 3. Configurar credenciales

Crea el archivo `.streamlit/secrets.toml` con tus credenciales de Supabase:

```toml
[supabase]
url = "https://tu-proyecto.supabase.co"
key = "tu_clave_anon_publica"
```

**Nota:** Para desplegar en Streamlit Cloud, agrega estos secrets en la configuración de tu app en el dashboard de Streamlit Cloud.

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 5. Migrar datos desde Google Sheets (Opcional)

Si tienes datos en Google Sheets y quieres migrarlos a Supabase, puedes crear un script de migración o importar manualmente los datos usando la interfaz de Supabase.

**Nota importante sobre los nombres de columnas:**
- Las columnas en Supabase usan snake_case (minúsculas con guiones bajos)
- Ejemplo: `ASESOR` → `asesor`, `FECHA` → `fecha`, `ACCION A SEGUIR` → `accion_seguir`

### 6. Ejecutar la aplicación

```bash
streamlit run app.py
```

## Estructura de las tablas

### Tabla `citas`
- `id`: ID autoincremental (clave primaria)
- `cita_id`: ID único generado por la aplicación (formato: ID-XXXXXXXXXXXXX)
- `asesor`: Nombre del asesor
- `fecha`: Fecha de la cita
- `prospecto`: Nombre del prospecto
- `giro`: Giro de negocio
- `accion_seguir`: Acción a seguir
- `ultimo_contacto`: Fecha del último contacto

### Tabla `prospeccion`
- `id`: ID autoincremental (clave primaria)
- `prospecto_id`: ID único generado por la aplicación
- `asesor`: Nombre del asesor
- `fecha`: Fecha de prospección
- `prospecto`: Nombre del prospecto
- `tipo`: Tipo (Venta o Renta)
- `accion`: Acción realizada

### Tabla `proyectos`
- `id`: ID autoincremental (clave primaria)
- `proyecto_id`: ID único generado por la aplicación
- `asesor`: Nombre del asesor
- `cotizacion`: Número de cotización
- `proyecto`: Nombre del proyecto
- `cliente`: Nombre del cliente
- `status`: Estado del proyecto (En Proceso, Ganado, Perdido)
- `total`: Monto total del proyecto
- `motivo_perdida`: Motivo si el proyecto se perdió
- `observaciones`: Observaciones adicionales

### Tabla `metas`
- `id`: ID autoincremental (clave primaria)
- `asesor`: Nombre del asesor
- `mes`: Número del mes (1-12)
- `ano`: Año
- `meta`: Monto de la meta

## Notas Importantes

1. **Cambio de nombres de columnas**: Todas las columnas ahora usan snake_case (minúsculas con guiones bajos) en lugar de mayúsculas.

2. **IDs únicos**: Cada tabla tiene:
   - Un `id` autoincremental como clave primaria de la base de datos
   - Un ID de aplicación (`cita_id`, `prospecto_id`, `proyecto_id`) que es el que se muestra al usuario

3. **Operaciones CRUD**: Todas las operaciones CRUD ahora se realizan directamente en Supabase en lugar de Google Sheets.

4. **Caché**: Los datos se cachean por 5 segundos para mejorar el rendimiento.

5. **Migración gradual**: Si necesitas migrar desde Google Sheets, puedes exportar los datos como CSV y luego importarlos en Supabase usando su interfaz web.
