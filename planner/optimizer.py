"""Weekly meal planner that optimises ingredient reuse across the whole week."""
import math
import random
from collections import defaultdict
from dataclasses import dataclass
from itertools import combinations

from .catalog import DAYS, INGREDIENTS, MEALS, OFFERS, PANTRY_STAPLES, RECIPES, STORES

MAX_REPEATS = {"breakfast": 3, "lunch": 2, "dinner": 2}
SHELF_STABLE_NOTE = "Shelf-stable, keep for next week"

# Objective weights; their relative size encodes the priority order of the shopping rules.
W_OVER_BUDGET = 1000.0
W_PROMO_SHARE = 25.0
W_DISTINCT_INGREDIENT = 1.5
W_DISTINCT_PROTEIN = 3.0
W_WASTE_EUR = 6.0
W_KCAL_PER_100 = 1.2
W_PROTEIN_PER_10G = 1.2
W_EXTRA_STORE = 3.0
W_COST_EUR = 1.0
W_REPEAT_SAME_DAY = 50.0
W_REPEAT_OVER_LIMIT = 50.0
W_REPEAT_NEXT_DAY = 1.5


@dataclass(frozen=True)
class PlanRequest:
    budget: float = 75.0
    people: int = 1
    kcal_target: int = 2000
    protein_target: int = 120
    max_stores: int = 2


def _recipe_nutrition(recipe):
    kcal = protein = 0.0
    for key, g in recipe.ingredients.items():
        kcal += INGREDIENTS[key].kcal * g / 100
        protein += INGREDIENTS[key].protein * g / 100
    for key, g in recipe.pantry.items():
        kcal += PANTRY_STAPLES[key].kcal * g / 100
        protein += PANTRY_STAPLES[key].protein * g / 100
    return kcal, protein


NUTRITION = {k: _recipe_nutrition(r) for k, r in RECIPES.items()}
SLOTS = [(d, m) for d in range(len(DAYS)) for m in MEALS]
MIN_PORTION, MAX_PORTION = 0.6, 2.0


def _day_scales(plan, kcal_target):
    """Portion multiplier per day so each day's meals add up to the calorie target."""
    scales = []
    for d in range(len(DAYS)):
        kcal = sum(NUTRITION[k][0] for k in plan[d * 3:(d + 1) * 3])
        scales.append(min(MAX_PORTION, max(MIN_PORTION, kcal_target / kcal)) if kcal else 1.0)
    return scales


def _best_offer(offers, grams):
    """Cheapest way to cover `grams` with a single offer; promotions win ties."""
    def cost(o):
        return math.ceil(grams / o.pack_g) * o.price, not o.on_promo, o.store
    return min(offers, key=cost)


class _Evaluator:
    def __init__(self, req: PlanRequest, stores: tuple):
        self.req = req
        self.offers = defaultdict(list)
        for o in OFFERS:
            if o.store in stores:
                self.offers[o.ingredient].append(o)
        self.candidates = {
            meal: sorted(k for k, r in RECIPES.items()
                         if meal in r.meals and all(i in self.offers for i in r.ingredients))
            for meal in MEALS
        }

    def feasible(self):
        return all(self.candidates[m] for m in MEALS)

    def purchases(self, plan):
        scales = _day_scales(plan, self.req.kcal_target)
        needs = defaultdict(float)
        for i, key in enumerate(plan):
            for ing, g in RECIPES[key].ingredients.items():
                needs[ing] += g * self.req.people * scales[i // 3]
        bought = {}
        for ing, g in needs.items():
            offer = _best_offer(self.offers[ing], g)
            packs = math.ceil(g / offer.pack_g)
            bought[ing] = (offer, packs, g)
        return bought

    def score(self, plan):
        req = self.req
        bought = self.purchases(plan)
        cost = sum(o.price * p for o, p, _ in bought.values())
        promo_spend = sum(o.price * p for o, p, _ in bought.values() if o.on_promo)
        promo_items = sum(1 for o, _, _ in bought.values() if o.on_promo)
        waste = sum((o.pack_g * p - g) * o.price_per_g
                    for ing, (o, p, g) in bought.items() if INGREDIENTS[ing].perishable)
        stores = {o.store for o, _, _ in bought.values()}
        proteins = {RECIPES[k].main_protein for k in plan
                    if RECIPES[k].main_protein and INGREDIENTS[RECIPES[k].main_protein].perishable}

        nutrition_pen = 0.0
        variety_pen = 0.0
        scales = _day_scales(plan, req.kcal_target)
        for d in range(len(DAYS)):
            day = plan[d * 3:(d + 1) * 3]
            variety_pen += W_REPEAT_SAME_DAY * (len(day) - len(set(day)))
            kcal = sum(NUTRITION[k][0] for k in day) * scales[d]
            protein = sum(NUTRITION[k][1] for k in day) * scales[d]
            nutrition_pen += W_KCAL_PER_100 * max(0, req.kcal_target * 0.9 - kcal, kcal - req.kcal_target * 1.15) / 100
            nutrition_pen += W_PROTEIN_PER_10G * max(0, req.protein_target - protein) / 10

        counts = defaultdict(int)
        for i, k in enumerate(plan):
            counts[k] += 1
            if i >= 3 and plan[i - 3] == k:
                variety_pen += W_REPEAT_NEXT_DAY
        for k, c in counts.items():
            limit = max(MAX_REPEATS[m] for m in RECIPES[k].meals)
            variety_pen += W_REPEAT_OVER_LIMIT * max(0, c - limit)

        return (W_OVER_BUDGET * max(0.0, cost - req.budget)
                - W_PROMO_SHARE * (promo_spend / cost if cost else 0)
                - W_PROMO_SHARE * (promo_items / len(bought) if bought else 0)
                + W_DISTINCT_INGREDIENT * len(bought)
                + W_DISTINCT_PROTEIN * len(proteins)
                + W_WASTE_EUR * waste
                + nutrition_pen
                + W_EXTRA_STORE * max(0, len(stores) - 1)
                + W_COST_EUR * cost
                + variety_pen)

    def _climb(self, plan, max_passes):
        best = self.score(plan)
        for _ in range(max_passes):
            improved = False
            for i, (_, meal) in enumerate(SLOTS):
                current = plan[i]
                for cand in self.candidates[meal]:
                    if cand == current:
                        continue
                    plan[i] = cand
                    s = self.score(plan)
                    if s < best - 1e-9:
                        best, current, improved = s, cand, True
                plan[i] = current
            # Block move: swap every occurrence of a recipe at once, so an ingredient can be dropped entirely.
            for old in sorted(set(plan)):
                idx = [i for i, k in enumerate(plan) if k == old]
                meal = SLOTS[idx[0]][1]
                for cand in self.candidates[meal]:
                    if cand == old or any(SLOTS[i][1] not in RECIPES[cand].meals for i in idx):
                        continue
                    trial = list(plan)
                    for i in idx:
                        trial[i] = cand
                    s = self.score(trial)
                    if s < best - 1e-9:
                        plan, best, improved = trial, s, True
                        break
            if not improved:
                break
        return plan, best

    def optimise(self, restarts=4, max_passes=25, seed=42):
        # Fixed seed keeps plans reproducible; restarts escape local optima of single-slot moves.
        rng = random.Random(seed)
        best = None
        for r in range(restarts):
            if r == 0 and seed == 42:
                plan = [self.candidates[m][d % len(self.candidates[m])] for d, m in SLOTS]
            else:
                plan = [rng.choice(self.candidates[m]) for _, m in SLOTS]
            plan, score = self._climb(plan, max_passes)
            if best is None or score < best[1]:
                best = (list(plan), score)
        return best


def generate_week_plan(req: PlanRequest) -> dict:
    best = None
    for n in range(1, min(req.max_stores, len(STORES)) + 1):
        for stores in combinations(STORES, n):
            ev = _Evaluator(req, stores)
            if not ev.feasible():
                continue
            plan, score = ev.optimise()
            if best is None or score < best[1]:
                best = (plan, score, ev)
    if best is None:
        raise ValueError("No combination of stores can supply a full week of meals.")
    plan, score, ev = best
    extra_plan, extra_score = ev.optimise(restarts=12, seed=7)
    if extra_score < score:
        plan = extra_plan
    return _build_report(plan, ev)


def _fmt_qty(g):
    return f"{g / 1000:g} kg" if g >= 1000 else f"{round(g)} g"


def _build_report(plan, ev: _Evaluator) -> dict:
    req = ev.req
    bought = ev.purchases(plan)
    scales = _day_scales(plan, req.kcal_target)
    first_use = {}
    usage = defaultdict(list)
    week = []
    for d, day in enumerate(DAYS):
        meals = []
        for m_idx, meal in enumerate(MEALS):
            i = d * 3 + m_idx
            recipe = RECIPES[plan[i]]
            kcal, protein = (v * scales[d] for v in NUTRITION[recipe.key])
            meal_cost = 0.0
            discounted, reused = [], []
            for ing, g in recipe.ingredients.items():
                offer = bought[ing][0]
                grams = g * req.people * scales[d]
                meal_cost += grams * offer.price_per_g
                usage[ing].append({"day": day, "meal": meal, "recipe": recipe.name, "grams": grams})
                name = INGREDIENTS[ing].name
                if offer.on_promo:
                    discounted.append(name)
                if ing in first_use:
                    reused.append(name)
                else:
                    first_use[ing] = i
            meals.append({
                "meal": meal,
                "recipe": recipe.name,
                "calories": round(kcal),
                "protein": round(protein, 1),
                "cost": round(meal_cost, 2),
                "ingredients": [INGREDIENTS[i].name for i in recipe.ingredients],
                "discounted": discounted,
                "reused": reused,
                "pantry": [PANTRY_STAPLES[p].name for p in recipe.pantry],
            })
        week.append({
            "day": day,
            "portion_scale": round(scales[d], 2),
            "meals": meals,
            "calories": sum(x["calories"] for x in meals),
            "protein": round(sum(x["protein"] for x in meals), 1),
            "cost": round(sum(x["cost"] for x in meals), 2),
        })

    tracking, shopping = [], []
    for ing in sorted(bought, key=lambda k: first_use[k]):
        offer, packs, needed = bought[ing]
        purchased = offer.pack_g * packs
        remaining = purchased - needed
        info = INGREDIENTS[ing]
        if remaining < 1:
            status = "Fully used"
        elif not info.perishable:
            status = SHELF_STABLE_NOTE
        elif remaining / purchased <= 0.15:
            status = "Small remainder"
        else:
            status = "Waste risk"
        tracking.append({
            "ingredient": info.name,
            "store": offer.store,
            "purchased_g": purchased,
            "purchased_label": f"{_fmt_qty(purchased)} purchased at {offer.store}",
            "uses": usage[ing],
            "meal_count": len(usage[ing]),
            "remaining_g": round(remaining),
            "status": status,
            "perishable": info.perishable,
        })
        shopping.append({
            "ingredient": info.name,
            "store": offer.store,
            "packs": packs,
            "pack_size": _fmt_qty(offer.pack_g),
            "price": round(offer.price * packs, 2),
            "regular_price": round(offer.regular_price * packs, 2),
            "on_promo": offer.on_promo,
        })

    pantry_totals = defaultdict(float)
    for i, key in enumerate(plan):
        for p, g in RECIPES[key].pantry.items():
            pantry_totals[p] += g * req.people * scales[i // 3]
    pantry, pantry_purchases = [], []
    for p, g in sorted(pantry_totals.items(), key=lambda x: PANTRY_STAPLES[x[0]].name):
        staple = PANTRY_STAPLES[p]
        large = g > staple.large_qty_g
        pantry.append({"name": staple.name, "weekly_g": round(g), "buy": large})
        if large:
            packs = math.ceil(g / staple.pack_g)
            pantry_purchases.append({
                "ingredient": staple.name, "store": "Any", "packs": packs,
                "pack_size": _fmt_qty(staple.pack_g), "price": round(staple.est_price * packs, 2),
                "regular_price": round(staple.est_price * packs, 2), "on_promo": False,
            })
    shopping.extend(pantry_purchases)

    total = round(sum(s["price"] for s in shopping), 2)
    regular = round(sum(s["regular_price"] for s in shopping), 2)
    promo_items = sum(1 for s in shopping if s["on_promo"])
    promo_pct = round(100 * promo_items / len(shopping)) if shopping else 0
    stores = sorted({s["store"] for s in shopping if s["store"] != "Any"})
    reused = sorted((t for t in tracking if t["meal_count"] >= 3), key=lambda t: -t["meal_count"])
    wasted = [t for t in tracking if t["status"] == "Waste risk"]

    summary = _summary_text(total, regular - total, promo_pct, reused, stores, req)
    return {
        "request": req.__dict__,
        "summary": {
            "text": summary,
            "total_cost": total,
            "savings": round(regular - total, 2),
            "promo_pct": promo_pct,
            "within_budget": total <= req.budget,
            "stores": stores,
            "reused_ingredients": [t["ingredient"] for t in reused],
            "waste_risk": [t["ingredient"] for t in wasted],
            "avg_calories": round(sum(d["calories"] for d in week) / len(week)),
            "avg_protein": round(sum(d["protein"] for d in week) / len(week), 1),
        },
        "week": week,
        "tracking": tracking,
        "shopping_list": shopping,
        "pantry": {"label": "Pantry Staples (Assumed Available)", "items": pantry},
    }


def _join(items):
    return items[0] if len(items) == 1 else ", ".join(items[:-1]) + " and " + items[-1]


def _summary_text(total, savings, promo_pct, reused, stores, req):
    people = "" if req.people == 1 else f" for {req.people} people"
    parts = [f"This meal plan costs €{total:.2f} for the week{people} and saves an estimated "
             f"€{savings:.2f} through current supermarket promotions."]
    if total > req.budget:
        parts.append(f"It is €{total - req.budget:.2f} over your €{req.budget:.2f} budget; "
                     "this is the cheapest week the current offers allow.")
    parts.append(f"{promo_pct}% of purchased ingredients are currently on promotion.")
    if reused:
        names = [t["ingredient"].lower().replace("greek", "Greek") for t in reused[:6]]
        parts.append(f"The plan uses {_join(names)} across multiple meals, "
                     "reducing food waste and maximizing the value of discounted products.")
    n = len(stores)
    parts.append(f"Only {n} supermarket{'s' if n != 1 else ''} need{'s' if n == 1 else ''} to be visited: "
                 f"{_join(stores)}.")
    return " ".join(parts)
