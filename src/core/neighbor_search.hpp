#pragma once

#include "core/model.hpp"
#include "core/periodic_geometry.hpp"

#include <algorithm>
#include <cstddef>
#include <unordered_set>
#include <vector>

namespace tp2 {

// Búsqueda de vecinos externos por fuerza bruta O(N^2). Sirve como oráculo de
// referencia para validar el Cell Index Method (etapa 3); no es el motor de
// producción.
//
// Supuestos documentados:
// - El resultado está indexado por posición dentro de `particles` (índice de
//   vector, no `id`), pero cada entrada contiene los `id` estables de los
//   vecinos, no índices de vector. Para comparar dos entradas construidas con
//   distinto orden de partículas, primero hay que asociar cada lista con el
//   `id` de su partícula correspondiente.
// - Los `id` de `particles` deben ser únicos; no se deduplican ids repetidos.
// - Un par (i, j) es vecino si `d_ij <= rc` (borde inclusive), usando la
//   distancia mínima periódica de `periodic_geometry.hpp`. Se compara
//   siempre distancia al cuadrado contra `rc^2`, sin usar `sqrt`.
// - La partícula `i` nunca aparece como vecina de sí misma.
// - Las listas resultantes son simétricas por construcción: cada par válido
//   se agrega una única vez a ambas listas, así que no hay duplicados.
// - Los vecinos de cada partícula se devuelven ordenados por `id` para que
//   el resultado sea determinista y comparable directamente entre
//   ejecuciones o contra el CIM.
inline std::vector<std::vector<std::size_t>> brute_force_neighbors(
    const std::vector<Particle>& particles, const Parameters& parameters) {
    const std::size_t count = particles.size();
    std::vector<std::vector<std::size_t>> neighbors(count);

    const double radius = parameters.interaction_radius;
    const double radius_squared = radius * radius;

    for (std::size_t i = 0; i < count; ++i) {
        for (std::size_t j = i + 1; j < count; ++j) {
            const double d2 = distance_squared_periodic(
                particles[i], particles[j], parameters.box_length);
            if (d2 <= radius_squared) {
                neighbors[i].push_back(particles[j].id);
                neighbors[j].push_back(particles[i].id);
            }
        }
    }

    for (auto& list : neighbors) {
        std::sort(list.begin(), list.end());
    }

    return neighbors;
}

// Cell Index Method (CIM): misma interfaz conceptual y mismo significado de
// salida que `brute_force_neighbors`, pero evita el recorrido O(N^2)
// agrupando partículas en una grilla de celdas cuadradas y solo comparando
// pares que caen en celdas vecinas (incluida la propia celda).
//
// Diseño de la grilla:
// - Número de celdas por lado: `M = floor(L / rc)`, con mínimo 1. El tamaño
//   de celda resultante es `cell_size = L / M`, que por construcción cumple
//   `cell_size >= rc`. Esa cota es la que garantiza que ningún par con
//   `d <= rc` pueda quedar fuera de la vecindad de 3x3 celdas (incluida la
//   celda propia) alrededor de cada partícula: si dos celdas están a 2 o más
//   pasos de distancia en algún eje, la separación mínima posible entre
//   cualquier par de partículas que contengan es `>= cell_size >= rc`, así
//   que jamás pueden ser vecinas y no hace falta inspeccionarlas.
// - Con `L=10` y `rc=1` (parámetros vinculantes del TP), `M=10` y
//   `cell_size=1.0`. La función queda igualmente definida para otros `L`/`rc`
//   usados en tests pequeños.
// - Asignación de partícula a celda: se repliega la coordenada con
//   `periodic_wrap` y se toma `floor(coordenada / cell_size)`, recortando a
//   `[0, M-1]` por seguridad ante errores de redondeo en el borde exacto.
// - Vecindad de celdas: para cada celda se recorren los 9 desplazamientos
//   `{-1,0,1}x{-1,0,1}`, replegando el índice de celda módulo `M` (borde
//   periódico también en la grilla). Cada par de celdas (o una celda consigo
//   misma) se procesa una única vez: se ignora un vecino cuyo índice lineal
//   sea menor al de la celda actual, y se deduplican índices de celda
//   repetidos (puede ocurrir cuando `M<=2`, donde un mismo vecino se alcanza
//   por más de un desplazamiento). Así se evita tanto procesar un par de
//   celdas dos veces como duplicar vecinos.
// - Dentro de una celda consigo misma se comparan todos los pares `a<b` de su
//   bucket; entre dos celdas distintas se comparan todos los pares
//   producto. En ambos casos el criterio de vecindad es idéntico al de
//   `brute_force_neighbors`: distancia mínima periódica al cuadrado
//   (`distance_squared_periodic`, sin `sqrt`) comparada con `rc^2`, inclusive
//   en el borde (`d <= rc`).
//
// Complejidad esperada: con partículas distribuidas aproximadamente
// uniformes, el número esperado de partículas por celda es `rho * cell_size^2`,
// una constante independiente de `N` para parámetros fijos. Eso deja el
// costo total en `O(N)` esperado (frente a `O(N^2)` de la fuerza bruta),
// aunque el peor caso degenera a `O(N^2)` si todas las partículas caen en la
// misma celda.
//
// Supuestos (idénticos a `brute_force_neighbors`, documentados de nuevo aquí
// porque esta función es un algoritmo distinto, no una reutilización directa):
// - El resultado está indexado por posición dentro de `particles`, no por
//   `id`; cada entrada contiene los `id` estables de los vecinos.
// - Los `id` de `particles` deben ser únicos.
// - No se modifica ni se reutiliza el estado de `brute_force_neighbors`; es
//   una implementación independiente pensada para producir exactamente el
//   mismo resultado, verificado por test.
inline std::vector<std::vector<std::size_t>> cell_index_neighbors(
    const std::vector<Particle>& particles, const Parameters& parameters) {
    const std::size_t count = particles.size();
    std::vector<std::vector<std::size_t>> neighbors(count);
    if (count == 0) {
        return neighbors;
    }

    const double box_length = parameters.box_length;
    const double radius = parameters.interaction_radius;
    const double radius_squared = radius * radius;

    long grid_size = static_cast<long>(box_length / radius);
    if (grid_size < 1) {
        grid_size = 1;
    }
    const double cell_size = box_length / static_cast<double>(grid_size);

    auto cell_coordinate_for = [&](double coordinate) -> long {
        const double wrapped = periodic_wrap(coordinate, box_length);
        long index = static_cast<long>(wrapped / cell_size);
        if (index < 0) {
            index = 0;
        }
        if (index >= grid_size) {
            index = grid_size - 1;
        }
        return index;
    };

    auto wrap_cell_index = [&](long index) -> long {
        long wrapped = index % grid_size;
        if (wrapped < 0) {
            wrapped += grid_size;
        }
        return wrapped;
    };

    auto linear_cell_index = [&](long cell_x, long cell_y) -> long {
        return cell_y * grid_size + cell_x;
    };

    std::vector<std::vector<std::size_t>> cell_buckets(
        static_cast<std::size_t>(grid_size) * static_cast<std::size_t>(grid_size));

    for (std::size_t i = 0; i < count; ++i) {
        const long cell_x = cell_coordinate_for(particles[i].x);
        const long cell_y = cell_coordinate_for(particles[i].y);
        cell_buckets[static_cast<std::size_t>(linear_cell_index(cell_x, cell_y))]
            .push_back(i);
    }

    auto evaluate_pair = [&](std::size_t i, std::size_t j) {
        const double d2 =
            distance_squared_periodic(particles[i], particles[j], box_length);
        if (d2 <= radius_squared) {
            neighbors[i].push_back(particles[j].id);
            neighbors[j].push_back(particles[i].id);
        }
    };

    for (long cell_y = 0; cell_y < grid_size; ++cell_y) {
        for (long cell_x = 0; cell_x < grid_size; ++cell_x) {
            const long self_linear = linear_cell_index(cell_x, cell_y);
            const auto& self_bucket =
                cell_buckets[static_cast<std::size_t>(self_linear)];
            if (self_bucket.empty()) {
                continue;
            }

            std::unordered_set<long> processed_neighbor_cells;
            for (long delta_y = -1; delta_y <= 1; ++delta_y) {
                for (long delta_x = -1; delta_x <= 1; ++delta_x) {
                    const long neighbor_x = wrap_cell_index(cell_x + delta_x);
                    const long neighbor_y = wrap_cell_index(cell_y + delta_y);
                    const long neighbor_linear =
                        linear_cell_index(neighbor_x, neighbor_y);

                    if (neighbor_linear < self_linear) {
                        continue;
                    }
                    if (!processed_neighbor_cells.insert(neighbor_linear).second) {
                        continue;
                    }

                    if (neighbor_linear == self_linear) {
                        for (std::size_t a = 0; a < self_bucket.size(); ++a) {
                            for (std::size_t b = a + 1; b < self_bucket.size(); ++b) {
                                evaluate_pair(self_bucket[a], self_bucket[b]);
                            }
                        }
                    } else {
                        const auto& other_bucket = cell_buckets[static_cast<std::size_t>(
                            neighbor_linear)];
                        for (const std::size_t a : self_bucket) {
                            for (const std::size_t b : other_bucket) {
                                evaluate_pair(a, b);
                            }
                        }
                    }
                }
            }
        }
    }

    for (auto& list : neighbors) {
        std::sort(list.begin(), list.end());
    }

    return neighbors;
}

}  // namespace tp2
