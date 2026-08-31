# Plan de presentación oral - TP2 Bandadas off-lattice

> Estado al 2026-08-30. Este documento propone una PPT de **13 minutos** a partir de los resultados finales disponibles. No reemplaza el informe ni cierra la etapa 9: las animaciones, el benchmark y los datos administrativos siguen pendientes.

## Principios de la cátedra aplicados

- Duración objetivo: **13 minutos**. La guía general organiza la charla como introducción (<1 min), implementación (~3 min), simulaciones (~2 min), resultados (~8 min) y conclusiones (<1 min).
- Numerar diapositivas y usar separadores de sección breves.
- Poco texto, mínimo de ecuaciones y no leer la diapositiva.
- En gráficos: fuente legible (>=20), sin grilla de fondo, parámetros al costado y no como título/caption interno; `v_a` y `S` separados.
- El PDF entregado lleva fotograma y link visible; la animación se muestra solo durante la exposición. Por ahora solo existen fotogramas estáticos: **no presentarlos como animaciones**.
- Una o dos figuras por diapositiva. Mantener colores de densidad consistentes y declarar que las barras/bandas son desvío estándar entre realizaciones.

## Activos disponibles

### Resultados finales

- [`figures/final_production_v1/README.md`](figures/final_production_v1/README.md): índice, protocolo y trazabilidad de las 36 figuras finales.
- Curvas finales de `v_a`, `S`, series temporales, relación `v_a`-`S` y comparaciones de ambos modelos en `figures/final_production_v1/`.
- Protocolo común: `eta={0,0.05,0.10,0.15,0.20,0.30,0.40,0.50,1,2,3,4,5,6}`, `R=20`, `steps=3000`, `t_eq=1500`; barras y bandas = desvío estándar entre realizaciones.
- Para clusters bajos: `rho_nominal={1/pi,1/(2pi),1/(3pi)}`, `N={32,16,11}`, `rho_effective={0.32,0.16,0.11}`.

### Fotogramas de referencia

- [`figures/reference_snapshots_v1/rho2_model_comparison_snapshot.png`](figures/reference_snapshots_v1/rho2_model_comparison_snapshot.png): Vicsek y votante lado a lado, `rho=2`.
- [`figures/reference_snapshots_v1/vicsek_rho2_snapshot.png`](figures/reference_snapshots_v1/vicsek_rho2_snapshot.png): Vicsek, `eta=3`, `t=2000`.
- [`figures/reference_snapshots_v1/voter_rho2_snapshot.png`](figures/reference_snapshots_v1/voter_rho2_snapshot.png): votante, `eta=0.4`, `t=2000`.
- Las flechas tienen escala visual x15 para legibilidad; la rapidez física sigue siendo `v=0.03` para todas las partículas. Ver el README de esa carpeta.

## Guion principal: 21 diapositivas

La numeración siguiente incluye separadores. Los separadores deben ser muy breves (2-4 segundos): organizan la charla, no agregan explicación.

| # | Sección / título hablado | Contenido visual y mensaje | Activo / estado | Tiempo |
|---:|---|---|---|---:|
| 1 | Portada | Título del TP, materia, grupo, integrantes, comisión y fecha. | **PENDIENTE:** datos administrativos. | 0:15 |
| 2 | Introducción: de reglas locales a orden colectivo | Una imagen simple de bandada o el concepto de agentes autopropulsados. Pregunta: cómo cambian orden y conectividad al variar ruido, densidad y regla local. | Preparar visual introductorio; no necesita resultados. | 0:30 |
| 3 | Dos reglas, misma geometría | Explicar en una línea cada modelo: Vicsek promedia direcciones vecinas; votante copia una **otra** partícula vecina. Mostrar ruido `xi ~ U[-eta/2,eta/2]`. | Dibujar esquema propio, no copiar la PPT externa. | 0:25 |
| 4 | Separador: Implementación | Solo “Implementación” y navegación de sección. | Preparar en plantilla. | 0:03 |
| 5 | Arquitectura desacoplada | Diagrama: motor C++ -> `observables.csv` / `trajectory.csv` -> análisis y visualizador. Explicar que la animación no controla la simulación. | **PENDIENTE:** crear diagrama/UML para la PPT. | 0:35 |
| 6 | Un paso de simulación correcto | Flujo: vecinos con CIM y borde periódico -> nuevas direcciones en buffer -> movimiento con `v(t)` -> pliegue periódico -> observables. Resaltar sincronía y actualización backward. | **PENDIENTE:** diagrama de flujo; el código y tests ya existen. | 0:35 |
| 7 | Validaciones que sostienen los resultados | Tres controles, sin llenar de tests: CIM contra fuerza bruta; vecinos medios; `v_a`/clusters con periodicidad. Mencionar 11/11 CTest en verde. | **PENDIENTE:** iconos/esquema compacto; evidencia disponible en el repositorio. | 0:25 |
| 8 | Separador: Simulaciones y medición | Solo “Simulaciones y medición”. | Preparar en plantilla. | 0:03 |
| 9 | Protocolo experimental | Caja `L=10`, `r_c=1`, `v=0.03`, `dt=1`; `rho={2,4,8}`; grilla de `eta`; `R=20`, `steps=3000`, `t_eq=1500`. Explicar: promedio temporal por realización y luego entre realizaciones; barras = desvío estándar. | Crear tabla/diagrama compacto desde el protocolo final. | 0:40 |
| 10 | Qué medimos | Definir en lenguaje y ecuación corta: polarización `v_a` y fracción de cluster gigante `S=n_max/N`. Aclarar `S` usa componentes conexas con borde periódico. | Preparar ecuaciones limpias; no agregar teoría extra. | 0:30 |
| 11 | Separador: Resultados | Solo “Resultados: ruido, orden y conectividad”. | Preparar en plantilla. | 0:03 |
| 12 | Fotogramas característicos, `rho=2` | Usar `rho2_model_comparison_snapshot.png`. Decir que son estados estacionarios representativos, no videos: Vicsek `eta=3`, votante `eta=0.4`, ambos en `t=2000`. Señalar color=ángulo y flecha=dirección. | Disponible. **PENDIENTE:** reemplazar o acompañar con animación y link visible cuando exista. | 0:35 |
| 13 | Vicsek: relajación y polarización estacionaria | A la izquierda `vicsek_va_t_rho_2.png`; a la derecha `vicsek_va_vs_eta.png` o su zoom. Narrativa: la densidad desplaza el rango de ruido donde se pierde orden. Marcar que la línea vertical es `t_eq=1500`. | Disponible. | 0:45 |
| 14 | Vicsek: conectividad | `vicsek_S_t_rho_2.png` + `vicsek_S_vs_eta.png`. Separar verbalmente conectividad (`S`) de alineamiento (`v_a`). | Disponible. | 0:40 |
| 15 | Vicsek: orden y conectividad no son el mismo observable | `vicsek_va_vs_S.png`. Explicar: cada punto es un `eta`; eje x es `<S>`, eje y es `<v_a>`. | Disponible. | 0:25 |
| 16 | Votante: la región relevante está cerca de ruido bajo | `voter_va_t_rho_2.png` + `voter_va_vs_eta_zoom_0_0p5.png`. Explicar por qué la grilla se densificó en `eta<=0.5`, sin llamar a esto `eta_c`. | Disponible. | 0:45 |
| 17 | Votante: conectividad | `voter_S_t_rho_2.png` + `voter_S_vs_eta.png`. Misma lectura estadística y mismo protocolo que Vicsek. | Disponible. | 0:40 |
| 18 | Votante: orden frente a conectividad | `voter_va_vs_S.png`. Reforzar que el cambio de regla, y no de geometría o protocolo, explica las diferencias observadas. | Disponible. | 0:25 |
| 19 | Clusters a baja densidad | `comparison_S_vs_eta_lowrho.png`. Aclarar etiquetas: densidad nominal, `N=32,16,11` y densidad efectiva. Mensaje: estas densidades hacen visible la fragmentación que en `rho=2,4,8` puede quedar cerca de saturación. | Disponible. | 0:35 |
| 20 | Comparación directa de modelos | `comparison_va_vs_eta.png` + `comparison_S_vs_eta_base.png`; si se vuelve ilegible, usar solo la primera y dejar la segunda en respaldo. Conclusión limitada: el votante pierde polarización en la zona baja de ruido que se resolvió finamente; Vicsek mantiene orden hasta ruido mayor. | Disponible. | 0:45 |
| 21 | Orden, conectividad y cierre | `comparison_va_vs_S.png` pequeño o sin figura si compite con el texto. Tres conclusiones: (1) el ruido controla el orden, (2) la regla modifica fuertemente el rango observado, (3) `S` y `v_a` responden a preguntas distintas. | Disponible. | 0:35 |

Tiempo total estimado: **~10:30-11:00**. Deja 2 minutos para transiciones, explicación oral de las figuras y preguntas breves sin exceder 13 minutos.

## Diapositivas que deben agregarse antes de la entrega final

No incluirlas como “resultados terminados” hasta contar con el material.

| Tema | Ubicación sugerida | Qué falta |
|---|---|---|
| Animaciones (punto A) | Antes de la diapositiva 13 para Vicsek y antes de la 16 para votante. | Generar módulo independiente, videos/GIF y publicar links. En el PDF: fotograma + link visible; en la oral: video integrado. |
| Rendimiento CIM vs. TP1 | Insertar antes de la diapositiva 21. | Definir medición comparable y producir tabla/gráfico. Es obligatorio para el cierre del TP; hoy no hay resultados. |
| Datos de portada y links | Diapositiva 1 y notas del PDF. | Grupo, comisión, integrantes, fecha final y URLs públicas de animaciones. |

Al insertar benchmark y dos diapositivas de animación, recortar tiempo de las diapositivas 15 y 18 o llevar una de las relaciones `v_a`-`S` a respaldo para mantener la exposición en 13 minutos.

## Diapositivas de respaldo (no planificarlas para exponer)

- Series temporales restantes por densidad: `*_va_t_rho_4.png`, `*_va_t_rho_8.png`, `*_S_t_rho_4.png`, `*_S_t_rho_8.png` para ambos modelos.
- Zooms de `S` y de clusters bajos disponibles en `figures/final_production_v1/`.
- Figuras individuales `vicsek_S_vs_eta_lowrho.png` y `voter_S_vs_eta_lowrho.png`.
- Tabla exacta del protocolo, semillas y rutas de datos desde `figures/final_production_v1/README.md`.
- Evidencia de validaciones del motor y formato de salida.

## Checklist de maquetación antes de exportar

- [ ] Portada con datos administrativos completos y sin placeholders.
- [ ] Todas las diapositivas numeradas; separadores coherentes con la navegación.
- [ ] Cada figura tiene ejes y leyenda legibles a pantalla completa; no se inserta una captura de baja resolución.
- [ ] Parámetros de cada figura aparecen al costado y coinciden con los archivos fuente.
- [ ] Cada mención de barra/banda dice “desvío estándar entre realizaciones, R=20”.
- [ ] En series temporales aparece `t_eq=1500` y se explica una sola vez el promedio estacionario.
- [ ] Los fotogramas se nombran como tales; no se afirma que son animaciones.
- [ ] Cuando haya videos, el PDF contiene fotograma + link explícito y probado.
- [ ] El benchmark se incorpora antes de afirmar que la presentación está completa.
- [ ] No aparecen `eta_c`, susceptibilidad, números con precisión artificial ni conclusiones fuera de los datos.
