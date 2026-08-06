#pragma once

#include <span>
#include <string>
#include <string_view>

namespace sister::hoa {

struct CommandDescriptor {
    std::string_view name;
    std::string_view summary;
    std::string_view usage;
    std::string_view risk;
    std::string_view details;
    bool mutatesState{false};
};

[[nodiscard]] std::span<const CommandDescriptor> commandCatalog();
[[nodiscard]] const CommandDescriptor* findCommand(std::string_view name);
[[nodiscard]] std::string renderGeneralHelp();
[[nodiscard]] std::string renderCommandHelp(std::string_view name);

} // namespace sister::hoa
