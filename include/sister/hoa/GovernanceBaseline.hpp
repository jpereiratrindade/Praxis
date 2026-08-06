#pragma once

#include <filesystem>
#include <string>
#include <vector>

namespace sister::hoa {

struct GovernanceCheck {
    std::string id;
    std::string description;
    std::filesystem::path path;
    bool ok{false};
};

struct GovernanceReport {
    std::filesystem::path repositoryRoot;
    std::vector<GovernanceCheck> checks;
    std::size_t agentCount{0};
    std::size_t skillCount{0};

    [[nodiscard]] bool ok() const;
};

[[nodiscard]] std::filesystem::path locateRepositoryRoot(
    const std::filesystem::path& start = std::filesystem::current_path());

[[nodiscard]] GovernanceReport inspectGovernanceBaseline(
    const std::filesystem::path& repositoryRoot);

} // namespace sister::hoa
