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

    ratings_sum = 0.0
    ratings_count = 0

    for r in specific_movie.ratings:
        ratings_sum += r.rating
        ratings_count += 1

    average_rating = round(ratings_sum / ratings_count,2)

    return render_template("show_specific_movie.html", specific_movie=specific_movie, average_rating=average_rating)



if __name__ == "__main__":
    app.run(debug = True)