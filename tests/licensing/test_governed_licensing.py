#!/usr/bin/env python3
"""Executable normal and adversarial proof for PRAXIS-LIC-001."""

from __future__ import annotations

import hashlib
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BOOTSTRAP = ROOT / "scripts/bootstrap_project_licensing.py"
VALIDATOR = ROOT / "scripts/validate_governed_licensing.py"
CAPABILITY = "praxis-initial-constitution/0.1\n"
PRAXIS_LICENSE_SHA256 = (
    "3972dc9744f6499f0f9b2dbf76696f2ae7ad8af9b23dde66d6af86c9dfb36986"
)


class GovernedLicensingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.workspace = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def run_script(self, script: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", str(script), str(self.workspace), *args],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def start_constitution(self, license_id: str | None = None) -> None:
        hoa = self.workspace / ".hoa"
        hoa.mkdir()
        (hoa / "initial-constitution").write_text(CAPABILITY, encoding="utf-8")
        if license_id is not None:
            (self.workspace / "LICENSE").write_text(
                f"SPDX-License-Identifier: {license_id}\n\nFixture terms.\n",
                encoding="utf-8",
            )

    def state(self) -> str:
        return (self.workspace / ".hoa/licensing.yaml").read_text(encoding="utf-8")

    def test_template_capability_contract(self) -> None:
        template = ROOT / "templates/governed-project/.hoa/initial-constitution"
        self.assertEqual(template.read_text(encoding="utf-8"), CAPABILITY)

    def test_lic_t01_explicit_valid_license(self) -> None:
        self.start_constitution("MIT")
        result = self.run_script(BOOTSTRAP, "--license", "MIT")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("resolved: MIT", self.state())
        self.assertIn("provenance: explicit", self.state())
        self.assertEqual(self.run_script(VALIDATOR).returncode, 0)

    def test_lic_t02_new_project_default(self) -> None:
        self.start_constitution()
        result = self.run_script(BOOTSTRAP)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("resolved: GPL-3.0-or-later", self.state())
        self.assertIn("provenance: default", self.state())
        self.assertIn(
            "SPDX-License-Identifier: GPL-3.0-or-later",
            (self.workspace / "LICENSE").read_text(encoding="utf-8"),
        )

    def test_lic_t03_explicit_differs_from_default_without_exception(self) -> None:
        self.start_constitution("Apache-2.0")
        result = self.run_script(BOOTSTRAP, "--license", "Apache-2.0")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("resolved: Apache-2.0", self.state())
        self.assertIn("provenance: explicit", self.state())
        self.assertNotIn("exception_rationale", self.state())

    def test_lic_t04_resolved_metadata_without_license_fails(self) -> None:
        self.start_constitution("MIT")
        self.assertEqual(self.run_script(BOOTSTRAP, "--license", "MIT").returncode, 0)
        (self.workspace / "LICENSE").unlink()
        result = self.run_script(VALIDATOR)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("LICENSE artifact is missing", result.stdout)

    def test_lic_t05_exception_without_rationale_fails_without_mutation(self) -> None:
        self.start_constitution("MIT")
        result = self.run_script(BOOTSTRAP, "--policy-exception", "MIT")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("requires --rationale", result.stderr)
        self.assertFalse((self.workspace / ".hoa/licensing.yaml").exists())
        self.assertTrue((self.workspace / ".hoa/initial-constitution").exists())

    def test_exception_with_rationale_is_distinct_and_valid(self) -> None:
        self.start_constitution("MIT")
        result = self.run_script(
            BOOTSTRAP,
            "--policy-exception",
            "MIT",
            "--rationale",
            "Institutional decision GOV-42",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("provenance: exception", self.state())
        self.assertIn("Institutional decision GOV-42", self.state())
        self.assertEqual(self.run_script(VALIDATOR).returncode, 0)

    def test_lic_t06_repeated_bootstrap_preserves_decision_and_bytes(self) -> None:
        self.start_constitution("MIT")
        self.assertEqual(self.run_script(BOOTSTRAP, "--license", "MIT").returncode, 0)
        before = {
            path: path.read_bytes()
            for path in (
                self.workspace / "LICENSE",
                self.workspace / ".hoa/licensing.yaml",
            )
        }
        result = self.run_script(BOOTSTRAP)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("existing decision preserved", result.stdout)
        self.assertEqual(before, {path: path.read_bytes() for path in before})

    def test_repeated_bootstrap_rejects_conflicting_explicit_request(self) -> None:
        self.start_constitution("MIT")
        self.assertEqual(self.run_script(BOOTSTRAP, "--license", "MIT").returncode, 0)
        result = self.run_script(BOOTSTRAP, "--license", "Apache-2.0")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("contradicts the existing decision", result.stderr)
        self.assertIn("resolved: MIT", self.state())

    def test_repeated_bootstrap_rejects_conflicting_provenance(self) -> None:
        self.start_constitution("MIT")
        self.assertEqual(self.run_script(BOOTSTRAP, "--license", "MIT").returncode, 0)
        result = self.run_script(
            BOOTSTRAP,
            "--policy-exception",
            "MIT",
            "--rationale",
            "Later claim",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("contradicts the existing decision", result.stderr)
        self.assertIn("provenance: explicit", self.state())

    def test_lic_t07_and_t11_legacy_absence_is_valid_but_not_newness(self) -> None:
        result = self.run_script(VALIDATOR)
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertIn("legacy/not constituted; no mutation", result.stdout)
        bootstrap = self.run_script(BOOTSTRAP)
        self.assertNotEqual(bootstrap.returncode, 0)
        self.assertIn("not inside", bootstrap.stderr)
        self.assertEqual(list(self.workspace.iterdir()), [])

    def test_lic_t08_praxis_self_license_is_preserved(self) -> None:
        observed = hashlib.sha256((ROOT / "LICENSE").read_bytes()).hexdigest()
        self.assertEqual(observed, PRAXIS_LICENSE_SHA256)
        self.assertIn(
            "SPDX-License-Identifier: GPL-3.0-only",
            (ROOT / "README.md").read_text(encoding="utf-8"),
        )
        self.assertFalse((ROOT / ".hoa/licensing.yaml").exists())
        result = subprocess.run(
            ["python3", str(VALIDATOR), str(ROOT)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("legacy/not constituted; no mutation", result.stdout)

    def test_lic_t09_artifact_mutation_is_detected(self) -> None:
        self.start_constitution("MIT")
        self.assertEqual(self.run_script(BOOTSTRAP, "--license", "MIT").returncode, 0)
        with (self.workspace / "LICENSE").open("a", encoding="utf-8") as stream:
            stream.write("unauthorized change\n")
        result = self.run_script(VALIDATOR)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("SHA-256 mismatch", result.stdout)

    def test_lic_t09_metadata_mutation_is_detected_when_artifact_identifies_license(self) -> None:
        self.start_constitution("MIT")
        self.assertEqual(self.run_script(BOOTSTRAP, "--license", "MIT").returncode, 0)
        state_path = self.workspace / ".hoa/licensing.yaml"
        state_path.write_text(
            self.state().replace("resolved: MIT", "resolved: Apache-2.0"),
            encoding="utf-8",
        )
        result = self.run_script(VALIDATOR)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("contradicts resolved", result.stdout)

    def test_lic_t10_metadata_artifact_contradiction_fails(self) -> None:
        self.start_constitution("MIT")
        self.assertEqual(self.run_script(BOOTSTRAP, "--license", "MIT").returncode, 0)
        (self.workspace / "LICENSE").write_text(
            "SPDX-License-Identifier: Apache-2.0\n", encoding="utf-8"
        )
        result = self.run_script(VALIDATOR)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("SHA-256 mismatch", result.stdout)
        self.assertIn("Apache-2.0", result.stdout)
        self.assertIn("MIT", result.stdout)

    def test_lic_t12_resolved_license_requires_machine_readable_declaration(self) -> None:
        self.start_constitution("MIT")
        self.assertEqual(self.run_script(BOOTSTRAP, "--license", "MIT").returncode, 0)
        artifact = self.workspace / "LICENSE"
        artifact.write_text("Fixture terms without a declaration.\n", encoding="utf-8")
        digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
        state_path = self.workspace / ".hoa/licensing.yaml"
        state_path.write_text(
            self.state().replace(
                self.state().split("artifact_sha256: ", 1)[1].strip(), digest
            ),
            encoding="utf-8",
        )
        result = self.run_script(VALIDATOR)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("SHA-256 mismatch", result.stdout)
        self.assertIn("must declare SPDX-License-Identifier", result.stdout)

    def test_bootstrap_rejects_artifact_without_machine_readable_declaration(self) -> None:
        self.start_constitution()
        result = self.run_script(
            BOOTSTRAP,
            "--license",
            "MIT",
            "--artifact-source",
            str(ROOT / "CMakeLists.txt"),
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must declare SPDX-License-Identifier", result.stderr)
        self.assertFalse((self.workspace / "LICENSE").exists())
        self.assertFalse((self.workspace / ".hoa/licensing.yaml").exists())

    def test_validator_rejects_ambiguous_duplicate_declarations(self) -> None:
        self.start_constitution("MIT")
        self.assertEqual(self.run_script(BOOTSTRAP, "--license", "MIT").returncode, 0)
        artifact = self.workspace / "LICENSE"
        with artifact.open("a", encoding="utf-8") as stream:
            stream.write("SPDX-License-Identifier: Apache-2.0\n")
        digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
        state_path = self.workspace / ".hoa/licensing.yaml"
        state_path.write_text(
            self.state().replace(
                self.state().split("artifact_sha256: ", 1)[1].strip(), digest
            ),
            encoding="utf-8",
        )
        result = self.run_script(VALIDATOR)
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("SHA-256 mismatch", result.stdout)
        self.assertIn("exactly one SPDX-License-Identifier", result.stdout)

    def test_forged_default_provenance_with_nondefault_value_fails(self) -> None:
        self.start_constitution("MIT")
        self.assertEqual(self.run_script(BOOTSTRAP, "--license", "MIT").returncode, 0)
        state_path = self.workspace / ".hoa/licensing.yaml"
        state_path.write_text(
            self.state().replace("provenance: explicit", "provenance: default"),
            encoding="utf-8",
        )
        result = self.run_script(VALIDATOR)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must resolve the policy default", result.stdout)

    def test_existing_license_blocks_default_without_being_overwritten(self) -> None:
        self.start_constitution("MIT")
        before = (self.workspace / "LICENSE").read_bytes()
        result = self.run_script(BOOTSTRAP)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("cannot replace", result.stderr)
        self.assertEqual((self.workspace / "LICENSE").read_bytes(), before)
        self.assertFalse((self.workspace / ".hoa/licensing.yaml").exists())

    def test_default_rejects_caller_supplied_artifact(self) -> None:
        self.start_constitution()
        source = self.workspace / "candidate.txt"
        source.write_text("SPDX-License-Identifier: MIT\n", encoding="utf-8")
        result = self.run_script(BOOTSTRAP, "--artifact-source", str(source))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not allowed", result.stderr)
        self.assertFalse((self.workspace / "LICENSE").exists())

    def test_exception_cannot_restate_the_default(self) -> None:
        self.start_constitution("GPL-3.0-or-later")
        result = self.run_script(
            BOOTSTRAP,
            "--policy-exception",
            "GPL-3.0-or-later",
            "--rationale",
            "No actual departure",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("must depart", result.stderr)

    def test_unconsumed_capability_after_constitution_is_rejected(self) -> None:
        self.start_constitution("MIT")
        self.assertEqual(self.run_script(BOOTSTRAP, "--license", "MIT").returncode, 0)
        (self.workspace / ".hoa/initial-constitution").write_text(
            CAPABILITY, encoding="utf-8"
        )
        result = self.run_script(VALIDATOR)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("was not consumed", result.stdout)


if __name__ == "__main__":
    unittest.main(verbosity=2)
