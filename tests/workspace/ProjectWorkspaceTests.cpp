#include "sister/hoa/ProjectWorkspace.hpp"
#include <filesystem>
#include <fstream>
#include <iostream>
#include <stdexcept>

int main() {
    const auto root = std::filesystem::temp_directory_path() / "hoa-workspace-test";
    std::filesystem::remove_all(root);
    std::filesystem::create_directories(root / ".hoa");
    std::ofstream(root / "CMakeLists.txt") << "cmake_minimum_required(VERSION 3.25)\n";
    std::ofstream(root / ".hoa/project.yaml") << "schema: hoa-project/0.1\n";
    sister::hoa::ProjectWorkspace workspace(root, sister::hoa::WorkspaceSelectionSource::command_line);
    if (!workspace.hasHoaManifest() || !workspace.hasCMakeProject()) throw std::runtime_error("discovery failed");
    if (!workspace.contains(root / "CMakeLists.txt")) throw std::runtime_error("containment failed");
    bool blocked = false;
    try { (void)workspace.resolve("../escape"); } catch (...) { blocked = true; }
    if (!blocked) throw std::runtime_error("workspace escape was not blocked");
    std::filesystem::remove_all(root);
    std::cout << "ProjectWorkspace tests: PASS\n";
}
