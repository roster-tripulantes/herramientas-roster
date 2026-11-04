#!/usr/bin/env python3
"""Cifra el portal Herramientas equipo Roster para GitHub Pages.

Uso:  python3 _build/cifrar.py <carpeta_origen> <carpeta_repo>

La carpeta de origen tiene index.html, herramientas/*.html y manuales/*.pdf en claro.
Cada página se cifra con una clave AES aleatoria; esa clave se cifra con la clave pública
RSA (_build/clave-publica.pem). La clave privada RSA solo existe cifrada con la clave de
acceso del equipo (_build/clave-privada-cifrada.json), así que para publicar no hace falta
conocer la clave de acceso: solo para abrir.
"""
import base64, gzip, json, os, sys, glob, html
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

AQUI = os.path.dirname(os.path.abspath(__file__))
b64 = lambda b: base64.b64encode(b).decode()

# Reemplaza el sistema de descargas de claude.ai por una descarga normal del navegador.
SHIM = """<script>(function(){function save(r){return new Promise(function(res,rej){try{var d=r&&r.data;var b=(d instanceof Blob)?d:new Blob([d]);var a=document.createElement('a');a.href=URL.createObjectURL(b);a.download=r.filename||'archivo';a.style.display='none';document.body.appendChild(a);a.click();setTimeout(function(){URL.revokeObjectURL(a.href);a.remove();},5000);res({status:'saved'});}catch(e){rej({code:'unavailable',message:String(e)});}});}
window.claude={use:function(n){return Promise.resolve(n==='downloads'?Object.freeze({save:save}):null);}};})();</script>"""


def cargar():
    pub = serialization.load_pem_public_key(open(os.path.join(AQUI, 'clave-publica.pem'), 'rb').read())
    priv = json.load(open(os.path.join(AQUI, 'clave-privada-cifrada.json')))
    return pub, priv


def sobre(pub, datos, gz):
    k = AESGCM.generate_key(256)
    iv = os.urandom(12)
    ct = AESGCM(k).encrypt(iv, gzip.compress(datos, 9) if gz else datos, None)
    wk = pub.encrypt(k, padding.OAEP(mgf=padding.MGF1(hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
    return {"v": 1, "gz": gz, "wk": b64(wk), "iv": b64(iv), "ct": b64(ct)}


def inyectar_shim(doc):
    i = doc.find('<body>')
    if i >= 0:
        return doc[:i + 6] + SHIM + doc[i + 6:]
    return SHIM + doc


def cargador(titulo, paquete, priv):
    plantilla = open(os.path.join(AQUI, 'cargador.html'), encoding='utf-8').read()
    datos = json.dumps({"k": priv, "p": paquete}, separators=(',', ':'))
    return (plantilla.replace('__TITULO__', html.escape(titulo))
                     .replace('__DATOS__', datos.replace('</', '<\\/')))


def titulo_de(doc, defecto):
    i = doc.find('<title>')
    j = doc.find('</title>', i)
    return html.unescape(doc[i + 7:j]).strip() if i >= 0 and j > i else defecto


def main(src, repo):
    pub, priv = cargar()
    paginas = ['index.html'] + sorted(os.path.relpath(p, src) for p in glob.glob(os.path.join(src, 'herramientas', '*.html')))
    for rel in paginas:
        doc = open(os.path.join(src, rel), encoding='utf-8').read()
        out = cargador(titulo_de(doc, 'Herramientas equipo Roster'), sobre(pub, inyectar_shim(doc).encode('utf-8'), True), priv)
        dst = os.path.join(repo, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        open(dst, 'w', encoding='utf-8').write(out)
        print('pagina', rel, len(out))
    for pdf in sorted(glob.glob(os.path.join(src, 'manuales', '*.pdf'))):
        rel = os.path.relpath(pdf, src)
        dst = os.path.join(repo, rel + '.enc')
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        json.dump(sobre(pub, open(pdf, 'rb').read(), False), open(dst, 'w'))
        print('manual', rel)


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
