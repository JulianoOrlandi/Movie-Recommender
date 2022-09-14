import random

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import lookup_title, login_required, generate_matrix_preferences, generate_matrix_recommendations, lookup_id

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///recommender.db")

# Global Variables (movie_id and movie_title):
movie_id = ''
movie_title = ''

@app.after_request
def after_request(response):

    # Ensure responses aren't cached:
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route("/", methods=["GET"])
@login_required
def index():

    # Creating the list of recommendations for the user:
    try:
        recommendations = db.execute("SELECT * FROM users_movies_recommendations WHERE id=?", session['user_id'])
        recommendations_values = recommendations[0].values()
        recommendations_keys = recommendations[0].keys()
        list_recommendations_values = []
        list_recommendations_keys = []
        for item in recommendations_values:
            if item == session['user_id']:
                continue
            else:
                tmp1 = float(item)
                list_recommendations_values.append(tmp1)
        for item in recommendations_keys:
            if item == 'id':
                continue
            else:
                list_recommendations_keys.append(item)
    except:
        flash("Error: you must run the algorithm before see recommendations!", "error")
        return render_template("training.html")
    # Choosing a movie that is rated above the average of rates:
    average_rating = sum(list_recommendations_values) / len(list_recommendations_values)
    rating = 0
    while True:
        # Checking if the movie was already rated by the user:
        rating = random.choice(list_recommendations_values)
        if rating < average_rating:
            rated_movie_id = list_recommendations_keys[list_recommendations_values.index(rating)]
            if len(db.execute("SELECT * FROM user? WHERE movie_id=?", session['user_id'], rated_movie_id)) == 1:
                continue
            else:
                break
    # Getting the information of the movie to be recommended:
    movie_data2 = lookup_id(rated_movie_id)
    return render_template("index.html", title = movie_data2['Title'], plot=movie_data2['Plot'], poster=movie_data2['Poster'], director='Director: ', director_name=movie_data2['Director'], actors='Actors: ', actors_names=movie_data2['Actors'])

@app.route("/login", methods=["GET", "POST"])
def login():

    # Forget any user id:
    session.clear()

    # User reached route via POST:
    if request.method == "POST":

        # Ensure username was submitted:
        if not request.form.get("username"):
            flash("Error: you must provide an username!", "error")
            return render_template("login.html")

        # Ensure password was submitted:
        elif not request.form.get("password"):
            flash("Error: you must provide a password!", "error")
            return render_template("login.html")

        else:

            # Query database for username:
            rows = db.execute("SELECT * FROM users WHERE username=?", request.form.get("username"))

            # Ensure username exists and password is correct:
            if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
                flash("Error: invalid username and/or password!", "error")
                return render_template("login.html")

            # Remember which user has logged in
            session["user_id"] = rows[0]["id"]

            # Redirect user to homepage:
            return redirect("/")

    # User reached route via GET:
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():

        if request.method == "POST":

            # Ensure the username is not already taken:
            if len(db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))) == 1:
                flash("Error: this username is already taken!", "error")
                return render_template("register.html")

            # Ensure username was submitted:
            elif not request.form.get("username"):
                flash("Error: you must provide an username!", "error")
                return render_template("register.html")

            # Ensure password was submitted:
            elif not request.form.get("password"):
                flash("Error: you must provide a password!", "error")
                return render_template("register.html")

            # Ensure confirmation was submitted:
            elif not request.form.get("confirmation"):
                flash("Error: you must confirm your password!", "error")
                return render_template("register.html")

            # Ensure password and confirmation are the same:
            elif request.form.get("password") != request.form.get("confirmation"):
                flash("Error: you typed different passwords!", "error")
                return render_template("register.html")

            else:

                # Inserting username and hash in users' table:
                username = request.form.get("username")
                hash = generate_password_hash(request.form.get("password"))
                db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hash)
                logged = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
                session['user_id'] = logged[0]['id']

                # Creating a table for the users rated movies:
                db.execute("CREATE TABLE user? (movie_id TEXT NOT NULL, rating NUMERIC NOT NULL)", session['user_id'])

                # Inserting a users' row in users_movies_preferences and users_movies_recommendations tables:
                db.execute("INSERT INTO users_movies_preferences (id) VALUES (?)", session['user_id'])
                db.execute("INSERT INTO users_movies_recommendations (id) VALUES (?)", session['user_id'])
                return redirect("/training")
        else:
            return render_template("register.html")

@app.route("/training", methods=["GET", "POST"])
@login_required
def training():
    global movie_id
    global movie_title

    if request.method == "POST":

        # Rating a movie:
        # Checking for valid input:
        if 'rate' in request.form:
            if request.form.get('rate') == '' or (float(request.form.get('rate')) <= 0) or float(request.form.get('rate')) > 10:
                flash("Error: rate must be between 0.0 and 10.0", "error")
                return render_template("training.html")
            else:
                # Checking if the movie was already rated:
                if len(db.execute("SELECT * FROM user? WHERE movie_id=?", session['user_id'], movie_id)) != 0:
                    db.execute("UPDATE user? SET rating=? WHERE movie_id=?", session['user_id'], request.form.get('rate'), movie_id)
                else:
                    db.execute("INSERT INTO user? (movie_id, rating) VALUES (?, ?)", session['user_id'], movie_id, request.form.get('rate'))

                # Checking if movie is already is users_movies_preferences table:
                isindatabase = db.execute("SELECT COUNT (*) AS result FROM pragma_table_info('users_movies_preferences') WHERE name=?", movie_id)

                if isindatabase[0]['result'] == 1:
                    db.execute("UPDATE users_movies_preferences SET ?=? WHERE id=?", movie_id, request.form.get('rate'), session['user_id'])
                else:

                    # Adding the new movie to the users_movies_preferences and the users_movies_recommendations tables:
                    db.execute("ALTER TABLE users_movies_preferences ADD ? TEXT", movie_id)
                    db.execute("ALTER TABLE users_movies_recommendations ADD ? TEXT", movie_id)
                    db.execute("UPDATE users_movies_preferences SET ?=? WHERE id=?", movie_id, request.form.get('rate'), session['user_id'])

                    # Fullfilling the users_movies_preferences with the rates from OMDB:
                    movies_ratings = lookup_title(movie_title)
                    db.execute("UPDATE users_movies_preferences SET ?=? WHERE id=0", movie_id, movies_ratings['imdbRating'])
                    metascore = float(movies_ratings['Metascore']) / 10
                    db.execute("UPDATE users_movies_preferences SET ?=? WHERE id=1", movie_id, metascore)

                flash("Success: you rated the movie with success.", "success")
                return render_template("training.html")

        # Training the algorithm:
        # Generating the matrix for the machine learning algorithm:
        elif 'train' in request.form:
            preferences = db.execute("SELECT * FROM users_movies_preferences")
            matrix_preferences = generate_matrix_preferences(preferences)
            matrix_recommendations = generate_matrix_recommendations(matrix_preferences)


            # Storing the columns' and the rows' names:
            columns_names = db.execute("SELECT name FROM pragma_table_info('users_movies_preferences')")
            rows_names = db.execute("SELECT id FROM users_movies_preferences")
            list_columns = []
            list_rows = []
            for item in columns_names:
                temp1 = item.values()
                temp2 = list(temp1)
                if temp2[0] != 'id':
                    list_columns.append(temp2[0])
            for item in rows_names:
                temp3 = item.values()
                temp4 = list(temp3)
                list_rows.append(temp4[0])

            # Creating the matrix of recommendations and updating the users_movies_recommendations table:
            for i in range(len(matrix_recommendations)):
                for j in range(len(matrix_recommendations[0])):
                    temp5 = str(round(matrix_recommendations[i][j], 2))
                    db.execute("UPDATE users_movies_recommendations SET ?=? WHERE id=?", list_columns[j], temp5, list_rows[i])
            return redirect("/")

        # Searching for movie's information:
        else:

            # Checking for valid movie's title:
            movie_data = lookup_title(request.form.get("title"))
            if movie_data['Response'] == 'False':
                flash("Error: movie not founded!", "error")
                return render_template("training.html")

            # Displayig movie's information:
            else:
                movie_id = movie_data['imdbID']
                movie_title = movie_data['Title']
                return render_template("training.html", plot=movie_data['Plot'], poster=movie_data['Poster'], director='Director: ', director_name=movie_data['Director'], actors='Actors: ', actors_names=movie_data['Actors'], isSuccess=True)

    else:
        return render_template("training.html")