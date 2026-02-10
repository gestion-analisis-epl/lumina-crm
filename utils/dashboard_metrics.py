"""
Cálculo de métricas para el Dashboard
"""
import pandas as pd
from datetime import datetime


class MetricsCalculator:
    """Calculador de métricas del dashboard"""
    
    def __init__(self, citas_data, prospeccion_data, proyectos_data, metas_data):
        """
        Inicializa el calculador de métricas
        
        Args:
            citas_data: DataFrame de citas
            prospeccion_data: DataFrame de prospección
            proyectos_data: DataFrame de proyectos
            metas_data: DataFrame de metas
        """
        self.citas_data = citas_data
        self.prospeccion_data = prospeccion_data
        self.proyectos_data = proyectos_data
        self.metas_data = metas_data
    
    def metricas_principales(self, citas_filtradas, prospeccion_filtrada, proyectos_filtrados):
        """
        Calcula las métricas principales del dashboard
        
        Returns:
            dict: Diccionario con las métricas principales
        """
        total_citas = len(citas_filtradas)
        total_prospectos = len(prospeccion_filtrada)
        total_proyectos = len(proyectos_filtrados)
        
        # Calcular ticket promedio
        vendidos = proyectos_filtrados[
            (proyectos_filtrados['status'] == 'Vendido') |
            (proyectos_filtrados['status'] == 'Ganado')
        ] if 'status' in proyectos_filtrados.columns else proyectos_filtrados.iloc[0:0]
        
        ticket_promedio = vendidos['total'].sum() / len(vendidos) if len(vendidos) > 0 else 0
        
        # Calcular total cartera
        total_cartera = proyectos_filtrados['total'].sum() if proyectos_filtrados.shape[0] > 0 else 0
        
        return {
            'total_citas': total_citas,
            'total_prospectos': total_prospectos,
            'total_proyectos': total_proyectos,
            'ticket_promedio': ticket_promedio,
            'total_cartera': total_cartera
        }
    
    def metricas_citas_semanales(self, fecha_inicio, fecha_fin, asesor_seleccionado):
        """
        Calcula las métricas de citas semanales
        
        Returns:
            dict: Diccionario con métricas de citas semanales
        """
        if 'fecha_dt' in self.citas_data.columns or 'fecha' in self.citas_data.columns:
            citas_con_fecha = self.citas_data.copy()
            if 'fecha_dt' not in citas_con_fecha.columns:
                citas_con_fecha['fecha_dt'] = pd.to_datetime(
                    citas_con_fecha['fecha'], dayfirst=True, errors='coerce'
                )
            
            # Aplicar filtros
            citas_analisis = citas_con_fecha.copy()
            if fecha_inicio is not None and fecha_fin is not None:
                fecha_inicio_dt = pd.to_datetime(fecha_inicio)
                fecha_fin_dt = pd.to_datetime(fecha_fin)
                mask = (
                    (citas_analisis['fecha_dt'].notna()) &
                    (citas_analisis['fecha_dt'] >= fecha_inicio_dt) &
                    (citas_analisis['fecha_dt'] <= fecha_fin_dt)
                )
                citas_analisis = citas_analisis[mask]
            
            if asesor_seleccionado and asesor_seleccionado != "Todos":
                citas_analisis = citas_analisis[
                    citas_analisis['asesor'].astype(str).str.strip() == asesor_seleccionado
                ]
            
            # Calcular semana del año
            citas_analisis['semana'] = citas_analisis['fecha_dt'].dt.isocalendar().week
            citas_analisis['ano'] = citas_analisis['fecha_dt'].dt.year
            
            # Contar citas por asesor y semana
            citas_por_semana = citas_analisis.groupby(['asesor', 'ano', 'semana']).size().reset_index(name='citas')
            
            # Calcular promedio
            promedio_general = citas_por_semana['citas'].mean() if len(citas_por_semana) > 0 else 0
            
            # Determinar meta
            meta_citas = 20 if asesor_seleccionado == "Todos" else 5
            
            # Calcular porcentaje de cumplimiento
            porcentaje = (promedio_general / meta_citas) * 100 if meta_citas > 0 else 0
            delta_text = f"{porcentaje:.0f}% cumplimiento"
            
            # Determinar color según cumplimiento
            if porcentaje >= 120:
                delta_color = "normal"
            elif porcentaje >= 100:
                delta_color = "normal"
            elif porcentaje >= 60:
                delta_color = "off"
            else:
                delta_color = "inverse"
            
            # Total de semanas analizadas
            semanas_unicas = citas_por_semana[['ano', 'semana']].drop_duplicates()
            total_semanas = len(semanas_unicas)
            
            return {
                'promedio_general': promedio_general,
                'delta_text': delta_text,
                'delta_color': delta_color,
                'total_semanas': total_semanas
            }
        
        return None
    
    def metricas_proyectos_por_estado(self, proyectos_filtrados):
        """
        Calcula las métricas de proyectos por estado
        
        Returns:
            dict: Diccionario con métricas por estado
        """
        proyectos_proceso = proyectos_filtrados[
            proyectos_filtrados['status'] == 'En Proceso'
        ]['total'].sum() if 'status' in proyectos_filtrados.columns else 0
        
        proyectos_ganados = proyectos_filtrados[
            proyectos_filtrados['status'] == 'Ganado'
        ]['total'].sum() if 'status' in proyectos_filtrados.columns else 0
        
        proyectos_perdidos = proyectos_filtrados[
            proyectos_filtrados['status'] == 'Perdido'
        ]['total'].sum() if 'status' in proyectos_filtrados.columns else 0
        
        return {
            'proyectos_proceso': proyectos_proceso,
            'proyectos_ganados': proyectos_ganados,
            'proyectos_perdidos': proyectos_perdidos
        }
    
    def metricas_ventas_cotizaciones(self, proyectos_filtrados, asesor_seleccionado, todos_asesores, fecha_inicio=None, fecha_fin=None):
        """
        Calcula las métricas de ventas y cotizaciones
        
        Args:
            proyectos_filtrados: DataFrame de proyectos filtrados
            asesor_seleccionado: Asesor seleccionado en filtros
            todos_asesores: Lista de todos los asesores
            fecha_inicio: Fecha de inicio del filtro (opcional)
            fecha_fin: Fecha de fin del filtro (opcional)
        
        Returns:
            dict: Diccionario con métricas de ventas y cotizaciones
        """
        # Si hay filtros de fecha, usar esos; si no, usar mes actual
        if fecha_inicio is not None and fecha_fin is not None:
            # Convertir a datetime para extraer mes y año
            fecha_inicio_dt = pd.to_datetime(fecha_inicio)
            fecha_fin_dt = pd.to_datetime(fecha_fin)
            
            # Determinar los meses involucrados en el rango
            if len(self.metas_data) > 0:
                # Filtrar metas para todos los meses en el rango
                meses_en_rango = []
                fecha_actual = fecha_inicio_dt
                while fecha_actual <= fecha_fin_dt:
                    meses_en_rango.append((fecha_actual.month, fecha_actual.year))
                    # Avanzar al siguiente mes
                    if fecha_actual.month == 12:
                        fecha_actual = fecha_actual.replace(year=fecha_actual.year + 1, month=1, day=1)
                    else:
                        fecha_actual = fecha_actual.replace(month=fecha_actual.month + 1, day=1)
                
                # Filtrar metas para los meses en el rango
                metas_filtradas = self.metas_data[
                    self.metas_data.apply(
                        lambda row: (int(row['mes']), int(row['ano'])) in meses_en_rango,
                        axis=1
                    )
                ].copy() if len(meses_en_rango) > 0 else pd.DataFrame()
            else:
                metas_filtradas = pd.DataFrame()
        else:
            # Sin filtros, usar mes actual
            fecha_actual = datetime.now()
            mes_actual = fecha_actual.month
            anio_actual = fecha_actual.year
            
            if len(self.metas_data) > 0:
                metas_filtradas = self.metas_data[
                    (self.metas_data['mes'].astype(int) == mes_actual) &
                    (self.metas_data['ano'].astype(int) == anio_actual)
                ].copy()
            else:
                metas_filtradas = pd.DataFrame()
        
        # Obtener asesores a analizar
        asesores_analizar = [asesor_seleccionado] if asesor_seleccionado != "Todos" else todos_asesores
        
        # Calcular totales agregados
        meta_total = 0
        ventas_totales = 0
        cotizaciones_totales = 0
        
        for asesor in asesores_analizar:
            # Obtener meta del asesor (sumar todas las metas del rango)
            meta_asesor = metas_filtradas[
                metas_filtradas['asesor'].astype(str).str.strip() == asesor
            ]['meta'].sum() if len(metas_filtradas) > 0 else 0
            meta_total += meta_asesor
            
            # Calcular ventas
            ventas_asesor = proyectos_filtrados[
                (proyectos_filtrados['asesor'].astype(str).str.strip() == asesor) &
                ((proyectos_filtrados['status'] == 'Vendido') | 
                 (proyectos_filtrados['status'] == 'Ganado'))
            ]['total'].sum() if len(proyectos_filtrados) > 0 else 0
            ventas_totales += ventas_asesor
            
            # Calcular cotizaciones
            cotizaciones_asesor = proyectos_filtrados[
                proyectos_filtrados['asesor'].astype(str).str.strip() == asesor
            ]['total'].sum() if len(proyectos_filtrados) > 0 else 0
            cotizaciones_totales += cotizaciones_asesor
        
        # Calcular porcentajes y deltas
        if meta_total > 0:
            porcentaje_ventas = (ventas_totales / meta_total) * 100
            faltante = meta_total - ventas_totales
            delta_ventas = f"Falta: ${faltante:,.2f}" if faltante > 0 else f"Superó: ${abs(faltante):,.2f}"
            color_ventas = "normal" if porcentaje_ventas >= 100 else "inverse"
        else:
            porcentaje_ventas = 0
            delta_ventas = "Sin meta definida"
            color_ventas = "off"
        
        # Meta de cotizaciones (10x la meta de ventas)
        meta_cotizaciones = meta_total * 10
        if meta_cotizaciones > 0:
            porcentaje_cotizaciones = (cotizaciones_totales / meta_cotizaciones) * 100
            faltante_cot = meta_cotizaciones - cotizaciones_totales
            delta_cot = f"Falta: ${faltante_cot:,.2f}" if faltante_cot > 0 else f"Superó: ${abs(faltante_cot):,.2f}"
            color_cot = "normal" if porcentaje_cotizaciones >= 100 else "inverse"
        else:
            porcentaje_cotizaciones = 0
            delta_cot = "Sin meta definida"
            color_cot = "off"
        
        return {
            'meta_total': meta_total,
            'ventas_totales': ventas_totales,
            'cotizaciones_totales': cotizaciones_totales,
            'delta_ventas': delta_ventas,
            'color_ventas': color_ventas,
            'delta_cot': delta_cot,
            'color_cot': color_cot
        }
    
    def metricas_ventas_trimestrales(self, proyectos_filtrados):
        """
        Calcula las métricas de ventas trimestrales agregadas de todos los asesores
        
        Returns:
            dict: Diccionario con métricas de ventas trimestrales
        """
        fecha_actual = datetime.now()
        mes_actual = fecha_actual.month
        anio_actual = fecha_actual.year
        
        # Determinar el trimestre actual
        if mes_actual in [1, 2, 3]:
            trimestre_actual = 1
            meses_trimestre = [1, 2, 3]
        elif mes_actual in [4, 5, 6]:
            trimestre_actual = 2
            meses_trimestre = [4, 5, 6]
        elif mes_actual in [7, 8, 9]:
            trimestre_actual = 3
            meses_trimestre = [7, 8, 9]
        else:
            trimestre_actual = 4
            meses_trimestre = [10, 11, 12]
        
        # Filtrar metas del trimestre actual
        if len(self.metas_data) > 0:
            metas_trimestre = self.metas_data[
                (self.metas_data['mes'].astype(int).isin(meses_trimestre)) &
                (self.metas_data['ano'].astype(int) == anio_actual)
            ].copy()
        else:
            metas_trimestre = pd.DataFrame()
        
        # Sumar todas las metas del trimestre de todos los asesores
        meta_trimestre_total = metas_trimestre['meta'].sum() if len(metas_trimestre) > 0 else 0
        
        # Filtrar proyectos vendidos del trimestre actual
        proyectos_con_fecha = proyectos_filtrados.copy()
        
        # Asegurar que tenemos la columna de fecha
        if 'fecha_dt' not in proyectos_con_fecha.columns:
            if 'fecha' in proyectos_con_fecha.columns:
                proyectos_con_fecha['fecha_dt'] = pd.to_datetime(
                    proyectos_con_fecha['fecha'], dayfirst=True, errors='coerce'
                )
            elif 'fecha_cotizacion' in proyectos_con_fecha.columns:
                proyectos_con_fecha['fecha_dt'] = pd.to_datetime(
                    proyectos_con_fecha['fecha_cotizacion'], errors='coerce'
                )
        
        # Filtrar ventas del trimestre actual (vendidos o ganados)
        if 'fecha_dt' in proyectos_con_fecha.columns:
            proyectos_con_fecha['mes'] = proyectos_con_fecha['fecha_dt'].dt.month
            proyectos_con_fecha['ano'] = proyectos_con_fecha['fecha_dt'].dt.year
            
            ventas_trimestre = proyectos_con_fecha[
                (proyectos_con_fecha['mes'].isin(meses_trimestre)) &
                (proyectos_con_fecha['ano'] == anio_actual) &
                ((proyectos_con_fecha['status'] == 'Vendido') | 
                 (proyectos_con_fecha['status'] == 'Ganado'))
            ] if 'status' in proyectos_con_fecha.columns else proyectos_con_fecha.iloc[0:0]
            
            ventas_trimestre_total = ventas_trimestre['total'].sum() if len(ventas_trimestre) > 0 else 0
        else:
            ventas_trimestre_total = 0
        
        # Calcular porcentaje y delta
        if meta_trimestre_total > 0:
            porcentaje_ventas = (ventas_trimestre_total / meta_trimestre_total) * 100
            faltante = meta_trimestre_total - ventas_trimestre_total
            delta_ventas = f"{porcentaje_ventas:.1f}% - Falta: ${faltante:,.2f}" if faltante > 0 else f"{porcentaje_ventas:.1f}% - Superó: ${abs(faltante):,.2f}"
            color_ventas = "normal" if porcentaje_ventas >= 100 else "inverse"
        else:
            porcentaje_ventas = 0
            delta_ventas = "Sin meta definida"
            color_ventas = "off"
        
        return {
            'trimestre_actual': trimestre_actual,
            'meta_trimestre_total': meta_trimestre_total,
            'ventas_trimestre_total': ventas_trimestre_total,
            'porcentaje_ventas': porcentaje_ventas,
            'delta_ventas': delta_ventas,
            'color_ventas': color_ventas
        }
