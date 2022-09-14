import requests
import numpy as np
import creds

from flask import redirect, session
from functools import wraps


def login_required(f):
    """ Decorate routes to require login """
    @wraps(f)
    def decorate_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorate_function


def lookup_title(title):

    url = f"http://www.omdbapi.com/?apikey={creds.api_key}&t={title}&plot=full"
    response = requests.get(url)
    return response.json()

def lookup_id(movie_id):

    url = f"http://www.omdbapi.com/?apikey={creds.api_key}&i={movie_id}&plot=full"
    response = requests.get(url)
    return response.json()

def generate_matrix_preferences(preferences):
    list_temp = []
    list_preferences = []
    for item in preferences:
        temp1 = item.values()
        temp2 = list(temp1)
        i = 0
        for i in range(1, len(temp2)):
            if temp2[i] == None:
                temp2[i] = '0'
            temp3 = float(temp2[i])
            list_temp.append(temp3)
        list_preferences.append(list_temp)
        list_temp = []
    return list_preferences

def generate_matrix_recommendations(matrix_preferences):
    features = 3
    u_f = np.random.uniform(low=1.0, high=4.0, size=(len(matrix_preferences), features))
    f_i = np.random.uniform(low=1.0, high=4.0, size=(features, len(matrix_preferences[0])))
    count = 0
    while count < 5000:
        for i in range(len(matrix_preferences)):
            for j in range(len(matrix_preferences[i])):
                if matrix_preferences[i][j] > 0:
                    e = (matrix_preferences[i][j] - (np.dot(u_f[i,:], f_i[:,j])))
                    for k in range(features):
                        u_f[i][k] = u_f[i][k] + 0.0002 * (2 * e * f_i[k][j] - 0.02 * u_f[i][k])
                        f_i[k][j] = f_i[k][j] + 0.0002 * (2 * e * u_f[i][k] - 0.02 * f_i[k][j])
        matrix_recommendations = np.dot(u_f,f_i)
        e = 0
        for i in range(len(matrix_preferences)):
            for j in range(len(matrix_preferences[i])):
                e = e + pow(matrix_preferences[i][j] - np.dot(u_f[i,:], f_i[:,j]), 2)
                for k in range(features):
                    e = e + (0.02/2) * (pow(u_f[i][k],2) + pow(f_i[k][j], 2))
        if e < 0.001:
            break
        count += 1
    return matrix_recommendations