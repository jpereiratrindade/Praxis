#include "sister/hoa/DashboardSnapshot.hpp"
#include "sister/hoa/ReadOnlyHttpServer.hpp"

#include <cstdlib>
#include <filesystem>
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
    const std::filesystem::path root{SISTER_HOA_SOURCE_DIR};
    const auto snapshot = sister::hoa::buildDashboardSnapshotJson(root);
    require(snapshot.find("\"dashboard_mode\": \"READ_ONLY\"") != std::string::npos,
            "snapshot must identify read-only mode");
    require(snapshot.find("\"mutating_skills_enabled\": false") != std::string::npos,
            "snapshot must deny mutating skills");
    require(snapshot.find("\"ecosystem\"") != std::string::npos,
            "snapshot must expose ecosystem observations");
    require(snapshot.find("\"project.build\"") != std::string::npos,
            "snapshot must expose the plan-only action catalog");
    require(snapshot.find("\"external_execution_enabled\": false") != std::string::npos,
            "snapshot must deny external execution");

    const auto index = sister::hoa::routeReadOnlyRequest("GET", "/", root);
    require(index.status == 200, "GET / must succeed");
    require(index.contentType.find("text/html") != std::string::npos, "GET / must be HTML");

    const auto head = sister::hoa::routeReadOnlyRequest("HEAD", "/api/snapshot", root);
    require(head.status == 200, "HEAD snapshot must succeed");

    const auto rejected = sister::hoa::routeReadOnlyRequest("POST", "/api/snapshot", root);
    require(rejected.status == 405, "POST must be rejected");
    require(rejected.allow == "GET, HEAD", "405 must advertise allowed methods");

    const auto missing = sister::hoa::routeReadOnlyRequest("GET", "/execute", root);
    require(missing.status == 404, "unknown operational-looking route must not exist");

    std::cout << "DashboardReadOnlyTests: PASS\n";
    return 0;
}
