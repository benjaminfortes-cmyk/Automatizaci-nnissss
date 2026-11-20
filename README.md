# Credenciales — 2ª Jornada de Investigación de Medicina Interna

Programa web para imprimir las credenciales del evento. Escribes o pegas
los nombres y salen maquetadas con el mismo diseño del Word original.

**Abrir:** https://benjaminfortes-cmyk.github.io/Automatizaci-nnissss/

También funciona sin internet: descarga `index.html` y ábrelo con doble clic.

## Qué hace

- Carga de nombres **uno por uno** (Enter agrega y deja el campo listo) o
  **pegando la lista** completa, un nombre por línea.
- Diseño del Word `recursos/Credenciales Medicina Interna.docx`: ondas
  azules y logos de ACEM UCN, UCN y Universidad del Alba.
- La barra del rol (ASISTENTE, ORGANIZADOR, EXPOSITOR) va siempre en el
  azul de "de Medicina Interna" (#4184B4).
  Con "Otro…" eliges cualquier color desde una paleta.
- Cada credencial mide **9,3 × 6,3 cm**, con separación entre tarjetas
  para pasar la tijera por el medio.
- 8 o 6 credenciales por hoja carta.
- Descarga en **PDF**, **Word (.docx)** o **imágenes PNG a 300 ppp**.
- La lista queda guardada en el navegador.

## Antes de imprimir

En el cuadro de impresión de Chrome, en "Más ajustes":

- **Escala: 100 %** (no "Ajustar al área de impresión")
- **Gráficos de fondo: activado**

Sin esto la barra de color no se imprime y las medidas salen achicadas.

## Carpeta `python`

Los archivos con los que se arma `index.html`: la plantilla, los
logotipos y los scripts que extraen el diseño del Word original.
No hace falta para usar el programa.

Para rehacer `js/datos.js` (logos y plantilla Word) después de un cambio:

```
python python/generar.py
```
