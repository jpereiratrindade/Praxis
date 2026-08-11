#include "praxis/Commands.hpp"

#include "praxis/CommandRegistry.hpp"
#include "praxis/DashboardSnapshot.hpp"
#include "praxis/GovernanceBaseline.hpp"
#include "praxis/ReadOnlyHttpServer.hpp"
#include "praxis/TargetRegistry.hpp"
#include "praxis/ExternalObservation.hpp"
#include "praxis/ActionPlan.hpp"
#include "praxis/Version.hpp"

#include <charconv>
#include <cstdint>
#include <iostream>
#include <algorithm>
#include <iomanip>
#include <optional>
#include <string>
#include <string_view>

namespace praxis {
namespace {

int commandStatus(const std::filesystem::path& repositoryRoot) {
    std::cout << "Praxis\n"
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
    std::cout << (report.skillCount >= 9 ? "PASS" : "FAIL")
              << "  skills — " << report.skillCount << " registered\n";
    std::cout << "\nGovernance baseline: " << (report.ok() ? "READY" : "NOT_READY") << '\n';
    return report.ok() ? 0 : 4;
}

int commandHealth(const std::filesystem::path& repositoryRoot) {
    const auto report = inspectGovernanceBaseline(repositoryRoot);
    std::cout << "Praxis health\n";
    std::cout << "  native_core: PASS\n";
    std::cout << "  language_standard: " << kLanguageBaseline << '\n';
    std::cout << "  governance: " << (report.ok() ? "PASS" : "FAIL") << '\n';
    std::cout << "  agents: " << report.agentCount << '\n';
    std::cout << "  skills: " << report.skillCount << '\n';
    std::cout << "  dashboard: READ_ONLY\n";
    return report.ok() ? 0 : 4;
}

int commandDoctor(const std::filesystem::path& repositoryRoot) {
    std::cout << "Praxis doctor\n\n";
    const auto report = inspectGovernanceBaseline(repositoryRoot);
    const auto result = printGovernance(report, true);
    std::cout << "\nHarness H1: " << (result == 0 ? "READY" : "NOT_READY") << '\n';
    std::cout << "LLM provider: DISABLED (expected in H1)\n";
    std::cout << "External execution: DISABLED; action planning: ENABLED (expected in H1)\n";
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
            std::cerr << "ERRO: uso: praxis dashboard snapshot\n";
            return 2;
        }
        std::cout << buildDashboardSnapshotJson(repositoryRoot);
        return 0;
    }

    if (arguments[0] == "serve") {
        std::uint16_t port = 8090;
        for (std::size_t index = 1; index < arguments.size(); ++index) {
            if (arguments[index] != "--port" || index + 1U >= arguments.size()) {
                std::cerr << "ERRO: uso: praxis dashboard serve [--port 8090]\n";
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


int commandTarget(const std::span<const std::string_view> arguments,
                  const std::filesystem::path& repositoryRoot) {
    TargetRegistry registry(repositoryRoot);
    if (arguments.empty() || arguments[0] == "catalog") {
        std::cout << "TARGET             KIND          FILESYSTEM   TCP         ACTIONS\n";
        for (const auto& target : registry.targets()) {
            const auto observation = observeTarget(target);
            std::string filesystem = "—";
            std::string tcp = "—";
            for (const auto& check : observation.checks) {
                if (check.id == "filesystem") filesystem = std::string(toString(check.state));
                if (check.id == "tcp") tcp = std::string(toString(check.state));
            }
            std::cout << std::left << std::setw(19) << target.id
                      << std::setw(14) << target.kind
                      << std::setw(13) << filesystem
                      << std::setw(12) << tcp
                      << target.actions.size() << '\n';
        }
        std::cout << "\nModo: READ_ONLY\n";
        return 0;
    }
    if (arguments[0] == "inspect" && arguments.size() == 2U) {
        const auto* target = registry.find(arguments[1]);
        if (target == nullptr) {
            std::cerr << "ERRO: target não registrado: " << arguments[1] << '\n';
            return 2;
        }
        const auto observation = observeTarget(*target);
        std::cout << "Target: " << target->name << " [" << target->id << "]\n"
                  << "Kind: " << target->kind << "\n"
                  << "Repository: " << target->repository.string() << "\n"
                  << "Result: " << toString(observation.state) << "\n\n";
        for (const auto& check : observation.checks) {
            std::cout << std::left << std::setw(14) << check.id
                      << std::setw(14) << toString(check.state)
                      << check.detail << '\n';
        }
        std::cout << "\nAuthority: observe=allowed, mutate=plan-only\n";
        return observation.state == ObservationState::unavailable ? 5 : 0;
    }
    std::cerr << "ERRO: uso: praxis target <catalog|inspect ID>\n";
    return 2;
}

int commandEcosystem(const std::span<const std::string_view> arguments,
                     const std::filesystem::path& repositoryRoot) {
    if (arguments.size() != 1U || (arguments[0] != "status" && arguments[0] != "health")) {
        std::cerr << "ERRO: uso: praxis ecosystem <status|health>\n";
        return 2;
    }
    TargetRegistry registry(repositoryRoot);
    std::cout << "Ecossistema SisTer\n\nTARGET             RESULT        CHECKS\n";
    bool allReady = true;
    for (const auto& target : registry.targets()) {
        const auto observation = observeTarget(target);
        allReady = allReady && observation.state == ObservationState::ready;
        std::cout << std::left << std::setw(19) << target.id
                  << std::setw(14) << toString(observation.state)
                  << observation.checks.size() << '\n';
    }
    std::cout << "\nModo: READ_ONLY\nHarness: H1 OBSERVATION\n";
    return allReady ? 0 : 5;
}

int commandAction(const std::span<const std::string_view> arguments,
                  const std::filesystem::path& repositoryRoot) {
    if (arguments.empty() || arguments[0] == "catalog") {
        std::cout << "Ações externas registradas\n\n"
                  << "  project.build    mutate_local   plan-only\n"
                  << "  project.test     mutate_local   plan-only\n"
                  << "  service.restart  mutate_local   plan-only\n\n"
                  << "Execução externa: DISABLED\n";
        return 0;
    }
    if (arguments[0] == "plan" && arguments.size() == 4U && arguments[2] == "--target") {
        const auto operation = arguments[1];
        if (!isKnownAction(operation)) {
            std::cerr << "ERRO: ação desconhecida: " << operation << '\n';
            return 2;
        }
        TargetRegistry registry(repositoryRoot);
        const auto* target = registry.find(arguments[3]);
        if (target == nullptr) {
            std::cerr << "ERRO: target não registrado: " << arguments[3] << '\n';
            return 2;
        }
        if (std::ranges::find(target->actions, operation) == target->actions.end()) {
            std::cerr << "ERRO: ação não autorizada pelo target: " << operation << '\n';
            return 3;
        }
        const auto plan = createActionPlan(repositoryRoot, *target, operation);
        std::cout << "Plano: " << plan.id << "\n"
                  << "Operação: " << operation << "\n"
                  << "Alvo: " << target->id << "\n"
                  << "Risco: mutate_local\n"
                  << "Estado: PLANNED_NOT_EXECUTED\n"
                  << "Execução externa: DISABLED\n\n"
                  << "Plano salvo em: " << plan.path.string() << '\n';
        return 0;
    }
    if (arguments[0] == "apply") {
        std::cerr << "ERRO: action apply ainda está desabilitado no H1; somente planos são permitidos\n";
        return 4;
    }
    std::cerr << "ERRO: uso: praxis action <catalog|plan OP --target ID>\n";
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
        std::cout << "praxis " << kVersion << " (C++23)\n";
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
    if (arguments[0] == "target") {
        return commandTarget(arguments.subspan(1), repositoryRoot);
    }
    if (arguments[0] == "ecosystem") {
        return commandEcosystem(arguments.subspan(1), repositoryRoot);
    }
    if (arguments[0] == "action") {
        return commandAction(arguments.subspan(1), repositoryRoot);
    }

    std::cerr << "ERRO: comando desconhecido: " << arguments[0] << "\n\n";
    std::cout << renderGeneralHelp();
    return 2;
}

} // namespace praxis
