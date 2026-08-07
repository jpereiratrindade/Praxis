#pragma once

#include <cstdint>
#include <filesystem>
#include <optional>
#include <string>
#include <string_view>
#include <vector>

namespace sister::hoa {

struct TargetDefinition {
    std::string id;
    std::string name;
    std::string kind;
    std::filesystem::path repository;
    std::string host;
    std::uint16_t port{0};
    std::vector<std::string> observations;
    std::vector<std::string> actions;
};

class TargetRegistry {
public:
    explicit TargetRegistry(std::filesystem::path repositoryRoot);

    [[nodiscard]] const std::vector<TargetDefinition>& targets() const noexcept;
    [[nodiscard]] const TargetDefinition* find(std::string_view id) const noexcept;

private:
    std::vector<TargetDefinition> targets_;
};

[[nodiscard]] std::filesystem::path expandUserPath(std::string_view value);

} // namespace sister::hoa
