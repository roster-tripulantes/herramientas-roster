#!/usr/bin/env python3
"""Arma el kit de respaldo sin clave (plan B) del portal Herramientas equipo Roster.

Uso:  python3 _build/kit_respaldo.py <carpeta_origen_en_claro> <zip_salida> <fecha AAAA-MM-DD>

El kit NO se sube a este repositorio (es público): se entrega al responsable para guardarlo
en una carpeta interna del equipo. Cada página abre con doble clic (file://) y descarga con
un enlace normal del navegador.
"""
import os, sys, glob, re, shutil, zipfile, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cifrar import SHIM, inyectar_shim

MESES = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre']
LINK = 'https://roster-tripulantes.github.io/herramientas-roster/'


def portal_kit(doc, fecha):
    a, m, d = fecha.split('-')
    txt = f'{int(d)} de {MESES[int(m) - 1]} de {a}'
    # Botón de manual: en file:// no se puede usar fetch; se abre el PDF directamente.
    doc, n = re.subn(r"function manualBtn\(h\)\{.*?\n  \}\n", "function manualBtn(h){return el('a',{cls:'btn',href:h.manualUrl,target:'_blank',rel:'noopener',text:'Abrir manual (PDF)'});}\n", doc, count=1, flags=re.S)
    if n != 1:
        raise SystemExit('No encontré manualBtn en el portal')
    aviso = (f'<p class="lede" style="color:#f3c94b;font-weight:600">Copia de respaldo sin conexión al portal · versión del {txt}. '
             f'Úsala solo si el link oficial no carga: {LINK}</p>')
    doc = doc.replace('<div class="stats" id="stats"></div>', aviso + '\n    <div class="stats" id="stats"></div>', 1)
    return doc


LEEME = """KIT DE RESPALDO - HERRAMIENTAS EQUIPO ROSTER
Versión del {fecha}

Cuándo usarlo
  Solo si el link oficial no carga: {link}
  (GitHub caído, exceso de tráfico o problema con la clave).

Cómo usarlo
  1. Descomprime esta carpeta completa en una carpeta interna del equipo (OneDrive, red) o en tu computador.
     No muevas los archivos de sus subcarpetas: el portal los busca ahí.
  2. Abre index.html con doble clic (Chrome o Edge). No pide clave.
  3. Escoge tu equipo (TCP o TCM) y abre la herramienta. Las descargas bajan directo, sin iniciar sesión.
  4. Los manuales en PDF están en la carpeta manuales.

Importante
  - Las herramientas necesitan internet para cargar sus librerías (Excel, lector de PDF), igual que en el link oficial.
  - Esta copia no se actualiza sola. Cuando se actualice una herramienta se entrega un kit nuevo: reemplaza la carpeta completa.
  - Es una copia sin clave: guárdala solo en carpetas internas del equipo. No la envíes por fuera.
"""


def main(src, zip_out, fecha):
    raiz = 'Herramientas_Roster_respaldo_' + fecha.replace('-', '')
    tmp = tempfile.mkdtemp()
    base = os.path.join(tmp, raiz)
    os.makedirs(os.path.join(base, 'herramientas'))
    os.makedirs(os.path.join(base, 'manuales'))
    portal = open(os.path.join(src, 'index.html'), encoding='utf-8').read()
    open(os.path.join(base, 'index.html'), 'w', encoding='utf-8').write(inyectar_shim(portal_kit(portal, fecha)))
    for p in sorted(glob.glob(os.path.join(src, 'herramientas', '*.html'))):
        doc = open(p, encoding='utf-8').read()
        open(os.path.join(base, 'herramientas', os.path.basename(p)), 'w', encoding='utf-8').write(inyectar_shim(doc))
    for p in sorted(glob.glob(os.path.join(src, 'manuales', '*.pdf'))):
        shutil.copy(p, os.path.join(base, 'manuales'))
    a, m, d = fecha.split('-')
    open(os.path.join(base, 'LEEME.txt'), 'w', encoding='utf-8').write(LEEME.format(fecha=f'{int(d)} de {MESES[int(m)-1]} de {a}', link=LINK).replace('\n', '\r\n'))
    with zipfile.ZipFile(zip_out, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for r, _, fs in os.walk(base):
            for f in fs:
                full = os.path.join(r, f)
                z.write(full, os.path.relpath(full, tmp))
    print('kit', zip_out, os.path.getsize(zip_out))
    return base


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])
