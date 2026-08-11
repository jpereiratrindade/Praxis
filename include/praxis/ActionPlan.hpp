#pragma once

#include "praxis/TargetRegistry.hpp"

#include <filesystem>
#include <string>
#include <string_view>

namespace praxis {

struct ActionPlanResult {
    std::string id;
    std::filesystem::path path;
};

[[nodiscard]] bool isKnownAction(std::string_view operation) noexcept;
[[nodiscard]] ActionPlanResult createActionPlan(
    const std::filesystem::path& repositoryRoot,
    const TargetDefinition& target,
    std::string_view operation);

} // namespace praxis
