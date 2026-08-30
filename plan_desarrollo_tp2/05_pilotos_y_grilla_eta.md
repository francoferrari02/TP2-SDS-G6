# Etapa 5 - Corridas preliminares y elección del barrido de ruido

## Objetivo

Tomar las decisiones numéricas que la cátedra deja abiertas: valores de `eta`, duración, inicio estacionario, cantidad de realizaciones y casos característicos.

## Qué no está fijado

El enunciado no establece:

- rango ni paso de `eta`;
- cantidad de puntos del barrido;
- cantidad de pasos;
- cantidad de realizaciones;
- semillas;
- definición de las barras.

Por eso no se congela ahora una grilla numérica ni una duración arbitraria.

## Procedimiento mínimo

1. Elegir una grilla inicial gruesa de varios valores de `eta`, expresados con la convención `U[-eta/2,eta/2]`.
2. Ejecutar corridas preliminares para ambos modelos y las densidades `2,4,8`.
3. Inspeccionar `va(t)` y `S(t)` para distinguir transitorio y estacionario.
4. Confirmar que la grilla contiene situaciones cualitativamente diferentes de ruido bajo y alto.
5. Si el cambio de los observables queda mal resuelto, agregar puntos en esa zona.
6. Fijar una grilla final y ejecutarla completa para ambos modelos y las tres densidades.
7. Repetir el procedimiento de `S` para las densidades adicionales del estudio de clusters.

Las densidades adicionales deben pilotarse por separado: con `L=10` tienen solamente `N=32,16,11`, por lo que su tiempo de relajación y variabilidad pueden ser muy distintos de los casos `N=200,400,800`. No extrapolarles automáticamente el mismo `t_eq` ni la misma duración. Si se eligen duraciones distintas por bloque de densidad, documentarlas antes de producción y conservar una ventana estacionaria comparable en significado.

Esta exploración es parte del diseño experimental requerido; no es un estudio adicional.

## Comparabilidad

Para comparar modelos y densidades, conviene usar la misma grilla final de `eta`, la misma cantidad de realizaciones y el mismo criterio estadístico. Si una decisión difiere, debe justificarse y declararse antes del barrido definitivo.

Los pilotos pueden usar una grilla gruesa o duraciones cortas, pero sus archivos deben vivir en rutas o identificadores distintos de la producción. La identidad de una corrida debe incluir, como mínimo, protocolo/versión, modelo, densidad o `N`, `eta`, semilla y cantidad de pasos. Una corrida exploratoria nunca puede sobrescribir ni ser confundida con una definitiva.

## Casos característicos

Las notas del profesor sugieren quedarse con dos casos claramente distintos para series y animaciones:

- un caso de ruido bajo;
- un caso de ruido alto.

Los valores se eligen después de las corridas preliminares. No hace falta animar cada punto del barrido.

## Resultado que debe quedar registrado

Una tabla de protocolo con:

```text
eta_values, transient_steps, measurement_steps,
realizations, seeds, error_definition,
scalar_output_frequency, animation_output_frequency
```

Cada valor debe estar acompañado por una breve justificación basada en las series preliminares o en reproducibilidad/costo.

## Criterio de cierre

- [ ] Hay varios valores de `eta` y situaciones de bajo/alto ruido.
- [ ] La grilla resuelve el cambio observado sin imponer un `eta_c` no solicitado.
- [ ] `t_eq` y duración se justifican con series temporales.
- [ ] Cantidad de realizaciones, semillas y barras quedaron definidas.
- [ ] El mismo protocolo permite comparar Vicsek y votante.
- [ ] La grilla final está registrada antes de producción.
- [ ] Las densidades bajas fueron pilotadas por separado antes de fijar su `t_eq` y duración.
- [ ] Los artefactos de pilotos y producción tienen identidades/rutas incompatibles entre sí.
