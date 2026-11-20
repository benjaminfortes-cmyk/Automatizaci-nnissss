"""
Genera js/datos.js: los logotipos, la foto y la plantilla de Word,
todo incrustado en base64.

Van incrustados a propósito. El navegador necesita los bytes crudos de
los logotipos para armar el .docx, y leerlos con fetch no funciona al
abrir la página con doble clic (file://). Así la página funciona igual
publicada en internet que descargada en un pendrive.

Uso, desde la raíz del proyecto:

    python python/generar.py
"""
import base64
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parent
RECURSOS = RAIZ / "recursos"
SALIDA = RAIZ / "js" / "datos.js"

sys.path.insert(0, str(AQUI))

LOGOS = {
    "olaIzq": "ola-izq.png",
    "olaDer": "ola-der.png",
    "acem":   "acem.png",
    "ucn":    "ucn.png",
    "alba":   "alba.png",
}


def data_uri(ruta: Path, tipo: str) -> str:
    datos = base64.b64encode(ruta.read_bytes()).decode("ascii")
    return f"data:{tipo};base64,{datos}"


def piezas_word() -> dict:
    """Todo lo que el navegador necesita para armar el .docx."""
    import armar_word as w
    from extraer_word import plantilla_celda

    celda, _ = plantilla_celda()
    return {
        "celda": celda,
        "cabecera": w.CABECERA,
        "raiz": w.RAIZ,
        "contentTypes": w.CONTENT_TYPES,
        "rels": w.RELS,
        "docRels": w.DOC_RELS,
        "styles": w.STYLES,
        "sinBordes": (
            "<w:tblBorders>"
            + "".join(
                f'<w:{lado} w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
                for lado in ("top", "left", "bottom", "right", "insideH", "insideV")
            )
            + "</w:tblBorders>"
        ),
        "anchoCred": w.ANCHO_CRED,
        "altoCred": w.ALTO_CRED,
        "anchoHoja": w.ANCHO_HOJA,
        "hoja": {str(k): {"sep": v["sep"], "margenV": v["margenV"]} for k, v in w.HOJA.items()},
        # El Word de Medicina Interna numera las imágenes en este orden.
        "imagenes": ["olaDer", "olaIzq", "alba", "acem", "ucn"],
    }


def main() -> None:
    datos = {
        "logos": {
            clave: data_uri(RECURSOS / "logos" / archivo, "image/png")
            for clave, archivo in LOGOS.items()
        },
        "foto": data_uri(RECURSOS / "foto.jpg", "image/jpeg"),
        "word": piezas_word(),
    }

    cuerpo = json.dumps(datos, ensure_ascii=False, separators=(",", ":"))
    SALIDA.write_text(f"const DATOS = {cuerpo};\n", encoding="utf-8")
    print(f"Listo: {SALIDA.relative_to(RAIZ)}  ({SALIDA.stat().st_size/1024:.0f} KB)")


if __name__ == "__main__":
    main()
