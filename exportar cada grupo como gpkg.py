#extrae la lista de primer grupo de GDB en python - qgis y exporta a un gpkg (ahora de cada grupo de la GDB)

import subprocess
import re
import os
from osgeo import ogr

gdb_path = r"D:\DESARROLLO\migracion de BD\BDP\GDB\BDP.gdb"
output_dir = r"D:\DESARROLLO\migracion de BD\BDP\exportacion de GDB\prueba"

# Crear carpeta de salida si no existe
os.makedirs(output_dir, exist_ok=True)

# -----------------------------------------------------------------
# 1. Extraer todos los grupos y sus capas usando ogrinfo
# -----------------------------------------------------------------
try:
    output = subprocess.check_output(['ogrinfo', gdb_path], text=True, shell=True)
except Exception as e:
    print(f"Error al ejecutar ogrinfo: {e}")
    exit()

lines = output.splitlines()

grupos = []
capas_por_grupo = {}
grupo_actual = None

for line in lines:
    # Detectar línea de grupo: "Group NOMBRE:"
    match_group = re.match(r'^Group\s+(\S+):', line)
    if match_group:
        grupo_actual = match_group.group(1)
        grupos.append(grupo_actual)
        capas_por_grupo[grupo_actual] = []
        continue

    # Detectar capas dentro del grupo actual
    if grupo_actual and re.match(r'^\s+Layer:', line):
        match_layer = re.search(r'Layer:\s+(\S+)', line)
        if match_layer:
            capas_por_grupo[grupo_actual].append(match_layer.group(1))

# Mostrar los grupos encontrados
print("Grupos encontrados:")
for g in grupos:
    print(f"  {g}")

if not grupos:
    print("No se encontraron grupos (Feature Datasets).")
    exit()

# -----------------------------------------------------------------
# 2. Abrir la GDB original una sola vez
# -----------------------------------------------------------------
ds = ogr.Open(gdb_path)
if ds is None:
    print(f"Error: no se pudo abrir la GDB {gdb_path}")
    exit()

# Driver GeoPackage
gpkg_drv = ogr.GetDriverByName('GPKG')

# -----------------------------------------------------------------
# 3. Exportar cada grupo a su propio GeoPackage
# -----------------------------------------------------------------
for grupo in grupos:
    capas = capas_por_grupo[grupo]
    if not capas:
        print(f"\n⚠️ Grupo '{grupo}' no contiene capas. Se omite.")
        continue

    # Ruta del GPKG de salida para este grupo
    output_gpkg = os.path.join(output_dir, f"{grupo}.gpkg")
    
    # Eliminar GPKG si ya existe (para empezar limpio)
    if os.path.exists(output_gpkg):
        gpkg_drv.DeleteDataSource(output_gpkg)
    
    # Crear nuevo GPKG vacío
    out_ds = gpkg_drv.CreateDataSource(output_gpkg)
    if out_ds is None:
        print(f"  ❌ Error al crear {output_gpkg}")
        continue
    
    print(f"\n📦 Exportando grupo '{grupo}' -> {output_gpkg}")
    print(f"   Capas a exportar: {len(capas)}")
    
    # Copiar cada capa del grupo al GPKG
    for capa_nombre in capas:
        layer = ds.GetLayerByName(capa_nombre)
        if layer is None:
            print(f"     ⚠️ Capa '{capa_nombre}' no encontrada en la GDB (omitida)")
            continue
        
        print(f"     ✓ Exportando {capa_nombre}...")
        out_ds.CopyLayer(layer, capa_nombre)
    
    # Cerrar el GPKG de este grupo
    out_ds = None
    print(f"  ✅ Grupo '{grupo}' completado.")

# Cerrar la GDB original
ds = None

print("\n🎉 Proceso finalizado. Todos los grupos han sido exportados.")
print(f"📁 Los archivos GPKG se encuentran en:\n   {output_dir}")