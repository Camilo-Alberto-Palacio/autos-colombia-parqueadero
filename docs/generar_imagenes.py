"""
Script de Generación Automática de Imágenes PNG y SVG desde PlantUML (.puml)
Autos Colombia 24/7 - Iteración 1
Docente: Reinaldo Rojas
"""

import os
import re
import zlib
import urllib.request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "diagramas")
os.makedirs(OUTPUT_DIR, exist_ok=True)

PLANTUML_CHARS = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_'

def encode6bit(b):
    return PLANTUML_CHARS[b & 0x3F]

def encode3bytes(b1, b2, b3):
    c1 = b1 >> 2
    c2 = ((b1 & 0x3) << 4) | (b2 >> 4)
    c3 = ((b2 & 0xF) << 2) | (b3 >> 6)
    c4 = b3 & 0x3F
    return encode6bit(c1) + encode6bit(c2) + encode6bit(c3) + encode6bit(c4)

def plantuml_encode(text):
    z = zlib.compressobj(level=9, method=zlib.DEFLATED, wbits=-15)
    compressed = z.compress(text.encode('utf-8')) + z.flush()
    res = []
    i = 0
    while i < len(compressed):
        b1 = compressed[i]
        b2 = compressed[i+1] if i+1 < len(compressed) else 0
        b3 = compressed[i+2] if i+2 < len(compressed) else 0
        res.append(encode3bytes(b1, b2, b3))
        i += 3
    if len(compressed) % 3 == 1:
        res[-1] = res[-1][:2]
    elif len(compressed) % 3 == 2:
        res[-1] = res[-1][:3]
    return ''.join(res)

def descargar_imagen(puml_code, nombre_archivo):
    enc = plantuml_encode(puml_code)
    url_png = f"http://www.plantuml.com/plantuml/png/~1{enc}"
    url_svg = f"http://www.plantuml.com/plantuml/svg/~1{enc}"
    
    png_path = os.path.join(OUTPUT_DIR, f"{nombre_archivo}.png")
    svg_path = os.path.join(OUTPUT_DIR, f"{nombre_archivo}.svg")
    
    headers = {'User-Agent': 'Mozilla/5.0'}
    
    try:
        req = urllib.request.Request(url_png, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            with open(png_path, "wb") as f:
                f.write(resp.read())
        print(f"[OK] Generado PNG: {png_path}")
    except Exception as e:
        print(f"[Error PNG] {nombre_archivo}: {e}")

    try:
        req = urllib.request.Request(url_svg, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as resp:
            with open(svg_path, "wb") as f:
                f.write(resp.read())
        print(f"[OK] Generado SVG: {svg_path}")
    except Exception as e:
        print(f"[Error SVG] {nombre_archivo}: {e}")

def procesar_archivos():
    archivo_md = os.path.join(BASE_DIR, "MODELADO_STARUML_Y_ARQUITECTURA.md")
    if not os.path.exists(archivo_md):
        print(f"No se encontró {archivo_md}")
        return

    with open(archivo_md, "r", encoding="utf-8") as f:
        contenido = f.read()

    # Buscar bloques ```plantuml ... ```
    bloques = re.findall(r"```plantuml\s*([\s\S]*?)```", contenido)
    nombres = [
        "1_diagrama_paquetes",
        "2_diagrama_casos_de_uso",
        "3_diagrama_de_clases",
        "4_diagrama_secuencia_entrada",
        "5_diagrama_secuencia_salida"
    ]

    for i, bloque in enumerate(bloques):
        nombre = nombres[i] if i < len(nombres) else f"diagrama_{i+1}"
        print(f"Procesando {nombre}...")
        descargar_imagen(bloque.strip(), nombre)

if __name__ == "__main__":
    print("=" * 60)
    print(" GENERADOR DE IMÁGENES PLANTUML A PNG / SVG")
    print("=" * 60)
    procesar_archivos()
