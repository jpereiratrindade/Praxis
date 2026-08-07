#include "sister/hoa/GovernanceBaseline.hpp"

#include <array>
#include <cstdlib>
#include <system_error>

namespace sister::hoa {
namespace {

constexpr std::array<std::pair<std::string_view, std::string_view>, 31> kRequiredPaths{{
    {"manifest", "project.sister.yaml"},
    {"license", "LICENSE"},
    {"contributing", "CONTRIBUTING.md"},
    {"codeowners", ".github/CODEOWNERS"},
    {"pull-request-template", ".github/pull_request_template.md"},
    {"ai-policy", "policies/ai_usage_policy.md"},
    {"approval-policy", "policies/approval_matrix.md"},
    {"context-policy", "policies/context_boundary_policy.md"},
    {"evidence-policy", "policies/evidence_and_audit_policy.md"},
    {"agent-contract", "contracts/operations/agent.schema.json"},
    {"skill-contract", "contracts/operations/skill.schema.json"},
    {"plan-contract", "contracts/operations/operation-plan.schema.json"},
    {"receipt-contract", "contracts/operations/execution-receipt.schema.json"},
    {"ddd", "docs/architecture/DDD.md"},
    {"adr", "docs/adr/ADR-0001-native-cpp23-core.md"},
    {"dai", "docs/dai/DAI.md"},
    {"tool-contract", "mcp/contracts/operation_registry_tool_contract.md"},
    {"evidence-example", "examples/evidence_log.json"},
    {"governance-validator", "scripts/validate_governance_repo.py"},
    {"dashboard-policy", "policies/read_only_dashboard_policy.md"},
    {"dashboard-adr", "docs/adr/ADR-0002-read-only-observation-dashboard.md"},
    {"dashboard-skill", "harness/skills/dashboard.observe.yaml"},
    {"dashboard-scenario", "harness/scenarios/HOA-EXP-002-dashboard-read-only.md"},
    {"dashboard-html", "web/index.html"},
    {"dashboard-css", "web/assets/app.css"},
    {"dashboard-js", "web/assets/app.js"},
    {"target-contract", "contracts/targets/target.schema.json"},
    {"external-authority-policy", "policies/external_authority_policy.md"},
    {"external-target-adr", "docs/adr/ADR-0003-external-targets-plan-only-actions.md"},
    {"external-scenario", "harness/scenarios/HOA-EXP-003-external-observation.md"},
    {"target-config", "config/targets/sister.target"},
}};

std::size_t countYamlFiles(const std::filesystem::path& directory) {
    std::error_code error;
    if (!std::filesystem::is_directory(directory, error)) {
        return 0;
    }

    std::size_t count = 0;
    for (const auto& entry : std::filesystem::directory_iterator(directory, error)) {
        if (error) {
            return count;
        }
        if (entry.is_regular_file() &&
            (entry.path().extension() == ".yaml" || entry.path().extension() == ".yml")) {
            ++count;
        }
    }
    return count;
}

} // namespace

bool GovernanceReport::ok() const {
    for (const auto& check : checks) {
        if (!check.ok) {
            return false;
        }
    }
    return agentCount >= 2 && skillCount >= 9;
}

std::filesystem::path locateRepositoryRoot(const std::filesystem::path& start) {
    if (const char* configured = std::getenv("SISTER_HOA_HOME")) {
        const std::filesystem::path candidate{configured};
        if (std::filesystem::exists(candidate / "project.sister.yaml")) {
            return std::filesystem::weakly_canonical(candidate);
        }
    }

    std::filesystem::path current = std::filesystem::absolute(start);
    while (!current.empty()) {
        if (std::filesystem::exists(current / "project.sister.yaml") &&
            std::filesystem::exists(current / "CMakeLists.txt")) {
            return std::filesystem::weakly_canonical(current);
        }
        const auto parent = current.parent_path();
        if (parent == current) {
            break;
        }
        current = parent;
    }

    return std::filesystem::path{SISTER_HOA_SOURCE_DIR};
}

GovernanceReport inspectGovernanceBaseline(const std::filesystem::path& repositoryRoot) {
    GovernanceReport report;
    report.repositoryRoot = repositoryRoot;
    report.checks.reserve(kRequiredPaths.size());

    for (const auto& [id, relativePath] : kRequiredPaths) {
        const auto path = repositoryRoot / relativePath;
        report.checks.push_back(GovernanceCheck{
            .id = std::string{id},
            .description = std::string{relativePath},
            .path = path,
            .ok = std::filesystem::exists(path),
        });
    }

    report.agentCount = countYamlFiles(repositoryRoot / "harness/agents");
    report.skillCount = countYamlFiles(repositoryRoot / "harness/skills");
    return report;
}

} // namespace sister::hoa
