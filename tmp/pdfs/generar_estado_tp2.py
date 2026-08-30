from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageBreak, Paragraph, Spacer, Table, TableStyle,
    KeepTogether
)

OUT = "output/pdf/estado_actual_tp2_explicado.pdf"

NAVY = colors.HexColor("#16324F")
BLUE = colors.HexColor("#2C6E9F")
TEAL = colors.HexColor("#2A9D8F")
GOLD = colors.HexColor("#E9C46A")
ORANGE = colors.HexColor("#F4A261")
RED = colors.HexColor("#E76F51")
PALE = colors.HexColor("#F4F7FA")
INK = colors.HexColor("#202A33")

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="TitleTP", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=23, leading=28, textColor=NAVY, spaceAfter=8))
styles.add(ParagraphStyle(name="SubTP", parent=styles["Normal"], fontName="Helvetica", fontSize=10.5, leading=15, textColor=colors.HexColor("#496172"), spaceAfter=12))
styles.add(ParagraphStyle(name="H1TP", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=15, leading=19, textColor=NAVY, spaceBefore=8, spaceAfter=7))
styles.add(ParagraphStyle(name="H2TP", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=11.2, leading=14, textColor=BLUE, spaceBefore=7, spaceAfter=4))
styles.add(ParagraphStyle(name="BodyTP", parent=styles["BodyText"], fontName="Helvetica", fontSize=9.3, leading=13.2, textColor=INK, spaceAfter=6))
styles.add(ParagraphStyle(name="SmallTP", parent=styles["BodyText"], fontName="Helvetica", fontSize=8.1, leading=10.7, textColor=INK))
styles.add(ParagraphStyle(name="CalloutTP", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=10.2, leading=14, textColor=NAVY))
styles.add(ParagraphStyle(name="TableHead", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=7.5, leading=9.2, textColor=colors.white, alignment=TA_CENTER))
styles.add(ParagraphStyle(name="TableCell", parent=styles["BodyText"], fontName="Helvetica", fontSize=7.3, leading=9.1, textColor=INK))
styles.add(ParagraphStyle(name="TableCellBold", parent=styles["BodyText"], fontName="Helvetica-Bold", fontSize=7.3, leading=9.1, textColor=INK))

def P(text, style="BodyTP"):
    return Paragraph(text, styles[style])

def cell(text, bold=False):
    return P(text, "TableCellBold" if bold else "TableCell")

def status_box(title, text, color):
    t = Table([[P(title, "CalloutTP")], [P(text, "BodyTP")]], colWidths=[17.3*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), color),
        ("BACKGROUND", (0,1), (-1,-1), colors.white),
        ("BOX", (0,0), (-1,-1), .6, color),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("RIGHTPADDING", (0,0), (-1,-1), 10),
        ("TOPPADDING", (0,0), (-1,0), 6),
        ("BOTTOMPADDING", (0,0), (-1,0), 4),
        ("TOPPADDING", (0,1), (-1,-1), 7),
        ("BOTTOMPADDING", (0,1), (-1,-1), 6),
    ]))
    return t

def header_footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#D9E2EA"))
    canvas.line(1.35*cm, 1.25*cm, 19.65*cm, 1.25*cm)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor("#617687"))
    canvas.drawString(1.35*cm, .82*cm, "Simulacion de Sistemas - TP2 | Estado del proyecto")
    canvas.drawRightString(19.65*cm, .82*cm, f"Pagina {doc.page}")
    canvas.restoreState()

doc = BaseDocTemplate(OUT, pagesize=A4, leftMargin=1.35*cm, rightMargin=1.35*cm, topMargin=1.25*cm, bottomMargin=1.65*cm)
doc.addPageTemplates([__import__('reportlab.platypus', fromlist=['PageTemplate']).PageTemplate(id='main', frames=[Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')], onPage=header_footer)])

story = []
story += [P("TP2 de Simulacion de Sistemas", "TitleTP"), P("Mapa explicativo del estado actual: que pide el enunciado, que esta construido, que se piloto y que falta decidir.<br/>Corte de informacion: 30 de agosto de 2026.", "SubTP")]
story.append(status_box("EN UNA FRASE: donde estamos", "El motor ya esta implementado y las pruebas automaticas principales pasan. Ya se hizo un piloto de 108 corridas. Aun no corresponde ejecutar el barrido definitivo ni hacer las figuras finales, porque faltan decisiones experimentales basadas en un piloto mas largo del modelo votante y una aclaracion sobre las densidades bajas.", GOLD))
story += [Spacer(1, 10), P("1. Que pide el TP (el recorrido completo)", "H1TP")]
story.append(P("El trabajo estudia bandadas de particulas puntuales en una caja continua y periodica. No es un modelo de fluidos ni una grilla. Se comparan dos reglas con los mismos parametros: <b>Vicsek</b> (promedia direcciones vecinas) y <b>votante ruidoso</b> (copia a un vecino aleatorio).", "BodyTP"))
req_rows = [[P("Consigna", "TableHead"), P("Que hay que entregar/mostrar", "TableHead"), P("Estado hoy", "TableHead")],
 [cell("Modelo y motor", True), cell("L=10, rc=1, dt=1, v=0.03; dos modelos; borde periodico; actualizacion sincronica."), cell("Implementado y probado en gran parte.")],
 [cell("Mediciones", True), cell("Series de polarizacion va(t) y cluster mayor S(t); promedio estacionario y barras."), cell("Calculadas por el motor; protocolo final pendiente.")],
 [cell("Barrido", True), cell("Dos modelos x rho=2,4,8 x varios eta x varias realizaciones."), cell("Solo piloto exploratorio; produccion aun no.")],
 [cell("Clusters", True), cell("S(t), <S> vs eta; extension solicitada a densidades bajas."), cell("Algoritmo listo; conversion N pendiente.")],
 [cell("Figuras y animaciones", True), cell("A-E para ambos modelos y comparacion; animacion independiente desde texto."), cell("Formato y datos listos; faltan datos definitivos y modulo visual.")],
 [cell("Rendimiento", True), cell("Tiempo del CIM comparable con TP1."), cell("Pendiente de protocolo y medicion.")],
 [cell("Entrega", True), cell("Presentacion 13 min, PDF con links, informe y ZIP liviano."), cell("Pendiente; depende de resultados finales.")]]
t = Table(req_rows, colWidths=[3.1*cm, 8.4*cm, 5.8*cm], repeatRows=1)
t.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), NAVY), ("GRID", (0,0), (-1,-1), .3, colors.HexColor("#C7D4DE")), ("VALIGN", (0,0), (-1,-1), "TOP"), ("BACKGROUND", (0,1), (-1,-1), PALE), ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, PALE]), ("LEFTPADDING", (0,0), (-1,-1), 5), ("RIGHTPADDING", (0,0), (-1,-1), 5), ("TOPPADDING", (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5)]))
story += [t, Spacer(1,8), P("Los observables centrales son: <b>va</b>, cuanto se alinean las direcciones globalmente (0 a 1), y <b>S</b>, fraccion de particulas dentro del cluster geometrico conectado mas grande (0 a 1).", "SmallTP"), PageBreak()]

story += [P("2. Lo que ya se construyo y verifico", "H1TP"), P("La parte de ingenieria del TP esta muy avanzada. El motor no es una maqueta: ya genera corridas reproducibles y archivos de texto autocontenidos.", "BodyTP")]
done_rows = [[P("Bloque", "TableHead"), P("Implementado", "TableHead"), P("Evidencia", "TableHead")],
 [cell("Geometria y vecinos", True), cell("Borde periodico, distancia minima, fuerza bruta y Cell Index Method (CIM)."), cell("CIM contrastado contra el oraculo de fuerza bruta.")],
 [cell("Reglas fisicas", True), cell("Vicsek incluye a si misma; votante elige otra particula. Ruido uniforme [-eta/2, eta/2]."), cell("Tests de reglas e invariancia al orden de almacenamiento.")],
 [cell("Paso temporal", True), cell("Actualizacion sincronica y movimiento backward: primero se mueve con v(t), no con la direccion nueva."), cell("Tests de sincronismo, borde y caso minimo.")],
 [cell("Observables", True), cell("Polarizacion va y S mediante union-find para clusters conectados."), cell("Tests de limites, transitividad, IDs no consecutivos y borde periodico.")],
 [cell("Inicializacion y corrida", True), cell("Posiciones/angulos aleatorios, semillas explicitas y simulacion multipaso reproducible."), cell("Tests de densidad, rangos, reproducibilidad y semillas por paso.")],
 [cell("Salida y CLI", True), cell("observables.csv siempre; trajectory.csv opcional. Metadatos, no sobreescritura por defecto y publicacion segura."), cell("Tests de formato, CLI, reproducibilidad byte a byte y entradas invalidas.")]]
t = Table(done_rows, colWidths=[3.2*cm, 8.0*cm, 6.1*cm], repeatRows=1)
t.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), TEAL), ("GRID", (0,0), (-1,-1), .3, colors.HexColor("#C7D4DE")), ("VALIGN", (0,0), (-1,-1), "TOP"), ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, PALE]), ("LEFTPADDING", (0,0), (-1,-1), 5), ("RIGHTPADDING", (0,0), (-1,-1), 5), ("TOPPADDING", (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5)]))
story += [t, Spacer(1,8), status_box("CONFIRMACION RECIENTE", "En esta revision se recompilo el proyecto y se ejecuto CTest: 11 de 11 pruebas pasaron, sin fallos. La etapa de validacion sigue abierta solo por un control fisico pendiente: repetir el consenso del votante sin ruido con los parametros reales del TP, no solo en un grafo completamente conectado de prueba.", colors.HexColor("#D8F0EC")), Spacer(1,10), P("Como se guardan los datos", "H2TP"), P("Cada corrida queda en su propio directorio. <b>observables.csv</b> contiene t, va y S para los graficos; <b>trajectory.csv</b> es opcional y contiene t, id, x, y, theta para animar. Esto cumple la separacion exigida: la animacion lee texto ya generado y no controla el tiempo del motor.", "BodyTP"), PageBreak()]

story += [P("3. El piloto que ya se hizo", "H1TP"), P("Antes de congelar el experimento final se ejecuto un piloto exploratorio. Sirve para aprender cuanto tarda el sistema y en que zona de ruido hacen falta mas puntos; sus resultados no son todavia los numeros finales del informe.", "BodyTP")]
pilot_rows = [[P("Elemento", "TableHead"), P("Valor del piloto", "TableHead")],
 [cell("Matriz", True), cell("2 modelos x 3 densidades (2, 4, 8) x 6 eta x 3 realizaciones = 108 corridas.")],
 [cell("Ruido explorado", True), cell("eta = {0, 1, 2, 3, 4, 6} radianes.")],
 [cell("Duracion", True), cell("600 pasos por corrida; observables en cada paso; CIM; trayectoria desactivada salvo una inspeccion.")],
 [cell("Calidad de archivos", True), cell("108/108 observables.csv validos: tiempos ordenados, va y S en rango, metadatos y pasos inicial/final presentes.")],
 [cell("Costo", True), cell("Lote completo: 65.7 s, sin fallos. Los datos crudos se pueden regenerar.")]]
t = Table(pilot_rows, colWidths=[4.2*cm, 13.1*cm], repeatRows=1)
t.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), BLUE), ("GRID", (0,0), (-1,-1), .3, colors.HexColor("#C7D4DE")), ("VALIGN", (0,0), (-1,-1), "TOP"), ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, PALE]), ("LEFTPADDING", (0,0), (-1,-1), 6), ("RIGHTPADDING", (0,0), (-1,-1), 6), ("TOPPADDING", (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5)]))
story += [t, Spacer(1,9), P("Que aprendimos del piloto", "H2TP"),
 P("<b>Vicsek:</b> la polarizacion cae al aumentar eta, como se esperaba. Para eta bajo a moderado se estabiliza usualmente dentro de los primeros 100-200 pasos. Cerca de eta=2 a 4 hay fluctuaciones importantes, por lo que la grilla final deberia tener mas resolucion alli.", "BodyTP"),
 P("<b>Votante:</b> con eta=0 la polarizacion seguia creciendo al paso 600 para rho=2, 4 y 8; por eso no se puede declarar estacionario ni usar esos promedios como resultados finales. Para eta>=1 la senal parece estabilizarse hacia t=400-600.", "BodyTP"),
 P("<b>Clusters:</b> con rho=2,4,8, S se mantiene cerca de 1 en casi todos los casos; las densidades bajas agregadas para el estudio de clusters son importantes para volver ese analisis mas informativo.", "BodyTP"),
 status_box("CONCLUSION OPERATIVA", "El siguiente trabajo concreto no es hacer graficos finales: es ejecutar un piloto mas largo del votante (en especial eta=0 y ruido bajo), y usar esa evidencia para proponer una duracion, t_eq, cantidad de realizaciones y grilla final.", colors.HexColor("#FCE9D6")), PageBreak()]

story += [P("4. Decisiones: tomadas, provisionales y abiertas", "H1TP"), P("Es importante separar estas categorias: una decision tomada ya condiciona el codigo; una propuesta provisional guia pilotos, pero no habilita produccion; una decision abierta requiere evidencia nueva o consulta a la catedra/usuario.", "BodyTP")]
story += [P("Decisiones ya tomadas", "H2TP")]
t = Table([[P("Decision", "TableHead"), P("Estado", "TableHead")],
 [cell("Especificacion fisica: L=10, rc=1, dt=1, v=0.03; ruido en radianes U[-eta/2,eta/2]."), cell("Fijada por catedra e implementada.")],
 [cell("Vicsek promedio vectorial con auto-inclusion; votante copia a otra particula y, aislada, conserva rumbo mas ruido."), cell("Fijada por especificacion e implementada.")],
 [cell("Actualizacion sincronica y movimiento backward."), cell("Fijada por catedra e implementada.")],
 [cell("Salida: directorio por corrida, CSV con metadatos; observables siempre y trayectoria opcional."), cell("Aprobada e implementada el 29/08.")]], colWidths=[11.6*cm, 5.7*cm])
t.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), TEAL), ("GRID", (0,0), (-1,-1), .3, colors.HexColor("#C7D4DE")), ("VALIGN", (0,0), (-1,-1), "TOP"), ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, PALE]), ("LEFTPADDING", (0,0), (-1,-1), 6), ("RIGHTPADDING", (0,0), (-1,-1), 6), ("TOPPADDING", (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5)]))
story += [t, Spacer(1,8), P("Propuestas provisionales (no congeladas)", "H2TP"), P("Redondear las densidades bajas a N=32,16,11 y registrar la densidad efectiva; mantener el punto E solo para rho=2,4,8; conservar observables con stride 1 y trayectoria solo en casos animados. Son opciones razonables, pero todavia no se usan como protocolo definitivo.", "BodyTP"),
 P("Decisiones abiertas que bloquean produccion", "H2TP")]
open_rows = [[P("Decision", "TableHead"), P("Por que importa", "TableHead"), P("Que falta", "TableHead")],
 [cell("Conversion de 1/pi, 1/(2pi), 1/(3pi) a N entero", True), cell("Bloquea el barrido definitivo de clusters."), cell("Confirmar con catedra o aprobar explicitamente la convencion de redondeo.")],
 [cell("Grilla final de eta", True), cell("Define las combinaciones del barrido y las curvas finales."), cell("Piloto largo y refinamiento entre eta=2 y 4.")],
 [cell("Pasos y t_eq", True), cell("Sin estacionario justificado no hay promedios validos."), cell("Piloto largo del votante en eta bajo/cero.")],
 [cell("R y semillas", True), cell("Determina la precision de las barras."), cell("Elegir mas de 3 cerca de la zona fluctuante segun costo/variabilidad.")],
 [cell("Barras: desvio o error estandar", True), cell("Debe declararse identicamente en todas las figuras."), cell("Eleccion del grupo tras mirar variabilidad del piloto.")],
 [cell("Strides productivos", True), cell("Afecta peso/resolucion de los datos, no el formato."), cell("Confirmar valores concretos para observables y animaciones.")],
 [cell("Benchmark vs TP1", True), cell("Requisito G: comparacion interpretable."), cell("Definir N, tramo, repeticiones y entorno comun.")]]
t = Table(open_rows, colWidths=[4.1*cm, 6.0*cm, 7.2*cm], repeatRows=1)
t.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), RED), ("GRID", (0,0), (-1,-1), .3, colors.HexColor("#C7D4DE")), ("VALIGN", (0,0), (-1,-1), "TOP"), ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, PALE]), ("LEFTPADDING", (0,0), (-1,-1), 4), ("RIGHTPADDING", (0,0), (-1,-1), 4), ("TOPPADDING", (0,0), (-1,-1), 4), ("BOTTOMPADDING", (0,0), (-1,-1), 4)]))
story += [t, PageBreak()]

story += [P("5. Hoja de ruta desde hoy", "H1TP"), P("La secuencia evita producir resultados definitivos con parametros no justificados. El orden recomendado ya esta reflejado en el plan del proyecto.", "BodyTP")]
road_rows = [[P("Ahora", "TableHead"), P("Accion", "TableHead"), P("Resultado que habilita", "TableHead")],
 [cell("1", True), cell("Cerrar validacion fisica: control de consenso votante sin ruido con L=10, rc=1 y densidades reales."), cell("Etapa 3 completa y evidencia de regresion representativa.")],
 [cell("2", True), cell("Piloto largo focalizado: votante eta=0 y bajo; tambien densidades bajas cuando N quede definido."), cell("Propuesta sustentada de steps y t_eq por caso/modelo.")],
 [cell("3", True), cell("Revisar evidencia y decidir grilla eta, R, semillas, barras y strides."), cell("Protocolo experimental congelado.")],
 [cell("4", True), cell("Confirmar conversion de densidades bajas y alcance del punto E si se desea ampliarlo."), cell("Matriz de produccion completa y no ambigua.")],
 [cell("5", True), cell("Ejecutar barrido definitivo y agregacion reproducible."), cell("Tablas finales de va y S con barras.")],
 [cell("6", True), cell("Generar animaciones, figuras, benchmark, informe, presentacion y ZIP."), cell("Entregables de Campus completos.")]]
t = Table(road_rows, colWidths=[1.1*cm, 9.0*cm, 7.2*cm], repeatRows=1)
t.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), NAVY), ("GRID", (0,0), (-1,-1), .3, colors.HexColor("#C7D4DE")), ("VALIGN", (0,0), (-1,-1), "TOP"), ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, PALE]), ("LEFTPADDING", (0,0), (-1,-1), 5), ("RIGHTPADDING", (0,0), (-1,-1), 5), ("TOPPADDING", (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5)]))
story += [t, Spacer(1,9), status_box("RESPUESTA A " + "\"QUE ESTAMOS HACIENDO AHORA\"", "Estamos afinando el experimento, no reescribiendo el modelo. El codigo ya permite correr ambos modelos y medir todo lo pedido. Falta convertir los resultados exploratorios en un protocolo defendible: demostrar cuanto tiempo necesita el votante, decidir como muestrear y promediar, y recien entonces lanzar la matriz completa para hacer las figuras y el informe final.", GOLD), Spacer(1,10), P("Pendientes y decisiones abiertas", "H2TP"), P("No quedan pendientes conocidos dentro de la generacion de este documento. Para el TP permanecen abiertos los puntos enumerados en la seccion 4; bloquean el barrido definitivo, las figuras finales, el benchmark y la entrega, pero no bloquean el motor ni la continuacion de los pilotos.", "BodyTP"),
 P("Fuentes de este resumen", "H2TP"), P("Se sintetizaron el enunciado operativo, la guia teorica, la hoja de ruta maestra, la revision de alcance, el registro de decisiones y las etapas 1 a 9 del repositorio. La evidencia tecnica reciente proviene de la compilacion y CTest ejecutados el 30/08/2026 (11/11 pruebas aprobadas) y del piloto documentado de 108 corridas.", "SmallTP")]

doc.build(story)
print(OUT)
