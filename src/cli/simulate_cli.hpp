#pragma once

#include "core/initialization.hpp"
#include "core/model.hpp"
#include "core/neighbor_search.hpp"
#include "core/observables.hpp"
#include "core/simulation.hpp"
#include "core/text_output.hpp"
#include "core/time_step.hpp"

#include <algorithm>
#include <cctype>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <filesystem>
#include <fstream>
#include <ios>
#include <limits>
#include <locale>
#include <ostream>
#include <sstream>
#include <string>
#include <system_error>
#include <utility>
#include <vector>

namespace tp2::cli {

// Interfaz productiva de línea de comandos para una corrida, equivalente a:
//
//   simulate
//     --model vicsek|voter
//     --rho-nominal RHO
//     --rho-label LABEL
//     --N N
//     --eta ETA
//     --steps T
//     --base-seed SEED
//     --realization R
//     --output-dir PATH
//     [--write-trajectory]
//     [--observables-stride K]
//     [--trajectory-stride K]
//     [--overwrite]
//
// `L`, `rc`, `dt` y `v` no son opciones de la CLI: son las "reglas que no se
// negocian" del TP (`L=10`, `rc=1`, `dt=1`, `v=0.03`, ver
// `plan_desarrollo_tp2/README.md`), así que se usan los valores por defecto
// de `Parameters` sin exponerlos como parámetros configurables.
//
// Este archivo separa dos responsabilidades para que ambas sean testeables
// sin pasar por un subproceso ni por el sistema de archivos real en cada
// caso:
// - `parse_arguments`: solo interpreta y valida los argumentos (tipos,
//   signos, densidades obligatorias). No toca disco ni corre nada.
// - `execute_run`: dado un `RunRequest` ya válido, corre la simulación en
//   memoria (reutilizando `initialize_particles`, `run_simulation`,
//   `cell_index_neighbors`, `polarization`, `largest_cluster_fraction`) y
//   escribe los archivos según el contrato de
//   `plan_desarrollo_tp2/DECISIONES_PENDIENTES.md`.

struct RunRequest {
    InteractionRule rule = InteractionRule::kVicsek;
    std::string model_name;  // "vicsek" o "voter": exactamente lo que pidió el usuario.
    double rho_nominal = 0.0;
    std::string rho_label;
    std::size_t particle_count = 0;  // N
    double eta = 0.0;
    std::size_t steps = 0;
    std::uint64_t base_seed = 0;
    std::size_t realization = 0;
    std::filesystem::path output_dir;
    bool write_trajectory = false;
    std::size_t observables_stride = 1;
    std::size_t trajectory_stride = 1;
    bool overwrite = false;
};

struct ParseResult {
    bool ok = false;
    RunRequest request;
    std::string error;
};

namespace detail {

inline bool parse_non_negative_integer(const std::string& text, unsigned long long& out) {
    if (text.empty() || text[0] == '-') {
        return false;
    }
    try {
        std::size_t consumed = 0;
        const unsigned long long value = std::stoull(text, &consumed);
        if (consumed != text.size()) {
            return false;
        }
        out = value;
        return true;
    } catch (...) {
        return false;
    }
}

inline bool parse_double_value(const std::string& text, double& out) {
    if (text.empty()) {
        return false;
    }
    try {
        std::size_t consumed = 0;
        const double value = std::stod(text, &consumed);
        if (consumed != text.size()) {
            return false;
        }
        out = value;
        return true;
    } catch (...) {
        return false;
    }
}

// Etiqueta segura para usar como componente de ruta (`--rho-label`): no
// vacía, no "." ni "..", y compuesta únicamente por letras, dígitos, '_' o
// '-'. Al no permitir '.' en absoluto, esto ya excluye "." y ".." (y
// cualquier secuencia de escape de directorio tipo "../algo") sin necesitar
// un chequeo aparte; tampoco permite '/' ni '\\' (separadores de ruta) ni
// espacios. Es intencionalmente una lista blanca, no una lista negra: es
// más fácil razonar sobre "solo estos caracteres son válidos" que enumerar
// todos los caracteres peligrosos de todos los sistemas de archivos.
inline bool is_safe_path_label(const std::string& text) {
    if (text.empty()) {
        return false;
    }
    for (const char c : text) {
        const auto uc = static_cast<unsigned char>(c);
        if (!(std::isalnum(uc) || c == '_' || c == '-')) {
            return false;
        }
    }
    return true;
}

inline bool nearly_equal(double a, double b, double tolerance) {
    return std::abs(a - b) <= tolerance;
}

// Resultado de escribir un archivo temporal completo (abrir, escribir,
// vaciar el buffer y cerrar), verificando el estado del stream en cada
// paso. No borra nada por su cuenta: quien llama decide qué limpiar si esto
// falla (ver `execute_run`).
struct TempWriteResult {
    bool ok = false;
    std::string error;
};

template <typename WriterFn>
inline TempWriteResult write_temp_file(const std::filesystem::path& tmp_path, WriterFn&& writer) {
    std::ofstream out(tmp_path, std::ios::binary | std::ios::trunc);
    if (!out) {
        return {false, "No se pudo abrir para escritura: " + tmp_path.string()};
    }

    writer(out);
    if (!out) {
        return {false, "Error al escribir en: " + tmp_path.string()};
    }

    out.flush();
    if (!out) {
        return {false, "Error al vaciar el buffer de escritura de: " + tmp_path.string()};
    }

    out.close();
    if (out.fail()) {
        return {false, "Error al cerrar el archivo: " + tmp_path.string()};
    }

    return {true, {}};
}

// Intenta eliminar `path` si existe, sin lanzar. Si `path` no existe, no
// hace nada (no es un error). Si existe pero no se pudo borrar, agrega un
// mensaje a `warnings` en vez de ignorar el error silenciosamente.
inline void remove_if_exists_best_effort(const std::filesystem::path& path,
                                          std::vector<std::string>& warnings) {
    std::error_code ec;
    if (!std::filesystem::exists(path, ec)) {
        return;
    }
    std::filesystem::remove(path, ec);
    if (ec) {
        warnings.push_back("no se pudo limpiar el archivo temporal '" + path.string() +
                            "': " + ec.message());
    }
}

}  // namespace detail

inline ParseResult parse_arguments(const std::vector<std::string>& args) {
    ParseResult result;
    RunRequest& request = result.request;

    bool has_model = false;
    bool has_rho_nominal = false;
    bool has_rho_label = false;
    bool has_n = false;
    bool has_eta = false;
    bool has_steps = false;
    bool has_base_seed = false;
    bool has_realization = false;
    bool has_output_dir = false;
    bool has_observables_stride = false;
    bool has_trajectory_stride = false;

    auto fail = [&](const std::string& message) {
        result.ok = false;
        result.error = message;
        return result;
    };

    for (std::size_t i = 0; i < args.size(); ++i) {
        const std::string& flag = args[i];

        auto next_value = [&](const std::string& flag_name) -> const std::string* {
            if (i + 1 >= args.size()) {
                return nullptr;
            }
            ++i;
            (void)flag_name;
            return &args[i];
        };

        if (flag == "--model") {
            const std::string* value = next_value(flag);
            if (!value) {
                return fail("--model requiere un valor ('vicsek' o 'voter').");
            }
            if (*value != "vicsek" && *value != "voter") {
                return fail("--model debe ser 'vicsek' o 'voter', se recibio: '" + *value + "'.");
            }
            request.model_name = *value;
            request.rule = (*value == "vicsek") ? InteractionRule::kVicsek : InteractionRule::kVoter;
            has_model = true;
        } else if (flag == "--rho-nominal") {
            const std::string* value = next_value(flag);
            double parsed = 0.0;
            if (!value || !detail::parse_double_value(*value, parsed)) {
                return fail("--rho-nominal requiere un numero valido.");
            }
            if (!std::isfinite(parsed)) {
                return fail("--rho-nominal no puede ser NaN ni infinito.");
            }
            if (!(parsed > 0.0)) {
                return fail("--rho-nominal debe ser estrictamente mayor que cero.");
            }
            request.rho_nominal = parsed;
            has_rho_nominal = true;
        } else if (flag == "--rho-label") {
            const std::string* value = next_value(flag);
            if (!value || !detail::is_safe_path_label(*value)) {
                return fail(
                    "--rho-label requiere una etiqueta no vacia, sin '.', '/', '\\' ni espacios "
                    "(solo letras, digitos, '_' y '-').");
            }
            request.rho_label = *value;
            has_rho_label = true;
        } else if (flag == "--N") {
            const std::string* value = next_value(flag);
            unsigned long long parsed = 0;
            if (!value || !detail::parse_non_negative_integer(*value, parsed)) {
                return fail("--N requiere un entero no negativo.");
            }
            request.particle_count = static_cast<std::size_t>(parsed);
            has_n = true;
        } else if (flag == "--eta") {
            const std::string* value = next_value(flag);
            double parsed = 0.0;
            if (!value || !detail::parse_double_value(*value, parsed)) {
                return fail("--eta requiere un numero valido.");
            }
            if (!std::isfinite(parsed)) {
                return fail("--eta no puede ser NaN ni infinito.");
            }
            if (parsed < 0.0) {
                return fail("--eta no puede ser negativo.");
            }
            request.eta = parsed;
            has_eta = true;
        } else if (flag == "--steps") {
            const std::string* value = next_value(flag);
            unsigned long long parsed = 0;
            if (!value || !detail::parse_non_negative_integer(*value, parsed)) {
                return fail("--steps requiere un entero no negativo.");
            }
            request.steps = static_cast<std::size_t>(parsed);
            has_steps = true;
        } else if (flag == "--base-seed") {
            const std::string* value = next_value(flag);
            unsigned long long parsed = 0;
            if (!value || !detail::parse_non_negative_integer(*value, parsed)) {
                return fail("--base-seed requiere un entero no negativo.");
            }
            request.base_seed = static_cast<std::uint64_t>(parsed);
            has_base_seed = true;
        } else if (flag == "--realization") {
            const std::string* value = next_value(flag);
            unsigned long long parsed = 0;
            if (!value || !detail::parse_non_negative_integer(*value, parsed)) {
                return fail("--realization requiere un entero no negativo.");
            }
            request.realization = static_cast<std::size_t>(parsed);
            has_realization = true;
        } else if (flag == "--output-dir") {
            const std::string* value = next_value(flag);
            if (!value || value->empty()) {
                return fail("--output-dir requiere una ruta no vacia.");
            }
            request.output_dir = *value;
            has_output_dir = true;
        } else if (flag == "--write-trajectory") {
            request.write_trajectory = true;
        } else if (flag == "--overwrite") {
            request.overwrite = true;
        } else if (flag == "--observables-stride") {
            const std::string* value = next_value(flag);
            unsigned long long parsed = 0;
            if (!value || !detail::parse_non_negative_integer(*value, parsed)) {
                return fail("--observables-stride requiere un entero no negativo.");
            }
            if (parsed == 0) {
                return fail("--observables-stride debe ser mayor que cero.");
            }
            request.observables_stride = static_cast<std::size_t>(parsed);
            has_observables_stride = true;
        } else if (flag == "--trajectory-stride") {
            const std::string* value = next_value(flag);
            unsigned long long parsed = 0;
            if (!value || !detail::parse_non_negative_integer(*value, parsed)) {
                return fail("--trajectory-stride requiere un entero no negativo.");
            }
            if (parsed == 0) {
                return fail("--trajectory-stride debe ser mayor que cero.");
            }
            request.trajectory_stride = static_cast<std::size_t>(parsed);
            has_trajectory_stride = true;
        } else {
            return fail("Opcion desconocida: '" + flag + "'.");
        }
    }

    if (!has_model) return fail("Falta --model.");
    if (!has_rho_nominal) return fail("Falta --rho-nominal.");
    if (!has_rho_label) return fail("Falta --rho-label.");
    if (!has_n) return fail("Falta --N.");
    if (!has_eta) return fail("Falta --eta.");
    if (!has_steps) return fail("Falta --steps.");
    if (!has_base_seed) return fail("Falta --base-seed.");
    if (!has_realization) return fail("Falta --realization.");
    if (!has_output_dir) return fail("Falta --output-dir.");

    if (!has_observables_stride) {
        request.observables_stride = 1;
    }
    // Trayectoria desactivada por defecto; si se activa sin indicar stride,
    // el contrato pide usar 1.
    if (!has_trajectory_stride) {
        request.trajectory_stride = 1;
    }

    // Para las densidades obligatorias del TP (rho=2,4,8 con L=10) se puede
    // verificar consistencia con N=rho*L^2 (200,400,800). Para cualquier
    // otro rho_nominal (por ejemplo las densidades bajas 1/pi, 1/(2pi),
    // 1/(3pi)) esta verificacion no aplica: ahi rho_nominal != N/L^2 a
    // proposito, y esa conversion sigue siendo una decision abierta (ver
    // plan_desarrollo_tp2/DECISIONES_PENDIENTES.md).
    constexpr double kDefaultBoxLength = 10.0;
    constexpr double kRhoTolerance = 1e-9;
    const double expected_area = kDefaultBoxLength * kDefaultBoxLength;
    for (const double obligatory_rho : {2.0, 4.0, 8.0}) {
        if (detail::nearly_equal(request.rho_nominal, obligatory_rho, kRhoTolerance)) {
            const auto expected_n = static_cast<std::size_t>(obligatory_rho * expected_area);
            if (request.particle_count != expected_n) {
                std::ostringstream message;
                message << "--rho-nominal=" << obligatory_rho << " requiere --N=" << expected_n
                        << " (N=rho*L^2 con L=" << kDefaultBoxLength
                        << "), se recibio --N=" << request.particle_count << ".";
                return fail(message.str());
            }
            break;
        }
    }

    result.ok = true;
    return result;
}

// Formatea `eta` para usarlo como segmento de ruta: sin coma ni punto
// decimal (se reemplaza `.` por `p`, p.ej. `0.5` -> `0p5`, `1` -> `1`).
//
// Usa `std::numeric_limits<double>::max_digits10` (17 dígitos
// significativos), no una precisión fija arbitraria: esa cantidad de
// dígitos es la que garantiza que un `double` se pueda reconstruir
// exactamente al volver a parsear su representación decimal (la misma
// garantía de round-trip que usa `core/text_output.hpp` para los valores
// dentro de los archivos). Como consecuencia, dos `double` distintos
// siempre producen cadenas distintas antes de la sustitución de
// caracteres: con precisión fija baja, dos valores de `eta` muy cercanos
// (por ejemplo separados por `1e-12`) podían truncarse a la misma cadena y
// colisionar en el mismo directorio de salida.
//
// El stream se imbuye con `std::locale::classic()` para que el separador
// decimal sea siempre `.` (nunca `,`), igual que en `text_output.hpp`. La
// sustitución de caracteres es un mapeo fijo, uno a uno, sobre los únicos
// caracteres que puede producir el formato por defecto de un `double`
// (dígitos, `.`, `-`, y opcionalmente `e`/`E` con signo si aparece notación
// científica): `.`/`,` -> `p`; `-` -> `m`; `+` se elimina (el signo `+` del
// exponente es redundante: su ausencia ya indica exponente no negativo, y
// nunca aparece en ninguna otra posición). Ningún caracter de reemplazo
// (`p`, `m`) aparece nunca en la cadena original sin transformar, así que
// esta sustitución no puede fusionar dos representaciones distintas en una
// misma salida. Los metadatos (`# eta=...`, con la misma precisión) siguen
// siendo la fuente de verdad del valor exacto; esta función solo produce un
// nombre de directorio legible y sin colisiones.
inline std::string format_eta_for_path(double eta) {
    std::ostringstream oss;
    oss.imbue(std::locale::classic());
    oss.precision(std::numeric_limits<double>::max_digits10);
    oss << eta;
    const std::string text = oss.str();

    std::string result;
    result.reserve(text.size());
    for (const char c : text) {
        switch (c) {
            case '.':
            case ',':
                result += 'p';
                break;
            case '-':
                result += 'm';
                break;
            case '+':
                break;  // se omite: la ausencia de 'm' ya indica exponente no negativo.
            default:
                result += c;
                break;
        }
    }
    return result;
}

inline std::string format_realization_for_path(std::size_t realization) {
    std::ostringstream oss;
    oss.fill('0');
    oss.width(3);
    oss << realization;
    return oss.str();
}

inline std::filesystem::path compute_run_directory(const RunRequest& request) {
    std::filesystem::path dir = request.output_dir;
    dir /= request.model_name;
    dir /= request.rho_label;
    dir /= ("eta_" + format_eta_for_path(request.eta));
    dir /= ("steps_" + std::to_string(request.steps));
    dir /= ("realization_" + format_realization_for_path(request.realization) + "_seed_" +
            std::to_string(request.base_seed));
    return dir;
}

struct RunOutcome {
    bool ok = false;
    std::string error;
    std::filesystem::path run_directory;
    std::filesystem::path observables_path;
    std::filesystem::path trajectory_path;  // vacio si no se escribio trayectoria
    std::size_t observables_rows = 0;
    std::size_t trajectory_rows = 0;
};

// Ejecuta una corrida completa a partir de un `RunRequest` ya validado por
// `parse_arguments`: corre la simulacion en memoria y escribe
// `observables.csv` (siempre) y `trajectory.csv` (solo si
// `write_trajectory`), respetando el contrato de nombres de directorio,
// metadatos y no-sobrescritura por defecto.
//
// Estrategia de publicacion (garantia de atomicidad obtenida en C++17
// portable, ver tambien `plan_desarrollo_tp2/DECISIONES_PENDIENTES.md`):
// 1. Ambos archivos requeridos se escriben primero completos a `.tmp`,
//    verificando apertura, escritura, `flush` y `close` en cada uno. Si
//    cualquiera de esos pasos falla para cualquiera de los dos archivos,
//    ningun archivo final (`observables.csv`/`trajectory.csv`) se toca: se
//    limpian los `.tmp` que hayan llegado a crearse y se devuelve error.
// 2. Recien despues de que ambos `.tmp` esten completos y verificados, se
//    "publican" con `std::filesystem::rename` (atomico dentro del mismo
//    directorio en los sistemas de archivos POSIX/NTFS habituales: la
//    version final del archivo nunca queda a medio escribir). Se publica
//    primero `trajectory.csv` (si corresponde) y `observables.csv` al
//    final, porque `observables.csv` es la senal de "esta corrida
//    termino" (siempre existe si la corrida tuvo exito): si el rename de
//    la trayectoria fallara, `observables.csv` nunca se publica, así que
//    nunca queda una corrida con observables nuevos pero trayectoria vieja
//    o ausente.
// 3. Limite real de esta estrategia: `std::filesystem::rename` no ofrece
//    una operacion portable en C++17 que renombre *dos* archivos como una
//    unica transaccion atomica. Si el proceso se interrumpe (crash, corte
//    de energia) exactamente entre el rename de `trajectory.csv` y el de
//    `observables.csv`, el directorio podria quedar con una trayectoria
//    nueva pero sin `observables.csv` (o con uno viejo, si fue una
//    sobrescritura). Ese estado se puede reconocer porque falta
//    `observables.csv` o su contenido no corresponde a la ejecucion mas
//    reciente, y se resuelve simplemente volviendo a correr con
//    `--overwrite`. Nunca se informa exito (`RunOutcome::ok=true`) en ese
//    caso: la funcion devuelve error apenas falla el segundo rename.
inline RunOutcome execute_run(const RunRequest& request) {
    namespace fs = std::filesystem;
    RunOutcome outcome;

    const fs::path dir = compute_run_directory(request);
    const fs::path obs_path = dir / "observables.csv";
    const fs::path traj_path = dir / "trajectory.csv";
    const fs::path obs_tmp = dir / "observables.csv.tmp";
    const fs::path traj_tmp = dir / "trajectory.csv.tmp";

    std::error_code ec;

    // Comprobar todos los destinos antes de empezar: si el directorio de la
    // corrida ya existe y no se pidio --overwrite, fallar sin modificar
    // nada (ni siquiera crear el directorio).
    if (!request.overwrite && fs::exists(dir, ec)) {
        outcome.ok = false;
        outcome.error = "El directorio de la corrida ya existe: " + dir.string() +
                         " (use --overwrite para reemplazarlo).";
        return outcome;
    }

    fs::create_directories(dir, ec);
    if (ec) {
        outcome.ok = false;
        outcome.error = "No se pudo crear el directorio '" + dir.string() + "': " + ec.message();
        return outcome;
    }

    Parameters parameters;  // L=10, rc=1, dt=1, v=0.03: valores fijos del TP, no configurables.

    const std::vector<Particle> initial_state =
        initialize_particles(request.particle_count, parameters, request.base_seed);

    const std::size_t steps = request.steps;
    const std::size_t obs_stride = request.observables_stride;
    const std::size_t traj_stride = request.trajectory_stride;
    const bool write_trajectory = request.write_trajectory;

    std::vector<ObservableRow> obs_rows;
    std::vector<TrajectoryRow> traj_rows;

    const StateObserver observer = [&](std::size_t t, const std::vector<Particle>& state) {
        const bool include_obs = (t % obs_stride == 0) || t == 0 || t == steps;
        const bool include_traj =
            write_trajectory && ((t % traj_stride == 0) || t == 0 || t == steps);

        if (include_obs) {
            const auto neighbors = cell_index_neighbors(state, parameters);
            ObservableRow row;
            row.t = t;
            row.va = polarization(state);
            row.s = largest_cluster_fraction(neighbors, state);
            obs_rows.push_back(row);
        }

        if (include_traj) {
            std::vector<Particle> sorted_state = state;
            std::sort(sorted_state.begin(), sorted_state.end(),
                      [](const Particle& a, const Particle& b) { return a.id < b.id; });
            for (const Particle& particle : sorted_state) {
                TrajectoryRow row;
                row.t = t;
                row.id = particle.id;
                row.x = particle.x;
                row.y = particle.y;
                row.theta = particle.theta;
                traj_rows.push_back(row);
            }
        }
    };

    // CIM como motor productivo de busqueda de vecinos: nunca fuerza bruta
    // en la CLI, tanto para avanzar la simulacion como para el S(t) que se
    // calcula dentro del observador.
    run_simulation(initial_state, parameters, request.eta, request.rule, steps, request.base_seed,
                    cell_index_neighbors, observer);

    RunMetadata metadata;
    metadata.model = request.model_name;
    metadata.box_length = parameters.box_length;
    metadata.interaction_radius = parameters.interaction_radius;
    metadata.time_step = parameters.time_step;
    metadata.speed = parameters.speed;
    metadata.rho_label = request.rho_label;
    metadata.rho_nominal = request.rho_nominal;
    metadata.particle_count = request.particle_count;
    metadata.rho_effective =
        static_cast<double>(request.particle_count) / (parameters.box_length * parameters.box_length);
    metadata.eta = request.eta;
    metadata.base_seed = request.base_seed;
    metadata.realization = request.realization;
    metadata.steps = steps;
    metadata.observables_stride = obs_stride;
    metadata.trajectory_stride = traj_stride;

    auto fail_with_cleanup = [&](std::string message) -> RunOutcome {
        std::vector<std::string> warnings;
        detail::remove_if_exists_best_effort(obs_tmp, warnings);
        detail::remove_if_exists_best_effort(traj_tmp, warnings);
        for (const std::string& warning : warnings) {
            message += " (" + warning + ")";
        }
        outcome.ok = false;
        outcome.error = std::move(message);
        return outcome;
    };

    // Paso 1: escribir y verificar ambos archivos requeridos como
    // temporales, sin publicar nada todavia. Si falta escribir la
    // trayectoria requerida, `observables.csv` nunca llega a existir.
    const detail::TempWriteResult obs_write = detail::write_temp_file(
        obs_tmp, [&](std::ostream& out) { write_observables_csv(out, metadata, obs_rows); });
    if (!obs_write.ok) {
        return fail_with_cleanup(obs_write.error);
    }

    if (write_trajectory) {
        const detail::TempWriteResult traj_write = detail::write_temp_file(
            traj_tmp, [&](std::ostream& out) { write_trajectory_csv(out, metadata, traj_rows); });
        if (!traj_write.ok) {
            return fail_with_cleanup(traj_write.error);
        }
    } else if (fs::exists(traj_path, ec)) {
        // Esta corrida no pide trayectoria: si --overwrite dejo un
        // directorio que ya tenia una de una corrida anterior, hay que
        // eliminarla para que no describa datos obsoletos que ya no
        // corresponden a los nuevos `observables.csv`. Se hace *antes* de
        // publicar nada nuevo: si el borrado falla, no se deja una mezcla
        // de archivo viejo + archivo nuevo, se falla limpiamente dejando
        // todo como estaba.
        fs::remove(traj_path, ec);
        if (ec) {
            return fail_with_cleanup("No se pudo eliminar la trayectoria anterior '" +
                                      traj_path.string() + "': " + ec.message());
        }
    }

    // Paso 2: publicar. Trayectoria primero, observables al final (ver
    // comentario de la funcion).
    if (write_trajectory) {
        fs::rename(traj_tmp, traj_path, ec);
        if (ec) {
            return fail_with_cleanup("No se pudo renombrar '" + traj_tmp.string() + "' a '" +
                                      traj_path.string() + "': " + ec.message());
        }
    }

    fs::rename(obs_tmp, obs_path, ec);
    if (ec) {
        // La trayectoria (si correspondia) ya quedo publicada en este
        // punto: es el limite de atomicidad entre dos archivos documentado
        // arriba. No se revierte la trayectoria ya publicada (no hay una
        // copia del contenido anterior para restaurar); se informa error
        // sin ambiguedad y se recomienda reintentar con --overwrite.
        outcome.ok = false;
        outcome.error = "No se pudo renombrar '" + obs_tmp.string() + "' a '" + obs_path.string() +
                         "': " + ec.message() +
                         " (si se publico trajectory.csv, quedo desincronizada; reintentar con "
                         "--overwrite).";
        return outcome;
    }

    // Nunca informar exito si queda un temporal sin limpiar (no deberia
    // pasar tras un rename exitoso, pero se verifica explicitamente).
    if (fs::exists(obs_tmp, ec) || fs::exists(traj_tmp, ec)) {
        outcome.ok = false;
        outcome.error = "Quedo un archivo temporal sin limpiar tras publicar la corrida en '" +
                         dir.string() + "'.";
        return outcome;
    }

    outcome.ok = true;
    outcome.run_directory = dir;
    outcome.observables_path = obs_path;
    outcome.trajectory_path = write_trajectory ? traj_path : fs::path();
    outcome.observables_rows = obs_rows.size();
    outcome.trajectory_rows = traj_rows.size();
    return outcome;
}

}  // namespace tp2::cli
