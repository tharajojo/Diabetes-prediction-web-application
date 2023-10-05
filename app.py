# import libraries
import re
from tkinter import *
import tkinter.messagebox

import numpy as np
import psycopg2 as psycopg2
import psycopg2.extras
from flask import Flask, render_template, request, flash, session, url_for
import pickle  # Initialize the flask App

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect

app = Flask(__name__)
model = pickle.load(open('model.pkl', 'rb'))
model1 = pickle.load(open('model1.pkl', 'rb'))

conn = psycopg2.connect(database="postgres", user="postgres", password="1234abcd", host="127.0.0.1", port="5432")
cur = conn.cursor()
app.secret_key = 'cairocoders-ednalan'


# default page of our web-app
@app.route('/')
def home():
    # Check if user is loggedin
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('Home.html', username=session['username'], choice="LOGOUT")
    # User is not loggedin redirect to login page
    return render_template('Home.html', choice="LOGIN")


@app.route('/login')
def login():
    if 'loggedin' in session:
        return redirect(url_for('logout'))
    else:
        return render_template('login.html')


@app.route('/logout')
def logout():
    # Remove session data, this will log the user out
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    # Redirect to login page
    return redirect(url_for('home'))


@app.route('/register')
def register():
    return render_template('Register.html')


@app.route('/BG')
def BG():
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('Page-2.html', username=session['username'], choice="LOGOUT")
    # User is not loggedin redirect to login page
    root = tkinter.Tk()
    tkinter.Label(root, text="Error! Please login for customized meal plans.").pack()
    root.mainloop()
    return render_template('Home.html', choice="LOGIN")


@app.route('/meals')
def meals():
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('Meals.html', username=session['username'], choice="LOGOUT")
    # User is not loggedin redirect to login page
    return render_template('Meals.html', choice="LOGIN")


@app.route('/details')
def details():
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('Details.html', username=session['username'], choice="LOGOUT")
    # User is not loggedin redirect to login page
    return render_template('Details.html', choice="LOGIN")


@app.route('/nonveg')
def nonveg():
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('non-veg.html', username=session['username'], choice="LOGOUT")
    # User is not loggedin redirect to login page
    return render_template('non-veg.html', choice="LOGIN")


@app.route('/veg')
def veg():
    if 'loggedin' in session:
        # User is loggedin show them the home page
        return render_template('veg.html', username=session['username'], choice="LOGOUT")
    # User is not loggedin redirect to login page
    return render_template('veg.html', choice="LOGIN")


@app.route('/predict', methods=['POST'])
def predict():
    # For rendering results on HTML GUI
    int_features = [float(x) for x in list(request.form.values())]
    print(int_features)
    w = int_features[8]
    h = int_features[9]
    BMI = (w / (h * h)) * 10000
    final_features = int_features[:-2]
    final_features.append(BMI)
    final_features2 = [np.array(final_features)]
    print(final_features2)
    prediction = model.predict(final_features2)
    output = prediction[0]
    if output == 0:
        ch = "Not Diabetic"
    elif output == 1:
        ch = "Diabetic"
    else:
        ch = "Pre-diabetic"
    print(ch)
    return render_template('Details.html', prediction_text='class :{} '.format(ch))


@app.route('/reg', methods=['GET', 'POST'])
def reg():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        fullname = request.form['fullname']
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        age = request.form['age']
        BP = request.form['BP']
        MP = request.form['MP']
        _hashed_password = generate_password_hash(password)

        # Check if account exists using MySQL
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        account = cursor.fetchone()
        print(account)
        # If account exists show error and validation checks
        if account:
            flash('Account already exists!')
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            flash('Invalid email address!')
        elif not re.match(r'[A-Za-z0-9]+', username):
            flash('Username must contain only characters and numbers!')
        elif not username or not password or not email:
            flash('Please fill out the form!')
        else:
            # Account doesnt exists and the form data is valid, now insert new account into users table
            cursor.execute(
                "INSERT INTO users (fullname, username, age, BP, MP, password, email) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                (fullname, username, age, BP, MP, _hashed_password, email))
            conn.commit()
            flash('You have successfully registered!')
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        flash('Please fill out the form!')
    # Show registration form with message (if any)
    return render_template('register.html')


@app.route('/login1', methods=['GET', 'POST'])
def login1():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        print(password)

        # Check if account exists using MySQL
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        # Fetch one record and return result
        account = cursor.fetchone()

        if account:
            password_rs = account['password']
            print(password_rs)
            # If account exists in users table in out database
            if check_password_hash(password_rs, password):
                # Create session data, we can access this data in other routes
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                # Redirect to home page
                return redirect(url_for('home'))
            else:
                # Account doesn't exist or username/password incorrect
                flash('Incorrect username/password')
        else:
            # Account doesn't exist or username/password incorrect
            flash('Incorrect username/password')

    return render_template('login.html')


@app.route('/blood',methods=['GET', 'POST'])
def blood():
    cursor = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'BG' in request.form:
        BG = request.form['BG']
        username = session['username']
        cursor.execute('SELECT * FROM users WHERE username = %s', (username,))
        # Fetch one record and return result
        account = cursor.fetchone()
        age = account['age']
        MP = account['mp']
        BP = account['bp']
        print(age)
        bh = ""
        bf = ""
        lh = ""
        ln = ""
        dh = ""
        dn = ""
        print(BG)
        print(username)
        blood = [age,BG]
        final = [np.array(blood)]
        prediction = model1.predict(final)
        output = prediction[0]
        print(output)

        if output == 0 or output == 1 or output == 3:
            if MP == "Veg":
                if BP == "Yes -Low":
                    cursor.execute('SELECT * FROM vlslp order by random() limit 7')
                    meal = cursor.fetchone()
                    bh = meal[1]
                    bf = meal[2]
                    lh = meal[3]
                    ln = meal[4]
                    dh = meal[5]
                    dn = meal[6]
                elif BP == "Yes- High":
                    cursor.execute('SELECT * FROM vlshp order by random() limit 7')
                    meal = cursor.fetchone()
                    bh = meal[1]
                    bf = meal[2]
                    lh = meal[3]
                    ln = meal[4]
                    dh = meal[5]
                    dn = meal[6]
                else:
                    cursor.execute('SELECT * FROM vls order by random() limit 7')
                    meal = cursor.fetchone()
                    bh = meal[1]
                    bf = meal[2]
                    lh = meal[3]
                    ln = meal[4]
                    dh = meal[5]
                    dn = meal[6]
            else:
                if BP == "Yes -Low":
                    cursor.execute('SELECT * FROM nlslp order by random() limit 7')
                    meal = cursor.fetchone()
                    bh = meal[1]
                    bf = meal[2]
                    lh = meal[3]
                    ln = meal[4]
                    dh = meal[5]
                    dn = meal[6]
                elif BP == "Yes- High":
                    cursor.execute('SELECT * FROM nlshp order by random() limit 7')
                    meal = cursor.fetchone()
                    bh = meal[1]
                    bf = meal[2]
                    lh = meal[3]
                    ln = meal[4]
                    dh = meal[5]
                    dn = meal[6]
                else:
                    cursor.execute('SELECT * FROM nls order by random() limit 7')
                    meal = cursor.fetchone()
                    bh = meal[1]
                    bf = meal[2]
                    lh = meal[3]
                    ln = meal[4]
                    dh = meal[5]
                    dn = meal[6]

        elif output == 2 or output == 5:
            if MP == "Veg":
                if BP == "Yes -Low":
                    cursor.execute('SELECT * FROM vhslp order by random() limit 7')
                    meal = cursor.fetchone()
                    bh = meal[1]
                    bf = meal[2]
                    lh = meal[3]
                    ln = meal[4]
                    dh = meal[5]
                    dn = meal[6]
                elif BP == "Yes- High":
                    cursor.execute('SELECT * FROM vhshp order by random() limit 7')
                    meal = cursor.fetchone()
                    bh = meal[1]
                    bf = meal[2]
                    lh = meal[3]
                    ln = meal[4]
                    dh = meal[5]
                    dn = meal[6]
                else:
                    cursor.execute('SELECT * FROM vhs order by random() limit 7')
                    meal = cursor.fetchone()
                    bh = meal[1]
                    bf = meal[2]
                    lh = meal[3]
                    ln = meal[4]
                    dh = meal[5]
                    dn = meal[6]
            else:
                if BP == "Yes -Low":
                    cursor.execute('SELECT * FROM nhslp order by random() limit 7')
                    meal = cursor.fetchone()
                    bh = meal[1]
                    bf = meal[2]
                    lh = meal[3]
                    ln = meal[4]
                    dh = meal[5]
                    dn = meal[6]
                elif BP == "Yes- High":
                    cursor.execute('SELECT * FROM nhshp order by random() limit 7')
                    meal = cursor.fetchone()
                    bh = meal[1]
                    bf = meal[2]
                    lh = meal[3]
                    ln = meal[4]
                    dh = meal[5]
                    dn = meal[6]
                else:
                    cursor.execute('SELECT * FROM nhs order by random() limit 7')
                    meal = cursor.fetchone()
                    bh = meal[1]
                    bf = meal[2]
                    lh = meal[3]
                    ln = meal[4]
                    dh = meal[5]
                    dn = meal[6]
        else:
            if MP == "Veg":
                if BP == "Yes -Low":
                    cursor.execute('SELECT * FROM vhslp order by random() limit 7')
                    meal = cursor.fetchone()
                    bh = meal[1]
                    bf = meal[2]
                    lh = meal[3]
                    ln = meal[4]
                    dh = meal[5]
                    dn = meal[6]
                elif BP == "Yes- High":
                    cursor.execute('SELECT * FROM vhshp order by random() limit 7')
                    meal = cursor.fetchone()
                    bh = meal[1]
                    bf = meal[2]
                    lh = meal[3]
                    ln = meal[4]
                    dh = meal[5]
                    dn = meal[6]
                else:
                    cursor.execute('SELECT * FROM vhs order by random() limit 7')
                    meal = cursor.fetchone()
                    bh = meal[1]
                    bf = meal[2]
                    lh = meal[3]
                    ln = meal[4]
                    dh = meal[5]
                    dn = meal[6]
            else:
                if BP == "Yes -Low":
                    cursor.execute('SELECT * FROM nhslp order by random() limit 7')
                    meal = cursor.fetchone()
                    bh = meal[1]
                    bf = meal[2]
                    lh = meal[3]
                    ln = meal[4]
                    dh = meal[5]
                    dn = meal[6]
                elif BP == "Yes- High":
                    cursor.execute('SELECT * FROM nhshp order by random() limit 7')
                    meal = cursor.fetchone()
                    bh = meal[1]
                    bf = meal[2]
                    lh = meal[3]
                    ln = meal[4]
                    dh = meal[5]
                    dn = meal[6]
                else:
                    cursor.execute('SELECT * FROM nhs order by random() limit 7')
                    meal = cursor.fetchone()
                    bh = meal[1]
                    bf = meal[2]
                    lh = meal[3]
                    ln = meal[4]
                    dh = meal[5]
                    dn = meal[6]
        print(bh)
        print(bf)
        print(lh)
        print(ln)
        print(dh)
        print(dn)
    """return render_template('Page-3.html',bh = bh, bf = bf,lh = lh, ln = ln, dh= dh, dn = dn,choice = "LOGOUT",username = username)"""
    return render_template('Page-3.html', bh=bh, lh=lh, dh=dh, choice="LOGOUT", username=username)
if __name__ == "__main__":
    app.run(debug=True)
