#pragma once

#include "sister/hoa/TargetRegistry.hpp"

#include <filesystem>
#include <string>
#include <string_view>

namespace sister::hoa {

struct ActionPlanResult {
    std::string id;
    std::filesystem::path path;
};

[[nodiscard]] bool isKnownAction(std::string_view operation) noexcept;
[[nodiscard]] ActionPlanResult createActionPlan(
    const std::filesystem::path& repositoryRoot,
    const TargetDefinition& target,
    std::string_view operation);

} // namespace sister::hoa
