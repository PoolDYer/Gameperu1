# Unity 6.6: comprobación real de herramientas

Se instaló Unity **6000.6.7f1**, revisión **b22767f04f04**, desde la descarga
oficial de Unity. El archivo de 4 138 711 428 bytes se verificó contra la suma
publicada en la API oficial. `Tools/unity_cloud.sh -version` devuelve 6000.6.7f1.

Se compilaron por separado el código Runtime y el de Editor con Roslyn y las
bibliotecas oficiales de esa instalación. Ambas compilaciones pasan. Se corrigió
un error CS0619 real: GetInstanceID() no se admite en ese uso en Unity 6.6.
La deduplicación de assets ahora guarda los objetos en un HashSet de Object.
Persisten advertencias CS0649 en campos del manifiesto que se cargan por JSON.
No se ocultaron ni se convirtieron errores en aprobaciones.

El comando de arranque del editor en batch falla con código **198** y el mensaje:
`No valid Unity Editor license found. Please activate your license.`
Se corrigió la ubicación de configuración y caché mediante variables XDG en
/workspace/unity-runtime, sin cambiar HOME ni desactivar verificaciones.

Por tanto, compilación C# y disponibilidad del ejecutable están verificadas;
importación del proyecto, ejecución, materiales, física y builds NO están
verificados. La compilación separada no sustituye estas pruebas del editor.

Reproducir la comprobación C# desde la raíz:

```bash
python3 Tools/check_unity_csharp.py
```

Tras activar legítimamente el editor, volver a intentar:

```bash
Tools/unity_cloud.sh -batchmode -nographics -quit -projectPath /workspace/Gameperu1 -logFile /tmp/unity-import.log
```

No introducir credenciales en scripts ni subir licencias al repositorio.
También se puede validar el proyecto en el Unity 6.6 ya activado del PC del usuario;
este entorno no tiene una conexión de control a ese PC.
