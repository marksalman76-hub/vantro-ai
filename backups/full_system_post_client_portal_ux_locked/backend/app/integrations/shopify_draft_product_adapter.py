"""
Shopify Draft Product Adapter

Prepares safe Shopify draft product payloads.
This adapter does not publish live products by default.
Publishing live products should require owner/client approval.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class ShopifyDraftProductRequest:
    tenant_id: str
    product_title: str
    product_description_html: str
    product_type: str
    vendor: str
    price: str
    currency: str
    seo_title: str
    seo_description: str
    tags: List[str] = field(default_factory=list)
    image_urls: List[str] = field(default_factory=list)
    publish_live: bool = False
    owner_approved: bool = False


@dataclass
class ShopifyDraftProductResult:
    success: bool
    status: str
    provider_ready: bool
    publish_live: bool
    message: str
    shopify_payload: Optional[Dict[str, object]] = None
    blocked_reason: Optional[str] = None


class ShopifyDraftProductAdapter:
    def prepare_product_payload(
        self,
        request: ShopifyDraftProductRequest,
    ) -> ShopifyDraftProductResult:
        if request.publish_live and not request.owner_approved:
            return ShopifyDraftProductResult(
                success=False,
                status="blocked_pending_owner_approval",
                provider_ready=False,
                publish_live=request.publish_live,
                message="Publishing live products requires owner/client approval.",
                blocked_reason="publish_live_requested_without_approval",
            )

        shopify_payload: Dict[str, object] = {
            "product": {
                "title": request.product_title,
                "body_html": request.product_description_html,
                "product_type": request.product_type,
                "vendor": request.vendor,
                "status": "draft" if not request.publish_live else "active",
                "tags": request.tags,
                "variants": [
                    {
                        "price": request.price,
                        "sku": self._build_sku(request),
                    }
                ],
                "images": [{"src": url} for url in request.image_urls],
                "metafields": [
                    {
                        "namespace": "seo",
                        "key": "title_tag",
                        "value": request.seo_title,
                        "type": "single_line_text_field",
                    },
                    {
                        "namespace": "seo",
                        "key": "description_tag",
                        "value": request.seo_description,
                        "type": "multi_line_text_field",
                    },
                    {
                        "namespace": "platform",
                        "key": "tenant_id",
                        "value": request.tenant_id,
                        "type": "single_line_text_field",
                    },
                    {
                        "namespace": "platform",
                        "key": "currency",
                        "value": request.currency,
                        "type": "single_line_text_field",
                    },
                ],
            }
        }

        return ShopifyDraftProductResult(
            success=True,
            status="shopify_draft_payload_prepared",
            provider_ready=False,
            publish_live=request.publish_live,
            message="Shopify product payload prepared safely. External Shopify API call not enabled yet.",
            shopify_payload=shopify_payload,
        )

    def _build_sku(self, request: ShopifyDraftProductRequest) -> str:
        safe_title = "".join(
            char for char in request.product_title.upper().replace(" ", "-")
            if char.isalnum() or char == "-"
        )
        return f"{request.tenant_id.upper()}-{safe_title[:24]}"


def shopify_draft_product_summary(result: ShopifyDraftProductResult) -> Dict[str, object]:
    return {
        "success": result.success,
        "status": result.status,
        "provider_ready": result.provider_ready,
        "publish_live": result.publish_live,
        "message": result.message,
        "blocked_reason": result.blocked_reason,
        "shopify_payload": result.shopify_payload,
    }