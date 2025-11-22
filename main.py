from fastapi import FastAPI, HTTPException, Response, Request, status, Header, Depends
from fastapi.responses import JSONResponse
from typing import List, Optional
from datetime import datetime
import hashlib
import random
import string
import logging
from sqlalchemy.orm import Session
from sqlalchemy import or_

from models.movie import MovieCreate, MovieUpdate, MovieRead
from models.person import PersonCreate, PersonUpdate, PersonRead
from models.db_models import Movie, Person, MoviePerson
from database import get_db, init_db, init_database, close_database
from utils.pagination import paginate


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------

def generate_etag(movie: Movie) -> str:
    """Generate ETag for a movie based on version and updated_at."""
    etag_string = f"{movie.version}-{movie.updated_at.isoformat()}"
    return hashlib.md5(etag_string.encode()).hexdigest()


def generate_version_hash() -> str:
    """Generate a random version hash (8 chars hex)."""
    return ''.join(random.choices(string.hexdigits.lower(), k=8))


# -----------------------------------------------------------------------------
# FastAPI Application
# -----------------------------------------------------------------------------

app = FastAPI(
    title="Movies & People API",
    description="Microservice 2 — Advanced REST API for movies and people with full CRUD, pagination, eTags, and linked data",
    version="0.0.1"
)


@app.on_event("startup")
async def startup_event():
    logger.info("Starting up application...")
    init_database()
    init_db()
    logger.info("Application startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down application...")
    close_database()
    logger.info("Application shutdown complete")


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
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    query = db.query(Movie)
    
    if title:
        query = query.filter(Movie.title.ilike(f"%{title}%"))
    
    if genre:
        query = query.filter(Movie.genre.ilike(genre))
    
    if year:
        query = query.filter(Movie.year == year)
    
    if year_min:
        query = query.filter(Movie.year >= year_min)
    
    if year_max:
        query = query.filter(Movie.year <= year_max)
    
    if sort == "year":
        if order.lower() == "desc":
            query = query.order_by(Movie.year.desc())
        else:
            query = query.order_by(Movie.year.asc())
    else:
        if order.lower() == "desc":
            query = query.order_by(Movie.title.desc())
        else:
            query = query.order_by(Movie.title.asc())
    
    movies = query.all()
    
    movies_read = []
    for movie in movies:
        movie_read = MovieRead(
            id=movie.id,
            title=movie.title,
            genre=movie.genre,
            year=movie.year,
            created_at=movie.created_at,
            updated_at=movie.updated_at,
            version=movie.version,
            processing_status=movie.processing_status,
            links={
                "self": f"/movies/{movie.id}",
                "cast": f"/movies/{movie.id}/people"
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
def create_movie(
    movie: MovieCreate,
    response: Response,
    db: Session = Depends(get_db)
):
    now = datetime.utcnow()
    version = generate_version_hash()
    
    new_movie = Movie(
        title=movie.title,
        genre=movie.genre,
        year=movie.year,
        created_at=now,
        updated_at=now,
        version=version,
        processing_status='COMPLETED'
    )
    
    db.add(new_movie)
    db.commit()
    db.refresh(new_movie)
    
    response.headers["Location"] = f"/movies/{new_movie.id}"
    
    return MovieRead(
        id=new_movie.id,
        title=new_movie.title,
        genre=new_movie.genre,
        year=new_movie.year,
        created_at=new_movie.created_at,
        updated_at=new_movie.updated_at,
        version=new_movie.version,
        processing_status=new_movie.processing_status,
        links={
            "self": f"/movies/{new_movie.id}",
            "cast": f"/movies/{new_movie.id}/people"
        }
    )


@app.get("/movies/{movie_id}", response_model=MovieRead)
def get_movie(
    movie_id: int,
    response: Response,
    if_none_match: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    etag = generate_etag(movie)
    
    if if_none_match and if_none_match.strip('"') == etag:
        return Response(status_code=status.HTTP_304_NOT_MODIFIED)
    
    response.headers["ETag"] = f'"{etag}"'
    
    return MovieRead(
        id=movie.id,
        title=movie.title,
        genre=movie.genre,
        year=movie.year,
        created_at=movie.created_at,
        updated_at=movie.updated_at,
        version=movie.version,
        processing_status=movie.processing_status,
        links={
            "self": f"/movies/{movie_id}",
            "cast": f"/movies/{movie_id}/people"
        }
    )


@app.put("/movies/{movie_id}", response_model=MovieRead)
def update_movie(
    movie_id: int,
    movie_update: MovieUpdate,
    db: Session = Depends(get_db)
):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    if movie_update.title is not None:
        movie.title = movie_update.title
    
    if movie_update.genre is not None:
        movie.genre = movie_update.genre
    
    if movie_update.year is not None:
        movie.year = movie_update.year
    
    movie.updated_at = datetime.utcnow()
    movie.version = generate_version_hash()
    
    db.commit()
    db.refresh(movie)
    
    return MovieRead(
        id=movie.id,
        title=movie.title,
        genre=movie.genre,
        year=movie.year,
        created_at=movie.created_at,
        updated_at=movie.updated_at,
        version=movie.version,
        processing_status=movie.processing_status,
        links={
            "self": f"/movies/{movie_id}",
            "cast": f"/movies/{movie_id}/people"
        }
    )


@app.delete("/movies/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    db.delete(movie)
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/movies/{movie_id}/people", response_model=List[dict])
def get_movie_people(movie_id: int, db: Session = Depends(get_db)):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    
    movie_people = db.query(MoviePerson).filter(MoviePerson.movie_id == movie_id).all()
    
    result = []
    for mp in movie_people:
        person = db.query(Person).filter(Person.id == mp.person_id).first()
        if person:
            person_data = {
                "id": person.id,
                "name": person.name,
                "role": person.role,
                "role_type": mp.role_type,
                "character_name": mp.character_name,
                "created_at": person.created_at.isoformat(),
                "updated_at": person.updated_at.isoformat(),
                "_links": {
                    "self": f"/people/{person.id}",
                    "movies": f"/people/{person.id}/movies"
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
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    query = db.query(Person)
    
    if movie_id is not None:
        movie = db.query(Movie).filter(Movie.id == movie_id).first()
        if not movie:
            raise HTTPException(status_code=404, detail="Movie not found")
        
        movie_people_ids = [mp.person_id for mp in db.query(MoviePerson).filter(MoviePerson.movie_id == movie_id).all()]
        
        if movie_people_ids:
            query = query.filter(Person.id.in_(movie_people_ids))
        else:
            query = query.filter(Person.id == -1)
    
    if name:
        query = query.filter(Person.name.ilike(f"%{name}%"))
    
    if role:
        query = query.filter(Person.role.ilike(f"%{role}%"))
    
    query = query.order_by(Person.name.asc())
    
    people = query.all()
    
    people_read = []
    for person in people:
        person_read = PersonRead(
            id=person.id,
            name=person.name,
            role=person.role,
            created_at=person.created_at,
            updated_at=person.updated_at,
            links={
                "self": f"/people/{person.id}",
                "movies": f"/people/{person.id}/movies"
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
def create_person(
    person: PersonCreate,
    response: Response,
    db: Session = Depends(get_db)
):
    now = datetime.utcnow()
    
    new_person = Person(
        name=person.name,
        role=person.role,
        created_at=now,
        updated_at=now
    )
    
    db.add(new_person)
    db.commit()
    db.refresh(new_person)
    
    response.headers["Location"] = f"/people/{new_person.id}"
    
    return PersonRead(
        id=new_person.id,
        name=new_person.name,
        role=new_person.role,
        created_at=new_person.created_at,
        updated_at=new_person.updated_at,
        links={
            "self": f"/people/{new_person.id}",
            "movies": f"/people/{new_person.id}/movies"
        }
    )


@app.get("/people/{person_id}", response_model=PersonRead)
def get_person(person_id: int, db: Session = Depends(get_db)):
    person = db.query(Person).filter(Person.id == person_id).first()
    
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    return PersonRead(
        id=person.id,
        name=person.name,
        role=person.role,
        created_at=person.created_at,
        updated_at=person.updated_at,
        links={
            "self": f"/people/{person_id}",
            "movies": f"/people/{person_id}/movies"
        }
    )


@app.put("/people/{person_id}", response_model=PersonRead)
def update_person(
    person_id: int,
    person_update: PersonUpdate,
    db: Session = Depends(get_db)
):
    person = db.query(Person).filter(Person.id == person_id).first()
    
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    if person_update.name is not None:
        person.name = person_update.name
    
    if person_update.role is not None:
        person.role = person_update.role
    
    person.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(person)
    
    return PersonRead(
        id=person.id,
        name=person.name,
        role=person.role,
        created_at=person.created_at,
        updated_at=person.updated_at,
        links={
            "self": f"/people/{person_id}",
            "movies": f"/people/{person_id}/movies"
        }
    )


@app.delete("/people/{person_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_person(person_id: int, db: Session = Depends(get_db)):
    person = db.query(Person).filter(Person.id == person_id).first()
    
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    db.delete(person)
    db.commit()
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@app.get("/people/{person_id}/movies", response_model=List[dict])
def get_person_movies(person_id: int, db: Session = Depends(get_db)):
    person = db.query(Person).filter(Person.id == person_id).first()
    
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    
    person_movies = db.query(MoviePerson).filter(MoviePerson.person_id == person_id).all()
    
    result = []
    for pm in person_movies:
        movie = db.query(Movie).filter(Movie.id == pm.movie_id).first()
        if movie:
            movie_data = {
                "id": movie.id,
                "title": movie.title,
                "genre": movie.genre,
                "year": movie.year,
                "role_type": pm.role_type,
                "character_name": pm.character_name,
                "created_at": movie.created_at.isoformat(),
                "updated_at": movie.updated_at.isoformat(),
                "version": movie.version,
                "processing_status": movie.processing_status,
                "_links": {
                    "self": f"/movies/{movie.id}",
                    "cast": f"/movies/{movie.id}/people"
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
