from pydantic import BaseModel
from typing import List, Optional

class OLXItem(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    price: Optional[dict] = None
    images: List[dict] = []
    url: str
    created_at: str

class OLXResponse(BaseModel):
    data: List[OLXItem]
    metadata: dict
