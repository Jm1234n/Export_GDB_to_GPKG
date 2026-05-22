# extrae la lista de grupos de GDB y exporta cada grupo a un GPKG
# además exporta tablas (geometry = None) a un GPKG aparte

import subprocess
import re
import os
from osgeo import ogr

# Ruta de la GDB
gdb_path = r"D:\DESARROLLO\migracion de BD\BDP\GDB\BDP.gdb"

# Carpeta de salida
output_dir = r"D:\DESARROLLO\migracion de BD\BDP\exportacion de GDB\prueba"

# Crear carpeta si no existe
os.makedirs(output_dir, exist_ok=True)

# -----------------------------------------------------------------
# 1. Extraer grupos y capas usando ogrinfo
# -----------------------------------------------------------------
try:
    output = subprocess.check_output(
        ['ogrinfo', gdb_path],
        text=True,
        shell=True
    )
except Exception as e:
    print(f"Error al ejecutar ogrinfo: {e}")
    exit()

lines = output.splitlines()

grupos = []
capas_por_grupo = {}

grupo_actual = None

for line in lines:

    # Detectar grupo
    match_group = re.match(r'^Group\s+(\S+):', line)

    if match_group:
        grupo_actual = match_group.group(1)

        grupos.append(grupo_actual)
        capas_por_grupo[grupo_actual] = []

        continue

    # Detectar capas dentro del grupo
    if grupo_actual and re.match(r'^\s+Layer:', line):

        match_layer = re.search(r'Layer:\s+(\S+)', line)

        if match_layer:
            capas_por_grupo[grupo_actual].append(
                match_layer.group(1)
            )

# -----------------------------------------------------------------
# 2. Abrir GDB
# -----------------------------------------------------------------
ds = ogr.Open(gdb_path)

if ds is None:
    print(f"Error: no se pudo abrir la GDB {gdb_path}")
    exit()

# Driver GeoPackage
gpkg_drv = ogr.GetDriverByName('GPKG')

# -----------------------------------------------------------------
# 3. Detectar tablas (geometry = None)
# -----------------------------------------------------------------

# capas que YA están dentro de grupos
capas_en_grupos = set()

for lista_capas in capas_por_grupo.values():
    capas_en_grupos.update(lista_capas)

# grupo especial
grupo_tablas = "TABLAS"
capas_por_grupo[grupo_tablas] = []

# recorrer TODAS las capas de la GDB
for i in range(ds.GetLayerCount()):

    layer = ds.GetLayerByIndex(i)

    if layer is None:
        continue

    nombre = layer.GetName()

    # evitar repetir capas ya agrupadas
    if nombre in capas_en_grupos:
        continue

    layer_defn = layer.GetLayerDefn()
    geom_type = layer_defn.GetGeomType()

    # geometry = None  -> tabla
    if geom_type == ogr.wkbNone:

        capas_por_grupo[grupo_tablas].append(nombre)

# agregar grupo TABLAS si tiene contenido
if capas_por_grupo[grupo_tablas]:
    grupos.append(grupo_tablas)

# -----------------------------------------------------------------
# 4. Mostrar grupos encontrados
# -----------------------------------------------------------------
print("\nGrupos encontrados:")

for g in grupos:
    print(f"  {g}")

# -----------------------------------------------------------------
# 5. Exportar cada grupo a su propio GPKG
# -----------------------------------------------------------------
for grupo in grupos:

    capas = capas_por_grupo[grupo]

    if not capas:
        print(f"\n⚠️ Grupo '{grupo}' vacío. Se omite.")
        continue

    # ruta del gpkg
    output_gpkg = os.path.join(
        output_dir,
        f"{grupo}.gpkg"
    )

    # eliminar existente
    if os.path.exists(output_gpkg):
        gpkg_drv.DeleteDataSource(output_gpkg)

    # crear gpkg
    out_ds = gpkg_drv.CreateDataSource(output_gpkg)

    if out_ds is None:
        print(f"❌ Error al crear {output_gpkg}")
        continue

    print(f"\n📦 Exportando grupo '{grupo}'")
    print(f"📁 Archivo: {output_gpkg}")
    print(f"📌 Capas: {len(capas)}")

    # exportar capas
    for capa_nombre in capas:

        layer = ds.GetLayerByName(capa_nombre)

        if layer is None:
            print(f"   ⚠️ No encontrada: {capa_nombre}")
            continue

        print(f"   ✓ Exportando {capa_nombre}")

        out_ds.CopyLayer(layer, capa_nombre)

    # cerrar gpkg
    out_ds = None

    print(f"✅ Grupo '{grupo}' completado.")

# cerrar GDB
ds = None

print("\n🎉 Proceso finalizado.")
print(f"📁 Exportaciones en:\n{output_dir}")