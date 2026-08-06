from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass
class ProductFilterDto:
    search_term: Optional[str] = None
    category_ids: Optional[list[int]] = None
    min_price: Optional[Decimal] = None
    max_price: Optional[Decimal] = None
    seller_id: Optional[int] = None
    min_rating: Optional[Decimal] = None
    sort_by: Optional[str] = None
    colors: Optional[list[str]] = None
    sizes: Optional[list[str]] = None
    in_stock_only: Optional[bool] = False
    discounted_only: Optional[bool] = False

