import cmath
import pandas as pd
import requests

username = 'User 19'

dt = pd.read_csv('data.csv', index_col=0, sep=', ', engine='python')
ctx = pd.read_csv('context.csv', index_col=0, sep=', ', engine='python')

def avg_rating(user_number, data):
    avg = 0
    cnt = 0
    ratings = data.iloc[user_number]
    for rate in ratings:
        if rate != -1:
            avg += rate
            cnt += 1
    return avg/cnt


def similarity(u, v, data):
    u_series = data.iloc[u]
    v_series = data.iloc[v]
    a = 0
    b = 0
    c = 0

    for i in range(0, len(u_series)):
        if u_series[i] != -1 and v_series[i] != -1:
            a += u_series[i]*v_series[i]
            b += u_series[i]**2
            c += v_series[i]**2

    return a / (cmath.sqrt(b) * cmath.sqrt(c))


def get_k_similar_users(u, k, data):
    sims = {}
    for v in range(0, len(data.axes[0])):
        if v != u:
            sims[v] = similarity(u, v, data)
    sims = dict(sorted(sims.items(), key=lambda x: x[1], reverse=True)[:k])
    return sims


def calculate_rate(u, i, data, sims):
    avg = avg_rating(u, data)
    top = 0
    bottom = 0

    for v in sims:
        sim = sims[v]
        v_rate = data.iloc[v, i]
        if v == u or v_rate == -1:
            continue
        top += sim * (v_rate - avg_rating(v, data))
        bottom += abs(sim)
    return avg + top / bottom


def predicted_film_rates(u, data):
    rates = {}
    sims = get_k_similar_users(u, 5, data)
    for i in range(0, len(data.axes[1])):
        if data.iloc[u, i] == -1:
            rates[data.axes[1][i]] = calculate_rate(u, i, data, sims)
    return rates




# TASK 2
def context_filtered_rates(u, data, context):
    filtered = data.copy()
    for user_id in range(0, len(context.axes[0])):
        if user_id == u:
            continue
        for movie_id in range(0, len(context.axes[1])):
            if context.iloc[user_id, movie_id] in ['Sun', 'Sat']:
                filtered.iloc[user_id, movie_id] = -1
    return filtered


def get_recommendation(u, data, context):
    filtered_data = context_filtered_rates(u, data, context)
    movie = {}
    movies_rates = predicted_film_rates(u, filtered_data)
    movies_rates = sorted(movies_rates.items(), key=lambda x: x[1], reverse=True)
    if len(movies_rates) > 0:
        movie['name'] = movies_rates[0][0]
        movie['rating'] = movies_rates[0][1]
        return movie
    return None

user_id = -1
for index in range(0, len(dt.axes[0])):
    if dt.axes[0][index] == username:
        user_id = index
        break

film_rates = predicted_film_rates(user_id, dt)
recommendation = get_recommendation(user_id, dt, ctx)

print(film_rates)
print(recommendation)

request_body = {}

request_body['user'] = user_id

request_body['1'] = {}
for (movie_name, movie_rating) in film_rates.items():
    request_body['1'][movie_name] = movie_rating.real

if recommendation:
    request_body['2'] = {
        recommendation['name']: recommendation['rating'].real
    }


print(request_body)

req = requests.post('https://cit-home1.herokuapp.com/api/rs_homework_1', json=request_body)

print(req.text)