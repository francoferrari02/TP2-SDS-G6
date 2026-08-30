#pragma once

#include "core/model.hpp"

#include <cmath>

namespace tp2 {

inline double periodic_wrap(double coordinate, double box_length) {
    const double wrapped = std::fmod(coordinate, box_length);
    return wrapped < 0.0 ? wrapped + box_length : wrapped;
}

inline double minimum_image_delta(double delta, double box_length) {
    return delta - box_length * std::round(delta / box_length);
}

inline double distance_squared_periodic(const Particle& first,
                                        const Particle& second,
                                        double box_length) {
    const double dx = minimum_image_delta(second.x - first.x, box_length);
    const double dy = minimum_image_delta(second.y - first.y, box_length);
    return dx * dx + dy * dy;
}

inline bool are_neighbors_periodic(const Particle& first,
                                   const Particle& second,
                                   const Parameters& parameters) {
    const double radius = parameters.interaction_radius;
    return distance_squared_periodic(first, second, parameters.box_length) <=
           radius * radius;
}

}  // namespace tp2
