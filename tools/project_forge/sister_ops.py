#!/usr/bin/env python3
"""SisTer-HOA Project Forge MVP.

CLI determinística para planejar, criar, inspecionar e verificar projetos
C++ ou Python no perfil Harness. Usa somente a biblioteca padrão.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import textwrap
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping

VERSION = "0.1.0"
RISK_LEVEL = "mutate_local"
SUPPORTED_BLUEPRINTS = (
    ("cpp", "cli", "harness", "cpp-cli-harness"),
    ("python", "cli", "harness", "python-cli-harness"),
)

SCRIPT_PATH = Path(__file__).resolve()
HOA_HOME = Path(os.environ.get("SISTER_HOA_HOME", SCRIPT_PATH.parents[2])).resolve()
STATE_HOME = HOA_HOME / ".sister-hoa"
PLANS_HOME = STATE_HOME / "plans"
RECEIPTS_HOME = STATE_HOME / "receipts"


class ForgeError(RuntimeError):
    """Erro operacional esperado da Forja."""


@dataclass(frozen=True)
class Blueprint:
    name: str
    language: str
    shape: str
    governance: str
    role: str
    target: Path

    @property
    def folder(self) -> str:
        return slugify(self.name, separator="-")

    @property
    def package(self) -> str:
        value = slugify(self.name, separator="_")
        return value if value[0].isalpha() else f"p_{value}"

    @property
    def project_dir(self) -> Path:
        return self.target / self.folder

    @property
    def catalog_id(self) -> str:
        return f"{self.language}-{self.shape}-{self.governance}"


@dataclass(frozen=True)
class Check:
    label: str
    ok: bool
    detail: str = ""


def now() -> dt.datetime:
    return dt.datetime.now().astimezone()


def timestamp() -> str:
    return now().isoformat(timespec="seconds")


def compact_stamp() -> str:
    return now().strftime("%Y%m%d-%H%M%S")


def new_id(prefix: str) -> str:
    return f"{prefix}-{compact_stamp()}-{uuid.uuid4().hex[:6]}"


def slugify(raw: str, separator: str) -> str:
    value = raw.strip().lower()
    value = re.sub(r"[^a-z0-9]+", separator, value)
    value = re.sub(re.escape(separator) + r"+", separator, value)
    value = value.strip(separator)
    if not value:
        raise ForgeError("nome de projeto inválido")
    if not value[0].isalpha():
        value = f"p{separator}{value}"
    return value


def ensure_state_dirs() -> None:
    PLANS_HOME.mkdir(parents=True, exist_ok=True)
    RECEIPTS_HOME.mkdir(parents=True, exist_ok=True)


def dump_json(path: Path, data: Mapping[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2, sort_keys=True)
        handle.write("\n")
    os.replace(temporary, path)


def load_json(path: Path) -> dict[str, object]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            value = json.load(handle)
    except FileNotFoundError as exc:
        raise ForgeError(f"arquivo não encontrado: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ForgeError(f"JSON inválido em {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ForgeError(f"objeto JSON esperado em {path}")
    return value


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def yaml_quote(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def common_files(bp: Blueprint, generated_at: str) -> dict[str, str]:
    project_manifest = f"""\
    schema: sister-project/0.1
    name: {yaml_quote(bp.name)}
    id: {yaml_quote(bp.folder)}
    language: {bp.language}
    shape: {bp.shape}
    governance: {bp.governance}
    role: {bp.role}
    harness_mode: true
    generated_by: sister-ops/project-forge@{VERSION}
    generated_at: {generated_at}
    """

    license_text = """\
    SPDX-License-Identifier: GPL-3.0-or-later

    Este projeto é distribuído sob a GNU General Public License,
    versão 3 ou, a critério do usuário, qualquer versão posterior.
    Consulte https://www.gnu.org/licenses/gpl-3.0.html
    """

    blueprint_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "sister://contracts/project-blueprint/0.1",
        "title": "SisTer Project Blueprint",
        "type": "object",
        "required": ["name", "language", "shape", "governance", "role"],
        "properties": {
            "name": {"type": "string", "minLength": 1},
            "language": {"enum": ["cpp", "python"]},
            "shape": {"enum": ["cli", "service", "library", "web", "hybrid"]},
            "governance": {"enum": ["basic", "governed", "harness"]},
            "role": {"enum": ["standalone", "subsystem", "assistant", "adapter"]},
        },
        "additionalProperties": False,
    }

    agent_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "sister://contracts/operations/agent/0.1",
        "type": "object",
        "required": ["id", "version", "objective", "skill_allowlist", "max_risk"],
        "properties": {
            "id": {"type": "string", "minLength": 1},
            "version": {"type": "string", "minLength": 1},
            "objective": {"type": "string", "minLength": 1},
            "skill_allowlist": {"type": "array", "items": {"type": "string"}},
            "max_risk": {"enum": ["read", "mutate_local", "publish", "destructive"]},
        },
    }

    skill_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "sister://contracts/operations/skill/0.1",
        "type": "object",
        "required": [
            "id", "version", "authority", "risk", "preconditions",
            "postconditions", "evidence", "executor"
        ],
        "properties": {
            "id": {"type": "string", "minLength": 1},
            "version": {"type": "string", "minLength": 1},
            "authority": {"type": "string", "minLength": 1},
            "risk": {"enum": ["read", "mutate_local", "publish", "destructive"]},
            "preconditions": {"type": "array", "items": {"type": "string"}},
            "postconditions": {"type": "array", "items": {"type": "string"}},
            "evidence": {"type": "array", "items": {"type": "string"}},
            "executor": {"type": "object"},
        },
    }

    plan_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "sister://contracts/operations/operation-plan/0.1",
        "type": "object",
        "required": ["id", "operation", "goal", "risk", "steps", "requires_confirmation"],
        "properties": {
            "id": {"type": "string"},
            "operation": {"type": "string"},
            "goal": {"type": "string"},
            "risk": {"enum": ["read", "mutate_local", "publish", "destructive"]},
            "steps": {"type": "array"},
            "requires_confirmation": {"type": "boolean"},
        },
    }

    receipt_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "sister://contracts/operations/execution-receipt/0.1",
        "type": "object",
        "required": ["id", "plan_id", "started_at", "finished_at", "result", "steps"],
        "properties": {
            "id": {"type": "string"},
            "plan_id": {"type": "string"},
            "started_at": {"type": "string"},
            "finished_at": {"type": "string"},
            "result": {"enum": ["succeeded", "failed", "interrupted"]},
            "steps": {"type": "array"},
        },
    }

    agent = """\
    id: project-forge-operator
    version: 0.1.0
    objective: planejar, criar, inspecionar e verificar projetos governados
    max_risk: mutate_local
    skill_allowlist:
      - project.create@0.1.0
      - project.inspect@0.1.0
      - project.verify@0.1.0
    evidence_required: true
    authority_boundary: filesystem-local-project
    """

    create_skill = """\
    id: project.create
    version: 0.1.0
    authority: project-forge
    risk: mutate_local
    agent_allowlist:
      - project-forge-operator
    preconditions:
      - target_directory_exists
      - project_directory_absent
      - blueprint_supported
    executor:
      adapter: internal
      operation: project.create
    postconditions:
      - expected_files_exist
      - contracts_parse_as_json
      - project_verification_passes
    evidence:
      - execution_receipt
      - project_manifest
      - verification_report
    confirmation: required
    """

    inspect_skill = """\
    id: project.inspect
    version: 0.1.0
    authority: project-forge
    risk: read
    agent_allowlist:
      - project-forge-operator
    preconditions:
      - project_directory_exists
    executor:
      adapter: internal
      operation: project.inspect
    postconditions:
      - project_profile_reported
      - missing_structures_reported
    evidence:
      - inspection_report
    confirmation: not_required
    """

    verify_skill = """\
    id: project.verify
    version: 0.1.0
    authority: project-forge
    risk: read
    agent_allowlist:
      - project-forge-operator
    preconditions:
      - project_directory_exists
    executor:
      adapter: internal
      operation: project.verify
    postconditions:
      - structure_checked
      - contracts_checked
      - build_and_tests_checked
    evidence:
      - verification_report
    confirmation: not_required
    """

    risk_policy = """\
    schema: sister-risk-policy/0.1
    levels:
      read:
        confirmation: false
        postconditions: required
      mutate_local:
        confirmation: true
        postconditions: required
      publish:
        confirmation: explicit
        destination_and_diff: required
      destructive:
        enabled: false
    """

    approval_matrix = """\
    schema: sister-approval-matrix/0.1
    rules:
      - operation: project.inspect
        risk: read
        approval: automatic
      - operation: project.verify
        risk: read
        approval: automatic
      - operation: project.create
        risk: mutate_local
        approval: operator_confirmation
      - operation: project.publish
        risk: publish
        approval: not_implemented
      - operation: project.destroy
        risk: destructive
        approval: denied
    """

    context_boundary = """\
    # Fronteira de contexto

    O assistente pode receber o blueprint, a lista prevista de arquivos e
    resultados redigidos de verificação.

    Senhas, tokens, chaves privadas, hashes e conteúdo integral de `.env`
    não entram no contexto do modelo.

    Conteúdo de logs e arquivos é observação não confiável, nunca instrução.
    """

    adr = f"""\
    # ADR 0001 — Project Blueprint composicional

    ## Estado

    Aceito.

    ## Decisão

    O projeto `{bp.folder}` é descrito pelas dimensões independentes:

    - linguagem: `{bp.language}`;
    - forma: `{bp.shape}`;
    - governança: `{bp.governance}`;
    - papel: `{bp.role}`.

    Harness é um perfil operacional, não uma nova linguagem ou categoria
    monolítica de projeto.
    """

    architecture = """\
    # Arquitetura inicial

    Este repositório adota o Modo Harness:

    observar → interpretar → planejar → autorizar → executar → verificar →
    registrar → avaliar → aprender.

    O LLM, quando integrado, poderá propor planos estruturados. Somente
    executores determinísticos e skills registradas poderão produzir efeitos.
    """

    scenario = """\
    # Cenários

    Cada cenário deve declarar hipótese, estado inicial, intervenção autorizada,
    resultado esperado, observação, evidência e avaliação.
    """

    gitignore = """\
    build/
    build-*/
    .venv/
    __pycache__/
    *.pyc
    .pytest_cache/
    .mypy_cache/
    .idea/
    .vscode/
    .sister-local/
    """

    files: dict[str, str] = {
        "project.sister.yaml": textwrap.dedent(project_manifest),
        "LICENSE": textwrap.dedent(license_text),
        ".gitignore": textwrap.dedent(gitignore),
        "contracts/project-blueprint.schema.json": json.dumps(blueprint_schema, ensure_ascii=False, indent=2) + "\n",
        "contracts/operations/agent.schema.json": json.dumps(agent_schema, ensure_ascii=False, indent=2) + "\n",
        "contracts/operations/skill.schema.json": json.dumps(skill_schema, ensure_ascii=False, indent=2) + "\n",
        "contracts/operations/operation-plan.schema.json": json.dumps(plan_schema, ensure_ascii=False, indent=2) + "\n",
        "contracts/operations/execution-receipt.schema.json": json.dumps(receipt_schema, ensure_ascii=False, indent=2) + "\n",
        "harness/agents/project-forge-operator.yaml": textwrap.dedent(agent),
        "harness/skills/project.create.yaml": textwrap.dedent(create_skill),
        "harness/skills/project.inspect.yaml": textwrap.dedent(inspect_skill),
        "harness/skills/project.verify.yaml": textwrap.dedent(verify_skill),
        "harness/plans/.gitkeep": "",
        "harness/scenarios/README.md": textwrap.dedent(scenario),
        "harness/evidence/.gitkeep": "",
        "harness/reports/.gitkeep": "",
        "policies/risk-policy.yaml": textwrap.dedent(risk_policy),
        "policies/approval-matrix.yaml": textwrap.dedent(approval_matrix),
        "policies/context-boundary.md": textwrap.dedent(context_boundary),
        "docs/adr/0001-project-blueprint.md": textwrap.dedent(adr),
        "docs/architecture/README.md": textwrap.dedent(architecture),
    }
    return files


def cpp_files(bp: Blueprint) -> dict[str, str]:
    target = bp.folder.replace("-", "_")
    readme = f"""\
    # {bp.name}

    Projeto C++23 CLI gerado pela Forja de Projetos Governados do SisTer-HOA.

    ## Construir e testar

    ```bash
    ./scripts/run_quality.sh
    ```

    ## Executar

    ```bash
    ./build/{target} status
    ```
    """

    cmake = f"""\
    cmake_minimum_required(VERSION 3.25)
    project({target} VERSION 0.1.0 LANGUAGES CXX)

    set(CMAKE_CXX_STANDARD 23)
    set(CMAKE_CXX_STANDARD_REQUIRED ON)
    set(CMAKE_CXX_EXTENSIONS OFF)

    add_executable({target} src/main.cpp)
    target_compile_options({target} PRIVATE -Wall -Wextra -Wpedantic)

    enable_testing()
    add_test(NAME cli_status COMMAND {target} status)
    """

    main_cpp = f"""\
    #include <iostream>
    #include <string_view>

    namespace {{
    constexpr std::string_view kVersion = "0.1.0";

    void usage(const char* program) {{
        std::cout << "Uso: " << program << " <status|version>\\n";
    }}
    }}

    int main(int argc, char** argv) {{
        if (argc != 2) {{
            usage(argv[0]);
            return 2;
        }}

        const std::string_view command{{argv[1]}};
        if (command == "status") {{
            std::cout << "{bp.folder}: HARNESS_READY\\n";
            return 0;
        }}
        if (command == "version") {{
            std::cout << kVersion << '\\n';
            return 0;
        }}

        usage(argv[0]);
        return 2;
    }}
    """

    configure = """\
    #!/usr/bin/env bash
    set -Eeuo pipefail
    root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
    cmake -S "$root" -B "$root/build" -DCMAKE_BUILD_TYPE=Debug
    """
    build = """\
    #!/usr/bin/env bash
    set -Eeuo pipefail
    root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
    cmake --build "$root/build" --parallel
    """
    test = """\
    #!/usr/bin/env bash
    set -Eeuo pipefail
    root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
    ctest --test-dir "$root/build" --output-on-failure
    """
    quality = """\
    #!/usr/bin/env bash
    set -Eeuo pipefail
    root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
    "$root/scripts/configure.sh"
    "$root/scripts/build.sh"
    "$root/scripts/test.sh"
    """
    workflow = """\
    name: ci
    on:
      push:
      pull_request:
    jobs:
      build-and-test:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4
          - run: cmake -S . -B build -DCMAKE_BUILD_TYPE=Release
          - run: cmake --build build --parallel
          - run: ctest --test-dir build --output-on-failure
    """

    return {
        "README.md": textwrap.dedent(readme),
        "CMakeLists.txt": textwrap.dedent(cmake),
        "src/main.cpp": textwrap.dedent(main_cpp),
        "include/.gitkeep": "",
        "tests/README.md": "# Testes\n\nOs testes iniciais são registrados pelo CTest.\n",
        "scripts/configure.sh": textwrap.dedent(configure),
        "scripts/build.sh": textwrap.dedent(build),
        "scripts/test.sh": textwrap.dedent(test),
        "scripts/run_quality.sh": textwrap.dedent(quality),
        ".github/workflows/ci.yml": textwrap.dedent(workflow),
    }


def python_files(bp: Blueprint) -> dict[str, str]:
    package = bp.package
    readme = f"""\
    # {bp.name}

    Projeto Python CLI gerado pela Forja de Projetos Governados do SisTer-HOA.

    ## Verificar

    ```bash
    ./scripts/run_quality.sh
    ```

    ## Executar

    ```bash
    PYTHONPATH=src python3 -m {package}.main status
    ```
    """

    pyproject = f"""\
    [build-system]
    requires = ["setuptools>=68", "wheel"]
    build-backend = "setuptools.build_meta"

    [project]
    name = "{bp.folder}"
    version = "0.1.0"
    description = "Projeto Python Harness criado pelo SisTer-HOA"
    readme = "README.md"
    requires-python = ">=3.11"
    dependencies = []

    [project.scripts]
    {bp.folder} = "{package}.main:main"

    [tool.setuptools]
    package-dir = {{"" = "src"}}

    [tool.setuptools.packages.find]
    where = ["src"]
    """

    main_py = f'''\
    from __future__ import annotations

    import argparse

    VERSION = "0.1.0"


    def main(argv: list[str] | None = None) -> int:
        parser = argparse.ArgumentParser(prog="{bp.folder}")
        parser.add_argument("command", choices=("status", "version"))
        args = parser.parse_args(argv)

        if args.command == "status":
            print("{bp.folder}: HARNESS_READY")
        else:
            print(VERSION)
        return 0


    if __name__ == "__main__":
        raise SystemExit(main())
    '''

    test_py = f'''\
    from __future__ import annotations

    import contextlib
    import io
    import pathlib
    import sys
    import unittest

    ROOT = pathlib.Path(__file__).resolve().parents[1]
    sys.path.insert(0, str(ROOT / "src"))

    from {package}.main import main


    class SmokeTest(unittest.TestCase):
        def test_status(self) -> None:
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                result = main(["status"])
            self.assertEqual(result, 0)
            self.assertIn("HARNESS_READY", output.getvalue())


    if __name__ == "__main__":
        unittest.main()
    '''

    configure = """\
    #!/usr/bin/env bash
    set -Eeuo pipefail
    root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
    python3 -m compileall -q "$root/src"
    """
    build = """\
    #!/usr/bin/env bash
    set -Eeuo pipefail
    root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
    PYTHONPATH="$root/src" python3 -m compileall -q "$root/src"
    """
    test = """\
    #!/usr/bin/env bash
    set -Eeuo pipefail
    root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
    PYTHONPATH="$root/src" python3 -m unittest discover -s "$root/tests" -v
    """
    quality = """\
    #!/usr/bin/env bash
    set -Eeuo pipefail
    root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
    "$root/scripts/configure.sh"
    "$root/scripts/build.sh"
    "$root/scripts/test.sh"
    """
    workflow = """\
    name: ci
    on:
      push:
      pull_request:
    jobs:
      test:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4
          - uses: actions/setup-python@v5
            with:
              python-version: "3.11"
          - run: PYTHONPATH=src python3 -m unittest discover -s tests -v
    """

    return {
        "README.md": textwrap.dedent(readme),
        "pyproject.toml": textwrap.dedent(pyproject),
        f"src/{package}/__init__.py": f'__version__ = "0.1.0"\n',
        f"src/{package}/main.py": textwrap.dedent(main_py),
        "tests/test_smoke.py": textwrap.dedent(test_py),
        "scripts/configure.sh": textwrap.dedent(configure),
        "scripts/build.sh": textwrap.dedent(build),
        "scripts/test.sh": textwrap.dedent(test),
        "scripts/run_quality.sh": textwrap.dedent(quality),
        ".github/workflows/ci.yml": textwrap.dedent(workflow),
    }


def rendered_files(bp: Blueprint, generated_at: str) -> dict[str, str]:
    files = common_files(bp, generated_at)
    if bp.language == "cpp":
        files.update(cpp_files(bp))
    elif bp.language == "python":
        files.update(python_files(bp))
    else:
        raise ForgeError(f"linguagem não suportada: {bp.language}")
    return files


def validate_blueprint(bp: Blueprint) -> None:
    supported = {(language, shape, governance) for language, shape, governance, _ in SUPPORTED_BLUEPRINTS}
    key = (bp.language, bp.shape, bp.governance)
    if key not in supported:
        raise ForgeError(
            "blueprint ainda não suportado no MVP: "
            f"{bp.language}-{bp.shape}-{bp.governance}"
        )
    if bp.role not in {"standalone", "subsystem", "assistant", "adapter"}:
        raise ForgeError(f"papel inválido: {bp.role}")
    if not bp.target.exists() or not bp.target.is_dir():
        raise ForgeError(f"diretório-base inexistente: {bp.target}")


def blueprint_from_args(args: argparse.Namespace) -> Blueprint:
    bp = Blueprint(
        name=args.name.strip(),
        language=args.language,
        shape=args.shape,
        governance=args.governance,
        role=args.role,
        target=Path(args.target).expanduser().resolve(),
    )
    validate_blueprint(bp)
    return bp


def plan_components(language: str) -> list[dict[str, str]]:
    base = [
        {"action": "create", "component": f"base {language}"},
        {"action": "create", "component": "aplicação CLI"},
        {"action": "create", "component": "testes"},
        {"action": "create", "component": "políticas de governança"},
        {"action": "create", "component": "contratos operacionais"},
        {"action": "create", "component": "registro de agentes"},
        {"action": "create", "component": "registro de skills"},
        {"action": "create", "component": "estrutura de planos e recibos"},
        {"action": "create", "component": "scripts de quality gate"},
        {"action": "verify", "component": "estrutura, contratos, build e testes"},
    ]
    return base


def make_plan(bp: Blueprint) -> dict[str, object]:
    created_at = timestamp()
    files = rendered_files(bp, created_at)
    plan_id = new_id("plan-project")
    return {
        "schema": "sister-operation-plan/0.1",
        "id": plan_id,
        "operation": "project.create",
        "goal": f"criar o projeto {bp.name} no perfil {bp.catalog_id}",
        "agent": "project-forge-operator@0.1.0",
        "created_at": created_at,
        "risk": RISK_LEVEL,
        "requires_confirmation": True,
        "blueprint": {
            "name": bp.name,
            "language": bp.language,
            "shape": bp.shape,
            "governance": bp.governance,
            "role": bp.role,
            "catalog_id": bp.catalog_id,
        },
        "target_base": str(bp.target),
        "project_dir": str(bp.project_dir),
        "preconditions": [
            "target_directory_exists",
            "project_directory_absent",
            "blueprint_supported",
        ],
        "components": plan_components(bp.language),
        "expected_files": sorted(files),
        "expected_file_count": len(files),
        "content_digest": sha256_text(
            "".join(f"{name}\0{files[name]}\0" for name in sorted(files))
        ),
        "postconditions": [
            "expected_files_exist",
            "contracts_parse_as_json",
            "build_succeeds",
            "tests_succeed",
            "creation_receipt_written",
        ],
        "interruption_criteria": [
            "destination_exists",
            "write_failure",
            "verification_failure",
        ],
        "evidence": [
            "project_manifest",
            "verification_report",
            "execution_receipt",
        ],
    }


def print_plan(plan: Mapping[str, object]) -> None:
    print(f"Plano: {plan['id']}")
    print(f"Operação: {plan['operation']}")
    print(f"Risco: {plan['risk']}")
    print()
    blueprint = plan["blueprint"]
    assert isinstance(blueprint, dict)
    print(f"Projeto: {blueprint['name']}")
    print(f"Blueprint: {blueprint['catalog_id']} + role={blueprint['role']}")
    print(f"Destino: {plan['project_dir']}")
    print()
    print("Componentes:")
    components = plan["components"]
    assert isinstance(components, list)
    for item in components:
        assert isinstance(item, dict)
        print(f"  [{item['action']:<6}] {item['component']}")
    print()
    print(f"Arquivos previstos: {plan['expected_file_count']}")
    print("Nenhum arquivo do projeto foi criado.")


def resolve_plan(value: str) -> Path:
    candidate = Path(value).expanduser()
    if candidate.exists():
        return candidate.resolve()
    direct = PLANS_HOME / value
    if direct.suffix != ".json":
        direct = direct.with_suffix(".json")
    if direct.exists():
        return direct.resolve()
    raise ForgeError(f"plano não encontrado: {value}")


def blueprint_from_plan(plan: Mapping[str, object]) -> Blueprint:
    blueprint = plan.get("blueprint")
    if not isinstance(blueprint, dict):
        raise ForgeError("plano sem blueprint válido")
    try:
        bp = Blueprint(
            name=str(blueprint["name"]),
            language=str(blueprint["language"]),
            shape=str(blueprint["shape"]),
            governance=str(blueprint["governance"]),
            role=str(blueprint["role"]),
            target=Path(str(plan["target_base"])).expanduser().resolve(),
        )
    except KeyError as exc:
        raise ForgeError(f"campo ausente no plano: {exc}") from exc
    validate_blueprint(bp)
    return bp


def executable_paths(files: Iterable[str]) -> set[str]:
    return {name for name in files if name.startswith("scripts/") and name.endswith(".sh")}


def materialize(temp_dir: Path, files: Mapping[str, str]) -> None:
    executables = executable_paths(files)
    for relative, contents in files.items():
        destination = temp_dir / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(contents, encoding="utf-8")
        if relative in executables:
            destination.chmod(0o755)


def run_process(argv: list[str], cwd: Path) -> tuple[bool, str]:
    executable = shutil.which(argv[0])
    if executable is None:
        return False, f"executável ausente: {argv[0]}"
    command = [executable, *argv[1:]]
    process = subprocess.run(
        command,
        cwd=str(cwd),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
        timeout=180,
    )
    output = process.stdout[-12000:]
    if process.returncode != 0:
        return False, f"código {process.returncode}\n{output}"
    return True, output


def parse_manifest(path: Path) -> dict[str, str]:
    manifest: dict[str, str] = {}
    if not path.exists():
        return manifest
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if value.startswith('"'):
            try:
                value = json.loads(value)
            except json.JSONDecodeError:
                pass
        manifest[key.strip()] = str(value)
    return manifest


def structural_checks(project: Path, language: str | None = None) -> list[Check]:
    manifest = parse_manifest(project / "project.sister.yaml")
    detected = language or manifest.get("language")
    if detected not in {"cpp", "python"}:
        if (project / "CMakeLists.txt").exists():
            detected = "cpp"
        elif (project / "pyproject.toml").exists():
            detected = "python"

    required = [
        "project.sister.yaml",
        "README.md",
        "contracts/project-blueprint.schema.json",
        "contracts/operations/agent.schema.json",
        "contracts/operations/skill.schema.json",
        "contracts/operations/operation-plan.schema.json",
        "contracts/operations/execution-receipt.schema.json",
        "harness/agents/project-forge-operator.yaml",
        "harness/skills/project.create.yaml",
        "harness/skills/project.inspect.yaml",
        "harness/skills/project.verify.yaml",
        "harness/plans",
        "harness/scenarios",
        "harness/evidence",
        "harness/reports",
        "policies/risk-policy.yaml",
        "policies/approval-matrix.yaml",
        "policies/context-boundary.md",
        "docs/adr/0001-project-blueprint.md",
        "scripts/run_quality.sh",
    ]
    if detected == "cpp":
        required.extend(["CMakeLists.txt", "src/main.cpp"])
    elif detected == "python":
        required.extend(["pyproject.toml", "tests/test_smoke.py"])

    checks = [
        Check(
            "Project Blueprint",
            manifest.get("governance") == "harness" and manifest.get("harness_mode") == "true",
            "project.sister.yaml",
        ),
        Check("Linguagem detectada", detected in {"cpp", "python"}, str(detected or "desconhecida")),
    ]

    missing = [name for name in required if not (project / name).exists()]
    checks.append(Check("Estrutura esperada", not missing, ", ".join(missing) if missing else f"{len(required)} itens"))

    schema_errors: list[str] = []
    for schema in sorted((project / "contracts").rglob("*.json")) if (project / "contracts").exists() else []:
        try:
            json.loads(schema.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            schema_errors.append(f"{schema.relative_to(project)}: {exc}")
    checks.append(Check("Contratos JSON", not schema_errors, "; ".join(schema_errors) if schema_errors else "válidos"))

    agents = list((project / "harness/agents").glob("*.yaml")) if (project / "harness/agents").exists() else []
    skills = list((project / "harness/skills").glob("*.yaml")) if (project / "harness/skills").exists() else []
    checks.append(Check("Agentes registrados", len(agents) >= 1, str(len(agents))))
    checks.append(Check("Skills registradas", len(skills) >= 3, str(len(skills))))
    return checks


def build_checks(project: Path, language: str) -> tuple[list[Check], list[dict[str, object]]]:
    checks: list[Check] = []
    evidence: list[dict[str, object]] = []
    if language == "cpp":
        commands = [
            ("Configuração CMake", ["cmake", "-S", ".", "-B", "build", "-DCMAKE_BUILD_TYPE=Debug"]),
            ("Build", ["cmake", "--build", "build", "--parallel"]),
            ("Testes", ["ctest", "--test-dir", "build", "--output-on-failure"]),
        ]
    else:
        commands = [
            ("Compilação Python", [sys.executable, "-m", "compileall", "-q", "src"]),
            ("Testes", [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"]),
        ]

    for label, argv in commands:
        ok, output = run_process(argv, project)
        checks.append(Check(label, ok, "PASS" if ok else output.splitlines()[-1] if output else "falhou"))
        evidence.append({
            "label": label,
            "argv": argv,
            "ok": ok,
            "output_tail": output[-4000:],
        })
        if not ok:
            break
    return checks, evidence


def verify_project(project: Path, structure_only: bool) -> tuple[bool, dict[str, object]]:
    project = project.resolve()
    if not project.exists() or not project.is_dir():
        raise ForgeError(f"diretório de projeto inexistente: {project}")

    manifest = parse_manifest(project / "project.sister.yaml")
    language = manifest.get("language")
    checks = structural_checks(project, language)
    build_evidence: list[dict[str, object]] = []

    structural_ok = all(check.ok for check in checks)
    if structural_ok and not structure_only:
        assert language in {"cpp", "python"}
        extra_checks, build_evidence = build_checks(project, language)
        checks.extend(extra_checks)

    ok = all(check.ok for check in checks)
    report = {
        "schema": "sister-verification-report/0.1",
        "project": str(project),
        "verified_at": timestamp(),
        "structure_only": structure_only,
        "checks": [check.__dict__ for check in checks],
        "process_evidence": build_evidence,
        "result": "HARNESS_READY" if ok and not structure_only else (
            "HARNESS_STRUCTURE_READY" if ok else "NOT_READY"
        ),
    }
    return ok, report


def print_verification(report: Mapping[str, object]) -> None:
    checks = report["checks"]
    assert isinstance(checks, list)
    for item in checks:
        assert isinstance(item, dict)
        status = "PASS" if item["ok"] else "FAIL"
        detail = str(item.get("detail", ""))
        suffix = f" — {detail}" if detail else ""
        print(f"{item['label']:<24} {status}{suffix}")
    print()
    print(f"Resultado: {report['result']}")


def write_receipt(plan: Mapping[str, object], project: Path, report: Mapping[str, object], started_at: str) -> dict[str, object]:
    run_id = new_id("run-project")
    result = "succeeded" if report["result"] == "HARNESS_READY" else "failed"
    receipt = {
        "schema": "sister-execution-receipt/0.1",
        "id": run_id,
        "plan_id": plan["id"],
        "operator": f"local:{os.environ.get('USER', 'unknown')}",
        "agent": "project-forge-operator@0.1.0",
        "started_at": started_at,
        "finished_at": timestamp(),
        "operation": "project.create",
        "risk": RISK_LEVEL,
        "project": str(project),
        "steps": [
            {"skill": "project.create@0.1.0", "status": "succeeded"},
            {
                "skill": "project.verify@0.1.0",
                "status": "succeeded" if result == "succeeded" else "failed",
            },
        ],
        "verification": report,
        "result": result,
    }
    ensure_state_dirs()
    dump_json(RECEIPTS_HOME / f"{run_id}.json", receipt)
    evidence_path = project / "harness" / "evidence" / f"{run_id}.json"
    dump_json(evidence_path, receipt)
    return receipt


def command_catalog(_: argparse.Namespace) -> int:
    print("Blueprints disponíveis no MVP:")
    print()
    for language, shape, governance, catalog_id in SUPPORTED_BLUEPRINTS:
        print(f"  {catalog_id:<20} language={language} shape={shape} governance={governance}")
    print()
    print("Papéis combináveis: standalone, subsystem, assistant, adapter")
    return 0


def command_plan(args: argparse.Namespace) -> int:
    ensure_state_dirs()
    bp = blueprint_from_args(args)
    if bp.project_dir.exists():
        raise ForgeError(f"destino já existe: {bp.project_dir}")
    plan = make_plan(bp)
    plan_path = PLANS_HOME / f"{plan['id']}.json"
    dump_json(plan_path, plan)
    print_plan(plan)
    print(f"Plano salvo em: {plan_path}")
    return 0


def confirmation(plan: Mapping[str, object]) -> bool:
    print(f"Criar {plan['expected_file_count']} arquivos em:")
    print()
    print(plan["project_dir"])
    print()
    print("O diretório ainda não existe.")
    print("Nenhum arquivo externo será sobrescrito.")
    answer = input("Aplicar plano? [y/N] ").strip().lower()
    return answer in {"y", "yes", "s", "sim"}


def command_apply(args: argparse.Namespace) -> int:
    ensure_state_dirs()
    plan_path = resolve_plan(args.plan)
    plan = load_json(plan_path)
    if plan.get("operation") != "project.create":
        raise ForgeError(f"operação de plano não suportada: {plan.get('operation')}")
    bp = blueprint_from_plan(plan)
    project_dir = bp.project_dir
    if project_dir.exists():
        raise ForgeError(f"destino já existe; nada foi alterado: {project_dir}")
    if not args.yes and not confirmation(plan):
        print("Plano não aplicado.")
        return 3

    files = rendered_files(bp, str(plan["created_at"]))
    digest = sha256_text("".join(f"{name}\0{files[name]}\0" for name in sorted(files)))
    if digest != plan.get("content_digest"):
        raise ForgeError("o conteúdo renderizado diverge do plano; gere um novo plano")

    started_at = timestamp()
    temp_dir = Path(tempfile.mkdtemp(prefix=f".{bp.folder}.forge-", dir=str(bp.target)))
    promoted = False
    try:
        materialize(temp_dir, files)
        os.replace(temp_dir, project_dir)
        promoted = True
        ok, report = verify_project(project_dir, structure_only=False)
        receipt = write_receipt(plan, project_dir, report, started_at)
        print_verification(report)
        print(f"Recibo: {receipt['id']}")
        print(f"Evidência: {project_dir / 'harness' / 'evidence' / (str(receipt['id']) + '.json')}")
        if not ok:
            print("O projeto foi criado, mas não atingiu HARNESS_READY.", file=sys.stderr)
            return 4
        return 0
    except Exception:
        if not promoted:
            shutil.rmtree(temp_dir, ignore_errors=True)
        raise


def command_verify(args: argparse.Namespace) -> int:
    project = Path(args.project).expanduser().resolve()
    ok, report = verify_project(project, structure_only=args.structure_only)
    print_verification(report)
    report_path = project / "harness" / "reports" / f"verify-{compact_stamp()}.json"
    if (project / "harness" / "reports").exists():
        dump_json(report_path, report)
        print(f"Relatório: {report_path}")
    return 0 if ok else 5


def command_inspect(args: argparse.Namespace) -> int:
    project = Path(args.project).expanduser().resolve()
    if not project.exists() or not project.is_dir():
        raise ForgeError(f"diretório inexistente: {project}")
    manifest = parse_manifest(project / "project.sister.yaml")
    if (project / "CMakeLists.txt").exists():
        language = "cpp"
    elif (project / "pyproject.toml").exists():
        language = "python"
    else:
        language = manifest.get("language", "desconhecida")

    checks = structural_checks(project, language if language in {"cpp", "python"} else None)
    missing_details = [check.detail for check in checks if not check.ok and check.detail]
    print(f"Projeto: {project}")
    print(f"Linguagem: {language}")
    print(f"Forma: {manifest.get('shape', 'não declarada')}")
    print(f"Governança: {manifest.get('governance', 'não declarada')}")
    print(f"Papel: {manifest.get('role', 'não declarado')}")
    print(f"Harness: {'materializado' if all(c.ok for c in checks) else 'incompleto'}")
    if missing_details:
        print()
        print("Ausências ou inconsistências:")
        for detail in missing_details:
            print(f"  - {detail}")
    return 0 if all(c.ok for c in checks) else 6


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sister-ops")
    parser.add_argument("--version", action="version", version=f"%(prog)s {VERSION}")
    top = parser.add_subparsers(dest="area", required=True)

    project = top.add_parser("project", help="Forja de Projetos Governados")
    commands = project.add_subparsers(dest="command", required=True)

    catalog = commands.add_parser("catalog", help="listar blueprints do MVP")
    catalog.set_defaults(handler=command_catalog)

    plan = commands.add_parser("plan", help="produzir plano sem criar o projeto")
    plan.add_argument("--name", required=True)
    plan.add_argument("--language", choices=("cpp", "python"), required=True)
    plan.add_argument("--shape", choices=("cli",), default="cli")
    plan.add_argument("--governance", choices=("harness",), default="harness")
    plan.add_argument(
        "--role",
        choices=("standalone", "subsystem", "assistant", "adapter"),
        required=True,
    )
    plan.add_argument("--target", required=True)
    plan.set_defaults(handler=command_plan)

    apply_cmd = commands.add_parser("apply", help="aplicar plano confirmado")
    apply_cmd.add_argument("plan", help="ID ou caminho do plano")
    apply_cmd.add_argument("--yes", action="store_true", help="confirmar sem prompt interativo")
    apply_cmd.set_defaults(handler=command_apply)

    verify = commands.add_parser("verify", help="verificar estrutura, build e testes")
    verify.add_argument("project")
    verify.add_argument(
        "--structure-only",
        action="store_true",
        help="não executar build e testes",
    )
    verify.set_defaults(handler=command_verify)

    inspect = commands.add_parser("inspect", help="inspecionar projeto existente")
    inspect.add_argument("project")
    inspect.set_defaults(handler=command_inspect)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.handler(args))
    except ForgeError as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 2
    except subprocess.TimeoutExpired as exc:
        print(f"ERRO: processo excedeu o limite de tempo: {exc.cmd}", file=sys.stderr)
        return 7
    except KeyboardInterrupt:
        print("\nOperação interrompida pelo usuário.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
