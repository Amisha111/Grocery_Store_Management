from .database import db

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String)
    password= db.Column(db.String)
    role = db.Column(db.String, default='USER')
    email = db.Column(db.String, unique=True)

class Orders(db.Model):
    __tablename__ = 'orders'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    order_num = db.Column(db.String, unique = False)
    user_name = db.Column(db.String)
    date = db.Column(db.String, unique=False)
    product_name = db.Column(db.String, unique = False)
    quantity = db.Column(db.Integer, unique=False)
    units = db.Column(db.String, unique=False)
    unit_price = db.Column(db.Integer, unique=True)
    total_product_amount = db.Column(db.Integer, unique=True)
    total_amount = db.Column(db.Integer, unique=True)

class Products(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    category = db.Column(db.String, db.ForeignKey('categories.category_name'), unique=True)
    product_name = db.Column(db.String, unique=True)
    units = db.Column(db.String, unique=False)
    stock = db.Column(db.Integer, unique=False)
    maxUnits= db.Column(db.Integer, unique=False)
    unit_price = db.Column(db.Integer, unique=False)
    description = db.Column(db.String, unique=False)
    image = db.Column(db.BLOB, unique=True)
    expiryDate = db.Column(db.String, unique=False)


class Categories(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    category_name = db.Column(db.String, unique = True)
    description = db.Column(db.String, unique=False)
    category_products = db.relationship("Products", backref='categories', lazy=True, cascade='all, delete')

