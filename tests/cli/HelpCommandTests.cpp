#include "praxis/CommandRegistry.hpp"

#include <cstdlib>
#include <iostream>
#include <string>

namespace {

void require(const bool condition, const char* message) {
    if (!condition) {
        std::cerr << "FAIL: " << message << '\n';
        std::exit(1);
    }
}

} // namespace

int main() {
    const auto general = praxis::renderGeneralHelp();
    require(general.find("dashboard serve") != std::string::npos, "general help must list dashboard serve");
    require(general.find("execução desabilitada") != std::string::npos,
            "general help must state mutation policy");

    const auto doctor = praxis::renderCommandHelp("doctor");
    require(doctor.find("Risco: read") != std::string::npos, "doctor help must expose risk");

    const auto dashboard = praxis::renderCommandHelp("dashboard");
    require(dashboard.find("GET e HEAD") != std::string::npos, "dashboard help must expose HTTP boundary");

    require(praxis::findCommand("target catalog") != nullptr, "target catalog descriptor must exist");
    require(praxis::findCommand("action plan") != nullptr, "action plan descriptor must exist");
    require(praxis::findCommand("status") != nullptr, "status descriptor must exist");
    require(praxis::findCommand("unknown") == nullptr, "unknown descriptor must not exist");

    std::cout << "HelpCommandTests: PASS\n";
    return 0;
}
