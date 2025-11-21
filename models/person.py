from __future__ import annotations

from typing import Optional, Dict
from datetime import datetime
from pydantic import BaseModel, Field


class PersonBase(BaseModel):
    """Base model for Person with core fields."""
    id: int = Field(
        ...,
        description="Unique person identifier",
        json_schema_extra={"example": 1},
    )
    name: str = Field(
        ...,
        description="Full name of the person",
        json_schema_extra={"example": "Christopher Nolan"},
    )
    role: str = Field(
        ...,
        description="Role (e.g., Actor, Director)",
        json_schema_extra={"example": "Director"},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "name": "Christopher Nolan",
                    "role": "Director",
                }
            ]
        }
    }


class PersonCreate(BaseModel):
    """Creation payload for a Person (no id - auto-generated)."""
    name: str = Field(
        ...,
        description="Full name of the person",
        json_schema_extra={"example": "Leonardo DiCaprio"},
    )
    role: str = Field(
        ...,
        description="Role (e.g., Actor, Director)",
        json_schema_extra={"example": "Actor"},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Leonardo DiCaprio",
                    "role": "Actor",
                }
            ]
        }
    }


class PersonUpdate(BaseModel):
    """Partial update for a Person; supply only fields to change."""
    name: Optional[str] = Field(
        None,
        description="Updated full name",
        json_schema_extra={"example": "Christopher J. Nolan"},
    )
    role: Optional[str] = Field(
        None,
        description="Updated role",
        json_schema_extra={"example": "Actor, Director"},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "Updated Name"
                },
                {
                    "role": "Actor, Director"
                }
            ]
        }
    }


class PersonRead(PersonBase):
    """Complete person data for reading/displaying."""
    created_at: datetime = Field(
        ...,
        description="Creation timestamp (UTC).",
        json_schema_extra={"example": "2025-11-21T02:06:47.584989+00:00"},
    )
    updated_at: datetime = Field(
        ...,
        description="Last update timestamp (UTC).",
        json_schema_extra={"example": "2025-11-21T02:06:47.584989+00:00"},
    )
    links: Dict[str, str] = Field(
        default_factory=dict,
        description="HATEOAS links for navigation",
        serialization_alias="_links",
        json_schema_extra={"example": {"self": "/people/1", "movies": "/people/1/movies"}},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "name": "Christopher Nolan",
                    "role": "Director",
                    "created_at": "2025-11-21T02:06:47.584989+00:00",
                    "updated_at": "2025-11-21T02:06:47.584989+00:00",
                    "_links": {
                        "self": "/people/1",
                        "movies": "/people/1/movies"
                    }
                }
            ]
        }
    }
