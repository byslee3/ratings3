from flask import Flask, render_template, redirect, request, session, flash
import model

app = Flask(__name__)

SECRET_KEY = 'power_pose'
app.config.from_object(__name__)

@app.route("/")
def index():
    # user_list = model.session.query(model.User).all()
    # return render_template("user_list.html", user_list = user_list)
    return redirect("/login")

@app.route("/test", methods=["GET","POST"])
def test():
    return render_template("test.html")

@app.route("/profile")
def profile():
    current_user = session['user_id']
    ratings_list = model.session.query(model.Rating).filter(model.Rating.user_id == current_user).all()
    return render_template("profile.html", ratings_list=ratings_list)

@app.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html")

@app.route("/logout", methods=["GET", "POST"])
def logout():
    session['user_id'] = None
    return redirect("/login")

@app.route("/authenticate", methods=["GET", "POST"])
def authenticate():
    try:
        email_entered = str(request.form['email_field'])
        password_entered = str(request.form['password_field'])

        logged_in_user = model.session.query(model.User).filter(model.User.email == email_entered, model.User.password == password_entered).one()

        if logged_in_user:

            session['user_id'] = logged_in_user.id
            return redirect("/profile")
    except:
        flash("Invalid user id")
        return redirect("/login")

@app.route("/movie_search", methods=["GET", "POST"])
def movie_search():

    target_movie_name = str(request.form['movie_field'])
    target_movie_name_formatted = "%" + target_movie_name + "%"

    all_matching_movies = model.session.query(model.Movie).filter(model.Movie.title.like(target_movie_name_formatted)).all()

    return render_template("movie_listing.html", searched_movie_name=target_movie_name, all_matching_movies=all_matching_movies)

@app.route("/show_specific_movie/<int:id>",methods=["GET","POST"])
def show_specific_movie(id):
    
    specific_movie = model.session.query(model.Movie).filter(model.Movie.id == id).first()

    current_user_id = session["user_id"]
    current_user = model.session.query(model.User).get(current_user_id)
    existing_user_rating = "Not rated yet"

    #Calculate the average rating for this movie
    ratings_sum = 0.0
    ratings_count = 0

    for r in specific_movie.ratings:
        ratings_sum += r.rating
        ratings_count += 1

        #BTW, also check if user has already rated
        if r.user_id == current_user_id:
            existing_user_rating = r.rating

    average_rating = round(ratings_sum / ratings_count,2)

    #If the user has not rated the movie yet, calculate a prediction
    #Otherwise, leave the prediction as None and pass the user rating to the html template
    if existing_user_rating == "Not rated yet":
        predicted_rating = current_user.predict_rating(specific_movie)
    else:
        predicted_rating = None

    #Get the rating from the Judgemental Eye
    the_eye = model.session.query(model.User).filter_by(email="the_eye").one()
    eye_rating = model.session.query(model.Rating).filter(model.Rating.movie_id==specific_movie.id, model.Rating.user_id==the_eye.id).first()

    if not eye_rating:
        eye_rating = the_eye.predict_rating(specific_movie)
    else:
        eye_rating = eye_rating.rating

    print eye_rating
    print predicted_rating
    print existing_user_rating

    #Pick a response based on how much you and the Eye differ
    if predicted_rating == "Not enough data":
        difference = 99
    elif predicted_rating:
        difference = abs(eye_rating - predicted_rating)
    else:
        difference = abs(eye_rating - existing_user_rating)

    messages = [ "I suppose you don't have such bad taste after all.",
    "I regret every decision that I've ever made that has brought me to listen to your opinion.",
    "Words fail me, as your taste in movies has clearly failed you.",
    "That movie is great. For a clown to watch. Idiot.",
    "You suck."]

    if difference < 5:
        beratement = messages[int(difference)]
    else:
        beratement = "You don't even have enough data for me to judge you."

    return render_template("show_specific_movie.html", specific_movie=specific_movie, average_rating=average_rating, predicted_rating=predicted_rating, existing_user_rating=existing_user_rating, eye_rating=eye_rating, difference=difference, beratement=beratement)

@app.route("/add_rating/<int:id>", methods=["GET","POST"])
def add_rating(id):

    specific_movie_id = id
    specific_user_id = session["user_id"]
    specific_rating = request.form["my_rating"]

    #first check if the record with same user_id and movie_id already exists
    #if so, overwrite this rating
    #else, add a new record to the Ratings table
    existing_rating = model.session.query(model.Rating).filter(model.Rating.movie_id==specific_movie_id, model.Rating.user_id==specific_user_id).first()
    
    if existing_rating:
        existing_rating.rating = specific_rating
        model.session.commit()
    else:
        new_rating = model.Rating(specific_movie_id, specific_user_id, specific_rating)
        model.session.add(new_rating)
        model.session.commit()

    flash("You added a new rating")
    return redirect("/profile")


#app starts running here
if __name__ == "__main__":
    app.run(debug = True)







