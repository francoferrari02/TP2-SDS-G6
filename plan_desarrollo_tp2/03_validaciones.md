# Etapa 3 - Validaciones que habilitan el barrido

## Regla de avance

No ejecutar el barrido definitivo si alguna validación crítica falla. Un test que solo reproduce la implementación no es evidencia: los resultados esperados deben derivarse de la ecuación, de una construcción manual o de un oráculo independiente.

## 1. Geometría periódica

Casos deterministas:

- Partículas en `x=0.1` y `x=9.9`, igual `y`, deben estar separadas por 0.2.
- Repetir cruzando `y` y una esquina.
- Una separación exactamente `rc` debe contar como vecina.
- Una separación `rc+epsilon` no debe contar.
- `periodic_wrap` siempre deja coordenadas en `[0,L)` incluso para desplazamientos negativos.

## 2. CIM contra fuerza bruta

Para muchos estados pequeños y semillas:

```text
sorted(neighbors_CIM[i]) == sorted(neighbors_bruteforce[i]) para todo i
```

Probar posiciones aleatorias y construcciones adversarias: bordes, esquinas, varias partículas en una celda y pares justo en el radio. Verificar listas simétricas, sin duplicados ni autoaristas.

Fuerza bruta queda únicamente como oráculo interno de test, no como motor productivo ni como estudio adicional.

## 3. Número medio inicial de vecinos

Promediar muchas inicializaciones uniformes. Para las densidades base, el número medio de otros vecinos debe aproximar:

| rho | valor asintótico `rho*pi*rc^2` |
|---:|---:|
| 2 | 6.283 |
| 4 | 12.566 |
| 8 | 25.133 |

No exigir igualdad exacta a una sola inicialización: la guía pide verificar que el promedio de varias condiciones iniciales se aproxime a esos valores.

## 4. Polarización

- Todas las orientaciones iguales: `va=1` dentro de tolerancia numérica.
- Pares opuestos balanceados: `va=0` dentro de tolerancia.
- Para estados aleatorios: `0 <= va <= 1`.

## 5. Promedio circular de Vicsek

- Dos ángulos `1 grado` y `359 grados` deben promediar cerca de `0`, no de `180`.
- Una partícula aislada con `eta=0` conserva su ángulo porque el promedio incluye a sí misma.
- Construcción manual de tres partículas con resultado analítico conocido.

## 6. Votante

- Con un único vecino externo y `eta=0`, debe copiarlo con probabilidad 1; nunca conservarse por autoelección.
- Aislada y `eta=0`: conserva ángulo.
- Aislada y `eta>0`: cambia solo por un ruido dentro de `[-eta/2,eta/2]`.
- Todas las direcciones producidas a `eta=0` deben pertenecer al conjunto de direcciones viejas.
- En sistema finito, `eta=0` debe poder alcanzar consenso polar; usar varias semillas y un horizonte largo como regresión, sin convertirlo en requisito temporal del barrido.

## 7. Sincronía y movimiento backward

Caso mínimo: una partícula en `(0,0)` con `theta_old=0` cuya interacción produce `theta_new=pi/2`, `v=0.03`, `dt=1`.

Resultado obligatorio:

```text
x_new=0.03, y_new=0, theta_new=pi/2
```

El resultado `(0,0.03)` prueba que se usó por error la orientación nueva.

Permutar el almacenamiento de partículas, conservar `id` y repetir un paso con el mismo `(seed,t)`. Al ordenar por `id`, posiciones y ángulos deben coincidir. Probar ambos modelos con ruido distinto de cero.

## 8. Clusters

- Cadena `A-B-C` con `A` no vecina directa de `C`: `S=1` para tres partículas; prueba transitividad.
- Componentes de tamaños 3, 2 y 1: `S=3/6`.
- Partículas conectadas solo a través de borde periódico: misma componente.
- Todas aisladas: `S=1/N`.
- Todas conectadas: `S=1`.
- El algoritmo elegido (BFS/DFS o `union-find`) debe coincidir con casos de componentes construidos manualmente.

## 9. Salida y reproducibilidad

- Misma configuración y semilla: archivos escalares idénticos.
- Semilla distinta: al menos la condición inicial o la dinámica difiere.
- La animación puede leer el formato de texto documentado sin llamar al motor.
- `va` y `S` rotulados con el mismo `t` pertenecen al mismo estado.
- Deshabilitar trayectoria no cambia la serie escalar.

## 10. Pruebas de humo físicas

No son asserts rígidos sobre una transición:

- Vicsek, bajo ruido: tendencia a aumentar polarización.
- Un caso de ruido alto elegido en el barrido debe diferenciarse del caso de ruido bajo.
- Densidad inicial alta: más vecinos medios que densidad baja.
- Votante sin ruido: coarsening/consenso eventual en corridas suficientemente largas.

Si una tendencia no aparece, investigar; no “arreglar” el test forzando un umbral arbitrario.

## Evidencia requerida para cerrar

- [ ] Geometría periódica y `d=rc` correctos.
- [ ] CIM igual a fuerza bruta.
- [ ] Vecinos medios compatibles con teoría.
- [ ] `va` y `S` dentro de límites y casos manuales correctos.
- [ ] Vicsek y votante satisfacen reglas distintas.
- [ ] Movimiento backward demostrado.
- [ ] Invarianza al orden demostrada con ruido.
- [ ] Reproducibilidad y lectura independiente de la salida verificadas.

Al completar esta lista queda habilitada la etapa de pilotos, no todavía la producción definitiva.
