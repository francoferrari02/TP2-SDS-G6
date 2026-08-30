#pragma once

#include "core/model.hpp"
#include "core/time_step.hpp"

#include <cstddef>
#include <cstdint>
#include <functional>
#include <vector>

namespace tp2 {

// Bucle reutilizable que encadena muchos pasos de `advance_time_step`.
//
// Alcance: únicamente la iteración en memoria (mantener sincronía,
// movimiento backward, reproducibilidad, invariancia al orden e
// independencia de sorteos entre pasos). No incluye escritura de texto, CLI,
// promedios estacionarios, `t_eq` ni realizaciones independientes; esas
// piezas se agregan en tareas posteriores sobre esta misma interfaz.

// Callback opcional que observa el estado en cada paso. Recibe el número de
// paso y el estado correspondiente por `const&`: no puede modificar el
// estado interno de la simulación, solo leerlo (por ejemplo, para acumular
// una serie temporal de `va`/`S` más adelante, sin mezclar esa
// responsabilidad con este bucle).
using StateObserver = std::function<void(std::size_t step, const std::vector<Particle>& state)>;

// Deriva una semilla de paso a partir de una semilla base y el número de
// paso, combinándolas con un mezclado determinista (variante del
// finalizador de MurmurHash3 / splitmix64, con constantes distintas de las
// de `make_particle_rng` en `rules.hpp` para no correlacionar ambos
// mezclados). `advance_time_step` combina esta `step_seed` con el `id` de
// cada partícula (dentro de `vicsek_update`/`voter_update`), así que el
// sorteo final de cada partícula en cada paso depende de la terna completa
// `(base_seed, step, id)`, nunca de la posición de almacenamiento.
inline std::uint64_t derive_step_seed(std::uint64_t base_seed, std::size_t step) {
    std::uint64_t state = base_seed ^ (static_cast<std::uint64_t>(step) * 0xD6E8FEB86659FD93ULL +
                                        0xA24BAED4963EE407ULL);
    state ^= state >> 30;
    state *= 0xBF58476D1CE4E5B9ULL;
    state ^= state >> 27;
    state *= 0x94D049BB133111EBULL;
    state ^= state >> 31;
    return state;
}

// Ejecuta `steps` pasos temporales sincrónicos a partir de `initial_state`
// (que no se modifica) y devuelve el estado final completo.
//
// Ciclo de vida de los estados y de los pasos observados:
//
// - `step=0` es el estado inicial `initial_state`, tal cual, sin ningún
//   avance todavía. Si se provee `observer`, se lo llama una única vez con
//   `(0, initial_state)` antes de ejecutar el primer paso. Ninguna semilla
//   se consume para producir este estado: `step=0` no corresponde a ningún
//   sorteo, es el punto de partida.
// - Para cada `t` de `1` a `steps`, se deriva `step_seed =
//   derive_step_seed(base_seed, t)` y se ejecuta `advance_time_step` una
//   vez sobre el estado producido por el paso anterior (nunca sobre
//   `initial_state` salvo en `t=1`), usando esa `step_seed`. Si se provee
//   `observer`, se lo llama con `(t, estado_después_del_paso_t)`
//   inmediatamente después de calcularlo.
// - `steps=0` es un caso válido: no se ejecuta ningún avance, `observer` (si
//   existe) se llama solamente con `step=0`, y la función devuelve
//   `initial_state` sin cambios.
// - El valor devuelto es el estado después de `steps` avances (o
//   `initial_state` si `steps=0`).
//
// `rule` y `neighbor_search` se aplican sin cambios en todos los pasos: el
// mismo modelo (Vicsek o votante) y la misma función de búsqueda de vecinos
// (fuerza bruta o CIM) se usan durante toda la corrida.
inline std::vector<Particle> run_simulation(const std::vector<Particle>& initial_state,
                                             const Parameters& parameters, double eta,
                                             InteractionRule rule, std::size_t steps,
                                             std::uint64_t base_seed,
                                             const NeighborSearchFunction& neighbor_search,
                                             const StateObserver& observer = {}) {
    std::vector<Particle> state = initial_state;

    if (observer) {
        observer(0, state);
    }

    for (std::size_t step = 1; step <= steps; ++step) {
        const std::uint64_t step_seed = derive_step_seed(base_seed, step);
        state = advance_time_step(state, parameters, eta, rule, step_seed, neighbor_search);

        if (observer) {
            observer(step, state);
        }
    }

    return state;
}

}  // namespace tp2
