# Herramientas equipo Roster — sitio publicado

Este repositorio publica en GitHub Pages el portal de herramientas del equipo Roster:
https://roster-tripulantes.github.io/herramientas-roster/

Todo el contenido está cifrado. Lo que se ve en el repositorio son páginas "cargador"
que piden la clave de acceso del equipo y descifran la herramienta en el navegador.

## Cómo está armado

- `index.html` = portal. `herramientas/<id>.html` = cada herramienta. `manuales/*.pdf.enc` = manuales en PDF cifrados.
- `_build/cifrar.py` cifra las páginas en claro de una carpeta de origen y escribe los cargadores aquí.
- `_build/clave-publica.pem` = clave pública RSA. Con ella se cifra; NO hace falta la clave de acceso para publicar.
- `_build/clave-privada-cifrada.json` = clave privada RSA cifrada con la clave de acceso (PBKDF2 600 000 + AES-GCM). Va dentro de cada cargador.
- `_build/cargador.html` = plantilla de la pantalla de acceso.
- `cifrar.py` inyecta en cada página un reemplazo de `window.claude.use('downloads')` que descarga con un enlace normal del navegador, para que nadie tenga que iniciar sesión.

## Cómo actualizar una herramienta o el portal

1. La fuente en claro del portal es el artifact de claude.ai "Herramientas equipo Roster"
   (https://claude.ai/artifact/18zre5WKBF3vL3wSZfNZt2): su `index.html`, `herramientas/<id>.html` y `manuales/*.pdf`.
   Actualiza primero la herramienta y el catálogo JSON del portal (tarjeta, fecha, manual, bitácora `cambios`) como siempre.
2. Arma una carpeta de origen con `index.html`, `herramientas/` y `manuales/` en claro, aplicando al `index.html` del portal
   los dos ajustes de este sitio:
   - el botón de manual descarga `h.manualUrl + '.enc'` y lo descifra con `window.__roster.abrir(o)`;
   - el pie lleva el botón "Olvidar la clave en este navegador" (`window.__roster.olvidar()`).
3. `python3 _build/cifrar.py <carpeta_origen> .` y luego commit + push a `main`. Pages publica en 1–2 minutos.
4. Nunca subas archivos en claro (HTML de herramientas, PDF, plantas o reportes) a este repositorio: es público.
5. Plan B: después de cada actualización regenera el kit de respaldo sin clave con
   `python3 _build/kit_respaldo.py <carpeta_origen> <ruta_fuera_del_repo>/Herramientas_Roster_respaldo_AAAAMMDD.zip AAAA-MM-DD`
   (la carpeta de origen lleva el `index.html` del portal tal cual está en claude.ai, sin los dos ajustes del paso 2)
   y entrégaselo al responsable para que reemplace la copia en la carpeta interna del equipo. El kit NUNCA se sube aquí.

## Cambiar la clave de acceso

Requiere generar un par RSA nuevo y una clave nueva, volver a cifrar todo con `cifrar.py` y entregar la clave nueva al
responsable (Esteban Toro Ortiz). La clave de acceso no se guarda en el repositorio.
