from pydantic import BaseModel, Field
from uuid import UUID, uuid4
from typing import Optional

class Movie(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    title: str
    year: Optional[int] = Field(None, description="Release year")
    genre: Optional[str] = Field(None, description="Genre of movie eg. Drama, Action, etc")
    director: Optional[str] = Field(None, description="Movie director")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "b1234567-b89c-12d3-a456-426614174000",
                "title": "Inception",
                "year": 2010,
                "genre": "Science Fiction",
                "director": "Christopher Nolan"
            }
        }