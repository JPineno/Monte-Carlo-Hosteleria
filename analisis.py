import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import simulaciones as sim

# Estimar los datos dadas las estimaciones de demanda y los datos en el Excel
ingresos, beneficios = sim.obtener_ingresos_beneficios_mensuales()

ingresos_prod = sim.obtener_ventas_productos()[0]
ingresos_productos_media = ingresos_prod.mean(axis=0)
ingresos_productos_std = ingresos_prod.std(axis=0)

ventas_prod = sim.obtener_ventas_productos()[1]
ventas_productos_media = ventas_prod.mean(axis=0)
ventas_productos_std = ventas_prod.std(axis=0)

# Realizar todas las simulaciones sobre los datos dados en el Excel
fracciones_grup = sim.simular_demanda_grupos()
fracciones_prod = sim.simular_demanda_productos()[0]
costes_ud = sim.simular_costes_unitarios()
costes_ind = sim.simular_costes_indirectos()
benef_prod = sim.simular_beneficios_mensuales()[0]
benef_total = sim.simular_beneficios_mensuales()[1]

fraccion_grupos_media = fracciones_grup.mean(axis=0).unstack(level=1, sort=False)
fraccion_grupos_std = fracciones_grup.std(axis=0).unstack(level=1, sort=False)

fraccion_productos_media = fracciones_prod.mean(axis=0).unstack(level=1, sort=False)
fraccion_productos_std = fracciones_prod.std(axis=0).unstack(level=1, sort=False)

beneficios_productos_media = benef_prod.mean(axis=0).unstack(level=1, sort=False)
beneficios_productos_std = benef_prod.std(axis=0).unstack(level=1, sort=False)