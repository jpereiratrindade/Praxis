#include "sister/hoa/Commands.hpp"

#include "sister/hoa/CommandRegistry.hpp"
#include "sister/hoa/DashboardSnapshot.hpp"
#include "sister/hoa/GovernanceBaseline.hpp"
#include "sister/hoa/ReadOnlyHttpServer.hpp"
#include "sister/hoa/Version.hpp"

#include <charconv>
#include <cstdint>
#include <iostream>
#include <optional>
#include <string>
#include <string_view>

namespace sister::hoa {
namespace {

int commandStatus(const std::filesystem::path& repositoryRoot) {
    std::cout << "SisTer-HOA\n"
              << "  version: " << kVersion << '\n'
              << "  document: " << kDocumentVersion << '\n'
              << "  implementation: native C++23\n"
              << "  harness_phase: " << kHarnessPhase << '\n'
              << "  mode: deterministic-no-llm\n"
              << "  dashboard: read-only-local\n"
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
    std::cout << (report.skillCount >= 4 ? "PASS" : "FAIL")
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
    std::cout << "  dashboard: READ_ONLY\n";
    return report.ok() ? 0 : 4;
}

int commandDoctor(const std::filesystem::path& repositoryRoot) {
    std::cout << "SisTer-HOA doctor\n\n";
    const auto report = inspectGovernanceBaseline(repositoryRoot);
    const auto result = printGovernance(report, true);
    std::cout << "\nHarness H0: " << (result == 0 ? "READY" : "NOT_READY") << '\n';
    std::cout << "LLM provider: DISABLED (expected in H0)\n";
    std::cout << "Mutating skills: DISABLED (expected in H0)\n";
    std::cout << "Dashboard control authority: NONE\n";
    return result;
}

int commandHelp(const std::span<const std::string_view> arguments) {
    if (arguments.empty()) {
        std::cout << renderGeneralHelp();
        return 0;
    }

    std::string query{arguments.front()};
    for (std::size_t index = 1; index < arguments.size(); ++index) {
        query += ' ';
        query += arguments[index];
    }

    const auto help = renderCommandHelp(query);
    if (help.empty()) {
        std::cerr << "ERRO: comando desconhecido para ajuda: " << query << "\n\n";
        std::cout << renderGeneralHelp();
        return 2;
    }

    std::cout << help;
    return 0;
}

std::optional<std::uint16_t> parsePort(const std::string_view value) {
    unsigned int parsed = 0;
    const auto* begin = value.data();
    const auto* end = value.data() + value.size();
    const auto result = std::from_chars(begin, end, parsed);
    if (result.ec != std::errc{} || result.ptr != end || parsed < 1024U || parsed > 65535U) {
        return std::nullopt;
    }
    return static_cast<std::uint16_t>(parsed);
}

int commandDashboard(
    const std::span<const std::string_view> arguments,
    const std::filesystem::path& repositoryRoot) {
    if (arguments.empty()) {
        std::cout << renderCommandHelp("dashboard");
        return 0;
    }

    if (arguments[0] == "snapshot") {
        if (arguments.size() != 1U) {
            std::cerr << "ERRO: uso: sister-ops dashboard snapshot\n";
            return 2;
        }
        std::cout << buildDashboardSnapshotJson(repositoryRoot);
        return 0;
    }

    if (arguments[0] == "serve") {
        std::uint16_t port = 8090;
        for (std::size_t index = 1; index < arguments.size(); ++index) {
            if (arguments[index] != "--port" || index + 1U >= arguments.size()) {
                std::cerr << "ERRO: uso: sister-ops dashboard serve [--port 8090]\n";
                return 2;
            }
            const auto parsed = parsePort(arguments[index + 1U]);
            if (!parsed) {
                std::cerr << "ERRO: porta inválida; use um valor entre 1024 e 65535\n";
                return 2;
            }
            port = *parsed;
            ++index;
        }
        return serveReadOnlyDashboard(repositoryRoot, port);
    }

    std::cerr << "ERRO: subcomando de dashboard desconhecido: " << arguments[0] << "\n\n";
    std::cout << renderCommandHelp("dashboard");
    return 2;
}

} // namespace

int runCommand(
    const std::span<const std::string_view> arguments,
    const std::filesystem::path& repositoryRoot) {
    if (arguments.empty()) {
        std::cout << renderGeneralHelp();
        return 0;
    }

    if (arguments[0] == "--help" || arguments[0] == "-h") {
        return commandHelp(arguments.subspan(1));
    }
    if (arguments[0] == "help") {
        return commandHelp(arguments.subspan(1));
    }
    if (arguments[0] == "--version" || arguments[0] == "version") {
        std::cout << "sister-ops " << kVersion << " (C++23)\n";
        return 0;
    }
    if (arguments[0] == "status" && arguments.size() == 1U) {
        return commandStatus(repositoryRoot);
    }
    if (arguments[0] == "health" && arguments.size() == 1U) {
        return commandHealth(repositoryRoot);
    }
    if (arguments[0] == "doctor" && arguments.size() == 1U) {
        return commandDoctor(repositoryRoot);
    }
    if (arguments.size() == 2U && arguments[0] == "governance" && arguments[1] == "check") {
        return printGovernance(inspectGovernanceBaseline(repositoryRoot), true);
    }
    if (arguments[0] == "dashboard") {
        return commandDashboard(arguments.subspan(1), repositoryRoot);
    }

    std::cerr << "ERRO: comando desconhecido: " << arguments[0] << "\n\n";
    std::cout << renderGeneralHelp();
    return 2;
}

} // namespace sister::hoa
