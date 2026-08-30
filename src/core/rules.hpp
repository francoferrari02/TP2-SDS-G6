#pragma once

#include "core/model.hpp"

#include <cmath>
#include <cstddef>
#include <cstdint>
#include <random>
#include <unordered_map>
#include <vector>

namespace tp2 {

// Reglas de orientación de Vicsek y votante ruidoso.
//
// Alcance de este archivo: solo calcula la orientación nueva de cada
// partícula a partir del estado viejo (`particles[i].theta`) y de las
// listas de vecinos externos ya calculadas (por `brute_force_neighbors` o
// `cell_index_neighbors`, en `neighbor_search.hpp`). No recalcula
// periodicidad ni vecindad: reutiliza las listas de `id` que recibe.
//
// Ninguna de las dos funciones modifica `particles`; ambas devuelven un
// `std::vector<double>` nuevo, indexado por posición (igual que
// `particles` y que las listas de vecinos), con las orientaciones nuevas.
// Esto hace que la actualización sea compatible con sincronía: todas las
// orientaciones nuevas se calculan leyendo exclusivamente el vector
// `particles` de entrada (estado viejo), nunca el vector de salida.
//
// Generador aleatorio y orden de almacenamiento:
// en vez de recibir un único `std::mt19937&` compartido y consumirlo en el
// orden en que aparecen las partículas en el vector, cada partícula deriva
// su propio sub-generador a partir de una semilla explícita (`seed`, provista
// por quien llama, nunca sembrada con el reloj) combinada con su `id`
// estable. Consumir un generador compartido en orden de índice de vector
// haría que el resultado dependiera de en qué posición quedó almacenada
// cada partícula, y no solo de su `id` y sus vecinos: dos ejecuciones con
// la misma semilla pero con las partículas permutadas darían orientaciones
// distintas para el mismo `id`. Derivar el sub-generador de `(seed, id)`
// evita ese problema por construcción: el resultado de la partícula `id`
// depende únicamente de `seed`, su propio estado y el de sus vecinos
// (identificados también por `id`), nunca de la posición de almacenamiento.
// Sigue siendo reproducible (misma `seed` -> mismo resultado) y sigue
// permitiendo que una `seed` distinta dé resultados distintos.

inline constexpr double kPi = 3.14159265358979323846;
inline constexpr double kTwoPi = 2.0 * kPi;

// Normaliza un ángulo a `[0, 2*pi)`.
inline double normalize_angle(double theta) {
    double wrapped = std::fmod(theta, kTwoPi);
    if (wrapped < 0.0) {
        wrapped += kTwoPi;
    }
    return wrapped;
}

// Combina una semilla explícita con el `id` de una partícula para obtener
// un generador determinista, independiente del orden de almacenamiento.
// El mezclado (variante del finalizador de MurmurHash3 / splitmix64) evita
// que ids consecutivos produzcan generadores con estados triviales o muy
// correlacionados entre sí.
inline std::mt19937 make_particle_rng(std::uint64_t seed, std::size_t id) {
    std::uint64_t state = seed ^ (static_cast<std::uint64_t>(id) * 0x9E3779B97F4A7C15ULL +
                                   0xBF58476D1CE4E5B9ULL);
    state ^= state >> 33;
    state *= 0xFF51AFD7ED558CCDULL;
    state ^= state >> 33;
    state *= 0xC4CEB9FE1A85EC53ULL;
    state ^= state >> 33;
    return std::mt19937(static_cast<std::mt19937::result_type>(state));
}

// Ruido angular uniforme `xi ~ U[-eta/2, eta/2]`, común a ambas reglas.
// `eta <= 0` se trata como "sin ruido" (devuelve 0 exactamente, sin
// consumir el generador), lo que permite comparar resultados de forma
// determinista en los tests con `eta=0`.
inline double sample_angular_noise(std::mt19937& rng, double eta) {
    if (eta <= 0.0) {
        return 0.0;
    }
    std::uniform_real_distribution<double> noise_distribution(-eta / 2.0, eta / 2.0);
    return noise_distribution(rng);
}

namespace detail {

// Mapa auxiliar `id -> posición en el vector`, necesario porque las listas
// de vecinos (`neighbor_search.hpp`) están expresadas en `id` estables, no
// en índices de vector.
inline std::unordered_map<std::size_t, std::size_t> index_particles_by_id(
    const std::vector<Particle>& particles) {
    std::unordered_map<std::size_t, std::size_t> id_to_index;
    id_to_index.reserve(particles.size());
    for (std::size_t index = 0; index < particles.size(); ++index) {
        id_to_index.emplace(particles[index].id, index);
    }
    return id_to_index;
}

}  // namespace detail

// Regla de Vicsek estándar: la orientación nueva de cada partícula es el
// promedio vectorial (no aritmético) de su propia orientación y la de
// todos sus vecinos externos, más ruido independiente.
//
//   theta_base   = atan2(sum sin(theta_j), sum cos(theta_j))   [incluye a i]
//   theta_new[i] = normalize(theta_base + xi),  xi ~ U[-eta/2, eta/2]
//
// Promediar con `atan2(sum_sin, sum_cos)` evita el error de promediar
// ángulos directamente (por ejemplo `1°` y `359°` promediando mal a
// `180°` en vez de a `0°`).
//
// `seed` es una semilla explícita (no sembrada con el reloj); el ruido de
// cada partícula sale de un sub-generador derivado de `(seed, particles[i].id)`
// (ver `make_particle_rng`), así que el resultado no depende del orden de
// almacenamiento de `particles`.
inline std::vector<double> vicsek_update(
    const std::vector<Particle>& particles,
    const std::vector<std::vector<std::size_t>>& neighbors,
    double eta,
    std::uint64_t seed) {
    const std::size_t count = particles.size();
    std::vector<double> new_theta(count);
    const auto id_to_index = detail::index_particles_by_id(particles);

    for (std::size_t i = 0; i < count; ++i) {
        double sum_sin = std::sin(particles[i].theta);
        double sum_cos = std::cos(particles[i].theta);
        for (const std::size_t neighbor_id : neighbors[i]) {
            const std::size_t j = id_to_index.at(neighbor_id);
            sum_sin += std::sin(particles[j].theta);
            sum_cos += std::cos(particles[j].theta);
        }
        const double theta_base = std::atan2(sum_sin, sum_cos);
        std::mt19937 particle_rng = make_particle_rng(seed, particles[i].id);
        new_theta[i] = normalize_angle(theta_base + sample_angular_noise(particle_rng, eta));
    }

    return new_theta;
}

// Regla de votante ruidoso: si la partícula tiene vecinos externos, elige
// exactamente uno al azar (nunca a sí misma, porque `neighbors[i]` nunca
// contiene a `i`) y copia su orientación vieja. Si no tiene vecinos,
// conserva su propia orientación vieja. En ambos casos suma después el
// mismo ruido `xi ~ U[-eta/2, eta/2]`.
//
// Con `eta=0`, `theta_new[i]` es siempre una orientación que ya existía en
// el estado viejo (la propia o la de un vecino elegido).
//
// `seed` funciona igual que en `vicsek_update`: tanto la elección del
// vecino como el ruido de la partícula `i` salen de un único sub-generador
// derivado de `(seed, particles[i].id)`, así que ni la elección ni el
// ruido dependen del orden de almacenamiento.
inline std::vector<double> voter_update(
    const std::vector<Particle>& particles,
    const std::vector<std::vector<std::size_t>>& neighbors,
    double eta,
    std::uint64_t seed) {
    const std::size_t count = particles.size();
    std::vector<double> new_theta(count);
    const auto id_to_index = detail::index_particles_by_id(particles);

    for (std::size_t i = 0; i < count; ++i) {
        std::mt19937 particle_rng = make_particle_rng(seed, particles[i].id);
        double base_theta = particles[i].theta;
        if (!neighbors[i].empty()) {
            std::uniform_int_distribution<std::size_t> pick_neighbor(
                0, neighbors[i].size() - 1);
            const std::size_t chosen_id = neighbors[i][pick_neighbor(particle_rng)];
            const std::size_t j = id_to_index.at(chosen_id);
            base_theta = particles[j].theta;
        }
        new_theta[i] = normalize_angle(base_theta + sample_angular_noise(particle_rng, eta));
    }

    return new_theta;
}

}  // namespace tp2
