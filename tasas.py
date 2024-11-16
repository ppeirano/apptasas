import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fredapi import Fred
from datetime import datetime, timedelta

# Configuración de la clave de API de FRED
fred = Fred(api_key='f5c520998557f7aec96adf6284098978')

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
        tasas_bonos[plazo] = fred.get_series(serie_id)

    tasas_fed = fred.get_series('FEDFUNDS')
    return tasas_bonos, tasas_fed

# Cargar los datos
tasas_bonos, tasas_fed = descargar_datos()

# Configuración de la interfaz de Streamlit
st.title('Curvas de Rendimiento de Bonos del Tesoro de EE. UU.')
st.write('Comparación de la curva de rendimiento y visualización de la tasa de los fondos federales.')

# Controles para seleccionar fechas (ahora "Desde" y "Hasta")
col1, col2 = st.columns(2)

with col1:
    fecha_comparar = st.date_input('Seleccione la fecha Desde (Naranja)', datetime.today() - timedelta(days=30))

with col2:
    fecha_actual = st.date_input('Seleccione la fecha Hasta (Azul)', datetime.today())

# Convertir fechas seleccionadas a strings
fecha_actual_str = fecha_actual.strftime('%Y-%m-%d')
fecha_comparar_str = fecha_comparar.strftime('%Y-%m-%d')

# Filtrar datos entre las fechas seleccionadas
tasas_bonos_filtradas = {
    plazo: data.loc[fecha_comparar:fecha_actual] for plazo, data in tasas_bonos.items()
}
tasas_fed_filtrada = tasas_fed.loc[fecha_comparar:fecha_actual]

# Gráfico de las curvas de rendimiento
fig1, ax1 = plt.subplots()

# Curvas de rendimiento para las dos fechas seleccionadas
datos_actuales = {plazo: data.loc[:fecha_actual].iloc[-1] for plazo, data in tasas_bonos.items() if not data.loc[:fecha_actual].empty}
datos_comparados = {plazo: data.loc[:fecha_comparar].iloc[-1] for plazo, data in tasas_bonos.items() if not data.loc[:fecha_comparar].empty}

# Graficar las curvas
ax1.plot(list(datos_actuales.keys()), list(datos_actuales.values()), marker='o', label=f'Curva {fecha_actual_str}')
ax1.plot(list(datos_comparados.keys()), list(datos_comparados.values()), marker='o', label=f'Curva {fecha_comparar_str}')

# Líneas horizontales para las tasas de la Fed
tasa_fed_actual = tasas_fed.loc[:fecha_actual].iloc[-1] if not tasas_fed.loc[:fecha_actual].empty else None
tasa_fed_comparada = tasas_fed.loc[:fecha_comparar].iloc[-1] if not tasas_fed.loc[:fecha_comparar].empty else None

if tasa_fed_actual is not None:
    ax1.axhline(y=tasa_fed_actual, color='blue', linestyle='--', label=f'Tasa Fed {fecha_actual_str}: {tasa_fed_actual:.2f}%')
if tasa_fed_comparada is not None:
    ax1.axhline(y=tasa_fed_comparada, color='orange', linestyle='--', label=f'Tasa Fed {fecha_comparar_str}: {tasa_fed_comparada:.2f}%')

# Configuración del gráfico
ax1.set_xlabel('Plazo')
ax1.set_ylabel('Rendimiento (%)')
ax1.legend()
ax1.grid(True)

# Mostrar el gráfico en Streamlit
st.pyplot(fig1)

# Gráfico de boxplot
fig2, ax2 = plt.subplots()

# Preparar los datos para el boxplot
boxplot_data = [data.dropna().values for data in tasas_bonos_filtradas.values()]
boxplot_labels = list(tasas_bonos_filtradas.keys())

# Agregar la tasa de la Fed al boxplot
if not tasas_fed_filtrada.empty:
    boxplot_data.append(tasas_fed_filtrada.dropna().values)
    boxplot_labels.append('Tasa Fed')

# Crear el boxplot (orientación vertical)
ax2.boxplot(boxplot_data, labels=boxplot_labels)

# Agregar puntos rojos para los valores actuales
for i, (plazo, data) in enumerate(tasas_bonos.items(), start=1):
    if plazo in datos_actuales:
        ax2.plot(i, datos_actuales[plazo], 'ro')  # Valor actual en rojo
        ax2.plot(i, datos_comparados[plazo], color='orange', marker='o')  # Valor comparado en azul

# Agregar el valor actual de la tasa Fed
if tasa_fed_actual is not None:
    ax2.plot(len(boxplot_labels), tasa_fed_actual, 'ro')  # Último valor de la tasa Fed

# Configuración del gráfico
ax2.set_ylabel('Rendimiento (%)')
ax2.set_xlabel('Instrumentos')
ax2.set_title('Distribución de las tasas entre las fechas seleccionadas')

# Mostrar el gráfico de boxplot en Streamlit
st.pyplot(fig2)
