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
# en cada mes del año, devolviendo tres escenarios distintos
def simular_demanda_grupos(num_sims=1000):
    """
    Simula la demanda (en porcentaje) de cada grupo de productos en cada mes del año, utilizando
    distribuciones uniformes que parten del nivel de demanda establecido en el Excel.
    
    Parámetros:
    - num_sims: número de simulaciones a realizar para cada grupo en cada mes.
    
    Devuelve:
    - demanda_grupos_base: un DataFrame con la demanda simulada de cada grupo en
    cada mes, partiendo de un escenario de base entorno al nivel de demanda establecido.
    - demanda_grupos_pos: un DataFrame con la demanda simulada de cada grupo en cada
    mes, partiendo de un escenario positivo respecto al nivel de demanda establecido.
    - demanda_grupos_neg: un DataFrame con la demanda simulada de cada grupo en cada
    mes, partiendo de un escenario negativo respecto al nivel de demanda establecido.
    """
    df_grupos = leer_excel_grupos()
    meses = df_grupos.columns
    grupos = df_grupos.index

    # Calcular el peso de cada grupo en la demanda total
    fraccion_grupos = pd.DataFrame(0, index=grupos, columns=meses)
    for grupo in grupos:
        for mes in meses:
            fraccion_grupos.loc[grupo, mes] =  df_grupos.loc[grupo, mes] / df_grupos[mes].sum()
    
    demanda_grupos_base = pd.DataFrame(0, index=grupos, columns=meses)
    demanda_grupos_pos = pd.DataFrame(0, index=grupos, columns=meses)
    demanda_grupos_neg = pd.DataFrame(0, index=grupos, columns=meses)
    for grupo in grupos:
        for mes in meses:
            nivel_demanda = fraccion_grupos.loc[grupo, mes]
            
            demanda_grupos_base.loc[grupo, mes] = np.random.uniform(low=nivel_demanda*0.7, high=nivel_demanda*1.3, size=num_sims).mean()
            demanda_grupos_pos.loc[grupo, mes] = np.random.uniform(low=nivel_demanda, high=nivel_demanda*1.4, size=num_sims).mean()
            demanda_grupos_neg.loc[grupo, mes] = np.random.uniform(low=nivel_demanda*0.6, high=nivel_demanda, size=num_sims).mean()
            
    return demanda_grupos_base, demanda_grupos_pos, demanda_grupos_neg

# Función para simular la demanda de cada producto
# en cada mes del año, devolviendo tres escenarios distintos
def simular_demanda_productos(num_sims=1000):
    """
    Simula la demanda (en porcentaje) de cada producto en cada mes del año, utilizando
    los datos del nivel de demanda de cada grupo, y de cada producto dentro de su grupo.
    
    Parámetros:
    - num_sims: número de simulaciones a realizar para cada producto en cada mes.
    
    Devuelve:
    - demanda_productos_base: un DataFrame con la demanda simulada de cada producto en
    cada mes, partiendo de un escenario de base entorno al nivel de demanda establecido.
    - demanda_productos_pos: un DataFrame con la demanda simulada de cada producto en cada
    mes, partiendo de un escenario positivo respecto al nivel de demanda establecido.
    - demanda_productos_neg: un DataFrame con la demanda simulada de cada producto en cada
    mes, partiendo de un escenario negativo respecto al nivel de demanda establecido.
    """
    df_productos = leer_excel_productos()
    meses = leer_excel_grupos().columns
    productos = df_productos.index
    grupos = df_productos['grupo'].unique()

    # Calcular la demanda de cada grupo, en cada escenario
    demanda_grupos_base, demanda_grupos_pos, demanda_grupos_neg = simular_demanda_grupos()

    # Calcular el peso de cada producto dentro de su grupo
    df_productos['fraccion'] = df_productos.groupby('grupo')['nivel_demanda_dentro_de_grupo'].transform(lambda x: x / x.sum())

    demanda_productos_base = pd.DataFrame(0, index=productos, columns=meses)
    demanda_productos_pos  = pd.DataFrame(0, index=productos, columns=meses)
    demanda_productos_neg  = pd.DataFrame(0, index=productos, columns=meses)

    for grupo in grupos:
        productos_grupo = df_productos[df_productos['grupo'] == grupo].index
        
        for producto in productos_grupo:
            fraccion = df_productos.loc[producto, 'fraccion']
            
            for mes in meses:
                nivel_base = demanda_grupos_base.loc[grupo, mes] * fraccion
                nivel_pos  = demanda_grupos_pos.loc[grupo, mes]  * fraccion
                nivel_neg  = demanda_grupos_neg.loc[grupo, mes]  * fraccion
                
                demanda_productos_base.loc[producto, mes] = np.random.uniform(low=nivel_base*0.9, high=nivel_base*1.1, size=num_sims).mean()
                demanda_productos_pos.loc[producto, mes] = np.random.uniform(low=nivel_pos*0.9, high=nivel_pos*1.2, size=num_sims).mean()
                demanda_productos_neg.loc[producto, mes] = np.random.uniform(low=nivel_neg*0.8, high=nivel_neg*1.1, size=num_sims).mean()

    return demanda_productos_base, demanda_productos_pos, demanda_productos_neg