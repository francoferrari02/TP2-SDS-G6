# Etapa 9 - Informe, presentación y entrega

## Objetivo

Cerrar el trabajo con una narrativa fiel a los datos, una exposición de 13 minutos y un ZIP de código pequeño y reproducible.

## Progreso parcial (2026-08-30)

- [ ] Se inició el informe colaborativo en Google Docs, `Informe TP2` (`https://docs.google.com/document/d/1t1TD7r5sQ0huV8YJaWgmTALZbk2qWMn7GYGv24nLJtY/edit`). Contiene carátula e índice con campos administrativos reservados, espacios explícitos para Introducción, Modelo e implementación, Clusters, Rendimiento, Conclusiones y Referencias, y la redacción completa de Polarización. Esta última incorpora siete figuras: dos configuraciones características, dos series temporales, dos curvas estacionarias y una comparación Vicsek-votante. El texto declara el protocolo final (`rho={2,4,8}`, `N={200,400,800}`, `R=20`, `steps=3000`, `t_eq=1500`, ventana `1500..3000`) y que barras/bandas son desvíos estándar entre realizaciones; evita atribuir causalidad no medida o estimar una transición crítica.
  - Evidencia: lectura estructurada posterior a la escritura: 59 párrafos, 7 objetos de imagen insertados, 0 marcadores `<<FIG_*>>` residuales y jerarquía nativa de títulos para portada, índice, secciones 1--7, subsecciones 3.1 y 4.1--4.3. Se solicitó exportación HTML/PDF, pero el conector devolvió referencias de archivo sin una ruta local materializable, por lo que todavía no se hizo revisión visual página a página del PDF.
  - Actualización 2026-09-03: se ajustaron los textos y captions para igualar las figuras usadas en la PPT: Vicsek temporal `eta={1,3,5}`, configuración de votante `eta={0.1,1}`, votante temporal `eta={0.05,0.3,1}` y una comparación única superpuesta, sin paneles. Lectura posterior confirmó las ocho sustituciones y no encontró las referencias obsoletas.
  - Actualización 2026-09-03: la sección `7. Conclusiones` ahora contiene la síntesis correspondiente a Polarización: dependencia con el ruido, mayor robustez de Vicsek, ordenamientos de densidad observados en ambos modelos, mayor variabilidad del votante, distinción entre `S` y `va`, y el alcance explícito de no estimar un punto crítico. Las conclusiones de clusters y rendimiento siguen pendientes de integración por el equipo.
  - Estado: en progreso. Falta que el equipo complete sus secciones, datos de carátula, referencias, enlaces de animaciones y la revisión final conjunta contra la presentación y el PDF de entrega.

- [x] Se creó el borrador avanzado local de la presentación en `output/presentation/TP2_Bandadas_Borrador_Presentacion.pptx`: 21 diapositivas para la exposición de 13 minutos y 12 de apéndice, en 16:9, con dirección visual propia azul marino/índigo, 29 PNG finales embebidos y notas del orador en las 33 diapositivas. La PPT usa únicamente `figures/final_production_v1/` y `figures/reference_snapshots_v1/`, conserva el protocolo `R=20`, `steps=3000`, `t_eq=1500` y desvío estándar, y declara como pendientes las animaciones, el benchmark y grupo/comisión.
  - Evidencia: se renderizaron e inspeccionaron individualmente las 33 diapositivas y se generó un montage; `slides_test.py output/presentation/TP2_Bandadas_Borrador_Presentacion.pptx` informó `Test passed. No overflow detected.`; el paquete contiene 33 `slide*.xml`, 33 `notesSlide*.xml` y 29 recursos en `ppt/media/`. La búsqueda sobre el texto visible no encontró `eta_c` ni susceptibilidad.
  - Alcance: cierra la creación y QA de este borrador PPTX, pero no la etapa 9. Siguen pendientes el informe final, animaciones y links, benchmark, grupo/comisión, PDF final y ZIP de código.

- [x] Se creó `output/presentation/TP2_Bandadas_Borrador_Presentacion_clarificada.pptx` como copia revisada del borrador. La diapositiva 12 ahora comunica explícitamente que compara estados de polarización instantánea casi idéntica (`va≈0.515`), identifica Vicsek a la izquierda (`eta=3`) y votante a la derecha (`eta=0.4`), y separa los parámetros comunes. El fotograma y las otras 32 diapositivas se preservaron.
  - Evidencia: render de las 33 diapositivas, inspección visual individual de la diapositiva 12, `slides_test.py` sin overflow y control de fidelidad de plantilla con `0` problemas.
  - Alcance: cierra esta corrección de claridad, no la etapa 9 ni el punto A de animaciones.

- [x] El 2026-08-31 se auditó el borrador clarificado contra la guía oficial `GuiaPresentaciones.pdf` y se exportó `output/presentation/TP2_Bandadas_Presentacion_reestructurada_guia_catedra.pptx`, preservando las figuras y los datos. La copia tiene 22 diapositivas de exposición y 11 de apéndice. Se eliminaron los rótulos `SECCIÓN 1/2/3`, se movió la arquitectura de salida/visualización desde Implementación a Simulaciones, se creó un separador exclusivo de Conclusiones y se quitó de la conclusión el texto de trabajo pendiente.
  - Evidencia: render completo de 33 diapositivas; inspección visual específica de las diapositivas 4-8, 11 y 21-23; `slides_test.py` informó `Test passed. No overflow detected.`; `check_template_fidelity.mjs` informó `0` problemas.
  - Diagnóstico: ya cumple estructura por secciones sin numerarlas, numeración de diapositivas, introducción breve, bajo volumen de texto, conclusión única basada en resultados y ausencia de bibliografía. Aún no cumple por completo la integración de animaciones/enlaces, la ubicación lateral de parámetros en todas las diapositivas de resultados, el esquema explícito de la simulación ni el reparto de expositores.
  - Alcance: cierra la primera reestructuración segura exigida por la guía, no la presentación final ni la etapa 9.

- [x] Se creó `PLAN_PPT_TP2.md` en la raíz como guion de 21 diapositivas para una exposición de 13 minutos. Asigna a cada resultado final disponible de `figures/final_production_v1/` y a los fotogramas estáticos de `figures/reference_snapshots_v1/` una ubicación narrativa, y marca explícitamente como pendientes las animaciones, el benchmark, los datos administrativos y los enlaces. No constituye la PPT ni cierra criterios de esta etapa.

- [x] Se generó una síntesis interna del estado para ubicar al grupo frente al enunciado: `output/pdf/estado_actual_tp2_explicado.pdf`. Explica el alcance, motor, validaciones, piloto de 108 corridas, decisiones tomadas y pendientes, y la secuencia que falta hasta la entrega.
  - Evidencia: el PDF se renderizó y revisó en cinco páginas A4; `pdfinfo` confirmó cinco páginas y la extracción de texto confirmó contenido en todas. En la misma revisión se ejecutó `cmake --build build` y `ctest --test-dir build --output-on-failure`, con 11/11 pruebas aprobadas.
  - Alcance: artefacto de orientación interna. No reemplaza el informe final, la presentación ni los resultados definitivos y por ello los criterios de cierre de esta etapa permanecen abiertos.

## Estructura narrativa sugerida

1. Sistema y pregunta: cómo ruido, densidad y regla de interacción afectan orden y conectividad.
2. Modelo: dominio, condiciones periódicas, ruido, Vicsek, votante y movimiento backward.
3. Implementación: sincronía, CIM, componentes conexas y texto desacoplado.
4. Validación: borde, vecinos medios, fuerza bruta, observables y consenso votante sin ruido.
5. Protocolo: grilla de `eta`, pilotos, `t_eq`, realizaciones y barras.
6. Animaciones/casos característicos.
7. Polarización temporal y estacionaria.
8. Clusters, incluida extensión de densidades.
9. Relación `va(S)` y comparación de modelos.
10. Rendimiento CIM.
11. Conclusiones limitadas por la evidencia.

## Qué debe quedar escrito sin ambigüedad

- `xi ~ U[-eta/2,eta/2]` y `eta` en radianes.
- Posición avanza con `v(t)`.
- Vicsek incluye a sí misma; votante elige otra partícula.
- `S=n_max/N` y clusters usan borde periódico.
- Cómo se eligió `t_eq`.
- Primero promedio temporal por realización, luego promedio entre realizaciones.
- Qué significan las barras y cuántas realizaciones hay.
- Densidad nominal, `N` y densidad efectiva de los casos `1/pi`.
- Qué parte del tiempo se cronometró.

## Discusión responsable

- Hablar de tendencias observadas, no de resultados “forzados” por teoría.
- No llamar transición crítica precisa a un cambio localizado por una grilla gruesa.
- No dar más decimales que la resolución/variabilidad permite.
- Distinguir conectividad de alineamiento.
- No incorporar análisis extra como si fueran parte del enunciado.
- Indicar `N=11,16,32` al presentar las densidades adicionales.
- Si `S` satura en densidades altas, presentarlo como resultado y usar las bajas para ampliar el estudio, no reemplazar las obligatorias.

## Presentación de 13 minutos

La exposición debe respetar los 13 minutos indicados y seguir las secciones de la guía oficial: Introducción/Sistema real/Fundamentos, Implementación, Simulaciones, Resultados y Conclusiones. Los separadores contienen solo el título de la sección y las secciones no se numeran. Abrir cada estudio con la animación o un fotograma y enlace explícito. Ensayar con cronómetro sin eliminar evidencia obligatoria para incluir análisis adicionales.

La presentación y el informe son documentos autocontenidos: no dejar una definición, cantidad de repeticiones o parámetro solamente en uno suponiendo que el lector consultará el otro. Numerar las diapositivas. En la presentación, ubicar los parámetros al costado de cada figura y no dentro de un título/caption del gráfico; usar ejes legibles y fuente de al menos 20. La versión usada para exponer integra las animaciones; el PDF entregado las reemplaza por un fotograma representativo y un enlace explícito.

## Trazabilidad de números

Crear una tabla o script que alimente directamente valores citados en texto. Antes de compilar entregables:

- buscar placeholders, `TODO`, enlaces vacíos y legajos incompletos;
- comparar títulos/captions con parámetros reales;
- verificar que cada figura se generó con el commit/config final;
- revisar que informe y presentación no citen números de pilotos;
- comprobar consistencia de símbolos (`va`, `S`, `eta`, `rho`).

Usar una única tabla de protocolo como fuente para duración, `R`, semillas, `t_eq`, barras y grilla. Después de cualquier cambio del motor o protocolo, invalidar datos y derivados afectados antes de volver a compilar. La revisión debe comparar también las ecuaciones y reglas escritas contra el código final: que el motor se haya corregido no actualiza automáticamente una ecuación vieja del informe.

## ZIP de código

Incluir solo el código fuente final del motor y lo mínimo para compilar/ejecutar, según el enunciado. Excluir:

- `.git` e historial;
- PDFs, documentación extensa y presentaciones;
- datos, figuras, GIFs y logs;
- binarios y objetos;
- entornos virtuales/cachés.
- archivos del sistema/editor como `.DS_Store`.

Verificar el ZIP extrayéndolo en un directorio temporal limpio, compilando y ejecutando self-tests/smoke test. Documentar formato de salida en un README breve si el límite lo permite.

## Revisión visual final

Renderizar informe y presentación completos y revisar todas las páginas:

- texto no recortado ni superpuesto;
- figuras legibles y nítidas;
- ecuaciones correctas;
- numeración/referencias consistentes;
- links clicables;
- portada, autores, comisión y fecha correctos.

## Criterio de cierre

- [ ] Informe y presentación contienen los mismos resultados finales.
- [ ] Todas las figuras obligatorias aparecen y son legibles.
- [ ] Animaciones publicadas y enlaces probados.
- [ ] Método estadístico y actualización backward declarados.
- [ ] Claims compatibles con incertidumbre y tamaño finito.
- [ ] Benchmark describe exactamente qué mide.
- [ ] Ecuaciones, reglas y tabla de protocolo coinciden entre código, informe, presentación y figuras.
- [ ] ZIP limpio recompila y pasa tests desde cero.
- [ ] Nombres de archivos y entrega coinciden con el enunciado.
