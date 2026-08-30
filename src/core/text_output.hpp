#pragma once

#include "core/model.hpp"

#include <cstddef>
#include <cstdint>
#include <limits>
#include <locale>
#include <ostream>
#include <string>
#include <vector>

namespace tp2 {

// Formato público de salida (propuesta aprobada, ver
// plan_desarrollo_tp2/DECISIONES_PENDIENTES.md): dos archivos de texto por
// corrida, `observables.csv` y `trajectory.csv`, cada uno con el mismo
// bloque de metadatos autocontenido (`# key=value`, uno por línea) seguido
// de una única línea de encabezado CSV y luego los datos, separados por
// coma, con punto como separador decimal (locale `C`, impuesto
// explícitamente sobre el stream para no depender del locale del sistema).
//
// Alcance de este archivo: únicamente el formato/serialización a un
// `std::ostream` ya abierto. La organización de directorios, el chequeo de
// sobrescritura y la escritura atómica (archivo temporal + rename) son
// responsabilidad de quien orquesta la corrida (`cli/simulate_cli.hpp`), no
// de este archivo: mantiene la serialización testeable de forma aislada,
// sin tocar el sistema de archivos.

struct RunMetadata {
    std::string model;                 // "vicsek" o "voter"
    double box_length = 0.0;           // L
    double interaction_radius = 0.0;   // rc
    double time_step = 0.0;            // dt
    double speed = 0.0;                // v
    std::string rho_label;             // p.ej. "rho_2", "rho_1_over_pi"
    double rho_nominal = 0.0;
    std::size_t particle_count = 0;    // N
    double rho_effective = 0.0;        // N / L^2
    double eta = 0.0;
    std::uint64_t base_seed = 0;
    std::size_t realization = 0;
    std::size_t steps = 0;
    std::size_t observables_stride = 1;
    std::size_t trajectory_stride = 1;
};

struct ObservableRow {
    std::size_t t = 0;
    double va = 0.0;
    double s = 0.0;
};

struct TrajectoryRow {
    std::size_t t = 0;
    std::size_t id = 0;
    double x = 0.0;
    double y = 0.0;
    double theta = 0.0;
};

namespace detail {

// `std::numeric_limits<double>::max_digits10` (17) dígitos significativos
// alcanzan para que cualquier `double` finito se reconstruya exactamente al
// volver a parsearlo (round-trip), por eso se usan aquí en vez de una
// cantidad fija de decimales.
inline void write_double(std::ostream& out, double value) {
    out.precision(std::numeric_limits<double>::max_digits10);
    out << value;
}

}  // namespace detail

// Bloque de metadatos común a ambos archivos: exactamente las claves del
// contrato aprobado, en este orden, una por línea, con prefijo `# `.
inline void write_metadata_header(std::ostream& out, const RunMetadata& metadata) {
    out << "# schema_version=1\n";
    out << "# model=" << metadata.model << "\n";
    out << "# L=";
    detail::write_double(out, metadata.box_length);
    out << "\n";
    out << "# rc=";
    detail::write_double(out, metadata.interaction_radius);
    out << "\n";
    out << "# dt=";
    detail::write_double(out, metadata.time_step);
    out << "\n";
    out << "# v=";
    detail::write_double(out, metadata.speed);
    out << "\n";
    out << "# periodic=true\n";
    out << "# rho_label=" << metadata.rho_label << "\n";
    out << "# rho_nominal=";
    detail::write_double(out, metadata.rho_nominal);
    out << "\n";
    out << "# N=" << metadata.particle_count << "\n";
    out << "# rho_effective=";
    detail::write_double(out, metadata.rho_effective);
    out << "\n";
    out << "# eta=";
    detail::write_double(out, metadata.eta);
    out << "\n";
    out << "# noise_convention=uniform[-eta/2,eta/2]\n";
    out << "# base_seed=" << metadata.base_seed << "\n";
    out << "# realization=" << metadata.realization << "\n";
    out << "# steps=" << metadata.steps << "\n";
    out << "# observables_stride=" << metadata.observables_stride << "\n";
    out << "# trajectory_stride=" << metadata.trajectory_stride << "\n";
}

// Escribe `observables.csv` completo (metadatos + encabezado `t,va,S` +
// filas) en `out`. `rows` debe venir ya ordenado por `t` ascendente; esta
// función no reordena ni valida el contenido, solo lo serializa.
inline void write_observables_csv(std::ostream& out, const RunMetadata& metadata,
                                   const std::vector<ObservableRow>& rows) {
    out.imbue(std::locale::classic());
    write_metadata_header(out, metadata);
    out << "t,va,S\n";
    for (const ObservableRow& row : rows) {
        out << row.t << ",";
        detail::write_double(out, row.va);
        out << ",";
        detail::write_double(out, row.s);
        out << "\n";
    }
}

// Escribe `trajectory.csv` completo (metadatos + encabezado `t,id,x,y,theta`
// + filas) en `out`. `rows` debe venir ya ordenado por `t` y, dentro de cada
// `t`, por `id` ascendente; esta función no reordena ni valida el
// contenido, solo lo serializa.
inline void write_trajectory_csv(std::ostream& out, const RunMetadata& metadata,
                                  const std::vector<TrajectoryRow>& rows) {
    out.imbue(std::locale::classic());
    write_metadata_header(out, metadata);
    out << "t,id,x,y,theta\n";
    for (const TrajectoryRow& row : rows) {
        out << row.t << "," << row.id << ",";
        detail::write_double(out, row.x);
        out << ",";
        detail::write_double(out, row.y);
        out << ",";
        detail::write_double(out, row.theta);
        out << "\n";
    }
}

}  // namespace tp2
