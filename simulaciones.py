import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# Funciones para leer los datos desde el archivo Excel
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
    Simula la demanda (en porcentaje) de cada grupo de productos en cada mes del año, utilizando
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
    Simula la demanda (en porcentaje) de cada producto en cada mes del año.
    
     Parámetros:
    - num_sims: número de simulaciones a realizar para cada producto en cada mes.
    
    Devuelve:
    - demanda_productos: un DataFrame con la demanda simulada de cada producto en
    cada mes, partiendo de las simulaciones de demanda de los grupos establecidas
    en la función "simular_demanda_grupos", y con el número de simulaciones establecido.
    """
    df_productos = leer_excel_productos()
    meses = leer_excel_grupos().columns
    productos = df_productos.index
    grupos = df_productos['grupo'].unique()

    # Obtener la demanda de cada grupo
    demanda_grupos = simular_demanda_grupos(num_sims=num_sims)

    # Sacar el peso de cada producto dentro de su grupo
    df_productos['fraccion'] = (df_productos.groupby('grupo')['nivel_demanda_dentro_de_grupo'].transform(lambda x: x / x.sum()))

    # Construir un DataFrame de simulaciones
    demanda_productos = pd.DataFrame({(producto, mes): (np.random.uniform(
        low=(demanda_grupos[(grupo := df_productos.loc[producto, 'grupo']), mes] * df_productos.loc[producto, 'fraccion'] * 0.9),
        high=(demanda_grupos[grupo, mes] * df_productos.loc[producto, 'fraccion'] * 1.1),
        size=num_sims)) for producto in productos for mes in meses})

    return demanda_productos