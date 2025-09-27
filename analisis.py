import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import textwrap
import simulaciones as sim

# Utilizar LaTeX para las gráficas si está disponible
try:
    plt.rcParams.update({
        "text.usetex": True,
        "font.family": "serif",
        "font.serif": ["Computer Modern"],
        "axes.labelsize": 12,
        "font.size": 12,
        "legend.fontsize": 10,
        "xtick.labelsize": 10,
        "ytick.labelsize": 10,
    })
except RuntimeError:
    plt.rcParams["text.usetex"] = False

# Obtener los ingresos reales del Excel
ingresos_reales = sim.leer_excel_ventas()

# Estimar los datos dadas las estimaciones de demanda y los datos en el Excel
ingresos, beneficios = sim.obtener_ingresos_beneficios_mensuales()

ingresos_prod = sim.obtener_ventas_productos()[0]
ingresos_productos_media = ingresos_prod.mean(axis=0)
ingresos_productos_std = ingresos_prod.std(axis=0)

ventas_prod = sim.obtener_ventas_productos()[1]
ventas_productos_media = ventas_prod.mean(axis=0)
ventas_productos_std = ventas_prod.std(axis=0)

fracciones_grup_reales = sim.simular_demanda_grupos()[1]
fracciones_prod_reales = sim.simular_demanda_productos()[1][['grupo', 'fraccion']]

# Realizar todas las simulaciones sobre los datos dados en el Excel
fracciones_grup = sim.simular_demanda_grupos()[1]
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

# Realizar las gráficas necesarias para el reporte

# Comparar los ingresos mensuales reales reflejados en el Excel y los ingresos
# que obtendríamos a partir de las estimaciones de demanda asumidas por el usuario
fig, ax = plt.subplots(figsize=(9, 5))

ax.plot(sim.leer_excel_ventas(), label='Ingresos observados', marker='o')
ax.plot(ingresos, label='Ingresos según estimaciones de demanda', marker='o')

ax.set_xlabel('Mes')
ax.set_ylabel('Ingresos (€)')
ax.set_title('Ingresos observados vs ingresos estimados según el nivel de demanda')
ax.legend(loc='upper left', bbox_to_anchor=(1,1))

fig.savefig('ingresos_vs_estimaciones.pdf', bbox_inches='tight')

# Crear un gráfico con los beneficios mensuales estimados
# a partir de las estimaciones de demanda asumidas por el usuario,
# y los datos de precios y costes registrados en el Excel
fig, ax = plt.subplots(figsize=(9, 5))

ax.plot(beneficios, marker='o')

ax.set_xlabel('Mes')
ax.set_ylabel('Beneficios (€)')
ax.set_title('Beneficios estimados según el nivel de demanda, precios, y costes')

fig.savefig("beneficios_estimados.pdf", bbox_inches="tight")

# Crear un gráfico con los porcentajes (fracciones) de demanda de
# cada grupo sobre el total cada mes
fig, ax = plt.subplots(figsize=(9,5))

fracciones_grup_reales.T.plot(kind='bar', stacked=True, ax=ax)

ax.set_ylabel('Porcentaje')
ax.set_xlabel('Mes')
ax.set_title('Porcentajes del total de demanda por grupo de producto')
plt.xticks(rotation=0)
ax.yaxis.set_major_formatter(PercentFormatter(1))
ax.legend(title='Grupo', bbox_to_anchor=(1, 1))

plt.tight_layout()
fig.savefig('porcentajes_grupos.pdf', bbox_inches='tight')

# Crear gráficos con los porcentajes (fracciones) de demanda de
# cada producto sobre el total de su grupo
grupos = fracciones_prod_reales['grupo'].unique()
for grupo in grupos:
    df_grupos = fracciones_prod_reales[fracciones_prod_reales['grupo'] == grupo].sort_values('fraccion', ascending=False)
    
    fig, ax = plt.subplots(figsize=(9,5))
    ax.bar(df_grupos.index, df_grupos['fraccion'])
    
    ax.set_ylabel('Porcentaje')
    ax.set_xlabel('Producto')
    ax.set_title(f'Porcentajes del total de demanda dentro del grupo: {grupo}')
    ax.tick_params(axis='x', rotation=45)
    ax.yaxis.set_major_formatter(PercentFormatter(1))
    
    plt.tight_layout()
    fig.savefig(f'porcentajes_productos_{grupo}.pdf', bbox_inches='tight')

# Crear un gráfico para los ingresos asociados a cada producto a lo largo del año
fig, ax = plt.subplots(figsize=(9, 5))

meses = ingresos_prod.columns
for producto in ingresos_prod.index:
    ax.plot(meses, ingresos_prod.loc[producto], marker='o', label=f'{producto}')

ax.set_xlabel('Mes')
ax.set_ylabel('Ingresos (€)')
ax.set_title('Ingresos por producto')
ax.legend(loc='upper left', bbox_to_anchor=(1,1))
plt.xticks(rotation=0)
plt.tight_layout()

fig.savefig('ingresos_prod.pdf', bbox_inches='tight')

# Crear un gráfico para las ventas de cada producto a lo largo del año
# (juntando los productos con las mismas ventas)
fig, ax = plt.subplots(figsize=(9, 5))

meses = ventas_prod.columns

vals_productos = {}
for producto in ventas_prod.index:
    vals_tuple = tuple(round(v) for v in ventas_prod.loc[producto])
    if vals_tuple in vals_productos:
        vals_productos[vals_tuple].append(producto)
    else:
        vals_productos[vals_tuple] = [producto]

for i, (vals_tuple, productos) in enumerate(vals_productos.items()):
    ax.plot(
        meses,
        list(vals_tuple),
        marker='o',
        linewidth=2,
        label=textwrap.fill((', '.join(productos)), width=15)
    )

ax.set_xlabel('Mes')
ax.set_ylabel('Ventas (unidades)')
ax.set_title('Ventas por producto')
plt.xticks(rotation=0)
ax.legend(loc='upper left', bbox_to_anchor=(1,1))
plt.tight_layout()

fig.savefig('ventas_prod.pdf', bbox_inches='tight')