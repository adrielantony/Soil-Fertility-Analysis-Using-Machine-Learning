from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database Connection Configuration
def get_db_connection():
    return pymysql.connect(
        host='localhost',  
        user='root',       
        password='Varsha', 
        database='Register',  
        cursorclass=pymysql.cursors.DictCursor  
    )


@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

       
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return render_template('registration.html')

       
        try:
            conn = get_db_connection()
            cur = conn.cursor()

          
            query = "SELECT * FROM `register_page` WHERE `email` = %s"
            cur.execute(query, (email,))
            existing_user = cur.fetchone()

            if existing_user:
                flash('Email is already registered!', 'error')
            else:
                
                insert_query = "INSERT INTO `register_page` (`username`, `email`, `password`) VALUES (%s, %s, %s)"
                cur.execute(insert_query, (username, email, password))  # Store plain password
                conn.commit()  # Commit the transaction
                flash('Registration completed successfully!', 'success')
                return redirect(url_for('login'))
        
        except pymysql.MySQLError as e:
            flash(f"An error occurred: {str(e)}", 'error')
        finally:
            conn.close()  
    
    return render_template('registration.html')


# Route for Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        try:
            connection = get_db_connection()
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT * FROM register_page WHERE email = %s",  
                    (email,)
                )
                user = cursor.fetchone()  
                
                if user:
                    # Directly compare the plain-text password
                    if password == user['password']:
                        flash('Logged in successfully!', 'success')
                        return render_template('login.html', logged_in=True)  
                    else:
                        flash('Invalid password!', 'error') 
                else:
                    flash('Email not found!', 'error')
        except Exception as e:
            flash(f"An error occurred: {str(e)}", 'error')
        finally:
            connection.close() 
    
    return render_template('login.html', logged_in=False)


if __name__ == '__main__':
    app.run(debug=True)
