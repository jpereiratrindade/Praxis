#include "praxis/ExternalObservation.hpp"

#include <algorithm>
#include <cerrno>
#include <cstring>
#include <sys/socket.h>
#include <netdb.h>
#include <unistd.h>

namespace praxis {
namespace {

bool contains(const std::vector<std::string>& values, const std::string_view value) {
    return std::ranges::find(values, value) != values.end();
}

ObservationCheck checkFilesystem(const TargetDefinition& target) {
    if (target.repository.empty()) return {"filesystem", ObservationState::unknown, "repository não configurado"};
    const bool exists = std::filesystem::exists(target.repository);
    return {"filesystem", exists ? ObservationState::ready : ObservationState::unavailable,
            exists ? target.repository.string() : "ausente: " + target.repository.string()};
}

ObservationCheck checkTcp(const TargetDefinition& target) {
    if (target.host.empty() || target.port == 0U) return {"tcp", ObservationState::unknown, "endpoint não configurado"};
    addrinfo hints{};
    hints.ai_socktype = SOCK_STREAM;
    hints.ai_family = AF_UNSPEC;
    addrinfo* result = nullptr;
    const auto service = std::to_string(target.port);
    if (::getaddrinfo(target.host.c_str(), service.c_str(), &hints, &result) != 0) {
        return {"tcp", ObservationState::unavailable, "falha ao resolver host"};
    }
    bool connected = false;
    for (auto* current = result; current != nullptr && !connected; current = current->ai_next) {
        const int socketFd = ::socket(current->ai_family, current->ai_socktype, current->ai_protocol);
        if (socketFd < 0) continue;
        connected = ::connect(socketFd, current->ai_addr, current->ai_addrlen) == 0;
        ::close(socketFd);
    }
    ::freeaddrinfo(result);
    return {"tcp", connected ? ObservationState::ready : ObservationState::unavailable,
            target.host + ":" + service};
}

} // namespace

std::string_view toString(const ObservationState state) noexcept {
    switch (state) {
        case ObservationState::ready: return "READY";
        case ObservationState::degraded: return "DEGRADED";
        case ObservationState::unavailable: return "UNAVAILABLE";
        case ObservationState::unknown: return "UNKNOWN";
    }
    return "UNKNOWN";
}

TargetObservation observeTarget(const TargetDefinition& target) {
    TargetObservation observation{.targetId = target.id, .state = ObservationState::unknown, .checks = {}};
    if (contains(target.observations, "filesystem")) observation.checks.push_back(checkFilesystem(target));
    if (contains(target.observations, "tcp")) observation.checks.push_back(checkTcp(target));
    observation.state = ObservationState::ready;
    for (const auto& check : observation.checks) {
        if (check.state == ObservationState::unavailable) { observation.state = ObservationState::unavailable; break; }
        if (check.state == ObservationState::degraded) observation.state = ObservationState::degraded;
        if (check.state == ObservationState::unknown && observation.state == ObservationState::ready) observation.state = ObservationState::unknown;
    }
    return observation;
}

} // namespace praxis
