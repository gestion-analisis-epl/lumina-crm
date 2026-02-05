"""
Script para actualizar nombres de columnas de mayúsculas a minúsculas con guiones bajos
en los archivos de utilidades del dashboard
"""
import os
import re

# Mapeo de nombres de columnas
COLUMN_MAPPING = {
    'ASESOR': 'asesor',
    'FECHA': 'fecha',
    'FECHA_DT': 'fecha_dt',
    'STATUS': 'status',
    'TOTAL': 'total',
    'PROSPECTO': 'prospecto',
    'PROYECTO': 'proyecto',
    'CLIENTE': 'cliente',
    'GIRO': 'giro',
    'ACCION': 'accion',
    'TIPO': 'tipo',
    'ID': 'id',
    'COTIZACIÓN': 'cotizacion',
    'MOTIVO PERDIDA': 'motivo_perdida',
    'OBSERVACIONES': 'observaciones',
    'ULTIMO CONTACTO': 'ultimo_contacto',
    'ACCION A SEGUIR': 'accion_seguir',
    'SEMANA': 'semana',
    'AÑO': 'ano',
    'CITAS': 'citas',
    'Asesor': 'asesor',
    'Mes': 'mes',
    'Año': 'ano',
    'Meta': 'meta',
    'Año_Mes': 'ano_mes',
    'EMPRESA': 'empresa',
    'MES': 'mes'
}

def update_file(file_path):
    """Actualiza un archivo reemplazando los nombres de columnas"""
    print(f"Procesando: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    
    # Reemplazar referencias a columnas entre comillas
    for old_col, new_col in COLUMN_MAPPING.items():
        # Reemplazar 'COLUMNA'
        content = re.sub(f"'{old_col}'", f"'{new_col}'", content)
        # Reemplazar "COLUMNA"
        content = re.sub(f'"{old_col}"', f'"{new_col}"', content)
        # Reemplazar ['COLUMNA']
        content = re.sub(f"\\['{old_col}'\\]", f"['{new_col}']", content)
        content = re.sub(f'\\["{old_col}"\\]', f'["{new_col}"]', content)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✓ Actualizado")
        return True
    else:
        print(f"  - Sin cambios")
        return False

def main():
    """Función principal"""
    base_path = os.path.dirname(os.path.abspath(__file__))
    utils_path = os.path.join(base_path, 'utils')
    
    files_to_update = [
        os.path.join(utils_path, 'dashboard_metrics.py'),
        os.path.join(utils_path, 'dashboard_filters.py'),
        os.path.join(utils_path, 'dashboard_charts.py'),
    ]
    
    # También actualizar el Dashboard
    dashboard_path = os.path.join(base_path, 'pages', '1_Dashboard.py')
    files_to_update.append(dashboard_path)
    
    print("Iniciando actualización de nombres de columnas...")
    print("=" * 60)
    
    updated_count = 0
    for file_path in files_to_update:
        if os.path.exists(file_path):
            if update_file(file_path):
                updated_count += 1
        else:
            print(f"⚠ Archivo no encontrado: {file_path}")
    
    print("=" * 60)
    print(f"Proceso completado. {updated_count} archivo(s) actualizado(s).")

if __name__ == "__main__":
    main()
