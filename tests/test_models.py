import pytest
from datetime import datetime, timezone
from src.models.olx import Product

@pytest.fixture
def raw_olx_item():
    return {
        "id": "12345",
        "title": "iPhone 15 Pro Max",
        "description": "Mint condition iPhone",
        "price": {
            "value": {
                "raw": 95000,
                "display": "₹ 95,000",
                "currency": {"iso_4217": "INR"}
            }
        },
        "locations_resolved": {
            "SUBLOCALITY_LEVEL_1_name": "Downtown",
            "ADMIN_LEVEL_3_name": "Mumbai",
            "ADMIN_LEVEL_1_name": "Maharashtra"
        },
        "images": [
            {
                "url": "http://example.com/img.jpg", 
                "full": {"url": "http://example.com/full.jpg"}
            }
        ],
        "created_at": "2026-05-30T10:00:00Z",
        "user_name": "John Doe",
        "is_kyc_verified_user": True,
        "parameters": [
            {"key": "make", "formatted_value": "Apple"},
            {"key": "model", "formatted_value": "15 Pro Max"}
        ],
        "favorites": {"count": 10},
        "status": {"display": "active"}
    }

def test_product_normalization(raw_olx_item):
    product = Product.from_olx_json(raw_olx_item)
    
    assert product.id == "12345"
    assert product.title == "iPhone 15 Pro Max"
    assert product.price.value == 95000.0
    assert product.price.display == "₹ 95,000"
    assert product.location == "Downtown"
    assert product.city == "Mumbai"
    assert product.state == "Maharashtra"
    assert product.seller_name == "John Doe"
    assert product.is_verified_user is True
    assert product.brand == "Apple"
    assert product.image_url == "http://example.com/full.jpg"
    assert "iphone-15-pro-max" in product.url
    assert product.favorite_count == 10

def test_product_is_new(raw_olx_item):
    product = Product.from_olx_json(raw_olx_item)
    # Set created_at to now
    product.created_at = datetime.now(timezone.utc)
    assert product.is_new is True
    
    # Set created_at to 2 hours ago
    from datetime import timedelta
    product.created_at = datetime.now(timezone.utc) - timedelta(hours=2)
    assert product.is_new is False

def test_safe_normalization_defaults():
    empty_data = {"id": "999"}
    product = Product.from_olx_json(empty_data)
    
    assert product.title == "No Title"
    assert product.price.display == "N/A"
    assert product.location == "Unknown"
    assert product.city == "Unknown"
    assert product.state == "Unknown"
    assert product.brand == "Generic"
