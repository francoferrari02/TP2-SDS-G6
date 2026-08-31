import fs from "node:fs/promises";
import { readFileSync } from "node:fs";
import path from "node:path";
import { Presentation, PresentationFile } from "@oai/artifact-tool";

const ROOT = "/Users/francoferrari/Desktop/ITBA/SimuTP2";
const FIG = path.join(ROOT, "figures/final_production_v1");
const SNAP = path.join(ROOT, "figures/reference_snapshots_v1");
const OUT = path.join(ROOT, "output/presentation/TP2_Bandadas_Borrador_Presentacion.pptx");
const PREVIEW = path.join(ROOT, ".tmp/presentation_build/previews");

const W = 1280, H = 720;
const C = { navy: "#111A42", indigo: "#3B36B8", blue: "#5562D9", pale: "#F5F6FA", ink: "#161A2C", muted: "#5F6578", line: "#D8DBE7", white: "#FFFFFF", softIndigo: "#ECEBFF", green: "#167D69", amber: "#C27819" };
const FONT = "Aptos";
const deck = Presentation.create({ slideSize: { width: W, height: H } });

function addShape(slide, geometry, position, fill = "none", line = { style: "solid", fill: "none", width: 0 }, name = undefined) {
  return slide.shapes.add({ geometry, position, fill, line, name });
}

function addText(slide, text, pos, size = 24, color = C.ink, bold = false, options = {}) {
  const box = addShape(slide, "textbox", pos, options.fill ?? "none", options.line ?? { style: "solid", fill: "none", width: 0 }, options.name);
  box.text = text;
  box.text.style = { fontFamily: FONT, fontSize: size, color, bold, alignment: options.align ?? "left", verticalAlignment: options.valign ?? "middle", ...(options.style ?? {}) };
  return box;
}

function addRule(slide, x, y, w, color = C.indigo, width = 4) {
  return addShape(slide, "line", { left: x, top: y, width: w, height: 0 }, "none", { style: "solid", fill: color, width });
}

function addTitle(slide, title, section = "") {
  addText(slide, section.toUpperCase(), { left: 66, top: 34, width: 410, height: 24 }, 15, C.indigo, true);
  addText(slide, title, { left: 66, top: 64, width: 1148, height: 48 }, 35, C.navy, true);
  addRule(slide, 66, 126, 1148, C.line, 1);
}

function addFooter(slide, n, short = "TP2 · Bandadas off-lattice", dark = false) {
  const color = dark ? "#C9CDEA" : "#7C8193";
  addText(slide, short, { left: 66, top: 680, width: 420, height: 20 }, 13, color, false);
  addText(slide, String(n), { left: 1170, top: 680, width: 44, height: 20 }, 13, color, true, { align: "right" });
}

function baseSlide(title, section, n) {
  const slide = deck.slides.add();
  slide.background.fill = C.white;
  addTitle(slide, title, section);
  addFooter(slide, n);
  return slide;
}

function sectionSlide(title, kicker, n) {
  const slide = deck.slides.add();
  slide.background.fill = C.navy;
  addShape(slide, "rect", { left: 0, top: 0, width: 18, height: H }, C.indigo);
  addText(slide, kicker.toUpperCase(), { left: 92, top: 230, width: 600, height: 28 }, 18, "#BFC4EA", true);
  addText(slide, title, { left: 92, top: 274, width: 1050, height: 100 }, 52, C.white, true);
  addRule(slide, 92, 400, 150, C.indigo, 7);
  addFooter(slide, n, "TP2 · Bandadas off-lattice", true);
  return slide;
}

function note(slide, central, duration, sources, extra = "") {
  const lines = [`Idea central: ${central}`, `Duración estimada: ${duration}.`];
  if (extra) lines.push(extra);
  lines.push("", "[Sources]", ...sources.map(s => `- ${s}`), "[/Sources]");
  slide.speakerNotes.textFrame.setText(lines);
  slide.speakerNotes.setVisible(true);
}

function addImage(slide, file, pos, alt) {
  addShape(slide, "rect", { left: pos.left - 3, top: pos.top - 3, width: pos.width + 6, height: pos.height + 6 }, C.white, { style: "solid", fill: C.line, width: 1 });
  const bytes = readFileSync(file);
  return slide.images.add({ blob: bytes, contentType: "image/png", alt, fit: "contain", position: pos });
}

function addSideNote(slide, heading, lines, pos = { left: 930, top: 165, width: 284, height: 430 }) {
  addShape(slide, "rect", pos, C.pale, { style: "solid", fill: C.line, width: 1 });
  addRule(slide, pos.left + 22, pos.top + 26, 74, C.indigo, 5);
  addText(slide, heading, { left: pos.left + 22, top: pos.top + 46, width: pos.width - 44, height: 48 }, 24, C.navy, true);
  addText(slide, lines.join("\n"), { left: pos.left + 22, top: pos.top + 108, width: pos.width - 44, height: pos.height - 132 }, 19, C.muted, false, { valign: "top" });
}

function imagePairSlide(title, section, n, leftFile, rightFile, message, stats, duration, sourceMd) {
  const slide = baseSlide(title, section, n);
  addText(slide, message, { left: 66, top: 139, width: 1148, height: 35 }, 22, C.indigo, true);
  addImage(slide, leftFile, { left: 66, top: 187, width: 548, height: 390 }, path.basename(leftFile));
  addImage(slide, rightFile, { left: 650, top: 187, width: 548, height: 390 }, path.basename(rightFile));
  addText(slide, stats, { left: 66, top: 596, width: 1132, height: 48 }, 17, C.muted, false, { align: "center" });
  note(slide, message, duration, [sourceMd, leftFile, rightFile]);
  return slide;
}

// 1 Portada
{
  const s = deck.slides.add(); s.background.fill = C.white;
  addShape(s, "rect", { left: 0, top: 0, width: 24, height: H }, C.navy);
  addShape(s, "ellipse", { left: 930, top: 96, width: 214, height: 214 }, C.softIndigo, { style: "solid", fill: "none", width: 0 });
  addShape(s, "ellipse", { left: 1000, top: 165, width: 74, height: 74 }, C.indigo, { style: "solid", fill: "none", width: 0 });
  for (let i=0;i<8;i++) addShape(s, "line", { left: 873 + i*34, top: 320 + (i%3)*28, width: 42, height: 14 + (i%2)*8 }, "none", { style: "solid", fill: i%2 ? C.indigo : C.navy, width: 4 });
  addText(s, "SIMULACIÓN DE SISTEMAS · TP2", { left: 78, top: 72, width: 600, height: 28 }, 17, C.indigo, true);
  addText(s, "Simulación de bandadas:\nmodelo de Vicsek y modelo de votante", { left: 78, top: 126, width: 790, height: 155 }, 52, C.navy, true);
  addText(s, "72.25 — Simulación de Sistemas | Trabajo Práctico 2", { left: 80, top: 306, width: 780, height: 40 }, 25, C.muted, false);
  addRule(s, 80, 380, 330, C.indigo, 6);
  addText(s, "Franco Ferrari — Legajo 63094\nMateo Pirola — Legajo 62810\nKatia Menshikoff — Legajo 64396", { left: 80, top: 414, width: 570, height: 112 }, 21, C.ink, false, { valign: "top" });
  addText(s, "04/09/2026", { left: 80, top: 568, width: 260, height: 32 }, 20, C.muted, true);
  addText(s, "Grupo / comisión: a completar", { left: 80, top: 614, width: 360, height: 28 }, 16, C.indigo, true);
  addFooter(s, 1);
  note(s, "Presentar el tema y a los integrantes; no demorar la portada.", "0:15", [path.join(ROOT,"PLAN_PPT_TP2.md")], "Pendiente administrativo: reemplazar “Grupo / comisión: a completar” antes de entregar.");
}

// 2 Introducción
{
  const s = baseSlide("Reglas locales pueden producir orden colectivo", "Introducción", 2);
  addText(s, "Partículas autopropulsadas ajustan su dirección usando información cercana. Sin líder central, la interacción repetida puede organizar el movimiento global.", { left: 66, top: 158, width: 560, height: 150 }, 26, C.ink, false, { valign: "top" });
  const centers = [[780,210],[920,205],[1050,260],[840,335],[1000,390],[720,430],[1110,445]];
  for (let i=0;i<centers.length;i++) addShape(s, "line", { left: centers[i][0]-18, top: centers[i][1]-14, width: 74, height: 12 + (i%3)*8 }, "none", { style: "solid", fill: i===2?C.indigo:C.navy, width: 5 });
  for (let i=0;i<centers.length;i++) addShape(s, "ellipse", { left: centers[i][0]-10, top: centers[i][1]-10, width: 20, height: 20 }, i===2?C.indigo:C.navy, { style: "solid", fill: "none", width: 0 });
  addShape(s, "rect", { left: 66, top: 428, width: 560, height: 132 }, C.navy, { style: "solid", fill: "none", width: 0 });
  addText(s, "¿Cómo modifican el ruido, la densidad y la regla local el orden y la conectividad?", { left: 92, top: 448, width: 508, height: 92 }, 28, C.white, true);
  note(s, "Plantear la pregunta que organiza toda la exposición.", "0:30", [path.join(ROOT,"bibliografia/enunciado_tp2_guia_de_trabajo.md"), path.join(ROOT,"bibliografia/teoria_tp2_automatas_off_lattice.md")]);
}

// 3 Reglas
{
  const s = baseSlide("Dos reglas de interacción sobre la misma geometría", "Introducción", 3);
  addShape(s, "line", { left: 310, top: 282, width: 85, height: 0 }, "none", { style:"solid",fill:C.indigo,width:4 }, undefined);
  addShape(s, "line", { left: 885, top: 282, width: 85, height: 0 }, "none", { style:"solid",fill:C.indigo,width:4 }, undefined);
  addShape(s, "rect", { left: 66, top: 164, width: 545, height: 300 }, C.pale, { style:"solid",fill:C.line,width:1 });
  addShape(s, "rect", { left: 669, top: 164, width: 545, height: 300 }, C.pale, { style:"solid",fill:C.line,width:1 });
  addText(s, "Vicsek", { left: 94, top: 188, width: 180, height: 42 }, 30, C.navy, true);
  addText(s, "Promedia vectorialmente todas las direcciones vecinas, incluida la propia partícula.", { left: 94, top: 250, width: 464, height: 112 }, 24, C.ink, false, { valign:"top" });
  addText(s, "Votante ruidoso", { left: 697, top: 188, width: 300, height: 42 }, 30, C.navy, true);
  addText(s, "Copia la dirección de otra partícula vecina elegida al azar. Si está aislada, conserva dirección y suma ruido.", { left: 697, top: 250, width: 468, height: 132 }, 24, C.ink, false, { valign:"top" });
  addText(s, "ξ ~ U[−η/2, η/2]   ·   η en radianes", { left: 266, top: 504, width: 748, height: 48 }, 30, C.indigo, true, { align:"center" });
  addText(s, "Misma caja, radio, velocidad y protocolo", { left: 330, top: 574, width: 620, height: 34 }, 21, C.muted, true, { align:"center" });
  note(s, "Aislar la única diferencia entre modelos: promedio colectivo frente a copia individual.", "0:25", [path.join(ROOT,"bibliografia/teoria_tp2_automatas_off_lattice.md"), path.join(ROOT,"bibliografia/enunciado_tp2_guia_de_trabajo.md")]);
}

sectionSlide("Implementación", "Sección 1", 4); note(deck.slides.items[3], "Introducir brevemente la implementación.", "0:03", [path.join(ROOT,"PLAN_PPT_TP2.md")]);

// 5 Arquitectura
{
  const s = baseSlide("Los resultados quedan desacoplados del visualizador", "Implementación", 5);
  const nodes = [
    {x:76,w:260,t:"Motor C++",sub:"simulación"},
    {x:405,w:380,t:"Salida de texto",sub:"observables.csv  ·  trajectory.csv"},
    {x:854,w:350,t:"Análisis y visualización",sub:"lectura independiente"}
  ];
  addShape(s,"line",{left:336,top:328,width:69,height:0},"none",{style:"solid",fill:C.indigo,width:4});
  addShape(s,"line",{left:785,top:328,width:69,height:0},"none",{style:"solid",fill:C.indigo,width:4});
  for (const n of nodes) { addShape(s,"rect",{left:n.x,top:245,width:n.w,height:166},C.pale,{style:"solid",fill:C.line,width:1}); addText(s,n.t,{left:n.x+20,top:274,width:n.w-40,height:44},28,C.navy,true,{align:"center"}); addText(s,n.sub,{left:n.x+18,top:330,width:n.w-36,height:48},19,C.muted,false,{align:"center"}); }
  addShape(s,"rect",{left:224,top:477,width:832,height:86},C.softIndigo,{style:"solid",fill:"none",width:0});
  addText(s,"El visualizador lee resultados ya producidos: no controla el avance de la simulación.",{left:250,top:492,width:780,height:54},24,C.indigo,true,{align:"center"});
  note(s,"Explicar que la simulación produce archivos estables y la visualización es un consumidor independiente.","0:35",[path.join(ROOT,"bibliografia/enunciado_tp2_guia_de_trabajo.md"),path.join(ROOT,"plan_desarrollo_tp2/09_informe_presentacion_entrega.md")]);
}

// 6 Paso temporal
{
  const s = baseSlide("Un paso temporal correcto: sincrónico y backward", "Implementación", 6);
  const xs=[76,306,536,766,996];
  for(let i=0;i<4;i++) addShape(s,"line",{left:xs[i]+174,top:317,width:56,height:0},"none",{style:"solid",fill:C.indigo,width:3});
  const labels=["1\nVecinos con CIM\ny periodicidad","2\nOrientaciones nuevas\ndesde el estado t","3\nMover posiciones\ncon v(t)","4\nReplegar borde\nperiódico","5\nMedir\nvₐ y S"];
  for(let i=0;i<5;i++){addShape(s,"rect",{left:xs[i],top:225,width:174,height:186},i===2?C.softIndigo:C.pale,{style:"solid",fill:i===2?C.indigo:C.line,width:i===2?2:1});addText(s,labels[i],{left:xs[i]+12,top:244,width:150,height:148},21,i===2?C.indigo:C.navy,i===2,{align:"center"});}
  addText(s,"SINCRÓNICO",{left:330,top:481,width:255,height:44},26,C.indigo,true,{align:"center"});
  addText(s,"BACKWARD UPDATE",{left:697,top:481,width:300,height:44},26,C.indigo,true,{align:"center"});
  addText(s,"Ninguna orientación nueva contamina el cálculo de otra partícula.",{left:250,top:548,width:780,height:42},21,C.muted,false,{align:"center"});
  note(s,"Recorrer el orden exacto del paso y remarcar que las posiciones usan v(t), no v(t+1).","0:35",[path.join(ROOT,"bibliografia/teoria_tp2_automatas_off_lattice.md"),path.join(ROOT,"plan_desarrollo_tp2/03_validaciones.md")]);
}

// 7 Validaciones
{
  const s=baseSlide("Las validaciones sostienen la lectura de los resultados","Implementación",7);
  const ys=[183,315,447]; const heads=["Vecindad","Estadística inicial","Observables y clusters"]; const body=["CIM coincide con fuerza bruta.","Otros vecinos ≈ ρ·π·r_c².","vₐ y S respetan límites, periodicidad y conectividad."];
  for(let i=0;i<3;i++){addText(s,String(i+1).padStart(2,"0"),{left:76,top:ys[i],width:74,height:54},32,C.indigo,true);addText(s,heads[i],{left:170,top:ys[i],width:340,height:40},25,C.navy,true);addText(s,body[i],{left:510,top:ys[i],width:650,height:54},24,C.ink,false);addRule(s,170,ys[i]+70,990,C.line,1);}
  addText(s,"11/11 pruebas CTest aprobadas",{left:845,top:588,width:315,height:32},18,C.green,true,{align:"right"});
  note(s,"Mostrar solo los controles que justifican vecinos, periodicidad y observables.","0:25",[path.join(ROOT,"plan_desarrollo_tp2/03_validaciones.md"),path.join(ROOT,"plan_desarrollo_tp2/README.md")]);
}

sectionSlide("Simulaciones y medición", "Sección 2", 8); note(deck.slides.items[7], "Pasar de la implementación al protocolo experimental.", "0:03", [path.join(ROOT,"PLAN_PPT_TP2.md")]);

// 9 Protocolo
{
  const s=baseSlide("Un protocolo común permite comparar reglas y densidades","Simulaciones y medición",9);
  addText(s,"L = 10   ·   r_c = 1   ·   v = 0.03   ·   Δt = 1",{left:66,top:160,width:1148,height:52},29,C.navy,true,{align:"center"});
  addRule(s,174,230,932,C.indigo,3);
  const cols=[{x:85,h:"Sistema",b:"ρ = 2, 4, 8\nN = 200, 400, 800"},{x:400,h:"Ruido",b:"14 valores de η\n0 a 6 rad"},{x:715,h:"Muestreo",b:"R = 20\n3000 pasos"},{x:1030,h:"Estacionario",b:"t_eq = 1500\ndesvío estándar"}];
  for(const c of cols){addText(s,c.h,{left:c.x,top:278,width:190,height:34},24,C.indigo,true,{align:"center"});addText(s,c.b,{left:c.x-32,top:332,width:254,height:90},22,C.ink,false,{align:"center"});}
  addShape(s,"rect",{left:150,top:491,width:980,height:82},C.pale,{style:"solid",fill:C.line,width:1});
  addText(s,"Primero: promedio temporal estacionario por realización    →    Después: promedio entre realizaciones",{left:176,top:509,width:928,height:46},22,C.navy,true,{align:"center"});
  note(s,"Explicar el orden de promediado y la definición de barras; no leer la lista completa de η.","0:40",[path.join(ROOT,"figures/final_production_v1/README.md"),path.join(ROOT,"plan_desarrollo_tp2/DECISIONES_PENDIENTES.md")]);
}

// 10 Observables
{
  const s=baseSlide("Medimos orden y conectividad por separado","Simulaciones y medición",10);
  addShape(s,"rect",{left:66,top:170,width:540,height:360},C.pale,{style:"solid",fill:C.line,width:1});
  addShape(s,"rect",{left:674,top:170,width:540,height:360},C.pale,{style:"solid",fill:C.line,width:1});
  addText(s,"Polarización",{left:96,top:198,width:300,height:42},28,C.navy,true);
  addText(s,"vₐ(t) = (1 / Nv) · |Σᵢ vᵢ(t)|",{left:96,top:267,width:450,height:54},30,C.indigo,true,{align:"center"});
  addText(s,"Magnitud de la velocidad media normalizada\n0 ≤ vₐ ≤ 1",{left:100,top:354,width:442,height:80},22,C.ink,false,{align:"center"});
  addText(s,"Componente gigante",{left:704,top:198,width:340,height:42},28,C.navy,true);
  addText(s,"S(t) = n_max(t) / N",{left:704,top:267,width:450,height:54},30,C.indigo,true,{align:"center"});
  addText(s,"Clusters: componentes conexas geométricas\ncon borde periódico",{left:708,top:354,width:442,height:80},22,C.ink,false,{align:"center"});
  addText(s,"Medir ambos evita confundir alineamiento global con proximidad espacial.",{left:180,top:575,width:920,height:38},22,C.muted,true,{align:"center"});
  note(s,"Definir vₐ y S antes de mostrar curvas; señalar que un cluster grande no implica alineamiento global.","0:30",[path.join(ROOT,"bibliografia/teoria_tp2_automatas_off_lattice.md"),path.join(ROOT,"bibliografia/enunciado_tp2_guia_de_trabajo.md")]);
}

sectionSlide("Resultados: ruido, orden y conectividad", "Sección 3", 11); note(deck.slides.items[10], "Abrir la sección de resultados.", "0:03", [path.join(ROOT,"PLAN_PPT_TP2.md")]);

// 12 Snapshot
{
  const s=baseSlide("Estados estacionarios representativos a ρ = 2","Resultados",12);
  addImage(s,path.join(SNAP,"rho2_model_comparison_snapshot.png"),{left:66,top:155,width:844,height:470},"Comparación estática Vicsek y votante a rho=2");
  addSideNote(s,"Parámetros",["Vicsek: η = 3","Votante: η = 0.4","t = 2000","Color: ángulo","Flecha: dirección","Escala visual ×15","Rapidez física v = 0.03"],{left:944,top:155,width:270,height:470});
  note(s,"Comparar dos estados con polarización media similar alcanzada con ruidos muy distintos.","0:35",[path.join(ROOT,"figures/reference_snapshots_v1/README.md"),path.join(SNAP,"rho2_model_comparison_snapshot.png")],"Pendiente: incorporar la animación cuando exista. Para el PDF final, conservar fotograma y agregar un link visible probado.");
}

imagePairSlide("Vicsek: más densidad sostiene el orden a mayor ruido","Resultados · Vicsek",13,path.join(FIG,"vicsek_va_t_rho_2.png"),path.join(FIG,"vicsek_va_vs_eta.png"),"Observación de estas simulaciones, no una ley universal.","Línea vertical: t_eq = 1500  ·  Bandas/barras: desvío estándar, R = 20","0:45",path.join(FIG,"README.md"));
imagePairSlide("Vicsek: conectividad y alineamiento evolucionan distinto","Resultados · Vicsek",14,path.join(FIG,"vicsek_S_t_rho_2.png"),path.join(FIG,"vicsek_S_vs_eta.png"),"La componente gigante aporta información espacial complementaria.","Línea vertical: t_eq = 1500  ·  Bandas/barras: desvío estándar, R = 20","0:40",path.join(FIG,"README.md"));

// 15 single
{
  const s=baseSlide("Vicsek: orden frente a conectividad","Resultados · Vicsek",15);
  addImage(s,path.join(FIG,"vicsek_va_vs_S.png"),{left:66,top:158,width:824,height:472},"Polarización frente a componente gigante para Vicsek");
  addSideNote(s,"Cómo leerlo",["Cada punto: un valor de η","Eje x: ⟨S⟩","Eje y: ⟨vₐ⟩","ρ = 2, 4, 8","Barras: desvío estándar"],{left:924,top:158,width:290,height:472});
  note(s,"Mostrar que la relación entre alineamiento y conectividad cambia a lo largo del barrido.","0:25",[path.join(FIG,"README.md"),path.join(FIG,"vicsek_va_vs_S.png")]);
}

imagePairSlide("Votante: la caída observada ocurre a ruido bajo","Resultados · Votante",16,path.join(FIG,"voter_va_t_rho_2.png"),path.join(FIG,"voter_va_vs_eta_zoom_0_0p5.png"),"La zona η ≤ 0.5 resuelve la caída observada.","Línea vertical: t_eq = 1500  ·  Bandas/barras: desvío estándar, R = 20","0:45",path.join(FIG,"README.md"));
imagePairSlide("Votante: conectividad","Resultados · Votante",17,path.join(FIG,"voter_S_t_rho_2.png"),path.join(FIG,"voter_S_vs_eta.png"),"La comparación conserva geometría, tiempos y estadística.","Línea vertical: t_eq = 1500  ·  Bandas/barras: desvío estándar, R = 20","0:40",path.join(FIG,"README.md"));

// 18 single
{
  const s=baseSlide("Votante: cambia la relación entre orden y conectividad","Resultados · Votante",18);
  addImage(s,path.join(FIG,"voter_va_vs_S.png"),{left:66,top:158,width:824,height:472},"Polarización frente a componente gigante para votante");
  addSideNote(s,"Lectura",["Cada punto: un valor de η","Eje x: ⟨S⟩","Eje y: ⟨vₐ⟩","Misma geometría","Mismo protocolo"],{left:924,top:158,width:290,height:472});
  note(s,"Atribuir la diferencia observada a la regla local, porque los demás parámetros se mantuvieron iguales.","0:25",[path.join(FIG,"README.md"),path.join(FIG,"voter_va_vs_S.png")]);
}

// 19 lowrho
{
  const s=baseSlide("Fragmentación a baja densidad","Resultados",19);
  addImage(s,path.join(FIG,"comparison_S_vs_eta_lowrho.png"),{left:66,top:160,width:848,height:468},"Comparación de componente gigante a bajas densidades");
  addSideNote(s,"Densidades",["ρ nominal:","1/π · 1/(2π) · 1/(3π)","","N:","32 · 16 · 11","","ρ efectiva:","0.32 · 0.16 · 0.11"],{left:946,top:160,width:268,height:468});
  addShape(s,"rect",{left:0,top:0,width:W,height:132},C.white,{style:"solid",fill:"none",width:0});
  addText(s,"RESULTADOS",{left:66,top:34,width:410,height:24},15,C.indigo,true);
  addText(s,"Fragmentación a baja densidad",{left:66,top:64,width:1148,height:48},35,C.navy,true);
  addRule(s,66,126,1148,C.line,1);
  note(s,"Explicar por qué se reportan densidad nominal, N entero y densidad efectiva.","0:35",[path.join(FIG,"README.md"),path.join(ROOT,"plan_desarrollo_tp2/DECISIONES_PENDIENTES.md"),path.join(FIG,"comparison_S_vs_eta_lowrho.png")]);
}

// 20 comparisons
{
  const s=baseSlide("Las reglas separan las escalas de ruido observadas","Resultados",20);
  addText(s,"El votante pierde polarización en la región de ruido bajo resuelta finamente; Vicsek conserva orden hasta ruidos mayores.",{left:66,top:139,width:1148,height:54},22,C.indigo,true,{align:"center"});
  addImage(s,path.join(FIG,"comparison_va_vs_eta.png"),{left:66,top:203,width:550,height:378},"Comparación de polarización entre modelos");
  addImage(s,path.join(FIG,"comparison_S_vs_eta_base.png"),{left:650,top:203,width:550,height:378},"Comparación de componente gigante entre modelos");
  addText(s,"Izquierda: ⟨vₐ⟩ vs. η   ·   Derecha: ⟨S⟩ vs. η   ·   Barras: desvío estándar, R = 20",{left:66,top:600,width:1132,height:36},17,C.muted,false,{align:"center"});
  note(s,"Cerrar la evidencia comparativa con una formulación prudente y limitada a estos datos.","0:45",[path.join(FIG,"README.md"),path.join(FIG,"comparison_va_vs_eta.png"),path.join(FIG,"comparison_S_vs_eta_base.png")]);
}

// 21 conclusions
{
  const s=baseSlide("Tres conclusiones: ruido, regla y conectividad","Conclusiones",21);
  const items=["El ruido controla el orden colectivo en ambos modelos.","La regla de interacción cambia el rango de ruido donde se observa la pérdida de polarización.","Conectividad espacial y alineamiento global no son equivalentes; por eso se estudian con S y vₐ por separado."];
  for(let i=0;i<3;i++){addText(s,String(i+1),{left:90,top:180+i*125,width:58,height:58},32,C.white,true,{align:"center",fill:i===1?C.indigo:C.navy});addText(s,items[i],{left:180,top:174+i*125,width:940,height:72},27,C.navy,i===2);}
  addRule(s,180,566,940,C.line,1);
  addText(s,"Pendientes de cierre: animaciones y benchmark CIM vs. TP1.",{left:180,top:588,width:940,height:34},18,C.muted,true);
  note(s,"Resolver la pregunta inicial con tres conclusiones y declarar con honestidad qué falta para la entrega final.","0:35",[path.join(ROOT,"PLAN_PPT_TP2.md"),path.join(FIG,"README.md"),path.join(ROOT,"plan_desarrollo_tp2/09_informe_presentacion_entrega.md")]);
}

// 22 appendix separator
sectionSlide("Apéndice", "Respaldo para preguntas", 22); note(deck.slides.items[21], "No exponer salvo preguntas; separa claramente el respaldo del relato principal.", "—", [path.join(ROOT,"PLAN_PPT_TP2.md")]);

// 23 comparison va-S
{
  const s=baseSlide("Comparación directa entre orden y conectividad","Apéndice",23);
  addImage(s,path.join(FIG,"comparison_va_vs_S.png"),{left:82,top:150,width:1116,height:486},"Comparación de polarización frente a componente gigante");
  note(s,"Usar solo si preguntan por la comparación punto a punto entre modelos.","respaldo",[path.join(FIG,"README.md"),path.join(FIG,"comparison_va_vs_S.png")]);
}

// 24-27 series rho4/8
imagePairSlide("Vicsek: vₐ(t) en ρ = 4 y ρ = 8","Apéndice",24,path.join(FIG,"vicsek_va_t_rho_4.png"),path.join(FIG,"vicsek_va_t_rho_8.png"),"Series restantes por densidad.","t_eq = 1500  ·  Bandas: desvío estándar, R = 20","respaldo",path.join(FIG,"README.md"));
imagePairSlide("Vicsek: S(t) en ρ = 4 y ρ = 8","Apéndice",25,path.join(FIG,"vicsek_S_t_rho_4.png"),path.join(FIG,"vicsek_S_t_rho_8.png"),"Series restantes por densidad.","t_eq = 1500  ·  Bandas: desvío estándar, R = 20","respaldo",path.join(FIG,"README.md"));
imagePairSlide("Votante: polarización en ρ = 4 y ρ = 8","Apéndice",26,path.join(FIG,"voter_va_t_rho_4.png"),path.join(FIG,"voter_va_t_rho_8.png"),"Series restantes por densidad.","t_eq = 1500  ·  Bandas: desvío estándar, R = 20","respaldo",path.join(FIG,"README.md"));
imagePairSlide("Votante: S(t) en ρ = 4 y ρ = 8","Apéndice",27,path.join(FIG,"voter_S_t_rho_4.png"),path.join(FIG,"voter_S_t_rho_8.png"),"Series restantes por densidad.","t_eq = 1500  ·  Bandas: desvío estándar, R = 20","respaldo",path.join(FIG,"README.md"));

// 28-29 individual low-rho
{
  const s=baseSlide("Vicsek: clusters en densidades bajas","Apéndice",28); addImage(s,path.join(FIG,"vicsek_S_vs_eta_lowrho.png"),{left:80,top:150,width:810,height:486},"Clusters bajos en Vicsek"); addSideNote(s,"Casos",["ρ nominal = 1/π, 1/(2π), 1/(3π)","N = 32, 16, 11","ρ efectiva = 0.32, 0.16, 0.11","Barras: desvío estándar"],{left:924,top:150,width:290,height:486}); note(s,"Detalle individual de Vicsek en densidades bajas.","respaldo",[path.join(FIG,"README.md"),path.join(FIG,"vicsek_S_vs_eta_lowrho.png")]);
}
{
  const s=baseSlide("Votante: clusters en densidades bajas","Apéndice",29); addImage(s,path.join(FIG,"voter_S_vs_eta_lowrho.png"),{left:80,top:150,width:810,height:486},"Clusters bajos en votante"); addSideNote(s,"Casos",["ρ nominal = 1/π, 1/(2π), 1/(3π)","N = 32, 16, 11","ρ efectiva = 0.32, 0.16, 0.11","Barras: desvío estándar"],{left:924,top:150,width:290,height:486}); note(s,"Detalle individual del votante en densidades bajas.","respaldo",[path.join(FIG,"README.md"),path.join(FIG,"voter_S_vs_eta_lowrho.png")]);
}

// 30-31 zooms S
{
  const s=deck.slides.add(); s.background.fill=C.white;
  addTitle(s,"S con η ≤ 0.5: densidades base","Apéndice"); addFooter(s,30);
  addText(s,"Mismo intervalo η ≤ 0.5 para ambos modelos.",{left:66,top:139,width:1148,height:35},22,C.indigo,true);
  addImage(s,path.join(FIG,"vicsek_S_vs_eta_zoom_0_0p5.png"),{left:66,top:187,width:548,height:390},"Zoom de S para Vicsek en densidades base");
  addImage(s,path.join(FIG,"voter_S_vs_eta_zoom_0_0p5.png"),{left:650,top:187,width:548,height:390},"Zoom de S para votante en densidades base");
  addText(s,"ρ = 2, 4, 8  ·  Barras: desvío estándar, R = 20",{left:66,top:596,width:1132,height:48},17,C.muted,false,{align:"center"});
  note(s,"Mismo intervalo η ≤ 0.5 para ambos modelos.","respaldo",[path.join(FIG,"README.md"),path.join(FIG,"vicsek_S_vs_eta_zoom_0_0p5.png"),path.join(FIG,"voter_S_vs_eta_zoom_0_0p5.png")]);
}
imagePairSlide("Zoom de S: densidades bajas","Apéndice",31,path.join(FIG,"vicsek_S_vs_eta_lowrho_zoom_0_0p5.png"),path.join(FIG,"voter_S_vs_eta_lowrho_zoom_0_0p5.png"),"Detalle del tramo fino η ≤ 0.5 en la extensión de clusters.","N = 32, 16, 11  ·  Barras: desvío estándar, R = 20","respaldo",path.join(FIG,"README.md"));

// 32 detailed protocol
{
  const s=baseSlide("Protocolo detallado","Apéndice",32);
  const rows=[
    ["Geometría","L=10 · r_c=1 · Δt=1 · v=0.03 · borde periódico"],
    ["Matriz base","modelos={Vicsek,votante} · ρ={2,4,8} · N={200,400,800}"],
    ["Ruido","η={0,0.05,0.10,0.15,0.20,0.30,0.40,0.50,1,2,3,4,5,6} rad"],
    ["Ejecución","R=20 · steps=3000 · t_eq=1500 · ventana t=1500…3000"],
    ["Agregación","promedio temporal por realización → promedio entre realizaciones"],
    ["Incertidumbre","desvío estándar entre realizaciones; no error estándar"],
    ["Densidades bajas","ρ nominal={1/π,1/(2π),1/(3π)} · N={32,16,11} · solo clusters"]
  ];
  for(let i=0;i<rows.length;i++){const y=156+i*69;addText(s,rows[i][0],{left:76,top:y,width:230,height:45},21,C.indigo,true);addText(s,rows[i][1],{left:314,top:y,width:870,height:45},20,C.ink,false);addRule(s,76,y+54,1108,C.line,1);}
  note(s,"Responder preguntas de reproducibilidad y método estadístico.","respaldo",[path.join(FIG,"README.md"),path.join(ROOT,"plan_desarrollo_tp2/DECISIONES_PENDIENTES.md")]);
}

// 33 validations detailed
{
  const s=baseSlide("Validaciones del motor: evidencia disponible","Apéndice",33);
  const items=["CIM = fuerza bruta en casos controlados.","Vecinos medios iniciales compatibles con ρπr_c².","Vicsek y votante satisfacen reglas distintas.","Actualización sincrónica y movimiento backward.","vₐ ∈ [0,1] y vale 1 para direcciones idénticas.","S valida transitividad, periodicidad e IDs no consecutivos.","Reproducibilidad con semillas y salida de texto verificada."];
  for(let i=0;i<items.length;i++){addShape(s,"ellipse",{left:85,top:160+i*62,width:20,height:20},i<6?C.indigo:C.green,{style:"solid",fill:"none",width:0});addText(s,items[i],{left:125,top:146+i*62,width:1015,height:46},22,C.ink,false);}
  addText(s,"Suite automatizada: 11/11 CTest aprobadas",{left:700,top:603,width:450,height:34},20,C.green,true,{align:"right"});
  note(s,"Usar como respaldo metodológico; no afirmar cierre de la regresión física de consenso si preguntan por ella.","respaldo",[path.join(ROOT,"plan_desarrollo_tp2/03_validaciones.md"),path.join(ROOT,"plan_desarrollo_tp2/README.md")]);
}

await fs.mkdir(PREVIEW,{recursive:true});
for (const [i,slide] of deck.slides.items.entries()) {
  const png=await deck.export({slide,format:"png",scale:1.2});
  await fs.writeFile(path.join(PREVIEW,`slide-${String(i+1).padStart(2,"0")}.png`),new Uint8Array(await png.arrayBuffer()));
}
const montage=await deck.export({format:"webp",montage:true,scale:0.55});
await fs.writeFile(path.join(ROOT,".tmp/presentation_build/montage.webp"),new Uint8Array(await montage.arrayBuffer()));
await fs.mkdir(path.dirname(OUT),{recursive:true});
try {
  const pptx=await PresentationFile.exportPptx(deck);
  await pptx.save(OUT);
  console.log(`Created ${OUT} with ${deck.slides.items.length} slides`);
} catch (error) {
  console.error(`PPTX_EXPORT_ERROR: ${error?.message ?? String(error)}`);
  process.exitCode = 1;
}
