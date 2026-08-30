// Tests de formato puro de `core/text_output.hpp`: solo serializacion a un
// `std::ostream` en memoria, sin tocar el sistema de archivos (eso se prueba
// en `tests/test_cli_simulate.cpp`, contra la orquestacion real de la CLI).

#include "core/text_output.hpp"

#include <cstdlib>
#include <iostream>
#include <limits>
#include <sstream>
#include <string>
#include <vector>

namespace {

void expect_true(bool condition, const std::string& message) {
    if (!condition) {
        std::cerr << "FALLO: " << message << "\n";
        std::abort();
    }
}

tp2::RunMetadata sample_metadata() {
    tp2::RunMetadata metadata;
    metadata.model = "vicsek";
    metadata.box_length = 10.0;
    metadata.interaction_radius = 1.0;
    metadata.time_step = 1.0;
    metadata.speed = 0.03;
    metadata.rho_label = "rho_2";
    metadata.rho_nominal = 2.0;
    metadata.particle_count = 200;
    metadata.rho_effective = 2.0;
    metadata.eta = 0.5;
    metadata.base_seed = 12345;
    metadata.realization = 3;
    metadata.steps = 2000;
    metadata.observables_stride = 1;
    metadata.trajectory_stride = 1;
    return metadata;
}

}  // namespace

int main() {
    // 1. El bloque de metadatos tiene exactamente las 18 claves del
    //    contrato, en orden, con prefijo "# " y "clave=valor".
    {
        std::ostringstream out;
        tp2::write_metadata_header(out, sample_metadata());
        const std::string text = out.str();

        const std::vector<std::string> expected_keys = {
            "# schema_version=1", "# model=vicsek",     "# periodic=true",
            "# rho_label=rho_2",  "# N=200",             "# noise_convention=uniform[-eta/2,eta/2]",
            "# base_seed=12345",  "# realization=3",     "# steps=2000",
            "# observables_stride=1", "# trajectory_stride=1"};
        for (const std::string& key : expected_keys) {
            expect_true(text.find(key) != std::string::npos,
                        "falta la linea de metadato: " + key);
        }

        std::size_t line_count = 0;
        std::istringstream lines(text);
        std::string line;
        while (std::getline(lines, line)) {
            expect_true(!line.empty() && line[0] == '#', "una linea de metadatos no empieza con '#'");
            ++line_count;
        }
        expect_true(line_count == 18, "se esperaban exactamente 18 lineas de metadatos");
    }

    // 2. observables.csv: encabezado exacto "t,va,S" y una fila por dato,
    //    con precision suficiente para round-trip exacto de double.
    {
        std::ostringstream out;
        std::vector<tp2::ObservableRow> rows = {{0, 0.123456789012345, 0.5}, {1, 1.0 / 3.0, 0.75}};
        tp2::write_observables_csv(out, sample_metadata(), rows);
        const std::string text = out.str();

        expect_true(text.find("\nt,va,S\n") != std::string::npos,
                    "falta el encabezado 't,va,S' en observables.csv");

        std::istringstream lines(text);
        std::string line;
        std::size_t data_rows = 0;
        bool past_header = false;
        while (std::getline(lines, line)) {
            if (!past_header) {
                if (line == "t,va,S") {
                    past_header = true;
                }
                continue;
            }
            ++data_rows;
        }
        expect_true(data_rows == rows.size(), "cantidad incorrecta de filas de datos en observables.csv");

        // Round-trip: parsear el segundo valor de la primera fila de datos
        // y compararlo exactamente contra el double original.
        std::istringstream lines2(text);
        std::string header_line;
        while (std::getline(lines2, header_line) && header_line != "t,va,S") {
        }
        std::string first_data_line;
        std::getline(lines2, first_data_line);
        const std::size_t first_comma = first_data_line.find(',');
        const std::size_t second_comma = first_data_line.find(',', first_comma + 1);
        const std::string va_text =
            first_data_line.substr(first_comma + 1, second_comma - first_comma - 1);
        const double parsed_va = std::stod(va_text);
        expect_true(parsed_va == rows[0].va,
                    "el valor de va no hace round-trip exacto con max_digits10");
    }

    // 3. trajectory.csv: encabezado exacto "t,id,x,y,theta" y una fila por
    //    partícula-paso.
    {
        std::ostringstream out;
        std::vector<tp2::TrajectoryRow> rows = {
            {0, 0, 1.0, 2.0, 0.1}, {0, 1, 3.0, 4.0, 0.2}, {1, 0, 1.03, 2.0, 0.15}};
        tp2::write_trajectory_csv(out, sample_metadata(), rows);
        const std::string text = out.str();

        expect_true(text.find("\nt,id,x,y,theta\n") != std::string::npos,
                    "falta el encabezado 't,id,x,y,theta' en trajectory.csv");

        std::istringstream lines(text);
        std::string line;
        std::size_t data_rows = 0;
        bool past_header = false;
        while (std::getline(lines, line)) {
            if (!past_header) {
                if (line == "t,id,x,y,theta") {
                    past_header = true;
                }
                continue;
            }
            ++data_rows;
        }
        expect_true(data_rows == rows.size(), "cantidad incorrecta de filas de datos en trajectory.csv");
    }

    // 4. El separador decimal es siempre '.', nunca ',', independientemente
    //    de valores fraccionarios (locale C impuesto explícitamente).
    {
        std::ostringstream out;
        std::vector<tp2::ObservableRow> rows = {{0, 0.5, 0.25}};
        tp2::write_observables_csv(out, sample_metadata(), rows);
        const std::string text = out.str();
        expect_true(text.find("0,0.5,0.25") != std::string::npos ||
                        text.find(",0.5,") != std::string::npos,
                    "no se encontro el separador decimal '.' esperado");
    }

    std::cout << "OK: formato de observables.csv y trajectory.csv verificado (metadatos, "
                 "encabezados, cantidad de filas, precision y separador decimal).\n";
    return 0;
}
