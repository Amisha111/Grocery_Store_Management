from flask import Flask, request,redirect,url_for,send_file,flash,session,jsonify
from flask import render_template
from flask import current_app as app
from application.models import User, Products, Orders, Categories
from .database import db
from io import BytesIO
import random
import datetime
import json

def clearSession():
    session.pop("user",None)
    session.pop("role",None)
    session.pop("basket",None)

    
# 1.index page routing 
@app.route("/", methods=["GET"])
def login_page():
    clearSession()
    return render_template("userLogin.html")

def userHomePageData():
    grouped_products ={}
    products = Products.query.all()
    for product in products:
        category = product.category
        if category in grouped_products:
            grouped_products[category].append(product)
        else:
            grouped_products[category] = [product]
    return grouped_products


# for each category in the list , query the products 
@app.route("/userLogin", methods=["POST"])
def login():
    clearSession()
    username = request.form['username']
    password = request.form['password'] 
    users = User.query.filter_by(name=username, role = 'USER').all()
    if (len(users) == 1):
        user = User.query.filter_by(name=username,password=password).first()
        if (user is None):
            flash('No such user or invalid password!!!', category='danger')
            return render_template("userLogin.html")
        else:
           if (user.role == "USER"):
               session["user"] = username
               session["role"] = 'USER'
               session["basket"] =[] 
            #persist the details of the basket in the session , before logging out . check if there are any issues while persisting.
               return render_template("userHome.html",products = userHomePageData(),error = 0)  
           else:
            flash('No such user or invalid password!!!', category='danger')
            return render_template("userLogin.html")
    else:
        flash('No such user or invalid password!!!', category='danger')
        return render_template("userLogin.html")

@app.route("/userHomePage", methods=["GET"])
def userHome_page():
    return render_template("userHome.html",products = userHomePageData(),error = 0)  
    
@app.route("/register", methods=["GET"])
def signup_page():
    clearSession()  
    return render_template("userSignup.html")

    
@app.route("/userSignup", methods=["POST"])
def signup():
    clearSession()
    username = request.form['username']
    password = request.form['password'] 
    email = request.form['email']
    users = User.query.filter_by(name=username,role = 'USER').all()
    if (len(users) == 1):
        flash('User already exists', category='danger')
        return render_template("userSignup.html")  
    else:
        user = User(name=username,password=password,email=email)
        db.session.add(user)
        db.session.commit()
        session["user"] = username
        session["role"] = 'USER'
        session["basket"] =[]
    return render_template("userHome.html",products = userHomePageData(),error = 0)  


@app.route("/admin", methods=["GET"])
def adminLogin_page():
    clearSession()
    return render_template("adminLogin.html")



@app.route("/adminLogin", methods=["POST"])
def adminLogin():
    clearSession() 
    username = request.form['username']
    password = request.form['password'] 
    users = User.query.filter_by(name=username, role = 'ADMIN').all()
    if (len(users) == 1):
        user = User.query.filter_by(name=username,password=password).first()
        if (user is None):
            flash('No such user or invalid password!!!', category='danger')
            return render_template("adminLogin.html")
        else:
           if (user.role == "ADMIN"):
               session["user"] = username
               session["role"] = 'ADMIN'
               return render_template("adminHome.html")
           else:
            flash('No such user or invalid password!!!', category='danger')
            return render_template("adminLogin.html")
    else:
        flash('No such user or invalid password!!!', category='danger')
        return render_template("adminLogin.html")


@app.route("/adminCategories",methods=["GET"])
def categories_page():
    category_list=Categories.query.all()
    return render_template("adminCategory.html",categories = category_list)

@app.route("/addNewCategory",methods=["POST"])
def addCategory():
    category = request.form['category']
    description = request.form['description'] 
    categories = Categories.query.filter_by(category_name=category).all()
    if (len(categories) == 1 or len(categories) >= 1):
        flash('Category Already Exists!!', category='danger')
        return redirect(url_for("categories_page"))  
    else:
        category = Categories(category_name=category,description = description)
        db.session.add(category)
        db.session.commit()
    return redirect(url_for("categories_page"))  


@app.route('/editCategory', methods=["POST"])
def editCategory():
    id = request.form['id']
    category = Categories.query.filter_by(id=id).first() 
    print(category)
    category.category_name = request.form['edit_category_name']
    category.description = request.form['edit_description']
    print(category.category_name)
    print(category.description)
    db.session.commit()
    return redirect(url_for("categories_page"))  


@app.route('/deleteCategory', methods=["POST"])
def deleteCategory():
    id = request.form['id']
    category = Categories.query.filter_by(id=id).first() 
    db.session.delete(category)
    db.session.commit()
    return redirect(url_for("categories_page"))  


@app.route("/adminProducts",methods=["GET"])
def products_page():
    products_list=Products.query.all()
    category_list=Categories.query.all()
    return render_template("adminProducts.html",products = products_list, categories= category_list)


@app.route("/addNewProduct", methods=["POST"])
def addProduct():  
    category = request.form['category'] 
    product_name = request.form['product_name']
    units = request.form['units'] 
    stock = request.form['stock'] 
    maxUnits = request.form['max_units'] 
    unit_price = request.form['unit_price'] 
    description = request.form['description']
    expiry_date = request.form['expiry_date']
    image =  request.files['image']
    blob = image.read()
    products = Products.query.filter_by(category=category, product_name=product_name).first()
    if (products is None):
       new_product = Products(category=category,product_name=product_name,units = units, stock = stock,maxUnits= maxUnits, unit_price=unit_price,  description=description,expiryDate= expiry_date, image=blob)
       db.session.add(new_product)
       db.session.commit()
       return redirect(url_for("products_page"))
    else:
        flash('Product already exists!!!', category='danger')
        return redirect(url_for("products_page"))

@app.route('/editProduct', methods=["POST"])
def editProduct():
    id = request.form['id']
    product = Products.query.filter_by(id=id).first() 
    existing_image = product.image
    product.category=request.form['edit_category'] 
    product.product_name=request.form['edit_product_name']
    product.units = request.form['edit_units'] 
    product.stock = request.form['edit_stock'] 
    product.maxUnits= request.form['edit_max_units'] 
    product.unit_price=request.form['edit_unit_price'] 
    product.description=request.form['edit_description']
    expirydate = request.form['edit_expiry_date']
    if(expirydate):
        product.expiryDate= expirydate
    image = request.files.get('edit_image')
    if(image):
        product.image = image.read()
    else:
        product.image = existing_image
    db.session.commit()
    return redirect(url_for("products_page"))

@app.route('/deleteProduct', methods=["POST"])
def deleteProduct():
    id = request.form['id']
    product = Products.query.filter_by(id=id).first() 
    db.session.delete(product)
    db.session.commit()
    return redirect(url_for("products_page"))


@app.route('/addToCart', methods=["POST"])
def addToCart():
    item = request.get_json()
    print("item")
    print(item.get('product_name'))
    cart = session.get('basket', [])
    print(cart)
    prod_del = item.get('product_name')
    cart = [product for product in cart if product.get('product_name') != prod_del]
    cart.append(item)
    session['basket'] = cart
    return jsonify(message='success')


@app.route('/userCart', methods=["GET"])
def cartPage():
    cart = session.get('basket', [])
    total = sum(item["totalamount"] for item in cart)  # Calculate the total of prices
    return render_template("cartPage.html", cart= cart, total = total)

# @app.route('/orderPage', methods=["GET"])
# def orderPage():
#     user_orders_list = Orders.query.filter_by(user_name=session.get('user')).all()
#     print(user_orders_list)
#     grouped_products={}
#     for order in user_orders_list:
#         if order.order_num in grouped_products:
#             grouped_products[order.order_num].append(order)
#         else:
#             grouped_products[order.order_num] = [order]
#     print(user_orders_list)
#     return render_template("orderPage.html", orders= user_orders_list , orderlist = grouped_products)


@app.route('/orderPage', methods=["GET"])
def orderPage():
    user_orders_list = Orders.query.filter_by(user_name=session.get('user')).all()
    print(user_orders_list)
    grouped_products={}
    for order in user_orders_list:
        if order.order_num in grouped_products:
            grouped_products[order.order_num].append(order)
        else:
            grouped_products[order.order_num] = [order]
    print(user_orders_list)
    return render_template("orderPage.html", orderlist = grouped_products)

@app.route('/searchCategories',methods=['POST'])
def searchCategory():
    search = request.form['search']
    query = request.form['query']
    filter = request.form['filter']
    sort = request.form['sort']
    print(filter)
    print(sort)
    like_query = "%"+query+"%"
    grouped_products ={}
    if(search =="Category"):
        categories_list = Categories.query.with_entities(Categories.category_name).filter(Categories.category_name.like(like_query)).all()
        results_size = len(categories_list)
        if(results_size == 0):
            return render_template("userHome.html",error=1) 
        else:
            categories_list = [row[0] for row in categories_list]
            for category in categories_list:
                print(category)
                if(filter == 'Price' and sort =='Highest'):
                    product = Products.query.filter_by(category=category).order_by(Products.unit_price.desc()).all() 
                elif(filter == 'Price'):
                    product = Products.query.filter_by(category=category).order_by(Products.unit_price).all() 
                elif(filter == 'ExpiryDate' and sort =='Highest'):
                    product = Products.query.filter_by(category=category).order_by(Products.expiryDate.desc()).all() 
                else:
                    product = Products.query.filter_by(category=category).order_by(Products.expiryDate).all() 

                for prod in product:
                    if category in grouped_products:
                        grouped_products[category].append(prod)
                    else:
                        grouped_products[category] = [prod]
    else:
        if(filter == 'Price' and sort =='Highest'):
            products_list = Products.query.filter(Products.product_name.like(like_query)).order_by(Products.unit_price.desc()).all() 
        elif(filter == 'Price'):
            products_list = Products.query.filter(Products.product_name.like(like_query)).order_by(Products.unit_price).all() 
        elif(filter == 'ExpiryDate' and sort =='Highest'):
            products_list = Products.query.filter(Products.product_name.like(like_query)).order_by(Products.expiryDate.desc()).all() 
        else:
            products_list = Products.query.filter(Products.product_name.like(like_query)).order_by(Products.expiryDate).all()
        results_size = len(products_list)
        if(results_size == 0):
            return render_template("userHome.html",error=1) 

        else:
            for product in products_list:
                category = product.category
                if category in grouped_products:
                    grouped_products[category].append(product)
                else:
                    grouped_products[category] = [product]
    return render_template("userHome.html",products = grouped_products, query = query,search = search,error = 0) 





@app.route('/order', methods=["GET"])
def order():
    username = session.get('user')
    basket = session.get('basket')
    total = sum(item["totalamount"] for item in basket)
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    numbers = "0123456789"
    transactionId = []
    for _ in range(6):
        index = random.randint(0, len(numbers) - 1)
        transactionId.append(numbers[index])
        transaction_id = 'TXN-'+"".join(transactionId)
    for item in basket:
        id = item.get('id')
        quantity= item.get('quantity')
        product = Products.query.filter_by(id=id).first()
        print(product.stock)
        product.stock = product.stock-quantity
        print(product.stock)
        db.session.commit()
        unit_price = item.get('unit_price')
        tpa = float(unit_price)*int(quantity)
        new_order = Orders(order_num=transaction_id,user_name=username,date=date,product_name=item.get('product_name'),quantity = quantity,units = item.get('units'),
                           unit_price = unit_price,
                           total_product_amount= tpa,
                             total_amount = total)
        db.session.add(new_order)
        db.session.commit()
    session.pop("basket",None)
    return redirect(url_for("orderPage"))  



@app.route('/logout', methods=["GET"])
def logout():
    if "role" in session:
        role = session["role"]
        if role =="ADMIN":
            clearSession()
            return render_template("adminLogin.html")
        else:
            clearSession()
            return render_template("userLogin.html")
    clearSession()
    return render_template("userLogin.html")

@app.route('/productImage/<product>')
def renderImage(product):
    image = Products.query.with_entities(Products.image).filter_by(product_name=product).first()
    for i in image:
        return send_file(
        BytesIO(i),
        download_name=product
    )





    


    