#pragma once

#include <filesystem>
#include <span>
#include <string_view>

namespace praxis {

int runCommand(
    std::span<const std::string_view> arguments,
    const std::filesystem::path& repositoryRoot);

} // namespace praxis
