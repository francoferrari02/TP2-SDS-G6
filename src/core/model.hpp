#pragma once

#include <cstddef>

namespace tp2 {

struct Parameters {
    double box_length = 10.0;
    double interaction_radius = 1.0;
    double time_step = 1.0;
    double speed = 0.03;
};

struct Particle {
    std::size_t id = 0;
    double x = 0.0;
    double y = 0.0;
    double theta = 0.0;
};

}  // namespace tp2
