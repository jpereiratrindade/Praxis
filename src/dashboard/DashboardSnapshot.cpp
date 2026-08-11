#include "sister/hoa/DashboardSnapshot.hpp"

#include "sister/hoa/ExternalObservation.hpp"
#include "sister/hoa/GovernanceBaseline.hpp"
#include "sister/hoa/TargetRegistry.hpp"
#include "sister/hoa/Version.hpp"

#include <chrono>
#include <ctime>
#include <filesystem>
#include <iomanip>
#include <sstream>
#include <string_view>
#include <system_error>

namespace sister::hoa {
namespace {

std::string escapeJson(const std::string_view value) {
    std::ostringstream output;
    for (const unsigned char character : value) {
        switch (character) {
        case '\"': output << "\\\""; break;
        case '\\': output << "\\\\"; break;
        case '\b': output << "\\b"; break;
        case '\f': output << "\\f"; break;
        case '\n': output << "\\n"; break;
        case '\r': output << "\\r"; break;
        case '\t': output << "\\t"; break;
        default:
            if (character < 0x20U) {
                output << "\\u" << std::hex << std::setw(4) << std::setfill('0')
                       << static_cast<int>(character) << std::dec;
            } else {
                output << static_cast<char>(character);
            }
        }
    }
    return output.str();
}

std::string utcTimestamp() {
    const auto current = std::chrono::system_clock::now();
    const std::time_t value = std::chrono::system_clock::to_time_t(current);
    std::tm utc{};
#if defined(_WIN32)
    gmtime_s(&utc, &value);
#else
    gmtime_r(&value, &utc);
#endif
    std::ostringstream output;
    output << std::put_time(&utc, "%Y-%m-%dT%H:%M:%SZ");
    return output.str();
}

std::size_t countRegularFiles(const std::filesystem::path& directory) {
    std::error_code error;
    if (!std::filesystem::is_directory(directory, error)) return 0;
    std::size_t count = 0;
    for (const auto& entry : std::filesystem::directory_iterator(directory, error)) {
        if (error) break;
        if (entry.is_regular_file()) ++count;
    }
    return count;
}

std::string_view aggregateState(const std::vector<TargetObservation>& observations) {
    bool degraded = false;
    bool unknown = false;
    for (const auto& observation : observations) {
        if (observation.state == ObservationState::unavailable) return "UNAVAILABLE";
        if (observation.state == ObservationState::degraded) degraded = true;
        if (observation.state == ObservationState::unknown) unknown = true;
    }
    if (degraded) return "DEGRADED";
    if (unknown) return "UNKNOWN";
    return "READY";
}

} // namespace

std::string buildDashboardSnapshotJson(const std::filesystem::path& repositoryRoot) {
    const auto report = inspectGovernanceBaseline(repositoryRoot);
    const auto scenarioCount = countRegularFiles(repositoryRoot / "harness/scenarios");
    const auto evidenceCount = countRegularFiles(repositoryRoot / "harness/evidence");
    const auto reportCount = countRegularFiles(repositoryRoot / "harness/reports");
    const TargetRegistry registry(repositoryRoot);

    std::vector<TargetObservation> observations;
    observations.reserve(registry.targets().size());
    for (const auto& target : registry.targets()) observations.push_back(observeTarget(target));

    std::ostringstream output;
    output << "{\n"
           << "  \"schema\": \"praxis-dashboard/0.3\",\n"
           << "  \"generated_at\": \"" << utcTimestamp() << "\",\n"
           << "  \"system\": {\n"
           << "    \"name\": \"SisTer-HOA\",\n"
           << "    \"version\": \"" << escapeJson(kVersion) << "\",\n"
           << "    \"document\": \"" << escapeJson(kDocumentVersion) << "\",\n"
           << "    \"implementation\": \"native C++23\",\n"
           << "    \"language_standard\": \"" << escapeJson(kLanguageBaseline) << "\",\n"
           << "    \"harness_phase\": \"" << escapeJson(kHarnessPhase) << "\",\n"
           << "    \"mode\": \"deterministic-no-llm\",\n"
           << "    \"repository\": \"" << escapeJson(repositoryRoot.string()) << "\"\n"
           << "  },\n"
           << "  \"safety\": {\n"
           << "    \"dashboard_mode\": \"READ_ONLY\",\n"
           << "    \"bind_address\": \"127.0.0.1\",\n"
           << "    \"allowed_http_methods\": [\"GET\", \"HEAD\"],\n"
           << "    \"mutating_skills_enabled\": false,\n"
           << "    \"external_execution_enabled\": false,\n"
           << "    \"action_planning_enabled\": true,\n"
           << "    \"llm_provider\": \"DISABLED\"\n"
           << "  },\n"
           << "  \"governance\": {\n"
           << "    \"status\": \"" << (report.ok() ? "READY" : "NOT_READY") << "\",\n"
           << "    \"agents\": " << report.agentCount << ",\n"
           << "    \"skills\": " << report.skillCount << ",\n"
           << "    \"checks\": [\n";

    for (std::size_t index = 0; index < report.checks.size(); ++index) {
        const auto& check = report.checks[index];
        output << "      {\"id\": \"" << escapeJson(check.id)
               << "\", \"description\": \"" << escapeJson(check.description)
               << "\", \"ok\": " << (check.ok ? "true" : "false") << "}";
        output << (index + 1U == report.checks.size() ? "\n" : ",\n");
    }

    output << "    ]\n"
           << "  },\n"
           << "  \"ecosystem\": {\n"
           << "    \"status\": \"" << aggregateState(observations) << "\",\n"
           << "    \"targets\": [\n";

    for (std::size_t index = 0; index < registry.targets().size(); ++index) {
        const auto& target = registry.targets()[index];
        const auto& observation = observations[index];
        output << "      {\"id\": \"" << escapeJson(target.id)
               << "\", \"name\": \"" << escapeJson(target.name)
               << "\", \"kind\": \"" << escapeJson(target.kind)
               << "\", \"state\": \"" << toString(observation.state)
               << "\", \"actions\": " << target.actions.size() << ", \"checks\": [";
        for (std::size_t checkIndex = 0; checkIndex < observation.checks.size(); ++checkIndex) {
            const auto& check = observation.checks[checkIndex];
            output << "{\"id\": \"" << escapeJson(check.id)
                   << "\", \"state\": \"" << toString(check.state)
                   << "\", \"detail\": \"" << escapeJson(check.detail) << "\"}";
            if (checkIndex + 1U != observation.checks.size()) output << ',';
        }
        output << "]}" << (index + 1U == registry.targets().size() ? "\n" : ",\n");
    }

    output << "    ]\n"
           << "  },\n"
           << "  \"actions\": {\n"
           << "    \"planning_enabled\": true,\n"
           << "    \"execution_enabled\": false,\n"
           << "    \"catalog\": [\n"
           << "      {\"id\": \"project.build\", \"risk\": \"mutate_local\", \"mode\": \"plan-only\"},\n"
           << "      {\"id\": \"project.test\", \"risk\": \"mutate_local\", \"mode\": \"plan-only\"},\n"
           << "      {\"id\": \"service.restart\", \"risk\": \"mutate_local\", \"mode\": \"plan-only\"}\n"
           << "    ]\n"
           << "  },\n"
           << "  \"harness\": {\n"
           << "    \"scenarios\": " << scenarioCount << ",\n"
           << "    \"evidence_files\": " << evidenceCount << ",\n"
           << "    \"report_files\": " << reportCount << "\n"
           << "  }\n"
           << "}\n";
    return output.str();
}

} // namespace sister::hoa
