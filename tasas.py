import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fredapi import Fred
from datetime import datetime, timedelta

# Configuración de la clave de API de FRED
fred = Fred(api_key='f5c520998557f7aec96adf6284098978')

# Fechas de inicio y fin para descargar los datos históricos
fecha_fin = datetime.today()
fecha_inicio = fecha_fin - timedelta(days=365 * 2)  # Últimos 2 años de datos

# Descargar todos los datos de una sola vez
@st.cache_data
def descargar_datos():
    series_ids = {
        '1M': 'DGS1MO',
        '3M': 'DGS3MO',
        '6M': 'DGS6MO',
        '1A': 'DGS1',
        '2A': 'DGS2',
        '3A': 'DGS3',
        '5A': 'DGS5',
        '7A': 'DGS7',
        '10A': 'DGS10',
        '20A': 'DGS20',
        '30A': 'DGS30'
    }
    tasas_bonos = {}
    for plazo, serie_id in series_ids.items():
        tasas_bonos[plazo] = fred.get_series(serie_id, start=fecha_inicio, end=fecha_fin)

    tasas_fed = fred.get_series('FEDFUNDS', start=fecha_inicio, end=fecha_fin)
    return tasas_bonos, tasas_fed

# Cargar los datos
tasas_bonos, tasas_fed = descargar_datos()

# Función para obtener datos para una fecha específica
def obtener_datos_para_fecha(datos, fecha):
    return {plazo: datos[plazo].loc[:fecha].iloc[-1] for plazo in datos if not datos[plazo].loc[:fecha].empty}

# Función para obtener la última tasa de la Fed para una fecha específica
def obtener_tasa_fed_para_fecha(datos, fecha):
    try:
        return datos.loc[:fecha].iloc[-1]
    except IndexError:
        return None

# Configuración de la interfaz de Streamlit
st.title('Curvas de Rendimiento de Bonos del Tesoro de EE. UU.')
st.write('Comparación de la curva actual con una fecha seleccionada y visualización de la tasa de los fondos federales.')

# Fecha por defecto: actual menos 30 días
fecha_por_defecto = datetime.today() - timedelta(days=30)
fecha_seleccionada = st.date_input('Seleccione una fecha para comparar', fecha_por_defecto)

# Fechas utilizadas
fecha_actual = datetime.today()
fecha_actual_str = fecha_actual.strftime('%Y-%m-%d')
fecha_comparar_str = fecha_seleccionada.strftime('%Y-%m-%d')

# Obtener datos para las fechas seleccionadas
datos_actuales = obtener_datos_para_fecha(tasas_bonos, fecha_actual)
datos_seleccionados = obtener_datos_para_fecha(tasas_bonos, fecha_seleccionada)

tasa_fed_actual = obtener_tasa_fed_para_fecha(tasas_fed, fecha_actual)
tasa_fed_seleccionada = obtener_tasa_fed_para_fecha(tasas_fed, fecha_seleccionada)

# Conversión a DataFrame para facilitar la manipulación
df_actual = pd.DataFrame(list(datos_actuales.items()), columns=['Plazo', 'Rendimiento'])
df_seleccionado = pd.DataFrame(list(datos_seleccionados.items()), columns=['Plazo', 'Rendimiento'])

# Reemplazo de NaN por 0 en los valores de rendimiento
df_actual['Rendimiento'] = df_actual['Rendimiento'].fillna(0)
df_seleccionado['Rendimiento'] = df_seleccionado['Rendimiento'].fillna(0)

# Gráfico de las curvas de rendimiento
fig, ax = plt.subplots()

# Curvas de rendimiento
ax.plot(df_actual['Plazo'], df_actual['Rendimiento'], label=f'Curva Actual ({fecha_actual_str})', marker='o')
ax.plot(df_seleccionado['Plazo'], df_seleccionado['Rendimiento'], label=f'Curva {fecha_comparar_str}', marker='o')

# Líneas horizontales para las tasas de la Fed
if tasa_fed_actual is not None:
    ax.axhline(y=tasa_fed_actual, color='blue', linestyle='--', label=f'Tasa Fed Actual: {tasa_fed_actual}%')
if tasa_fed_seleccionada is not None:
    ax.axhline(y=tasa_fed_seleccionada, color='orange', linestyle='--', label=f'Tasa Fed {fecha_comparar_str}: {tasa_fed_seleccionada}%')

# Ajustar el rango del eje Y para incluir las tasas de la Fed
max_rendimiento = max(
    df_actual['Rendimiento'].max(),
    df_seleccionado['Rendimiento'].max(),
    tasa_fed_actual or 0,
    tasa_fed_seleccionada or 0
)
ax.set_ylim(0, max_rendimiento + 1)

# Configuración de ejes y leyendas
ax.set_xlabel('Plazo')
ax.set_ylabel('Rendimiento (%)')
ax.legend()
ax.grid(True)

# Mostrar el gráfico en Streamlit
st.pyplot(fig)
