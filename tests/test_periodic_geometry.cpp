#include "core/periodic_geometry.hpp"

#include <cassert>
#include <cmath>

namespace {

constexpr double kTolerance = 1e-12;

void expect_close(double actual, double expected) {
    assert(std::abs(actual - expected) <= kTolerance);
}

void test_wrap() {
    expect_close(tp2::periodic_wrap(10.2, 10.0), 0.2);
    expect_close(tp2::periodic_wrap(-0.2, 10.0), 9.8);
    expect_close(tp2::periodic_wrap(-20.2, 10.0), 9.8);
}

void test_minimum_image_across_x_boundary() {
    const tp2::Particle first{0, 0.1, 5.0, 0.0};
    const tp2::Particle second{1, 9.9, 5.0, 0.0};
    expect_close(tp2::distance_squared_periodic(first, second, 10.0), 0.04);
}

void test_neighbor_boundary_is_inclusive() {
    const tp2::Parameters parameters;
    const tp2::Particle first{0, 0.0, 0.0, 0.0};
    const tp2::Particle at_radius{1, 1.0, 0.0, 0.0};
    const tp2::Particle outside_radius{2, 1.0 + 1e-9, 0.0, 0.0};

    assert(tp2::are_neighbors_periodic(first, at_radius, parameters));
    assert(!tp2::are_neighbors_periodic(first, outside_radius, parameters));
}

void test_minimum_image_across_corner() {
    const tp2::Particle first{0, 0.1, 0.1, 0.0};
    const tp2::Particle second{1, 9.9, 9.9, 0.0};
    expect_close(tp2::distance_squared_periodic(first, second, 10.0), 0.08);
}

}  // namespace

int main() {
    test_wrap();
    test_minimum_image_across_x_boundary();
    test_neighbor_boundary_is_inclusive();
    test_minimum_image_across_corner();
}
