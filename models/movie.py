from __future__ import annotations

from typing import Optional, Dict
from datetime import datetime
from pydantic import BaseModel, Field


class MovieBase(BaseModel):
    """Base model for Movie with core fields."""
    id: int = Field(
        ...,
        description="Unique movie identifier",
        json_schema_extra={"example": 1},
    )
    title: str = Field(
        ...,
        description="Title of the movie",
        json_schema_extra={"example": "Inception"},
    )
    genre: str = Field(
        ...,
        description="Genre of the movie",
        json_schema_extra={"example": "Sci-Fi"},
    )
    year: int = Field(
        ...,
        description="Release year",
        json_schema_extra={"example": 2010},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "title": "Inception",
                    "genre": "Sci-Fi",
                    "year": 2010,
                }
            ]
        }
    }


class MovieCreate(BaseModel):
    """Creation payload for a Movie (no id - auto-generated)."""
    title: str = Field(
        ...,
        description="Title of the movie",
        json_schema_extra={"example": "The Matrix"},
    )
    genre: str = Field(
        ...,
        description="Genre of the movie",
        json_schema_extra={"example": "Action"},
    )
    year: int = Field(
        ...,
        description="Release year",
        json_schema_extra={"example": 1999},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "The Matrix",
                    "genre": "Action",
                    "year": 1999,
                }
            ]
        }
    }


class MovieUpdate(BaseModel):
    """Partial update for a Movie; supply only fields to change."""
    title: Optional[str] = Field(
        None,
        description="Updated title of the movie",
        json_schema_extra={"example": "Inception: Director's Cut"},
    )
    genre: Optional[str] = Field(
        None,
        description="Updated genre of the movie",
        json_schema_extra={"example": "Thriller"},
    )
    year: Optional[int] = Field(
        None,
        description="Updated release year",
        json_schema_extra={"example": 2011},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "Updated Title"
                },
                {
                    "genre": "Drama",
                    "year": 2015
                }
            ]
        }
    }


class MovieRead(MovieBase):
    """Complete movie data for reading/displaying."""
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
    version: str = Field(
        ...,
        description="Version hash for ETag support",
        json_schema_extra={"example": "b12e3c84"},
    )
    processing_status: str = Field(
        ...,
        description="Processing status (PENDING, COMPLETED, FAILED)",
        json_schema_extra={"example": "COMPLETED"},
    )
    links: Dict[str, str] = Field(
        default_factory=dict,
        description="HATEOAS links for navigation",
        serialization_alias="_links",
        json_schema_extra={"example": {"self": "/movies/1", "cast": "/movies/1/people"}},
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "title": "Inception",
                    "genre": "Sci-Fi",
                    "year": 2010,
                    "created_at": "2025-11-21T02:06:47.584989+00:00",
                    "updated_at": "2025-11-21T02:06:47.584989+00:00",
                    "version": "b12e3c84",
                    "processing_status": "COMPLETED",
                    "_links": {
                        "self": "/movies/1",
                        "cast": "/movies/1/people"
                    }
                }
            ]
        }
    }
