"""Looks up a Nook product by ID from a fixed in-memory catalog."""

from system_card.tools.nook_product_lookup.types import ProductInfo, ProductNotFoundError

_CATALOG: dict[str, ProductInfo] = {
    "nook-100": ProductInfo(
        product_id="nook-100", name="Nook Reader Lite", price_usd=89.99, in_stock=True
    ),
    "nook-200": ProductInfo(
        product_id="nook-200", name="Nook Reader Plus", price_usd=149.99, in_stock=True
    ),
    "nook-300": ProductInfo(
        product_id="nook-300", name="Nook Reader Pro", price_usd=249.99, in_stock=False
    ),
}


def nook_product_lookup(product_id: str) -> ProductInfo:
    """Looks up a Nook product's name, price, and stock status by ID.

    Args:
        product_id: The product's identifier, e.g. "nook-100".

    Returns:
        The matching product's catalog entry.

    Raises:
        ProductNotFoundError: If no product matches product_id.
    """
    product = _CATALOG.get(product_id)
    if product is None:
        raise ProductNotFoundError(f"No product found for ID '{product_id}'.")

    return product
