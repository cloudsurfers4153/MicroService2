from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class MoviePersonBase(BaseModel):
    """Base model for MoviePerson relationship."""
    movie_id: int = Field(
        ...,
        description="ID of the movie",
        json_schema_extra={"example": 1},
    )
    person_id: int = Field(
        ...,
        description="ID of the person",
        json_schema_extra={"example": 1},
    )
    role_type: str = Field(
        ...,
        description="Role type (actor, director)",
        json_schema_extra={"example": "actor"},
    )
    character_name: Optional[str] = Field(
        None,
        description="Character name (for actors)",
        json_schema_extra={"example": "Dom Cobb"},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "movie_id": 1,
                    "person_id": 1,
                    "role_type": "actor",
                    "character_name": "Dom Cobb",
                }
            ]
        }
    }


class MoviePersonCreate(MoviePersonBase):
    """Creation payload for MoviePerson relationship."""
    pass


class MoviePersonRead(MoviePersonBase):
    """Complete MoviePerson data for reading."""
    pass

