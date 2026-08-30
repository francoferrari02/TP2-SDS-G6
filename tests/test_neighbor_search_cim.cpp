#include "core/model.hpp"
#include "core/neighbor_search.hpp"

#include <algorithm>
#include <cassert>
#include <cstdlib>
#include <iostream>
#include <random>
#include <string>
#include <utility>
#include <vector>

namespace {

using tp2::Parameters;
using tp2::Particle;
using tp2::brute_force_neighbors;
using tp2::cell_index_neighbors;

std::vector<Particle> generate_random_particles(std::size_t count, unsigned seed,
                                                  double box_length) {
    std::mt19937 rng(seed);
    std::uniform_real_distribution<double> position(0.0, box_length);
    std::vector<Particle> particles;
    particles.reserve(count);
    for (std::size_t i = 0; i < count; ++i) {
        particles.push_back(Particle{i, position(rng), position(rng), 0.0});
    }
    return particles;
}

// Falla con un mensaje claro (partícula, posición y listas completas de IDs)
// en lugar de solo comparar tamaños.
void expect_same_neighbors(const std::vector<std::vector<std::size_t>>& bruteforce,
                            const std::vector<std::vector<std::size_t>>& cim,
                            const std::vector<Particle>& particles,
                            const std::string& case_name) {
    if (bruteforce.size() != cim.size()) {
        std::cerr << "[" << case_name << "] tamanios de resultado distintos: "
                  << "bruteforce=" << bruteforce.size() << " cim=" << cim.size()
                  << std::endl;
        std::abort();
    }
    for (std::size_t i = 0; i < bruteforce.size(); ++i) {
        if (bruteforce[i] != cim[i]) {
            std::cerr << "[" << case_name
                      << "] las listas de vecinos difieren para la particula id="
                      << particles[i].id << " (posicion " << i
                      << " en el vector de entrada)\n";
            std::cerr << "  fuerza bruta (" << bruteforce[i].size() << "): ";
            for (const auto id : bruteforce[i]) {
                std::cerr << id << ' ';
            }
            std::cerr << "\n  CIM          (" << cim[i].size() << "): ";
            for (const auto id : cim[i]) {
                std::cerr << id << ' ';
            }
            std::cerr << std::endl;
            std::abort();
        }
    }
}

void compare_cim_vs_bruteforce(const std::vector<Particle>& particles,
                                const Parameters& parameters,
                                const std::string& case_name) {
    const auto bruteforce = brute_force_neighbors(particles, parameters);
    const auto cim = cell_index_neighbors(particles, parameters);
    expect_same_neighbors(bruteforce, cim, particles, case_name);
}

// 1. Muchos estados pequeños generados con semillas fijas.
void test_many_small_random_states_fixed_seeds() {
    const Parameters parameters;
    for (unsigned seed = 1; seed <= 30; ++seed) {
        const auto particles = generate_random_particles(12, seed, parameters.box_length);
        compare_cim_vs_bruteforce(particles, parameters,
                                   "small_random_seed_" + std::to_string(seed));
    }
}

// 2. Partículas aleatorias uniformes en cantidad moderada.
void test_random_uniform_moderate_size() {
    const Parameters parameters;
    for (unsigned seed = 100; seed <= 105; ++seed) {
        const auto particles = generate_random_particles(120, seed, parameters.box_length);
        compare_cim_vs_bruteforce(particles, parameters,
                                   "random_uniform_moderate_seed_" + std::to_string(seed));
    }
}

// 3. Partículas cruzando el borde en x.
void test_cross_periodic_border_x() {
    const Parameters parameters;
    const std::vector<Particle> particles{
        Particle{0, 0.05, 5.0, 0.0},
        Particle{1, 9.97, 5.0, 0.0},
        Particle{2, 9.5, 5.0, 0.0},
        Particle{3, 0.5, 5.0, 0.0},
    };
    compare_cim_vs_bruteforce(particles, parameters, "cross_border_x");
}

// 4. Partículas cruzando el borde en y.
void test_cross_periodic_border_y() {
    const Parameters parameters;
    const std::vector<Particle> particles{
        Particle{0, 5.0, 0.05, 0.0},
        Particle{1, 5.0, 9.97, 0.0},
        Particle{2, 5.0, 9.5, 0.0},
        Particle{3, 5.0, 0.5, 0.0},
    };
    compare_cim_vs_bruteforce(particles, parameters, "cross_border_y");
}

// 5. Partículas cruzando una esquina periódica.
void test_cross_periodic_corner() {
    const Parameters parameters;
    const std::vector<Particle> particles{
        Particle{0, 0.1, 0.1, 0.0},
        Particle{1, 9.9, 9.9, 0.0},
        Particle{2, 9.85, 0.15, 0.0},
        Particle{3, 0.15, 9.85, 0.0},
    };
    compare_cim_vs_bruteforce(particles, parameters, "cross_border_corner");
}

// 6. Pares exactamente a distancia rc.
void test_pairs_exactly_at_radius() {
    const Parameters parameters;
    const std::vector<Particle> particles{
        Particle{0, 5.0, 5.0, 0.0},
        Particle{1, 6.0, 5.0, 0.0},   // distancia exacta 1.0 en x
        Particle{2, 5.0, 4.0, 0.0},   // distancia exacta 1.0 en y (desde particula 0)
        Particle{3, 0.0, 0.0, 0.0},
        Particle{4, 1.0, 0.0, 0.0},   // distancia exacta 1.0, cerca del origen de celdas
    };
    compare_cim_vs_bruteforce(particles, parameters, "pairs_exactly_at_radius");
}

// 7. Pares apenas fuera de rc.
void test_pairs_just_outside_radius() {
    const Parameters parameters;
    const double eps = 1e-9;
    const std::vector<Particle> particles{
        Particle{0, 5.0, 5.0, 0.0},
        Particle{1, 6.0 + eps, 5.0, 0.0},
        Particle{2, 5.0, 4.0 - eps, 0.0},
        Particle{3, 0.0, 0.0, 0.0},
        Particle{4, 1.0 + eps, 0.0, 0.0},
    };
    compare_cim_vs_bruteforce(particles, parameters, "pairs_just_outside_radius");
}

// 8. Varias partículas dentro de la misma celda.
void test_several_particles_in_same_cell() {
    const Parameters parameters;  // cell_size = 1.0 con L=10, rc=1
    const std::vector<Particle> particles{
        Particle{0, 5.05, 5.05, 0.0},
        Particle{1, 5.10, 5.20, 0.0},
        Particle{2, 5.40, 5.60, 0.0},
        Particle{3, 5.90, 5.90, 0.0},
        Particle{4, 5.20, 5.80, 0.0},
    };
    compare_cim_vs_bruteforce(particles, parameters, "several_particles_same_cell");
}

// 9. Partículas en celdas vecinas.
void test_particles_in_neighboring_cells() {
    const Parameters parameters;
    const std::vector<Particle> particles{
        Particle{0, 5.05, 5.05, 0.0},  // celda (5,5)
        Particle{1, 5.95, 5.05, 0.0},  // celda (5,5) o (5,5) vecina en x -> (5,5)/(5,5)... queda cerca del borde
        Particle{2, 6.05, 5.05, 0.0},  // celda (6,5): vecina en x de la celda (5,5)
        Particle{3, 5.05, 6.05, 0.0},  // celda (5,6): vecina en y
        Particle{4, 6.05, 6.05, 0.0},  // celda (6,6): vecina diagonal
    };
    compare_cim_vs_bruteforce(particles, parameters, "particles_in_neighboring_cells");
}

// 10. Partículas en celdas alejadas (no deben interactuar).
void test_particles_in_far_cells() {
    const Parameters parameters;
    const std::vector<Particle> particles{
        Particle{0, 0.5, 0.5, 0.0},
        Particle{1, 5.5, 0.5, 0.0},
        Particle{2, 0.5, 5.5, 0.0},
        Particle{3, 5.5, 5.5, 0.0},
        Particle{4, 9.5, 9.5, 0.0},
    };
    const auto cim = cell_index_neighbors(particles, parameters);
    for (const auto& list : cim) {
        assert(list.empty());
    }
    compare_cim_vs_bruteforce(particles, parameters, "particles_in_far_cells");
}

// 11. Simetría, ausencia de auto-vecinos y ausencia de duplicados en el CIM.
void test_cim_symmetry_no_self_no_duplicates() {
    const Parameters parameters;
    const auto particles = generate_random_particles(60, 777, parameters.box_length);
    const auto cim = cell_index_neighbors(particles, parameters);

    for (std::size_t i = 0; i < particles.size(); ++i) {
        // sin auto-vecinos
        for (const auto id : cim[i]) {
            assert(id != particles[i].id);
        }
        // sin duplicados (lista ordenada estrictamente creciente)
        for (std::size_t k = 1; k < cim[i].size(); ++k) {
            assert(cim[i][k - 1] < cim[i][k]);
        }
        // simetria: si j aparece como vecino de i, i aparece como vecino de j
        for (const auto neighbor_id : cim[i]) {
            const auto it = std::find_if(particles.begin(), particles.end(),
                                          [neighbor_id](const Particle& p) {
                                              return p.id == neighbor_id;
                                          });
            assert(it != particles.end());
            const std::size_t j = static_cast<std::size_t>(it - particles.begin());
            const auto& back = cim[j];
            assert(std::find(back.begin(), back.end(), particles[i].id) != back.end());
        }
    }
}

// 12. Distintos órdenes de almacenamiento: los resultados deben coincidir al
// asociar cada lista con el ID de su partícula.
void test_order_independence() {
    const Parameters parameters;
    auto particles = generate_random_particles(40, 2024, parameters.box_length);

    const auto cim_original = cell_index_neighbors(particles, parameters);
    const auto bruteforce_original = brute_force_neighbors(particles, parameters);

    // Construir un mapa id -> lista de vecinos (ids), a partir del orden original.
    std::vector<std::pair<std::size_t, std::vector<std::size_t>>> expected;
    expected.reserve(particles.size());
    for (std::size_t i = 0; i < particles.size(); ++i) {
        expected.emplace_back(particles[i].id, cim_original[i]);
    }

    // Permutar el vector de partículas (orden inverso + rotación) y recalcular.
    std::vector<Particle> shuffled(particles.rbegin(), particles.rend());
    std::rotate(shuffled.begin(), shuffled.begin() + shuffled.size() / 3, shuffled.end());

    const auto cim_shuffled = cell_index_neighbors(shuffled, parameters);
    const auto bruteforce_shuffled = brute_force_neighbors(shuffled, parameters);
    expect_same_neighbors(bruteforce_shuffled, cim_shuffled, shuffled,
                           "order_independence_shuffled");

    for (std::size_t i = 0; i < shuffled.size(); ++i) {
        const std::size_t id = shuffled[i].id;
        const auto match = std::find_if(
            expected.begin(), expected.end(),
            [id](const std::pair<std::size_t, std::vector<std::size_t>>& entry) {
                return entry.first == id;
            });
        assert(match != expected.end());
        if (match->second != cim_shuffled[i]) {
            std::cerr << "[order_independence] resultado distinto para id=" << id
                      << " al cambiar el orden de almacenamiento" << std::endl;
            std::abort();
        }
    }
}

// 13. Varios tamaños pequeños de sistema, incluidos casos degenerados.
void test_various_small_system_sizes() {
    const Parameters parameters;
    const std::vector<std::size_t> sizes{0, 1, 2, 3, 5, 8, 13, 21, 50};
    for (const std::size_t n : sizes) {
        for (unsigned seed = 1; seed <= 3; ++seed) {
            const auto particles = generate_random_particles(n, seed * 1000 + static_cast<unsigned>(n),
                                                               parameters.box_length);
            compare_cim_vs_bruteforce(
                particles, parameters,
                "size_" + std::to_string(n) + "_seed_" + std::to_string(seed));
        }
    }
}

}  // namespace

int main() {
    test_many_small_random_states_fixed_seeds();
    test_random_uniform_moderate_size();
    test_cross_periodic_border_x();
    test_cross_periodic_border_y();
    test_cross_periodic_corner();
    test_pairs_exactly_at_radius();
    test_pairs_just_outside_radius();
    test_several_particles_in_same_cell();
    test_particles_in_neighboring_cells();
    test_particles_in_far_cells();
    test_cim_symmetry_no_self_no_duplicates();
    test_order_independence();
    test_various_small_system_sizes();
    std::cout << "test_neighbor_search_cim: todos los casos OK" << std::endl;
    return 0;
}
