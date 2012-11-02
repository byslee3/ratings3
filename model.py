import correlation
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship, backref, scoped_session

#The file that calculates the Pearson correlation


engine = create_engine("sqlite:///ratings.db", echo=False)
session = scoped_session(sessionmaker(bind=engine, autocommit=False, autoflush=False))

Base = declarative_base()
Base.query = session.query_property()


### Class declarations go here
class User(Base):
    __tablename__ = "Users"

    id = Column(Integer, primary_key = True)
    email = Column(String(64), nullable=True)
    password = Column(String(64), nullable=True)
    age = Column(Integer, nullable=True)
    zipcode = Column(String(15), nullable=True)

    def __init__(self, email = None, password = None, age=None, zipcode=None):
        self.email = email
        self.password = password
        self.age = age
        self.zipcode = zipcode

    def similarity(self, other):

        my_ratings = {}
        paired_ratings = []
        for r in self.ratings:
            my_ratings[r.movie_id] = r

        for o in other.ratings:
            matching_rating = my_ratings.get(o.movie_id)
            if matching_rating:
                paired_ratings.append( (matching_rating.rating, o.rating) )

        if paired_ratings:
            return correlation.pearson(paired_ratings)
        else:
            return 0.0

class Movie(Base):
    __tablename__ = "Movies"

    id = Column(Integer, primary_key = True)
    title = Column(String(64))
    released_at = Column(DateTime)
    imdb_url = Column(String)

    def __init__(self, title, released_at, imdb_url):
        self.title = title
        self.released_at = released_at
        self.imdb_url = imdb_url

class Rating(Base):
    __tablename__ = "Ratings"

    id = Column(Integer, primary_key = True)
    movie_id = Column(Integer, ForeignKey('Movies.id'))
    user_id = Column(Integer, ForeignKey('Users.id'))
    rating = Column(Integer)

    # creating new attributes for the rating object
    # create a relationship between User class with rating attribute
    # from current class. List them in order by id.
    user = relationship("User", backref=backref("ratings", order_by=id))
    movie = relationship("Movie", backref=backref("ratings", order_by=id))

    def __init__(self, movie_id, user_id, rating):
        self.movie_id = movie_id
        self.user_id = user_id
        self.rating = rating



### End class declarations

def main():
    """In case we need this for something"""
    pass

if __name__ == "__main__":
    main()
