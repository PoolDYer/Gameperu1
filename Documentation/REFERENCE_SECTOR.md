# Corrección visual del sector

Se abandona la cuadrícula general como respuesta válida a la imagen y se conserva
por separado para no borrar trabajo. El nuevo archivo ReferenceSector representa
únicamente el sector visible del torreón como estudio de formas y desniveles.

Referencia principal: figura 10, página impresa 112 (página 17 del PDF), atribuida a
Luis Jaime Castillo/PASJM. Las panorámicas proporcionadas por el usuario ahora
responden HTTP 200; se inspeccionaron cuatro caras de cubo de la vista panorámica.
Se observan muros de piedra irregular, terrazas elevadas y fuertes desniveles. No
se obtuvo ninguna malla 3D ni dato de elevación medido desde esos recursos.

Elementos implementados: basamento rocoso irregular inclinado, muro curvo superior
con piezas tangenciales, retornos y nichos, pisos de recintos a distintas cotas,
muros de contención y escalera lateral de 64 peldaños con contrahuella estimada
de 0,18 m. Las cotas, dimensiones de los recintos y huellas fueron interpretadas,
no medidas. El terreno local tiene 50 × 44 m; esto no define el tamaño real del
sector ni altera el área general de 530 × 200 m proporcionada por el usuario.

La imagen adjunta no permite resolver por sí sola profundidad, zonas ocultas,
plantas completas y cotas absolutas. El objetivo de igualdad al 100 % y el alcance
de toda la ciudadela siguen sin cumplirse. No presentar este estudio como sustituto
del modelo fotogramétrico de 2829 fotografías.

Verificaciones: generación y render en Blender, inspección visual, corrección de
intersecciones de pisos con el terreno. La exportación FBX conserva las mallas
separadas. Pendientes en Unity: compilación, orientación y escala de importación,
recorridos, colisiones, materiales, rendimiento y ejecutable.

Recursos oficiales consultados: API de versiones de Unity confirmó 6000.6.7f1 para
Linux, paquete de aproximadamente 4,14 GB y tamaño instalado de 9,15 GB. Se mantuvo
la verificación TLS; no se descargó ni instaló porque el dominio de descarga
devolvió HTTP 403 del proxy. No se ha comprobado una licencia utilizable.

## Plano del recorrido encontrado después de la corrección

El archivo script_general.js del recorrido completo declara un mapa de 1679 ×
1000 unidades de imagen y 25 posiciones de panorámicas. Se extrajeron esas
coordenadas sin ejecutar código remoto y se guardaron en tour-map-positions.json.
La imagen de mayor resolución del mapa es de 2048 × 1219 píxeles; sus coordenadas
no deben mezclarse con las del mapa lógico sin transformar la resolución.

Las posiciones son marcadores de vistas, no plantas ni cotas de edificios. No se
han identificado latitud, longitud, georreferencia o modelo 3D en los archivos
consultados. Las referencias genéricas a Model3D del reproductor no demuestran
que el recorrido incluya geometría descargable. No se encontró un recurso GLB,
GLTF u OBJ en estos archivos.

El plano puede orientar la siguiente revisión de distribución; todavía hace falta
calibrar su escala, comprobar qué área incluye y obtener cotas. Ajustar por
separado sus ejes a 530 y 200 metros deformaría las proporciones y no resolvería
esa falta de información. La imagen original no se redistribuye como textura.
