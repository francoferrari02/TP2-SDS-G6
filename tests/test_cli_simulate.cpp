// Tests de la CLI productiva (`cli/simulate_cli.hpp`): parseo/validacion de
// argumentos y orquestacion real de una corrida (directorios, archivos,
// sobrescritura), usando el sistema de archivos real bajo un directorio
// temporal exclusivo de este proceso de test.
//
// Se llama directamente a `tp2::cli::parse_arguments`/`execute_run` en vez
// de invocar el ejecutable `simulate` como subproceso: es el mismo codigo
// que usa `main()` (que es un `main()` deliberadamente fino sobre estas dos
// funciones), y evitar el subproceso hace que los tests sean rapidos y
// portables.

#include "cli/simulate_cli.hpp"
#include "core/model.hpp"

#include <algorithm>
#include <cmath>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <sstream>
#include <string>
#include <vector>

namespace fs = std::filesystem;

namespace {

void expect_true(bool condition, const std::string& message) {
    if (!condition) {
        std::cerr << "FALLO: " << message << "\n";
        std::abort();
    }
}

fs::path make_scratch_root() {
    const fs::path root = fs::temp_directory_path() / "tp2_test_cli_simulate_scratch";
    std::error_code ec;
    fs::remove_all(root, ec);
    return root;
}

std::string read_file(const fs::path& path) {
    std::ifstream in(path, std::ios::binary);
    expect_true(static_cast<bool>(in), "no se pudo abrir para lectura: " + path.string());
    std::ostringstream buffer;
    buffer << in.rdbuf();
    return buffer.str();
}

// Divide el contenido de un CSV producido por esta CLI en: mapa de
// metadatos ("clave" -> "valor", de las lineas "# clave=valor"), la linea de
// encabezado, y las filas de datos (cada una como vector de campos, en
// orden).
struct ParsedCsv {
    std::map<std::string, std::string> metadata;
    std::string header;
    std::vector<std::vector<std::string>> rows;
};

std::vector<std::string> split_csv_line(const std::string& line) {
    std::vector<std::string> fields;
    std::string field;
    std::istringstream stream(line);
    while (std::getline(stream, field, ',')) {
        fields.push_back(field);
    }
    return fields;
}

ParsedCsv parse_csv(const std::string& text) {
    ParsedCsv parsed;
    std::istringstream stream(text);
    std::string line;
    bool past_header = false;
    while (std::getline(stream, line)) {
        if (!line.empty() && line.back() == '\r') {
            line.pop_back();
        }
        if (!past_header) {
            if (!line.empty() && line[0] == '#') {
                const std::size_t equal_pos = line.find('=');
                expect_true(equal_pos != std::string::npos, "linea de metadato sin '=': " + line);
                const std::string key = line.substr(2, equal_pos - 2);
                const std::string value = line.substr(equal_pos + 1);
                parsed.metadata[key] = value;
                continue;
            }
            parsed.header = line;
            past_header = true;
            continue;
        }
        if (line.empty()) {
            continue;
        }
        parsed.rows.push_back(split_csv_line(line));
    }
    return parsed;
}

tp2::cli::RunRequest base_request(const fs::path& output_dir) {
    tp2::cli::RunRequest request;
    request.rule = tp2::InteractionRule::kVicsek;
    request.model_name = "vicsek";
    request.rho_nominal = 2.0;
    request.rho_label = "rho_2";
    request.particle_count = 3;
    request.eta = 0.5;
    request.steps = 2;
    request.base_seed = 4242;
    request.realization = 3;
    request.output_dir = output_dir;
    request.write_trajectory = false;
    request.observables_stride = 1;
    request.trajectory_stride = 1;
    request.overwrite = false;
    return request;
}

}  // namespace

int main() {
    const fs::path scratch_root = make_scratch_root();

    // --- 1. steps=2, N=3 -> 3 filas de observables, 9 filas de trayectoria ---
    {
        tp2::cli::RunRequest request = base_request(scratch_root / "case1");
        request.write_trajectory = true;

        const tp2::cli::RunOutcome outcome = tp2::cli::execute_run(request);
        expect_true(outcome.ok, "caso 1: la corrida deberia haber tenido exito: " + outcome.error);

        const ParsedCsv obs = parse_csv(read_file(outcome.observables_path));
        expect_true(obs.rows.size() == 3, "caso 1: se esperaban 3 filas de observables (t=0,1,2)");

        const ParsedCsv traj = parse_csv(read_file(outcome.trajectory_path));
        expect_true(traj.rows.size() == 9,
                    "caso 1: se esperaban 9 filas de trayectoria (3 pasos x N=3)");
    }

    // --- 2. Sin --write-trajectory, trajectory.csv no existe ---
    {
        tp2::cli::RunRequest request = base_request(scratch_root / "case2");
        request.write_trajectory = false;

        const tp2::cli::RunOutcome outcome = tp2::cli::execute_run(request);
        expect_true(outcome.ok, "caso 2: la corrida deberia haber tenido exito: " + outcome.error);
        expect_true(outcome.trajectory_path.empty(), "caso 2: no deberia reportarse trajectory_path");
        expect_true(!fs::exists(outcome.run_directory / "trajectory.csv"),
                    "caso 2: trajectory.csv no deberia existir en disco");
        expect_true(fs::exists(outcome.observables_path), "caso 2: observables.csv si debe existir");
    }

    // --- 3. Misma configuracion y semilla -> archivos identicos byte a byte ---
    {
        tp2::cli::RunRequest request_a = base_request(scratch_root / "case3_a");
        request_a.write_trajectory = true;
        tp2::cli::RunRequest request_b = base_request(scratch_root / "case3_b");
        request_b.write_trajectory = true;

        const tp2::cli::RunOutcome outcome_a = tp2::cli::execute_run(request_a);
        const tp2::cli::RunOutcome outcome_b = tp2::cli::execute_run(request_b);
        expect_true(outcome_a.ok && outcome_b.ok, "caso 3: ambas corridas deberian tener exito");

        expect_true(read_file(outcome_a.observables_path) == read_file(outcome_b.observables_path),
                    "caso 3: observables.csv deberia ser identico byte a byte");
        expect_true(read_file(outcome_a.trajectory_path) == read_file(outcome_b.trajectory_path),
                    "caso 3: trajectory.csv deberia ser identico byte a byte");
    }

    // --- 4. vx=v*cos(theta), vy=v*sin(theta) reconstruible desde theta ---
    {
        tp2::cli::RunRequest request = base_request(scratch_root / "case4");
        request.write_trajectory = true;
        request.steps = 1;

        const tp2::cli::RunOutcome outcome = tp2::cli::execute_run(request);
        expect_true(outcome.ok, "caso 4: la corrida deberia haber tenido exito: " + outcome.error);

        const ParsedCsv traj = parse_csv(read_file(outcome.trajectory_path));
        expect_true(traj.header == "t,id,x,y,theta", "caso 4: encabezado de trayectoria incorrecto");

        const double v = 0.03;  // parametro fijo del TP (Parameters::speed).
        for (const std::vector<std::string>& row : traj.rows) {
            expect_true(row.size() == 5, "caso 4: fila de trayectoria con cantidad de campos incorrecta");
            const double theta = std::stod(row[4]);
            expect_true(theta >= 0.0 && theta < 2.0 * 3.14159265358979323846 + 1e-9,
                        "caso 4: theta fuera de [0,2*pi)");
            const double vx = v * std::cos(theta);
            const double vy = v * std::sin(theta);
            expect_true(std::abs(std::hypot(vx, vy) - v) < 1e-12,
                        "caso 4: vx,vy reconstruidos no tienen modulo v");
        }
    }

    // --- 5. Cada paso de trayectoria tiene exactamente N ids distintos ---
    {
        tp2::cli::RunRequest request = base_request(scratch_root / "case5");
        request.write_trajectory = true;
        request.particle_count = 7;
        request.steps = 3;

        const tp2::cli::RunOutcome outcome = tp2::cli::execute_run(request);
        expect_true(outcome.ok, "caso 5: la corrida deberia haber tenido exito: " + outcome.error);

        const ParsedCsv traj = parse_csv(read_file(outcome.trajectory_path));
        std::map<std::string, std::set<std::string>> ids_by_step;
        for (const std::vector<std::string>& row : traj.rows) {
            ids_by_step[row[0]].insert(row[1]);
        }
        expect_true(ids_by_step.size() == 4, "caso 5: se esperaban 4 pasos distintos (t=0..3)");
        for (const auto& [step, ids] : ids_by_step) {
            expect_true(ids.size() == 7, "caso 5: el paso t=" + step + " no tiene N=7 ids distintos");
        }
    }

    // --- 6. Los metadatos coinciden con la configuracion solicitada ---
    {
        tp2::cli::RunRequest request = base_request(scratch_root / "case6");
        request.model_name = "voter";
        request.rule = tp2::InteractionRule::kVoter;
        request.rho_nominal = 4.0;
        request.rho_label = "rho_4";
        request.particle_count = 400;
        request.eta = 0.25;
        request.steps = 5;
        request.base_seed = 999;
        request.realization = 7;
        request.write_trajectory = true;
        request.observables_stride = 2;
        request.trajectory_stride = 3;

        const tp2::cli::RunOutcome outcome = tp2::cli::execute_run(request);
        expect_true(outcome.ok, "caso 6: la corrida deberia haber tenido exito: " + outcome.error);

        const ParsedCsv obs = parse_csv(read_file(outcome.observables_path));
        expect_true(obs.metadata.at("model") == "voter", "caso 6: metadato model incorrecto");
        expect_true(obs.metadata.at("rho_label") == "rho_4", "caso 6: metadato rho_label incorrecto");
        expect_true(obs.metadata.at("N") == "400", "caso 6: metadato N incorrecto");
        expect_true(obs.metadata.at("eta") == "0.25", "caso 6: metadato eta incorrecto");
        expect_true(obs.metadata.at("base_seed") == "999", "caso 6: metadato base_seed incorrecto");
        expect_true(obs.metadata.at("realization") == "7", "caso 6: metadato realization incorrecto");
        expect_true(obs.metadata.at("steps") == "5", "caso 6: metadato steps incorrecto");
        expect_true(obs.metadata.at("observables_stride") == "2",
                    "caso 6: metadato observables_stride incorrecto");
        expect_true(obs.metadata.at("trajectory_stride") == "3",
                    "caso 6: metadato trajectory_stride incorrecto");
        expect_true(obs.metadata.at("L") == "10", "caso 6: metadato L incorrecto");
        expect_true(obs.metadata.at("rc") == "1", "caso 6: metadato rc incorrecto");
        expect_true(obs.metadata.at("dt") == "1", "caso 6: metadato dt incorrecto");
        expect_true(std::stod(obs.metadata.at("v")) == 0.03, "caso 6: metadato v incorrecto");
        expect_true(obs.metadata.at("periodic") == "true", "caso 6: metadato periodic incorrecto");
        expect_true(obs.metadata.at("schema_version") == "1", "caso 6: metadato schema_version incorrecto");

        const ParsedCsv traj = parse_csv(read_file(outcome.trajectory_path));
        expect_true(traj.metadata == obs.metadata,
                    "caso 6: observables.csv y trajectory.csv deberian tener el mismo bloque de metadatos");
    }

    // --- 7. Un archivo/directorio existente produce error y no se modifica ---
    {
        tp2::cli::RunRequest request = base_request(scratch_root / "case7");
        const tp2::cli::RunOutcome first = tp2::cli::execute_run(request);
        expect_true(first.ok, "caso 7: la primera corrida deberia haber tenido exito");
        const std::string original_content = read_file(first.observables_path);

        const tp2::cli::RunOutcome second = tp2::cli::execute_run(request);
        expect_true(!second.ok, "caso 7: repetir la misma corrida sin --overwrite deberia fallar");
        expect_true(!second.error.empty(), "caso 7: el error deberia tener un mensaje");

        expect_true(read_file(first.observables_path) == original_content,
                    "caso 7: observables.csv no deberia haberse modificado tras el intento fallido");
    }

    // --- 8. --overwrite reemplaza coherentemente toda la corrida ---
    {
        tp2::cli::RunRequest request = base_request(scratch_root / "case8");
        request.write_trajectory = true;
        const tp2::cli::RunOutcome first = tp2::cli::execute_run(request);
        expect_true(first.ok, "caso 8: la primera corrida deberia haber tenido exito");
        expect_true(fs::exists(first.run_directory / "trajectory.csv"),
                    "caso 8: la primera corrida deberia haber escrito trayectoria");

        tp2::cli::RunRequest overwrite_request = request;
        overwrite_request.write_trajectory = false;
        overwrite_request.overwrite = true;
        // observables_stride no forma parte del directorio (solo modelo, rho_label,
        // eta, steps, realizacion y semilla lo hacen), asi que cambiarlo permite
        // verificar que --overwrite reemplazo el contenido sin cambiar el destino.
        overwrite_request.observables_stride = 2;
        const tp2::cli::RunOutcome second = tp2::cli::execute_run(overwrite_request);
        expect_true(second.ok, "caso 8: la corrida con --overwrite deberia haber tenido exito: " +
                                    second.error);
        expect_true(second.run_directory == first.run_directory,
                    "caso 8: overwrite deberia apuntar al mismo directorio (misma quintupla identificadora)");

        expect_true(!fs::exists(second.run_directory / "trajectory.csv"),
                    "caso 8: trajectory.csv viejo deberia haberse eliminado al sobrescribir sin trayectoria");
        const ParsedCsv obs = parse_csv(read_file(second.observables_path));
        expect_true(obs.metadata.at("observables_stride") == "2",
                    "caso 8: observables.csv deberia reflejar la configuracion nueva tras --overwrite");
    }

    // --- 9. Los strides guardan t=0 y el estado final aunque no sea multiplo ---
    {
        tp2::cli::RunRequest request = base_request(scratch_root / "case9");
        request.write_trajectory = true;
        request.steps = 10;
        request.observables_stride = 4;
        request.trajectory_stride = 3;

        const tp2::cli::RunOutcome outcome = tp2::cli::execute_run(request);
        expect_true(outcome.ok, "caso 9: la corrida deberia haber tenido exito: " + outcome.error);

        const ParsedCsv obs = parse_csv(read_file(outcome.observables_path));
        std::set<int> obs_steps;
        for (const auto& row : obs.rows) obs_steps.insert(std::stoi(row[0]));
        const std::set<int> expected_obs_steps = {0, 4, 8, 10};
        expect_true(obs_steps == expected_obs_steps,
                    "caso 9: los pasos de observables no coinciden con stride=4 + t=0 + t=T");

        const ParsedCsv traj = parse_csv(read_file(outcome.trajectory_path));
        std::set<int> traj_steps;
        for (const auto& row : traj.rows) traj_steps.insert(std::stoi(row[0]));
        const std::set<int> expected_traj_steps = {0, 3, 6, 9, 10};
        expect_true(traj_steps == expected_traj_steps,
                    "caso 9: los pasos de trayectoria no coinciden con stride=3 + t=0 + t=T");
    }

    // --- 10. Modelo, densidad, eta, pasos, realizacion y semilla se ---
    //         diferencian en la ruta.
    {
        tp2::cli::RunRequest request_a = base_request(scratch_root / "case10");
        request_a.eta = 0.5;
        tp2::cli::RunRequest request_b = base_request(scratch_root / "case10");
        request_b.eta = 0.75;

        const fs::path dir_a = tp2::cli::compute_run_directory(request_a);
        const fs::path dir_b = tp2::cli::compute_run_directory(request_b);
        expect_true(dir_a != dir_b, "caso 10: distinto eta deberia dar distinto directorio");

        const std::string dir_a_text = dir_a.string();
        expect_true(dir_a_text.find("vicsek") != std::string::npos, "caso 10: falta el modelo en la ruta");
        expect_true(dir_a_text.find("rho_2") != std::string::npos, "caso 10: falta la densidad en la ruta");
        expect_true(dir_a_text.find("eta_0p5") != std::string::npos, "caso 10: falta eta en la ruta");
        expect_true(dir_a_text.find("steps_2") != std::string::npos, "caso 10: faltan los pasos en la ruta");
        expect_true(dir_a_text.find("realization_003") != std::string::npos,
                    "caso 10: falta la realizacion en la ruta");
        expect_true(dir_a_text.find("seed_4242") != std::string::npos, "caso 10: falta la semilla en la ruta");
    }

    // --- 11. Los nombres no usan coma decimal: eta_0p5, no eta_0,5 ni eta_0.5 ---
    {
        const std::string formatted = tp2::cli::format_eta_for_path(0.5);
        expect_true(formatted == "0p5", "caso 11: se esperaba 'eta_0p5' -> formatted == '0p5'");
        expect_true(formatted.find(',') == std::string::npos, "caso 11: no debe haber coma");
        expect_true(formatted.find('.') == std::string::npos, "caso 11: no debe haber punto");

        expect_true(tp2::cli::format_eta_for_path(1.0) == "1", "caso 11: eta=1.0 deberia formatear a '1'");
        expect_true(tp2::cli::format_eta_for_path(0.0) == "0", "caso 11: eta=0.0 deberia formatear a '0'");
    }

    // --- 12. Casos invalidos de CLI fallan correctamente ---
    {
        auto args_ok = [&]() {
            return std::vector<std::string>{"--model",       "vicsek",
                                             "--rho-nominal", "2",
                                             "--rho-label",   "rho_2",
                                             "--N",           "200",
                                             "--eta",         "0.5",
                                             "--steps",       "10",
                                             "--base-seed",   "1",
                                             "--realization", "0",
                                             "--output-dir",  (scratch_root / "case12_ok").string()};
        };

        const tp2::cli::ParseResult valid = tp2::cli::parse_arguments(args_ok());
        expect_true(valid.ok, "caso 12: la configuracion valida deberia parsear correctamente");

        auto expect_parse_failure = [&](std::vector<std::string> args, const std::string& label) {
            const tp2::cli::ParseResult result = tp2::cli::parse_arguments(args);
            expect_true(!result.ok, "caso 12 (" + label + "): deberia fallar el parseo");
            expect_true(!result.error.empty(), "caso 12 (" + label + "): el error no deberia estar vacio");
        };

        {
            std::vector<std::string> args = args_ok();
            args[1] = "invalid_model";
            expect_parse_failure(args, "modelo invalido");
        }
        {
            std::vector<std::string> args = args_ok();
            const std::size_t idx =
                std::find(args.begin(), args.end(), "--steps") - args.begin();
            args[idx + 1] = "-5";
            expect_parse_failure(args, "steps negativo");
        }
        {
            std::vector<std::string> args = args_ok();
            const std::size_t idx = std::find(args.begin(), args.end(), "--N") - args.begin();
            args[idx + 1] = "-3";
            expect_parse_failure(args, "N negativo");
        }
        {
            std::vector<std::string> args = args_ok();
            const std::size_t idx = std::find(args.begin(), args.end(), "--eta") - args.begin();
            args[idx + 1] = "-0.1";
            expect_parse_failure(args, "eta negativo");
        }
        {
            std::vector<std::string> args = args_ok();
            args.push_back("--observables-stride");
            args.push_back("0");
            expect_parse_failure(args, "observables-stride cero");
        }
        {
            std::vector<std::string> args = args_ok();
            const std::size_t idx = std::find(args.begin(), args.end(), "--N") - args.begin();
            args[idx + 1] = "199";  // rho_nominal=2 exige N=200
            expect_parse_failure(args, "N inconsistente con rho=2 obligatorio");
        }
        {
            std::vector<std::string> args = args_ok();
            args.pop_back();
            args.pop_back();  // elimina --output-dir y su valor
            expect_parse_failure(args, "falta --output-dir");
        }
        {
            std::vector<std::string> args = args_ok();
            args.push_back("--unknown-flag");
            expect_parse_failure(args, "flag desconocida");
        }
        {
            // --- valores no finitos y densidad nominal invalida (revision) ---
            std::vector<std::string> args = args_ok();
            const std::size_t idx = std::find(args.begin(), args.end(), "--rho-nominal") - args.begin();
            args[idx + 1] = "nan";
            expect_parse_failure(args, "rho-nominal nan");
        }
        {
            std::vector<std::string> args = args_ok();
            const std::size_t idx = std::find(args.begin(), args.end(), "--rho-nominal") - args.begin();
            args[idx + 1] = "inf";
            expect_parse_failure(args, "rho-nominal inf");
        }
        {
            std::vector<std::string> args = args_ok();
            const std::size_t idx = std::find(args.begin(), args.end(), "--rho-nominal") - args.begin();
            args[idx + 1] = "-1";
            expect_parse_failure(args, "rho-nominal negativo");
        }
        {
            std::vector<std::string> args = args_ok();
            const std::size_t idx = std::find(args.begin(), args.end(), "--rho-nominal") - args.begin();
            args[idx + 1] = "0";
            expect_parse_failure(args, "rho-nominal cero");
        }
        {
            std::vector<std::string> args = args_ok();
            const std::size_t idx = std::find(args.begin(), args.end(), "--eta") - args.begin();
            args[idx + 1] = "nan";
            expect_parse_failure(args, "eta nan");
        }
        {
            std::vector<std::string> args = args_ok();
            const std::size_t idx = std::find(args.begin(), args.end(), "--eta") - args.begin();
            args[idx + 1] = "inf";
            expect_parse_failure(args, "eta inf");
        }
        {
            std::vector<std::string> args = args_ok();
            const std::size_t idx = std::find(args.begin(), args.end(), "--eta") - args.begin();
            args[idx + 1] = "-inf";
            expect_parse_failure(args, "eta -inf");
        }
    }

    // --- 13. Etiquetas de --rho-label inseguras fallan; etiquetas legitimas ---
    //          con guion bajo, letras y digitos siguen siendo validas.
    {
        auto args_with_label = [&](const std::string& label) {
            return std::vector<std::string>{"--model",       "vicsek",
                                             "--rho-nominal", "2",
                                             "--rho-label",   label,
                                             "--N",           "200",
                                             "--eta",         "0.5",
                                             "--steps",       "10",
                                             "--base-seed",   "1",
                                             "--realization", "0",
                                             "--output-dir",  (scratch_root / "case13").string()};
        };

        for (const std::string& bad_label : {".", "..", "../escape", "rho/2", "rho 2", "rho\\2", ""}) {
            const tp2::cli::ParseResult result = tp2::cli::parse_arguments(args_with_label(bad_label));
            expect_true(!result.ok, "caso 13: --rho-label '" + bad_label + "' deberia rechazarse");
            expect_true(!result.error.empty(), "caso 13: el error de rho-label no deberia estar vacio");
        }

        for (const std::string& good_label : {"rho_2", "rho_1_over_pi", "rho_1_over_2pi", "rho-2", "RHO2"}) {
            const tp2::cli::ParseResult result = tp2::cli::parse_arguments(args_with_label(good_label));
            expect_true(result.ok, "caso 13: --rho-label '" + good_label + "' deberia aceptarse");
        }
    }

    // --- 14. format_eta_for_path no colisiona para valores de eta muy cercanos ---
    {
        const double eta_a = 0.5;
        const double eta_b = std::nextafter(eta_a, 1.0);  // el double representable inmediatamente
                                                            // superior a 0.5: con precision fija
                                                            // baja (por ejemplo 10 digitos) ambos
                                                            // formateaban igual.
        expect_true(eta_a != eta_b, "caso 14: precondicion invalida, eta_a y eta_b deberian diferir");

        const std::string formatted_a = tp2::cli::format_eta_for_path(eta_a);
        const std::string formatted_b = tp2::cli::format_eta_for_path(eta_b);
        expect_true(formatted_a != formatted_b,
                    "caso 14: dos valores de eta distintos no deberian formatear igual (colision)");
        expect_true(formatted_a.find(',') == std::string::npos &&
                        formatted_a.find('.') == std::string::npos,
                    "caso 14: formatted_a no debe tener ',' ni '.'");
        expect_true(formatted_b.find(',') == std::string::npos &&
                        formatted_b.find('.') == std::string::npos,
                    "caso 14: formatted_b no debe tener ',' ni '.'");

        // Debe ser deterministico: llamar dos veces con el mismo valor da el mismo resultado.
        expect_true(tp2::cli::format_eta_for_path(eta_a) == formatted_a,
                    "caso 14: format_eta_for_path deberia ser deterministico");
    }

    // --- 15. No quedan archivos temporales tras una corrida exitosa ---
    {
        tp2::cli::RunRequest request = base_request(scratch_root / "case15");
        request.write_trajectory = true;

        const tp2::cli::RunOutcome outcome = tp2::cli::execute_run(request);
        expect_true(outcome.ok, "caso 15: la corrida deberia haber tenido exito: " + outcome.error);

        expect_true(!fs::exists(outcome.run_directory / "observables.csv.tmp"),
                    "caso 15: no deberia quedar observables.csv.tmp tras una corrida exitosa");
        expect_true(!fs::exists(outcome.run_directory / "trajectory.csv.tmp"),
                    "caso 15: no deberia quedar trajectory.csv.tmp tras una corrida exitosa");

        std::size_t file_count = 0;
        for (const auto& entry : fs::directory_iterator(outcome.run_directory)) {
            (void)entry;
            ++file_count;
        }
        expect_true(file_count == 2,
                    "caso 15: el directorio de la corrida deberia contener exactamente 2 archivos "
                    "(observables.csv y trajectory.csv), sin temporales sueltos");
    }

    // --- 16. Eliminacion de trayectoria vieja: exito la elimina; si no existe, no es error ---
    {
        tp2::cli::RunRequest request = base_request(scratch_root / "case16");
        request.write_trajectory = true;
        const tp2::cli::RunOutcome first = tp2::cli::execute_run(request);
        expect_true(first.ok, "caso 16: la primera corrida deberia haber tenido exito");
        expect_true(fs::exists(first.run_directory / "trajectory.csv"),
                    "caso 16: deberia existir trajectory.csv tras la primera corrida");

        tp2::cli::RunRequest overwrite_request = request;
        overwrite_request.write_trajectory = false;
        overwrite_request.overwrite = true;
        const tp2::cli::RunOutcome second = tp2::cli::execute_run(overwrite_request);
        expect_true(second.ok, "caso 16: --overwrite sin trayectoria deberia tener exito: " +
                                    second.error);
        expect_true(!fs::exists(second.run_directory / "trajectory.csv"),
                    "caso 16: trajectory.csv deberia haberse eliminado");

        // Repetir de nuevo sin trayectoria: ya no hay trajectory.csv que
        // borrar, no deberia fallar por "no encontrado".
        tp2::cli::RunRequest third_request = overwrite_request;
        const tp2::cli::RunOutcome third = tp2::cli::execute_run(third_request);
        expect_true(third.ok,
                    "caso 16: repetir --overwrite sin trayectoria cuando ya no hay una vieja no "
                    "deberia fallar: " +
                        third.error);
    }

    // --- 17. Error real de escritura (permisos) no deja archivos publicados ---
    //          y no informa exito. Se salta la aseveracion estricta si el
    //          proceso corre con privilegios que ignoran permisos (por
    //          ejemplo root en un contenedor de CI), en vez de fallar el
    //          test por una condicion del entorno ajena al codigo.
    {
        tp2::cli::RunRequest request = base_request(scratch_root / "case17");
        const fs::path dir = tp2::cli::compute_run_directory(request);
        std::error_code ec;
        fs::create_directories(dir, ec);
        expect_true(!ec, "caso 17: no se pudo preparar el directorio de la corrida");

        fs::permissions(dir, fs::perms::owner_read | fs::perms::owner_exec,
                         fs::perm_options::replace, ec);
        expect_true(!ec, "caso 17: no se pudieron restringir permisos del directorio");

        request.overwrite = true;  // el directorio ya existe (lo creamos arriba a proposito).
        const tp2::cli::RunOutcome outcome = tp2::cli::execute_run(request);

        // Restaurar permisos siempre, incluso si la aseveracion de abajo no aplica,
        // para no dejar el directorio temporal del test inaccesible.
        fs::permissions(dir, fs::perms::owner_all, fs::perm_options::replace, ec);

        if (!outcome.ok) {
            expect_true(!fs::exists(dir / "observables.csv"),
                        "caso 17: no deberia haberse publicado observables.csv tras un error de escritura");
            expect_true(!fs::exists(dir / "observables.csv.tmp"),
                        "caso 17: no deberia quedar un observables.csv.tmp tras limpiar el error");
            expect_true(!outcome.error.empty(), "caso 17: el error deberia tener un mensaje");
        } else {
            std::cerr << "AVISO: caso 17 no pudo forzar un error de permisos en este entorno "
                         "(por ejemplo, proceso con privilegios que ignoran permisos de "
                         "directorio); se omite la aseveracion estricta.\n";
        }
    }

    std::cout << "OK: escritor de salida y CLI verificados (17/17 casos requeridos).\n";
    return 0;
}
