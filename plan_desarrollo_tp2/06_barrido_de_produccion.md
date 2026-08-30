# Etapa 6 - Barrido definitivo

## Objetivo

Ejecutar todas las combinaciones pedidas con el protocolo fijado en la etapa anterior y producir tablas reproducibles para las figuras.

## Matriz principal obligatoria

Para cada valor de la grilla final:

```text
model in {vicsek,voter}
rho in {2,4,8}
eta in {eta_1,...,eta_K}
realization in {1,...,R}
```

De cada corrida guardar las series `va(t)` y `S(t)`. Para los pocos casos animados, guardar además posiciones y velocidades por instante en texto.

## Extensión del punto de clusters

Para `S(t)` y `<S>` vs. `eta`, agregar en ambos modelos:

```text
rho nominal in {1/pi,1/(2pi),1/(3pi)}
```

Con `L=10` se debe convertir cada densidad a un `N` entero y registrar tanto el valor nominal como el realmente simulado. La cátedra no indicó cómo resolver el valor no entero; usando provisionalmente redondeo al entero más cercano:

| rho nominal | N | rho efectiva |
|---:|---:|---:|
| `1/pi` | 32 | 0.32 |
| `1/(2pi)` | 16 | 0.16 |
| `1/(3pi)` | 11 | 0.11 |

Estas densidades adicionales no se incorporan a `<va>` vs. `eta` ni a `<va>` vs. `<S>` sin una confirmación explícita de la cátedra. El mínimo obligatorio de esos gráficos sigue usando `rho=2,4,8`.

Confirmar la convención de redondeo antes de ejecutar este bloque definitivo.

El formato escalar puede seguir escribiendo `va(t)` junto con `S(t)` porque el motor mide ambos observables; conservar ese dato no crea una figura ni un estudio adicional.

## Control de combinaciones

Antes de ejecutar, generar una tabla con una fila por corrida:

```text
run_id,protocol_id,code_id,model,rho_nominal,rho_effective,N,
eta,realization,seed,steps,t_eq,output_path,status
```

Esto es una herramienta interna para verificar el pedido “hacer todas las combinaciones”. No es un experimento adicional.

`run_id` debe cambiar si cambia cualquier entrada capaz de modificar los datos. `protocol_id` identifica la grilla, duraciones, realizaciones, ventanas y definición estadística; `code_id` identifica la versión del motor. No reutilizar un archivo solo porque su nombre contiene `rho`, `eta` y semilla: antes de aceptarlo, comprobar que coincide también en duración, parámetros fijos, protocolo y código.

Durante la ejecución:

- registrar fallos y repetir únicamente las corridas fallidas con la misma semilla;
- comprobar que `0 <= va <= 1` y `1/N <= S <= 1`;
- comprobar que cada archivo tenga exactamente los instantes/campos esperados y una terminación válida;
- no descartar realizaciones por producir resultados atípicos.

El resumen definitivo se genera solo si la matriz esperada está completa. Registrar fallos y continuar puede ser útil durante la ejecución, pero la agregación final debe fallar si falta una combinación, si un punto tiene menos de `R` realizaciones o si mezcla identificadores de protocolo/código. No producir silenciosamente barras con un `n_realizations` menor al acordado.

## Agregación

Para cada `(model,rho,eta)`:

1. promediar `va(t)` y `S(t)` en la ventana estacionaria de cada realización;
2. promediar esos resultados entre realizaciones;
3. calcular la barra según la definición fijada;
4. guardar `R`, `t_eq` y semillas junto al resumen.

Tablas mínimas:

```text
per_realization.csv
summary.csv
```

## Fuera de alcance

No se agrega un barrido continuo de densidad, percolación estática, susceptibilidad ni estimación de transición crítica. La extensión de densidad se limita al estudio de cluster solicitado.

## Criterio de cierre

- [ ] Están todas las combinaciones de dos modelos, tres densidades base y todos los `eta`.
- [ ] El bloque de clusters incluye las tres densidades adicionales.
- [ ] Cada punto tiene la cantidad `R` acordada de realizaciones válidas.
- [ ] No hay corridas fallidas o incompletas sin resolver.
- [ ] Las tablas se obtienen aplicando el promedio temporal y entre realizaciones definido.
- [ ] Se pueden rastrear parámetros y semilla de cualquier resultado.
- [ ] Ningún dato de piloto o de un protocolo/código anterior fue reutilizado como producción.
- [ ] La agregación verifica el producto cartesiano y exige exactamente `R` realizaciones por punto.
