from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional
from datetime import datetime
import re

class PriceInfo(BaseModel):
    value: float
    currency: str = "INR"
    display: str

class Product(BaseModel):
    """Normalized internal product representation for OLX v4."""
    id: str
    external_id: str
    title: str
    description: Optional[str] = None
    price: PriceInfo
    location: str
    url: str
    image_url: Optional[str] = None
    created_at: datetime
    first_seen: datetime = Field(default_factory=datetime.utcnow)

    @classmethod
    def from_olx_json(cls, data: dict) -> "Product":
        """
        Robustly converts raw OLX v4 JSON to a Normalized Product.
        Uses safe defaults for missing or unexpected fields.
        """
        item_id = str(data.get("id", "0"))
        
        # Price extraction (Safe Path)
        price_node = data.get("price", {}).get("value", {})
        price = PriceInfo(
            value=float(price_node.get("raw", 0)),
            currency=price_node.get("currency", {}).get("iso_4217", "INR"),
            display=price_node.get("display", "N/A")
        )

        # Location extraction (Building readable string)
        loc_res = data.get("locations_resolved", {})
        parts = [
            loc_res.get("SUBLOCALITY_LEVEL_1_name"),
            loc_res.get("ADMIN_LEVEL_3_name"),
            loc_res.get("ADMIN_LEVEL_1_name")
        ]
        location = ", ".join([p for p in parts if p]) or "Unknown Location"

        # URL Reconstruction: https://www.olx.in/item/[title-slug]-iid-[id]
        title = data.get("title", "No Title")
        slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
        url = f"https://www.olx.in/item/{slug}-iid-{item_id}"

        # Image extraction (Prefer 'big' size for Telegram)
        images = data.get("images", [])
        image_url = None
        if images:
            # Try to get 'big' first, then 'url' (default)
            image_url = images[0].get("big", {}).get("url") or images[0].get("url")

        # Date handling
        created_at_str = data.get("created_at", datetime.utcnow().isoformat())
        try:
            # Handle OLX ISO format with offsets
            created_at = datetime.fromisoformat(created_at_str.replace("Z", "+00:00"))
        except ValueError:
            created_at = datetime.utcnow()

        return cls(
            id=item_id,
            external_id=item_id,
            title=title,
            description=data.get("description"),
            price=price,
            location=location,
            url=url,
            image_url=image_url,
            created_at=created_at
        )
