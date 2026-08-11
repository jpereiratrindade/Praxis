#pragma once

#include <cstdint>
#include <filesystem>
#include <string>
#include <string_view>

namespace praxis {

struct HttpResponse {
    int status{500};
    std::string reason{"Internal Server Error"};
    std::string contentType{"text/plain; charset=utf-8"};
    std::string body;
    std::string allow;
};

[[nodiscard]] HttpResponse routeReadOnlyRequest(
    std::string_view method,
    std::string_view target,
    const std::filesystem::path& repositoryRoot);

int serveReadOnlyDashboard(
    const std::filesystem::path& repositoryRoot,
    std::uint16_t port);

} // namespace praxis
