#include "sister/hoa/Commands.hpp"

#include "sister/hoa/GovernanceBaseline.hpp"
#include "sister/hoa/Version.hpp"

#include <iostream>
#include <string_view>

namespace sister::hoa {
namespace {

void printUsage() {
    std::cout
        << "Uso: sister-ops <status|health|doctor|governance check>\n"
        << "      sister-ops --version\n";
}

int commandStatus(const std::filesystem::path& repositoryRoot) {
    std::cout << "SisTer-HOA\n"
              << "  version: " << kVersion << '\n'
              << "  document: " << kDocumentVersion << '\n'
              << "  implementation: native C++23\n"
              << "  harness_phase: " << kHarnessPhase << '\n'
              << "  mode: deterministic-no-llm\n"
              << "  repository: " << repositoryRoot.string() << '\n';
    return 0;
}

int printGovernance(const GovernanceReport& report, const bool verbose) {
    for (const auto& check : report.checks) {
        if (verbose || !check.ok) {
            std::cout << (check.ok ? "PASS" : "FAIL") << "  "
                      << check.id << " — " << check.description << '\n';
        }
    }

    std::cout << (report.agentCount >= 2 ? "PASS" : "FAIL")
              << "  agents — " << report.agentCount << " registered\n";
    std::cout << (report.skillCount >= 3 ? "PASS" : "FAIL")
              << "  skills — " << report.skillCount << " registered\n";
    std::cout << "\nGovernance baseline: " << (report.ok() ? "READY" : "NOT_READY") << '\n';
    return report.ok() ? 0 : 4;
}

int commandHealth(const std::filesystem::path& repositoryRoot) {
    const auto report = inspectGovernanceBaseline(repositoryRoot);
    std::cout << "SisTer-HOA health\n";
    std::cout << "  native_core: PASS\n";
    std::cout << "  language_standard: " << kLanguageBaseline << '\n';
    std::cout << "  governance: " << (report.ok() ? "PASS" : "FAIL") << '\n';
    std::cout << "  agents: " << report.agentCount << '\n';
    std::cout << "  skills: " << report.skillCount << '\n';
    return report.ok() ? 0 : 4;
}

int commandDoctor(const std::filesystem::path& repositoryRoot) {
    std::cout << "SisTer-HOA doctor\n\n";
    const auto report = inspectGovernanceBaseline(repositoryRoot);
    const auto result = printGovernance(report, true);
    std::cout << "\nHarness H0: " << (result == 0 ? "READY" : "NOT_READY") << '\n';
    std::cout << "LLM provider: DISABLED (expected in H0)\n";
    std::cout << "Mutating skills: DISABLED (expected in H0)\n";
    return result;
}

} // namespace

int runCommand(
    const std::span<const std::string_view> arguments,
    const std::filesystem::path& repositoryRoot) {
    if (arguments.empty()) {
        printUsage();
        return 2;
    }

    if (arguments[0] == "--version" || arguments[0] == "version") {
        std::cout << "sister-ops " << kVersion << " (C++23)\n";
        return 0;
    }
    if (arguments[0] == "status") {
        return commandStatus(repositoryRoot);
    }
    if (arguments[0] == "health") {
        return commandHealth(repositoryRoot);
    }
    if (arguments[0] == "doctor") {
        return commandDoctor(repositoryRoot);
    }
    if (arguments.size() == 2 && arguments[0] == "governance" && arguments[1] == "check") {
        return printGovernance(inspectGovernanceBaseline(repositoryRoot), true);
    }

    printUsage();
    return 2;
}

} // namespace sister::hoa
