#pragma once

#include <filesystem>
#include <string>

namespace sister::hoa {

[[nodiscard]] std::string buildDashboardSnapshotJson(
    const std::filesystem::path& repositoryRoot);

} // namespace sister::hoa
