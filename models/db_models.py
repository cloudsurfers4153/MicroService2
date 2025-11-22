from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Index
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Movie(Base):
    __tablename__ = "movies"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    genre = Column(String(100), nullable=False, index=True)
    year = Column(Integer, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    version = Column(String(8), nullable=False)
    processing_status = Column(String(20), default="COMPLETED", nullable=False)
    
    movie_people = relationship("MoviePerson", back_populates="movie", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Movie(id={self.id}, title='{self.title}', year={self.year})>"


class Person(Base):
    __tablename__ = "people"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False, index=True)
    role = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    person_movies = relationship("MoviePerson", back_populates="person", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Person(id={self.id}, name='{self.name}', role='{self.role}')>"


class MoviePerson(Base):
    __tablename__ = "movie_people"
    
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    person_id = Column(Integer, ForeignKey("people.id", ondelete="CASCADE"), primary_key=True, nullable=False)
    character_name = Column(String(255), nullable=True)
    role_type = Column(String(100), nullable=False)
    
    movie = relationship("Movie", back_populates="movie_people")
    person = relationship("Person", back_populates="person_movies")
    
    __table_args__ = (
        Index("idx_movie_id", "movie_id"),
        Index("idx_person_id", "person_id"),
    )
    
    def __repr__(self):
        return f"<MoviePerson(movie_id={self.movie_id}, person_id={self.person_id}, role_type='{self.role_type}')>"

