#include "core/model.hpp"
#include "core/neighbor_search.hpp"
#include "core/simulation.hpp"
#include "core/time_step.hpp"

#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <random>
#include <string>
#include <utility>
#include <vector>

namespace {

constexpr double kPi = 3.14159265358979323846;
constexpr double kTolerance = 1e-9;

void expect_true(bool condition, const std::string& case_name, const std::string& detail) {
    if (!condition) {
        std::cerr << "FALLO [" << case_name << "]: " << detail << "\n";
        std::abort();
    }
}

void expect_near(double actual, double expected, double tolerance, const std::string& case_name,
                  const std::string& detail) {
    if (std::abs(actual - expected) > tolerance) {
        std::cerr << "FALLO [" << case_name << "]: " << detail << " (esperado=" << expected
                   << ", obtenido=" << actual << ")\n";
        std::abort();
    }
}

double angular_distance(double a, double b) {
    double diff = std::fmod(std::abs(a - b), 2.0 * kPi);
    if (diff > kPi) {
        diff = 2.0 * kPi - diff;
    }
    return diff;
}

bool states_equal(const std::vector<tp2::Particle>& a, const std::vector<tp2::Particle>& b,
                   double tolerance) {
    if (a.size() != b.size()) {
        return false;
    }
    for (std::size_t i = 0; i < a.size(); ++i) {
        if (a[i].id != b[i].id) {
            return false;
        }
        if (std::abs(a[i].x - b[i].x) > tolerance || std::abs(a[i].y - b[i].y) > tolerance ||
            std::abs(a[i].theta - b[i].theta) > tolerance) {
            return false;
        }
    }
    return true;
}

tp2::Particle make_particle(std::size_t id, double x, double y, double theta) {
    tp2::Particle particle;
    particle.id = id;
    particle.x = x;
    particle.y = y;
    particle.theta = theta;
    return particle;
}

std::vector<tp2::Particle> random_particles(std::size_t count, const tp2::Parameters& parameters,
                                             std::uint64_t seed) {
    std::mt19937 rng(static_cast<std::mt19937::result_type>(seed));
    std::uniform_real_distribution<double> position_distribution(0.0, parameters.box_length);
    std::uniform_real_distribution<double> angle_distribution(0.0, 2.0 * kPi);

    std::vector<tp2::Particle> particles;
    particles.reserve(count);
    for (std::size_t id = 0; id < count; ++id) {
        particles.push_back(make_particle(id, position_distribution(rng),
                                           position_distribution(rng), angle_distribution(rng)));
    }
    return particles;
}

// 1. steps=0: devuelve el estado inicial, no realiza avances, el observador
// solo recibe step=0.
void test_zero_steps_returns_initial_state() {
    tp2::Parameters parameters;
    const std::vector<tp2::Particle> initial = {make_particle(0, 1.0, 2.0, 0.5),
                                                 make_particle(1, 3.0, 4.0, 1.5)};

    std::vector<std::pair<std::size_t, std::vector<tp2::Particle>>> observed;
    const auto observer = [&observed](std::size_t step, const std::vector<tp2::Particle>& state) {
        observed.emplace_back(step, state);
    };

    const auto final_state =
        tp2::run_simulation(initial, parameters, 0.3, tp2::InteractionRule::kVicsek, 0, 777,
                             tp2::brute_force_neighbors, observer);

    expect_true(states_equal(final_state, initial, kTolerance), "zero_steps_returns_initial_state",
                "con steps=0 el estado devuelto debe ser exactamente el inicial");
    expect_true(observed.size() == 1, "zero_steps_returns_initial_state",
                "el observador debe recibir una única llamada con steps=0");
    expect_true(observed[0].first == 0, "zero_steps_returns_initial_state",
                "la única llamada al observador debe ser con step=0");
    expect_true(states_equal(observed[0].second, initial, kTolerance),
                "zero_steps_returns_initial_state",
                "el estado observado en step=0 debe ser el estado inicial");
}

// 2. steps=1 coincide exactamente con llamar una vez a advance_time_step,
// para Vicsek y para votante.
void test_one_step_matches_advance_time_step() {
    tp2::Parameters parameters;
    const std::vector<tp2::Particle> initial = {make_particle(0, 1.0, 1.0, 0.2),
                                                 make_particle(1, 1.3, 1.1, 2.0),
                                                 make_particle(2, 5.0, 5.0, 4.0)};
    const std::uint64_t base_seed = 4242;

    for (const tp2::InteractionRule rule :
         {tp2::InteractionRule::kVicsek, tp2::InteractionRule::kVoter}) {
        const auto simulated = tp2::run_simulation(initial, parameters, 0.4, rule, 1, base_seed,
                                                     tp2::brute_force_neighbors);

        const std::uint64_t step_seed = tp2::derive_step_seed(base_seed, 1);
        const auto direct = tp2::advance_time_step(initial, parameters, 0.4, rule, step_seed,
                                                     tp2::brute_force_neighbors);

        expect_true(states_equal(simulated, direct, 0.0), "one_step_matches_advance_time_step",
                    "steps=1 debe coincidir exactamente con una llamada directa a "
                    "advance_time_step usando derive_step_seed(base_seed, 1)");
    }
}

// 3. Varios pasos: se conserva tamaño e IDs, posiciones en [0,L), ángulos
// normalizados.
void test_multiple_steps_preserve_invariants() {
    tp2::Parameters parameters;
    const auto initial = random_particles(30, parameters, 909);

    const auto final_state = tp2::run_simulation(
        initial, parameters, 0.5, tp2::InteractionRule::kVicsek, 8, 123, tp2::brute_force_neighbors);

    expect_true(final_state.size() == initial.size(), "multiple_steps_preserve_invariants",
                "el tamaño del estado debe conservarse");
    for (std::size_t i = 0; i < initial.size(); ++i) {
        expect_true(final_state[i].id == initial[i].id, "multiple_steps_preserve_invariants",
                    "los IDs deben conservarse en la misma posición");
        expect_true(final_state[i].x >= 0.0 && final_state[i].x < parameters.box_length,
                    "multiple_steps_preserve_invariants", "x debe quedar en [0,L)");
        expect_true(final_state[i].y >= 0.0 && final_state[i].y < parameters.box_length,
                    "multiple_steps_preserve_invariants", "y debe quedar en [0,L)");
        expect_true(final_state[i].theta >= 0.0 && final_state[i].theta < 2.0 * kPi,
                    "multiple_steps_preserve_invariants", "theta debe quedar normalizado");
    }
}

// 4. Observador: recibe todos los pasos esperados, en orden, con el estado
// correcto en cada uno; el estado inicial no se modifica.
void test_observer_receives_ordered_steps() {
    tp2::Parameters parameters;
    const std::vector<tp2::Particle> initial_original = {make_particle(0, 2.0, 2.0, 0.1),
                                                          make_particle(1, 2.3, 2.1, 1.0),
                                                          make_particle(2, 8.0, 8.0, 3.0)};
    const std::vector<tp2::Particle> initial = initial_original;
    constexpr std::size_t steps = 5;

    std::vector<std::pair<std::size_t, std::vector<tp2::Particle>>> observed;
    const auto observer = [&observed](std::size_t step, const std::vector<tp2::Particle>& state) {
        observed.emplace_back(step, state);
    };

    const auto final_state =
        tp2::run_simulation(initial, parameters, 0.3, tp2::InteractionRule::kVoter, steps, 55,
                             tp2::brute_force_neighbors, observer);

    expect_true(observed.size() == steps + 1, "observer_receives_ordered_steps",
                "el observador debe recibir steps+1 llamadas (incluyendo step=0)");
    for (std::size_t step = 0; step <= steps; ++step) {
        expect_true(observed[step].first == step, "observer_receives_ordered_steps",
                    "las llamadas deben llegar en orden creciente de step");
    }

    // Reconstruir la corrida paso a paso con advance_time_step y comparar
    // contra lo observado, para verificar que el estado en step=t coincide
    // con el estado realmente producido después de t avances.
    std::vector<tp2::Particle> replayed = initial_original;
    expect_true(states_equal(observed[0].second, replayed, kTolerance),
                "observer_receives_ordered_steps", "step=0 observado debe ser el estado inicial");
    for (std::size_t step = 1; step <= steps; ++step) {
        const std::uint64_t step_seed = tp2::derive_step_seed(55, step);
        replayed = tp2::advance_time_step(replayed, parameters, 0.3, tp2::InteractionRule::kVoter,
                                           step_seed, tp2::brute_force_neighbors);
        expect_true(states_equal(observed[step].second, replayed, kTolerance),
                    "observer_receives_ordered_steps",
                    "el estado observado en step=" + std::to_string(step) +
                        " debe coincidir con el producido tras esa cantidad de avances");
    }

    expect_true(states_equal(replayed, final_state, kTolerance), "observer_receives_ordered_steps",
                "el estado devuelto debe coincidir con el último estado observado");
    expect_true(states_equal(initial, initial_original, 0.0), "observer_receives_ordered_steps",
                "run_simulation no debe modificar el vector de estado inicial de entrada");
}

// 5. Reproducibilidad: misma configuración y base_seed dan corridas
// idénticas; una semilla distinta puede dar una corrida distinta con
// eta>0.
void test_reproducibility_and_seed_sensitivity() {
    tp2::Parameters parameters;
    const auto initial = random_particles(20, parameters, 314);

    const auto run_a = tp2::run_simulation(initial, parameters, 0.5, tp2::InteractionRule::kVicsek,
                                            6, 2024, tp2::brute_force_neighbors);
    const auto run_b = tp2::run_simulation(initial, parameters, 0.5, tp2::InteractionRule::kVicsek,
                                            6, 2024, tp2::brute_force_neighbors);
    expect_true(states_equal(run_a, run_b, 0.0), "reproducibility_and_seed_sensitivity",
                "misma configuración y base_seed deben dar corridas idénticas");

    bool found_difference = false;
    for (std::uint64_t base_seed = 1; base_seed < 40; ++base_seed) {
        const auto run_other = tp2::run_simulation(
            initial, parameters, 0.5, tp2::InteractionRule::kVicsek, 6, base_seed,
            tp2::brute_force_neighbors);
        if (!states_equal(run_other, run_a, 1e-12)) {
            found_difference = true;
            break;
        }
    }
    expect_true(found_difference, "reproducibility_and_seed_sensitivity",
                "alguna base_seed distinta debe producir una corrida distinta con eta>0");
}

// 6. Semillas por paso: dos pasos consecutivos no usan exactamente el mismo
// sorteo (con ruido no nulo); no se asume una secuencia específica, solo que
// no se repite artificialmente.
void test_step_seeds_differ_between_consecutive_steps() {
    tp2::Parameters parameters;
    // Partícula aislada con votante: en cada paso conserva su propia
    // orientación como base y le suma únicamente ruido, así que la
    // diferencia entre pasos consecutivos aísla directamente el sorteo de
    // ruido de ese paso.
    const std::vector<tp2::Particle> initial = {make_particle(0, 5.0, 5.0, 1.0)};
    constexpr double eta = 0.6;

    std::vector<double> theta_by_step;
    const auto observer = [&theta_by_step](std::size_t, const std::vector<tp2::Particle>& state) {
        theta_by_step.push_back(state[0].theta);
    };

    tp2::run_simulation(initial, parameters, eta, tp2::InteractionRule::kVoter, 2, 9001,
                         tp2::brute_force_neighbors, observer);

    expect_true(theta_by_step.size() == 3, "step_seeds_differ_between_consecutive_steps",
                "se esperan 3 estados observados (step 0,1,2)");

    const double noise_step_1 = angular_distance(theta_by_step[1], theta_by_step[0]);
    const double noise_step_2 = angular_distance(theta_by_step[2], theta_by_step[1]);

    expect_true(std::abs(noise_step_1 - noise_step_2) > 1e-6,
                "step_seeds_differ_between_consecutive_steps",
                "el ruido aplicado en el paso 1 y en el paso 2 no debería coincidir "
                "exactamente si las semillas de paso son distintas");
}

// 7. Invariancia al orden: permutar las partículas iniciales, ejecutar con
// la misma configuración y base_seed, comparar por ID después de varios
// pasos. Se prueba con Vicsek y con votante.
void test_order_invariance_across_steps() {
    tp2::Parameters parameters;
    const std::vector<tp2::Particle> original = {
        make_particle(0, 1.0, 1.0, 0.1), make_particle(1, 1.4, 1.2, 1.0),
        make_particle(2, 1.1, 1.6, 2.0), make_particle(3, 5.0, 5.0, 3.0)};
    const std::vector<tp2::Particle> permuted = {original[3], original[1], original[0],
                                                  original[2]};

    for (const tp2::InteractionRule rule :
         {tp2::InteractionRule::kVicsek, tp2::InteractionRule::kVoter}) {
        const auto result_original = tp2::run_simulation(original, parameters, 0.4, rule, 5, 6060,
                                                           tp2::brute_force_neighbors);
        const auto result_permuted = tp2::run_simulation(permuted, parameters, 0.4, rule, 5, 6060,
                                                           tp2::brute_force_neighbors);

        std::vector<std::size_t> index_of_id(original.size());
        for (std::size_t i = 0; i < result_original.size(); ++i) {
            index_of_id[result_original[i].id] = i;
        }

        for (const auto& particle : result_permuted) {
            const auto& counterpart = result_original[index_of_id[particle.id]];
            expect_near(particle.x, counterpart.x, kTolerance, "order_invariance_across_steps",
                        "x debe coincidir por id sin importar el orden de almacenamiento inicial");
            expect_near(particle.y, counterpart.y, kTolerance, "order_invariance_across_steps",
                        "y debe coincidir por id sin importar el orden de almacenamiento inicial");
            expect_near(particle.theta, counterpart.theta, kTolerance,
                        "order_invariance_across_steps",
                        "theta debe coincidir por id sin importar el orden de almacenamiento "
                        "inicial");
        }
    }
}

// 8. Búsqueda de vecinos: la misma corrida con fuerza bruta y con CIM debe
// dar el mismo estado final y los mismos estados observados.
void test_consistent_between_bruteforce_and_cim() {
    tp2::Parameters parameters;
    const auto initial = random_particles(35, parameters, 4242);

    std::vector<std::vector<tp2::Particle>> observed_bruteforce;
    const auto observer_bruteforce = [&observed_bruteforce](std::size_t,
                                                              const std::vector<tp2::Particle>& state) {
        observed_bruteforce.push_back(state);
    };
    std::vector<std::vector<tp2::Particle>> observed_cim;
    const auto observer_cim = [&observed_cim](std::size_t, const std::vector<tp2::Particle>& state) {
        observed_cim.push_back(state);
    };

    const auto final_bruteforce =
        tp2::run_simulation(initial, parameters, 0.4, tp2::InteractionRule::kVicsek, 6, 77,
                             tp2::brute_force_neighbors, observer_bruteforce);
    const auto final_cim =
        tp2::run_simulation(initial, parameters, 0.4, tp2::InteractionRule::kVicsek, 6, 77,
                             tp2::cell_index_neighbors, observer_cim);

    expect_true(states_equal(final_bruteforce, final_cim, 1e-9),
                "consistent_between_bruteforce_and_cim",
                "el estado final debe coincidir usando fuerza bruta o CIM");
    expect_true(observed_bruteforce.size() == observed_cim.size(),
                "consistent_between_bruteforce_and_cim",
                "debe observarse la misma cantidad de pasos con ambos métodos");
    for (std::size_t step = 0; step < observed_bruteforce.size(); ++step) {
        expect_true(states_equal(observed_bruteforce[step], observed_cim[step], 1e-9),
                    "consistent_between_bruteforce_and_cim",
                    "el estado observado en step=" + std::to_string(step) +
                        " debe coincidir usando fuerza bruta o CIM");
    }
}

// 9. Estado aislado: con eta=0 conserva la orientación esperada y se mueve
// según la orientación vieja en cada paso.
void test_isolated_particle_moves_with_conserved_theta() {
    tp2::Parameters parameters;
    const double theta = 0.0;
    const std::vector<tp2::Particle> initial = {make_particle(0, 5.0, 5.0, theta)};
    constexpr std::size_t steps = 4;

    std::vector<std::vector<tp2::Particle>> observed;
    const auto observer = [&observed](std::size_t, const std::vector<tp2::Particle>& state) {
        observed.push_back(state);
    };

    tp2::run_simulation(initial, parameters, 0.0, tp2::InteractionRule::kVoter, steps, 5555,
                         tp2::brute_force_neighbors, observer);

    expect_true(observed.size() == steps + 1, "isolated_particle_moves_with_conserved_theta",
                "deben observarse steps+1 estados");
    for (std::size_t step = 0; step <= steps; ++step) {
        expect_near(observed[step][0].theta, theta, kTolerance,
                    "isolated_particle_moves_with_conserved_theta",
                    "una partícula aislada con eta=0 debe conservar su orientación en cada paso");
        const double expected_x =
            5.0 + parameters.speed * std::cos(theta) * parameters.time_step *
                      static_cast<double>(step);
        expect_near(observed[step][0].x, expected_x, 1e-9,
                    "isolated_particle_moves_with_conserved_theta",
                    "la posición x en el step=" + std::to_string(step) +
                        " debe seguir x0 + v*cos(theta)*dt*step");
        expect_near(observed[step][0].y, 5.0, 1e-9, "isolated_particle_moves_with_conserved_theta",
                    "con theta=0 la posición y no debe cambiar");
    }
}

// 10. Cadena de pasos: el segundo paso usa las posiciones resultantes del
// primero, no las posiciones iniciales.
void test_second_step_uses_positions_from_first_step() {
    tp2::Parameters parameters;
    // Dos partículas separadas 1.02 en x (fuera de rc=1) que se acercan
    // moviéndose una hacia la otra; tras un paso quedan separadas por
    // 1.02 - 2*0.03 = 0.96 (dentro de rc), así que recién en el segundo
    // paso deberían verse como vecinas.
    const std::vector<tp2::Particle> initial = {make_particle(0, 4.0, 5.0, 0.0),
                                                 make_particle(1, 5.02, 5.0, kPi)};

    std::vector<std::vector<tp2::Particle>> observed;
    const auto observer = [&observed](std::size_t, const std::vector<tp2::Particle>& state) {
        observed.push_back(state);
    };

    tp2::run_simulation(initial, parameters, 0.0, tp2::InteractionRule::kVoter, 2, 31,
                         tp2::brute_force_neighbors, observer);

    expect_true(observed.size() == 3, "second_step_uses_positions_from_first_step",
                "deben observarse 3 estados (step 0,1,2)");

    // Tras el primer paso todavía no eran vecinas (tomó la geometría
    // inicial), así que cada una conservó su propia orientación (votante
    // aislado, eta=0).
    expect_near(observed[1][0].theta, 0.0, kTolerance, "second_step_uses_positions_from_first_step",
                "en el primer paso las partículas todavía no son vecinas: conservan su theta");
    expect_near(observed[1][1].theta, kPi, kTolerance,
                "second_step_uses_positions_from_first_step",
                "en el primer paso las partículas todavía no son vecinas: conservan su theta");

    const double gap_after_first_step = observed[1][1].x - observed[1][0].x;
    expect_true(gap_after_first_step < parameters.interaction_radius,
                "second_step_uses_positions_from_first_step",
                "tras el primer paso la separación debe quedar por debajo de rc, habilitando "
                "vecindad para el segundo paso");

    // En el segundo paso, calculado con las posiciones ya actualizadas del
    // primero, ahora sí son vecinas: con votante y eta=0, cada una termina
    // con la orientación vieja de la otra (única vecina posible).
    const bool particle0_copied_neighbor =
        angular_distance(observed[2][0].theta, kPi) < kTolerance;
    const bool particle1_copied_neighbor = angular_distance(observed[2][1].theta, 0.0) < kTolerance;
    expect_true(particle0_copied_neighbor, "second_step_uses_positions_from_first_step",
                "en el segundo paso, usando las posiciones actualizadas, la partícula 0 debe ver "
                "a la 1 como vecina y copiar su orientación");
    expect_true(particle1_copied_neighbor, "second_step_uses_positions_from_first_step",
                "en el segundo paso, usando las posiciones actualizadas, la partícula 1 debe ver "
                "a la 0 como vecina y copiar su orientación");
}

}  // namespace

int main() {
    test_zero_steps_returns_initial_state();
    test_one_step_matches_advance_time_step();
    test_multiple_steps_preserve_invariants();
    test_observer_receives_ordered_steps();
    test_reproducibility_and_seed_sensitivity();
    test_step_seeds_differ_between_consecutive_steps();
    test_order_invariance_across_steps();
    test_consistent_between_bruteforce_and_cim();
    test_isolated_particle_moves_with_conserved_theta();
    test_second_step_uses_positions_from_first_step();

    std::cout << "test_simulation: todos los casos pasaron\n";
    return 0;
}
