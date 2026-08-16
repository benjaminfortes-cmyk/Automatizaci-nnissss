"""
Quita los comentarios de la página antes de publicarla, para que el
código que se ve con Ctrl+U quede limpio.

Los comentarios se quedan en plantilla.html, que es donde sirven.
"""
import re

ABRE_REGEX = set("(,=:[!&|?{};+-*%~^\n")


def _js(src: str) -> str:
    """Quita comentarios de JavaScript sin tocar textos ni expresiones regulares."""
    salida = []
    dentro = None          # None, ', ", ` o "regex"
    i, n = 0, len(src)

    def ultimo_util():
        for c in reversed(salida):
            if not c.isspace():
                return c
        return "\n"

    while i < n:
        c = src[i]
        par = src[i : i + 2]

        if dentro is None:
            if par == "//":
                salto = src.find("\n", i)
                i = n if salto == -1 else salto
                continue
            if par == "/*":
                fin = src.find("*/", i + 2)
                i = n if fin == -1 else fin + 2
                continue
            if c in "'\"`":
                dentro = c
            elif c == "/" and ultimo_util() in ABRE_REGEX:
                dentro = "regex"
            salida.append(c)
            i += 1
            continue

        if c == "\\":
            salida.append(src[i : i + 2])
            i += 2
            continue

        if dentro == "regex":
            if c == "[":
                # Dentro de una clase, / y las comillas no cierran nada.
                j = i + 1
                while j < n and src[j] != "]":
                    j += 2 if src[j] == "\\" else 1
                salida.append(src[i : j + 1])
                i = j + 1
                continue
            if c == "/":
                dentro = None
        elif c == dentro:
            dentro = None

        salida.append(c)
        i += 1

    return "".join(salida)


def _bloques(texto: str, etiqueta: str, funcion) -> str:
    patron = re.compile(f"(<{etiqueta}[^>]*>)(.*?)(</{etiqueta}>)", re.S)
    return patron.sub(lambda m: m.group(1) + funcion(m.group(2)) + m.group(3), texto)


def limpiar(html: str) -> str:
    html = re.sub(r"<!--(?!\[if).*?-->", "", html, flags=re.S)
    html = _bloques(html, "style", lambda s: re.sub(r"/\*.*?\*/", "", s, flags=re.S))
    html = _bloques(html, "script", _js)

    # Deja como mucho una línea en blanco seguida y sin espacios al final.
    html = re.sub(r"[ \t]+$", "", html, flags=re.M)
    html = re.sub(r"\n{3,}", "\n\n", html)
    return html
