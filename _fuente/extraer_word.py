"""
Saca del Word original la celda que dibuja una credencial y la deja
lista para usarla como plantilla: con huecos donde van el nombre, el
rol, el color y los textos del evento.

La usa generar.py; no hace falta ejecutarla a mano.
"""
import re
import zipfile
from pathlib import Path

ORIGINAL = Path(__file__).resolve().parent.parent / "Credenciales  Traumatologia.docx"


def bloque(xml: str, etiqueta: str, desde: int) -> str:
    """Devuelve el elemento `etiqueta` que empieza en `desde`, contando anidados.

    Hace falta porque las credenciales llevan una tabla dentro de otra:
    una expresión regular perezosa cortaría en el cierre equivocado.
    """
    ab_t, ce_t = f"<{etiqueta}>", f"</{etiqueta}>"
    i, hondo = desde, 0
    while True:
        ab = xml.find(ab_t, i)
        ce = xml.find(ce_t, i)
        if ce == -1:
            raise ValueError(f"no se cerró {etiqueta}")
        if ab != -1 and ab < ce:
            hondo += 1
            i = ab + len(ab_t)
        else:
            hondo -= 1
            i = ce + len(ce_t)
            if hondo == 0:
                return xml[desde:i]


def plantilla_celda():
    with zipfile.ZipFile(ORIGINAL) as z:
        doc = z.read("word/document.xml").decode("utf-8")

    # La segunda tabla del cuerpo es una credencial ya terminada (ORGANIZADOR).
    p = doc.index("<w:tbl>")
    p = doc.index("<w:tbl>", p + len(bloque(doc, "w:tbl", p)))
    tabla = bloque(doc, "w:tbl", p)
    celda = bloque(tabla, "w:tc", tabla.index("<w:tc>"))

    # Ruido de edición de Word que no aporta nada y puede chocar al repetir.
    celda = re.sub(r'\s+w:rsid[A-Za-z]*="[^"]*"', "", celda)
    celda = re.sub(r'\s+w14:(?:paraId|textId)="[^"]*"', "", celda)

    # Huecos de contenido.
    celda = celda.replace("2ª JORNADA DE TRAUMATOLOGÍA", "{{TITULO}}")
    celda = celda.replace("y Medicina del Ejercicio y Estilo de Vida", "{{SUB}}")
    celda = celda.replace("ACEM UCN  ·  Universidad Católica del Norte", "{{INST}}")
    celda = celda.replace("ORGANIZADOR", "{{ROL}}")
    celda = celda.replace('w:fill="1D2D59"', 'w:fill="{{COLOR}}"')

    # El nombre venía partido en dos runs; lo dejamos en uno solo.
    celda = re.sub(
        r'(<w:r><w:rPr><w:rFonts w:ascii="Calibri" w:hAnsi="Calibri" w:cs="Calibri"/>'
        r"<w:b/><w:bCs/><w:color w:val=\"747474\"[^>]*/><w:sz w:val=\"24\"/>"
        r'<w:szCs w:val="24"/></w:rPr><w:t[^>]*>).*?(</w:t></w:r>)'
        r'(?:<w:r><w:rPr>.*?</w:rPr><w:t[^>]*>.*?</w:t></w:r>)*',
        r"\1{{NOMBRE}}\2",
        celda,
        flags=re.S,
    )

    # Los identificadores de imagen tienen que ser únicos en todo el documento.
    n = [0]

    def numerar(m):
        n[0] += 1
        return f'<wp:docPr id="{{{{ID{n[0]}}}}}" name="Imagen {n[0]}"/>'

    celda = re.sub(r'<wp:docPr id="\d+" name="[^"]*"/>', numerar, celda)
    celda = re.sub(r'<pic:cNvPr id="\d+" name="[^"]*"/>', '<pic:cNvPr id="0" name=""/>', celda)

    return celda, n[0]


if __name__ == "__main__":
    c, ids = plantilla_celda()
    print(f"{len(c)} bytes, {ids} imágenes")
    for hueco in ("{{TITULO}}", "{{SUB}}", "{{INST}}", "{{NOMBRE}}", "{{ROL}}", "{{COLOR}}"):
        print(f"  {hueco}: {c.count(hueco)}")
