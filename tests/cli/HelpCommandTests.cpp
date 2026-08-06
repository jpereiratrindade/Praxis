#include "sister/hoa/CommandRegistry.hpp"

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
    const auto general = sister::hoa::renderGeneralHelp();
    require(general.find("dashboard serve") != std::string::npos, "general help must list dashboard serve");
    require(general.find("operações mutáveis  desabilitadas") != std::string::npos,
            "general help must state mutation policy");

    const auto doctor = sister::hoa::renderCommandHelp("doctor");
    require(doctor.find("Risco: read") != std::string::npos, "doctor help must expose risk");

    const auto dashboard = sister::hoa::renderCommandHelp("dashboard");
    require(dashboard.find("GET e HEAD") != std::string::npos, "dashboard help must expose HTTP boundary");

    require(sister::hoa::findCommand("status") != nullptr, "status descriptor must exist");
    require(sister::hoa::findCommand("unknown") == nullptr, "unknown descriptor must not exist");

    std::cout << "HelpCommandTests: PASS\n";
    return 0;
}
