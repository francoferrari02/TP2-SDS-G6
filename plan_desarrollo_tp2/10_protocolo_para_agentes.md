# Etapa 10 - Protocolo de trabajo con agentes

## Objetivo

Permitir desarrollo paralelo sin que distintos agentes inventen convenciones incompatibles o declaren etapas terminadas sin evidencia.

Este documento organiza el trabajo con agentes solicitado para el proyecto. No agrega requisitos científicos ni entregables a los definidos por la cátedra.

## Principio de autoridad

Cada agente debe leer:

1. `AGENTS.md` del repositorio.
2. Las tres fuentes vinculantes de `bibliografia/`.
3. `plan_desarrollo_tp2/README.md`.
4. `plan_desarrollo_tp2/REVISION_FINAL_DE_ALCANCE.md`.
5. `plan_desarrollo_tp2/DECISIONES_PENDIENTES.md`.
6. El documento de su etapa y los documentos previos de los que depende.

Si una tarea contradice la especificación congelada, el agente se detiene y registra el conflicto; no cambia silenciosamente el modelo.

## Seguimiento documental obligatorio

El estado persistente del proyecto vive en los Markdown del repositorio, no solo en la conversación del agente.

- Al comenzar, el agente identifica la etapa, sus dependencias y las decisiones abiertas que podrían bloquearla.
- Durante el trabajo, mantiene actualizadas las listas de verificación del documento de etapa usando `[ ]` y `[x]`.
- Solo tacha una tarea cuando está completa y existe evidencia verificable. Si está parcial, permanece `[ ]` y se documentan tanto lo realizado como lo faltante.
- Al cerrar una etapa, actualiza también el estado correspondiente en `README.md`.
- Si una modificación invalida una verificación previa, vuelve a dejarla pendiente y enumera los artefactos que deben regenerarse.
- Las decisiones no resueltas se registran en `DECISIONES_PENDIENTES.md`; cuando se resuelven, se anota la decisión, fecha, evidencia y alcance afectado.

## Puertas de decisión

Antes de iniciar una etapa, el agente debe distinguir entre una dependencia comprobable y una elección que corresponde al usuario.

- Si falta un resultado previo verificable y producirlo está dentro del alcance, se completa primero esa dependencia.
- Si falta evidencia para decidir, se ejecuta primero un piloto o validación no bloqueada y se presentan sus resultados.
- Si la elección afecta el modelo, alcance, protocolo experimental, formato público, costo de producción o interpretación de una ambigüedad de la cátedra, el agente no elige por cuenta propia.
- En ese caso explica qué se sabe, qué falta, qué etapa queda bloqueada, presenta alternativas con sus consecuencias e invita explícitamente al usuario a pensar y decidir.
- Una recomendación del agente debe estar identificada como tal y nunca presentarse como requisito de la cátedra.

El trabajo preparatorio que no dependa de la decisión puede avanzar, pero no se declara cerrada la etapa ni se inicia producción definitiva usando un supuesto provisional.

## Dependencias

```text
Etapa 1 -> Etapa 2 -> Etapa 3 -> Etapas 4 y 5 -> Etapa 6 -> Etapa 7 -> Etapa 9
                                      |
                                      +-------------> Etapa 8 ->+
```

Paralelización segura:

- En etapa 2, geometría/CIM, reglas y salida pueden trabajarse en ramas/tareas separadas si sus interfaces ya están congeladas.
- En etapa 3, distintos agentes pueden añadir familias de tests sin editar las mismas líneas.
- En producción, corridas son independientes; el manifiesto central asigna `run_id` únicos.
- Figuras y benchmark pueden avanzar en paralelo después de congelar tablas de producción.

No paralelizar decisiones de convención ni permitir que dos agentes editen el mismo archivo de configuración.

## Plantilla de tarea

Cada encargo debe incluir:

```text
Objetivo concreto:
Archivos permitidos:
Entradas/versiones:
Convenciones que no pueden cambiar:
Tests o comandos requeridos:
Artefacto de salida:
Criterio de terminado:
Qué queda explícitamente fuera de alcance:
```

Ejemplo: “Implementar distancia periódica y CIM” no está terminado al compilar; debe coincidir con fuerza bruta, incluir el caso `d=rc`, cruce de bordes y listas sin duplicados.

## Handoff obligatorio

Al cerrar una tarea, el agente entrega:

- resumen de cambios;
- archivos modificados;
- comandos ejecutados y resultados;
- decisiones tomadas y su fuente;
- riesgos o casos no cubiertos;
- datos/configuración usados;
- siguiente paso desbloqueado.

Además, incluye siempre una sección visible de **Pendientes y decisiones abiertas**. Si no hay ninguno para la tarea, lo dice expresamente. Si los hay, indica qué etapa afectan y si bloquean el siguiente paso.

No usar “todos los tests pasan” sin indicar cuáles. No presentar un resultado de piloto como definitivo.

## Propiedad de artefactos

- Un único agente/rol mantiene el contrato de configuración.
- Un único agregador escribe tablas finales.
- Cada corrida escribe solo su propia ruta temporal/final.
- Gráficos son derivados; nunca se corrigen manualmente en lugar de corregir datos/código.
- Los datos crudos son inmutables una vez marcados `complete`.

## Revisiones independientes recomendadas

Antes de producción:

- Revisor A: ecuaciones y reglas de modelo.
- Revisor B: periodicidad, CIM y clusters.
- Revisor C: estadística, `t_eq`, semillas y barras.

Antes de entrega:

- Revisor técnico: reproduce build, tests, una corrida y una figura.
- Revisor científico: contrasta claims con tablas/barras.
- Revisor visual: recorre todas las páginas y links.

El autor de una parte puede corregirla, pero el cierre requiere evidencia o revisión distinta en los puntos críticos.

## Estados del proyecto

Mantener un tablero o Markdown con:

```text
pending | in_progress | blocked | review | complete
```

`complete` significa que el criterio del documento de etapa está satisfecho. Si una corrección cambia el motor después de producción, todos los artefactos derivados vuelven a estado pendiente hasta regenerarse.

## Regla de cambios tardíos

Clasificar todo cambio:

- Solo presentación: no cambia datos; regenerar PDF y revisar.
- Análisis: cambia agregación/figura; regenerar tablas y figuras afectadas.
- Protocolo: cambia `t_eq`, semillas, grilla o `R`; regenerar puntos afectados.
- Motor/modelo: invalida todas las corridas dependientes; repetir barrido completo.

El error de movimiento o la autoinclusión del votante pertenecen a la última categoría.

## Definición global de terminado

El objetivo está realmente completo solo si:

- el motor satisface las ecuaciones y tests;
- el producto cartesiano no tiene faltantes;
- las series justifican estacionariedad;
- tablas y figuras se regeneran automáticamente;
- informe/presentación coinciden con el dataset final;
- el ZIP limpio recompila;
- un tercero puede seguir la procedencia desde figura hasta semilla/configuración.

No se declara terminado el proyecto mientras existan bloqueos, decisiones requeridas, combinaciones faltantes, pruebas fallidas o derivados desactualizados.

## Estado de este protocolo

- [x] Define la fuente de autoridad y el orden de lectura.
- [x] Define cómo actualizar el progreso en los Markdown.
- [x] Define cuándo consultar al usuario en lugar de asumir.
- [x] Exige comunicar pendientes y decisiones abiertas.
- [x] Define dependencias, handoff e invalidación de artefactos.
