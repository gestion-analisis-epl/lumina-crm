"""
Carga de datos desde Supabase
"""
import pandas as pd
from .supabase_client import get_supabase_client
import streamlit as st


class DataLoader:
    """Manejador de conexión y carga de datos desde Supabase"""
    
    def __init__(self):
        """
        Inicializa el cargador de datos
        """
        self.client = get_supabase_client()
        self.citas_data = None
        self.prospeccion_data = None
        self.proyectos_data = None
        self.metas_data = None
    
    def cargar_todos_datos(self):
        """
        Carga todos los datos de las tablas de Supabase
        
        Returns:
            tuple: (citas_data, prospeccion_data, proyectos_data, metas_data)
        """
        try:
            # Cargar CITAS
            citas_response = self.client.select("citas").execute()
            self.citas_data = pd.DataFrame(citas_response.data) if citas_response.data else pd.DataFrame()
            
            # Cargar PROSPECCION
            prospeccion_response = self.client.select("prospeccion").execute()
            self.prospeccion_data = pd.DataFrame(prospeccion_response.data) if prospeccion_response.data else pd.DataFrame()
            
            # Cargar PROYECTOS
            proyectos_response = self.client.select("proyectos").execute()
            self.proyectos_data = pd.DataFrame(proyectos_response.data) if proyectos_response.data else pd.DataFrame()
            
            # Cargar METAS
            metas_response = self.client.select("metas").execute()
            self.metas_data = pd.DataFrame(metas_response.data) if metas_response.data else pd.DataFrame()
            
            return self.citas_data, self.prospeccion_data, self.proyectos_data, self.metas_data
        except Exception as e:
            st.error(f"Error al cargar datos desde Supabase: {str(e)}")
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
    
    def obtener_lista_asesores(self):
        """
        Obtiene la lista única de asesores de todas las tablas
        
        Returns:
            list: Lista ordenada de asesores únicos
        """
        asesores_citas = (
            self.citas_data['asesor'].dropna().unique().tolist()
            if 'asesor' in self.citas_data.columns and len(self.citas_data) > 0
            else []
        )
        asesores_prospeccion = (
            self.prospeccion_data['asesor'].dropna().unique().tolist()
            if 'asesor' in self.prospeccion_data.columns and len(self.prospeccion_data) > 0
            else []
        )
        asesores_proyectos = (
            self.proyectos_data['asesor'].dropna().unique().tolist()
            if 'asesor' in self.proyectos_data.columns and len(self.proyectos_data) > 0
            else []
        )
        asesores_metas = (
            self.metas_data['asesor'].dropna().unique().tolist()
            if 'asesor' in self.metas_data.columns and len(self.metas_data) > 0
            else []
        )
        
        todos_asesores = sorted(list(set(
            asesores_citas + asesores_prospeccion + asesores_proyectos + asesores_metas
        )))
        
        return todos_asesores


def inicializar_conexion():
    """
    Función helper para inicializar la conexión y cargar datos
        
    Returns:
        DataLoader: Instancia del cargador de datos
    """
    loader = DataLoader()
    loader.cargar_todos_datos()
    return loader
