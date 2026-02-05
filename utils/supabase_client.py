"""
Cliente de Supabase para gestionar la conexión y operaciones CRUD
"""
from supabase import create_client, Client
import streamlit as st


class SupabaseClient:
    """Cliente para interactuar con Supabase"""
    
    _instance = None
    _client: Client = None
    
    def __new__(cls):
        """Singleton para asegurar una única instancia del cliente"""
        if cls._instance is None:
            cls._instance = super(SupabaseClient, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Inicializa la conexión con Supabase"""
        if self._client is None:
            # Obtener las credenciales de st.secrets
            try:
                supabase_url = st.secrets["supabase"]["url"]
                supabase_key = st.secrets["supabase"]["key"]
            except (KeyError, FileNotFoundError):
                raise ValueError(
                    "Las credenciales de Supabase no están configuradas. "
                    "Por favor configura SUPABASE_URL y SUPABASE_KEY en .streamlit/secrets.toml"
                )
            
            if not supabase_url or not supabase_key:
                raise ValueError(
                    "Las credenciales de Supabase no pueden estar vacías. "
                    "Por favor configura SUPABASE_URL y SUPABASE_KEY en .streamlit/secrets.toml"
                )
            
            self._client = create_client(supabase_url, supabase_key)
    
    @property
    def client(self) -> Client:
        """Retorna el cliente de Supabase"""
        return self._client
    
    def select(self, table: str, columns: str = "*"):
        """
        Realiza una consulta SELECT
        
        Args:
            table: Nombre de la tabla
            columns: Columnas a seleccionar (por defecto todas)
        
        Returns:
            Query builder de Supabase
        """
        return self._client.table(table).select(columns)
    
    def insert(self, table: str, data: dict):
        """
        Inserta un nuevo registro
        
        Args:
            table: Nombre de la tabla
            data: Diccionario con los datos a insertar
        
        Returns:
            Respuesta de Supabase
        """
        return self._client.table(table).insert(data).execute()
    
    def update(self, table: str, data: dict, match: dict):
        """
        Actualiza registros existentes
        
        Args:
            table: Nombre de la tabla
            data: Diccionario con los datos a actualizar
            match: Diccionario con las condiciones de búsqueda
        
        Returns:
            Respuesta de Supabase
        """
        query = self._client.table(table).update(data)
        for key, value in match.items():
            query = query.eq(key, value)
        return query.execute()
    
    def delete(self, table: str, match: dict):
        """
        Elimina registros
        
        Args:
            table: Nombre de la tabla
            match: Diccionario con las condiciones de búsqueda
        
        Returns:
            Respuesta de Supabase
        """
        query = self._client.table(table).delete()
        for key, value in match.items():
            query = query.eq(key, value)
        return query.execute()


def get_supabase_client() -> SupabaseClient:
    """
    Función helper para obtener la instancia del cliente Supabase
    
    Returns:
        SupabaseClient: Instancia del cliente
    """
    return SupabaseClient()
