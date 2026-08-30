// Valida el inicializador productivo del estado (`src/core/initialization.hpp`):
// IDs estables, cantidad correcta de partículas, posiciones y orientaciones
// en rango, reproducibilidad con la misma semilla, variación con semillas
// distintas, las tres densidades obligatorias, no modificación de
// `Parameters`, caso `N=0`, compatibilidad directa con `run_simulation` y
// ausencia de cualquier fuente de aleatoriedad no determinista (reloj).
//
// Alcance: ver plan_desarrollo_tp2/03_validaciones.md, sección "Validación
// del inicializador". No modifica `time_step.hpp`, `rules.hpp` ni
// `neighbor_search.hpp`.

#include "core/initialization.hpp"
#include "core/model.hpp"
#include "core/simulation.hpp"
#include "core/neighbor_search.hpp"

#include <cmath>
#include <cstdlib>
#include <iostream>
#include <set>
#include <string>
#include <vector>

namespace {

constexpr double kPi = 3.14159265358979323846;

void expect_true(bool condition, const std::string& case_name, const std::string& detail) {
    if (!condition) {
        std::cerr << "FALLO [" << case_name << "]: " << detail << "\n";
        std::abort();
    }
}

}  // namespace

int main() {
    tp2::Parameters parameters;
    parameters.box_length = 10.0;
    parameters.interaction_radius = 1.0;
    parameters.time_step = 1.0;
    parameters.speed = 0.03;

    // 1-3: IDs consecutivos y únicos, cantidad correcta, posiciones en [0,L).
    {
        constexpr std::size_t kCount = 50;
        const std::vector<tp2::Particle> particles =
            tp2::initialize_particles(kCount, parameters, /*seed=*/1);

        expect_true(particles.size() == kCount, "particle_count",
                    "initialize_particles debe devolver exactamente `count` particulas");

        std::set<std::size_t> ids;
        for (std::size_t i = 0; i < particles.size(); ++i) {
            expect_true(particles[i].id == i, "consecutive_ids",
                        "el id debe coincidir con la posicion, 0..N-1");
            ids.insert(particles[i].id);
        }
        expect_true(ids.size() == kCount, "unique_ids", "los ids no deben repetirse");

        for (const auto& particle : particles) {
            expect_true(particle.x >= 0.0 && particle.x < parameters.box_length, "position_x_range",
                        "x debe quedar en [0,L)");
            expect_true(particle.y >= 0.0 && particle.y < parameters.box_length, "position_y_range",
                        "y debe quedar en [0,L)");
        }
    }

    // 4: orientaciones en [0, 2*pi).
    {
        const std::vector<tp2::Particle> particles =
            tp2::initialize_particles(200, parameters, /*seed=*/2);
        for (const auto& particle : particles) {
            expect_true(particle.theta >= 0.0 && particle.theta < 2.0 * kPi, "angle_range",
                        "theta debe quedar en [0,2*pi)");
        }
    }

    // 5: misma semilla produce estados idénticos.
    {
        const std::vector<tp2::Particle> first =
            tp2::initialize_particles(80, parameters, /*seed=*/42);
        const std::vector<tp2::Particle> second =
            tp2::initialize_particles(80, parameters, /*seed=*/42);

        expect_true(first.size() == second.size(), "same_seed_same_size", "mismo tamano esperado");
        for (std::size_t i = 0; i < first.size(); ++i) {
            expect_true(first[i].id == second[i].id && first[i].x == second[i].x &&
                            first[i].y == second[i].y && first[i].theta == second[i].theta,
                        "same_seed_identical_state",
                        "la misma semilla debe reproducir exactamente el mismo estado");
        }
    }

    // 6: semillas distintas pueden producir estados distintos.
    {
        const std::vector<tp2::Particle> base =
            tp2::initialize_particles(80, parameters, /*seed=*/1000);

        bool any_different = false;
        for (std::uint64_t seed = 1001; seed < 1001 + 20; ++seed) {
            const std::vector<tp2::Particle> other =
                tp2::initialize_particles(80, parameters, seed);
            for (std::size_t i = 0; i < base.size(); ++i) {
                if (other[i].x != base[i].x || other[i].y != base[i].y ||
                    other[i].theta != base[i].theta) {
                    any_different = true;
                    break;
                }
            }
            if (any_different) {
                break;
            }
        }
        expect_true(any_different, "different_seeds_can_differ",
                    "al menos una semilla distinta deberia dar un estado distinto");
    }

    // 7: las tres densidades obligatorias producen N=200,400,800.
    {
        struct DensityCase {
            double rho;
            std::size_t expected_count;
        };
        const std::vector<DensityCase> cases = {{2.0, 200}, {4.0, 400}, {8.0, 800}};
        for (const auto& density_case : cases) {
            const std::vector<tp2::Particle> particles =
                tp2::initialize_particles_from_density(density_case.rho, parameters, /*seed=*/7);
            expect_true(particles.size() == density_case.expected_count, "density_case_count",
                        "rho=" + std::to_string(density_case.rho) +
                            " debe producir N=" + std::to_string(density_case.expected_count));
        }
    }

    // 8: la inicialización no modifica los parámetros.
    {
        tp2::Parameters parameters_copy = parameters;
        (void)tp2::initialize_particles(30, parameters, /*seed=*/9);
        (void)tp2::initialize_particles_from_density(4.0, parameters, /*seed=*/9);
        expect_true(parameters.box_length == parameters_copy.box_length &&
                        parameters.interaction_radius == parameters_copy.interaction_radius &&
                        parameters.time_step == parameters_copy.time_step &&
                        parameters.speed == parameters_copy.speed,
                    "parameters_untouched", "Parameters no debe modificarse por la inicializacion");
    }

    // 9: el inicializador funciona con N=0.
    {
        const std::vector<tp2::Particle> particles =
            tp2::initialize_particles(0, parameters, /*seed=*/11);
        expect_true(particles.empty(), "zero_particles", "N=0 debe devolver un vector vacio");

        const std::vector<tp2::Particle> from_density =
            tp2::initialize_particles_from_density(0.0, parameters, /*seed=*/11);
        expect_true(from_density.empty(), "zero_density",
                    "rho=0 debe producir N=0 y devolver un vector vacio");
    }

    // 10: el estado generado puede usarse directamente con run_simulation.
    {
        const std::vector<tp2::Particle> initial_state =
            tp2::initialize_particles(30, parameters, /*seed=*/13);

        const std::vector<tp2::Particle> final_state = tp2::run_simulation(
            initial_state, parameters, /*eta=*/0.3, tp2::InteractionRule::kVicsek, /*steps=*/5,
            /*base_seed=*/13, tp2::cell_index_neighbors);

        expect_true(final_state.size() == initial_state.size(), "run_simulation_integration",
                    "run_simulation debe aceptar el estado del inicializador y devolver el mismo "
                    "tamano");
        for (const auto& particle : final_state) {
            expect_true(particle.x >= 0.0 && particle.x < parameters.box_length &&
                            particle.y >= 0.0 && particle.y < parameters.box_length,
                        "run_simulation_integration_bounds",
                        "el estado final debe seguir en [0,L) tras avanzar con el estado inicial "
                        "del inicializador");
        }
    }

    // 11: el resultado no depende de ninguna semilla del reloj: dos llamadas
    // consecutivas con la misma semilla explicita, separadas en tiempo real
    // de ejecucion, siguen dando exactamente el mismo resultado (si el
    // inicializador usara el reloj como parte de la semilla, esto fallaria).
    {
        const std::vector<tp2::Particle> first =
            tp2::initialize_particles(40, parameters, /*seed=*/2024);
        // Trabajo intermedio no trivial para separar en el tiempo ambas llamadas.
        volatile double busy = 0.0;
        for (int i = 0; i < 1000000; ++i) {
            busy += static_cast<double>(i) * 1e-9;
        }
        const std::vector<tp2::Particle> second =
            tp2::initialize_particles(40, parameters, /*seed=*/2024);

        for (std::size_t i = 0; i < first.size(); ++i) {
            expect_true(first[i].x == second[i].x && first[i].y == second[i].y &&
                            first[i].theta == second[i].theta,
                        "no_clock_seeding",
                        "el resultado no debe depender del reloj: misma semilla explicita debe "
                        "dar el mismo resultado sin importar cuando se ejecuta");
        }
    }

    std::cout << "OK: inicializador productivo valida IDs, rangos, reproducibilidad, densidades, "
                 "N=0, integracion con run_simulation y ausencia de siembra por reloj.\n";

    return 0;
}
