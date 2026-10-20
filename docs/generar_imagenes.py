"""
Script de Generación Oficial de Diagramas PNG y SVG
Autos Colombia 24/7 - Iteración 1
Docente: Reinaldo Rojas
"""

import os
import re
import urllib.request
import urllib.error

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = os.path.join(BASE_DIR, "diagramas")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def descargar_diagrama(puml_code: str, nombre: str):
    headers = {
        'Content-Type': 'text/plain; charset=utf-8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
    data = puml_code.strip().encode('utf-8')

    # Descargar PNG
    try:
        url_png = "https://kroki.io/plantuml/png"
        req = urllib.request.Request(url_png, data=data, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            png_bytes = resp.read()
            png_path = os.path.join(OUTPUT_DIR, f"{nombre}.png")
            with open(png_path, "wb") as f:
                f.write(png_bytes)
            print(f"[OK] PNG: {nombre}.png ({len(png_bytes)} bytes)")
    except urllib.error.HTTPError as e:
        err = e.read().decode('utf-8')
        print(f"[ERROR PNG] {nombre}: HTTP {e.code} - {err}")
    except Exception as e:
        print(f"[ERROR PNG] {nombre}: {e}")

    # Descargar SVG
    try:
        url_svg = "https://kroki.io/plantuml/svg"
        req = urllib.request.Request(url_svg, data=data, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as resp:
            svg_bytes = resp.read()
            svg_path = os.path.join(OUTPUT_DIR, f"{nombre}.svg")
            with open(svg_path, "wb") as f:
                f.write(svg_bytes)
            print(f"[OK] SVG: {nombre}.svg ({len(svg_bytes)} bytes)")
    except urllib.error.HTTPError as e:
        err = e.read().decode('utf-8')
        print(f"[ERROR SVG] {nombre}: HTTP {e.code} - {err}")
    except Exception as e:
        print(f"[ERROR SVG] {nombre}: {e}")

def main():
    print("=" * 65)
    print(" GENERADOR OFICIAL DE DIAGRAMAS UML EN PNG Y SVG")
    print("=" * 65)
    
    archivo_md = os.path.join(BASE_DIR, "MODELADO_STARUML_Y_ARQUITECTURA.md")
    with open(archivo_md, "r", encoding="utf-8") as f:
        contenido = f.read()

    bloques = re.findall(r"```plantuml\s*([\s\S]*?)```", contenido)
    nombres = [
        "1_diagrama_paquetes",
        "2_diagrama_casos_de_uso",
        "3_diagrama_de_clases",
        "4_diagrama_secuencia_entrada",
        "5_diagrama_secuencia_salida",
        "6_diagrama_arquitectura_componentes",
        "7_diagrama_entidad_relacion_mer"
    ]

    for i, bloque in enumerate(bloques):
        nombre = nombres[i] if i < len(nombres) else f"diagrama_{i+1}"
        print(f"\nGenerando {nombre}...")
        descargar_diagrama(bloque, nombre)

    print("\n[LISTO] Todos los diagramas generados en:", OUTPUT_DIR)

if __name__ == "__main__":
    main()
