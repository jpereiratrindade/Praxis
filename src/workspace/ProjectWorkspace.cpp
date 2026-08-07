#include "sister/hoa/ProjectWorkspace.hpp"
#include <stdexcept>

namespace sister::hoa {
namespace {
std::filesystem::path canonicalDirectory(const std::filesystem::path& value) {
    std::error_code error;
    const auto absolute = std::filesystem::absolute(value, error);
    if (error) throw std::runtime_error("não foi possível resolver o workspace: " + value.string());
    const auto canonical = std::filesystem::weakly_canonical(absolute, error);
    if (error || !std::filesystem::is_directory(canonical)) {
        throw std::runtime_error("workspace inexistente ou inválido: " + value.string());
    }
    return canonical;
}
}

ProjectWorkspace::ProjectWorkspace(std::filesystem::path root, WorkspaceSelectionSource source)
    : root_(canonicalDirectory(root)), source_(source) {}
const std::filesystem::path& ProjectWorkspace::root() const noexcept { return root_; }
WorkspaceSelectionSource ProjectWorkspace::selectionSource() const noexcept { return source_; }
std::filesystem::path ProjectWorkspace::resolve(const std::filesystem::path& relative) const {
    if (relative.is_absolute()) throw std::runtime_error("caminho absoluto não permitido no workspace");
    const auto result = std::filesystem::weakly_canonical(root_ / relative);
    if (!contains(result)) throw std::runtime_error("caminho escapa da fronteira do workspace: " + relative.string());
    return result;
}
bool ProjectWorkspace::contains(const std::filesystem::path& candidate) const {
    const auto normalized = std::filesystem::weakly_canonical(candidate);
    auto rootIt = root_.begin();
    auto valueIt = normalized.begin();
    for (; rootIt != root_.end(); ++rootIt, ++valueIt) {
        if (valueIt == normalized.end() || *rootIt != *valueIt) return false;
    }
    return true;
}
bool ProjectWorkspace::hasHoaManifest() const { return std::filesystem::is_regular_file(root_ / ".hoa/project.yaml"); }
bool ProjectWorkspace::hasCMakeProject() const { return std::filesystem::is_regular_file(root_ / "CMakeLists.txt"); }
bool ProjectWorkspace::hasGitRepository() const { return std::filesystem::exists(root_ / ".git"); }
std::string toString(const WorkspaceSelectionSource source) {
    return source == WorkspaceSelectionSource::command_line ? "command-line" : "current-directory";
}
} // namespace sister::hoa
