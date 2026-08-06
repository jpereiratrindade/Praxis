#include "sister/hoa/DashboardSnapshot.hpp"

#include "sister/hoa/GovernanceBaseline.hpp"
#include "sister/hoa/Version.hpp"

#include <chrono>
#include <ctime>
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
    if (!std::filesystem::is_directory(directory, error)) {
        return 0;
    }

    std::size_t count = 0;
    for (const auto& entry : std::filesystem::directory_iterator(directory, error)) {
        if (error) {
            break;
        }
        if (entry.is_regular_file()) {
            ++count;
        }
    }
    return count;
}

} // namespace

std::string buildDashboardSnapshotJson(const std::filesystem::path& repositoryRoot) {
    const auto report = inspectGovernanceBaseline(repositoryRoot);
    const auto scenarioCount = countRegularFiles(repositoryRoot / "harness/scenarios");
    const auto evidenceCount = countRegularFiles(repositoryRoot / "harness/evidence");
    const auto reportCount = countRegularFiles(repositoryRoot / "harness/reports");

    std::ostringstream output;
    output << "{\n"
           << "  \"schema\": \"sister-hoa-dashboard/0.1\",\n"
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
           << "  \"harness\": {\n"
           << "    \"scenarios\": " << scenarioCount << ",\n"
           << "    \"evidence_files\": " << evidenceCount << ",\n"
           << "    \"report_files\": " << reportCount << "\n"
           << "  }\n"
           << "}\n";
    return output.str();
}

} // namespace sister::hoa
