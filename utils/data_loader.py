"""
Carga de datos desde Google Sheets
"""
import pandas as pd
from streamlit_gsheets import GSheetsConnection


class DataLoader:
    """Manejador de conexión y carga de datos desde Google Sheets"""
    
    def __init__(self, connection):
        """
        Inicializa el cargador de datos
        
        Args:
            connection: Conexión de Streamlit a Google Sheets
        """
        self.conn = connection
        self.citas_data = None
        self.prospeccion_data = None
        self.proyectos_data = None
        self.metas_data = None
    
    def cargar_todos_datos(self):
        """
        Carga todos los datos de las hojas de Google Sheets
        
        Returns:
            tuple: (citas_data, prospeccion_data, proyectos_data, metas_data)
        """
        self.citas_data = self.conn.read(worksheet="CITAS", ttl=5).dropna(how="all")
        self.prospeccion_data = self.conn.read(worksheet="PROSPECCION", ttl=5).dropna(how="all")
        self.proyectos_data = self.conn.read(worksheet="PROYECTOS", ttl=5).dropna(how="all")
        self.metas_data = self.conn.read(worksheet="METAS", ttl=5).dropna(how="all")
        
        return self.citas_data, self.prospeccion_data, self.proyectos_data, self.metas_data
    
    def obtener_lista_asesores(self):
        """
        Obtiene la lista única de asesores de todas las hojas
        
        Returns:
            list: Lista ordenada de asesores únicos
        """
        asesores_citas = (
            self.citas_data['ASESOR'].dropna().unique().tolist()
            if 'ASESOR' in self.citas_data.columns and len(self.citas_data) > 0
            else []
        )
        asesores_prospeccion = (
            self.prospeccion_data['ASESOR'].dropna().unique().tolist()
            if 'ASESOR' in self.prospeccion_data.columns and len(self.prospeccion_data) > 0
            else []
        )
        asesores_proyectos = (
            self.proyectos_data['ASESOR'].dropna().unique().tolist()
            if 'ASESOR' in self.proyectos_data.columns and len(self.proyectos_data) > 0
            else []
        )
        asesores_metas = (
            self.metas_data['Asesor'].dropna().unique().tolist()
            if 'Asesor' in self.metas_data.columns and len(self.metas_data) > 0
            else []
        )
        
        todos_asesores = sorted(list(set(
            asesores_citas + asesores_prospeccion + asesores_proyectos + asesores_metas
        )))
        
        return todos_asesores


def inicializar_conexion(st_connection):
    """
    Función helper para inicializar la conexión y cargar datos
    
    Args:
        st_connection: Objeto st.connection de Streamlit
        
    Returns:
        DataLoader: Instancia del cargador de datos
    """
    loader = DataLoader(st_connection)
    loader.cargar_todos_datos()
    return loader
