#pragma once
#include <filesystem>
#include <string>

namespace praxis {

enum class WorkspaceSelectionSource { command_line, current_directory };

class ProjectWorkspace final {
public:
    ProjectWorkspace(std::filesystem::path root, WorkspaceSelectionSource source);
    [[nodiscard]] const std::filesystem::path& root() const noexcept;
    [[nodiscard]] WorkspaceSelectionSource selectionSource() const noexcept;
    [[nodiscard]] std::filesystem::path resolve(const std::filesystem::path& relative) const;
    [[nodiscard]] bool contains(const std::filesystem::path& candidate) const;
    [[nodiscard]] bool hasHoaManifest() const;
    [[nodiscard]] bool hasCMakeProject() const;
    [[nodiscard]] bool hasGitRepository() const;
private:
    std::filesystem::path root_;
    WorkspaceSelectionSource source_;
};

[[nodiscard]] std::string toString(WorkspaceSelectionSource source);

} // namespace praxis
