#pragma once

#include "core/model.hpp"
#include "core/periodic_geometry.hpp"
#include "core/rules.hpp"

#include <cmath>
#include <cstddef>
#include <cstdint>
#include <functional>
#include <vector>

namespace tp2 {

// Paso temporal sincrónico completo (Vicsek o votante), reutilizando la
// búsqueda de vecinos (`neighbor_search.hpp`) y las reglas de orientación
// (`rules.hpp`) ya implementadas. Este archivo no duplica ninguna de esas
// dos cosas: solo las combina en el orden que exige la sincronía.
//
// Alcance: únicamente el paso temporal (orientación + movimiento +
// repliegue periódico). No incluye clusters, observables `va`/`S`, salida
// de texto ni CLI.

enum class InteractionRule { kVicsek, kVoter };

// Firma de una función de búsqueda de vecinos compatible con
// `brute_force_neighbors`/`cell_index_neighbors`: recibe el estado y los
// parámetros, devuelve listas de `id` de vecinos externos indexadas por
// posición. Se pasa como parámetro (en vez de fijar una sola
// implementación) para poder validar el paso temporal tanto con el oráculo
// de fuerza bruta como con el CIM, sin duplicar la lógica del paso.
using NeighborSearchFunction = std::function<std::vector<std::vector<std::size_t>>(
    const std::vector<Particle>&, const Parameters&)>;

// Ejecuta un paso temporal sincrónico completo a partir del estado viejo
// `particles` (que no se modifica) y devuelve el estado nuevo completo,
// respetando exactamente este orden:
//
// 1. Construir la lista de vecinos usando las posiciones `x(t)` (el propio
//    `particles` de entrada, antes de mover nada).
// 2. Calcular todas las orientaciones nuevas usando solamente `theta(t)`
//    (delegado en `vicsek_update`/`voter_update`, que ya garantizan esto:
//    leen `particles` y devuelven un vector nuevo sin tocar el viejo).
// 3. Calcular todas las posiciones nuevas usando la orientación vieja
//    `theta(t)`, nunca `theta(t+1)`:
//
//      x_new = x(t) + v * cos(theta(t)) * dt
//      y_new = y(t) + v * sin(theta(t)) * dt
//
//    Es un movimiento "backward": la orientación nueva recién calculada en
//    el paso 2 no participa en el movimiento de este mismo paso, solo
//    quedará disponible para el paso siguiente.
// 4. Aplicar el borde periódico (`periodic_wrap`) a todas las posiciones
//    nuevas.
// 5. El estado completo nuevo se arma en un `std::vector<Particle>`
//    separado del de entrada; la sustitución de `x(t)`/`theta(t)` por
//    `x(t+1)`/`theta(t+1)` ocurre en un único punto, al devolver ese
//    vector nuevo. Nada del vector de entrada se sobrescribe en ningún
//    momento intermedio.
inline std::vector<Particle> advance_time_step(const std::vector<Particle>& particles,
                                                const Parameters& parameters, double eta,
                                                InteractionRule rule, std::uint64_t seed,
                                                const NeighborSearchFunction& neighbor_search) {
    // Paso 1: vecinos a partir de x(t), estado viejo sin tocar.
    const std::vector<std::vector<std::size_t>> neighbors = neighbor_search(particles, parameters);

    // Paso 2: orientaciones nuevas a partir únicamente de theta(t). `seed`
    // se combina con el `id` de cada partícula dentro de
    // `vicsek_update`/`voter_update` (ver `rules.hpp`), así que el
    // resultado no depende del orden de almacenamiento de `particles`.
    const std::vector<double> new_theta = (rule == InteractionRule::kVicsek)
                                               ? vicsek_update(particles, neighbors, eta, seed)
                                               : voter_update(particles, neighbors, eta, seed);

    // Pasos 3-4: posiciones nuevas a partir de theta(t) (no de new_theta),
    // con repliegue periódico.
    const double speed = parameters.speed;
    const double dt = parameters.time_step;
    const double box_length = parameters.box_length;

    std::vector<Particle> next_state(particles.size());
    for (std::size_t i = 0; i < particles.size(); ++i) {
        const double theta_old = particles[i].theta;
        const double x_new = particles[i].x + speed * std::cos(theta_old) * dt;
        const double y_new = particles[i].y + speed * std::sin(theta_old) * dt;

        next_state[i].id = particles[i].id;
        next_state[i].x = periodic_wrap(x_new, box_length);
        next_state[i].y = periodic_wrap(y_new, box_length);
        next_state[i].theta = new_theta[i];
    }

    // Paso 5: el estado completo nuevo se devuelve de una sola vez; quien
    // llama lo asigna sobre el estado viejo (por ejemplo
    // `particles = advance_time_step(particles, ...)`), que reemplaza
    // `x(t)`/`theta(t)` por `x(t+1)`/`theta(t+1)` en un único punto.
    return next_state;
}

}  // namespace tp2
