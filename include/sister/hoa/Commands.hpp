#pragma once

#include <filesystem>
#include <span>
#include <string_view>

namespace sister::hoa {

int runCommand(
    std::span<const std::string_view> arguments,
    const std::filesystem::path& repositoryRoot);

} // namespace sister::hoa
