#include "praxis/GovernanceBaseline.hpp"

#include <cstdlib>
#include <iostream>

namespace {

void require(const bool condition, const char* message) {
    if (!condition) {
        std::cerr << "FAIL: " << message << '\n';
        std::exit(1);
    }
}

} // namespace

int main() {
    const auto root = praxis::locateRepositoryRoot(PRAXIS_SOURCE_DIR);
    const auto report = praxis::inspectGovernanceBaseline(root);

    require(report.ok(), "governance baseline must be complete");
    require(report.agentCount >= 2, "at least two agents must be registered");
    require(report.skillCount >= 4, "at least four skills must be registered");

    std::cout << "GovernanceBaselineTests: PASS\n";
    return 0;
}
