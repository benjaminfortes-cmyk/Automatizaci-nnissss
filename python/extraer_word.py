"""
Saca del Word original la celda que dibuja una credencial y la deja
lista para usarla como plantilla: con huecos donde van el nombre, el
rol, el color y los textos del evento.

La usa generar.py; no hace falta ejecutarla a mano.
"""
import re
import zipfile
from pathlib import Path

ORIGINAL = Path(__file__).resolve().parent.parent / "recursos" / "Credenciales  Traumatologia.docx"


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


# --- fila de auspiciadores -------------------------------------------------
# El Word original traía cinco logos; el sexto no existe allí, así que se
# copia de uno de ellos y se reparte la fila entera un poco más chica.
# Las cajas son las mismas que usa la hoja de estilos (en pt), medidas desde
# el borde de la credencial; Word las cuenta desde el margen de la celda, que
# queda 6,83 pt a la derecha y 5,20 pt más abajo.
PT = 12700  # EMU por punto
DESFASE_X, DESFASE_Y = 6.83, 5.20

# rId de la imagen -> (izquierda, arriba, ancho, alto)
AUSPICIADORES = {
    "rId9":  (8.01,   131.97, 27.39,  9.40),   # bagó
    "rId8":  (40.39,  132.13, 47.70, 11.28),   # double medical
    "rId10": (93.10,  132.24, 44.66, 10.52),   # blunding
    "rId11": (142.76, 131.19, 43.68, 11.50),   # sb sports
    "rId7":  (191.43, 129.06, 20.36, 17.81),   # san bartolomé
    "rId12": (216.80, 132.30, 38.82, 10.00),   # essity
}
MODELO = "rId9"   # el logo del que se copia el envoltorio del nuevo


def _caja(anchor: str, medidas) -> str:
    """Deja el anclaje en la posición y el tamaño pedidos."""
    x, y, ancho, alto = medidas
    cx, cy = round(ancho * PT), round(alto * PT)
    anchor = re.sub(
        r'(<wp:positionH relativeFrom="margin"><wp:posOffset>)-?\d+',
        lambda m: m.group(1) + str(round((x - DESFASE_X) * PT)), anchor)
    anchor = re.sub(
        r'(<wp:positionV relativeFrom="margin"><wp:posOffset>)-?\d+',
        lambda m: m.group(1) + str(round((y - DESFASE_Y) * PT)), anchor)
    anchor = re.sub(r'<wp:extent cx="\d+" cy="\d+"/>', f'<wp:extent cx="{cx}" cy="{cy}"/>', anchor)
    anchor = re.sub(r'<a:ext cx="\d+" cy="\d+"/>', f'<a:ext cx="{cx}" cy="{cy}"/>', anchor)
    return re.sub(r'<wp:effectExtent[^/]*/>', '<wp:effectExtent l="0" t="0" r="0" b="0"/>', anchor)


def fila_auspiciadores(celda: str) -> str:
    def ajustar(m):
        anchor = m.group(0)
        rid = re.search(r'r:embed="(rId\d+)"', anchor)
        medidas = AUSPICIADORES.get(rid.group(1)) if rid else None
        return _caja(anchor, medidas) if medidas else anchor

    celda = re.sub(r"<wp:anchor.*?</wp:anchor>", ajustar, celda, flags=re.S)

    # La imagen nueva reusa el envoltorio de otra: mismo formato, otra foto.
    marca = f'r:embed="{MODELO}"'
    ini = celda.rindex("<w:r>", 0, celda.index(marca))
    fin = celda.index("</w:r>", ini) + len("</w:r>")
    corrida = celda[ini:fin]

    nueva = _caja(corrida.replace(marca, 'r:embed="rId12"'), AUSPICIADORES["rId12"])
    nueva = re.sub(r'relativeHeight="\d+"', 'relativeHeight="251712512"', nueva)
    nueva = re.sub(r'wp14:anchorId="\w+"', 'wp14:anchorId="0E1D7B2C"', nueva)
    return celda[:fin] + nueva + celda[fin:]


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

    celda = fila_auspiciadores(celda)

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
