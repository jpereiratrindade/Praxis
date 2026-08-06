#include "sister/hoa/ReadOnlyHttpServer.hpp"

#include "sister/hoa/DashboardSnapshot.hpp"

#include <array>
#include <atomic>
#include <cerrno>
#include <csignal>
#include <cstring>
#include <fstream>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>

#if defined(__unix__) || defined(__APPLE__)
#include <arpa/inet.h>
#include <netinet/in.h>
#include <poll.h>
#include <sys/socket.h>
#include <unistd.h>
#else
#error "The H0 read-only dashboard server currently supports POSIX systems only."
#endif

namespace sister::hoa {
namespace {

volatile std::sig_atomic_t gStopRequested = 0;

void handleSignal(int) {
    gStopRequested = 1;
}

std::string readFile(const std::filesystem::path& path) {
    std::ifstream input(path, std::ios::binary);
    if (!input) {
        return {};
    }
    std::ostringstream buffer;
    buffer << input.rdbuf();
    return buffer.str();
}

std::string normalizedTarget(const std::string_view rawTarget) {
    const auto query = rawTarget.find('?');
    const std::string_view path = query == std::string_view::npos
        ? rawTarget
        : rawTarget.substr(0, query);
    return path.empty() ? "/" : std::string{path};
}

std::string responseText(const HttpResponse& response, const bool headOnly) {
    std::ostringstream output;
    output << "HTTP/1.1 " << response.status << ' ' << response.reason << "\r\n"
           << "Content-Type: " << response.contentType << "\r\n"
           << "Content-Length: " << response.body.size() << "\r\n"
           << "Cache-Control: no-store\r\n"
           << "Content-Security-Policy: default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; img-src 'self' data:; frame-ancestors 'none'\r\n"
           << "Referrer-Policy: no-referrer\r\n"
           << "X-Content-Type-Options: nosniff\r\n"
           << "X-Frame-Options: DENY\r\n";
    if (!response.allow.empty()) {
        output << "Allow: " << response.allow << "\r\n";
    }
    output << "Connection: close\r\n\r\n";
    if (!headOnly) {
        output << response.body;
    }
    return output.str();
}

bool sendAll(const int socketDescriptor, const std::string_view data) {
    std::size_t sent = 0;
    while (sent < data.size()) {
        const auto result = ::send(
            socketDescriptor,
            data.data() + sent,
            data.size() - sent,
            0);
        if (result <= 0) {
            return false;
        }
        sent += static_cast<std::size_t>(result);
    }
    return true;
}

} // namespace

HttpResponse routeReadOnlyRequest(
    const std::string_view method,
    const std::string_view target,
    const std::filesystem::path& repositoryRoot) {
    if (method != "GET" && method != "HEAD") {
        return HttpResponse{
            .status = 405,
            .reason = "Method Not Allowed",
            .body = "SisTer-HOA dashboard is read-only. Allowed methods: GET, HEAD.\n",
            .allow = "GET, HEAD",
        };
    }

    const auto path = normalizedTarget(target);
    if (path == "/api/snapshot") {
        return HttpResponse{
            .status = 200,
            .reason = "OK",
            .contentType = "application/json; charset=utf-8",
            .body = buildDashboardSnapshotJson(repositoryRoot),
            .allow = {},
        };
    }

    std::filesystem::path asset;
    std::string contentType;
    if (path == "/" || path == "/index.html") {
        asset = repositoryRoot / "web/index.html";
        contentType = "text/html; charset=utf-8";
    } else if (path == "/assets/app.css") {
        asset = repositoryRoot / "web/assets/app.css";
        contentType = "text/css; charset=utf-8";
    } else if (path == "/assets/app.js") {
        asset = repositoryRoot / "web/assets/app.js";
        contentType = "text/javascript; charset=utf-8";
    } else {
        return HttpResponse{
            .status = 404,
            .reason = "Not Found",
            .body = "Not found.\n",
            .allow = {},
        };
    }

    auto body = readFile(asset);
    if (body.empty()) {
        return HttpResponse{
            .status = 500,
            .reason = "Internal Server Error",
            .body = "Dashboard asset unavailable.\n",
            .allow = {},
        };
    }

    return HttpResponse{
        .status = 200,
        .reason = "OK",
        .contentType = std::move(contentType),
        .body = std::move(body),
        .allow = {},
    };
}

int serveReadOnlyDashboard(
    const std::filesystem::path& repositoryRoot,
    const std::uint16_t port) {
    gStopRequested = 0;
    std::signal(SIGINT, handleSignal);
    std::signal(SIGTERM, handleSignal);

    const int server = ::socket(AF_INET, SOCK_STREAM, 0);
    if (server < 0) {
        throw std::runtime_error(std::string{"cannot create socket: "} + std::strerror(errno));
    }

    const int reuseAddress = 1;
    ::setsockopt(server, SOL_SOCKET, SO_REUSEADDR, &reuseAddress, sizeof(reuseAddress));

    sockaddr_in address{};
    address.sin_family = AF_INET;
    address.sin_port = htons(port);
    address.sin_addr.s_addr = htonl(INADDR_LOOPBACK);

    if (::bind(server, reinterpret_cast<const sockaddr*>(&address), sizeof(address)) < 0) {
        const auto message = std::string{"cannot bind 127.0.0.1:"} + std::to_string(port) + ": " + std::strerror(errno);
        ::close(server);
        throw std::runtime_error(message);
    }

    if (::listen(server, 16) < 0) {
        const auto message = std::string{"cannot listen: "} + std::strerror(errno);
        ::close(server);
        throw std::runtime_error(message);
    }

    std::cout << "SisTer-HOA — Painel de Observação\n"
              << "URL: http://127.0.0.1:" << port << "\n\n"
              << "Modo: READ_ONLY\n"
              << "Métodos aceitos: GET, HEAD\n"
              << "Operações mutáveis: DISABLED\n"
              << "Pressione Ctrl+C para encerrar.\n";

    while (!gStopRequested) {
        pollfd descriptor{.fd = server, .events = POLLIN, .revents = 0};
        const int ready = ::poll(&descriptor, 1, 250);
        if (ready < 0) {
            if (errno == EINTR) {
                continue;
            }
            std::cerr << "AVISO: falha no poll: " << std::strerror(errno) << '\n';
            continue;
        }
        if (ready == 0 || (descriptor.revents & POLLIN) == 0) {
            continue;
        }

        sockaddr_in clientAddress{};
        socklen_t clientSize = sizeof(clientAddress);
        const int client = ::accept(
            server,
            reinterpret_cast<sockaddr*>(&clientAddress),
            &clientSize);
        if (client < 0) {
            if (errno == EINTR) {
                continue;
            }
            std::cerr << "AVISO: falha ao aceitar conexão: " << std::strerror(errno) << '\n';
            continue;
        }

        std::array<char, 8192> buffer{};
        const auto received = ::recv(client, buffer.data(), buffer.size() - 1U, 0);
        if (received > 0) {
            std::istringstream request(std::string{buffer.data(), static_cast<std::size_t>(received)});
            std::string method;
            std::string target;
            std::string version;
            request >> method >> target >> version;

            const auto response = routeReadOnlyRequest(method, target, repositoryRoot);
            const auto serialized = responseText(response, method == "HEAD");
            sendAll(client, serialized);
        }
        ::close(client);
    }

    ::close(server);
    std::cout << "\nPainel encerrado. Nenhuma operação foi executada.\n";
    return 0;
}

} // namespace sister::hoa
