#include "sister/hoa/Commands.hpp"
#include "sister/hoa/GitSyncStatus.hpp"
#include "sister/hoa/GovernanceBaseline.hpp"
#include "sister/hoa/ProjectWorkspace.hpp"

#include <filesystem>
#include <iostream>
#include <string_view>
#include <vector>

namespace {
void usage() {
    std::cout << "Praxis — Governed Operational Harness (HOA)\n\n"
              << "Praxis implements a Governed Operational Harness (HOA).\n\n"
              << "Uso:\n"
              << "  praxis [--project PATH] workspace inspect\n"
              << "  praxis [--project PATH] workspace sync-status [--fetch]\n"
              << "  praxis <comando-do-operador> [opções]\n";
}
}

int main(int argc, char** argv) {
    try {
        std::filesystem::path project = std::filesystem::current_path();
        auto source = sister::hoa::WorkspaceSelectionSource::current_directory;
        int index = 1;

        if (index < argc && std::string_view{argv[index]} == "--project") {
            if (++index >= argc) {
                usage();
                return 2;
            }
            project = argv[index++];
            source = sister::hoa::WorkspaceSelectionSource::command_line;
        }

        if (index < argc && std::string_view{argv[index]} == "workspace") {
            if (index + 1 >= argc) {
                usage();
                return 2;
            }

            const std::string_view operation{argv[index + 1]};
            const sister::hoa::ProjectWorkspace workspace(project, source);

            if (operation == "sync-status") {
                const bool fetch = index + 2 < argc && std::string_view{argv[index + 2]} == "--fetch";
                const auto status = sister::hoa::inspectGitSync(workspace.root(), fetch);
                std::cout << "Workspace: " << workspace.root().string() << '\n'
                          << "Branch: " << status.branch << '\n'
                          << "Local: " << status.localCommit << '\n'
                          << "Remote: " << status.remoteCommit << '\n'
                          << "Ahead: " << status.ahead << '\n'
                          << "Behind: " << status.behind << '\n'
                          << "State: " << sister::hoa::toString(status.state) << '\n'
                          << "Fetch: " << (fetch ? "executed" : "not-requested") << '\n';
                return status.state == sister::hoa::GitSyncState::up_to_date ? 0 : 5;
            }

            if (operation != "inspect") {
                usage();
                return 2;
            }

            std::cout << "Workspace root: " << workspace.root().string() << '\n'
                      << "Selection source: " << sister::hoa::toString(workspace.selectionSource()) << '\n'
                      << "Manifest: " << (workspace.hasHoaManifest() ? ".hoa/project.yaml" : "not-found") << '\n'
                      << "CMake: " << (workspace.hasCMakeProject() ? "detected" : "not-detected") << '\n'
                      << "Git: " << (workspace.hasGitRepository() ? "detected" : "not-detected") << '\n'
                      << "Access boundary: confined\n";
            return 0;
        }

        if (index == 1 && argc == 1) {
            usage();
            return 0;
        }

        if (source == sister::hoa::WorkspaceSelectionSource::command_line) {
            std::cerr << "ERRO: --project é válido apenas para comandos workspace nesta etapa da migração.\n";
            return 2;
        }

        std::vector<std::string_view> arguments;
        arguments.reserve(argc > index ? static_cast<std::size_t>(argc - index) : 0U);
        for (int argumentIndex = index; argumentIndex < argc; ++argumentIndex) {
            arguments.emplace_back(argv[argumentIndex]);
        }

        const auto operatorRoot = sister::hoa::locateRepositoryRoot();
        return sister::hoa::runCommand(arguments, operatorRoot);
    } catch (const std::exception& error) {
        std::cerr << "ERRO: " << error.what() << '\n';
        return 1;
    }
}
