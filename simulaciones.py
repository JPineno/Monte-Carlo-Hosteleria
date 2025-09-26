import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Funciones para leer los datos desde archivos Excel
def leer_excel_ventas(ruta_excel='datos/ventas_grupos_productos_costes.xlsx'):
    """
    Lee los datos desde el archivo Excel preparado para las ventas del año,
    y devuelve un DataFrame con los datos en cada mes del año.
    """
    df = pd.read_excel(ruta_excel, sheet_name='ventas', index_col=0)

    # Eliminar los meses que no tienen datos
    df = df.dropna(axis=0, how="all")
    return df

def leer_excel_grupos(ruta_excel='datos/ventas_grupos_productos_costes.xlsx'):
    """
    Lee los datos desde el archivo Excel preparado para los grupos de productos,
    y devuelve un DataFrame con el nivel de demanda de cada grupo en cada mes del año.
    """
    df = pd.read_excel(ruta_excel, sheet_name='grupos', index_col=0)

    # Eliminar los meses que no tienen datos
    df = df.dropna(axis=1, how="all")
    return df

def leer_excel_productos(ruta_excel='datos/ventas_grupos_productos_costes.xlsx'):
    """
    Lee los datos desde el archivo Excel preparado para los productos,
    y devuelve un DataFrame con:
    - 'Producto'
    - 'Grupo'
    - 'Beneficio unitario'
    - 'Nivel de demanda dentro del grupo'
    """
    df = pd.read_excel(ruta_excel, sheet_name='productos', index_col=0)
    return df

def leer_excel_costes(ruta_excel='datos/ventas_grupos_productos_costes.xlsx'):
    """
    Lee los datos desde el archivo Excel preparado para los costes,
    y devuelve un DataFrame con el total de cada coste en cada mes del año.
    """
    df = pd.read_excel(ruta_excel, sheet_name='costes', index_col=0)

    # Eliminar los meses que no tienen datos
    df = df.dropna(axis=1, how="all")
    return df

# Función para simular la demanda de cada grupo de productos
# en cada mes del año
def simular_demanda_grupos(num_sims=1000000):
    """
    Simula la demanda (en porcentaje del total) de cada grupo de productos en cada mes del año, utilizando
    distribuciones uniformes que parten del nivel de demanda establecido en el Excel.
    
    Parámetros:
    - num_sims: número de simulaciones a realizar para cada grupo en cada mes.
    
    Devuelve:
    - demanda_grupos: un DataFrame con la demanda simulada de cada grupo en
    cada mes, partiendo del nivel de demanda establecido en el documento de Excel,
    y con el número de simulaciones establecido.
    """
    df_grupos = leer_excel_grupos()
    meses = df_grupos.columns
    grupos = df_grupos.index

    # Calcular el peso de cada grupo en la demanda total
    fraccion_grupos = df_grupos.div(df_grupos.sum(axis=0), axis=1)
    
    # Construir un DataFrame de simulaciones
    demanda_grupos = pd.DataFrame({(grupo, mes): np.random.uniform(low=fraccion_grupos.loc[grupo, mes]*0.5,
                                    high=fraccion_grupos.loc[grupo, mes]*1.5,
                                    size=num_sims) for grupo in grupos for mes in meses})
            
    return demanda_grupos

# Función para simular la demanda de cada producto
# en cada mes del año
def simular_demanda_productos(num_sims=1000000):
    """
    Simula la demanda (en porcentaje del total) de cada producto en cada mes del año.
    
     Parámetros:
    - num_sims: número de simulaciones a realizar para cada producto en cada mes.
    
    Devuelve:
    - demanda_productos: un DataFrame con la demanda simulada de cada producto en
    cada mes, partiendo de las simulaciones de demanda de los grupos establecidas
    en la función "simular_demanda_grupos()", y con el número de simulaciones establecido.
    - df_productos: un DataFrame con la información de la página del Excel dedicada
    a los productos, pero con una columna adicional que refleja el peso de cada producto
    en la demanda total.
    """
    df_productos = leer_excel_productos()
    meses = leer_excel_grupos().columns
    productos = df_productos.index

    # Obtener la demanda de cada grupo
    demanda_grupos = simular_demanda_grupos(num_sims=num_sims)

    # Sacar el peso de cada producto dentro de su grupo
    df_productos['fraccion'] = (df_productos.groupby('grupo')['nivel_demanda_dentro_de_grupo'].transform(lambda x: x / x.sum()))

    # Construir un DataFrame de simulaciones
    demanda_productos = pd.DataFrame({(producto, mes): (np.random.uniform(
        low=(demanda_grupos[(grupo := df_productos.loc[producto, 'grupo']), mes] * df_productos.loc[producto, 'fraccion'] * 0.9),
        high=(demanda_grupos[grupo, mes] * df_productos.loc[producto, 'fraccion'] * 1.1),
        size=num_sims)) for producto in productos for mes in meses})

    return demanda_productos, df_productos

# Función para obtener los ingresos y las ventas mensuales por producto,
# partiendo de los datos de ingresos y precios del Excel, y de
# las suposiciones de demanda por cada producto, para sacar las unidades vendidas
def obtener_ventas_productos():
    """
    Obtiene las ventas de cada producto en cada mes del año.
    
    Devuelve:
    - ingresos_productos: un DataFrame con los ingresos generados por cada producto
    en cada mes, dados los datos de ventas en el Excel, los pesos de cada
    producto sobre el total estimados con "simular_demanda_productos()", y los
    precios de cada producto.
    - ventas_productos: un DataFrame con las ventas de cada producto
    en cada mes, dados los datos de ventas en el Excel, los pesos de cada
    producto sobre el total estimados con "simular_demanda_productos()", y los
    precios de cada producto.
    """
    df_productos = simular_demanda_productos()[1]
    meses = leer_excel_ventas().index
    ventas_totales = leer_excel_ventas()['ventas_totales']
    pesos = df_productos['fraccion']
    precios = df_productos['precio']

    # Sacar la parte de los ingresos generada por cada producto, según su peso
    ingresos_productos = pd.DataFrame({mes: ventas_totales.loc[mes] * pesos for mes in meses}, index=pesos.index)

    # Obtener las ventas de cada producto, dividiendo los ingresos entre el precio
    ventas_productos = ingresos_productos.div(precios, axis=0)

    return ingresos_productos, ventas_productos

# Función para obtener los ingresos y beneficios totales mensuales,
# partiendo de los datos de ventas obtenidos anteriormente
def obtener_ingresos_beneficios_mensuales():
    """
    Agrega los ingresos y beneficios unitarios de cada producto en cada mes del año, para
    obtener los ingesos y beneficios unitarios totales, y poder ver cómo se comparan con los
    datos reales observados (para comprobar las estimaciones de demanda).
    
    Devuelve:
    - ingresos_simulados: una Serie con los ingresos totales mensuales,
    simulados a partir de las estimaciones generadas con "obtener_ventas_productos()".
    - beneficios_simulados: una Serie con los beneficios totales mensuales,
    simulados a partir de las estimaciones generadas con "obtener_ventas_productos()".
    """
    ingresos_prod, ventas_prod = obtener_ventas_productos()
    beneficios_ud = leer_excel_productos()['precio'] - leer_excel_productos()['coste_unitario']
    meses = ingresos_prod.columns

    # Sumar los ingresos de cada producto en cada mes
    ingresos_simulados = pd.Series({mes: ingresos_prod[mes].sum() for mes in meses})

    # Obtener los beneficios unitarios totales en cada mes
    beneficios_simulados = pd.Series({mes: (beneficios_ud * ventas_prod[mes]).sum() for mes in meses})

    return ingresos_simulados, beneficios_simulados