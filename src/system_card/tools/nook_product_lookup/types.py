"""Types for the nook_product_lookup tool."""

from pydantic import BaseModel


class ProductNotFoundError(Exception):
    """Raised when no product matches the given product ID."""


class ProductInfo(BaseModel):
    """A single Nook product's catalog entry.

    Attributes:
        product_id: The product's identifier.
        name: The product's display name.
        price_usd: The product's price in US dollars.
        in_stock: Whether the product currently has stock available.
    """

    product_id: str
    name: str
    price_usd: float
    in_stock: bool
