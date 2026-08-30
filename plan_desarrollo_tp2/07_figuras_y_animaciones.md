# Etapa 7 - Figuras y animaciones obligatorias

## Objetivo

Generar únicamente los estudios A-E para ambos modelos y la comparación F indicados por el enunciado.

## A. Animaciones características

- Un vector por partícula, ubicado en su posición.
- Dirección y módulo dados por su velocidad.
- Color asociado al ángulo.
- Módulo de animación independiente que lee la salida de texto.
- Pocos casos representativos; las notas del profesor sugieren dos casos bien distintos, de ruido bajo y alto.

Las animaciones deben abrir cada estudio en la presentación. El PDF lleva links explícitos y no las embebe.

## B. Evolución temporal de polarización

Para cada densidad `rho=2,4,8` y situaciones características de `eta`:

- graficar `va(t)`;
- comparar Vicsek y votante bajo el mismo protocolo;
- marcar `t_eq` con una línea vertical;
- explicar la ventana usada para el promedio estacionario.

## C. Polarización estacionaria vs. ruido

```text
x = eta
y = <va>_est
densidades = {2,4,8}
modelos = {vicsek,voter}
barras = definición declarada del protocolo
```

Las tres densidades deben distinguirse claramente mediante curvas o paneles comparables.

## D. Estudio de clusters

Para ambos modelos:

1. graficar `S(t)` en situaciones características;
2. marcar la misma ventana estacionaria usada para `va`;
3. graficar `<S>_est` vs. `eta` con barras de error.

Este punto incluye:

```text
rho = {2,4,8,1/pi,1/(2pi),1/(3pi)}
```

Se recomienda separar densidades base y adicionales en paneles para mantener legibilidad, sin agregar otro estudio.

## E. Relación entre orden y conectividad

El enunciado pide polarización en función de componente gigante:

```text
x = <S>_est
y = <va>_est
cada punto = un eta del barrido
densidades = {2,4,8}
```

Distinguir densidades y modelos. `eta` no es un eje. Este gráfico estudia si conectividad espacial y alineamiento global se relacionan, pero no presupone el resultado.

La ampliación a las tres densidades bajas no se incluye como obligación porque el punto E dice explícitamente “distinguir las tres densidades”. Solo se hará si la cátedra confirma que la aclaración de clusters también abarca este punto.

## F. Comparación entre modelos

Repetir A-E para el votante y comparar contra Vicsek usando:

- mismos parámetros;
- misma grilla de ruido;
- mismo criterio de estacionario;
- misma cantidad de realizaciones;
- misma definición de barras.

## Convenciones de presentación

- `va` y `S` se muestran en su rango `[0,1]`.
- Colores, líneas y marcadores identifican siempre de la misma forma modelo y densidad.
- Cada epígrafe declara `rho`, `eta` cuando corresponda, `R` y significado de barras.
- No se suavizan datos ni se agregan ajustes no solicitados.

La copia de la Guía de Presentaciones incluida en el repositorio de referencia agrega controles de formato que sí son coherentes con la documentación citada por el enunciado:

- en la presentación, la figura no lleva título interno ni *caption*; los parámetros se escriben al costado de la figura;
- los ejes se rotulan preferentemente con palabras y unidades cuando correspondan;
- letras y números dentro de la figura deben tener tamaño legible, al menos 20 para las diapositivas;
- cada dato promedio debe distinguirse con un símbolo o su barra; una línea recta puede usarse como guía visual, pero no una interpolación arbitraria;
- para el PDF se usa un fotograma representativo y un enlace explícito; durante la exposición en vivo la animación debe quedar integrada en la diapositiva, sin salir a otro programa.

El repositorio externo afirma además que la cátedra pidió figuras sin grilla de fondo, `va` y `S` separados y cada modelo individual antes de la superposición comparativa. Mantener estas indicaciones como pendientes de confirmación: no cambian el barrido ni bloquean la generación de tablas, pero sí el diseño visual final.

## Fuera de alcance

No generar susceptibilidad, `eta_c`, histéresis, distribución de tamaños de cluster ni curva de percolación. Ninguna reemplaza los gráficos A-E.

## Criterio de cierre

- [ ] Hay animaciones independientes con vectores coloreados por ángulo.
- [ ] `va(t)` y `S(t)` muestran y justifican `t_eq`.
- [ ] `<va>` vs. `eta` cubre ambos modelos y `rho=2,4,8`.
- [ ] `<S>` vs. `eta` incorpora las densidades adicionales solo en clusters.
- [ ] `<va>` vs. `<S>` usa `S` en x, `va` en y y las tres densidades base.
- [ ] Todos los gráficos tienen barras definidas cuando corresponde.
- [ ] Vicsek y votante se comparan bajo el mismo protocolo.
- [ ] Las exportaciones para diapositivas cumplen tamaños de fuente, ejes, símbolos y ubicación de parámetros de la guía.
- [ ] La versión para exposición integra las animaciones y el PDF usa fotogramas con links probados.
