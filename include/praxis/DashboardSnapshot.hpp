#pragma once

#include <filesystem>
#include <string>

namespace praxis {

[[nodiscard]] std::string buildDashboardSnapshotJson(
    const std::filesystem::path& repositoryRoot);

} // namespace praxis
