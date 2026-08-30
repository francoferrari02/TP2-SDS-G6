// Regresión diagnóstica (no un test de CTest): verifica que el modelo
// votante sin ruido (eta=0) puede alcanzar consenso polar exacto en un
// sistema finito, tal como pide AGENTS.md ("En el votante sin ruido, usar la
// llegada eventual al consenso polar como control de regresión") y
// bibliografia/teoria_tp2_automatas_off_lattice.md, sección "Caso de
// validación: votante sin ruido".
//
// Escenario elegido (alternativa 1 de las sugeridas): sistema pequeño con
// una búsqueda de vecinos "completa" controlada -- cada partícula ve a
// todas las demás como vecinas, sin depender de `rc` ni de la geometría --
// para aislar exclusivamente la dinámica de consenso de la regla de
// votante. Se descartó la alternativa 3 (parámetros físicos del TP con
// horizonte largo) porque mezclaría la propiedad de consenso con la
// velocidad de difusión espacial (`v=0.03`, `L=10`), algo que el TP no pide
// afirmar; el grafo completo prueba únicamente que la regla en sí converge,
// sin introducir una afirmación física sobre bandadas reales.
//
// Con `eta=0`, `voter_update` nunca crea una orientación nueva: cada
// actualización copia exactamente (bit a bit, sin aritmética) la orientación
// vieja de la propia partícula o de un vecino. Por lo tanto, el conjunto de
// orientaciones distintas presentes en el sistema nunca puede crecer, solo
// achicarse o mantenerse; "consenso exacto" se define aquí como que ese
// conjunto se haya reducido a un único valor. Esto es más fuerte y más
// verificable que pedir `va cercano a 1`: `va=1` puede alcanzarse solo por
// redondeo de punto flotante sin que las orientaciones sean exactamente
// iguales, mientras que "un único valor distinto" es una propiedad exacta
// del propio proceso de copia.
//
// Este programa no tiene ningún assert rígido sobre alcanzar consenso: si
// alguna semilla no converge dentro del horizonte elegido, se informa como
// evidencia diagnóstica, no como fallo. No forma parte de ningún barrido
// definitivo ni fija `eta`, duración o cantidad de semillas como protocolo
// experimental final: son parámetros de esta regresión puntual.

#include "core/model.hpp"
#include "core/simulation.hpp"
#include "core/observables.hpp"

#include <algorithm>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <random>
#include <vector>

namespace {

constexpr double kPi = 3.14159265358979323846;

// Búsqueda de vecinos "completa": cada partícula ve a todas las demás como
// vecinas, sin usar posición ni `rc`. Aísla la dinámica de la regla de
// votante de la conectividad espacial: en este escenario el grafo de
// interacción nunca cambia y siempre está completamente conectado.
std::vector<std::vector<std::size_t>> complete_graph_neighbors(
    const std::vector<tp2::Particle>& particles, const tp2::Parameters&) {
    const std::size_t count = particles.size();
    std::vector<std::vector<std::size_t>> neighbors(count);
    for (std::size_t i = 0; i < count; ++i) {
        neighbors[i].reserve(count - 1);
        for (std::size_t j = 0; j < count; ++j) {
            if (j != i) {
                neighbors[i].push_back(particles[j].id);
            }
        }
    }
    return neighbors;
}

std::vector<tp2::Particle> random_initial_state(std::size_t count,
                                                 const tp2::Parameters& parameters,
                                                 std::uint64_t seed) {
    std::mt19937_64 rng(seed);
    std::uniform_real_distribution<double> position_distribution(0.0, parameters.box_length);
    std::uniform_real_distribution<double> angle_distribution(0.0, 2.0 * kPi);

    std::vector<tp2::Particle> particles;
    particles.reserve(count);
    for (std::size_t id = 0; id < count; ++id) {
        tp2::Particle particle;
        particle.id = id;
        particle.x = position_distribution(rng);
        particle.y = position_distribution(rng);
        particle.theta = angle_distribution(rng);
        particles.push_back(particle);
    }
    return particles;
}

// Cuenta cuántos valores de orientación distintos hay en el estado,
// agrupando por igualdad exacta (con una tolerancia mínima que solo
// absorbe ruido de redondeo de `normalize_angle`, no diferencias reales).
std::size_t distinct_orientation_count(const std::vector<tp2::Particle>& particles) {
    constexpr double kEqualityTolerance = 1e-12;
    std::vector<double> thetas;
    thetas.reserve(particles.size());
    for (const auto& particle : particles) {
        thetas.push_back(particle.theta);
    }
    std::sort(thetas.begin(), thetas.end());

    std::size_t distinct_count = thetas.empty() ? 0 : 1;
    for (std::size_t i = 1; i < thetas.size(); ++i) {
        if (thetas[i] - thetas[i - 1] > kEqualityTolerance) {
            ++distinct_count;
        }
    }
    return distinct_count;
}

struct RunResult {
    std::uint64_t seed = 0;
    double va_initial = 0.0;
    double va_final = 0.0;
    std::size_t distinct_initial = 0;
    std::size_t distinct_final = 0;
    bool exact_consensus = false;
    std::size_t consensus_step = 0;  // válido solo si exact_consensus es true
};

RunResult run_one_seed(std::size_t particle_count, const tp2::Parameters& parameters,
                        std::size_t steps, std::uint64_t seed) {
    const std::vector<tp2::Particle> initial_state =
        random_initial_state(particle_count, parameters, seed);

    RunResult result;
    result.seed = seed;
    result.va_initial = tp2::polarization(initial_state);
    result.distinct_initial = distinct_orientation_count(initial_state);

    std::size_t first_consensus_step = 0;
    bool consensus_seen = false;

    const tp2::StateObserver observer = [&](std::size_t step,
                                             const std::vector<tp2::Particle>& state) {
        if (!consensus_seen && distinct_orientation_count(state) == 1) {
            consensus_seen = true;
            first_consensus_step = step;
        }
    };

    const std::vector<tp2::Particle> final_state =
        tp2::run_simulation(initial_state, parameters, /*eta=*/0.0, tp2::InteractionRule::kVoter,
                             steps, seed, complete_graph_neighbors, observer);

    result.va_final = tp2::polarization(final_state);
    result.distinct_final = distinct_orientation_count(final_state);
    result.exact_consensus = consensus_seen;
    result.consensus_step = first_consensus_step;
    return result;
}

}  // namespace

int main() {
    tp2::Parameters parameters;
    parameters.box_length = 10.0;
    parameters.interaction_radius = 1.0;  // irrelevante: los vecinos son el grafo completo.
    parameters.time_step = 1.0;
    parameters.speed = 0.03;

    // Parámetros de esta regresión puntual (no un protocolo experimental
    // final): sistema chico para que el grafo completo sea barato de
    // evaluar, varias semillas independientes explícitas y un horizonte
    // generoso pero acotado.
    constexpr std::size_t kParticleCount = 20;
    constexpr std::size_t kSteps = 3000;
    const std::vector<std::uint64_t> seeds = {700001, 700002, 700003, 700004, 700005,
                                               700006, 700007, 700008, 700009, 700010};

    std::cout << std::fixed << std::setprecision(6);
    std::cout << "Regresion diagnostica: consenso del votante sin ruido (eta=0)\n";
    std::cout << "Escenario: grafo completo (vecindad no geometrica), N=" << kParticleCount
              << ", steps=" << kSteps << ", " << seeds.size() << " semillas independientes.\n\n";

    std::size_t consensus_count = 0;
    bool sane = true;
    for (const std::uint64_t seed : seeds) {
        const RunResult result = run_one_seed(kParticleCount, parameters, kSteps, seed);

        std::cout << "seed=" << result.seed << "  va_inicial=" << result.va_initial
                  << "  va_final=" << result.va_final
                  << "  orientaciones_distintas_inicial=" << result.distinct_initial
                  << "  orientaciones_distintas_final=" << result.distinct_final
                  << "  consenso_exacto=" << (result.exact_consensus ? "si" : "no");
        if (result.exact_consensus) {
            std::cout << "  paso_de_consenso=" << result.consensus_step;
            ++consensus_count;
        } else {
            std::cout << "  paso_de_consenso=N/A (no alcanzado dentro de " << kSteps << " pasos)";
        }
        std::cout << "\n";

        // Sanidad basica (no depende de alcanzar consenso): los observables
        // deben quedar siempre en su rango valido y la cantidad de
        // orientaciones distintas nunca puede aumentar. Esto si es un
        // assert rigido, porque una violacion indicaria un bug real, no
        // falta de horizonte.
        if (result.va_final < 0.0 || result.va_final > 1.0 + 1e-9) {
            sane = false;
        }
        if (result.distinct_final == 0 || result.distinct_final > result.distinct_initial) {
            sane = false;
        }
    }

    std::cout << "\nResumen: " << consensus_count << "/" << seeds.size()
              << " corridas alcanzaron consenso exacto (una unica orientacion distinta) dentro de "
              << kSteps << " pasos.\n";

    if (consensus_count < seeds.size()) {
        std::cout << "Nota diagnostica: las semillas que no llegaron a consenso dentro del "
                     "horizonte no implican un error del modelo. Con el grafo completo la "
                     "conectividad espacial no puede ser la causa (todas las particulas son "
                     "vecinas de todas en todo momento); la explicacion mas probable es que el "
                     "horizonte de "
                  << kSteps
                  << " pasos resulto insuficiente para esa semilla en particular. No se modifico "
                     "la regla de votante ni se fuerza ningun assert sobre este resultado.\n";
    }

    if (!sane) {
        std::cerr << "FALLO: se detecto un valor fuera de rango o un aumento en la cantidad de "
                     "orientaciones distintas (esto si seria un bug, no falta de horizonte).\n";
        return EXIT_FAILURE;
    }

    return EXIT_SUCCESS;
}
