# Referencia visual 01 — sector arquitectónico

Imagen adjunta en la conversación: dos vistas similares de un sector de ruinas.
Panel a: superficie texturizada. Panel b: geometría con material uniforme violeta.
La procedencia fue confirmada mediante el PDF proporcionado por el usuario: figura
10, página impresa 112 (página 17 del PDF), torreón de Machu Picchu. Fotografías y
modelo atribuidos a Luis Jaime Castillo/PASJM. No se dispone del archivo 3D,
escala métrica, calibración de cámara ni condiciones de reutilización del modelo.
No se ha incorporado la ilustración como textura.

## Rasgos visibles que deben conservarse

- Muro curvo central de mampostería, asentado sobre una gran formación rocosa.
  Las hiladas y juntas se perciben también en el panel geométrico: no todo el
  detalle proviene de una imagen de color.
- Roca con superficies inclinadas, variaciones de volumen y contacto irregular
  con los muros; requiere malla independiente del heightfield.
- Escaleras a la derecha, cambios de dirección y conexiones entre plataformas;
  escalones más pequeños visibles cerca de la base izquierda de la roca.
- Muros posteriores con secuencia de nichos y vanos; conservar separación,
  profundidad y alineación cuando las medidas estén disponibles.
- Recintos laterales, pasajes estrechos y cotas de pavimento distintas.
- Muros de contención delanteros con aparejo más irregular que el muro curvo.
- Bordes superiores irregulares, variación de altura entre muros y encuentro
  entre roca natural y piedra trabajada.

## Interpretación y límites

El pie de la figura confirma que es un modelo fotogramétrico realizado con 2829
fotografías, exclusivamente desde la superficie y con una cámara fotográfica.
La figura no documenta una precisión métrica específica para este modelo.
Los fondos negros y discontinuidades pueden corresponder a límites o huecos de
captura. No tratarlos automáticamente como aberturas reales de la arquitectura.
La perspectiva y la ausencia de una escala impiden deducir medidas fiables.
No inventar la cara posterior, interiores ocultos o dimensiones de escalones.
Esta imagen cubre un sector, no la totalidad del sitio arqueológico.

## Aplicación al proyecto

Localizar la fuente y, si está disponible para reutilización, obtener el modelo
original y sus texturas, unidades y puntos de control. Preservar una copia maestra.
Inspeccionar en Blender normales, escala, huecos de captura, topología y materiales.
Derivar mallas de render con niveles de detalle y colliders independientes; conservar
siluetas, accesos y contactos con el suelo. Llevar el conjunto a Architecture.unity
con la misma transformación geográfica que el TerrainData.

Comparar encuadres equivalentes del modelo con ambos paneles, incluyendo una pasada
sin texturas. Esta prueba diferencia errores geométricos de errores de material.
No afirmar equivalencia visual, métrica o cobertura completa antes de esa revisión.

## Publicación verificada

Luis Jaime Castillo Butters y Héctor Barrera Yaranga (2024). *Fotogrametría,
modelamiento tridimensional y drones en arqueología. Primera parte. La ilustración
arqueológica. De la representación artística al modelamiento tridimensional*.
Boletín de Arqueología PUCP, n.º 35, pp. 96–121.
DOI: https://doi.org/10.18800/boletindearqueologiapucp.202402.005

El pie de la figura 10 especifica «en base a 2829 fotos» y acredita «Luis Jaime
Castillo/PASJM». PASJM corresponde al Programa Arqueológico San José de Moro,
según la afiliación de la primera página. El artículo publica el contacto
lcastil@pucp.edu.pe. No se ha enviado ningún mensaje.

Se revisaron el texto, los enlaces del PDF, sus adjuntos y sus objetos 3D. No hay
archivos embebidos ni streams 3D; no se identificó un enlace de descarga del modelo
del torreón. Esto no demuestra que no exista una descarga fuera del documento.
El acceso al DOI desde este entorno devolvió HTTP 403 del proxy.

La publicación trata la georreferenciación y sus limitaciones en la página 108;
las referencias generales a precisión centimétrica no constituyen un certificado
de precisión del modelo de la figura 10. No se asignará esa precisión al proyecto.

Para continuar con esta fuente se necesita localizar u obtener el modelo original
con texturas, unidades, georreferencia/puntos de control y condiciones de uso, o las
fotografías originales y datos de medición. Este modelo corresponde a un sector;
no acredita cobertura del conjunto de Machu Picchu.
