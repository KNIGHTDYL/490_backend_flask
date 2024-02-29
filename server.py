from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, or_

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:great-days321@localhost:3306/sakila'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
CORS(app)

class Actor(db.Model):
    __tablename__ = 'actor'
    actor_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(45))
    last_name = db.Column(db.String(45))
    last_update = db.Column(db.DateTime)

class Category(db.Model):
    __tablename__ = 'category'
    category_id = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(25), nullable=False)

class Customer(db.Model):
    __tablename__ = 'customer'
    customer_id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('store.store_id'), nullable=False)
    first_name = db.Column(db.String(45), nullable=False)
    last_name = db.Column(db.String(45), nullable=False)
    email = db.Column(db.String(50))
    address_id = db.Column(db.Integer, db.ForeignKey('address.address_id'), nullable=False)
    active = db.Column(db.Boolean, nullable=False, default=True)
    create_date = db.Column(db.DateTime, nullable=False)
    last_update = db.Column(db.DateTime, nullable=False)

class Film(db.Model):
    __tablename__ = 'film'
    film_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    release_year = db.Column(db.Integer)
    language_id = db.Column(db.Integer, db.ForeignKey('language.language_id'))
    original_language_id = db.Column(db.Integer, db.ForeignKey('language.language_id'))
    rental_duration = db.Column(db.Integer, default=3)
    rental_rate = db.Column(db.Numeric(4, 2), default=4.99)
    length = db.Column(db.Integer)
    replacement_cost = db.Column(db.Numeric(5, 2), default=19.99)
    rating = db.Column(db.Enum('G', 'PG', 'PG-13', 'R', 'NC-17'), default='G')
    special_features = db.Column(db.String(255))
    last_update = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())
    language = db.relationship('Language', foreign_keys=[language_id])
    original_language = db.relationship('Language', foreign_keys=[original_language_id])

class FilmActor(db.Model):
    __tablename__ = 'film_actor'
    actor_id = db.Column(db.Integer, db.ForeignKey('actor.actor_id'), primary_key=True)
    film_id = db.Column(db.Integer, db.ForeignKey('film.film_id'), primary_key=True)
    last_update = db.Column(db.DateTime, nullable=False)

class FilmCategory(db.Model):
    __tablename__ = 'film_category'
    film_id = db.Column(db.Integer, db.ForeignKey('film.film_id'), primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.category_id'), primary_key=True)
    last_update = db.Column(db.DateTime)
    film = db.relationship('Film', backref=db.backref('film_categories'))
    category = db.relationship('Category', backref=db.backref('film_categories'))

class Inventory(db.Model):
    __tablename__ = 'inventory'
    inventory_id = db.Column(db.Integer, primary_key=True)
    film_id = db.Column(db.Integer, db.ForeignKey('film.film_id'))
    store_id = db.Column(db.Integer, db.ForeignKey('store.store_id'))
    last_update = db.Column(db.DateTime)

class Language(db.Model):
    __tablename__ = 'language'
    language_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    last_update = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

class Rental(db.Model):
    __tablename__ = 'rental'
    rental_id = db.Column(db.Integer, primary_key=True)
    rental_date = db.Column(db.DateTime)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.inventory_id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'))
    return_date = db.Column(db.DateTime)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.staff_id'))
    last_update = db.Column(db.DateTime)

class Staff(db.Model):
    __tablename__ = 'staff'
    staff_id = db.Column(db.Integer, primary_key=True)

@app.route('/', methods=['GET'])
def get_actors():
    actors = Actor.query.all()
    actor_list = []
    for actor in actors:
        actor_data = {
            'actor_id': actor.actor_id,
            'first_name': actor.first_name,
            'last_name': actor.last_name,
            'last_update': actor.last_update.strftime('%Y-%m-%d %H:%M:%S')
        }
        actor_list.append(actor_data)
    return jsonify({'actors': actor_list})

@app.route('/customers', methods=['GET'])
def get_customers():
    try:
        customers = Customer.query.all()
        customer_list = []
        for customer in customers:
            customer_info = {
                'customer_id': customer.customer_id,
                'store_id': customer.store_id,
                'first_name': customer.first_name,
                'last_name': customer.last_name,
                'email': customer.email,
                'address_id': customer.address_id,
                'active': customer.active,
                'create_date': customer.create_date.isoformat(),
                'last_update': customer.last_update.isoformat()
            }
            customer_list.append(customer_info)
        return jsonify({'customers': customer_list}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/customers', methods=['POST'])
def add_customer():
    try:
        data = request.json
        new_customer = Customer(
            store_id=data['store_id'],
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            address_id=data['address_id'],
            active=data['active'],
            create_date=data['create_date'],
            last_update=data['last_update']
        )
        db.session.add(new_customer)
        db.session.commit()
        return jsonify({'message': 'Customer added successfully'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/customers/<int:customer_id>', methods=['PUT'])
def update_customer(customer_id):
    try:
        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        data = request.json
        customer.store_id = data.get('store_id', customer.store_id)
        customer.first_name = data.get('first_name', customer.first_name)
        customer.last_name = data.get('last_name', customer.last_name)
        customer.email = data.get('email', customer.email)
        customer.address_id = data.get('address_id', customer.address_id)
        customer.active = data.get('active', customer.active)
        customer.create_date = data.get('create_date', customer.create_date)
        customer.last_update = data.get('last_update', customer.last_update)

        db.session.commit()
        return jsonify({'message': 'Customer updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/customers/<int:customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    try:
        customer = Customer.query.get(customer_id)
        if not customer:
            return jsonify({'error': 'Customer not found'}), 404
        
        db.session.delete(customer)
        db.session.commit()
        return jsonify({'message': 'Customer deleted successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/films', methods=['GET'])
def get_films():
    query = (
        db.session.query(
            Film.film_id,
            Film.title,
            Film.description,
            Film.release_year,
            Film.language_id,
            Film.rental_duration,
            Film.rental_rate,
            Film.length,
            Film.rating,
            Film.special_features,
            func.count(Rental.rental_id).label('rental_count')
        )
        .join(Inventory, Film.film_id == Inventory.film_id)
        .join(Rental, Inventory.inventory_id == Rental.inventory_id)
        .group_by(Film.film_id, Film.title, Film.description, Film.release_year, Film.language_id,
                  Film.rental_duration, Film.rental_rate, Film.length, Film.rating, Film.special_features)
    )

    films = query.all()

    films_data = []
    for film in films:
        film_data = {
            'film_id': film.film_id,
            'title': film.title,
            'description': film.description,
            'release_year': film.release_year,
            'language_id': film.language_id,
            'rental_duration': film.rental_duration,
            'rental_rate': float(film.rental_rate),  
            'length': film.length,
            'rating': film.rating,
            'special_features': film.special_features,
            'rental_count': film.rental_count
        }
        films_data.append(film_data)

    return jsonify(films_data)

@app.route('/films_and_actors', methods=['GET'])
def get_films_and_actors():
    query = (
        db.session.query(
            Film.film_id,
            Film.title,
            Film.description,
            Film.release_year,
            Language.name.label('language_name'),
            Film.rental_duration,
            Film.rental_rate,
            Film.length,
            Film.rating,
            Film.special_features,
            func.count(Rental.rental_id).label('rental_count'),
            Actor.first_name,
            Actor.last_name,
            Category.name.label('category_name')
        )
        .join(Language, Film.language_id == Language.language_id)
        .join(FilmActor, Film.film_id == FilmActor.film_id)
        .join(Actor, FilmActor.actor_id == Actor.actor_id)
        .join(Inventory, Film.film_id == Inventory.film_id)
        .join(Rental, Inventory.inventory_id == Rental.inventory_id)
        .join(FilmCategory, Film.film_id == FilmCategory.film_id)
        .join(Category, FilmCategory.category_id == Category.category_id)
        .group_by(
            Film.film_id,
            Film.title,
            Film.description,
            Film.release_year,
            Language.name,
            Film.rental_duration,
            Film.rental_rate,
            Film.length,
            Film.rating,
            Film.special_features,
            Actor.first_name,
            Actor.last_name,
            Category.name
        )
    )
    
    films_data = {}
    
    for row in query.all():
        film_id = row.film_id
        if film_id not in films_data:
            films_data[film_id] = {
                'film_id': film_id,
                'title': row.title,
                'description': row.description,
                'release_year': row.release_year,
                'language_name': row.language_name,
                'rental_duration': row.rental_duration,
                'rental_rate': float(row.rental_rate),
                'length': row.length,
                'rating': row.rating,
                'special_features': row.special_features,
                'rental_count': row.rental_count,
                'actors': [],
                'categories': []
            }
        
        films_data[film_id]['actors'].append({
            'first_name': row.first_name,
            'last_name': row.last_name
        })
        
        films_data[film_id]['categories'].append(row.category_name)

    films_and_actors = list(films_data.values())
    
    return jsonify(films_and_actors)

@app.route('/top_actors', methods=['GET'])
def top_actors_and_movies():
    top_actors = db.session.query(
        Actor.actor_id,
        Actor.first_name,
        Actor.last_name,
        db.func.count(FilmActor.film_id).label('films_featured_in'),
    ).join(
        FilmActor, Actor.actor_id == FilmActor.actor_id
    ).group_by(
        Actor.actor_id,
        Actor.first_name,
        Actor.last_name
    ).order_by(
        db.func.count(FilmActor.film_id).desc()
    ).limit(5).all()

    result = []

    for actor in top_actors:
        actor_data = {
            'actor_id': actor.actor_id,
            'first_name': actor.first_name,
            'last_name': actor.last_name,
            'films_featured_in': actor.films_featured_in,
            'top_movies': []
        }

        top_movies = db.session.query(
            Film.film_id,
            Film.title,
            Film.description,
            Film.release_year,
            Language.name,
            Film.rental_duration,
            Film.rental_rate,
            Film.length,
            Film.rating,
            Film.special_features,
            Film.last_update,
            db.func.count(Rental.rental_id).label('rental_count')
        ).join(
            FilmActor, Film.film_id == FilmActor.film_id
        ).join(
            Inventory, Film.film_id == Inventory.film_id
        ).join(
            Language, Film.language_id == Language.language_id
        ).join(
            Rental, Inventory.inventory_id == Rental.inventory_id
        ).filter(
            FilmActor.actor_id == actor.actor_id
        ).group_by(
            Film.film_id,
            Film.title,
            Film.description,
            Film.release_year,
            Language.name,
            Film.rental_duration,
            Film.rental_rate,
            Film.length,
            Film.rating,
            Film.special_features,
            Film.last_update,
        ).order_by(
            db.func.count(Rental.rental_id).desc()
        ).limit(5).all()

        actor_data['top_movies'] = [
            {
                'film_id': movie.film_id,
                'title': movie.title,
                'description': movie.description,
                'release_year': movie.release_year,
                'language_name': movie.name,
                'rental_duration': movie.rental_duration,
                'rental_rate': float(movie.rental_rate),
                'length': movie.length,
                'rating': movie.rating,
                'special_features': movie.special_features,
                'last_update': movie.last_update,
                'rental_count': movie.rental_count
            }
            for movie in top_movies
        ]

        result.append(actor_data)

    return jsonify(result)

@app.route('/top_movies', methods=['GET'])
def get_top5_most_rented_movies():
    query = (
        db.session.query(
            Film.film_id,
            Film.title,
            Film.description,
            Film.release_year,
            Language.name,
            Film.rental_duration,
            Film.rental_rate,
            Film.length,
            Film.rating,
            Film.special_features,
            Film.last_update,
            func.count(Rental.rental_id).label('rental_count')
        )
        .join(Inventory, Film.film_id == Inventory.film_id)
        .join(Rental, Inventory.inventory_id == Rental.inventory_id)
        .join(Language, Film.language_id == Language.language_id)
        .group_by(Film.film_id, Film.title, Film.description, Film.release_year, Language.name, Film.language_id,
                  Film.rental_duration, Film.rental_rate, Film.length, Film.rating, Film.special_features)
        .order_by(func.count(Rental.rental_id).desc())
        .limit(5)
    )

    result = query.all()

    movies = [
        {
            'film_id': row.film_id,
            'title': row.title,
            'description': row.description,
            'release_year': row.release_year,
            'language_name': row.name,
            'rental_duration': row.rental_duration,
            'rental_rate': float(row.rental_rate),
            'length': row.length,
            'rating': row.rating,
            'special_features': row.special_features,
            'rental_count': row.rental_count,
            'last_update': row.last_update
        }
        for row in result
    ]

    return jsonify(movies)

if __name__ == "__main__":
    app.run(debug=True)
