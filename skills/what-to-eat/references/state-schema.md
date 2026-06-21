# Local state schema

`meal_memory.py` owns three JSON files in the state directory:

- `profile.json`: long-term preferences and hard constraints.
- `history.json`: actual/selected meals and satisfaction.
- `recommendations.json`: recommendation batches and user actions.
- `memory.json`: current-meal and expiring short-term instructions.

All files use UTF-8 and include a schema version. The script writes atomically. Do not edit them directly during normal use.

Profile fields: `completed`, `taste_preference`, `cuisine_preference`, `spicy_level`, `oil_salt_level`, `health_goal`, `allergies`, `dietary_restrictions`, `disliked_foods`, `preferred_forms`, `disliked_forms`, `recommendation_style`, `created_at`, and `updated_at`.

Meal records include `date`, `meal`, `actual_dish`, `source`, `satisfaction`, `tags`, and `feedback_text`.

Recommendation batches include `date`, `meal`, `recommendations`, `user_action`, `selected_dish`, `actual_dish`, `satisfaction`, and `feedback_text`.

Short-term memory entries include `scope`, `kind`, `value`, `created_at`, and `expires_at`; expired entries are removed when a snapshot is read.
