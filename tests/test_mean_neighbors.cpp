// Validación estadística: número medio inicial de vecinos externos vs. la
// predicción teórica rho*pi*rc^2 para posiciones uniformes en una caja
// periódica. No mide comportamiento dinámico: solo inicialización + CIM.
//
// Alcance: ver plan_desarrollo_tp2/03_validaciones.md, sección "3. Número
// medio inicial de vecinos". No modifica el motor ni la búsqueda de vecinos.
//
// Las posiciones iniciales ya no se generan con una función propia de este
// archivo: se usa el inicializador productivo `tp2::initialize_particles`
// (`src/core/initialization.hpp`), el mismo que usará la simulación, para
// que esta validación y el motor nunca diverjan en cómo arranca el estado.

#include "core/model.hpp"
#include "core/initialization.hpp"
#include "core/neighbor_search.hpp"

#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <iomanip>
#include <iostream>
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

// Promedio global de vecinos externos por partícula, sobre `realizations`
// inicializaciones uniformes independientes (una semilla explícita por
// realización, derivada de `seed_offset + realization_index`).
double measure_mean_neighbors(std::size_t particle_count, const tp2::Parameters& parameters,
                               std::size_t realizations, std::uint64_t seed_offset) {
    double total_neighbors = 0.0;
    std::size_t total_particles = 0;

    for (std::size_t realization = 0; realization < realizations; ++realization) {
        const std::uint64_t seed = seed_offset + static_cast<std::uint64_t>(realization);
        const std::vector<tp2::Particle> particles =
            tp2::initialize_particles(particle_count, parameters, seed);

        const std::vector<std::vector<std::size_t>> neighbors =
            tp2::cell_index_neighbors(particles, parameters);

        for (const auto& list : neighbors) {
            total_neighbors += static_cast<double>(list.size());
        }
        total_particles += particles.size();
    }

    return total_neighbors / static_cast<double>(total_particles);
}

struct DensityCase {
    double rho;
    std::size_t particle_count;
    double expected_mean;        // aproximacion de la catedra: rho*pi*rc^2
    double expected_mean_exact;  // expectativa finita exacta: (N-1)*pi*rc^2/L^2
};

}  // namespace

int main() {
    tp2::Parameters parameters;
    parameters.box_length = 10.0;
    parameters.interaction_radius = 1.0;

    // aproximada = rho*pi*rc^2, con rc=1: 2*pi, 4*pi, 8*pi.
    // finita exacta = (N-1)*pi*rc^2/L^2, con L=10, rc=1.
    const std::vector<DensityCase> cases = {
        {2.0, 200, 2.0 * kPi, 199.0 * kPi / 100.0},
        {4.0, 400, 4.0 * kPi, 399.0 * kPi / 100.0},
        {8.0, 800, 8.0 * kPi, 799.0 * kPi / 100.0},
    };

    // Cantidad de realizaciones independientes por densidad y semilla base
    // por densidad (registradas para trazabilidad, no elegidas ad hoc por
    // caso). Cada realización usa la semilla `seed_base + realization_index`.
    constexpr std::size_t kRealizations = 40;
    constexpr std::uint64_t kSeedBaseRho2 = 100000;
    constexpr std::uint64_t kSeedBaseRho4 = 200000;
    constexpr std::uint64_t kSeedBaseRho8 = 300000;
    const std::vector<std::uint64_t> seed_bases = {kSeedBaseRho2, kSeedBaseRho4, kSeedBaseRho8};

    // Tolerancia de validación empírica (no un requisito de la cátedra): con
    // N particulas y `kRealizations` realizaciones independientes, el error
    // estándar del promedio de vecinos escala aproximadamente como
    // sqrt(<k>/(N*realizations)). Para el caso más chico (rho=2, N=200,
    // <k>~6.28) eso da ~0.028; se toma un margen generoso de 10 desvíos
    // estándar (~0.3) para evitar falsos negativos por fluctuación
    // estadística, mientras que un error de geometría/periodicidad/radio
    // produce desvíos de order 1 o mayores, muy por encima de esta banda.
    constexpr double kRelativeTolerance = 0.05;  // 5% del valor teórico

    std::vector<double> measured_means;
    measured_means.reserve(cases.size());

    std::cout << std::fixed << std::setprecision(3);
    for (std::size_t i = 0; i < cases.size(); ++i) {
        const DensityCase& density_case = cases[i];
        const double measured = measure_mean_neighbors(density_case.particle_count, parameters,
                                                         kRealizations, seed_bases[i]);
        measured_means.push_back(measured);

        std::cout << "rho=" << static_cast<int>(density_case.rho)
                   << "  N=" << density_case.particle_count
                   << "  expected_approx=" << density_case.expected_mean
                   << "  expected_exact_finite=" << density_case.expected_mean_exact
                   << "  measured=" << measured << "  realizations=" << kRealizations
                   << "  seed_base=" << seed_bases[i] << "\n";

        const double tolerance = kRelativeTolerance * density_case.expected_mean;
        expect_true(std::abs(measured - density_case.expected_mean) <= tolerance,
                    "mean_neighbors_close_to_theory",
                    "rho=" + std::to_string(density_case.rho) +
                        ": el promedio medido se aleja demasiado de rho*pi*rc^2 (posible error "
                        "de geometria, periodicidad, radio o asignacion de vecinos)");
    }

    // Orden estricto entre densidades: el promedio de vecinos debe crecer
    // monótonamente con rho, sin depender de la cercanía numérica al valor
    // teórico.
    expect_true(measured_means[0] < measured_means[1], "mean_neighbors_monotone_rho_2_4",
                "mean_k(rho=2) deberia ser menor que mean_k(rho=4)");
    expect_true(measured_means[1] < measured_means[2], "mean_neighbors_monotone_rho_4_8",
                "mean_k(rho=4) deberia ser menor que mean_k(rho=8)");

    std::cout << "OK: promedio de vecinos externos crece con la densidad y se aproxima a "
                 "rho*pi*rc^2 dentro de la tolerancia de validacion empirica ("
              << (kRelativeTolerance * 100.0) << "%).\n";

    return 0;
}
