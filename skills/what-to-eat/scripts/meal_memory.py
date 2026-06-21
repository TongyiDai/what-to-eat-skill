#!/usr/bin/env python3
"""Local, dependency-free memory store for the what-to-eat skill."""

import argparse
import json
import os
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

SCHEMA_VERSION = 1
MEALS = {"breakfast", "lunch", "dinner"}
SATISFACTIONS = {"satisfied", "neutral", "bad", "unknown"}


def now():
    return datetime.now().astimezone()


def stamp():
    return now().isoformat(timespec="seconds")


def default_profile():
    t = stamp()
    return {
        "schema_version": SCHEMA_VERSION,
        "completed": False,
        "taste_preference": [], "cuisine_preference": [], "spicy_level": None,
        "oil_salt_level": None, "health_goal": [], "allergies": [],
        "dietary_restrictions": [], "disliked_foods": [], "preferred_forms": [],
        "disliked_forms": [], "recommendation_style": "dish_with_reason",
        "created_at": t, "updated_at": t,
    }


DEFAULTS = {
    "profile.json": default_profile,
    "history.json": lambda: {"schema_version": SCHEMA_VERSION, "meals": []},
    "recommendations.json": lambda: {"schema_version": SCHEMA_VERSION, "batches": []},
    "memory.json": lambda: {"schema_version": SCHEMA_VERSION, "entries": []},
}


class Store:
    def __init__(self, root):
        self.root = Path(root).expanduser()
        self.root.mkdir(parents=True, exist_ok=True)

    def load(self, name):
        path = self.root / name
        if not path.exists():
            data = DEFAULTS[name]()
            self.save(name, data)
            return data
        try:
            with path.open(encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError) as exc:
            raise SystemExit(f"Cannot read {path}: {exc}")
        if data.get("schema_version") != SCHEMA_VERSION:
            raise SystemExit(f"Unsupported schema version in {path}")
        return data

    def save(self, name, data):
        target = self.root / name
        fd, tmp = tempfile.mkstemp(prefix=f".{name}.", dir=self.root, text=True)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write("\n")
            os.replace(tmp, target)
        finally:
            if os.path.exists(tmp):
                os.unlink(tmp)


def parse_json(raw, expected):
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON: {exc}")
    if not isinstance(value, expected):
        raise SystemExit(f"Expected JSON {expected.__name__}")
    return value


def snapshot(store, _args):
    profile = store.load("profile.json")
    history = store.load("history.json")
    recs = store.load("recommendations.json")
    memory = store.load("memory.json")
    current = now()
    kept = []
    for entry in memory["entries"]:
        expiry = entry.get("expires_at")
        if not expiry or datetime.fromisoformat(expiry) > current:
            kept.append(entry)
    if len(kept) != len(memory["entries"]):
        memory["entries"] = kept
        store.save("memory.json", memory)
    result = {
        "profile": profile,
        "recent_meals": history["meals"][-14:],
        "recent_recommendations": recs["batches"][-10:],
        "active_memory": kept,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))


def update_profile(store, args):
    updates = parse_json(args.data, dict)
    forbidden = {"schema_version", "created_at"}
    if forbidden.intersection(updates):
        raise SystemExit("schema_version and created_at cannot be changed")
    profile = store.load("profile.json")
    unknown = set(updates) - set(profile)
    if unknown:
        raise SystemExit(f"Unknown profile fields: {', '.join(sorted(unknown))}")
    profile.update(updates)
    profile["updated_at"] = stamp()
    store.save("profile.json", profile)
    print(json.dumps(profile, ensure_ascii=False, indent=2))


def record_recommendation(store, args):
    dishes = parse_json(args.dishes, list)
    if len(dishes) != 3:
        raise SystemExit("A recommendation batch must contain exactly 3 dishes")
    if any(not isinstance(x, dict) or not x.get("dish") for x in dishes):
        raise SystemExit("Each recommendation must be an object with a dish")
    data = store.load("recommendations.json")
    data["batches"].append({
        "date": stamp(), "meal": args.meal, "recommendations": dishes,
        "user_action": "no_response", "selected_dish": None,
        "actual_dish": None, "satisfaction": "unknown", "feedback_text": None,
    })
    data["batches"] = data["batches"][-100:]
    store.save("recommendations.json", data)
    print(json.dumps(data["batches"][-1], ensure_ascii=False, indent=2))


def record_meal(store, args):
    tags = parse_json(args.tags, dict)
    history = store.load("history.json")
    record = {
        "date": stamp(), "meal": args.meal, "actual_dish": args.dish,
        "source": args.source, "satisfaction": args.satisfaction,
        "tags": tags, "feedback_text": args.feedback_text,
    }
    history["meals"].append(record)
    history["meals"] = history["meals"][-200:]
    store.save("history.json", history)
    recs = store.load("recommendations.json")
    for batch in reversed(recs["batches"]):
        if batch["meal"] == args.meal and batch["user_action"] == "no_response":
            names = [x["dish"] for x in batch["recommendations"]]
            batch["actual_dish"] = args.dish
            batch["selected_dish"] = args.dish if args.dish in names else None
            batch["user_action"] = "selected_top3" if args.dish in names else "ate_other"
            batch["satisfaction"] = args.satisfaction
            batch["feedback_text"] = args.feedback_text
            store.save("recommendations.json", recs)
            break
    print(json.dumps(record, ensure_ascii=False, indent=2))


def add_memory(store, args):
    data = store.load("memory.json")
    created = now()
    expires = created + timedelta(days=args.days) if args.scope == "short_term" else None
    entry = {
        "scope": args.scope, "kind": args.kind, "value": args.value,
        "created_at": created.isoformat(timespec="seconds"),
        "expires_at": expires.isoformat(timespec="seconds") if expires else None,
    }
    data["entries"].append(entry)
    store.save("memory.json", data)
    print(json.dumps(entry, ensure_ascii=False, indent=2))


def rate_latest(store, args):
    history = store.load("history.json")
    if not history["meals"]:
        raise SystemExit("No meal exists to rate")
    history["meals"][-1]["satisfaction"] = args.satisfaction
    store.save("history.json", history)
    recs = store.load("recommendations.json")
    actual = history["meals"][-1]["actual_dish"]
    for batch in reversed(recs["batches"]):
        if batch.get("actual_dish") == actual:
            batch["satisfaction"] = args.satisfaction
            store.save("recommendations.json", recs)
            break
    print(json.dumps(history["meals"][-1], ensure_ascii=False, indent=2))


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", default=os.environ.get("WHAT_TO_EAT_HOME", "~/.codex/state/what-to-eat"))
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("snapshot").set_defaults(func=snapshot)
    p = sub.add_parser("update-profile"); p.add_argument("--data", required=True); p.set_defaults(func=update_profile)
    p = sub.add_parser("record-recommendation"); p.add_argument("--meal", choices=sorted(MEALS), required=True); p.add_argument("--dishes", required=True); p.set_defaults(func=record_recommendation)
    p = sub.add_parser("record-meal"); p.add_argument("--meal", choices=sorted(MEALS), required=True); p.add_argument("--dish", required=True); p.add_argument("--source", choices=["selected_top3", "user_input", "post_meal_checkin"], required=True); p.add_argument("--satisfaction", choices=sorted(SATISFACTIONS), default="unknown"); p.add_argument("--tags", default="{}"); p.add_argument("--feedback-text"); p.set_defaults(func=record_meal)
    p = sub.add_parser("add-memory"); p.add_argument("--scope", choices=["current_meal", "short_term"], required=True); p.add_argument("--kind", choices=["prefer", "avoid", "exclude", "goal"], required=True); p.add_argument("--value", required=True); p.add_argument("--days", type=int, default=7); p.set_defaults(func=add_memory)
    p = sub.add_parser("rate-latest-meal"); p.add_argument("--satisfaction", choices=sorted(SATISFACTIONS - {"unknown"}), required=True); p.set_defaults(func=rate_latest)
    return parser


def main():
    args = build_parser().parse_args()
    if getattr(args, "days", 1) < 1:
        raise SystemExit("--days must be at least 1")
    args.func(Store(args.state_dir), args)


if __name__ == "__main__":
    main()
