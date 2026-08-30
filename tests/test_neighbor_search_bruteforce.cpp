#include "core/neighbor_search.hpp"
#include "core/model.hpp"

#include <algorithm>
#include <cassert>
#include <cstddef>
#include <vector>

namespace {

using tp2::Parameters;
using tp2::Particle;
using tp2::brute_force_neighbors;

bool contains(const std::vector<std::size_t>& list, std::size_t id) {
    return std::find(list.begin(), list.end(), id) != list.end();
}

bool is_sorted_unique(const std::vector<std::size_t>& list) {
    for (std::size_t k = 1; k < list.size(); ++k) {
        if (list[k - 1] >= list[k]) {
            return false;
        }
    }
    return true;
}

// 1. Dos partículas separadas por menos de rc: deben ser vecinas.
void test_pair_closer_than_radius() {
    const Parameters parameters;
    const std::vector<Particle> particles{
        Particle{0, 5.0, 5.0, 0.0},
        Particle{1, 5.5, 5.0, 0.0},  // distancia 0.5 < rc=1
    };
    const auto neighbors = brute_force_neighbors(particles, parameters);
    assert(contains(neighbors[0], 1));
    assert(contains(neighbors[1], 0));
}

// 2. Dos partículas separadas exactamente por rc: el borde es inclusive.
void test_pair_exactly_at_radius() {
    const Parameters parameters;
    const std::vector<Particle> particles{
        Particle{0, 5.0, 5.0, 0.0},
        Particle{1, 6.0, 5.0, 0.0},  // distancia 1.0 == rc
    };
    const auto neighbors = brute_force_neighbors(particles, parameters);
    assert(contains(neighbors[0], 1));
    assert(contains(neighbors[1], 0));
}

// 3. Dos partículas separadas por más de rc: no deben ser vecinas.
void test_pair_farther_than_radius() {
    const Parameters parameters;
    const std::vector<Particle> particles{
        Particle{0, 5.0, 5.0, 0.0},
        Particle{1, 6.0 + 1e-9, 5.0, 0.0},  // distancia > rc
    };
    const auto neighbors = brute_force_neighbors(particles, parameters);
    assert(!contains(neighbors[0], 1));
    assert(!contains(neighbors[1], 0));
}

// 4. Dos partículas vecinas cruzando el borde periódico (eje x).
void test_pair_neighbors_across_periodic_border() {
    const Parameters parameters;
    const std::vector<Particle> particles{
        Particle{0, 0.1, 5.0, 0.0},
        Particle{1, 9.9, 5.0, 0.0},  // distancia mínima periódica = 0.2 < rc
    };
    const auto neighbors = brute_force_neighbors(particles, parameters);
    assert(contains(neighbors[0], 1));
    assert(contains(neighbors[1], 0));
}

// 5. Dos partículas que no son vecinas (separación grande, sin borde).
void test_pair_not_neighbors() {
    const Parameters parameters;
    const std::vector<Particle> particles{
        Particle{0, 1.0, 1.0, 0.0},
        Particle{1, 8.0, 8.0, 0.0},
    };
    const auto neighbors = brute_force_neighbors(particles, parameters);
    assert(neighbors[0].empty());
    assert(neighbors[1].empty());
}

// 6. Varias partículas: verificación de simetría completa.
void test_symmetry_with_several_particles() {
    const Parameters parameters;
    const std::vector<Particle> particles{
        Particle{0, 1.0, 1.0, 0.0}, Particle{1, 1.5, 1.0, 0.0},
        Particle{2, 5.0, 5.0, 0.0}, Particle{3, 5.3, 5.2, 0.0},
        Particle{4, 9.8, 1.0, 0.0}, Particle{5, 0.1, 1.0, 0.0},
    };
    const auto neighbors = brute_force_neighbors(particles, parameters);

    for (std::size_t i = 0; i < particles.size(); ++i) {
        for (const std::size_t neighbor_id : neighbors[i]) {
            const auto it = std::find_if(
                particles.begin(), particles.end(),
                [neighbor_id](const Particle& p) { return p.id == neighbor_id; });
            assert(it != particles.end());
            const std::size_t j = static_cast<std::size_t>(it - particles.begin());
            assert(contains(neighbors[j], particles[i].id));
        }
    }
}

// 7. Ninguna partícula aparece como vecina de sí misma.
void test_no_self_neighbor() {
    const Parameters parameters;
    const std::vector<Particle> particles{
        Particle{0, 5.0, 5.0, 0.0},
        Particle{1, 5.0, 5.0, 0.0},  // misma posición, distancia 0
        Particle{2, 9.0, 9.0, 0.0},
    };
    const auto neighbors = brute_force_neighbors(particles, parameters);
    for (std::size_t i = 0; i < particles.size(); ++i) {
        assert(!contains(neighbors[i], particles[i].id));
    }
}

// 8. No hay vecinos duplicados en ninguna lista.
void test_no_duplicate_neighbors() {
    const Parameters parameters;
    const std::vector<Particle> particles{
        Particle{0, 5.0, 5.0, 0.0}, Particle{1, 5.2, 5.0, 0.0},
        Particle{2, 5.4, 5.0, 0.0}, Particle{3, 4.8, 5.0, 0.0},
    };
    const auto neighbors = brute_force_neighbors(particles, parameters);
    for (const auto& list : neighbors) {
        assert(is_sorted_unique(list));
    }
}

// 9. Comparación con una construcción manual conocida (cadena A-B-C, D aislada).
void test_matches_manual_construction() {
    const Parameters parameters;
    const std::vector<Particle> particles{
        Particle{0, 1.0, 1.0, 0.0},  // A
        Particle{1, 1.8, 1.0, 0.0},  // B, dist(A,B)=0.8 < rc
        Particle{2, 2.6, 1.0, 0.0},  // C, dist(B,C)=0.8 < rc, dist(A,C)=1.6 > rc
        Particle{3, 8.0, 8.0, 0.0},  // D, aislada
    };
    const auto neighbors = brute_force_neighbors(particles, parameters);

    const std::vector<std::size_t> expected_a{1};
    const std::vector<std::size_t> expected_b{0, 2};
    const std::vector<std::size_t> expected_c{1};
    const std::vector<std::size_t> expected_d{};

    assert(neighbors[0] == expected_a);
    assert(neighbors[1] == expected_b);
    assert(neighbors[2] == expected_c);
    assert(neighbors[3] == expected_d);
}

// 10. Partículas que cruzan una esquina periódica.
void test_pair_neighbors_across_periodic_corner() {
    const Parameters parameters;
    const std::vector<Particle> particles{
        Particle{0, 0.1, 0.1, 0.0},
        Particle{1, 9.9, 9.9, 0.0},  // distancia mínima periódica: dx=dy=0.2
    };
    const auto neighbors = brute_force_neighbors(particles, parameters);
    // d^2 = 0.2^2 + 0.2^2 = 0.08 < rc^2 = 1
    assert(contains(neighbors[0], 1));
    assert(contains(neighbors[1], 0));
}

// Determinismo: dos llamadas con las mismas partículas dan el mismo resultado.
void test_deterministic_result() {
    const Parameters parameters;
    const std::vector<Particle> particles{
        Particle{0, 1.0, 1.0, 0.0}, Particle{1, 1.5, 1.0, 0.0},
        Particle{2, 5.0, 5.0, 0.0}, Particle{3, 5.3, 5.2, 0.0},
    };
    const auto first_run = brute_force_neighbors(particles, parameters);
    const auto second_run = brute_force_neighbors(particles, parameters);
    assert(first_run == second_run);
}

}  // namespace

int main() {
    test_pair_closer_than_radius();
    test_pair_exactly_at_radius();
    test_pair_farther_than_radius();
    test_pair_neighbors_across_periodic_border();
    test_pair_not_neighbors();
    test_symmetry_with_several_particles();
    test_no_self_neighbor();
    test_no_duplicate_neighbors();
    test_matches_manual_construction();
    test_pair_neighbors_across_periodic_corner();
    test_deterministic_result();
}
