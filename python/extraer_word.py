"""
Saca del Word de Medicina Interna la celda que dibuja una credencial y la
deja lista para usarla como plantilla: con huecos donde van el nombre, el
rol, el color y los textos del evento.

La usa generar.py; no hace falta ejecutarla a mano.
"""
import re
import zipfile
from pathlib import Path

ORIGINAL = Path(__file__).resolve().parent.parent / "recursos" / "Credenciales Medicina Interna.docx"

CALIBRI = '<w:rFonts w:ascii="Calibri" w:eastAsia="Calibri" w:hAnsi="Calibri" w:cs="Calibri"/>'


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


def _parrafo_con(celda: str, texto: str) -> tuple[int, int]:
    """Inicio y fin del párrafo cuyo texto visible empieza por `texto`.

    Se busca dentro de <w:t> porque los logos traen el mismo nombre en su
    texto alternativo.
    """
    i = re.search(r"<w:t(?: [^>]*)?>" + re.escape(texto), celda).start()
    ini = max(celda.rfind("<w:p>", 0, i), celda.rfind("<w:p ", 0, i))
    fin = celda.index("</w:p>", i) + len("</w:p>")
    return ini, fin


def _una_corrida(celda: str, texto: str, hueco: str) -> str:
    """Junta todas las corridas de texto del párrafo en una sola con `hueco`.

    Conserva el formato de la primera corrida. En el camino se van los
    campos sueltos que traía el Word (un INCLUDEPICTURE vacío en el título).
    """
    ini, fin = _parrafo_con(celda, texto)
    p = celda[ini:fin]
    ppr = re.search(r"<w:pPr>.*?</w:pPr>", p, re.S).group(0)
    rpr = re.search(r"<w:r><w:rPr>(.*?)</w:rPr><w:t", p, re.S).group(1)
    nuevo = f'<w:p>{ppr}<w:r><w:rPr>{rpr}</w:rPr><w:t xml:space="preserve">{hueco}</w:t></w:r></w:p>'
    return celda[:ini] + nuevo + celda[fin:]


def plantilla_celda():
    with zipfile.ZipFile(ORIGINAL) as z:
        doc = z.read("word/document.xml").decode("utf-8")

    # La primera credencial del documento es la de Medicina Interna.
    p = doc.index("<w:tbl>")
    tabla = bloque(doc, "w:tbl", p)
    celda = bloque(tabla, "w:tc", tabla.index("<w:tc>"))

    # Ruido de edición de Word que no aporta nada y puede chocar al repetir.
    celda = re.sub(r'\s+w:rsid[A-Za-z]*="[^"]*"', "", celda)
    celda = re.sub(r'\s+w14:(?:paraId|textId)="[^"]*"', "", celda)

    # Huecos de contenido: cada texto queda en una sola corrida.
    celda = _una_corrida(celda, "JORNADA", "{{TITULO}}")
    celda = _una_corrida(celda, "de Medicina Interna", "{{SUB}}")
    celda = _una_corrida(celda, "ACEM UCN", "{{INST}}")

    # El nombre venía sin formato (Times, a la izquierda): se deja como en
    # la página, centrado, en Calibri negrita gris.
    ini, fin = _parrafo_con(celda, "JUANA ARAYA")
    nombre = (
        '<w:p><w:pPr><w:pBdr><w:bottom w:val="single" w:sz="4" w:space="2" w:color="D9D9D9"/></w:pBdr>'
        '<w:spacing w:after="140"/><w:jc w:val="center"/></w:pPr>'
        f'<w:r><w:rPr>{CALIBRI}<w:b/><w:bCs/><w:caps/><w:color w:val="747474"/>'
        '<w:sz w:val="24"/><w:szCs w:val="24"/></w:rPr><w:t xml:space="preserve">{{NOMBRE}}</w:t></w:r></w:p>'
    )
    celda = celda[:ini] + nombre + celda[fin:]

    # La barra del rol: la tabla interna traía una segunda fila vacía que
    # se salía de la credencial; queda solo la fila con el rol.
    t = celda.index("<w:tbl>")
    interna = bloque(celda, "w:tbl", t)
    filas = re.findall(r"<w:tr>.*?</w:tr>", interna, re.S)
    if len(filas) > 1:
        sin_sobra = interna.replace("".join(filas[1:]), "")
        celda = celda.replace(interna, sin_sobra)
    celda = re.sub(r"<w:t>ASISTENTE?</w:t>", "<w:t>{{ROL}}</w:t>", celda)
    celda = celda.replace('w:fill="3E9FA0"', 'w:fill="{{COLOR}}"')
    celda = celda.replace('<w:bottom w:val="single" w:sz="4" w:space="0" w:color="4184B4"/>',
                          '<w:bottom w:val="single" w:sz="4" w:space="0" w:color="{{COLOR}}"/>')

    # Los identificadores de imagen tienen que ser únicos en todo el documento.
    n = [0]

    def numerar(m):
        n[0] += 1
        return f'<wp:docPr id="{{{{ID{n[0]}}}}}" name="Imagen {n[0]}"/>'

    celda = re.sub(r'<wp:docPr id="\d+" name="[^"]*"(?: descr="[^"]*")?/>', numerar, celda)
    celda = re.sub(r'<pic:cNvPr id="\d+" name="[^"]*"/>', '<pic:cNvPr id="0" name=""/>', celda)

    return celda, n[0]


if __name__ == "__main__":
    c, ids = plantilla_celda()
    print(f"{len(c)} bytes, {ids} imágenes")
    print("  imágenes usadas:", sorted(set(re.findall(r'r:embed="(rId\d+)"', c))))
    for hueco in ("{{TITULO}}", "{{SUB}}", "{{INST}}", "{{NOMBRE}}", "{{ROL}}", "{{COLOR}}"):
        print(f"  {hueco}: {c.count(hueco)}")
