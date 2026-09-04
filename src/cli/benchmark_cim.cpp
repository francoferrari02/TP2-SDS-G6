// Benchmark aislado del Cell Index Method (etapa 8: comparación con TP1).
//
// Mide EXCLUSIVAMENTE la llamada a `cell_index_neighbors` (reconstrucción de
// celdas + búsqueda de vecinos), sin generación de partículas, sin I/O y sin
// ninguna otra parte del motor (reglas, movimiento, observables). Esto replica
// la metodología de `benchmark.py` del TP1 (`medir_tiempo_busqueda`): las
// partículas se generan una única vez fuera del bucle de repeticiones, y solo
// se cronometra la búsqueda en sí.
//
// Uso: benchmark_cim L rc N repeticiones seed
// Salida (stdout, una línea, CSV): N,tiempo_promedio_s,tiempo_std_s
//
// No se registra en CMakeLists como parte de la suite de tests (no es una
// validación de correctitud): es una herramienta de medición para la etapa 8,
// análoga a benchmark.py mas no un test de CTest.

#include "core/initialization.hpp"
#include "core/model.hpp"
#include "core/neighbor_search.hpp"

#include <chrono>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <numeric>
#include <string>
#include <vector>

int main(int argc, char** argv) {
    if (argc != 6) {
        std::fprintf(stderr, "uso: %s L rc N repeticiones seed\n", argv[0]);
        return 2;
    }

    const double L = std::stod(argv[1]);
    const double rc = std::stod(argv[2]);
    const std::size_t N = std::stoul(argv[3]);
    const int repeticiones = std::stoi(argv[4]);
    const std::uint64_t seed = std::stoull(argv[5]);

    tp2::Parameters params;
    params.box_length = L;
    params.interaction_radius = rc;

    // Generación fuera del bucle cronometrado (misma convención que TP1).
    const std::vector<tp2::Particle> particles = tp2::initialize_particles(N, params, seed);

    std::vector<double> tiempos(static_cast<std::size_t>(repeticiones));
    std::size_t total_vecinos_ultima = 0;

    for (int r = 0; r < repeticiones; ++r) {
        const auto t0 = std::chrono::steady_clock::now();
        const auto vecinos = tp2::cell_index_neighbors(particles, params);
        const auto t1 = std::chrono::steady_clock::now();
        tiempos[static_cast<std::size_t>(r)] = std::chrono::duration<double>(t1 - t0).count();

        // Evita que el compilador optimice la llamada como muerta.
        total_vecinos_ultima = 0;
        for (const auto& lista : vecinos) {
            total_vecinos_ultima += lista.size();
        }
    }

    const double media =
        std::accumulate(tiempos.begin(), tiempos.end(), 0.0) / static_cast<double>(repeticiones);
    double suma_sq = 0.0;
    for (const double t : tiempos) {
        suma_sq += (t - media) * (t - media);
    }
    const double desvio = std::sqrt(suma_sq / static_cast<double>(repeticiones));

    // total_vecinos_ultima se imprime a stderr solo como diagnóstico (numero
    // medio de vecinos), nunca se mezcla con la salida CSV de stdout.
    std::fprintf(stderr, "# N=%zu vecinos_totales_ultima_corrida=%zu mean_k=%.4f\n", N,
                 total_vecinos_ultima, N > 0 ? static_cast<double>(total_vecinos_ultima) / static_cast<double>(N) : 0.0);

    std::printf("%zu,%.9f,%.9f\n", N, media, desvio);
    return 0;
}
