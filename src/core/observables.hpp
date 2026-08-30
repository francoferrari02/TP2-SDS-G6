#pragma once

#include "core/model.hpp"

#include <cmath>
#include <cstddef>
#include <numeric>
#include <unordered_map>
#include <utility>
#include <vector>

namespace tp2 {

// Polarización `va`: mide qué tan alineadas están las orientaciones, sin usar
// la velocidad (todos los módulos valen `v`, así que dividir por `v` sería
// redundante y solo agregaría error numérico). No modifica `particles`.
//
// Convención para N=0: se documenta y se devuelve 0.0 (no hay bandada que
// alinear; evita dividir por cero).
inline double polarization(const std::vector<Particle>& particles) {
    if (particles.empty()) {
        return 0.0;
    }

    double sum_cos = 0.0;
    double sum_sin = 0.0;
    for (const Particle& particle : particles) {
        sum_cos += std::cos(particle.theta);
        sum_sin += std::sin(particle.theta);
    }

    return std::hypot(sum_cos, sum_sin) / static_cast<double>(particles.size());
}

namespace detail {

// Union-Find (Disjoint Set Union) con compresión de camino y unión por
// rango. Se eligió por sobre BFS/DFS porque la entrada ya es una lista de
// aristas (par de vecinos) en vez de un grafo de adyacencia que convenga
// recorrer nodo por nodo; con DSU cada arista se procesa una sola vez, en
// O(alpha(N)) amortizado, sin necesitar pilas ni colas auxiliares.
class DisjointSet {
public:
    explicit DisjointSet(std::size_t count) : parent_(count), rank_(count, 0) {
        std::iota(parent_.begin(), parent_.end(), 0);
    }

    std::size_t find(std::size_t node) {
        while (parent_[node] != node) {
            parent_[node] = parent_[parent_[node]];
            node = parent_[node];
        }
        return node;
    }

    void unite(std::size_t a, std::size_t b) {
        a = find(a);
        b = find(b);
        if (a == b) {
            return;
        }
        if (rank_[a] < rank_[b]) {
            std::swap(a, b);
        }
        parent_[b] = a;
        if (rank_[a] == rank_[b]) {
            ++rank_[a];
        }
    }

private:
    std::vector<std::size_t> parent_;
    std::vector<std::size_t> rank_;
};

}  // namespace detail

// Tamaño del cluster (componente conexa) más grande de la red de vecinos.
//
// `neighbors[i]` contiene los `id` de los vecinos de `particles[i]`, tal
// como los devuelven `brute_force_neighbors`/`cell_index_neighbors` (que ya
// aplican el criterio periódico `d <= rc`); esta función no vuelve a calcular
// distancias, solo recorre las aristas ya dadas.
//
// Tratamiento de IDs: `neighbors` está indexado por posición de vector (como
// `particles`), pero su contenido son `id`, que pueden no ser consecutivos ni
// coincidir con la posición. Se construye un mapa `id -> índice` antes de
// unir componentes, igual que en `rules.hpp`, para no asumir `id == índice`.
//
// Convención para N=0: se documenta y se devuelve 0 (no hay cluster).
inline std::size_t largest_cluster_size(
    const std::vector<std::vector<std::size_t>>& neighbors,
    const std::vector<Particle>& particles) {
    const std::size_t count = particles.size();
    if (count == 0) {
        return 0;
    }

    std::unordered_map<std::size_t, std::size_t> id_to_index;
    id_to_index.reserve(count);
    for (std::size_t index = 0; index < count; ++index) {
        id_to_index.emplace(particles[index].id, index);
    }

    detail::DisjointSet components(count);
    for (std::size_t i = 0; i < count; ++i) {
        for (const std::size_t neighbor_id : neighbors[i]) {
            const std::size_t j = id_to_index.at(neighbor_id);
            components.unite(i, j);
        }
    }

    std::unordered_map<std::size_t, std::size_t> component_size;
    component_size.reserve(count);
    std::size_t largest = 0;
    for (std::size_t i = 0; i < count; ++i) {
        const std::size_t root = components.find(i);
        const std::size_t size = ++component_size[root];
        if (size > largest) {
            largest = size;
        }
    }

    return largest;
}

// Fracción `S = n_max / N` contenida en el cluster más grande.
//
// Convención para N=0: se documenta y se devuelve 0.0.
inline double largest_cluster_fraction(
    const std::vector<std::vector<std::size_t>>& neighbors,
    const std::vector<Particle>& particles) {
    if (particles.empty()) {
        return 0.0;
    }
    return static_cast<double>(largest_cluster_size(neighbors, particles)) /
           static_cast<double>(particles.size());
}

}  // namespace tp2
