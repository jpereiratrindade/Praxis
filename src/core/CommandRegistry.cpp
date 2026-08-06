#include "sister/hoa/CommandRegistry.hpp"

#include "sister/hoa/Version.hpp"

#include <array>
#include <sstream>

namespace sister::hoa {
namespace {

constexpr std::array<CommandDescriptor, 7> kCommands{{
    {
        .name = "status",
        .summary = "Exibe identidade, versão e fase atual do Harness.",
        .usage = "sister-ops status",
        .risk = "read",
        .details = "Apresenta a identidade operacional do SisTer-HOA sem executar diagnósticos ou alterar estado.",
    },
    {
        .name = "health",
        .summary = "Resume a saúde do núcleo e da governança.",
        .usage = "sister-ops health",
        .risk = "read",
        .details = "Inspeciona a baseline de governança e apresenta um resumo compacto de disponibilidade.",
    },
    {
        .name = "doctor",
        .summary = "Executa diagnóstico detalhado e somente leitura.",
        .usage = "sister-ops doctor",
        .risk = "read",
        .details = "Verifica manifesto, políticas, contratos, agentes, skills, documentação e validadores.",
    },
    {
        .name = "governance check",
        .summary = "Valida a baseline de governança do repositório.",
        .usage = "sister-ops governance check",
        .risk = "read",
        .details = "Executa a mesma inspeção estrutural usada pelos quality gates do estágio H0.",
    },
    {
        .name = "dashboard snapshot",
        .summary = "Emite em JSON o estado observável atual.",
        .usage = "sister-ops dashboard snapshot",
        .risk = "read",
        .details = "Produz um snapshot em stdout. Não cria arquivos, não executa comandos e não expõe segredos.",
    },
    {
        .name = "dashboard serve",
        .summary = "Serve o painel web local em modo somente leitura.",
        .usage = "sister-ops dashboard serve [--port 8090]",
        .risk = "read",
        .details = "Escuta apenas em 127.0.0.1 e aceita somente GET e HEAD. POST, PUT, PATCH e DELETE retornam 405.",
    },
    {
        .name = "help",
        .summary = "Mostra ajuda geral ou contextual.",
        .usage = "sister-ops help [comando]",
        .risk = "read",
        .details = "Também disponível por -h e --help.",
    },
}};

bool startsWithCommandGroup(const std::string_view command, const std::string_view group) {
    return command.size() > group.size() && command.starts_with(group) && command[group.size()] == ' ';
}

void appendDescriptor(std::ostringstream& output, const CommandDescriptor& command) {
    output << "\n" << command.name << "\n"
           << "  " << command.summary << "\n\n"
           << "Uso:\n  " << command.usage << "\n\n"
           << "Risco: " << command.risk << "\n"
           << "Muta estado: " << (command.mutatesState ? "sim" : "não") << "\n\n"
           << command.details << "\n";
}

} // namespace

std::span<const CommandDescriptor> commandCatalog() {
    return kCommands;
}

const CommandDescriptor* findCommand(const std::string_view name) {
    for (const auto& command : kCommands) {
        if (command.name == name) {
            return &command;
        }
    }
    return nullptr;
}

std::string renderGeneralHelp() {
    std::ostringstream output;
    output << "SisTer-HOA — Harness Operacional Assistido\n\n"
           << "Uso:\n"
           << "  sister-ops <comando> [opções]\n\n"
           << "Comandos:\n";

    for (const auto& command : kCommands) {
        output << "  " << command.name;
        if (command.name.size() < 20U) {
            output << std::string(20U - command.name.size(), ' ');
        } else {
            output << ' ';
        }
        output << command.summary << '\n';
    }

    output << "\nOpções globais:\n"
           << "  -h, --help          Mostra esta ajuda\n"
           << "  --version           Mostra a versão\n\n"
           << "Modo atual:\n"
           << "  versão              " << kVersion << "\n"
           << "  Harness             " << kHarnessPhase << "\n"
           << "  implementação       C++23 nativo\n"
           << "  LLM                  desabilitado\n"
           << "  operações mutáveis  desabilitadas\n"
           << "  painel web           somente leitura em 127.0.0.1\n\n"
           << "Ajuda contextual:\n"
           << "  sister-ops help doctor\n"
           << "  sister-ops help dashboard\n";
    return output.str();
}

std::string renderCommandHelp(const std::string_view name) {
    if (const auto* command = findCommand(name)) {
        std::ostringstream output;
        output << "SisTer-HOA — ajuda contextual";
        appendDescriptor(output, *command);
        return output.str();
    }

    std::ostringstream output;
    bool found = false;
    for (const auto& command : kCommands) {
        if (startsWithCommandGroup(command.name, name)) {
            if (!found) {
                output << "SisTer-HOA — grupo " << name << "\n";
            }
            appendDescriptor(output, command);
            found = true;
        }
    }

    if (!found) {
        return {};
    }
    return output.str();
}

} // namespace sister::hoa
