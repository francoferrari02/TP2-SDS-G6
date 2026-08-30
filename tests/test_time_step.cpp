#include "core/model.hpp"
#include "core/neighbor_search.hpp"
#include "core/time_step.hpp"

#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <iostream>
#include <random>
#include <string>
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

tp2::Particle make_particle(std::size_t id, double x, double y, double theta) {
    tp2::Particle particle;
    particle.id = id;
    particle.x = x;
    particle.y = y;
    particle.theta = theta;
    return particle;
}

tp2::Parameters make_parameters(double box_length, double radius, double dt, double speed) {
    tp2::Parameters parameters;
    parameters.box_length = box_length;
    parameters.interaction_radius = radius;
    parameters.time_step = dt;
    parameters.speed = speed;
    return parameters;
}

// 1. Caso mínimo de 03_validaciones.md, sección 7: una partícula en (0,0)
// con theta_old=0 cuya interacción produce theta_new=pi/2. Debe moverse con
// la orientación VIEJA (0.03, 0), no con la nueva (que daría (0, 0.03)).
void test_backward_motion_uses_old_theta_not_new() {
    // Votante con eta=0: la partícula 0 tiene un único vecino externo con
    // theta=pi/2, así que su theta_new queda forzado a pi/2 exactamente.
    const std::vector<tp2::Particle> particles = {make_particle(0, 0.0, 0.0, 0.0),
                                                   make_particle(1, 0.05, 0.0, kPi / 2.0)};
    const tp2::Parameters parameters = make_parameters(10.0, 1.0, 1.0, 0.03);
    const std::uint64_t seed = 1;

    const auto next_state = tp2::advance_time_step(particles, parameters, 0.0,
                                                     tp2::InteractionRule::kVoter, seed,
                                                     tp2::brute_force_neighbors);

    expect_near(next_state[0].theta, kPi / 2.0, kTolerance, "backward_motion_uses_old_theta_not_new",
                "el votante sin ruido con un único vecino a pi/2 debe copiar exactamente pi/2");
    expect_near(next_state[0].x, 0.03, kTolerance, "backward_motion_uses_old_theta_not_new",
                "x_new debe calcularse con theta_old=0 (cos(0)=1), no con theta_new=pi/2");
    expect_near(next_state[0].y, 0.0, kTolerance, "backward_motion_uses_old_theta_not_new",
                "y_new debe calcularse con theta_old=0 (sin(0)=0); (0,0.03) indicaría el bug de "
                "usar theta_new");
}

// 2. Ecuación de movimiento exacta para una partícula aislada (sin vecinos,
// eta=0): x_new = x + v*cos(theta)*dt, y_new = y + v*sin(theta)*dt.
void test_equation_of_motion_exact_isolated_particle() {
    const double theta = kPi / 4.0;
    const std::vector<tp2::Particle> particles = {make_particle(0, 5.0, 5.0, theta)};
    const tp2::Parameters parameters = make_parameters(10.0, 1.0, 1.0, 0.03);
    const std::uint64_t seed = 2;

    const auto next_state = tp2::advance_time_step(particles, parameters, 0.0,
                                                     tp2::InteractionRule::kVicsek, seed,
                                                     tp2::brute_force_neighbors);

    const double expected_x = 5.0 + 0.03 * std::cos(theta) * 1.0;
    const double expected_y = 5.0 + 0.03 * std::sin(theta) * 1.0;
    expect_near(next_state[0].x, expected_x, kTolerance, "equation_of_motion_exact_isolated_particle",
                "x_new debe coincidir con x + v*cos(theta)*dt");
    expect_near(next_state[0].y, expected_y, kTolerance, "equation_of_motion_exact_isolated_particle",
                "y_new debe coincidir con y + v*sin(theta)*dt");
    expect_near(next_state[0].theta, tp2::normalize_angle(theta), kTolerance,
                "equation_of_motion_exact_isolated_particle",
                "una partícula aislada con eta=0 conserva su orientación (Vicsek incluye a sí misma)");
}

// 3. El borde periódico se aplica a las posiciones nuevas: una partícula
// que se mueve más allá de L debe reaparecer del otro lado.
void test_periodic_wrap_applied_to_new_positions() {
    const std::vector<tp2::Particle> particles = {make_particle(0, 9.99, 5.0, 0.0)};
    const tp2::Parameters parameters = make_parameters(10.0, 1.0, 1.0, 0.03);
    const std::uint64_t seed = 3;

    const auto next_state = tp2::advance_time_step(particles, parameters, 0.0,
                                                     tp2::InteractionRule::kVicsek, seed,
                                                     tp2::brute_force_neighbors);

    // x = 9.99 + 0.03 = 10.02 -> repliega a 0.02.
    expect_near(next_state[0].x, 0.02, 1e-9, "periodic_wrap_applied_to_new_positions",
                "una posición que cruza x=L debe replegarse a [0,L)");
    expect_true(next_state[0].x >= 0.0 && next_state[0].x < parameters.box_length,
                "periodic_wrap_applied_to_new_positions", "x_new debe quedar en [0,L)");
}

// 4. La lista de vecinos se construye con x(t) (posiciones viejas), no con
// x(t+1). Se arma un caso donde, si se usara la posición nueva, el
// resultado de vecindad cambiaría.
void test_neighbors_built_from_old_positions() {
    // Dos partículas separadas por 1.02 (justo fuera de rc=1) en x, con
    // theta=0 (se mueven hacia +x con v=0.03). Si el motor recalculara
    // vecinos con las posiciones nuevas dentro del mismo paso, la partícula
    // 0 (que avanza hacia la partícula 1) terminaría a distancia 0.99 y
    // votante la vería como vecina; pero según la especificación, la
    // vecindad debe salir de x(t), donde la distancia es 1.02 (no vecinos).
    const std::vector<tp2::Particle> particles = {make_particle(0, 0.0, 0.0, 0.0),
                                                   make_particle(1, 1.02, 0.0, kPi)};
    const tp2::Parameters parameters = make_parameters(10.0, 1.0, 1.0, 0.03);
    const std::uint64_t seed = 4;

    const auto next_state = tp2::advance_time_step(particles, parameters, 0.0,
                                                     tp2::InteractionRule::kVoter, seed,
                                                     tp2::brute_force_neighbors);

    // Ninguna tiene vecinos externos según x(t) (distancia 1.02 > rc=1), así
    // que el votante debe conservar la orientación vieja de cada una.
    expect_near(next_state[0].theta, tp2::normalize_angle(0.0), kTolerance,
                "neighbors_built_from_old_positions",
                "sin vecinos según x(t), la partícula 0 debe conservar su orientación");
    expect_near(next_state[1].theta, tp2::normalize_angle(kPi), kTolerance,
                "neighbors_built_from_old_positions",
                "sin vecinos según x(t), la partícula 1 debe conservar su orientación");
}

// 5. Sincronía / invarianza al orden de almacenamiento: permutar el orden
// de las partículas y repetir el mismo paso con la misma semilla; al
// identificar por `id`, el resultado debe coincidir.
void test_order_independence_with_same_seed() {
    const std::vector<tp2::Particle> original = {
        make_particle(0, 1.0, 1.0, 0.1), make_particle(1, 1.3, 1.0, 0.5),
        make_particle(2, 1.0, 1.3, 1.2), make_particle(3, 5.0, 5.0, 2.0)};
    std::vector<tp2::Particle> permuted = {original[3], original[1], original[0], original[2]};
    const tp2::Parameters parameters = make_parameters(10.0, 1.0, 1.0, 0.03);

    const std::uint64_t seed = 2024;
    const auto result_a = tp2::advance_time_step(original, parameters, 0.4,
                                                   tp2::InteractionRule::kVicsek, seed,
                                                   tp2::brute_force_neighbors);
    const auto result_b = tp2::advance_time_step(permuted, parameters, 0.4,
                                                   tp2::InteractionRule::kVicsek, seed,
                                                   tp2::brute_force_neighbors);

    for (const auto& particle_a : result_a) {
        bool found = false;
        for (const auto& particle_b : result_b) {
            if (particle_b.id == particle_a.id) {
                found = true;
                expect_near(particle_b.x, particle_a.x, 1e-9, "order_independence_with_same_seed",
                            "misma id, distinto orden de almacenamiento: x debe coincidir");
                expect_near(particle_b.y, particle_a.y, 1e-9, "order_independence_with_same_seed",
                            "misma id, distinto orden de almacenamiento: y debe coincidir");
                expect_near(particle_b.theta, particle_a.theta, 1e-9,
                            "order_independence_with_same_seed",
                            "misma id, distinto orden de almacenamiento: theta debe coincidir");
            }
        }
        expect_true(found, "order_independence_with_same_seed",
                    "cada id del resultado original debe aparecer en el resultado permutado");
    }
}

// 6. `advance_time_step` no debe modificar el vector de entrada.
void test_input_state_not_mutated() {
    const std::vector<tp2::Particle> original = {make_particle(0, 1.0, 1.0, 0.2),
                                                  make_particle(1, 1.5, 1.0, 1.1),
                                                  make_particle(2, 8.0, 8.0, 3.0)};
    std::vector<tp2::Particle> particles = original;
    const tp2::Parameters parameters = make_parameters(10.0, 1.0, 1.0, 0.03);
    const std::uint64_t seed = 6;

    const auto next_state = tp2::advance_time_step(particles, parameters, 0.5,
                                                     tp2::InteractionRule::kVoter, seed,
                                                     tp2::brute_force_neighbors);

    for (std::size_t i = 0; i < particles.size(); ++i) {
        expect_near(particles[i].x, original[i].x, 0.0, "input_state_not_mutated",
                    "x vieja no debe cambiar tras llamar a advance_time_step");
        expect_near(particles[i].y, original[i].y, 0.0, "input_state_not_mutated",
                    "y vieja no debe cambiar tras llamar a advance_time_step");
        expect_near(particles[i].theta, original[i].theta, 0.0, "input_state_not_mutated",
                    "theta vieja no debe cambiar tras llamar a advance_time_step");
    }
    (void)next_state;
}

// 7. Reproducibilidad: misma semilla produce exactamente el mismo estado
// nuevo.
void test_reproducible_with_same_seed() {
    const std::vector<tp2::Particle> particles = {make_particle(0, 2.0, 2.0, 0.3),
                                                   make_particle(1, 2.4, 2.0, 1.0),
                                                   make_particle(2, 2.0, 2.4, 2.2)};
    const tp2::Parameters parameters = make_parameters(10.0, 1.0, 1.0, 0.03);

    const std::uint64_t seed = 555;
    const auto result_a = tp2::advance_time_step(particles, parameters, 0.6,
                                                   tp2::InteractionRule::kVicsek, seed,
                                                   tp2::brute_force_neighbors);
    const auto result_b = tp2::advance_time_step(particles, parameters, 0.6,
                                                   tp2::InteractionRule::kVicsek, seed,
                                                   tp2::brute_force_neighbors);

    for (std::size_t i = 0; i < result_a.size(); ++i) {
        expect_near(result_a[i].x, result_b[i].x, 0.0, "reproducible_with_same_seed",
                    "misma semilla debe dar exactamente el mismo x_new");
        expect_near(result_a[i].theta, result_b[i].theta, 0.0, "reproducible_with_same_seed",
                    "misma semilla debe dar exactamente el mismo theta_new");
    }
}

// 8. Semillas distintas pueden producir resultados distintos (con ruido).
void test_different_seed_can_differ() {
    const std::vector<tp2::Particle> particles = {make_particle(0, 2.0, 2.0, 0.3),
                                                   make_particle(1, 2.4, 2.0, 1.0),
                                                   make_particle(2, 2.0, 2.4, 2.2)};
    const tp2::Parameters parameters = make_parameters(10.0, 1.0, 1.0, 0.03);

    const auto baseline = tp2::advance_time_step(particles, parameters, 0.6,
                                                   tp2::InteractionRule::kVoter, 1,
                                                   tp2::brute_force_neighbors);

    bool found_difference = false;
    for (std::uint64_t seed = 2; seed < 40; ++seed) {
        const auto result = tp2::advance_time_step(particles, parameters, 0.6,
                                                     tp2::InteractionRule::kVoter, seed,
                                                     tp2::brute_force_neighbors);
        for (std::size_t i = 0; i < result.size(); ++i) {
            if (std::abs(result[i].theta - baseline[i].theta) > 1e-12) {
                found_difference = true;
            }
        }
    }
    expect_true(found_difference, "different_seed_can_differ",
                "alguna semilla distinta debe producir un resultado distinto");
}

// 9. El paso da el mismo resultado usando fuerza bruta o CIM como función
// de búsqueda de vecinos, ya que ambas están validadas como equivalentes.
void test_consistent_between_bruteforce_and_cim_neighbor_search() {
    std::vector<tp2::Particle> particles;
    std::mt19937 particle_rng(777);
    std::uniform_real_distribution<double> position(0.0, 10.0);
    std::uniform_real_distribution<double> angle(0.0, 2.0 * kPi);
    for (std::size_t id = 0; id < 40; ++id) {
        particles.push_back(make_particle(id, position(particle_rng), position(particle_rng),
                                           angle(particle_rng)));
    }
    const tp2::Parameters parameters = make_parameters(10.0, 1.0, 1.0, 0.03);

    const std::uint64_t seed = 2222;
    const auto result_bf = tp2::advance_time_step(particles, parameters, 0.3,
                                                    tp2::InteractionRule::kVicsek, seed,
                                                    tp2::brute_force_neighbors);
    const auto result_cim = tp2::advance_time_step(particles, parameters, 0.3,
                                                     tp2::InteractionRule::kVicsek, seed,
                                                     tp2::cell_index_neighbors);

    for (std::size_t i = 0; i < result_bf.size(); ++i) {
        expect_near(result_bf[i].x, result_cim[i].x, 1e-9,
                    "consistent_between_bruteforce_and_cim_neighbor_search",
                    "x_new debe coincidir usando fuerza bruta o CIM como búsqueda de vecinos");
        expect_near(result_bf[i].theta, result_cim[i].theta, 1e-9,
                    "consistent_between_bruteforce_and_cim_neighbor_search",
                    "theta_new debe coincidir usando fuerza bruta o CIM como búsqueda de vecinos");
    }
}

// 10. Votante, partícula aislada, eta=0: conserva orientación y se mueve
// según esa orientación conservada.
void test_voter_isolated_moves_with_conserved_theta() {
    const std::vector<tp2::Particle> particles = {make_particle(0, 3.0, 3.0, kPi)};
    const tp2::Parameters parameters = make_parameters(10.0, 1.0, 1.0, 0.03);
    const std::uint64_t seed = 10;

    const auto next_state = tp2::advance_time_step(particles, parameters, 0.0,
                                                     tp2::InteractionRule::kVoter, seed,
                                                     tp2::brute_force_neighbors);

    expect_near(next_state[0].theta, tp2::normalize_angle(kPi), kTolerance,
                "voter_isolated_moves_with_conserved_theta",
                "votante aislado con eta=0 conserva su orientación");
    expect_near(next_state[0].x, 3.0 + 0.03 * std::cos(kPi), 1e-9,
                "voter_isolated_moves_with_conserved_theta",
                "se mueve con la orientación conservada");
    expect_near(next_state[0].y, 3.0 + 0.03 * std::sin(kPi), 1e-9,
                "voter_isolated_moves_with_conserved_theta",
                "se mueve con la orientación conservada");
}

// 11. Vicsek: aunque theta_new difiera mucho de theta_old, el movimiento de
// este paso usa theta_old, nunca theta_new.
void test_vicsek_movement_ignores_new_theta() {
    // Dos partículas vecinas con orientaciones opuestas (0 y pi): el
    // promedio vectorial se anula en seno/coseno... en cambio, para forzar
    // un theta_new bien distinto de theta_old, usamos tres partículas: la
    // 0 mira a 0, sus vecinas miran a pi/2, dando theta_new(0) = pi/4,
    // claramente distinto de theta_old(0) = 0.
    const std::vector<tp2::Particle> particles = {make_particle(0, 5.0, 5.0, 0.0),
                                                   make_particle(1, 5.1, 5.0, kPi / 2.0)};
    const tp2::Parameters parameters = make_parameters(10.0, 1.0, 1.0, 0.03);
    const std::uint64_t seed = 11;

    const auto next_state = tp2::advance_time_step(particles, parameters, 0.0,
                                                     tp2::InteractionRule::kVicsek, seed,
                                                     tp2::brute_force_neighbors);

    expect_true(std::abs(next_state[0].theta - 0.0) > 0.1, "vicsek_movement_ignores_new_theta",
                "theta_new debe diferir claramente de theta_old para que el test sea significativo");
    expect_near(next_state[0].x, 5.0 + 0.03 * std::cos(0.0), 1e-9,
                "vicsek_movement_ignores_new_theta",
                "x_new debe calcularse con theta_old=0, no con theta_new");
    expect_near(next_state[0].y, 5.0 + 0.03 * std::sin(0.0), 1e-9,
                "vicsek_movement_ignores_new_theta",
                "y_new debe calcularse con theta_old=0 (sin(0)=0), no con theta_new");
}

// 12. El estado nuevo conserva los mismos `id` que el estado viejo, en el
// mismo orden posicional de entrada.
void test_ids_preserved_across_step() {
    const std::vector<tp2::Particle> particles = {make_particle(7, 0.0, 0.0, 0.0),
                                                   make_particle(3, 1.0, 1.0, 1.0),
                                                   make_particle(9, 2.0, 2.0, 2.0)};
    const tp2::Parameters parameters = make_parameters(10.0, 1.0, 1.0, 0.03);
    const std::uint64_t seed = 12;

    const auto next_state = tp2::advance_time_step(particles, parameters, 0.2,
                                                     tp2::InteractionRule::kVoter, seed,
                                                     tp2::brute_force_neighbors);

    expect_true(next_state.size() == particles.size(), "ids_preserved_across_step",
                "el estado nuevo debe tener la misma cantidad de partículas");
    for (std::size_t i = 0; i < particles.size(); ++i) {
        expect_true(next_state[i].id == particles[i].id, "ids_preserved_across_step",
                    "el id en la posición " + std::to_string(i) + " debe conservarse");
    }
}

// 13. Encadenar dos pasos: el segundo paso debe construir sus vecinos a
// partir de la posición resultante del primer paso, no de la posición
// original. Se verifica moviendo dos partículas hasta quedar vecinas recién
// después del primer paso.
void test_two_step_chain_uses_updated_positions() {
    // Separadas 1.05 en x (fuera de rc=1); ambas con theta=0 se acercan
    // 0.03 cada una hacia la otra en cada paso (una avanza hacia +x mirando
    // a la otra desde la izquierda... para simplificar, movemos solo la de
    // la izquierda hacia la derecha y dejamos la otra mirando en dirección
    // opuesta para no alejarse; total de acercamiento: 0.06 por paso).
    std::vector<tp2::Particle> particles = {make_particle(0, 0.0, 5.0, 0.0),
                                             make_particle(1, 1.05, 5.0, kPi)};
    const tp2::Parameters parameters = make_parameters(10.0, 1.0, 1.0, 0.03);
    const std::uint64_t seed = 13;

    // Paso 1: separación sigue siendo 1.05 - 0.06 = 0.99 recién en las
    // posiciones nuevas, pero los vecinos de ESTE paso se calculan con la
    // separación vieja (1.05, no vecinos), así que ambas conservan theta.
    particles = tp2::advance_time_step(particles, parameters, 0.0, tp2::InteractionRule::kVoter,
                                        seed, tp2::brute_force_neighbors);
    expect_near(particles[0].theta, 0.0, kTolerance, "two_step_chain_uses_updated_positions",
                "en el primer paso todavía no son vecinas (separación vieja 1.05 > rc)");
    expect_near(particles[1].theta, tp2::normalize_angle(kPi), kTolerance,
                "two_step_chain_uses_updated_positions",
                "en el primer paso todavía no son vecinas (separación vieja 1.05 > rc)");

    const double separation_after_step_one = particles[1].x - particles[0].x;
    expect_true(separation_after_step_one <= 1.0 + 1e-9, "two_step_chain_uses_updated_positions",
                "tras el primer paso la separación debe haber quedado dentro de rc=1 "
                "(0.99 esperado), para que el segundo paso sí las vea vecinas");

    // Paso 2: ahora la búsqueda de vecinos debe usar la posición resultante
    // del paso 1 (separación ~0.99), así que deben pasar a verse vecinas.
    const auto second_step_neighbors = tp2::brute_force_neighbors(particles, parameters);
    expect_true(!second_step_neighbors[0].empty(), "two_step_chain_uses_updated_positions",
                "el segundo paso debe construir vecinos con la posición actualizada del primer "
                "paso, no con la posición original");
}

}  // namespace

int main() {
    test_backward_motion_uses_old_theta_not_new();
    test_equation_of_motion_exact_isolated_particle();
    test_periodic_wrap_applied_to_new_positions();
    test_neighbors_built_from_old_positions();
    test_order_independence_with_same_seed();
    test_input_state_not_mutated();
    test_reproducible_with_same_seed();
    test_different_seed_can_differ();
    test_consistent_between_bruteforce_and_cim_neighbor_search();
    test_voter_isolated_moves_with_conserved_theta();
    test_vicsek_movement_ignores_new_theta();
    test_ids_preserved_across_step();
    test_two_step_chain_uses_updated_positions();

    std::cout << "test_time_step: todos los casos pasaron\n";
    return 0;
}
