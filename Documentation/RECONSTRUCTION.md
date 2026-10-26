# Reconstrucción y aceptación

## Datos pendientes

Se proporcionaron una visita panorámica y una imagen comparativa de un sector
texturizado y su geometría. Posteriormente se recibió el artículo de Castillo
Butters y Barrera Yaranga (2024), que identifica la figura como el torreón de Machu
Picchu y acredita su modelo fotogramétrico; ver VISUAL_REFERENCE_01.md. No hay
dimensiones, levantamiento ni archivos 3D originales adjuntos. El enlace sigue bloqueado por
la red del entorno. La reconstrucción completa no puede validarse al 100 % a partir
de una visita visual: no aporta necesariamente profundidad, escala o cobertura
oculta, y no se ha comprobado todavía su contenido.

Conseguir y registrar procedencia, fecha, resolución, precisión, cobertura y permiso
de reutilización de:

- DEM/DTM o nube de puntos con referencia horizontal y vertical; distinguir terreno
  desnudo de superficies con vegetación o edificios.
- Ortofoto georreferenciada para alinear caminos, terrazas y plantas de estructuras.
- Levantamiento de muros, plataformas, escalinatas y edificios; cotas y puntos de
  control independientes para comprobar errores.
- Fotografías originales solapadas si se usará fotogrametría. Una panorámica aislada
  no sustituye un conjunto de captura calibrado.
- Delimitación del área y accesos a representar. No hay un tamaño final establecido
  y no se elegirá un rectángulo arbitrario como tamaño real de Machu Picchu.

Las elevaciones globales de baja resolución podrían servir para montañas de fondo,
pero no permiten resolver los andenes, muros y escalones del recinto.

## Producción cuando estén disponibles

1. Auditar cobertura y unidades, elegir origen local y guardar transformación al CRS
   real. Comparar distancias y elevaciones contra controles independientes.
2. Importar el relieve sin exageración. Mantener fuente sin modificar y versiones
   de trabajo diferenciadas; cada importación crea una carpeta nueva.
3. Modelar arquitectura por sectores con Blender, aplicando escala métrica, normales
   correctas, UV de materiales y lightmaps, y pivotes coherentes. Conservar fuentes
   `.blend` y exportaciones. Usar mallas para desniveles verticales.
4. Crear materiales PBR con albedo sin iluminación incrustada, normales y rugosidad
   coherentes con las referencias; evitar repetir patrones visibles en muros.
5. Ajustar HDRP en una copia versionada con la versión compatible con Unity 6.6.
   Elegir texturas, iluminación, sombras y vegetación según perfilado en el PC real.
6. Añadir LODGroup, colliders simplificados, culling y carga por sectores cuando la
   extensión real lo justifique. Los colliders no deben modificar la geometría
   visible; comprobar puertas, peldaños, bordes y rutas con el controlador real.
7. Validar cámaras emparejadas con las referencias y errores métricos contra el
   levantamiento. Registrar qué sectores están medidos, interpretados o pendientes.

## Criterios de aceptación por acordar con datos y hardware

La tolerancia geométrica debe derivarse de la precisión de la medición. La tasa de
fotogramas debe medirse en una GPU, resolución y configuración definidas. No hay
un presupuesto de FPS, número de polígonos o error centimétrico prometido sin esas
condiciones. La aceptación requiere terreno real editable, pruebas de recorrido,
ausencia de caídas a través del suelo, escala comprobada, escenas restaurables,
build funcional y evaluación visual de cada sector documentado.

## Estado actual

A petición del usuario se generó un prototipo interpretativo de 200 × 530 m, con
172 recintos de distribución inventada, terrazas, escaleras y un estudio del muro
curvo sobre roca. La media de elevación del relieve se ajusta a 2430 m; el perfil
no es topografía medida. Existen fuente Blender, FBX, render y una escena de
arranque Unity con generación en Play y herramienta de escenas editables.

La geometría se generó y validó en Blender y pasaron 14 pruebas Python. Las pruebas
de Unity siguen pendientes porque no está instalado/activado en esta máquina.
El prototipo no sustituye la adquisición de datos ni la reconstrucción exacta.
Las instrucciones y limitaciones actuales están en README.md.
