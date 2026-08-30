#pragma once

#include "core/model.hpp"

#include <cmath>
#include <cstddef>
#include <cstdint>
#include <random>
#include <vector>

namespace tp2 {

// Inicializador productivo del estado: genera un estado inicial uniforme y
// reproducible, para usarlo tanto en la simulación como en las
// validaciones (evita que cada consumidor tenga su propia función de
// generación de posiciones, como pasaba hasta ahora en
// `tests/test_mean_neighbors.cpp`).
//
// Alcance: únicamente la construcción del estado inicial en memoria. No
// incluye avance temporal (`time_step.hpp`/`simulation.hpp`), reglas de
// orientación (`rules.hpp`) ni búsqueda de vecinos (`neighbor_search.hpp`),
// que no se modifican.
//
// Generador y distribuciones: `std::mt19937_64` (Mersenne Twister de 64
// bits; se eligió sobre el `std::mt19937` de 32 bits porque el resto del
// motor ya usa semillas/derivaciones de 64 bits -- `derive_step_seed`,
// `make_particle_rng` -- y para mantener consistencia con
// `tests/test_mean_neighbors.cpp`, que ya usaba `mt19937_64` antes de esta
// tarea), sembrado únicamente con `seed` (nunca con el reloj ni ninguna otra
// fuente no determinista). Se usa `std::uniform_real_distribution<double>`
// para posición (`[0, box_length)`) y para orientación (`[0, 2*pi)`).
//
// Orden de consumo del generador: para cada `id` de `0` a `count-1`, en ese
// orden, se sortean `x`, luego `y`, luego `theta` (tres sorteos por
// partícula, siempre en ese orden). Esto hace que el estado generado para
// `count` partículas sea, partícula por partícula, idéntico al que se
// generaría para cualquier `count' > count` truncado a las primeras `count`
// partículas -- no es un requisito que pida el TP, pero es una consecuencia
// natural de sortear secuencialmente por `id` creciente, y ayuda a razonar
// sobre la reproducibilidad.
//
// Reproducibilidad: misma `seed` y misma `count` producen exactamente el
// mismo estado (mismos `x`, `y`, `theta` para cada `id`). Una `seed`
// distinta puede (no tiene por qué, pero en la práctica casi siempre lo
// hace) producir un estado distinto. No se modifica `parameters`.
inline std::vector<Particle> initialize_particles(std::size_t count,
                                                    const Parameters& parameters,
                                                    std::uint64_t seed) {
    constexpr double kPi = 3.14159265358979323846;

    std::mt19937_64 rng(seed);
    std::uniform_real_distribution<double> position_distribution(0.0, parameters.box_length);
    std::uniform_real_distribution<double> angle_distribution(0.0, 2.0 * kPi);

    std::vector<Particle> particles;
    particles.reserve(count);
    for (std::size_t id = 0; id < count; ++id) {
        Particle particle;
        particle.id = id;
        particle.x = position_distribution(rng);
        particle.y = position_distribution(rng);
        particle.theta = angle_distribution(rng);
        particles.push_back(particle);
    }
    return particles;
}

// Variante basada en densidad: `count = round(rho * box_length^2)`, y
// delega en `initialize_particles` para no duplicar la lógica de sorteo.
//
// Para las tres densidades obligatorias del TP (`rho=2,4,8` con `L=10`),
// `rho * L^2` ya es un entero exacto (`200`, `400`, `800`), así que el
// redondeo no introduce ninguna aproximación. Esta función no resuelve la
// conversión de las densidades bajas (`1/pi`, `1/(2*pi)`, `1/(3*pi)`), que
// con `L=10` no dan un `N` entero: esa conversión sigue pendiente y
// registrada como decisión abierta en `plan_desarrollo_tp2/DECISIONES_PENDIENTES.md`;
// llamar a esta función con esas densidades redondea con la misma regla que
// cualquier otro `rho` (al entero más cercano), sin que eso implique que la
// decisión ya esté tomada.
inline std::vector<Particle> initialize_particles_from_density(double rho,
                                                                 const Parameters& parameters,
                                                                 std::uint64_t seed) {
    const double exact_count = rho * parameters.box_length * parameters.box_length;
    const auto count = static_cast<std::size_t>(std::llround(exact_count));
    return initialize_particles(count, parameters, seed);
}

}  // namespace tp2
