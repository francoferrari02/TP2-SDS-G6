// CLI productiva del motor: parsea argumentos, corre una simulacion en
// memoria y escribe `observables.csv` (siempre) y `trajectory.csv` (solo si
// se pide `--write-trajectory`), segun el contrato aprobado en
// `plan_desarrollo_tp2/DECISIONES_PENDIENTES.md`.
//
// Toda la logica reutilizable (parseo/validacion de argumentos, ejecucion y
// escritura) vive en `cli/simulate_cli.hpp` para que los tests puedan
// llamarla directamente sin pasar por un subproceso; este archivo es
// deliberadamente un `main()` fino.

#include "cli/simulate_cli.hpp"

#include <iostream>
#include <string>
#include <vector>

int main(int argc, char** argv) {
    std::vector<std::string> args;
    args.reserve(static_cast<std::size_t>(argc > 0 ? argc - 1 : 0));
    for (int i = 1; i < argc; ++i) {
        args.emplace_back(argv[i]);
    }

    const tp2::cli::ParseResult parsed = tp2::cli::parse_arguments(args);
    if (!parsed.ok) {
        std::cerr << "Error de argumentos: " << parsed.error << "\n";
        return 2;
    }

    const tp2::cli::RunOutcome outcome = tp2::cli::execute_run(parsed.request);
    if (!outcome.ok) {
        std::cerr << "Error: " << outcome.error << "\n";
        return 1;
    }

    std::cout << "OK: corrida escrita en " << outcome.run_directory.string() << "\n";
    std::cout << "  observables: " << outcome.observables_path.string() << " (" << outcome.observables_rows
              << " filas)\n";
    if (!outcome.trajectory_path.empty()) {
        std::cout << "  trayectoria: " << outcome.trajectory_path.string() << " (" << outcome.trajectory_rows
                  << " filas)\n";
    } else {
        std::cout << "  trayectoria: no escrita (usar --write-trajectory para activarla)\n";
    }

    return 0;
}
