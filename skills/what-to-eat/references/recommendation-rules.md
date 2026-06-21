# Recommendation rules

## Evidence priority

Use this order when signals conflict:

1. Hard safety constraints
2. Actual dishes eaten
3. Post-meal satisfaction
4. Explicit rejection reasons
5. Selected recommendations
6. Onboarding declarations

Make a compromise when behavior conflicts with a stated health goal. Preserve satisfaction while reducing the repeated heavy pattern; do not lecture.

## Repetition controls

- Same dish recommended within 3 days: exclude by default.
- Same dish eaten within 7 days: strongly penalize.
- Explicit “最近别推荐”: short-term exclusion.
- Explicit “以后少推荐”: long-term low weight.
- Same cuisine for 2 consecutive meals: penalize next meal.
- Same cuisine more than 3 times in the last 7 meals: penalize for 2 meals.
- Two consecutive heavy-spicy-dry meals: favor soup, steamed/boiled, light, or sweet-sour forms next.
- Repeated rice bowls, noodles, hotpot, fried food, or another form: rotate the form.

Strong preferences retain a higher baseline but never bypass repetition controls.

## Top 3 roles

- Top 1, preference hit: best safe match for the current meal and state.
- Top 2, adjacent variation: familiar enough, but vary cuisine, taste, ingredient, or form.
- Top 3, safe exploration: a lower-frequency cuisine or form without a large preference jump.

Start near 60% familiar, 25% adjacent, 15% exploratory over time. Increase exploration after “吃腻了” or repeated exploration acceptance. Decrease it after repeated exploration rejection or “今天就想吃熟悉的”.

## Meal defaults

- Breakfast: easy to digest, practical, moderate portion; do not assume sweet or savory.
- Lunch: adequate satiety and execution speed; consider afternoon comfort.
- Dinner: respect the user’s desired satisfaction while avoiding automatic overemphasis on heaviness.

## Tag every recommendation

Include dish, cuisine, taste tags, form tags, main ingredients when known, and a rough health level. Tags drive later deduplication; do not leave them empty merely because they are not shown to the user.
