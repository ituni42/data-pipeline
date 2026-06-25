VARIANTS    = ["compact", "basic", "comfort", "premium"]
DEDUCTIBLES = [100, 200, 500]

DEDUCTIBLE_FACTOR = {100: 1.00, 200: 0.90, 500: 0.80}  # -10% per step (100€ is base)
VARIANT_STEP      = 1.07                                 # each variant costs about 7% more than the previous

#simple help fuction for updating prices and reports inconsistencies
#takes current price, new price, key and reason why fix is applied
def _fix(prices: dict, key: str, new_price: float, reason: str) -> None:
    old = prices[key]
    new = round(new_price)
    print(f"{key}: €{old} → €{new} ({'raised' if new > old else 'lowered'}) {reason}")
    prices[key] = new

#for each neighboring pair (prev, current), current must be cheaper than prev.
#if not, fix using the 100€ base using 10%
def _check_deductibles(prices: dict) -> None:
    for product in ("limited_casco", "casco"):
        for variant in VARIANTS:
            base = prices[f"{product}_{variant}_100"]
            for deductible, prev_deductible in zip(DEDUCTIBLES[1:], DEDUCTIBLES):
                k      = f"{product}_{variant}_{deductible}"
                prev_k = f"{product}_{variant}_{prev_deductible}"
                if prices[k] >= prices[prev_k]:
                    _fix(prices, k, base * DEDUCTIBLE_FACTOR[deductible],
                         f"deductible {deductible}€ must be cheaper than {prev_deductible}€ "
                         f"(spec: -{round((1 - DEDUCTIBLE_FACTOR[deductible]) * 100)}% from 100€ base)")


# each variant (comfort, premium) must be more expensive than the previous.
# if not, fix by applying 7% step on top of the previous variant price.
def _check_variants(prices: dict) -> None:
    for product in ("limited_casco", "casco"):
        for deductible in DEDUCTIBLES:
            for variant, prev in (("comfort", "basic"), ("premium", "comfort")):
                k      = f"{product}_{variant}_{deductible}"
                prev_k = f"{product}_{prev}_{deductible}"
                if prices[k] <= prices[prev_k]:
                    _fix(prices, k, prices[prev_k] * VARIANT_STEP,
                         f"{variant} must be above {prev} (spec: +7% per variants)")


#Since spec didn't provide difference between products, we make minimal changes to satisfy given rules
#I thought of making sure there is some % gap between different products, 
# but went with this instead for simplicity, since nothing is mentioned, should be easy to update if needed
#I believe from business perpsective, we'd definetly need some info, 
#increasing/decreasing price based on percentages of previous ones sounds like a bad idea. Too many outside variables that are being ignored.
#hence this script best use case would be only reporting the errors specification mentioned, not applying changes by it's own, but for the given task we do it minimally.


#(mtpl < limited casco < casco must hold for every variant/deductible)
def _check_product_levels(prices: dict) -> None:
    mtpl = prices.get("mtpl", 0)
    for variant in VARIANTS:
        for deductible in DEDUCTIBLES:
            lc_key    = f"limited_casco_{variant}_{deductible}"
            casco_key = f"casco_{variant}_{deductible}"
            #if mtpl is bigger than limited_casco, increase limited_casco (+1)
            if mtpl >= prices[lc_key]:
                _fix(prices, lc_key, mtpl + 1, f"MTPL (€{mtpl}) must be cheaper than Limited Casco")
            #if limited casco > casco, increase casco price to satisfy the rule (+1)
            if prices[lc_key] >= prices[casco_key]:
                _fix(prices, casco_key, prices[lc_key] + 1, f"Casco must be more expensive than Limited Casco (€{prices[lc_key]})")


def validate_and_fix(prices: dict[str, float]) -> dict[str, float]:
    
    result = prices.copy() #work with the copy, not original
    
    _check_product_levels(result) # MTPL < limited casco < casco
    _check_variants(result) # compact/basic < comfort < premium
    _check_deductibles(result) # 100€ < 200€ < 500€
    return result

#example given in specification
example_prices_to_correct = {
"mtpl": 400,
"limited_casco_compact_100": 820,
"limited_casco_compact_200": 760,
"limited_casco_compact_500": 650,
"limited_casco_basic_100": 900,
"limited_casco_basic_200": 780,
"limited_casco_basic_500": 600,
"limited_casco_comfort_100": 950,
"limited_casco_comfort_200": 870,
"limited_casco_comfort_500": 720,
"limited_casco_premium_100": 1100,
"limited_casco_premium_200": 980,
"limited_casco_premium_500": 800,
"casco_compact_100": 750,
"casco_compact_200": 700,
"casco_compact_500": 620,
"casco_basic_100": 830,
"casco_basic_200": 760,
"casco_basic_500": 650,
"casco_comfort_100": 900,
"casco_comfort_200": 820,
"casco_comfort_500": 720,
"casco_premium_100": 1050,
"casco_premium_200": 950,
"casco_premium_500": 780
}

if __name__ == "__main__":
    corrected = validate_and_fix(example_prices_to_correct)

    print("\nFinal prices:")
    for key, price in corrected.items():
        print(f"{key}: €{price}")