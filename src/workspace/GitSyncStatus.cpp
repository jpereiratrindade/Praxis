#include "praxis/GitSyncStatus.hpp"
#include <array>
#include <cstdio>
#include <cstdlib>
#include <stdexcept>
#include <string>
#include <sys/wait.h>

namespace praxis {
namespace {
std::string shellQuote(const std::string& value) {
    std::string out{"'"};
    for (char c : value) out += (c == '\'' ? "'\\''" : std::string(1, c));
    out += '\'';
    return out;
}
std::string run(const std::filesystem::path& root, const std::string& args, int* status = nullptr) {
    const std::string command = "git -C " + shellQuote(root.string()) + " " + args + " 2>/dev/null";
    std::array<char, 256> buffer{};
    std::string output;
    FILE* pipe = popen(command.c_str(), "r");
    if (!pipe) throw std::runtime_error("não foi possível executar git");
    while (fgets(buffer.data(), static_cast<int>(buffer.size()), pipe)) output += buffer.data();
    const int rc = pclose(pipe);
    if (status) *status = WIFEXITED(rc) ? WEXITSTATUS(rc) : 1;
    while (!output.empty() && (output.back() == '\n' || output.back() == '\r')) output.pop_back();
    return output;
}
}

GitSyncStatus inspectGitSync(const std::filesystem::path& root, const bool fetchRemote) {
    GitSyncStatus result;
    int rc = 0;
    run(root, "rev-parse --is-inside-work-tree", &rc);
    if (rc != 0) { result.state = GitSyncState::not_repository; return result; }
    if (fetchRemote) {
        const auto command = "git -C " + shellQuote(root.string()) + " fetch origin --prune >/dev/null 2>&1";
        if (std::system(command.c_str()) != 0) { result.state = GitSyncState::unavailable; return result; }
    }
    result.branch = run(root, "branch --show-current", &rc);
    result.localCommit = run(root, "rev-parse --short HEAD", &rc);
    result.dirty = !run(root, "status --porcelain", &rc).empty();
    if (result.dirty) { result.state = GitSyncState::dirty; return result; }
    result.remoteCommit = run(root, "rev-parse --short origin/" + result.branch, &rc);
    if (rc != 0 || result.branch.empty()) { result.state = GitSyncState::unavailable; return result; }
    const auto counts = run(root, "rev-list --left-right --count HEAD...origin/" + result.branch, &rc);
    if (rc != 0) { result.state = GitSyncState::unavailable; return result; }
    if (std::sscanf(counts.c_str(), "%d%d", &result.ahead, &result.behind) != 2) {
        result.state = GitSyncState::unavailable; return result;
    }
    if (result.ahead == 0 && result.behind == 0) result.state = GitSyncState::up_to_date;
    else if (result.ahead > 0 && result.behind == 0) result.state = GitSyncState::ahead;
    else if (result.ahead == 0 && result.behind > 0) result.state = GitSyncState::behind;
    else result.state = GitSyncState::diverged;
    return result;
}
std::string toString(const GitSyncState state) {
    switch (state) {
        case GitSyncState::not_repository: return "NOT_REPOSITORY";
        case GitSyncState::up_to_date: return "UP_TO_DATE";
        case GitSyncState::ahead: return "AHEAD";
        case GitSyncState::behind: return "BEHIND";
        case GitSyncState::diverged: return "DIVERGED";
        case GitSyncState::dirty: return "DIRTY";
        case GitSyncState::unavailable: return "UNAVAILABLE";
    }
    return "UNAVAILABLE";
}
} // namespace praxis
