#pragma once

#include "praxis/TargetRegistry.hpp"

#include <string>
#include <vector>

namespace praxis {

enum class ObservationState { ready, degraded, unavailable, unknown };

struct ObservationCheck {
    std::string id;
    ObservationState state{ObservationState::unknown};
    std::string detail;
};

struct TargetObservation {
    std::string targetId;
    ObservationState state{ObservationState::unknown};
    std::vector<ObservationCheck> checks;
};

[[nodiscard]] TargetObservation observeTarget(const TargetDefinition& target);
[[nodiscard]] std::string_view toString(ObservationState state) noexcept;

} // namespace praxis
