#pragma once
#include <filesystem>
#include <string>

namespace sister::hoa {

enum class GitSyncState { not_repository, up_to_date, ahead, behind, diverged, dirty, unavailable };
struct GitSyncStatus {
    GitSyncState state{GitSyncState::unavailable};
    std::string branch;
    std::string localCommit;
    std::string remoteCommit;
    int ahead{};
    int behind{};
    bool dirty{};
};
[[nodiscard]] GitSyncStatus inspectGitSync(const std::filesystem::path& root, bool fetchRemote);
[[nodiscard]] std::string toString(GitSyncState state);

} // namespace sister::hoa
