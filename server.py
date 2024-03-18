# Import necessary modules new commit
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func , or_
from flask_cors import CORS
from datetime import datetime

# Create Flask app
app = Flask(__name__)

# Configure SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:great-days321@localhost:3306/sakila'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
CORS(app)

# Define Actor model
class Actor(db.Model):
    __tablename__ = 'actor'
    actor_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(45))
    last_name = db.Column(db.String(45))
    last_update = db.Column(db.DateTime)

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
    def serialize(self):
        return {
            'film_id': self.film_id,
            'title': self.title,
            'description': self.description,
            'release_year': self.release_year,
            # Add other attributes as needed
        }

class Language(db.Model):
    __tablename__ = 'language'

    language_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    last_update = db.Column(db.DateTime, default=db.func.now(), onupdate=db.func.now())

class Inventory(db.Model):
    __tablename__ = 'inventory'

    inventory_id = db.Column(db.Integer, primary_key=True)
    film_id = db.Column(db.Integer, db.ForeignKey('film.film_id'))
    store_id = db.Column(db.Integer, db.ForeignKey('store.store_id'))
    last_update = db.Column(db.DateTime)

    rentals = db.relationship('Rental', backref='inventory')

class Rental(db.Model):
    __tablename__ = 'rental'

    rental_id = db.Column(db.Integer, primary_key=True)
    rental_date = db.Column(db.DateTime)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.inventory_id'))
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'))
    return_date = db.Column(db.DateTime)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.staff_id'))
    last_update = db.Column(db.DateTime)

    customer = db.relationship('Customer', backref='rentals')

class FilmActor(db.Model):
    __tablename__ = 'film_actor'

    actor_id = db.Column(db.Integer, db.ForeignKey('actor.actor_id'), primary_key=True)
    film_id = db.Column(db.Integer, db.ForeignKey('film.film_id'), primary_key=True)
    last_update = db.Column(db.DateTime, nullable=False)

class Category(db.Model):
    __tablename__ = 'category'

    category_id = db.Column(db.SmallInteger, primary_key=True, autoincrement=True)
    name = db.Column(db.String(25), nullable=False)

class FilmCategory(db.Model):
    __tablename__ = 'film_category'

    film_id = db.Column(db.Integer, db.ForeignKey('film.film_id'), primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.category_id'), primary_key=True)
    last_update = db.Column(db.DateTime)
    film = db.relationship('Film', backref=db.backref('film_categories'))
    category = db.relationship('Category', backref=db.backref('film_categories'))

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
   # Define relationships
    store = db.relationship('Store', backref='customers', foreign_keys=[store_id])
    address = db.relationship('Address', backref='customer', foreign_keys=[address_id])

class Address(db.Model):
    __tablename__ = 'address'

    address_id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(50))
    address2 = db.Column(db.String(50))
    district = db.Column(db.String(20))
    city_id = db.Column(db.Integer, db.ForeignKey('city.city_id'))
    postal_code = db.Column(db.String(10))
    phone = db.Column(db.String(20))
    last_update = db.Column(db.String(50))

    # Define relationship to City table
    city = db.relationship("City", back_populates="addresses")

class City(db.Model):
    __tablename__ = 'city'

    city_id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(50))
    country_id = db.Column(db.Integer, db.ForeignKey('country.country_id'))
    last_update = db.Column(db.String(50))

    # Define relationship to Country table
    country = db.relationship("Country", back_populates="cities")
    addresses = db.relationship("Address", back_populates="city")

class Country(db.Model):
    __tablename__ = 'country'

    country_id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(50))
    last_update = db.Column(db.String(50))

    # Define relationship to City table
    cities = db.relationship("City", back_populates="country")

class Store(db.Model):
    __tablename__ = 'store'

    store_id = db.Column(db.Integer, primary_key=True)
    manager_staff_id = db.Column(db.Integer, db.ForeignKey('staff.staff_id'))
    address_id = db.Column(db.Integer, db.ForeignKey('address.address_id'))
    last_update = db.Column(db.DateTime)

    # Define relationships
    manager = db.relationship('Staff', backref='managed_store', foreign_keys=[manager_staff_id])
    address = db.relationship('Address', backref='store_address', foreign_keys=[address_id])

class Staff(db.Model):
    __tablename__ = 'staff'

    staff_id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(45))
    last_name = db.Column(db.String(45))
    address_id = db.Column(db.Integer, db.ForeignKey('address.address_id'))
    email = db.Column(db.String(50))
    store_id = db.Column(db.Integer, db.ForeignKey('store.store_id'))
    active = db.Column(db.Boolean)
    username = db.Column(db.String(16))
    password = db.Column(db.String(40))
    last_update = db.Column(db.DateTime)

    # Define relationships
    address = db.relationship('Address', backref='staff', foreign_keys=[address_id])
    assigned_store = db.relationship('Store', backref='assigned_staff', foreign_keys=[store_id])

class Payment(db.Model):
    __tablename__ = 'payment'

    payment_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.customer_id'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('staff.staff_id'), nullable=False)
    rental_id = db.Column(db.Integer, db.ForeignKey('rental.rental_id'))
    amount = db.Column(db.Numeric(5, 2), nullable=False)
    payment_date = db.Column(db.DateTime, nullable=False)
    last_update = db.Column(db.DateTime, nullable=False, server_default=db.text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))

    # Define relationships
    customer = db.relationship('Customer', backref=db.backref('payments', lazy=True))
    staff = db.relationship('Staff', backref=db.backref('payments', lazy=True))
    rental = db.relationship('Rental', backref=db.backref('payments', lazy=True))

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

@app.route('/films', methods=['GET'])
def get_all_films():
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

@app.route('/search', methods=['GET'])
def search_films():
    search_term = request.args.get('keyword')

    films = db.session.query(Film).\
        join(FilmActor, Film.film_id == FilmActor.film_id).\
        join(Actor, FilmActor.actor_id == Actor.actor_id).\
        join(FilmCategory, Film.film_id == FilmCategory.film_id).\
        join(Category, FilmCategory.category_id == Category.category_id).\
        filter(or_(
            Film.title.ilike(f'%{search_term}%'),  # Search by film title
             (Actor.first_name + ' ' + Actor.last_name).ilike(f'%{search_term}%'),  # Search by actor full name
            Category.name.ilike(f'%{search_term}%')  # Search by category/genre
        )).all()

    # Convert SQLAlcheiiiimy objects to dictionaries for JSON serialization
    films_json = []
    for film in films:
        film_dict = {
            'film_id': film.film_id,
            'title': film.title,
            'description': film.description,
            'release_year': film.release_year,
            'rental_duration': film.rental_duration,
            'rental_rate': float(film.rental_rate),  # Convert Numeric to float
            'length': film.length,
            'rating': film.rating,
            'special_features': film.special_features,
            # Add more fields as needed
        }
        films_json.append(film_dict)

    return jsonify(films_json)

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

@app.route('/rental_info', methods=['GET'])
def get_rental_info():
    customer_id = request.args.get('customer_id')
    if customer_id is None:
        return jsonify({'error': 'Customer ID is required'}), 400

    rental_info = db.session.query(
        Customer.customer_id,
        Customer.first_name,
        Customer.last_name,
        Rental.rental_id,
        Rental.rental_date.label('rental_start_date'),
        Rental.return_date.label('rental_return_date'),
        Film.title.label('movie_title')
    ).join(
        Rental
    ).join(
        Inventory
    ).join(
        Film
    ).filter(
        Customer.customer_id == customer_id
    ).order_by(
        Customer.customer_id, Rental.rental_date
    ).all()

    if not rental_info:
        return jsonify({'error': 'No rental information found for the provided customer ID'}), 404

    result = []
    for row in rental_info:
        result.append({
            'customer_id': row.customer_id,
            'first_name': row.first_name,
            'last_name': row.last_name,
            'rental_id': row.rental_id,
            'rental_start_date': row.rental_start_date.isoformat(),
            'rental_return_date': row.rental_return_date.isoformat() if row.rental_return_date else None,
            'movie_title': row.movie_title
        })

    return jsonify(result)

@app.route('/rental_movie/<int:rental_id>', methods=['POST'])
def return_movie(rental_id):
   
     
    rental = Rental.query.get(rental_id)

    if rental is None:
        return jsonify({'error': 'Rental not found'}), 404

    rental.return_date = datetime.now()

    try:
        db.session.commit()
        return jsonify({'message': 'Movie returned successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        db.session.close()

@app.route('/search/customers', methods=['GET'])
def search_customers():
    search_term = request.args.get('keyword')

    # Query database to fetch required data
    customers = db.session.query(
        Customer.customer_id,
        Customer.first_name,
        Customer.last_name,
        Customer.email,
        Customer.address_id,
        Customer.active,
        Customer.create_date,
        Customer.last_update,
        Rental.rental_date.label('rental_start_date'),
        Rental.return_date.label('rental_return_date'),
        Film.title.label('movie_title')
    ).join(
        Rental, Customer.customer_id == Rental.customer_id
    ).join(
        Inventory, Rental.inventory_id == Inventory.inventory_id
    ).join(
        Film, Inventory.film_id == Film.film_id
    ).filter(
        or_(
            Customer.customer_id == search_term,  # Search by customer ID
            Customer.first_name.ilike(f'%{search_term}%'),  # Search by first name
            Customer.last_name.ilike(f'%{search_term}%')  # Search by last name
        )
    ).order_by(
        Customer.customer_id, Rental.rental_date
    ).all()

    # Convert query results to JSON format
    customers_json = []
    current_customer_id = None
    current_customer = None
    for customer in customers:
        if customer.customer_id != current_customer_id:
            # If this is a new customer, create a new customer dictionary
            if current_customer:
                # If we have previous customer data, append it to the main result
                customers_json.append(current_customer)
            current_customer_id = customer.customer_id
            current_customer = {
                'customer_id': customer.customer_id,
                'first_name': customer.first_name,
                'last_name': customer.last_name,
                'email': customer.email,
                'address_id': customer.address_id,
                'active': customer.active,
                'create_date': customer.create_date.strftime('%Y-%m-%d %H:%M:%S'),
                'last_update': customer.last_update.strftime('%Y-%m-%d %H:%M:%S'),
                'rental_history': []
            }
        # Add rental history to the current customer's rental history list
        rental = {
            'rental_start_date': customer.rental_start_date.strftime('%Y-%m-%d %H:%M:%S'),
            'rental_return_date': customer.rental_return_date.strftime('%Y-%m-%d %H:%M:%S') if customer.rental_return_date else None,
            'movie_title': customer.movie_title
        }
        current_customer['rental_history'].append(rental)

    # Append the last customer's data to the main result
    if current_customer:
        customers_json.append(current_customer)

    return jsonify(customers_json)

@app.route('/create_customer', methods=['POST'])
def create_customer():
    data = request.json
    if not all(key in data for key in ['store_id', 'first_name', 'last_name', 'email', 'address_id']):
        return jsonify({'error': 'Missing parameters'}), 400

    new_customer = Customer(
        store_id=data['store_id'],
        first_name=data['first_name'],
        last_name=data['last_name'],
        email=data['email'],
        address_id=data['address_id'],
        active=True,
        create_date=datetime.now(),
        last_update=datetime.now()
    )

    db.session.add(new_customer)
    db.session.commit()

    return jsonify({'message': 'Customer created successfully'}), 201

@app.route('/delete_customer/<customer_id>', methods=['DELETE'])
def delete_customer(customer_id):
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({'message': 'Customer not found'}), 404

    db.session.delete(customer)
    db.session.commit()

    return jsonify({'message': 'Customer deleted successfully'}), 200

@app.route('/customers-edit/<int:customer_id>', methods=['PUT'])
def edit_customer(customer_id):
    customer = Customer.query.get(customer_id)
    if not customer:
        return jsonify({'message': 'Customer not found'}), 404

    data = request.json
    if 'first_name' in data:
        customer.first_name = data['first_name']
    if 'last_name' in data:
        customer.last_name = data['last_name']
    if 'email' in data:
        customer.email = data['email']
    if 'address_id' in data:
        customer.address_id = data['address_id']
    if 'active' in data:
        customer.active = data['active']
    
    try:
        db.session.commit()
        return jsonify({'message': 'Customer updated successfully'}), 200
    except:
        db.session.rollback()
        return jsonify({'message': 'Failed to update customer'}), 500

@app.route('/available-rent', methods=['GET'])
def rent_films():
    results = db.session.query(
        Film.film_id,
        Film.title,
        Inventory.inventory_id,
        Film.rental_rate
    ).join(
        Inventory, Film.film_id == Inventory.film_id
    ).outerjoin(
        Rental, Inventory.inventory_id == Rental.inventory_id
    ).filter(
        (Rental.return_date.is_(None)) | (Rental.return_date > datetime.now())
    ).all()

    films = []
    for row in results:
        films.append({
            'film_id': row.film_id,
            'title': row.title,
            'inventory_id': row.inventory_id,
            'rental_rate': float(row.rental_rate)  # Convert Decimal to float for JSON serialization
        })

    return jsonify(films)

@app.route('/add_rental', methods=['POST'])
def add_rental():
    try:
        data = request.json
        inventory_id = data['inventory_id']
        customer_id = data['customer_id']
        staff_id = data['staff_id']
        
        # Create a new Rental object
        new_rental = Rental(
            rental_date=datetime.now(),
            inventory_id=inventory_id,
            customer_id=customer_id,
            staff_id=staff_id,
            return_date=None,  # Setting return_date to null
            last_update=datetime.now()
        )

        # Add the new rental to the database session
        db.session.add(new_rental)
        db.session.commit()

        return jsonify({'message': 'Rental added successfully.'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 400

# Run the Flask app
if __name__ == "__main__":
    app.run(debug=True)