"""
Arma index.html incrustando los logotipos dentro del archivo, para que
funcione sin internet y se pueda copiar a cualquier computador.

Se llama index.html porque es el nombre que GitHub Pages busca en la
raíz del sitio.

Uso:  python _fuente/generar.py
"""
import base64
import json
from pathlib import Path

AQUI = Path(__file__).resolve().parent
SALIDA = AQUI.parent / "index.html"

LOGOS = {
    "arco":     "arco.png",
    "acem":     "acem-ucn.png",
    "bago":     "bago.png",
    "double":   "double-medical.png",
    "blunding": "blunding.png",
    "sbsports": "sb-sports.png",
    "sanbarto": "san-bartolome.png",
}


def a_data_uri(ruta: Path) -> str:
    datos = base64.b64encode(ruta.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{datos}"


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
        # El Word original numera las imágenes en este orden.
        "imagenes": ["acem", "arco", "sanbarto", "double", "bago", "blunding", "sbsports"],
    }


def main() -> None:
    incrustados = {
        clave: a_data_uri(AQUI / "logos" / archivo)
        for clave, archivo in LOGOS.items()
    }
    plantilla = (AQUI / "plantilla.html").read_text(encoding="utf-8")
    html = plantilla.replace("__LOGOS__", json.dumps(incrustados, indent=0))
    html = html.replace("__DOCX__", json.dumps(piezas_word(), ensure_ascii=False))
    SALIDA.write_text(html, encoding="utf-8")
    print(f"Listo: {SALIDA}  ({SALIDA.stat().st_size/1024:.0f} KB)")


if __name__ == "__main__":
    main()
