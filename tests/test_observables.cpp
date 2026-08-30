#include "core/model.hpp"
#include "core/neighbor_search.hpp"
#include "core/observables.hpp"

#include <cmath>
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

// ---------------------------------------------------------------------
// Polarización
// ---------------------------------------------------------------------

// 1. Una sola partícula: va=1.
void test_polarization_single_particle() {
    const std::vector<tp2::Particle> particles = {make_particle(0, 0.0, 0.0, 1.234)};
    expect_near(tp2::polarization(particles), 1.0, kTolerance, "polarization_single_particle",
                "una única partícula debe dar va=1");
}

// 2. Todas las orientaciones iguales: va=1.
void test_polarization_all_equal() {
    const std::vector<tp2::Particle> particles = {
        make_particle(0, 0.0, 0.0, 0.7), make_particle(1, 1.0, 1.0, 0.7),
        make_particle(2, 2.0, 2.0, 0.7), make_particle(3, 3.0, 3.0, 0.7)};
    expect_near(tp2::polarization(particles), 1.0, kTolerance, "polarization_all_equal",
                "todas las orientaciones iguales deben dar va=1");
}

// 3. Dos partículas con orientaciones opuestas: va=0.
void test_polarization_opposite_pair() {
    const std::vector<tp2::Particle> particles = {make_particle(0, 0.0, 0.0, 0.0),
                                                   make_particle(1, 0.0, 0.0, kPi)};
    expect_near(tp2::polarization(particles), 0.0, kTolerance, "polarization_opposite_pair",
                "dos orientaciones opuestas deben cancelarse, va=0");
}

// 4. Cuatro direcciones balanceadas (0, pi/2, pi, 3*pi/2): va=0.
void test_polarization_four_balanced_directions() {
    const std::vector<tp2::Particle> particles = {
        make_particle(0, 0.0, 0.0, 0.0), make_particle(1, 0.0, 0.0, kPi / 2.0),
        make_particle(2, 0.0, 0.0, kPi), make_particle(3, 0.0, 0.0, 3.0 * kPi / 2.0)};
    expect_near(tp2::polarization(particles), 0.0, 1e-12, "polarization_four_balanced_directions",
                "cuatro direcciones balanceadas deben cancelarse, va=0");
}

// 5. Direcciones conocidas con resultado analítico: theta = 0 y pi/2 (dos
// partículas). sum_cos=1, sum_sin=1, hypot=sqrt(2), N=2 => va=sqrt(2)/2.
void test_polarization_known_analytic_result() {
    const std::vector<tp2::Particle> particles = {make_particle(0, 0.0, 0.0, 0.0),
                                                   make_particle(1, 0.0, 0.0, kPi / 2.0)};
    const double expected = std::sqrt(2.0) / 2.0;
    expect_near(tp2::polarization(particles), expected, 1e-12, "polarization_known_analytic_result",
                "theta=0 y pi/2 deben dar va=sqrt(2)/2");
}

// 6. Estado aleatorio: 0 <= va <= 1.
void test_polarization_random_state_in_range() {
    std::mt19937 rng(2026);
    std::uniform_real_distribution<double> angle_distribution(0.0, 2.0 * kPi);
    std::vector<tp2::Particle> particles;
    for (std::size_t id = 0; id < 100; ++id) {
        particles.push_back(make_particle(id, 0.0, 0.0, angle_distribution(rng)));
    }

    const double va = tp2::polarization(particles);
    expect_true(va >= -1e-12 && va <= 1.0 + 1e-12, "polarization_random_state_in_range",
                "va debe quedar en [0,1] salvo error numérico despreciable");
}

// 7. El cálculo no modifica el estado.
void test_polarization_does_not_mutate_state() {
    const std::vector<tp2::Particle> original = {make_particle(0, 0.0, 0.0, 0.3),
                                                  make_particle(1, 1.0, 1.0, 1.9)};
    std::vector<tp2::Particle> particles = original;
    const double va = tp2::polarization(particles);
    (void)va;
    for (std::size_t i = 0; i < particles.size(); ++i) {
        expect_near(particles[i].x, original[i].x, 0.0, "polarization_does_not_mutate_state",
                    "polarization no debe modificar x");
        expect_near(particles[i].y, original[i].y, 0.0, "polarization_does_not_mutate_state",
                    "polarization no debe modificar y");
        expect_near(particles[i].theta, original[i].theta, 0.0,
                    "polarization_does_not_mutate_state", "polarization no debe modificar theta");
    }
}

// 8. Caso N=0: convención documentada, va=0.
void test_polarization_empty_state() {
    const std::vector<tp2::Particle> particles;
    expect_near(tp2::polarization(particles), 0.0, kTolerance, "polarization_empty_state",
                "N=0 debe devolver va=0 según la convención documentada");
}

// ---------------------------------------------------------------------
// Clusters
// ---------------------------------------------------------------------

// 1. Todas las partículas aisladas: S=1/N.
void test_cluster_all_isolated() {
    const std::vector<tp2::Particle> particles = {make_particle(0, 0.0, 0.0, 0.0),
                                                   make_particle(1, 5.0, 5.0, 0.0),
                                                   make_particle(2, 2.0, 8.0, 0.0)};
    const std::vector<std::vector<std::size_t>> neighbors = {{}, {}, {}};

    expect_true(tp2::largest_cluster_size(neighbors, particles) == 1, "cluster_all_isolated",
                "sin vecinos, el cluster más grande debe tener tamaño 1");
    expect_near(tp2::largest_cluster_fraction(neighbors, particles), 1.0 / 3.0, kTolerance,
                "cluster_all_isolated", "S debe ser 1/N cuando todas están aisladas");
}

// 2. Todas conectadas: S=1.
void test_cluster_all_connected() {
    const std::vector<tp2::Particle> particles = {
        make_particle(0, 0.0, 0.0, 0.0), make_particle(1, 0.0, 0.0, 0.0),
        make_particle(2, 0.0, 0.0, 0.0), make_particle(3, 0.0, 0.0, 0.0)};
    const std::vector<std::vector<std::size_t>> neighbors = {
        {1, 2, 3}, {0, 2, 3}, {0, 1, 3}, {0, 1, 2}};

    expect_true(tp2::largest_cluster_size(neighbors, particles) == 4, "cluster_all_connected",
                "clique completo debe dar un único cluster de tamaño N");
    expect_near(tp2::largest_cluster_fraction(neighbors, particles), 1.0, kTolerance,
                "cluster_all_connected", "S debe ser 1 cuando todas están conectadas");
}

// 3. Cadena A-B-C, donde A y C no son vecinos directos: S=1 (transitividad).
void test_cluster_chain_transitive() {
    const std::vector<tp2::Particle> particles = {make_particle(0, 0.0, 0.0, 0.0),
                                                   make_particle(1, 0.0, 0.0, 0.0),
                                                   make_particle(2, 0.0, 0.0, 0.0)};
    // A(0)-B(1)-C(2), A y C no son vecinos directos entre sí.
    const std::vector<std::vector<std::size_t>> neighbors = {{1}, {0, 2}, {1}};

    expect_true(tp2::largest_cluster_size(neighbors, particles) == 3, "cluster_chain_transitive",
                "A-B-C debe formar un único cluster de tamaño 3 aunque A y C no sean vecinos "
                "directos");
    expect_near(tp2::largest_cluster_fraction(neighbors, particles), 1.0, kTolerance,
                "cluster_chain_transitive", "S debe ser 1 para la cadena completa");
}

// 4. Componentes de tamaños 3, 2 y 1: S = 3/6.
void test_cluster_mixed_component_sizes() {
    // Cluster grande: 0-1-2 (cadena). Cluster mediano: 3-4. Aislada: 5.
    const std::vector<tp2::Particle> particles = {
        make_particle(0, 0.0, 0.0, 0.0), make_particle(1, 0.0, 0.0, 0.0),
        make_particle(2, 0.0, 0.0, 0.0), make_particle(3, 0.0, 0.0, 0.0),
        make_particle(4, 0.0, 0.0, 0.0), make_particle(5, 0.0, 0.0, 0.0)};
    const std::vector<std::vector<std::size_t>> neighbors = {
        {1}, {0, 2}, {1}, {4}, {3}, {}};

    expect_true(tp2::largest_cluster_size(neighbors, particles) == 3,
                "cluster_mixed_component_sizes", "el cluster más grande debe tener tamaño 3");
    expect_near(tp2::largest_cluster_fraction(neighbors, particles), 3.0 / 6.0, kTolerance,
                "cluster_mixed_component_sizes", "S debe ser 3/6");
}

// 5. Vecinos que cruzan el borde periódico: posiciones cerca de x=0 y x=L,
// vecinos obtenidos con el CIM, deben pertenecer al mismo cluster.
void test_cluster_periodic_boundary_with_cim() {
    tp2::Parameters parameters;
    parameters.box_length = 10.0;
    parameters.interaction_radius = 1.0;

    // Dos partículas separadas 0.2 a través del borde (9.9 y 0.1), y una
    // tercera lejos de ambas para verificar que no se une al cluster.
    const std::vector<tp2::Particle> particles = {make_particle(0, 9.9, 5.0, 0.0),
                                                   make_particle(1, 0.1, 5.0, 0.0),
                                                   make_particle(2, 5.0, 5.0, 0.0)};

    const auto neighbors = tp2::cell_index_neighbors(particles, parameters);

    expect_true(tp2::largest_cluster_size(neighbors, particles) == 2,
                "cluster_periodic_boundary_with_cim",
                "las partículas cercanas cruzando x=0/x=L deben quedar en el mismo cluster");
}

// 6. Misma configuración produce el mismo resultado con fuerza bruta y CIM.
void test_cluster_matches_bruteforce_and_cim() {
    tp2::Parameters parameters;
    parameters.box_length = 10.0;
    parameters.interaction_radius = 1.0;

    std::mt19937 rng(77);
    std::uniform_real_distribution<double> position_distribution(0.0, parameters.box_length);
    std::vector<tp2::Particle> particles;
    for (std::size_t id = 0; id < 60; ++id) {
        particles.push_back(
            make_particle(id, position_distribution(rng), position_distribution(rng), 0.0));
    }

    const auto neighbors_bruteforce = tp2::brute_force_neighbors(particles, parameters);
    const auto neighbors_cim = tp2::cell_index_neighbors(particles, parameters);

    const std::size_t largest_bruteforce = tp2::largest_cluster_size(neighbors_bruteforce, particles);
    const std::size_t largest_cim = tp2::largest_cluster_size(neighbors_cim, particles);

    expect_true(largest_bruteforce == largest_cim, "cluster_matches_bruteforce_and_cim",
                "el cluster más grande debe coincidir usando fuerza bruta y CIM");
}

// 7. Caso N=0: convención documentada, S=0.
void test_cluster_empty_state() {
    const std::vector<tp2::Particle> particles;
    const std::vector<std::vector<std::size_t>> neighbors;

    expect_true(tp2::largest_cluster_size(neighbors, particles) == 0, "cluster_empty_state",
                "N=0 debe devolver tamaño de cluster 0");
    expect_near(tp2::largest_cluster_fraction(neighbors, particles), 0.0, kTolerance,
                "cluster_empty_state", "N=0 debe devolver S=0 según la convención documentada");
}

// 8. Los IDs pueden no ser consecutivos (por ejemplo 7, 20, 99).
void test_cluster_non_consecutive_ids() {
    const std::vector<tp2::Particle> particles = {make_particle(99, 0.0, 0.0, 0.0),
                                                   make_particle(7, 0.0, 0.0, 0.0),
                                                   make_particle(20, 0.0, 0.0, 0.0)};
    // 99 y 7 son vecinos entre sí; 20 está aislada.
    const std::vector<std::vector<std::size_t>> neighbors = {{7}, {99}, {}};

    expect_true(tp2::largest_cluster_size(neighbors, particles) == 2,
                "cluster_non_consecutive_ids",
                "debe usar id para resolver vecinos, no la posición en el vector");
    expect_near(tp2::largest_cluster_fraction(neighbors, particles), 2.0 / 3.0, kTolerance,
                "cluster_non_consecutive_ids", "S debe ser 2/3 con ids no consecutivos");
}

// 9. La lista de vecinos no se modifica.
void test_cluster_does_not_mutate_neighbors() {
    const std::vector<tp2::Particle> particles = {make_particle(0, 0.0, 0.0, 0.0),
                                                   make_particle(1, 0.0, 0.0, 0.0),
                                                   make_particle(2, 0.0, 0.0, 0.0)};
    const std::vector<std::vector<std::size_t>> original_neighbors = {{1}, {0, 2}, {1}};
    std::vector<std::vector<std::size_t>> neighbors = original_neighbors;

    const std::size_t size = tp2::largest_cluster_size(neighbors, particles);
    (void)size;

    expect_true(neighbors == original_neighbors, "cluster_does_not_mutate_neighbors",
                "largest_cluster_size no debe modificar la lista de vecinos");
}

// 10. Verificar explícitamente la transitividad y no solo la cantidad de
// vecinos directos: A-B, C-D, B-C forman un único cluster de 4 aunque A no
// sea vecina directa de C ni de D.
void test_cluster_transitivity_not_just_direct_count() {
    const std::vector<tp2::Particle> particles = {
        make_particle(0, 0.0, 0.0, 0.0), make_particle(1, 0.0, 0.0, 0.0),
        make_particle(2, 0.0, 0.0, 0.0), make_particle(3, 0.0, 0.0, 0.0)};
    // A(0)-B(1), B(1)-C(2), C(2)-D(3). Cada partícula tiene a lo sumo 2
    // vecinos directos, pero la componente conexa completa tiene tamaño 4.
    const std::vector<std::vector<std::size_t>> neighbors = {{1}, {0, 2}, {1, 3}, {2}};

    expect_true(tp2::largest_cluster_size(neighbors, particles) == 4,
                "cluster_transitivity_not_just_direct_count",
                "la cadena A-B-C-D debe formar un único cluster de tamaño 4 por transitividad");
}

}  // namespace

int main() {
    test_polarization_single_particle();
    test_polarization_all_equal();
    test_polarization_opposite_pair();
    test_polarization_four_balanced_directions();
    test_polarization_known_analytic_result();
    test_polarization_random_state_in_range();
    test_polarization_does_not_mutate_state();
    test_polarization_empty_state();

    test_cluster_all_isolated();
    test_cluster_all_connected();
    test_cluster_chain_transitive();
    test_cluster_mixed_component_sizes();
    test_cluster_periodic_boundary_with_cim();
    test_cluster_matches_bruteforce_and_cim();
    test_cluster_empty_state();
    test_cluster_non_consecutive_ids();
    test_cluster_does_not_mutate_neighbors();
    test_cluster_transitivity_not_just_direct_count();

    std::cout << "test_observables: todos los casos pasaron\n";
    return 0;
}
