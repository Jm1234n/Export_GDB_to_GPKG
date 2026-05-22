Aun esta en desarrollo este proyecto, se busca poder exportar toda una GDB de ESRI,
 del tipo compleja a una estructura usable, para una base de datos, donde no se
 dependa del ecosistema de ESRI, para hacer pruebas o testear compatibilidad con
 otros programas.

 #Hasta el momento se tiene un script que itera los nombres de los featuresdatasets de
 #la GDB, convirtiendo cada featuredataset en un grupo y este a su vez en un GPKG,
 #esto porque asi puedes ordenarlas por coordenadas geograficas, es decir cada GPKG
 tendra una coordenadaa geograficas y las capas dentro de ella, compartiran esas
 #coordenadas

 -Hecho por: jm1234n