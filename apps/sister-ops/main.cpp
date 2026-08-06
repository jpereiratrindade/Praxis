#include "sister/hoa/Commands.hpp"
#include "sister/hoa/GovernanceBaseline.hpp"

#include <exception>
#include <iostream>
#include <string_view>
#include <vector>

int main(int argc, char** argv) {
    try {
        std::vector<std::string_view> arguments;
        arguments.reserve(argc > 1 ? static_cast<std::size_t>(argc - 1) : 0U);
        for (int index = 1; index < argc; ++index) {
            arguments.emplace_back(argv[index]);
        }

        const auto repositoryRoot = sister::hoa::locateRepositoryRoot();
        return sister::hoa::runCommand(arguments, repositoryRoot);
    } catch (const std::exception& error) {
        std::cerr << "ERRO: " << error.what() << '\n';
        return 1;
    }
}
