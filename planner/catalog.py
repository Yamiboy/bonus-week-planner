"""Sample supermarket offers, pantry staples and recipes (prices in EUR, quantities in grams)."""
from dataclasses import dataclass, field

STORES = ("Lidl", "Albert Heijn", "Jumbo")


@dataclass(frozen=True)
class Ingredient:
    key: str
    name: str
    kcal: float  # per 100 g
    protein: float  # per 100 g
    category: str
    perishable: bool = True


@dataclass(frozen=True)
class Offer:
    ingredient: str
    store: str
    pack_g: int
    price: float
    regular_price: float

    @property
    def on_promo(self) -> bool:
        return self.price < self.regular_price

    @property
    def price_per_g(self) -> float:
        return self.price / self.pack_g


@dataclass(frozen=True)
class PantryStaple:
    key: str
    name: str
    kcal: float
    protein: float
    large_qty_g: float  # weekly usage above this means the user must buy a pack
    pack_g: int
    est_price: float


@dataclass(frozen=True)
class Recipe:
    key: str
    name: str
    meals: tuple
    ingredients: dict  # ingredient key -> grams per serving
    pantry: dict = field(default_factory=dict)  # pantry key -> grams per serving
    main_protein: str | None = None


INGREDIENTS = {i.key: i for i in [
    Ingredient("chicken_breast", "Chicken breast", 165, 31, "protein"),
    Ingredient("minced_beef", "Minced beef", 250, 26, "protein"),
    Ingredient("salmon", "Salmon fillet", 208, 20, "protein"),
    Ingredient("eggs", "Eggs", 143, 13, "protein"),
    Ingredient("tofu", "Firm tofu", 120, 13, "protein"),
    Ingredient("canned_tuna", "Canned tuna", 116, 26, "protein", perishable=False),
    Ingredient("chickpeas", "Chickpeas (canned)", 139, 7, "protein", perishable=False),
    Ingredient("greek_yogurt", "Greek yogurt", 73, 9, "dairy"),
    Ingredient("cottage_cheese", "Cottage cheese", 98, 11, "dairy"),
    Ingredient("milk", "Semi-skimmed milk", 46, 3.4, "dairy"),
    Ingredient("cheese", "Grated cheese", 380, 25, "dairy"),
    Ingredient("feta", "Feta", 264, 14, "dairy"),
    Ingredient("rice", "Rice", 350, 7, "carb", perishable=False),
    Ingredient("pasta", "Pasta", 355, 12, "carb", perishable=False),
    Ingredient("tortilla_wraps", "Tortilla wraps", 300, 8, "carb"),
    Ingredient("oats", "Rolled oats", 370, 13, "carb", perishable=False),
    Ingredient("bread", "Wholemeal bread", 245, 10, "carb"),
    Ingredient("potatoes", "Potatoes", 77, 2, "carb"),
    Ingredient("broccoli", "Broccoli", 34, 2.8, "veg"),
    Ingredient("bell_pepper", "Bell peppers", 26, 1, "veg"),
    Ingredient("spinach", "Spinach", 23, 2.9, "veg"),
    Ingredient("tomatoes", "Tomatoes", 18, 0.9, "veg"),
    Ingredient("cucumber", "Cucumber", 15, 0.7, "veg"),
    Ingredient("carrots", "Carrots", 41, 0.9, "veg"),
    Ingredient("zucchini", "Zucchini", 17, 1.2, "veg"),
    Ingredient("lettuce", "Lettuce mix", 17, 1.4, "veg"),
    Ingredient("passata", "Tomato passata", 30, 1.3, "veg", perishable=False),
    Ingredient("banana", "Bananas", 89, 1.1, "fruit"),
    Ingredient("berries", "Frozen mixed berries", 50, 1, "fruit", perishable=False),
    Ingredient("peanut_butter", "Peanut butter", 600, 25, "spread", perishable=False),
]}

OFFERS = [
    Offer("chicken_breast", "Lidl", 1000, 7.99, 10.99),
    Offer("chicken_breast", "Albert Heijn", 500, 6.49, 6.49),
    Offer("chicken_breast", "Jumbo", 900, 9.49, 9.49),
    Offer("minced_beef", "Lidl", 500, 4.29, 4.29),
    Offer("minced_beef", "Albert Heijn", 500, 3.99, 5.29),
    Offer("minced_beef", "Jumbo", 1000, 7.99, 7.99),
    Offer("salmon", "Lidl", 250, 4.49, 4.49),
    Offer("salmon", "Albert Heijn", 250, 5.29, 5.29),
    Offer("salmon", "Jumbo", 250, 3.99, 5.49),
    Offer("eggs", "Lidl", 600, 2.69, 2.69),
    Offer("eggs", "Albert Heijn", 600, 2.99, 2.99),
    Offer("eggs", "Jumbo", 360, 1.89, 1.89),
    Offer("tofu", "Albert Heijn", 375, 2.29, 2.29),
    Offer("tofu", "Jumbo", 375, 1.79, 2.39),
    Offer("canned_tuna", "Lidl", 145, 1.29, 1.29),
    Offer("canned_tuna", "Albert Heijn", 145, 1.79, 1.79),
    Offer("canned_tuna", "Jumbo", 435, 3.49, 4.99),
    Offer("chickpeas", "Lidl", 265, 0.69, 0.69),
    Offer("chickpeas", "Albert Heijn", 265, 0.89, 0.89),
    Offer("greek_yogurt", "Albert Heijn", 1000, 2.49, 3.29),
    Offer("greek_yogurt", "Lidl", 500, 1.49, 1.49),
    Offer("greek_yogurt", "Jumbo", 1000, 2.99, 2.99),
    Offer("cottage_cheese", "Albert Heijn", 200, 1.29, 1.29),
    Offer("cottage_cheese", "Lidl", 250, 1.09, 1.09),
    Offer("milk", "Lidl", 1000, 1.09, 1.09),
    Offer("milk", "Albert Heijn", 1000, 1.19, 1.19),
    Offer("milk", "Jumbo", 1000, 1.15, 1.15),
    Offer("cheese", "Lidl", 200, 2.19, 2.19),
    Offer("cheese", "Albert Heijn", 150, 2.29, 2.29),
    Offer("cheese", "Jumbo", 175, 1.99, 2.59),
    Offer("feta", "Lidl", 200, 1.79, 1.79),
    Offer("feta", "Albert Heijn", 200, 2.49, 2.49),
    Offer("rice", "Lidl", 1000, 1.49, 1.99),
    Offer("rice", "Albert Heijn", 1000, 2.29, 2.29),
    Offer("rice", "Jumbo", 1000, 1.99, 1.99),
    Offer("pasta", "Lidl", 500, 0.89, 0.89),
    Offer("pasta", "Albert Heijn", 500, 1.19, 1.59),
    Offer("pasta", "Jumbo", 1000, 1.69, 1.69),
    Offer("tortilla_wraps", "Albert Heijn", 370, 1.99, 2.49),
    Offer("tortilla_wraps", "Lidl", 370, 1.39, 1.39),
    Offer("oats", "Lidl", 500, 0.99, 0.99),
    Offer("oats", "Albert Heijn", 500, 1.29, 1.29),
    Offer("oats", "Jumbo", 1000, 1.79, 1.79),
    Offer("bread", "Albert Heijn", 800, 2.19, 2.19),
    Offer("bread", "Lidl", 800, 1.59, 1.59),
    Offer("bread", "Jumbo", 800, 1.89, 1.89),
    Offer("potatoes", "Lidl", 2000, 1.99, 1.99),
    Offer("potatoes", "Albert Heijn", 1500, 2.49, 2.99),
    Offer("broccoli", "Albert Heijn", 500, 0.99, 1.59),
    Offer("broccoli", "Lidl", 500, 1.29, 1.29),
    Offer("broccoli", "Jumbo", 500, 1.39, 1.39),
    Offer("bell_pepper", "Lidl", 500, 1.29, 1.89),
    Offer("bell_pepper", "Albert Heijn", 500, 2.19, 2.19),
    Offer("spinach", "Albert Heijn", 300, 1.79, 1.79),
    Offer("spinach", "Lidl", 300, 1.19, 1.69),
    Offer("tomatoes", "Lidl", 500, 1.49, 1.49),
    Offer("tomatoes", "Albert Heijn", 500, 1.69, 1.69),
    Offer("tomatoes", "Jumbo", 500, 1.29, 1.79),
    Offer("cucumber", "Lidl", 350, 0.69, 0.69),
    Offer("cucumber", "Albert Heijn", 350, 0.79, 0.99),
    Offer("carrots", "Lidl", 1000, 0.99, 0.99),
    Offer("carrots", "Albert Heijn", 1000, 1.29, 1.29),
    Offer("zucchini", "Lidl", 300, 0.79, 0.79),
    Offer("zucchini", "Albert Heijn", 300, 0.99, 0.99),
    Offer("lettuce", "Lidl", 200, 0.99, 0.99),
    Offer("lettuce", "Albert Heijn", 150, 1.19, 1.19),
    Offer("passata", "Lidl", 500, 0.69, 0.69),
    Offer("passata", "Albert Heijn", 500, 0.89, 1.09),
    Offer("banana", "Lidl", 1000, 1.39, 1.39),
    Offer("banana", "Albert Heijn", 1000, 1.69, 1.99),
    Offer("berries", "Lidl", 750, 2.99, 3.99),
    Offer("berries", "Albert Heijn", 500, 3.29, 3.29),
    Offer("peanut_butter", "Lidl", 350, 1.99, 1.99),
    Offer("peanut_butter", "Albert Heijn", 350, 2.69, 2.69),
]

PANTRY_STAPLES = {p.key: p for p in [
    PantryStaple("salt", "Salt", 0, 0, 500, 1000, 0.59),
    PantryStaple("pepper", "Pepper", 250, 10, 100, 50, 1.49),
    PantryStaple("oil", "Cooking oil", 884, 0, 500, 1000, 2.49),
    PantryStaple("olive_oil", "Olive oil", 884, 0, 400, 500, 5.99),
    PantryStaple("garlic", "Garlic", 149, 6.4, 150, 250, 0.99),
    PantryStaple("onion", "Onion", 40, 1.1, 1000, 1000, 1.19),
    PantryStaple("butter", "Butter", 717, 0.9, 250, 250, 2.79),
    PantryStaple("flour", "Flour", 364, 10, 500, 1000, 0.89),
    PantryStaple("sugar", "Sugar", 387, 0, 500, 1000, 1.19),
    PantryStaple("soy_sauce", "Soy sauce", 53, 8, 250, 250, 1.99),
    PantryStaple("dried_herbs", "Dried herbs", 270, 10, 100, 20, 1.29),
    PantryStaple("spices", "Common spices", 300, 12, 100, 40, 1.49),
    PantryStaple("stock_cube", "Stock cubes", 250, 10, 100, 80, 1.09),
    PantryStaple("vinegar", "Vinegar", 20, 0, 500, 500, 0.99),
    PantryStaple("mustard", "Mustard", 66, 4, 200, 250, 1.19),
    PantryStaple("ketchup", "Ketchup", 112, 1.2, 300, 500, 1.79),
    PantryStaple("mayonnaise", "Mayonnaise", 680, 1, 250, 500, 2.29),
]}

B, L, D = "breakfast", "lunch", "dinner"

RECIPES = {r.key: r for r in [
    # Breakfast
    Recipe("yogurt_bowl", "Greek yogurt bowl with berries and oats", (B,),
           {"greek_yogurt": 250, "berries": 100, "oats": 50}, main_protein="greek_yogurt"),
    Recipe("overnight_oats", "Overnight oats with banana and peanut butter", (B,),
           {"oats": 70, "milk": 250, "banana": 100, "peanut_butter": 15}),
    Recipe("scrambled_eggs", "Scrambled eggs on toast with spinach", (B,),
           {"eggs": 180, "bread": 70, "spinach": 50}, {"butter": 10, "salt": 1, "pepper": 1}, "eggs"),
    Recipe("cottage_toast", "Cottage cheese toast with tomato", (B,),
           {"cottage_cheese": 150, "bread": 80, "tomatoes": 100}, {"pepper": 1}, "cottage_cheese"),
    Recipe("pepper_omelette", "Bell pepper and cheese omelette", (B,),
           {"eggs": 180, "bell_pepper": 80, "cheese": 20}, {"oil": 5, "salt": 1}, "eggs"),
    Recipe("banana_smoothie", "Banana and yogurt smoothie", (B,),
           {"greek_yogurt": 200, "banana": 120, "milk": 200, "oats": 30}, main_protein="greek_yogurt"),
    # Lunch
    Recipe("chicken_wraps", "Chicken wraps with peppers and yogurt sauce", (L, D),
           {"chicken_breast": 150, "tortilla_wraps": 120, "bell_pepper": 80, "lettuce": 40, "greek_yogurt": 50},
           {"oil": 5, "spices": 2, "garlic": 3}, "chicken_breast"),
    Recipe("tuna_pasta_salad", "Tuna pasta salad", (L,),
           {"pasta": 90, "canned_tuna": 120, "cucumber": 80, "tomatoes": 80},
           {"mayonnaise": 15, "pepper": 1}, "canned_tuna"),
    Recipe("chickpea_feta_salad", "Chickpea, feta and pepper salad", (L,),
           {"chickpeas": 200, "feta": 50, "cucumber": 100, "tomatoes": 100, "bell_pepper": 60},
           {"olive_oil": 10, "vinegar": 5, "dried_herbs": 1}, "chickpeas"),
    Recipe("chicken_rice_bowl", "Chicken, broccoli and rice bowl", (L, D),
           {"chicken_breast": 150, "rice": 80, "broccoli": 150, "greek_yogurt": 40},
           {"soy_sauce": 15, "oil": 5, "garlic": 3}, "chicken_breast"),
    Recipe("egg_spinach_wrap", "Egg and spinach wrap", (L,),
           {"eggs": 120, "tortilla_wraps": 120, "spinach": 60, "cheese": 20}, {"butter": 5, "salt": 1}, "eggs"),
    Recipe("tomato_soup_toastie", "Tomato soup with cheese toastie", (L,),
           {"passata": 300, "bread": 80, "cheese": 40}, {"onion": 50, "stock_cube": 5, "butter": 5}),
    Recipe("salmon_potato_salad", "Salmon and potato salad", (L, D),
           {"salmon": 120, "potatoes": 250, "spinach": 50, "greek_yogurt": 50},
           {"mustard": 5, "dried_herbs": 1}, "salmon"),
    Recipe("tuna_wrap", "Tuna wrap with cucumber", (L,),
           {"canned_tuna": 120, "tortilla_wraps": 120, "lettuce": 40, "cucumber": 60},
           {"mayonnaise": 10}, "canned_tuna"),
    # Dinner
    Recipe("chicken_stir_fry", "Chicken stir fry with broccoli and peppers", (D,),
           {"chicken_breast": 180, "broccoli": 150, "bell_pepper": 100, "rice": 80},
           {"soy_sauce": 15, "oil": 10, "garlic": 5}, "chicken_breast"),
    Recipe("chicken_pasta", "Chicken and broccoli pasta", (D,),
           {"chicken_breast": 150, "pasta": 100, "broccoli": 150, "cheese": 20},
           {"olive_oil": 10, "garlic": 5}, "chicken_breast"),
    Recipe("beef_chilli", "Beef chilli with rice", (D,),
           {"minced_beef": 150, "passata": 200, "bell_pepper": 100, "chickpeas": 100, "rice": 75},
           {"onion": 80, "spices": 4, "oil": 5}, "minced_beef"),
    Recipe("bolognese", "Spaghetti bolognese", (D,),
           {"minced_beef": 150, "pasta": 100, "passata": 200, "carrots": 80},
           {"onion": 80, "garlic": 5, "dried_herbs": 2, "olive_oil": 5}, "minced_beef"),
    Recipe("salmon_potatoes", "Salmon with potatoes and broccoli", (D,),
           {"salmon": 150, "potatoes": 300, "broccoli": 150}, {"butter": 10, "salt": 1}, "salmon"),
    Recipe("tofu_stir_fry", "Tofu vegetable stir fry", (D,),
           {"tofu": 200, "broccoli": 100, "bell_pepper": 100, "zucchini": 100, "rice": 80},
           {"soy_sauce": 15, "oil": 10, "garlic": 5}, "tofu"),
    Recipe("chicken_traybake", "Chicken traybake with potatoes and peppers", (D,),
           {"chicken_breast": 180, "potatoes": 300, "bell_pepper": 120, "zucchini": 100},
           {"olive_oil": 15, "dried_herbs": 2}, "chicken_breast"),
    Recipe("shakshuka", "Shakshuka with spinach and bread", (D,),
           {"eggs": 180, "passata": 250, "bell_pepper": 100, "spinach": 50, "bread": 80},
           {"onion": 60, "spices": 3, "olive_oil": 5}, "eggs"),
    Recipe("chickpea_curry", "Chickpea and spinach curry with rice", (D,),
           {"chickpeas": 200, "passata": 200, "spinach": 100, "rice": 80},
           {"onion": 80, "garlic": 5, "spices": 5, "oil": 10}, "chickpeas"),
]}

DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
MEALS = (B, L, D)
