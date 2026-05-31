from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime
import re

class PriceInfo(BaseModel):
    value: float
    currency: str = "INR"
    display: str

class Product(BaseModel):
    """Rich internal product representation for OLX v4."""
    id: str
    external_id: str
    title: str
    description: Optional[str] = None
    price: PriceInfo
    location: str
    city: str
    state: str
    url: str
    image_url: Optional[str] = None
    all_images: List[str] = []
    created_at: datetime
    
    # Minor Details / Metadata
    seller_name: Optional[str] = None
    user_type: Optional[str] = None
    is_verified_user: bool = False
    parameters: Dict[str, str] = {}
    status_display: Optional[str] = None
    favorite_count: int = 0
    
    @property
    def brand(self) -> str:
        return self.parameters.get("make", "Generic")

    @property
    def is_new(self) -> bool:
        from datetime import datetime, timezone
        # Use timezone-aware comparison for accuracy
        now = datetime.now(timezone.utc)
        created = self.created_at
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        delta = now - created
        return delta.total_seconds() < 1800  # 30 minutes

    @classmethod
    def from_olx_json(cls, data: dict) -> "Product":
        item_id = str(data.get("id", "0"))
        
        # Price
        price_node = data.get("price", {}).get("value", {})
        price = PriceInfo(
            value=float(price_node.get("raw", 0)),
            display=price_node.get("display", "N/A")
        )

        # Location
        loc_res = data.get("locations_resolved", {})
        location = loc_res.get("SUBLOCALITY_LEVEL_1_name", "Unknown")
        city = loc_res.get("ADMIN_LEVEL_3_name", "Unknown")
        state = loc_res.get("ADMIN_LEVEL_1_name", "Unknown")

        # URL
        title = data.get("title", "No Title")
        slug = re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
        url = f"https://www.olx.in/item/{slug}-iid-{item_id}"

        # Images
        images = data.get("images", [])
        all_images = [img.get("full", {}).get("url") or img.get("url") for img in images if img]
        image_url = all_images[0] if all_images else None

        # Parameters (Minor details)
        params = {p.get("key"): p.get("formatted_value") for p in data.get("parameters", []) if p.get("key")}

        return cls(
            id=item_id,
            external_id=item_id,
            title=title,
            description=data.get("description"),
            price=price,
            location=location,
            city=city,
            state=state,
            url=url,
            image_url=image_url,
            all_images=all_images,
            created_at=datetime.fromisoformat(data.get("created_at", datetime.utcnow().isoformat()).replace("Z", "+00:00")),
            seller_name=data.get("user_name"),
            user_type=data.get("user_type"),
            is_verified_user=data.get("is_kyc_verified_user", False),
            parameters=params,
            status_display=data.get("status", {}).get("display"),
            favorite_count=data.get("favorites", {}).get("count", 0)
        )
