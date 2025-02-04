from flask import Flask, request, render_template, session, flash, redirect, url_for
import numpy as np
import joblib
import psycopg2

app = Flask(__name__)
app.secret_key = "soil"

# Load the trained model and scaler
model_path = "regression_model_fertility.pkl"
scaler_path = "scaler_fertility.pkl"

try:
    model = joblib.load(model_path)
    scaler = joblib.load(scaler_path)
except Exception as e:
    print(f"Error loading model or scaler: {e}")


def connect_to_db():
    try:
        return psycopg2.connect(
            user="postgres",
            password="Joel@123",
            host="localhost",
            port=5432,
            database="soil"
        )
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None


def create_table():
    conn = connect_to_db()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    category VARCHAR(50) NOT NULL,
                    price DECIMAL(10, 2) NOT NULL,
                    quantity INT NOT NULL,
                    farmer_name VARCHAR(100) NOT NULL,
                    contact VARCHAR(20) NOT NULL
                )
            """)
            conn.commit()
        except Exception as e:
            print(f"Error creating table: {e}")
        finally:
            cur.close()
            conn.close()


def recommend_crop(fertility_score):
    crop_recommendations = {
        (0, 10): ["Finger_Millet", "Pearl_Millet", "Sorghum", "Green_Gram", "Black_Gram"],
        (10, 12): ["Rice", "Wheat", "Maize", "Barley", "Cotton"],
        (12, float("inf")): ["Sugarcane", "Tomato", "Spinach", "Cauliflower", "Banana", "Mango", "Citrus"]
    }
    for (low, high), crops in crop_recommendations.items():
        if low <= fertility_score < high:
            return crops
    return []

def recommend_fertilizer(crop):
    # Fertilizer recommendations data
    fertilizer_recommendations = {
        "Rice": "Urea: 100kg/ha, DAP: 50kg/ha, Potash: 50kg/ha",
        "Wheat": "Urea: 120kg/ha, DAP: 60kg/ha, Potash: 40kg/ha",
        "Maize": "Urea: 150kg/ha, DAP: 75kg/ha, Potash: 60kg/ha",
        "Barley": "Urea: 80kg/ha, DAP: 40kg/ha, Potash: 30kg/ha",
        "Finger_Millet": "Urea: 90kg/ha, DAP: 45kg/ha, Potash: 23kg/ha",
        "Pearl_Millet": "Urea: 100kg/ha, DAP: 50kg/ha, Potash: 40kg/ha",
        "Sorghum": "Urea: 80kg/ha, DAP: 40kg/ha, Potash: 30kg/ha",
        "Green_Gram": "Urea: 20kg/ha, DAP: 40kg/ha, Potash: 20kg/ha",
        "Black_Gram": "Urea: 20kg/ha, DAP: 35kg/ha, Potash: 15kg/ha",
        "Sugarcane": "Urea: 250kg/ha, DAP: 100kg/ha, Potash: 150kg/ha",
        "Tomato": "Urea: 200kg/ha, DAP: 100kg/ha, Potash: 80kg/ha",
        "Spinach": "Urea: 50kg/ha, DAP: 25kg/ha, Potash: 30kg/ha",
        "Cauliflower": "Urea: 150kg/ha, DAP: 75kg/ha, Potash: 60kg/ha",
        "Banana": "Urea: 300kg/ha, DAP: 150kg/ha, Potash: 200kg/ha",
        "Mango": "Urea: 200kg/tree/year, DAP: 100kg/tree/year, Potash: 150kg/tree/year",
        "Citrus": "Urea: 250kg/ha, DAP: 120kg/ha, Potash: 150kg/ha",
        "Cotton": "Urea: 120kg/ha, DAP: 60kg/ha, Potash: 50kg/ha",
        "Potato": "Urea: 200kg/ha, DAP: 100kg/ha, Potash: 150kg/ha",
        "Onion": "Urea: 150kg/ha, DAP: 80kg/ha, Potash: 120kg/ha",
        "Carrot": "Urea: 120kg/ha, DAP: 60kg/ha, Potash: 90kg/ha",
        "Chili": "Urea: 120kg/ha, DAP: 60kg/ha, Potash: 80kg/ha",
        "Groundnut": "Urea: 20kg/ha, DAP: 40kg/ha, Potash: 20kg/ha",
        "Soybean": "Urea: 30kg/ha, DAP: 50kg/ha, Potash: 30kg/ha",
        "Pigeon Pea": "Urea: 20kg/ha, DAP: 40kg/ha, Potash: 20kg/ha",
        "Mustard": "Urea: 100kg/ha, DAP: 50kg/ha, Potash: 40kg/ha",
        "Sunflower": "Urea: 80kg/ha, DAP: 40kg/ha, Potash: 50kg/ha",
        "Cabbage": "Urea: 150kg/ha, DAP: 75kg/ha, Potash: 100kg/ha",
    }
    return fertilizer_recommendations.get(crop, "Fertilizer data not available")



@app.route("/")
def login():
    return render_template("registration.html")


@app.route("/login")
def register():
    return render_template("login.html")


@app.route('/add_users', methods=['POST'])
def add_users():
    name = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')

    conn = connect_to_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO login(name, email, password)
                VALUES(%s, %s, %s)
            """, (name, email, password))
            conn.commit()
            session['user_name'] = name
            session['user_email'] = email
            flash("Registration successful!", "success")
        except Exception as e:
            flash(f"Error adding user: {e}", "danger")
        finally:
            cursor.close()
            conn.close()

    return redirect('/')


@app.route('/login_validation', methods=['POST'])
def login_validation():
    email = request.form.get('email')
    password = request.form.get('password')

    conn = connect_to_db()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, name FROM login WHERE email = %s AND password = %s", (email, password))
            user = cursor.fetchone()

            if user:
                session['user_id'] = user[0]
                session['user_name'] = user[1]
                return redirect('/starter')
            else:
                flash('Invalid email or password', 'danger')
        finally:
            cursor.close()
            conn.close()

    return redirect('/')


@app.route('/starter')
def starter():
    if 'user_name' in session:
        return render_template("home.html")
    flash('Please log in first.', 'warning')
    return redirect('/')

@app.route("/fertility")
def fertility():
    return render_template("form.html")


@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        pname = request.form['pname']
        category = request.form['category']
        price = request.form['price']
        quantity = request.form['quantity']
        farmer_name = request.form['farmer_name']
        contact = request.form['contact']

        conn = connect_to_db()
        cur = conn.cursor()
        cur.execute(
                    "INSERT INTO products (pname, category, price, quantity, farmer_name, contact) VALUES (%s, %s, %s, %s, %s, %s)",
                    (pname, category, price, quantity, farmer_name, contact)
        )
        conn.commit()

        cur.close()
        conn.close()

        return redirect(url_for('view_products'))

    return render_template('add_product.html')


@app.route('/products')
def view_products():
    conn = connect_to_db()
    products = []
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT * FROM products")
            products = cur.fetchall()
        except Exception as e:
            flash(f"Error fetching products: {e}", "danger")
        finally:
            cur.close()
            conn.close()

    return render_template('products.html', products=products)


@app.route("/predict", methods=["POST"])
def predict():
    try:
        # Collecting input features from form
        input_features = [
            float(request.form["Soil_pH"]),
            float(request.form["Nitrogen"]),
            float(request.form["Phosphorus"]),
            float(request.form["Potassium"]),
            float(request.form["Temperature"]),
            float(request.form["Rainfall"]),
            float(request.form["Humidity"]),
        ]

        # Transform input for the model
        new_input = np.array([input_features])
        new_input_scaled = scaler.transform(new_input)
        fertility_score = model.predict(new_input_scaled)[0]

        # Getting recommendations
        crops = recommend_crop(fertility_score)  # List of recommended crops
        fertilizer_recommendations = {
            crop: recommend_fertilizer(crop) for crop in crops
        }

        # Redirecting to the results page with data
        return render_template(
            "results.html",
            fertility_score=f"{fertility_score:.2f}",
            crops=crops,
            fertilizers=fertilizer_recommendations
        )
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
        return redirect("/form")  # Redirecting back to the form in case of error

@app.route("/fertilizer_recommendation", methods=["POST", "GET"])
def fertilizer_recommendation():
    try:
        if request.method == "POST":
            recommended_crops = request.form.getlist("recommended_crops")  # List from the form
            fertilizer_data = {crop: recommend_fertilizer(crop) for crop in recommended_crops}

            return render_template(
                "fertilizer_recommendation.html",
                fertilizers=fertilizer_data
            )
        else:
            return redirect("/starter")  # Redirect if accessed via GET
    except Exception as e:
        flash(f"Error: {str(e)}", "danger")
        return redirect("/starter")

@app.route("/market_prices")
def market_prices():
    # Example data for crops/vegetables
    crops_data = [
        {"name": "Tomato", "price": "₹40/kg", "image": "/static/images/tomato.jpg"},
        {"name": "Potato", "price": "₹25/kg", "image": "/static/images/potato.jpg"},
        {"name": "Onion", "price": "₹30/kg", "image": "/static/images/onion.jpg"},
        {"name": "Carrot", "price": "₹50/kg", "image": "/static/images/carrot.jpg"},
        {"name": "Spinach", "price": "₹20/bundle", "image": "/static/images/spinach.jpg"},
        {"name": "Brinjal", "price": "₹40/bundle", "image": "/static/images/brinjal.jpg"},
        {"name": "Apple", "price": "₹120/bundle", "image": "/static/images/apple.jpg"},
        {"name": "Orange", "price": "₹120/bundle", "image": "/static/images/orange.jpg"},
    ]
    return render_template("market_prices.html", crops=crops_data)



@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)
