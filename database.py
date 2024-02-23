from flask import Flask, jsonify
import pymysql.cursors

# Connect to the database
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='416G@*zy8k4r12',
                             database='sakila',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

api = Flask(__name__)

@api.route('/profile')
def profile():
    top_films = top_five_rented_films()
    top_actors = top_five_actors_in_inventory()
    cutomers = customers()
    return jsonify({'top_films': top_films, 'top_actors': top_actors, 'customers': cutomers})

# Returns the top 5 most rented movies + details
def top_five_rented_films():
    cursor = connection.cursor()
    sql = """SELECT film.title, film.description, film.release_year, language.name as langauge, film.length as duration, film.rating, film.special_features, COUNT(rental.rental_id) AS times_rented, film.last_update
            FROM film
            JOIN inventory ON film.film_id = inventory.film_id 
            JOIN rental ON inventory.inventory_id = rental.inventory_id
            join language on film.language_id = language.language_id
            GROUP BY film.title, film.description, film.release_year, language.name, duration, film.rating, film.special_features, film.last_update
            Order by times_rented DESC
            limit 5;"""
    cursor.execute(sql)
    result = cursor.fetchall()
    return result

# Returns the top 5 most rented movies + details
def top_five_actors_in_inventory():
    cursor = connection.cursor()
    sql = """SELECT actor.first_name, actor.last_name, count(inventory.film_id) as num_films
            from actor
            join film_actor on film_actor.actor_id = actor.actor_id 
            join film on film_actor.film_id = film.film_id 
            join inventory on film.film_id =inventory.inventory_id 
            group by actor.first_name, actor.last_name
            order by num_films DESC
            limit 5;"""
    cursor.execute(sql)
    result = cursor.fetchall()
    return result

# As a user I want to view a list of all customers + customer details
def customers():
    cursor = connection.cursor()
    sql = """Select *
            from customer"""
    cursor.execute(sql)
    result = cursor.fetchall()
    return result


# def get_actors():
#     cursor = connection.cursor()
#     sql = "SELECT * from actor limit 5"
#     cursor.execute(sql)
#     result = cursor.fetchall()
#     return result

if __name__ == '__main__':
    api.run(debug=True)