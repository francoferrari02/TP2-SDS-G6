#include "core/model.hpp"
#include "core/rules.hpp"

#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <iostream>
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

// Distancia angular mínima entre dos ángulos, en [0, pi], para comparar
// orientaciones sin ambigüedad de wraparound en 0/2*pi.
double angular_distance(double a, double b) {
    double diff = std::fmod(std::abs(a - b), 2.0 * kPi);
    if (diff > kPi) {
        diff = 2.0 * kPi - diff;
    }
    return diff;
}

tp2::Particle make_particle(std::size_t id, double x, double y, double theta) {
    tp2::Particle particle;
    particle.id = id;
    particle.x = x;
    particle.y = y;
    particle.theta = theta;
    return particle;
}

// 1. Vicsek con una partícula aislada y eta=0: conserva su orientación.
void test_vicsek_isolated_eta_zero() {
    const std::vector<tp2::Particle> particles = {make_particle(0, 1.0, 1.0, 1.234)};
    const std::vector<std::vector<std::size_t>> neighbors = {{}};
    const std::uint64_t seed = 42;

    const auto result = tp2::vicsek_update(particles, neighbors, 0.0, seed);

    expect_near(result[0], tp2::normalize_angle(1.234), kTolerance, "vicsek_isolated_eta_zero",
                "una partícula aislada con eta=0 debe conservar su orientación");
}

// 2. Vicsek con dos ángulos cercanos a 0 (1° y 359°): el promedio queda
// cerca de 0°, no de 180°.
void test_vicsek_average_across_zero() {
    const double theta_a = 1.0 * kPi / 180.0;
    const double theta_b = 359.0 * kPi / 180.0;
    const std::vector<tp2::Particle> particles = {make_particle(0, 0.0, 0.0, theta_a),
                                                   make_particle(1, 0.0, 0.0, theta_b)};
    const std::vector<std::vector<std::size_t>> neighbors = {{1}, {0}};
    const std::uint64_t seed = 7;

    const auto result = tp2::vicsek_update(particles, neighbors, 0.0, seed);

    expect_true(angular_distance(result[0], 0.0) < 1e-6, "vicsek_average_across_zero",
                "el promedio de 1 grado y 359 grados debe quedar cerca de 0, no de 180");
    expect_true(angular_distance(result[1], 0.0) < 1e-6, "vicsek_average_across_zero",
                "ambas partículas comparten el mismo vecindario, deben promediar igual");
}

// 3. Vicsek con varias orientaciones y resultado analítico conocido.
void test_vicsek_known_analytic_result() {
    // Tres partículas con theta = 0, pi/2, pi. sum_cos = cos(0)+cos(pi/2)+cos(pi) = 0,
    // sum_sin = sin(0)+sin(pi/2)+sin(pi) = 1. atan2(1, 0) = pi/2.
    const std::vector<tp2::Particle> particles = {make_particle(0, 0.0, 0.0, 0.0),
                                                   make_particle(1, 0.0, 0.0, kPi / 2.0),
                                                   make_particle(2, 0.0, 0.0, kPi)};
    const std::vector<std::vector<std::size_t>> neighbors = {{1, 2}, {0, 2}, {0, 1}};
    const std::uint64_t seed = 123;

    const auto result = tp2::vicsek_update(particles, neighbors, 0.0, seed);

    expect_near(result[0], kPi / 2.0, 1e-9, "vicsek_known_analytic_result",
                "atan2(1,0) debe dar exactamente pi/2 para las tres partículas");
    expect_near(result[1], kPi / 2.0, 1e-9, "vicsek_known_analytic_result", "misma vecindad completa");
    expect_near(result[2], kPi / 2.0, 1e-9, "vicsek_known_analytic_result", "misma vecindad completa");
}

// 4. Vicsek con todas las orientaciones iguales y eta=0: conserva esa
// orientación.
void test_vicsek_all_equal_eta_zero() {
    const double theta = 2.5;
    const std::vector<tp2::Particle> particles = {make_particle(0, 0.0, 0.0, theta),
                                                   make_particle(1, 0.5, 0.5, theta),
                                                   make_particle(2, 1.0, 1.0, theta)};
    const std::vector<std::vector<std::size_t>> neighbors = {{1, 2}, {0, 2}, {0, 1}};
    const std::uint64_t seed = 99;

    const auto result = tp2::vicsek_update(particles, neighbors, 0.0, seed);

    for (std::size_t i = 0; i < result.size(); ++i) {
        expect_near(result[i], tp2::normalize_angle(theta), 1e-9, "vicsek_all_equal_eta_zero",
                    "todas las orientaciones iguales deben conservarse con eta=0");
    }
}

// 5. Votante con un único vecino externo y eta=0: copia siempre a ese
// vecino.
void test_voter_single_neighbor_eta_zero() {
    const std::vector<tp2::Particle> particles = {make_particle(0, 0.0, 0.0, 0.3),
                                                   make_particle(1, 0.0, 0.0, 1.7)};
    const std::vector<std::vector<std::size_t>> neighbors = {{1}, {0}};

    for (std::uint64_t seed = 0; seed < 20; ++seed) {
        const auto result = tp2::voter_update(particles, neighbors, 0.0, seed);
        expect_near(result[0], tp2::normalize_angle(1.7), 1e-9, "voter_single_neighbor_eta_zero",
                    "con un único vecino externo debe copiarlo siempre, semilla " +
                        std::to_string(seed));
    }
}

// 6. Votante aislado y eta=0: conserva su orientación.
void test_voter_isolated_eta_zero() {
    const std::vector<tp2::Particle> particles = {make_particle(0, 0.0, 0.0, 4.1)};
    const std::vector<std::vector<std::size_t>> neighbors = {{}};
    const std::uint64_t seed = 5;

    const auto result = tp2::voter_update(particles, neighbors, 0.0, seed);

    expect_near(result[0], tp2::normalize_angle(4.1), 1e-9, "voter_isolated_eta_zero",
                "una partícula aislada con eta=0 debe conservar su orientación");
}

// 7. Votante aislado y eta>0: cambia solamente dentro de [-eta/2, eta/2].
void test_voter_isolated_eta_positive_bounded() {
    const double theta = 1.0;
    const double eta = 0.4;
    const std::vector<tp2::Particle> particles = {make_particle(0, 0.0, 0.0, theta)};
    const std::vector<std::vector<std::size_t>> neighbors = {{}};

    for (std::uint64_t seed = 0; seed < 50; ++seed) {
        const auto result = tp2::voter_update(particles, neighbors, eta, seed);
        const double delta = angular_distance(result[0], tp2::normalize_angle(theta));
        expect_true(delta <= eta / 2.0 + 1e-9, "voter_isolated_eta_positive_bounded",
                    "el cambio debe quedar dentro de [-eta/2, eta/2], semilla " +
                        std::to_string(seed));
    }
}

// 8. Votante con varios vecinos y eta=0: el resultado pertenece al
// conjunto de orientaciones viejas de sus vecinos.
void test_voter_multiple_neighbors_eta_zero() {
    const std::vector<tp2::Particle> particles = {make_particle(0, 0.0, 0.0, 0.0),
                                                   make_particle(1, 0.0, 0.0, 1.0),
                                                   make_particle(2, 0.0, 0.0, 2.0),
                                                   make_particle(3, 0.0, 0.0, 3.0)};
    const std::vector<std::vector<std::size_t>> neighbors = {{1, 2, 3}, {}, {}, {}};

    for (std::uint64_t seed = 0; seed < 30; ++seed) {
        const auto result = tp2::voter_update(particles, neighbors, 0.0, seed);
        const bool matches_a_neighbor = angular_distance(result[0], 1.0) < 1e-9 ||
                                         angular_distance(result[0], 2.0) < 1e-9 ||
                                         angular_distance(result[0], 3.0) < 1e-9;
        expect_true(matches_a_neighbor, "voter_multiple_neighbors_eta_zero",
                    "el resultado debe ser exactamente una de las orientaciones de los vecinos, "
                    "semilla " + std::to_string(seed));
    }
}

// 9. Ninguna regla debe modificar el vector de orientaciones viejo.
void test_rules_do_not_mutate_old_state() {
    const std::vector<tp2::Particle> original = {make_particle(0, 0.0, 0.0, 0.3),
                                                  make_particle(1, 0.0, 0.0, 1.9),
                                                  make_particle(2, 0.0, 0.0, 5.5)};
    std::vector<tp2::Particle> particles = original;
    const std::vector<std::vector<std::size_t>> neighbors = {{1, 2}, {0, 2}, {0, 1}};
    const std::uint64_t seed_vicsek = 11;
    const std::uint64_t seed_voter = 12;

    const auto vicsek_result = tp2::vicsek_update(particles, neighbors, 0.3, seed_vicsek);
    for (std::size_t i = 0; i < particles.size(); ++i) {
        expect_near(particles[i].theta, original[i].theta, 0.0, "rules_do_not_mutate_old_state",
                    "vicsek_update no debe modificar particles[" + std::to_string(i) + "]");
    }

    const auto voter_result = tp2::voter_update(particles, neighbors, 0.3, seed_voter);
    for (std::size_t i = 0; i < particles.size(); ++i) {
        expect_near(particles[i].theta, original[i].theta, 0.0, "rules_do_not_mutate_old_state",
                    "voter_update no debe modificar particles[" + std::to_string(i) + "]");
    }

    (void)vicsek_result;
    (void)voter_result;
}

// 10. El resultado de cada regla debe quedar normalizado.
void test_results_are_normalized() {
    const std::vector<tp2::Particle> particles = {make_particle(0, 0.0, 0.0, -10.0),
                                                   make_particle(1, 0.0, 0.0, 25.0)};
    const std::vector<std::vector<std::size_t>> neighbors = {{1}, {0}};
    const std::uint64_t seed_vicsek = 1;
    const std::uint64_t seed_voter = 2;

    const auto vicsek_result = tp2::vicsek_update(particles, neighbors, 1.0, seed_vicsek);
    for (const double theta : vicsek_result) {
        expect_true(theta >= 0.0 && theta < 2.0 * kPi, "results_are_normalized",
                    "vicsek_update debe devolver ángulos en [0, 2*pi)");
    }

    const auto voter_result = tp2::voter_update(particles, neighbors, 1.0, seed_voter);
    for (const double theta : voter_result) {
        expect_true(theta >= 0.0 && theta < 2.0 * kPi, "results_are_normalized",
                    "voter_update debe devolver ángulos en [0, 2*pi)");
    }
}

// 11. El ruido debe ser reproducible si se usa la misma semilla.
void test_noise_reproducible_with_same_seed() {
    const std::vector<tp2::Particle> particles = {make_particle(0, 0.0, 0.0, 0.5),
                                                   make_particle(1, 0.0, 0.0, 1.5),
                                                   make_particle(2, 0.0, 0.0, 2.5)};
    const std::vector<std::vector<std::size_t>> neighbors = {{1, 2}, {0, 2}, {0, 1}};

    const std::uint64_t seed = 2024;
    const auto result_a = tp2::vicsek_update(particles, neighbors, 0.6, seed);
    const auto result_b = tp2::vicsek_update(particles, neighbors, 0.6, seed);
    for (std::size_t i = 0; i < result_a.size(); ++i) {
        expect_near(result_a[i], result_b[i], 0.0, "noise_reproducible_with_same_seed",
                    "misma semilla debe producir exactamente el mismo resultado (vicsek)");
    }

    const auto voter_a = tp2::voter_update(particles, neighbors, 0.6, seed);
    const auto voter_b = tp2::voter_update(particles, neighbors, 0.6, seed);
    for (std::size_t i = 0; i < voter_a.size(); ++i) {
        expect_near(voter_a[i], voter_b[i], 0.0, "noise_reproducible_with_same_seed",
                    "misma semilla debe producir exactamente el mismo resultado (voter)");
    }
}

// 12. Una semilla diferente debe poder producir resultados diferentes.
void test_noise_differs_with_different_seed() {
    const std::vector<tp2::Particle> particles = {make_particle(0, 0.0, 0.0, 0.5),
                                                   make_particle(1, 0.0, 0.0, 1.5),
                                                   make_particle(2, 0.0, 0.0, 2.5)};
    const std::vector<std::vector<std::size_t>> neighbors = {{1, 2}, {0, 2}, {0, 1}};

    bool vicsek_found_difference = false;
    bool voter_found_difference = false;
    const auto baseline_vicsek = tp2::vicsek_update(particles, neighbors, 0.6, 1);
    const auto baseline_voter = tp2::voter_update(particles, neighbors, 0.6, 1);

    for (std::uint64_t seed = 2; seed < 40; ++seed) {
        const auto vicsek_result = tp2::vicsek_update(particles, neighbors, 0.6, seed);
        for (std::size_t i = 0; i < vicsek_result.size(); ++i) {
            if (std::abs(vicsek_result[i] - baseline_vicsek[i]) > 1e-12) {
                vicsek_found_difference = true;
            }
        }

        const auto voter_result = tp2::voter_update(particles, neighbors, 0.6, seed);
        for (std::size_t i = 0; i < voter_result.size(); ++i) {
            if (std::abs(voter_result[i] - baseline_voter[i]) > 1e-12) {
                voter_found_difference = true;
            }
        }
    }

    expect_true(vicsek_found_difference, "noise_differs_with_different_seed",
                "alguna semilla distinta debe producir un resultado distinto (vicsek)");
    expect_true(voter_found_difference, "noise_differs_with_different_seed",
                "alguna semilla distinta debe producir un resultado distinto (voter)");
}

// 13. Verificar que el promedio vectorial de Vicsek funciona correctamente
// al cruzar el ángulo 0/2*pi.
void test_vicsek_average_wraps_correctly() {
    // Ángulos simétricos alrededor de 2*pi: 350° y 10°, deben promediar a 0°/360°.
    const double theta_a = 350.0 * kPi / 180.0;
    const double theta_b = 10.0 * kPi / 180.0;
    const std::vector<tp2::Particle> particles = {make_particle(0, 0.0, 0.0, theta_a),
                                                   make_particle(1, 0.0, 0.0, theta_b)};
    const std::vector<std::vector<std::size_t>> neighbors = {{1}, {0}};
    const std::uint64_t seed = 321;

    const auto result = tp2::vicsek_update(particles, neighbors, 0.0, seed);

    expect_true(angular_distance(result[0], 0.0) < 1e-6, "vicsek_average_wraps_correctly",
                "350 grados y 10 grados deben promediar cerca de 0/360 grados");
    expect_true(angular_distance(result[1], 0.0) < 1e-6, "vicsek_average_wraps_correctly",
                "350 grados y 10 grados deben promediar cerca de 0/360 grados");
}

// 14. El resultado de cada regla no debe depender del orden de
// almacenamiento de las partículas: solo de la semilla y del `id`.
void test_rules_are_order_independent() {
    const std::vector<tp2::Particle> original = {
        make_particle(0, 0.0, 0.0, 0.1), make_particle(1, 0.0, 0.0, 0.5),
        make_particle(2, 0.0, 0.0, 1.2), make_particle(3, 0.0, 0.0, 2.0)};
    const std::vector<std::vector<std::size_t>> neighbors_original = {
        {1, 2, 3}, {0, 2}, {0, 1, 3}, {0, 2}};

    // Misma partículas y vecinos, pero permutadas; los vecinos siguen
    // expresados en `id`, así que la vecindad "real" no cambia.
    const std::vector<tp2::Particle> permuted = {original[3], original[1], original[0],
                                                  original[2]};
    const std::vector<std::vector<std::size_t>> neighbors_permuted = {
        neighbors_original[3], neighbors_original[1], neighbors_original[0],
        neighbors_original[2]};
    // permuted[k].id -> posición k. Mapa id -> posición en `permuted` para
    // no asumir a mano una fórmula de índices.
    std::vector<std::size_t> permuted_index_of_id(original.size());
    for (std::size_t k = 0; k < permuted.size(); ++k) {
        permuted_index_of_id[permuted[k].id] = k;
    }

    const std::uint64_t seed = 4242;
    const auto result_original = tp2::vicsek_update(original, neighbors_original, 0.5, seed);
    const auto result_permuted = tp2::vicsek_update(permuted, neighbors_permuted, 0.5, seed);

    for (std::size_t i = 0; i < original.size(); ++i) {
        const std::size_t permuted_index = permuted_index_of_id[original[i].id];
        expect_near(result_original[i], result_permuted[permuted_index], 0.0,
                    "rules_are_order_independent",
                    "vicsek: la orientación de la partícula id=" +
                        std::to_string(original[i].id) +
                        " debe coincidir sin importar el orden de almacenamiento");
    }

    const auto voter_original = tp2::voter_update(original, neighbors_original, 0.5, seed);
    const auto voter_permuted = tp2::voter_update(permuted, neighbors_permuted, 0.5, seed);
    for (std::size_t i = 0; i < original.size(); ++i) {
        const std::size_t permuted_index = permuted_index_of_id[original[i].id];
        expect_near(voter_original[i], voter_permuted[permuted_index], 0.0,
                    "rules_are_order_independent",
                    "voter: la orientación de la partícula id=" +
                        std::to_string(original[i].id) +
                        " debe coincidir sin importar el orden de almacenamiento");
    }
}

}  // namespace

int main() {
    test_vicsek_isolated_eta_zero();
    test_vicsek_average_across_zero();
    test_vicsek_known_analytic_result();
    test_vicsek_all_equal_eta_zero();
    test_voter_single_neighbor_eta_zero();
    test_voter_isolated_eta_zero();
    test_voter_isolated_eta_positive_bounded();
    test_voter_multiple_neighbors_eta_zero();
    test_rules_do_not_mutate_old_state();
    test_results_are_normalized();
    test_noise_reproducible_with_same_seed();
    test_noise_differs_with_different_seed();
    test_vicsek_average_wraps_correctly();
    test_rules_are_order_independent();

    std::cout << "test_rules: todos los casos pasaron\n";
    return 0;
}
