#!/usr/bin/env python3
"""Constitute a governed project license once, inside an explicit boundary."""

from __future__ import annotations

import argparse
import os
import re
import tempfile
from pathlib import Path

from governed_licensing import (
    ARTIFACT_RELATIVE,
    CAPABILITY_RELATIVE,
    CAPABILITY_VALUE,
    POLICY_DEFAULT,
    PRAXIS_ROOT,
    STATE_RELATIVE,
    render_state,
    sha256,
    validate_licensing,
)


LICENSE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9.+-]*$")


def fail(message: str) -> None:
    raise SystemExit(f"FAIL  governed licensing bootstrap — {message}")


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def default_artifact() -> bytes:
    terms = (PRAXIS_ROOT / "LICENSE").read_bytes()
    if b"GNU GENERAL PUBLIC LICENSE" not in terms or b"Version 3" not in terms:
        fail("Praxis GPLv3 terms source is not recognizable")
    declaration = (
        "SPDX-License-Identifier: GPL-3.0-or-later\n\n"
        "This new governed project applies the GNU General Public License, "
        "version 3 or any later version.\n\n"
    ).encode("utf-8")
    return declaration + terms


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("workspace", nargs="?", default=".")
    choice = parser.add_mutually_exclusive_group()
    choice.add_argument("--license", dest="explicit_license")
    choice.add_argument("--policy-exception", dest="exception_license")
    parser.add_argument("--rationale")
    parser.add_argument("--artifact-source", type=Path)
    args = parser.parse_args()
    root = Path(args.workspace).resolve()

    status, errors = validate_licensing(root)
    if status == "constituted":
        if errors:
            fail("existing licensing decision is invalid: " + "; ".join(errors))
        if args.artifact_source is not None:
            fail("artifact source cannot be applied to an existing decision")
        if args.explicit_license is not None or args.exception_license is not None:
            requested = args.explicit_license or args.exception_license
            from governed_licensing import load_licensing_state

            state = load_licensing_state(root)
            requested_provenance = (
                "explicit" if args.explicit_license is not None else "exception"
            )
            if (
                requested != state["resolved"]
                or requested_provenance != state["provenance"]
                or (
                    requested_provenance == "exception"
                    and (args.rationale or "").strip()
                    != state.get("exception_rationale")
                )
            ):
                fail("requested decision contradicts the existing decision")
        print("PASS  governed licensing bootstrap — existing decision preserved")
        return 0

    capability = root / CAPABILITY_RELATIVE
    if status != "pending" or errors or not capability.is_file():
        fail("not inside a valid governed initial-constitution boundary")
    if capability.read_text(encoding="utf-8").strip() != CAPABILITY_VALUE:
        fail("invalid initial-constitution capability")

    if args.rationale is not None and args.exception_license is None:
        fail("rationale is only valid with --policy-exception")
    if args.exception_license is not None and not (args.rationale or "").strip():
        fail("policy exception requires --rationale")
    if args.exception_license == POLICY_DEFAULT:
        fail("policy exception must depart from the applicable default")
    if (
        args.artifact_source is not None
        and args.explicit_license is None
        and args.exception_license is None
    ):
        fail(
            "default resolution uses the governed default artifact; "
            "--artifact-source is not allowed"
        )

    resolved = args.explicit_license or args.exception_license or POLICY_DEFAULT
    if LICENSE_ID.fullmatch(resolved) is None:
        fail(f"invalid license identifier: {resolved!r}")
    provenance = (
        "explicit"
        if args.explicit_license is not None
        else "exception"
        if args.exception_license is not None
        else "default"
    )

    artifact = root / ARTIFACT_RELATIVE
    created_artifact = False
    if args.artifact_source is not None:
        source = args.artifact_source.resolve()
        if not source.is_file():
            fail(f"artifact source is missing: {source}")
        if artifact.exists():
            fail("LICENSE already exists; refusing to overwrite it")
        artifact_content = source.read_bytes()
        created_artifact = True
    elif provenance == "default":
        if artifact.exists():
            fail("LICENSE already exists; default resolution cannot replace it")
        artifact_content = default_artifact()
        created_artifact = True
    else:
        if not artifact.is_file():
            fail("explicit and exception decisions require an existing LICENSE or --artifact-source")
        artifact_content = artifact.read_bytes()

    markers = re.findall(
        rb"(?m)^SPDX-License-Identifier:\s*(\S.*?)\s*$", artifact_content
    )
    if not markers:
        fail("artifact must declare SPDX-License-Identifier")
    if len(markers) != 1:
        fail("artifact must contain exactly one SPDX-License-Identifier")
    if markers[0].decode("utf-8", "replace") != resolved:
        fail("artifact SPDX declaration contradicts the requested license")

    if created_artifact:
        atomic_write(artifact, artifact_content)
    digest = sha256(artifact)
    state_content = render_state(
        resolved=resolved,
        provenance=provenance,
        artifact_sha256=digest,
        rationale=args.rationale.strip() if args.rationale is not None else None,
    ).encode("utf-8")
    atomic_write(root / STATE_RELATIVE, state_content)

    post_status, post_errors = validate_licensing(root)
    expected_post_errors = ["initial-constitution capability was not consumed"]
    if post_status != "constituted" or post_errors != expected_post_errors:
        fail("new decision failed pre-consumption validation: " + "; ".join(post_errors))
    capability.unlink()

    final_status, final_errors = validate_licensing(root)
    if final_status != "constituted" or final_errors:
        fail("new decision failed validation: " + "; ".join(final_errors))
    print(f"PASS  governed licensing bootstrap — {resolved} ({provenance})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
