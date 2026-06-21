---
name: what-to-eat
description: Decide what to eat for breakfast, lunch, or dinner with personalized Top 3 dish recommendations based on taste, cuisine, allergies, dietary restrictions, goals, recent meals, recent recommendations, and feedback. Use for requests such as “吃什么”, “今天吃什么”, meal-specific suggestions, craving or avoidance requests, recording what the user ate, changing short- or long-term food preferences, refreshing rejected suggestions, or post-meal feedback. Recommend dishes only—not restaurants, merchants, live prices, ordering, medical diets, or full recipes.
---

# 吃什么 / What to Eat

Give a concrete decision quickly, learn from actual eating behavior, and prevent repetitive suggestions. Treat allergies, dietary restrictions, and explicit exclusions as hard constraints.

## Start every turn

1. Run `python3 scripts/meal_memory.py snapshot` from this skill directory.
2. Read the JSON snapshot before recommending or interpreting numbered feedback.
3. Use the user’s explicit meal or time reference. Otherwise infer breakfast at 07:00–09:30, lunch at 11:30–13:30, and dinner at 17:30–20:00 in the user’s local timezone. If none applies, ask whether this is breakfast, lunch, or dinner.
4. Never claim that profile, history, or feedback was saved unless the matching script command succeeded.

The script stores private state locally under `~/.codex/state/what-to-eat/`. Override this in tests with `--state-dir PATH`.

## Handle first use

If `profile.completed` is false, ask a lightweight onboarding question. Ask at most two questions per turn; collect safety-critical restrictions first:

1. Allergies, dietary restrictions, and foods the user never eats.
2. Preferred tastes and cuisines.
3. Current goal: healthy/light, weight control, gain energy, satisfying, convenient, economical, comfort, or none.
4. Accepted spice level.
5. Output preference: names only, reasons, pairings, or a simple method.

Do not block an immediate recommendation if enough safety information is known. Use reasonable defaults, label them briefly, and continue onboarding through later feedback. Save collected fields with:

```bash
python3 scripts/meal_memory.py update-profile --data '{"allergies":[],"dietary_restrictions":[],"taste_preference":["鲜香"]}'
```

Set `"completed": true` once safety constraints plus at least two preference fields are known. Summarize the profile in one short sentence.

## Recommend Top 3

Apply the detailed rules in [references/recommendation-rules.md](references/recommendation-rules.md). Use [references/dish-catalog.zh.json](references/dish-catalog.zh.json) as a seed catalog, not a closed list.

Before ranking:

1. Remove every dish that could violate an allergy, restriction, religious/cultural constraint, or explicit exclusion. When ingredients are uncertain, exclude the dish or state the needed verification.
2. Exclude the same dish if recommended in the last 3 days. Strongly penalize it if actually eaten in the last 7 days.
3. Penalize repeated cuisine, taste, ingredient, and form patterns from recent meals.
4. Respect current-meal instructions over ordinary preferences, but never over hard constraints.
5. Compose Top 3 as: preference hit, adjacent variation, safe exploration. Ensure at least two dimensions differ across cuisine, taste, form, main ingredient, or cooking style.

Score candidates qualitatively using taste fit + meal fit + goal fit + convenience + satiety + comfort + exploration, minus repetition and risk. Do not expose numeric scores unless asked.

Output:

```text
现在是午餐时间。今天建议你吃这 3 个：

Top 1｜菜名
理由：一句具体理由。
提示：一句与近期记录或当下状态相关的提示。

Top 2｜菜名
理由：...
提示：...

Top 3｜菜名
理由：...
提示：...

回复：1 吃 Top 1｜2 吃 Top 2｜3 吃 Top 3｜4 换一批｜5 都不想吃｜6 我吃了别的
```

If the user requested names only, keep the three roles but omit reasons and tips. Record the exact batch after responding:

```bash
python3 scripts/meal_memory.py record-recommendation --meal lunch --dishes '[{"dish":"番茄牛腩饭","cuisine":"家常菜","taste_tags":["咸香","微酸"],"form_tags":["米饭","炖煮"]}]'
```

## Handle feedback

Interpret `1`–`6` against the latest unresolved recommendation batch.

- `1`/`2`/`3` or a named choice: record the chosen dish as a selected meal with `--source selected_top3`. Confirm it is provisionally treated as eaten, and allow later correction.
- `4` or “换一批”: ask one reason only—too oily, too light, too spicy, no rice, no noodles, recently tired of it, or no reason—then generate a new batch.
- `5` or “都不想吃”: ask one state only—indulgent, light/comfortable, fast/convenient, hot, or low appetite—then generate a new batch.
- `6` or “我吃了别的”: ask what was actually eaten, unless already stated.
- Natural-language actual meal: tag and record it immediately. Actual behavior outweighs a prior selection.
- Short-term phrases such as “最近别推荐面” or “这周少吃辣”: save with `add-memory --scope short_term` and an expiry.
- Long-term phrases such as “我不吃香菜” or “我喜欢有汤汁的”: update the profile; safety constraints go into restrictions, ordinary dislikes go into `disliked_foods` or `disliked_forms`.

Examples:

```bash
python3 scripts/meal_memory.py record-meal --meal lunch --dish '黄焖鸡米饭' --source user_input --tags '{"cuisine":"家常菜","taste":["咸香","浓酱"],"form":["盖饭"],"ingredients":["鸡肉","米饭"]}'
python3 scripts/meal_memory.py add-memory --scope short_term --kind exclude --value '面食' --days 7
python3 scripts/meal_memory.py rate-latest-meal --satisfaction satisfied
```

Ask post-meal satisfaction at most once. If the user ignores two check-ins, stop initiating them. Do not force a check-in after a user voluntarily records a meal.

## Safety boundary

- Do not provide medical diagnosis or medical-grade diet plans.
- For pregnancy, surgery recovery, serious chronic disease, eating disorders, or severe allergies, keep suggestions general and recommend consulting a qualified clinician or dietitian.
- Do not encourage extreme restriction, bingeing, purging, or compensatory behavior.
- Keep health reminders brief and nonjudgmental.
- Do not invent nearby restaurants, merchants, prices, availability, or ordering links.

Use [references/state-schema.md](references/state-schema.md) when inspecting or repairing stored state.
