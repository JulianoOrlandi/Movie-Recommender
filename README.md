# Movie Recommender
#### **Video Demo:**  <URL https://youtu.be/ekn8H-DYaik>

#### **Objective:**
Implementing a machine learning algorithm for movie recommendation

#### **Justification:**
Since I started to learn Computer Science, I am increasingly interested in ​​data science and analysis. For this reason, I decided to develop as my **Final Project** in **CS50** somenthing related to these subjects. I have attended to the seminar, [Introduction to Machine Learning](https://www.youtube.com/watch?v=b_ZVSvAHLKQ), and I decided to create **a web-based application using Python and SQL**.

#### **Description:**
Overall, my project is a web application developed in Python and SQL. It uses the [IMDB database](http://www.omdbapi.com) for retrieving information and it has the function of recommending movies to users based on a machine learning algorithm.


#### **HTML and CSS:**
There are only five .html archives: [layout](/project/templates/layout.html), [login](/project/templates/login.html), [register](/project/templates/register.html), [index](/project/templates/index.html) and [training](/project/templates/training.html). The first three contain the general design of the web page and the specific fields for registering and logging into the application. Nothing too fancy. The [index](/project/templates/index.html) page is simply composed of a field to show information about the recommended movie and a button to move to the next recommendation. The [training](/project/templates/training.html) is where things get a little more complicated. It has a form and a button to search for movies. But when it shows the information of a movie, it adds a new form and a new button to rate that movie. And on top of that, it has a button to start the machine learning algorithm.

There is also a .css archive for handling styles: [styles](/project/static/styles.css).

#### **Recommender.db:**
There are three main tables in the recommender.db file. In the first one, *users*, the application stores user data (username and password hash).

The second, *users_movies_preferences*, holds information about users' movie preferences. The columns are the movies that were rated and the rows correspond to the users. The first two users in the table actually represent Metacritic and IMDB ratings. The information comes from the [IMDB database](http://www.omdbapi.com). Below I will explain in more detail why I treated them as users. The number of columns, that is, the number of films evaluated, can always increase. But I already created the table with 100 movies. There were two reasons for that: firstly, I wanted to simulate the idea that the same system has a limited number of movies as in any streaming platform. And second, the algorithm takes some time to do the calculations. If the table were too long, the application could take too much time to provide recommendations to users.

The third table, *users_movies_recommendations*, has the same structure as the *users_movies_preferences* table. The difference is that it is filled with the results of the machine learning algorithm. Therefore it contains predictions of users' preferences. It is based on this table that the application can make movie recommendations.

Each time a user registers in the application, it creates a specific table to store the preferences of each individual. It does not have much use in the application as it is designed right now, but it could be used to implement other algorithms which improve the movie recommendation process.

#### **creds.py:**
This [file](/project/creds.py) only contains the API key to search the [IMDB database](http://www.omdbapi.com). There was no need for each user to register a key to access the database. I created this file, however, to hide the API key, following the directions of this [tutorial](https://www.youtube.com/watch?v=CJjSOzb0IYs).

#### **app.py:**
There are five routes in the [application file](/project/app.py): *login*, *logout*, *register*, *training* and *index*. The first two are simply for the user to connect or disconnect from the application.

In the *register* route, in addition to having your username and password hash entered in the *users* table, the application creates a specific table to store the user's movie preferences and includes the user ID as a row in the *users_movies_preferences* and *users_movies_recommendations* tables.

In the *training* route, there are three functions the user can perform: *search*, *rate* and *train*. The first one searches the [IMDB database](http://www.omdbapi.com) for the movie information indicated by the user and renders them on the page.

The second changes the preferences table of the logged in user, the *users_movies_preferences* table and the *users_movies_recommendations* table to include the rated movie. It then stores in *users_movies_preferences* the rating given by the user, as well as the Metacritic and IMDB ratings.

The third function of the *training* route starts the machine learning algorithm. Its specifics will be presented below. But in short, the function generates an 2D array from the *users_movies_preferences* table. Second, it uses this array to generate another one with the recommendations. And finally, it uses this new 2d array to populate the *users_movies_recommendations* table.

Finally, the *index* route creates from *users_movies_recommendations* a list of movie recommendations for the logged in user. Randomly chooses an item from this list and checks if the user has already watched this movie. If he has not watched, the function searches for the information in the [IMDB database](http://www.omdbapi.com) and shows it to the user.

#### **helpers.py:**
There are five functions in this [file](/project/helpers.py): *login_required*, *lookup_title*, *lookup_id*, *generate_matrix_preferences* and *generate_matrix_recommendations*. The first is a wrapper to ensure that only the registered user can access the other functions of the application. The second and third are functions that communicate with the [IMDB database](http://www.omdbapi.com) and allow the search for information about the movies. One of them uses the movie title to search and the other uses the ID. The fourth function takes a list of dictionaries and generates an array with the values of the dictionaries.

The fifth function is the machine learning algorithm itself. The fundamental idea here is the implementation of a collaborative filter, that is, the use of the ratings given by all users to generate recommendations for new movies. It was for this reason that it includes the Metacritic and IMDB ratings as users. If there is no previously given score, the algorithm will not be able to make predictions.

The approach chosen was the gradient descent algorithm. The tutorials I used to learn and implement the algorithm are the following: [Matrix Factorization: A Simple Tutorial and Implementation in Python
](https://albertauyeung.github.io/2017/04/23/python-matrix-factorization.html/), [Matrix Factorization as a Recommender System](https://medium.com/analytics-vidhya/matrix-factorization-as-a-recommender-system-727ee64683f0) and [Python: Implementing Matrix Factorization from Scratch!](https://towardsdatascience.com/recommender-systems-in-python-from-scratch-643c8fc4f704).

The operation of the algorithm is basically as follows. The function receives the preferences matrix generated by the *generate_matrix_preferences* function. It then randomly generates two matrices (u_f, f_i) whose product is a matrix of the same size as the preferences matrix. The algorithm then starts a loop in which it compares the values ​​of the preference matrix with this new matrix. It then identifies the difference between these values ​​as the error factor (e) and corrects the values ​​of those two matrices (u_f, f_i) with the help of a command that uses this factor. After that, the algorithm calculates a new error factor between the preference matrix and the recommendation matrix. If the factor is less than 0.001, it breaks the loop and returns the 2D array of recommendations. Otherwise, it restarts the process of calculating the error factor and the process of adjusting the values ​​of the matrices u_f and f_i. If the factor calculated at the end is never less than 0.001, the function repeats 5000 times and then returns the matrix of recommendations. The two most important items for the accuracy and efficiency of the algorithm are the number of repetitions and the number of features used to create the matrices u_f and f_i. Here the number of repetitions is 5000, but it can be increased. And the number of features is 3 and could be increased as well. The price to pay if one of the two is increased is execution time.