from fastapi import FastAPI, HTTPException
from models.person import Person
from models.movie import Movie
from typing import List
from uuid import UUID

app = FastAPI(
    title="Movie/Person API",
    description="Microservice 2 — handles people and movies (placeholder version)",
    version="0.1.0"
)

# -----------------------------------------------------------------------------
# Person endpoints
# -----------------------------------------------------------------------------

@app.get("/persons")
def list_persons():
    raise HTTPException(status_code=501, detail="Not implemented")

@app.post("/persons")
def create_person():
    raise HTTPException(status_code=501, detail="Not implemented")

@app.put("/persons/{person_id}")
def update_person(person_id: str):
    raise HTTPException(status_code=501, detail="Not implemented")

@app.delete("/persons/{person_id}")
def delete_person(person_id: str):
    raise HTTPException(status_code=501, detail="Not implemented")

# -----------------------------------------------------------------------------
# Movie endpoints
# -----------------------------------------------------------------------------

@app.get("/movies")
def list_movies():
    raise HTTPException(status_code=501, detail="Not implemented")

@app.post("/movies")
def create_movie():
    raise HTTPException(status_code=501, detail="Not implemented")

@app.put("/movies/{movie_id}")
def update_movie(movie_id: str):
    raise HTTPException(status_code=501, detail="Not implemented")

@app.delete("/movies/{movie_id}")
def delete_movie(movie_id: str):
    raise HTTPException(status_code=501, detail="Not implemented")

# -----------------------------------------------------------------------------
# Root
# -----------------------------------------------------------------------------

@app.get("/")
def root():
    return {"message": "Welcome to Microservice 2 — Movie/Person API placeholder"}