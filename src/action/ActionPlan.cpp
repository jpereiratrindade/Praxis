#include "sister/hoa/ActionPlan.hpp"

#include <chrono>
#include <fstream>
#include <iomanip>
#include <random>
#include <sstream>

namespace sister::hoa {
namespace {

std::string escapeJson(const std::string_view value) {
    std::string out;
    for (const char ch : value) {
        if (ch == '\\' || ch == '"') out.push_back('\\');
        out.push_back(ch);
    }
    return out;
}

std::string planId() {
    const auto now = std::chrono::system_clock::now();
    const auto time = std::chrono::system_clock::to_time_t(now);
    std::tm tm{};
    gmtime_r(&time, &tm);
    std::mt19937 engine{std::random_device{}()};
    std::uniform_int_distribution<unsigned int> distribution(0, 0xFFFFFFU);
    std::ostringstream out;
    out << "plan-action-" << std::put_time(&tm, "%Y%m%d-%H%M%S") << '-' << std::hex << std::setw(6)
        << std::setfill('0') << distribution(engine);
    return out.str();
}

} // namespace

bool isKnownAction(const std::string_view operation) noexcept {
    return operation == "project.build" || operation == "project.test" || operation == "service.restart";
}

ActionPlanResult createActionPlan(const std::filesystem::path& repositoryRoot,
                                  const TargetDefinition& target,
                                  const std::string_view operation) {
    const auto id = planId();
    const auto directory = repositoryRoot / ".sister-hoa" / "plans";
    std::filesystem::create_directories(directory);
    const auto path = directory / (id + ".json");
    std::ofstream output(path);
    output << "{\n"
           << "  \"schema\": \"sister-external-action-plan/0.1\",\n"
           << "  \"id\": \"" << id << "\",\n"
           << "  \"operation\": \"" << escapeJson(operation) << "\",\n"
           << "  \"target\": \"" << escapeJson(target.id) << "\",\n"
           << "  \"risk\": \"mutate_local\",\n"
           << "  \"requires_confirmation\": true,\n"
           << "  \"authorized_by_target\": true,\n"
           << "  \"status\": \"PLANNED_NOT_EXECUTED\",\n"
           << "  \"preconditions\": [\"target_registered\", \"operation_allowlisted\", \"repository_available\"],\n"
           << "  \"postconditions\": [\"exit_status_recorded\", \"evidence_written\"],\n"
           << "  \"execution_enabled\": false\n"
           << "}\n";
    return {id, path};
}

} // namespace sister::hoa
