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
    match = marker.search(workflow)
    assert match, f"Missing workflow step: {name}"
    next_step = re.search(r"(?m)^      - (?:name|uses):", workflow[match.end():])
    end = match.end() + next_step.start() if next_step else len(workflow)
    return workflow[match.start():end]


assert re.search(r"(?m)^  workflow_dispatch:\s*$", workflow), "R125 must remain manually dispatched"
assert "schedule:" not in workflow, "Unexpected scheduled R125 execution"
assert workflow.count("default: false") >= 2, "Translation and repair inputs must default to false"
assert re.search(r"(?m)^  cancel-in-progress: false\s*$", workflow), "Do not cancel an active R125 run"

translation = step_block("Resume public UI candidates")
assert "if: github.event_name == 'workflow_dispatch' && inputs.run_translations" in translation

for name in (
    "Repair immutable locale identifiers (deterministic, no AI)",
    "Repair executable CSS source invariants (deterministic, no AI)",
):
    block = step_block(name)
    assert "if: success() && (inputs.run_translations || inputs.repair_candidates)" in block, (
        f"Candidate-mutating step is not explicitly gated: {name}"
    )

save = step_block("Save progress without publishing")
assert "if: always() && (inputs.run_translations || inputs.repair_candidates)" in save, (
    "Candidate-branch persistence must require explicit translation or repair opt-in"
)
for command in (
    "git add docs/locale-candidates-20261008/",
    "git push origin HEAD:work/r125-locale-candidates-20261008",
):
    positions = [m.start() for m in re.finditer(re.escape(command), workflow)]
    assert len(positions) == 1 and save.find(command) >= 0, (
        f"Candidate persistence command must appear only inside the guarded save step: {command}"
    )

print("R125_AUDIT_ONLY_NO_CANDIDATE_WRITE_PASS")
