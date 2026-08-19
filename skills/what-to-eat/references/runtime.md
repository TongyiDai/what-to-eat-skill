# Runtime, state, and automation contract

## Local state

The Skill stores private state under `WHAT_TO_EAT_HOME`, defaulting to
`~/.codex/state/what-to-eat`. Test runs must pass a temporary `--state-dir` and
must not touch the user's real history. Run `scripts/doctor.py --json` before
using the store. A failed write means the meal, recommendation, or feedback was
not saved.

## Automation

Recurring reminders require the active host's automation capability. The Skill
must report the capability as unavailable when it cannot create or update
recurring tasks. In that case, provide the recommendation on demand and keep
the local profile unchanged with respect to automation IDs.

When changing a reminder, update the saved automation ID. Never create a second
task when an existing ID is available. Scheduling is successful only after all
requested automation calls return success.

## Time and safety

Use the user's local timezone. Store meal times as `HH:MM`. Allergies and hard
dietary restrictions outrank taste preferences. This Skill does not diagnose,
prescribe medical diets, choose merchants, or invent prices and ordering links.
