"""Pagination utilities for collection endpoints."""

from typing import List, Dict, Any, Optional, TypeVar, Generic
from pydantic import BaseModel, Field
from math import ceil


T = TypeVar('T')


class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T] = Field(
        ...,
        description="List of items in the current page"
    )
    page: int = Field(
        ...,
        description="Current page number",
        json_schema_extra={"example": 1}
    )
    page_size: int = Field(
        ...,
        description="Number of items per page",
        json_schema_extra={"example": 20}
    )
    total_items: int = Field(
        ...,
        description="Total number of items across all pages",
        json_schema_extra={"example": 100}
    )
    total_pages: int = Field(
        ...,
        description="Total number of pages",
        json_schema_extra={"example": 5}
    )
    links: Dict[str, str] = Field(
        default_factory=dict,
        description="HATEOAS navigation links",
        serialization_alias="_links",
        json_schema_extra={
            "example": {
                "self": "/movies?page=1&page_size=20",
                "next": "/movies?page=2&page_size=20"
            }
        }
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "items": [],
                    "page": 1,
                    "page_size": 20,
                    "total_items": 100,
                    "total_pages": 5,
                    "_links": {
                        "self": "/movies?page=1&page_size=20",
                        "next": "/movies?page=2&page_size=20"
                    }
                }
            ]
        }
    }


def paginate(
    items: List[Any],
    page: int,
    page_size: int,
    base_url: str,
    query_params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    
    if query_params is None:
        query_params = {}
    
    page = max(1, page)
    page_size = max(1, min(page_size, 100))  # Max 100 items per page
    
    total_items = len(items)
    total_pages = ceil(total_items / page_size) if total_items > 0 else 1
    
    page = min(page, total_pages)
    
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_items = items[start_idx:end_idx]
    
    def build_query_string(p: int) -> str:
        params = query_params.copy()
        params['page'] = p
        params['page_size'] = page_size
        
        query_parts = []
        for key, value in params.items():
            if value is not None:
                query_parts.append(f"{key}={value}")
        
        if query_parts:
            return f"{base_url}?{'&'.join(query_parts)}"
        return f"{base_url}?page={p}&page_size={page_size}"
    
    links = {
        "self": build_query_string(page)
    }
    
    if page > 1:
        links["prev"] = build_query_string(page - 1)
        links["first"] = build_query_string(1)
    
    if page < total_pages:
        links["next"] = build_query_string(page + 1)
        links["last"] = build_query_string(total_pages)
    
    return {
        "items": paginated_items,
        "page": page,
        "page_size": page_size,
        "total_items": total_items,
        "total_pages": total_pages,
        "_links": links
    }

