from pydantic import BaseModel, Field
from uuid import UUID, uuid4

class Person(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    first_name: str
    last_name: str
    role: str = Field(description="Person's role, e.g., Actor or Director")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "first_name": "Christopher",
                "last_name": "Nolan",
                "role": "Director"
            }
        }