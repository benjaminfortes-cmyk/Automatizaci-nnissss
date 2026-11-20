"""
Piezas del .docx que descarga la aplicación.

Aquí viven la plantilla de la celda, los XML de apoyo y las medidas de
página. generar.py las incrusta en Credenciales.html; el navegador
arma el archivo con las mismas reglas.

Ejecutar este archivo a mano genera un .docx de prueba en la carpeta
temporal para revisarlo con Word.
"""
import base64
import re
import zipfile
from pathlib import Path

from extraer_word import plantilla_celda

AQUI = Path(__file__).resolve().parent

# --- medidas de página, en twips (1 mm = 56,7 twips) ---------------------
# La separación se hace con una columna y una fila vacías entre tarjetas:
# es la única forma en que Word reparte las páginas siempre igual.
# El margen deja algo de holgura para que entren justo las filas previstas.
HOJA = {
    8: {"filas": 4, "sep": 181, "margenV": 400},   # sep 3,0 mm
    6: {"filas": 3, "sep": 351, "margenV": 2000},  # sep 6,0 mm
}
# Mismo ajuste que en el alto: Word encoge un poco el ancho dibujado.
ANCHO_CRED = 5272 + 20   # 93,0 mm reales
ANCHO_HOJA = 12240  # carta

# Word dibuja la fila 110 twips más alta de lo que se le pide (los bordes
# de la celda van por fuera del alto exacto). Se descuentan aquí para que
# la credencial impresa mida los 63,0 mm de verdad.
ALTO_CRED = 3572 - 110

RAIZ = (
    '<w:document '
    'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
    'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
    'xmlns:wp14="http://schemas.microsoft.com/office/word/2010/wordprocessingDrawing" '
    'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
    'xmlns:pic="http://schemas.openxmlformats.org/drawingml/2006/picture" '
    'xmlns:a14="http://schemas.microsoft.com/office/drawing/2010/main" '
    'xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" '
    'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
    'xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" '
    'mc:Ignorable="w14 wp14">'
)

CABECERA = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\r\n'

CONTENT_TYPES = CABECERA + (
    '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
    '<Default Extension="png" ContentType="image/png"/>'
    '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
    '<Default Extension="xml" ContentType="application/xml"/>'
    '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
    '<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>'
    "</Types>"
)

RELS = CABECERA + (
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
    "</Relationships>"
)

_IMG = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"
DOC_RELS = CABECERA + (
    '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
    '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>'
    + "".join(
        f'<Relationship Id="rId{n + 4}" Type="{_IMG}" Target="media/image{n}.png"/>'
        for n in range(1, 6)
    )
    + "</Relationships>"
)

STYLES = CABECERA + (
    '<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
    "<w:docDefaults><w:rPrDefault><w:rPr>"
    '<w:rFonts w:ascii="Times New Roman" w:eastAsia="Times New Roman" '
    'w:hAnsi="Times New Roman" w:cs="Times New Roman"/>'
    '<w:lang w:val="es-CL"/></w:rPr></w:rPrDefault><w:pPrDefault/></w:docDefaults>'
    '<w:style w:type="paragraph" w:default="1" w:styleId="Normal">'
    '<w:name w:val="Normal"/><w:qFormat/></w:style>'
    "</w:styles>"
)


def escapar(t: str) -> str:
    return (
        str(t)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def documento(items, evento, por_hoja, celda_plantilla):
    """Arma word/document.xml con una celda por credencial."""
    cfg = HOJA.get(por_hoja, HOJA[8])
    sep = cfg["sep"]
    ancho_tabla = 2 * ANCHO_CRED + sep
    margen_h = (ANCHO_HOJA - ancho_tabla) // 2

    ident = [0]

    def celda(item):
        c = celda_plantilla
        c = c.replace("{{TITULO}}", escapar(evento["titulo"]))
        c = c.replace("{{SUB}}", escapar(evento["sub"]))
        c = c.replace("{{INST}}", escapar(evento["inst"]))
        c = c.replace("{{NOMBRE}}", escapar(item["nombre"].upper()))
        c = c.replace("{{ROL}}", escapar(item["rol"].upper()))
        c = c.replace("{{COLOR}}", item["color"].lstrip("#").upper())

        def num(m):
            ident[0] += 1
            return f'<wp:docPr id="{ident[0]}" name="Imagen {ident[0]}"/>'

        return re.sub(r'<wp:docPr id="\{\{ID\d+\}\}" name="[^"]*"/>', num, c)

    def hueca(ancho):
        return (
            f'<w:tc><w:tcPr><w:tcW w:w="{ancho}" w:type="dxa"/></w:tcPr>'
            '<w:p><w:pPr><w:rPr><w:sz w:val="2"/></w:rPr></w:pPr></w:p></w:tc>'
        )

    columna_sep = hueca(sep)

    # Cada fila de tarjetas lleva debajo una fila vacía: así toda página
    # empieza con una tarjeta y siempre caben las mismas por hoja.
    fila_sep = (
        f'<w:tr><w:trPr><w:trHeight w:hRule="exact" w:val="{sep}"/><w:cantSplit/></w:trPr>'
        + hueca(ANCHO_CRED) + columna_sep + hueca(ANCHO_CRED) + "</w:tr>"
    )

    filas = []
    for i in range(0, len(items), 2):
        par = items[i : i + 2]
        celdas = celda(par[0]) + columna_sep
        celdas += celda(par[1]) if len(par) == 2 else hueca(ANCHO_CRED)
        filas.append(
            "<w:tr><w:trPr>"
            f'<w:trHeight w:hRule="exact" w:val="{ALTO_CRED}"/>'
            "<w:cantSplit/></w:trPr>" + celdas + "</w:tr>"
        )
        filas.append(fila_sep)

    tabla = (
        "<w:tbl><w:tblPr>"
        f'<w:tblW w:w="{ancho_tabla}" w:type="dxa"/>'
        '<w:jc w:val="center"/>'
        '<w:tblBorders>'
        '<w:top w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        '<w:left w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        '<w:bottom w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        '<w:right w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        '<w:insideH w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        '<w:insideV w:val="none" w:sz="0" w:space="0" w:color="auto"/>'
        "</w:tblBorders>"
        '<w:tblCellMar><w:top w:w="0" w:type="dxa"/><w:left w:w="0" w:type="dxa"/>'
        '<w:bottom w:w="0" w:type="dxa"/><w:right w:w="0" w:type="dxa"/></w:tblCellMar>'
        '<w:tblLayout w:type="fixed"/>'
        "</w:tblPr>"
        f'<w:tblGrid><w:gridCol w:w="{ANCHO_CRED}"/><w:gridCol w:w="{sep}"/>'
        f'<w:gridCol w:w="{ANCHO_CRED}"/></w:tblGrid>'
        + "".join(filas)
        + "</w:tbl>"
    )

    sect = (
        "<w:sectPr>"
        f'<w:pgSz w:w="{ANCHO_HOJA}" w:h="15840"/>'
        f'<w:pgMar w:top="{cfg["margenV"]}" w:right="{margen_h}" '
        f'w:bottom="{cfg["margenV"]}" w:left="{margen_h}" '
        'w:header="0" w:footer="0" w:gutter="0"/>'
        "</w:sectPr>"
    )

    cuerpo = tabla + '<w:p><w:pPr><w:rPr><w:sz w:val="2"/></w:rPr></w:pPr></w:p>' + sect
    return CABECERA + RAIZ + "<w:body>" + cuerpo + "</w:body></w:document>"


def armar(items, evento, por_hoja, destino: Path):
    celda_plantilla, _ = plantilla_celda()
    doc = documento(items, evento, por_hoja, celda_plantilla)

    with zipfile.ZipFile(destino, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", CONTENT_TYPES)
        z.writestr("_rels/.rels", RELS)
        z.writestr("word/document.xml", doc)
        z.writestr("word/_rels/document.xml.rels", DOC_RELS)
        z.writestr("word/styles.xml", STYLES)
        for n in ORDEN:
            z.writestr(f"word/media/image{n}.png", (AQUI.parent / "recursos" / "logos" / ORDEN[n]).read_bytes())
    return destino


# El Word de Medicina Interna numera las imágenes así (rId5 = image1, ...);
# la plantilla las llama por ese nombre.
ORDEN = {
    1: "ola-der.png",
    2: "ola-izq.png",
    3: "alba.png",
    4: "acem.png",
    5: "ucn.png",
}


if __name__ == "__main__":
    import tempfile

    evento = {
        "titulo": "2ª JORNADA DE INVESTIGACIÓN",
        "sub": "de Medicina Interna",
        "inst": "ACEM UCN  ·  Universidad Católica del Norte  ·  Universidad del Alba",
    }
    items = (
        [{"nombre": f"Asistente {i}", "rol": "ASISTENTE", "color": "#4184b4"} for i in range(1, 5)]
        + [{"nombre": f"Organizador {i}", "rol": "ORGANIZADOR", "color": "#4184b4"} for i in range(1, 5)]
        + [{"nombre": "Dra. Sandra Mahecha", "rol": "EXPOSITOR", "color": "#4184b4"}]
    )
    salida = Path(tempfile.gettempdir()) / "prueba_credenciales.docx"
    armar(items, evento, 8, salida)
    print(f"Listo: {salida}  ({salida.stat().st_size/1024:.0f} KB)")
