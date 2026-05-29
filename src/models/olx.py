from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional
from datetime import datetime

class PriceInfo(BaseModel):
    value: float
    currency: str = "INR"
    display: str

class Product(BaseModel):
    """Normalized internal product representation."""
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
        """Factory method to convert raw OLX v4 JSON to Product."""
        # Note: OLX v4 structure usually has price in 'price' -> 'value' -> 'display'
        price_data = data.get("price", {})
        display_price = price_data.get("value", {}).get("display", "N/A")
        raw_value = price_data.get("value", {}).get("raw", 0)
        
        # Location is often in 'locations' list or 'location_str'
        location = data.get("location_str", "Unknown")
        
        # Construct URL (usually https://www.olx.in/item/TITLE-iid-ID)
        # For now, we'll use a placeholder or the provided URL if available
        item_id = str(data.get("id"))
        slug = data.get("title", "").lower().replace(" ", "-")
        url = f"https://www.olx.in/item/{slug}-iid-{item_id}"
        
        # First image
        images = data.get("images", [])
        image_url = images[0].get("url") if images else None

        return cls(
            id=item_id,
            external_id=item_id,
            title=data.get("title", "No Title"),
            description=data.get("description"),
            price=PriceInfo(
                value=float(raw_value),
                display=display_price
            ),
            location=location,
            url=url,
            image_url=image_url,
            created_at=datetime.fromisoformat(data.get("created_at").replace("Z", "+00:00"))
        )
