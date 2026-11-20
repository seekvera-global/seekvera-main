#!/usr/bin/env python3
"""Regression guard: an R125 audit-only run must never persist candidate-branch changes."""
import os
import re
from pathlib import Path

default_path = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "r125-hourly-candidate-resume.yml"
workflow_path = Path(os.environ.get("R125_WORKFLOW_SOURCE", str(default_path)))
workflow = workflow_path.read_text(encoding="utf-8")


def step_block(name: str) -> str:
    marker = re.compile(r"(?m)^      - name: " + re.escape(name) + r"\s*$")
    matches = list(marker.finditer(workflow))
    assert len(matches) == 1, f"Expected exactly one workflow step: {name}"
    match = matches[0]
    next_step = re.search(r"(?m)^      - (?:name|uses):", workflow[match.end():])
    end = match.end() + next_step.start() if next_step else len(workflow)
    return workflow[match.start():end]


def input_block(name: str) -> str:
    marker = re.compile(
        r"(?ms)^      " + re.escape(name) + r":\s*\n"
        r"(.*?)(?=^      [a-z_]+:\s*$|^  [a-z_]+:\s*$|\Z)"
    )
    match = marker.search(workflow)
    assert match, f"Missing workflow_dispatch input: {name}"
    return match.group(1)


assert re.search(r"(?m)^  workflow_dispatch:\s*$", workflow), "R125 must remain manually dispatched"
assert re.search(r"(?m)^name: R125 manual candidate resume \\(quota-safe by default\\)$", workflow), "Workflow name must reflect manual-only operation"
assert not re.search(r"(?im)^name: .*hourly", workflow), "Do not label a manual-only workflow as hourly"
assert "schedule:" not in workflow, "Unexpected scheduled R125 execution"
assert not re.search(r"(?m)^  push:\s*$", workflow), "R125 must not resume automatically on push"
assert re.search(r"(?m)^  cancel-in-progress: false\s*$", workflow), "Do not cancel an active R125 run"

for name in ("run_translations", "repair_candidates"):
    block = input_block(name)
    assert re.search(r"(?m)^        type: boolean\s*$", block), f"{name} must be a boolean input"
    assert re.search(r"(?m)^        required: false\s*$", block), f"{name} must remain optional"
    assert re.search(r"(?m)^        default: false\s*$", block), f"{name} must default to false"

translation = step_block("Resume public UI candidates")
assert "if: github.event_name == 'workflow_dispatch' && inputs.run_translations" in translation

audit_only = step_block("Record manual audit-only mode without querying translation quota")
assert "if: github.event_name == 'workflow_dispatch' && !inputs.run_translations" in audit_only
for command in ("git add ", "git commit ", "git push "):
    assert command not in audit_only, f"Audit-only bookkeeping must not persist candidate changes: {command}"

for name in (
    "Repair immutable locale identifiers (deterministic, no AI)",
    "Repair executable CSS source invariants (deterministic, no AI)",
):
    block = step_block(name)
    assert "if: success() && (inputs.run_translations || inputs.repair_candidates)" in block, (
        f"Candidate-mutating step is not explicitly gated: {name}"
    )

save = step_block("Save progress without publishing")
assert "if: success() && (inputs.run_translations || inputs.repair_candidates)" in save, (
    "Candidate-branch persistence must require explicit translation or repair opt-in"
)
assert "if: always()" not in save, "Persistence must not run after a failed validation step"
for command in (
    "git add docs/locale-candidates-20261008/",
    "git commit -m 'Checkpoint resumed locale candidates [skip ci]'",
    "git push origin HEAD:work/r125-locale-candidates-20261008",
):
    positions = [m.start() for m in re.finditer(re.escape(command), workflow)]
    assert len(positions) == 1 and save.find(command) >= 0, (
        f"Candidate persistence command must appear only inside the guarded save step: {command}"
    )

print("R125_AUDIT_ONLY_NO_CANDIDATE_WRITE_PASS")
