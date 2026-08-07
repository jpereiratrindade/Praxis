#include "sister/hoa/TargetRegistry.hpp"

#include <algorithm>
#include <cstdlib>
#include <fstream>
#include <sstream>
#include <stdexcept>

namespace sister::hoa {
namespace {

std::string trim(std::string value) {
    const auto first = value.find_first_not_of(" \t\r\n");
    if (first == std::string::npos) return {};
    const auto last = value.find_last_not_of(" \t\r\n");
    return value.substr(first, last - first + 1U);
}

std::vector<std::string> splitCsv(const std::string& value) {
    std::vector<std::string> result;
    std::stringstream stream(value);
    std::string item;
    while (std::getline(stream, item, ',')) {
        item = trim(item);
        if (!item.empty()) result.push_back(item);
    }
    return result;
}

TargetDefinition loadTarget(const std::filesystem::path& path) {
    std::ifstream input(path);
    if (!input) throw std::runtime_error("não foi possível abrir target: " + path.string());

    TargetDefinition target;
    std::string line;
    while (std::getline(input, line)) {
        line = trim(line);
        if (line.empty() || line.starts_with('#')) continue;
        const auto separator = line.find('=');
        if (separator == std::string::npos) continue;
        const auto key = trim(line.substr(0, separator));
        const auto value = trim(line.substr(separator + 1U));
        if (key == "id") target.id = value;
        else if (key == "name") target.name = value;
        else if (key == "kind") target.kind = value;
        else if (key == "repository") target.repository = expandUserPath(value);
        else if (key == "host") target.host = value;
        else if (key == "port" && !value.empty()) target.port = static_cast<std::uint16_t>(std::stoul(value));
        else if (key == "observations") target.observations = splitCsv(value);
        else if (key == "actions") target.actions = splitCsv(value);
    }
    if (target.id.empty() || target.name.empty()) {
        throw std::runtime_error("target inválido: " + path.string());
    }
    return target;
}

} // namespace

std::filesystem::path expandUserPath(const std::string_view value) {
    if (!value.starts_with("~/")) return std::filesystem::path(value);
    const char* home = std::getenv("HOME");
    if (home == nullptr) return std::filesystem::path(value);
    return std::filesystem::path(home) / std::string(value.substr(2));
}

TargetRegistry::TargetRegistry(std::filesystem::path repositoryRoot) {
    const auto directory = repositoryRoot / "config" / "targets";
    if (!std::filesystem::exists(directory)) return;
    for (const auto& entry : std::filesystem::directory_iterator(directory)) {
        if (entry.is_regular_file() && entry.path().extension() == ".target") {
            targets_.push_back(loadTarget(entry.path()));
        }
    }
    std::ranges::sort(targets_, {}, &TargetDefinition::id);
}

const std::vector<TargetDefinition>& TargetRegistry::targets() const noexcept { return targets_; }

const TargetDefinition* TargetRegistry::find(const std::string_view id) const noexcept {
    for (const auto& target : targets_) if (target.id == id) return &target;
    return nullptr;
}

} // namespace sister::hoa
