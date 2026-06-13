from typing import List, Optional


def recommend_products(products: List[dict], category: Optional[str] = None, budget: Optional[float] = None, limit: int = 3) -> List[dict]:
    if not products:
        return []

    category_normalized = str(category).strip().lower() if category else ""
    eligible = []
    for p in products:
        prod_category = str(p.get("category", "")).strip().lower()
        if category_normalized and prod_category != category_normalized:
            continue

        if budget is not None:
            price_value = p.get("price_value")
            try:
                price = float(price_value or 0.0)
            except Exception:
                continue
            if price > budget:
                continue

        eligible.append(p)

    if not eligible:
        return []

    ranked = sorted(
        eligible,
        key=lambda p: (
            -(float(p.get("rating") or 0.0)),
            -(int(p.get("reviewCount") or 0)),
        ),
    )

    return ranked[:limit]
