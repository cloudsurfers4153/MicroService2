from fastapi import FastAPI, HTTPException, Response, Request, status, Header
from fastapi.responses import JSONResponse
from typing import List, Optional
from datetime import datetime
import hashlib
import random
import string

from models.movie import MovieCreate, MovieUpdate, MovieRead
from models.person import PersonCreate, PersonUpdate, PersonRead
from utils.pagination import paginate


# -----------------------------------------------------------------------------
# In-Memory Data Stores
# -----------------------------------------------------------------------------

movies_db: dict[int, dict] = {}
people_db: dict[int, dict] = {}
movie_people_db: list[dict] = []

max_movie_id: int = 0
max_person_id: int = 0


# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------

def get_next_movie_id() -> int:
    """Get next available movie ID."""
    global max_movie_id
    max_movie_id += 1
    return max_movie_id


def get_next_person_id() -> int:
    """Get next available person ID."""
    global max_person_id
    max_person_id += 1
    return max_person_id


def generate_etag(movie: dict) -> str:
    """Generate ETag for a movie based on version and updated_at."""
    etag_string = f"{movie['version']}-{movie['updated_at'].isoformat()}"
    return hashlib.md5(etag_string.encode()).hexdigest()


def generate_version_hash() -> str:
    """Generate a random version hash (8 chars hex)."""
    return ''.join(random.choices(string.hexdigits.lower(), k=8))


def get_people_for_movie(movie_id: int) -> List[dict]:
    """Get all people associated with a movie."""
    people_list = []
    for relation in movie_people_db:
        if relation['movie_id'] == movie_id:
            person_id = relation['person_id']
            if person_id in people_db:
                person_data = people_db[person_id].copy()
                person_data['role_type'] = relation['role_type']
                person_data['character_name'] = relation['character_name']
                people_list.append(person_data)
    return people_list


def get_movies_for_person(person_id: int) -> List[dict]:
    """Get all movies associated with a person."""
    movies_list = []
    for relation in movie_people_db:
        if relation['person_id'] == person_id:
            movie_id = relation['movie_id']
            if movie_id in movies_db:
                movie_data = movies_db[movie_id].copy()
                movie_data['role_type'] = relation['role_type']
                movie_data['character_name'] = relation['character_name']
                movies_list.append(movie_data)
    return movies_list


# -----------------------------------------------------------------------------
# FastAPI Application
# -----------------------------------------------------------------------------

app = FastAPI(
    title="Movies & People API",
    description="Microservice 2 — Advanced REST API for movies and people with full CRUD, pagination, eTags, and linked data",
    version="0.0.1"
)


# -----------------------------------------------------------------------------
# Movie Endpoints
# -----------------------------------------------------------------------------

@app.get("/movies", response_model=dict)
def list_movies(
    title: Optional[str] = None,
    genre: Optional[str] = None,
    year: Optional[int] = None,
    year_min: Optional[int] = None,
    year_max: Optional[int] = None,
    sort: Optional[str] = "title",
    order: Optional[str] = "asc",
    page: int = 1,
    page_size: int = 20
):
    movies = list(movies_db.values())
    
    if title:
        movies = [m for m in movies if title.lower() in m['title'].lower()]
    
    if genre:
        movies = [m for m in movies if m['genre'].lower() == genre.lower()]
    
    if year:
        movies = [m for m in movies if m['year'] == year]
    
    if year_min:
        movies = [m for m in movies if m['year'] >= year_min]
    
    if year_max:
        movies = [m for m in movies if m['year'] <= year_max]
    
    reverse = (order.lower() == "desc")
    if sort == "year":
        movies.sort(key=lambda x: x['year'], reverse=reverse)
    else:
        movies.sort(key=lambda x: x['title'].lower(), reverse=reverse)
    
    movies_read = []
    for movie in movies:
        movie_read = MovieRead(
            id=movie['id'],
            title=movie['title'],
            genre=movie['genre'],
            year=movie['year'],
            created_at=movie['created_at'],
            updated_at=movie['updated_at'],
            version=movie['version'],
            processing_status=movie['processing_status'],
            links={
                "self": f"/movies/{movie['id']}",
                "cast": f"/movies/{movie['id']}/people"
            }
        )
        movies_read.append(movie_read.model_dump())
    
    query_params = {}
    if title:
        query_params['title'] = title
    if genre:
        query_params['genre'] = genre
    if year:
        query_params['year'] = year
    if year_min:
        query_params['year_min'] = year_min
    if year_max:
        query_params['year_max'] = year_max
    if sort != "title":
        query_params['sort'] = sort
    if order != "asc":
        query_params['order'] = order
    
    return paginate(movies_read, page, page_size, "/movies", query_params)


@app.post("/movies", response_model=MovieRead, status_code=status.HTTP_201_CREATED)
def create_movie(movie: MovieCreate, response: Response):
    movie_id = get_next_movie_id()
    now = datetime.utcnow()
    version = generate_version_hash()
    
    new_movie = {
        'id': movie_id,
        'title': movie.title,
        'genre': movie.genre,
        'year': movie.year,
        'created_at': now,
        'updated_at': now,
        'version': version,
        'processing_status': 'COMPLETED'
    }
    
    movies_db[movie_id] = new_movie
    
    response.headers["Location"] = f"/movies/{movie_id}"
    
    return MovieRead(
        id=new_movie['id'],
        title=new_movie['title'],
        genre=new_movie['genre'],
        year=new_movie['year'],
        created_at=new_movie['created_at'],
        updated_at=new_movie['updated_at'],
        version=new_movie['version'],
        processing_status=new_movie['processing_status'],
        links={
            "self": f"/movies/{movie_id}",
            "cast": f"/movies/{movie_id}/people"
        }
    )


@app.get("/movies/{movie_id}", response_model=MovieRead)
def get_movie(
    movie_id: int,
    response: Response,
    if_none_match: Optional[str] = Header(None)
):
    if movie_id not in movies_db:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    movie = movies_db[movie_id]
    
    etag = generate_etag(movie)
    
    if if_none_match and if_none_match.strip('"') == etag:
        return Response(status_code=status.HTTP_304_NOT_MODIFIED)
    
    response.headers["ETag"] = f'"{etag}"'
    
    return MovieRead(
        id=movie['id'],
        title=movie['title'],
        genre=movie['genre'],
        year=movie['year'],
        created_at=movie['created_at'],
        updated_at=movie['updated_at'],
        version=movie['version'],
        processing_status=movie['processing_status'],
        links={
            "self": f"/movies/{movie_id}",
            "cast": f"/movies/{movie_id}/people"
        }
    )


@app.put("/movies/{movie_id}", response_model=MovieRead)
def update_movie(movie_id: int, movie_update: MovieUpdate):
    if movie_id not in movies_db:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    movie = movies_db[movie_id]
    
    if movie_update.title is not None:
        movie['title'] = movie_update.title
    
    if movie_update.genre is not None:
        movie['genre'] = movie_update.genre
    
    if movie_update.year is not None:
        movie['year'] = movie_update.year
    
    movie['updated_at'] = datetime.utcnow()
    movie['version'] = generate_version_hash()
    
    return MovieRead(
        id=movie['id'],
        title=movie['title'],
        genre=movie['genre'],
        year=movie['year'],
        created_at=movie['created_at'],
        updated_at=movie['updated_at'],
        version=movie['version'],
        processing_status=movie['processing_status'],
        links={
            "self": f"/movies/{movie_id}",
            "cast": f"/movies/{movie_id}/people"
        }
    )


@app.delete("/movies/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movie(movie_id: int):
    if movie_id not in movies_db:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    del movies_db[movie_id]
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/movies/{movie_id}/people", response_model=List[dict])
def get_movie_people(movie_id: int):
    if movie_id not in movies_db:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    people = get_people_for_movie(movie_id)
    
    result = []
    for person in people:
        person_data = {
            "id": person['id'],
            "name": person['name'],
            "role": person['role'],
            "role_type": person['role_type'],
            "character_name": person.get('character_name'),
            "created_at": person['created_at'].isoformat(),
            "updated_at": person['updated_at'].isoformat(),
            "_links": {
                "self": f"/people/{person['id']}",
                "movies": f"/people/{person['id']}/movies"
            }
        }
        result.append(person_data)
    
    return result


# -----------------------------------------------------------------------------
# People Endpoints
# -----------------------------------------------------------------------------

@app.get("/people", response_model=dict)
def list_people(
    name: Optional[str] = None,
    role: Optional[str] = None,
    movie_id: Optional[int] = None,
    page: int = 1,
    page_size: int = 20
):
    people = list(people_db.values())
    
    if movie_id is not None:
        if movie_id not in movies_db:
            raise HTTPException(status_code=404, detail="Movie not found")
        
        movie_people_ids = set()
        for relation in movie_people_db:
            if relation['movie_id'] == movie_id:
                movie_people_ids.add(relation['person_id'])
        
        people = [p for p in people if p['id'] in movie_people_ids]
    
    if name:
        people = [p for p in people if name.lower() in p['name'].lower()]
    
    if role:
        people = [p for p in people if role.lower() in p['role'].lower()]
    
    people.sort(key=lambda x: x['name'].lower())
    
    people_read = []
    for person in people:
        person_read = PersonRead(
            id=person['id'],
            name=person['name'],
            role=person['role'],
            created_at=person['created_at'],
            updated_at=person['updated_at'],
            links={
                "self": f"/people/{person['id']}",
                "movies": f"/people/{person['id']}/movies"
            }
        )
        people_read.append(person_read.model_dump())
    
    query_params = {}
    if name:
        query_params['name'] = name
    if role:
        query_params['role'] = role
    if movie_id:
        query_params['movie_id'] = movie_id
    
    return paginate(people_read, page, page_size, "/people", query_params)


@app.post("/people", response_model=PersonRead, status_code=status.HTTP_201_CREATED)
def create_person(person: PersonCreate, response: Response):
    person_id = get_next_person_id()
    now = datetime.utcnow()
    
    new_person = {
        'id': person_id,
        'name': person.name,
        'role': person.role,
        'created_at': now,
        'updated_at': now
    }
    
    people_db[person_id] = new_person
    
    response.headers["Location"] = f"/people/{person_id}"
    
    return PersonRead(
        id=new_person['id'],
        name=new_person['name'],
        role=new_person['role'],
        created_at=new_person['created_at'],
        updated_at=new_person['updated_at'],
        links={
            "self": f"/people/{person_id}",
            "movies": f"/people/{person_id}/movies"
        }
    )


@app.get("/people/{person_id}", response_model=PersonRead)
def get_person(person_id: int):
    if person_id not in people_db:
        raise HTTPException(status_code=404, detail="Person not found")
    
    person = people_db[person_id]
    
    return PersonRead(
        id=person['id'],
        name=person['name'],
        role=person['role'],
        created_at=person['created_at'],
        updated_at=person['updated_at'],
        links={
            "self": f"/people/{person_id}",
            "movies": f"/people/{person_id}/movies"
        }
    )


@app.put("/people/{person_id}", response_model=PersonRead)
def update_person(person_id: int, person_update: PersonUpdate):
    if person_id not in people_db:
        raise HTTPException(status_code=404, detail="Person not found")
    
    person = people_db[person_id]
    
    if person_update.name is not None:
        person['name'] = person_update.name
    
    if person_update.role is not None:
        person['role'] = person_update.role
    
    person['updated_at'] = datetime.utcnow()
    
    return PersonRead(
        id=person['id'],
        name=person['name'],
        role=person['role'],
        created_at=person['created_at'],
        updated_at=person['updated_at'],
        links={
            "self": f"/people/{person_id}",
            "movies": f"/people/{person_id}/movies"
        }
    )


@app.delete("/people/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_person(person_id: int):
    if person_id not in people_db:
        raise HTTPException(status_code=404, detail="Person not found")
    
    del people_db[person_id]
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/people/{person_id}/movies", response_model=List[dict])
def get_person_movies(person_id: int):
    if person_id not in people_db:
        raise HTTPException(status_code=404, detail="Person not found")
    
    movies = get_movies_for_person(person_id)
    
    result = []
    for movie in movies:
        movie_data = {
            "id": movie['id'],
            "title": movie['title'],
            "genre": movie['genre'],
            "year": movie['year'],
            "role_type": movie['role_type'],
            "character_name": movie.get('character_name'),
            "created_at": movie['created_at'].isoformat(),
            "updated_at": movie['updated_at'].isoformat(),
            "version": movie['version'],
            "processing_status": movie['processing_status'],
            "_links": {
                "self": f"/movies/{movie['id']}",
                "cast": f"/movies/{movie['id']}/people"
            }
        }
        result.append(movie_data)
    
    return result


# -----------------------------------------------------------------------------
# Root
# -----------------------------------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "Welcome to Movies & People API",
        "version": "0.0.1",
        "description": "Advanced REST API with full CRUD, pagination, eTags, and linked data",
        "_links": {
            "movies": "/movies",
            "people": "/people",
            "docs": "/docs",
        }
    }



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
