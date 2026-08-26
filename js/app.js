const LOGOS = DATOS.logos;
const DOCX = DATOS.word;
document.getElementById("fotoChica").src = DATOS.foto;
document.getElementById("fotoGrande").src = DATOS.foto;

const CLAVE = "acem-credenciales-v1";

const estado = {
  items: [],
  porHoja: 8,
  evento: {
    titulo: "2ª JORNADA DE TRAUMATOLOGÍA",
    sub:    "y Medicina del Ejercicio y Estilo de Vida",
    inst:   "ACEM UCN  ·  Universidad Católica del Norte"
  }
};
let rolActivo = "ASISTENTE";
let colorActivo = null;

const $ = s => document.querySelector(s);

function guardar(){
  try{ localStorage.setItem(CLAVE, JSON.stringify(estado)); }catch(e){}
}
function cargar(){
  try{
    const d = JSON.parse(localStorage.getItem(CLAVE) || "null");
    if(!d) return;
    if(Array.isArray(d.items)) estado.items = d.items;
    if(d.porHoja) estado.porHoja = d.porHoja;
    if(d.evento) Object.assign(estado.evento, d.evento);
  }catch(e){}
}

const ANCHO_NOMBRE = 249.41;
const BASE_NOMBRE  = 98.78;

const COLOR_ROL = {
  ASISTENTE:   "#3e9fa0",
  ORGANIZADOR: "#1d2d59",
  EXPOSITOR:   "#9e1f79"
};
const COLOR_POR_DEFECTO = "#1d2d59";

function colorDe(item){
  return item.color || COLOR_ROL[(item.rol || "").toUpperCase()] || COLOR_POR_DEFECTO;
}

const cvs = document.createElement("canvas").getContext("2d");

function tamanoNombre(texto){
  const aPx = 96/72;
  for(let s = 12; s >= 7; s -= 0.25){
    cvs.font = `700 ${s*aPx}px Calibri, Carlito, sans-serif`;
    if(cvs.measureText(texto).width / aPx <= ANCHO_NOMBRE) return s;
  }
  return 7;
}

function credencial(item){
  const nombre = (item.nombre || "").toUpperCase().trim();
  const s = tamanoNombre(nombre);
  const top = (BASE_NOMBRE - 0.75*s).toFixed(2);
  const ev = estado.evento;

  const el = document.createElement("div");
  el.className = "cred";
  el.style.setProperty("--rol", colorDe(item));
  el.innerHTML = `
    <img src="${LOGOS.arco}"     style="left:.05pt;  top:.18pt;  width:36.45pt; height:33.6pt">
    <span class="arco-der"><img src="${LOGOS.arco}"></span>
    <img src="${LOGOS.acem}"     style="left:119.94pt; top:2.33pt; width:23.75pt; height:26.2pt">

    <div class="t titulo">${esc(ev.titulo)}</div>
    <div class="t subtitulo">${esc(ev.sub)}</div>
    <div class="t inst">${esc(ev.inst)}</div>

    <div class="t nombre" style="top:${top}pt; font-size:${s}pt">${esc(nombre)}</div>
    <div class="regla"></div>

    <div class="t auspician">Auspician</div>
    <img src="${LOGOS.bago}"     style="left:8.01pt;  top:131.97pt; width:27.39pt;height:9.4pt">
    <img src="${LOGOS.double}"   style="left:40.39pt; top:132.13pt; width:47.7pt; height:11.28pt">
    <img src="${LOGOS.blunding}" style="left:93.1pt;  top:132.24pt; width:44.66pt;height:10.52pt">
    <img src="${LOGOS.sbsports}" style="left:142.76pt;top:131.19pt; width:43.68pt;height:11.5pt">
    <img src="${LOGOS.sanbarto}" style="left:191.43pt;top:129.06pt; width:20.36pt;height:17.81pt">
    <img src="${LOGOS.essity}"   style="left:216.8pt; top:132.3pt;  width:38.82pt;height:10pt">

    <div class="barra"></div>
    <div class="rol">${esc(item.rol)}</div>`;
  return el;
}

function esc(t){
  return String(t).replace(/[&<>"]/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
}

const SEPARACION = { 8:"3mm", 6:"6mm" };

function pintarHojas(){
  const cont = $("#sheets");
  cont.innerHTML = "";
  const n = estado.porHoja;
  const sep = SEPARACION[n] || "3mm";
  const hojas = Math.max(1, Math.ceil(estado.items.length / n));

  for(let h = 0; h < hojas; h++){
    const wrap = document.createElement("div");
    wrap.className = "sheet-wrap";

    const tag = document.createElement("span");
    tag.className = "sheet-tag";
    tag.textContent = `Hoja ${h+1} de ${hojas}`;
    wrap.appendChild(tag);

    const hoja = document.createElement("div");
    hoja.className = "sheet";
    const grid = document.createElement("div");
    grid.className = "grid";
    grid.style.setProperty("--sep", sep);
    estado.items.slice(h*n, h*n + n).forEach(it => grid.appendChild(credencial(it)));
    hoja.appendChild(grid);
    wrap.appendChild(hoja);
    cont.appendChild(wrap);
  }
  escalar();
}

function escalar(){
  const mesa = document.querySelector(".table");
  if(!mesa) return;
  const disponible = mesa.clientWidth - 72;
  document.querySelectorAll(".sheet-wrap").forEach(wrap => {
    const hoja = wrap.querySelector(".sheet");
    const ancho = hoja.offsetWidth, alto = hoja.offsetHeight;
    const z = Math.min(1, disponible / ancho);
    hoja.style.transform = `scale(${z})`;
    hoja.style.marginLeft = ((disponible - ancho*z)/2) + "px";
    wrap.style.width  = disponible + "px";
    wrap.style.height = (alto*z) + "px";
  });
}
window.addEventListener("resize", escalar);

const mesa = document.querySelector(".table");
const barra = document.querySelector(".table__bar");
mesa.addEventListener("scroll", () => {
  barra.classList.toggle("table__bar--oculta", mesa.scrollTop > 12);
}, { passive: true });

function pintarLista(){
  const ul = $("#roster");
  ul.innerHTML = "";
  const n = estado.porHoja;

  estado.items.forEach((it, i) => {
    const li = document.createElement("li");
    li.className = "row";

    const pos = document.createElement("span");
    pos.className = "row__pos";
    pos.textContent = `H${Math.floor(i/n)+1}·${i % n + 1}`;
    pos.title = `Hoja ${Math.floor(i/n)+1}, posición ${i % n + 1}`;

    const inp = document.createElement("input");
    inp.className = "row__name";
    inp.value = it.nombre;
    inp.setAttribute("aria-label", "Nombre");
    inp.addEventListener("input", () => {
      it.nombre = inp.value; guardar(); pintarHojas();
    });

    const tinta = document.createElement("span");
    tinta.className = "row__pip";
    tinta.style.background = colorDe(it);

    const rol = document.createElement("input");
    rol.className = "row__role";
    rol.value = it.rol;
    rol.setAttribute("aria-label", "Rol");
    rol.addEventListener("input", () => {
      it.rol = rol.value.toUpperCase();
      if(COLOR_ROL[it.rol]) delete it.color;
      tinta.style.background = colorDe(it);
      guardar(); pintarHojas();
    });

    const del = document.createElement("button");
    del.className = "row__del";
    del.textContent = "×";
    del.title = "Quitar";
    del.setAttribute("aria-label", `Quitar a ${it.nombre}`);
    del.addEventListener("click", () => {
      estado.items.splice(i, 1); guardar(); pintarTodo();
    });

    li.append(pos, inp, tinta, rol, del);
    ul.appendChild(li);
  });

  const total = estado.items.length;
  $("#vacio").style.display = total ? "none" : "";
  $("#conteo").textContent = total === 1 ? "1 credencial" : `${total} credenciales`;
  $("#borrarTodo").hidden = !total;

  const hojas = Math.max(1, Math.ceil(total / estado.porHoja));
  $("#resumen").innerHTML = total
    ? `<b>${total}</b> credenciales · <b>${hojas}</b> ${hojas===1?"hoja":"hojas"}`
    : "Sin credenciales";
}

function pintarNotaHoja(){
  const n    = estado.porHoja;
  const sep  = parseFloat(SEPARACION[n]);
  const fila = n / 2;
  const coma = x => x.toFixed(1).replace(".", ",");
  const lado   = (215.9 - (2*93 + sep)) / 2;
  const arriba = (279.4 - (fila*63 + (fila-1)*sep)) / 2;
  $("#notaHoja").innerHTML =
    `Credencial <b>9,3 × 6,3 cm</b> · separación para cortar <b>${coma(sep)} mm</b> ` +
    `· margen libre <b>${coma(lado)} mm</b> a los lados y <b>${coma(arriba)} mm</b> arriba y abajo.`;
}

function pintarTodo(){ pintarLista(); pintarHojas(); pintarNotaHoja(); }

$("#roles").addEventListener("click", e => {
  const b = e.target.closest(".role");
  if(!b) return;
  document.querySelectorAll(".role").forEach(x => x.setAttribute("aria-pressed", x === b));
  const caja = $("#cajaOtro");
  if(b.dataset.rol === "__otro"){
    caja.classList.add("on"); $("#rolOtro").focus();
    rolActivo = $("#rolOtro").value.toUpperCase() || "ASISTENTE";
    colorActivo = $("#tinta").value;
  }else{
    caja.classList.remove("on");
    rolActivo = b.dataset.rol;
    colorActivo = null;
  }
});
$("#rolOtro").addEventListener("input", e => {
  rolActivo = e.target.value.toUpperCase() || "ASISTENTE";
});
$("#tinta").addEventListener("input", e => {
  colorActivo = e.target.value;
  $("#tintaHex").textContent = colorActivo.toUpperCase();
});

let modo = "uno";

$("#modos").addEventListener("click", e => {
  const b = e.target.closest(".modo");
  if(!b) return;
  modo = b.dataset.modo;
  document.querySelectorAll(".modo").forEach(x => x.setAttribute("aria-pressed", x === b));
  $("#panelUno").hidden  = modo !== "uno";
  $("#panelLote").hidden = modo !== "lote";
  (modo === "uno" ? $("#nombreUno") : $("#nombres")).focus();
});

function agregarLinea(linea){
  const p = linea.split("|");
  const nombre = p[0].trim();
  if(!nombre) return false;
  const rol = (p[1] || rolActivo).trim().toUpperCase();
  const item = { nombre, rol };

  if(!COLOR_ROL[rol] && colorActivo) item.color = colorActivo;
  estado.items.push(item);
  return true;
}

$("#agregar").addEventListener("click", () => {
  const campo = modo === "uno" ? $("#nombreUno") : $("#nombres");
  const lineas = campo.value.split(/\r?\n/).map(l => l.trim()).filter(Boolean);
  if(!lineas.length){ campo.focus(); return; }

  lineas.forEach(agregarLinea);
  campo.value = "";
  guardar(); pintarTodo();
  campo.focus();

  if(modo === "lote") document.querySelector(".table").scrollTo({ top:0, behavior:"smooth" });
});

$("#nombreUno").addEventListener("keydown", e => {
  if(e.key === "Enter"){ e.preventDefault(); $("#agregar").click(); }
});
$("#nombres").addEventListener("keydown", e => {
  if((e.ctrlKey || e.metaKey) && e.key === "Enter") $("#agregar").click();
});

$("#nombreUno").addEventListener("paste", e => {
  const txt = (e.clipboardData || window.clipboardData).getData("text");
  if(!/\r?\n/.test(txt.trim())) return;
  e.preventDefault();
  txt.split(/\r?\n/).map(l => l.trim()).filter(Boolean).forEach(agregarLinea);
  guardar(); pintarTodo();
});

function armarBorrado(boton, textoNormal, textoConfirma){
  let pedido = false, reloj;

  const volver = () => {
    clearTimeout(reloj);
    pedido = false;
    boton.textContent = textoNormal;
    boton.classList.remove("confirma");
  };

  boton.addEventListener("click", () => {
    if(!estado.items.length){ avisar("La lista ya está vacía."); return; }

    if(!pedido){
      pedido = true;
      boton.textContent = textoConfirma;
      boton.classList.add("confirma");
      reloj = setTimeout(volver, 4000);
      return;
    }

    volver();
    estado.items = [];
    guardar(); pintarTodo();
    avisar("Lista borrada. Puedes empezar otra.");
  });

}

armarBorrado($("#borrarTodo"), "Borrar todo", "¿Seguro?");
armarBorrado($("#borrarPie"), "Borrar la lista", "¿Seguro? Presiona otra vez");

$("#imprimir").addEventListener("click", () => {
  if(!estado.items.length){ $("#nombres").focus(); return; }
  window.print();
});

$("#porHoja").addEventListener("click", e => {
  const b = e.target.closest(".opt");
  if(!b) return;
  document.querySelectorAll(".opt").forEach(x => x.setAttribute("aria-pressed", x === b));
  estado.porHoja = +b.dataset.n;
  guardar(); pintarTodo();
});

[["#fTitulo","titulo","#hTitulo"],["#fSub","sub",null],["#fInst","inst","#hInst"]]
  .forEach(([sel, campo, espejo]) => {
    $(sel).addEventListener("input", e => {
      estado.evento[campo] = e.target.value;
      if(espejo) $(espejo).textContent = e.target.value;
      guardar(); pintarHojas();
    });
  });

function avisar(txt){ $("#estado").textContent = txt || ""; }

function descargar(blob, nombre){
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = nombre;
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 2000);
}

function bytesDe(dataUri){
  const bin = atob(dataUri.slice(dataUri.indexOf(",") + 1));
  const u = new Uint8Array(bin.length);
  for(let i = 0; i < bin.length; i++) u[i] = bin.charCodeAt(i);
  return u;
}

function nombreArchivo(){
  const base = (estado.evento.titulo || "Credenciales")
    .replace(/[\\/:*?"<>|]/g, "").trim().slice(0, 60);
  return "Credenciales - " + (base || "evento");
}

const CRC_TABLA = (() => {
  const t = new Uint32Array(256);
  for(let n = 0; n < 256; n++){
    let c = n;
    for(let k = 0; k < 8; k++) c = (c & 1) ? (0xEDB88320 ^ (c >>> 1)) : (c >>> 1);
    t[n] = c >>> 0;
  }
  return t;
})();

function crc32(b){
  let c = 0xFFFFFFFF;
  for(let i = 0; i < b.length; i++) c = CRC_TABLA[(c ^ b[i]) & 0xFF] ^ (c >>> 8);
  return (c ^ 0xFFFFFFFF) >>> 0;
}

async function comprimir(b){
  if(typeof CompressionStream === "undefined") return null;
  const flujo = new Blob([b]).stream().pipeThrough(new CompressionStream("deflate-raw"));
  return new Uint8Array(await new Response(flujo).arrayBuffer());
}

const HORA_FIJA  = 0x6000;
const FECHA_FIJA = 0x5A21;

async function crearZip(archivos){
  const enc = new TextEncoder();
  const cuerpo = [], central = [];
  let salto = 0;

  for(const a of archivos){
    const nombre = enc.encode(a.nombre);
    const crudo = a.datos;
    const suma = crc32(crudo);
    let datos = await comprimir(crudo), metodo = 8;
    if(!datos || datos.length >= crudo.length){ datos = crudo; metodo = 0; }

    const local = new DataView(new ArrayBuffer(30));
    local.setUint32(0,  0x04034b50, true);
    local.setUint16(4,  20, true);
    local.setUint16(6,  0x0800, true);
    local.setUint16(8,  metodo, true);
    local.setUint16(10, HORA_FIJA, true);
    local.setUint16(12, FECHA_FIJA, true);
    local.setUint32(14, suma, true);
    local.setUint32(18, datos.length, true);
    local.setUint32(22, crudo.length, true);
    local.setUint16(26, nombre.length, true);
    local.setUint16(28, 0, true);
    cuerpo.push(new Uint8Array(local.buffer), nombre, datos);

    const dir = new DataView(new ArrayBuffer(46));
    dir.setUint32(0,  0x02014b50, true);
    dir.setUint16(4,  20, true);
    dir.setUint16(6,  20, true);
    dir.setUint16(8,  0x0800, true);
    dir.setUint16(10, metodo, true);
    dir.setUint16(12, HORA_FIJA, true);
    dir.setUint16(14, FECHA_FIJA, true);
    dir.setUint32(16, suma, true);
    dir.setUint32(20, datos.length, true);
    dir.setUint32(24, crudo.length, true);
    dir.setUint16(28, nombre.length, true);
    dir.setUint32(42, salto, true);
    central.push(new Uint8Array(dir.buffer), nombre);

    salto += 30 + nombre.length + datos.length;
  }

  const largoCentral = central.reduce((s, p) => s + p.length, 0);
  const fin = new DataView(new ArrayBuffer(22));
  fin.setUint32(0, 0x06054b50, true);
  fin.setUint16(8, archivos.length, true);
  fin.setUint16(10, archivos.length, true);
  fin.setUint32(12, largoCentral, true);
  fin.setUint32(16, salto, true);

  return new Blob([...cuerpo, ...central, new Uint8Array(fin.buffer)]);
}

function xmlSeguro(t){
  return String(t).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

function documentoWord(){
  const cfg = DOCX.hoja[estado.porHoja] || DOCX.hoja[8];
  const sep = cfg.sep;
  const anchoTabla = 2 * DOCX.anchoCred + sep;
  const margenH = Math.floor((DOCX.anchoHoja - anchoTabla) / 2);
  let id = 0;

  const celda = it => DOCX.celda
    .replace("{{TITULO}}", xmlSeguro(estado.evento.titulo))
    .replace("{{SUB}}",    xmlSeguro(estado.evento.sub))
    .replace("{{INST}}",   xmlSeguro(estado.evento.inst))
    .replace("{{NOMBRE}}", xmlSeguro(it.nombre.toUpperCase()))
    .replace("{{ROL}}",    xmlSeguro(it.rol.toUpperCase()))
    .replace("{{COLOR}}",  colorDe(it).replace("#", "").toUpperCase())
    .replace(/<wp:docPr id="\{\{ID\d+\}\}" name="[^"]*"\/>/g,
             () => `<wp:docPr id="${++id}" name="Imagen ${id}"/>`);

  const hueca = ancho =>
    `<w:tc><w:tcPr><w:tcW w:w="${ancho}" w:type="dxa"/></w:tcPr>` +
    `<w:p><w:pPr><w:rPr><w:sz w:val="2"/></w:rPr></w:pPr></w:p></w:tc>`;

  const colSep = hueca(sep);
  const filaSep =
    `<w:tr><w:trPr><w:trHeight w:hRule="exact" w:val="${sep}"/><w:cantSplit/></w:trPr>` +
    hueca(DOCX.anchoCred) + colSep + hueca(DOCX.anchoCred) + "</w:tr>";

  let filas = "";
  for(let i = 0; i < estado.items.length; i += 2){
    const a = estado.items[i], b = estado.items[i + 1];
    filas +=
      `<w:tr><w:trPr><w:trHeight w:hRule="exact" w:val="${DOCX.altoCred}"/><w:cantSplit/></w:trPr>` +
      celda(a) + colSep + (b ? celda(b) : hueca(DOCX.anchoCred)) + "</w:tr>" + filaSep;
  }

  const tabla =
    `<w:tbl><w:tblPr><w:tblW w:w="${anchoTabla}" w:type="dxa"/><w:jc w:val="center"/>` +
    DOCX.sinBordes +
    '<w:tblCellMar><w:top w:w="0" w:type="dxa"/><w:left w:w="0" w:type="dxa"/>' +
    '<w:bottom w:w="0" w:type="dxa"/><w:right w:w="0" w:type="dxa"/></w:tblCellMar>' +
    '<w:tblLayout w:type="fixed"/></w:tblPr>' +
    `<w:tblGrid><w:gridCol w:w="${DOCX.anchoCred}"/><w:gridCol w:w="${sep}"/>` +
    `<w:gridCol w:w="${DOCX.anchoCred}"/></w:tblGrid>` + filas + "</w:tbl>";

  const sect =
    `<w:sectPr><w:pgSz w:w="${DOCX.anchoHoja}" w:h="15840"/>` +
    `<w:pgMar w:top="${cfg.margenV}" w:right="${margenH}" w:bottom="${cfg.margenV}" ` +
    `w:left="${margenH}" w:header="0" w:footer="0" w:gutter="0"/></w:sectPr>`;

  return DOCX.cabecera + DOCX.raiz + "<w:body>" + tabla +
         '<w:p><w:pPr><w:rPr><w:sz w:val="2"/></w:rPr></w:pPr></w:p>' +
         sect + "</w:body></w:document>";
}

async function descargarWord(){
  const enc = new TextEncoder();
  const archivos = [
    { nombre: "[Content_Types].xml",         datos: enc.encode(DOCX.contentTypes) },
    { nombre: "_rels/.rels",                 datos: enc.encode(DOCX.rels) },
    { nombre: "word/document.xml",           datos: enc.encode(documentoWord()) },
    { nombre: "word/_rels/document.xml.rels",datos: enc.encode(DOCX.docRels) },
    { nombre: "word/styles.xml",             datos: enc.encode(DOCX.styles) }
  ];
  DOCX.imagenes.forEach((clave, i) => {
    archivos.push({ nombre: `word/media/image${i + 1}.png`, datos: bytesDe(LOGOS[clave]) });
  });
  descargar(await crearZip(archivos), nombreArchivo() + ".docx");
}

function estilosCredencial(){
  let css = "";
  for(const hoja of document.styleSheets){
    let reglas;
    try{ reglas = hoja.cssRules; }catch(e){ continue; }
    for(const r of reglas){

      if(r.selectorText && /(^|,\s*)(\.cred\b|:root$)/.test(r.selectorText)) css += r.cssText + "\n";
    }
  }
  return css;
}

async function pngDe(item, css, escala){
  const ancho = 93 / 25.4 * 96, alto = 63 / 25.4 * 96;
  const caja = document.createElement("div");
  caja.setAttribute("xmlns", "http://www.w3.org/1999/xhtml");
  const est = document.createElement("style");
  est.textContent = css;
  caja.append(est, credencial(item));

  const svg =
    `<svg xmlns="http://www.w3.org/2000/svg" width="${ancho}" height="${alto}">` +
    `<foreignObject width="100%" height="100%">` +
    new XMLSerializer().serializeToString(caja) +
    "</foreignObject></svg>";

  const img = new Image();
  img.src = "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svg);
  await img.decode();

  const lienzo = document.createElement("canvas");
  lienzo.width = Math.round(ancho * escala);
  lienzo.height = Math.round(alto * escala);
  const ctx = lienzo.getContext("2d");
  ctx.fillStyle = "#fff";
  ctx.fillRect(0, 0, lienzo.width, lienzo.height);
  ctx.drawImage(img, 0, 0, lienzo.width, lienzo.height);

  return new Promise(r => lienzo.toBlob(r, "image/png"));
}

async function descargarImagenes(){
  const css = estilosCredencial();
  const escala = 300 / 96;
  const total = estado.items.length;
  const limpio = t => t.replace(/[\\/:*?"<>|]/g, "").trim() || "sin nombre";

  if(total === 1){
    const blob = await pngDe(estado.items[0], css, escala);
    descargar(blob, limpio(estado.items[0].nombre.toUpperCase()) + ".png");
    return;
  }

  const archivos = [];
  for(let i = 0; i < total; i++){
    avisar(`Generando imágenes… ${i + 1} de ${total}`);
    const blob = await pngDe(estado.items[i], css, escala);
    const n = String(i + 1).padStart(String(total).length, "0");
    archivos.push({
      nombre: `${n} - ${limpio(estado.items[i].nombre.toUpperCase())}.png`,
      datos: new Uint8Array(await blob.arrayBuffer())
    });
  }
  avisar("Comprimiendo…");
  descargar(await crearZip(archivos), nombreArchivo() + " (imagenes).zip");
}

async function conAviso(boton, tarea, listo){
  if(!estado.items.length){ avisar("Primero agrega nombres a la lista."); return; }
  const botones = document.querySelectorAll(".descargas .btn");
  botones.forEach(b => b.disabled = true);
  avisar("Preparando…");
  try{
    await tarea();
    avisar(listo);
  }catch(e){
    avisar("No se pudo generar el archivo: " + e.message);
  }finally{
    botones.forEach(b => b.disabled = false);
  }
}

$("#dlWord").addEventListener("click", () =>
  conAviso(null, descargarWord, "Word descargado."));

$("#dlPng").addEventListener("click", () =>
  conAviso(null, descargarImagenes, "Imágenes descargadas (300 ppp)."));

$("#dlPdf").addEventListener("click", () => {
  if(!estado.items.length){ avisar("Primero agrega nombres a la lista."); return; }
  avisar('En destino elige "Guardar como PDF" y deja la escala en 100 %.');
  setTimeout(() => window.print(), 400);
});

const visor = $("#visor");
const botonFoto = $("#verFoto");

function cerrarVisor(){
  visor.classList.remove("on");
  botonFoto.focus();
}

botonFoto.addEventListener("click", () => visor.classList.add("on"));
visor.addEventListener("click", cerrarVisor);
document.addEventListener("keydown", e => {
  if(e.key === "Escape" && visor.classList.contains("on")) cerrarVisor();
});

cargar();
$("#fTitulo").value = estado.evento.titulo;
$("#fSub").value    = estado.evento.sub;
$("#fInst").value   = estado.evento.inst;
$("#hTitulo").textContent = estado.evento.titulo;
$("#hInst").textContent   = estado.evento.inst;
document.querySelectorAll(".opt").forEach(x =>
  x.setAttribute("aria-pressed", +x.dataset.n === estado.porHoja));
pintarTodo();
