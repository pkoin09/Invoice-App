# from distutils import debug
from flask import Flask, flash, redirect, render_template, request, session, send_file, url_for, abort
from flask_session import Session
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash

# additional libraries
from datetime import datetime
from weasyprint import HTML

from helpers import apology, login_required, usd

# key = environ.get('SECRET_KEY')

app = Flask(__name__)

# remove
app.config["ENV"] = "development"
app.config["DEBUG"] = True

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# database
# change line #38 to invoice.db to allow storage as shown in line #37
# with sqlite3.connect("invoice.db", check_same_thread=False) as conn:
with sqlite3.connect(":memory:", check_same_thread=False) as conn:
    c = conn.cursor()


    @app.after_request
    def after_request(response):
        """Ensure responses aren't cached"""
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"
        return response


    @app.route("/")
    def index():
        return render_template("index.html")


    @app.route("/admin", methods=["GET", "POST"])
    @login_required
    def admin():
        user_id = session["user_id"]

        if request.method == "GET":
            if user_id == 1:
                # get all staff members to present to admin view
                c.execute(
                    "SELECT username, permission, role FROM users INNER JOIN roles ON users.role = roles.role_id;"
                )
                rows = c.fetchall()

                # get roles
                c.execute("SELECT * FROM roles;")
                roles = c.fetchall()

                return render_template("admin.html", rows=rows, roles=roles)
            else:
                flash("must be staff to access", "error")
                return redirect("/")
        else:
            staff = request.form.get("staff")
            role = request.form.get("role")

            c.execute("SELECT username FROM users WHERE user_id = ?", (user_id,))
            users = c.fetchone()
            username = users[0]

            try:
                if not username == staff:
                    c.execute("UPDATE users SET role = ? WHERE username = ?", (role, staff))
                    conn.commit()

                    # get all staff members roles
                    c.execute(
                        "SELECT username, permission, role FROM users INNER JOIN roles ON users.role = roles.role_id"
                    )
                    rows = c.fetchall()

                    # get roles
                    c.execute("SELECT * FROM roles;")
                    roles = c.fetchall()

                    return render_template("admin.html", rows=rows, roles=roles)
                else:
                    raise TypeError

            except TypeError:
                return apology("cannot change admin roles", 401)


    @app.route("/login", methods=["GET", "POST"])
    def login():
        """Log user in"""

        # Forget any user_id
        session.clear()

        # User reached route via POST (as by submitting a form via POST)
        if request.method == "POST":
            # check if users table exists in the database
            c.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
            )
            users_table_exists = c.fetchall()

            if users_table_exists == []:
                flash("Please register. You are the first user and will be assigned root priviledges")
                # operational error
                return render_template("register.html")

            username = request.form.get("username")
            password = request.form.get("password")

            # Ensure username was submitted
            if not username:
                flash("must provide username")
                return render_template("login.html")

            # Ensure password was submitted
            elif not password:
                flash("must provide password")
                return redirect(url_for("login"))

            # Query database for username
            c.execute(
                "SELECT * FROM users INNER JOIN roles ON users.role = roles.role_id WHERE username = ?",
                (username,)
            )
            rows = c.fetchone()

            # Ensure username exists and password is correct
            if not rows or not check_password_hash(rows[2], password):
                return apology("Could not be authenticated. please register to book services", 401)

            # Remember which user has logged in
            session["user_id"] = rows[0]
            session["role"] = rows[5]

            # Redirect user to home page
            return redirect("/booking")

        # User reached route via GET (as by clicking a link or via redirect)
        else:
            return render_template("login.html")


    @app.route("/register", methods=["GET", "POST"])
    def register():
        """Register user"""

        # forget any user_id
        session.clear()

        # user reached route via POST
        if request.method == "POST":
            user = request.form.get("username")
            password = request.form.get("password")
            confirmation = request.form.get("confirmation")

            # create table 'roles' and its values
            # check if table exists
            c.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
            )
            users_table_exists = c.fetchall()

            # ensure code runs on first run
            if users_table_exists == []:
                # create table 'users' if it doesnt exist
                c.execute(
                    "CREATE TABLE IF NOT EXISTS users (user_id INTEGER UNIQUE PRIMARY KEY, username TEXT UNIQUE NOT NULL, hash TEXT NOT NULL, role INTEGER NOT NULL)"
                )

                # create table services if it does not exist
                c.execute(
                    "CREATE TABLE IF NOT EXISTS services (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, service TEXT NOT NULL, rate INTEGER NOT NULL, description TEXT)"
                )

                # create table if it doesnt already exist
                c.execute(
                    "CREATE TABLE IF NOT EXISTS bookings (id INTEGER UNIQUE PRIMARY KEY, client_id INTEGER NOT NULL, client_name TEXT NOT NULL, email TEXT NOT NULL, attaches_name TEXT NOT NULL, date TEXT NOT NULL, invoice INTEGER NOT NULL, service TEXT NOT NULL, rate REAL NOT NULL, hours INTEGER, total INTEGER, Address TEXT NOT NULL, subtotal INTEGER, serviceId INTEGER NOT NULL, inv_num TEXT)"
                )

                # create table 'roles'
                c.execute(
                    "CREATE TABLE IF NOT EXISTS roles (role_id PRIMARY KEY UNIQUE NOT NULL, permission TEXT UNIQUE NOT NULL, FOREIGN KEY (role_id) REFERENCES users(role_id))"
                )

                # define roles
                multi_rows_roles = [
                    (0, 'default'),
                    (1, 'super'),
                    (2, 'staff'),
                ]

                # create roles
                c.executemany("INSERT INTO roles (role_id, permission) VALUES (?, ?)", (multi_rows_roles))

                # create table 'status'
                c.execute("CREATE TABLE IF NOT EXISTS status (id INTEGER PRIMARY KEY UNIQUE, invoice TEXT NOT NULL)")

                # define status
                multi_rows_status = [
                    (1, 'booked'),
                    (2, 'inprogress'),
                    (3, 'complete'),
                ]

                # create status
                c.executemany("INSERT INTO status VALUES (?, ?)", multi_rows_status)

                conn.commit()

            # Ensure user name was submitted
            if not user:
                return apology("must provide username", 403)

            # Ensure password was submitted
            elif not password:
                return apology("must provide a password", 403)

            # Ensure password and confirmation pwd match
            elif password != confirmation:
                return apology("passwords do not match", 401)

            # hash the password
            hash_number = generate_password_hash(password)

            # insert into the users table in the invoice database
            try:
                # input user values into user table
                c.execute(
                    "INSERT INTO users VALUES (NULL, ?, ?, ?)", (user, hash_number, 0)
                )
                # input into roles table
                conn.commit()

                # sets the first person to login (user_id 1) as the admin
                c.execute("UPDATE users SET role = 1 WHERE user_id = 1")
                conn.commit()
            except:
                return apology("username already exists", 400)

            # redirect to homepage
            return redirect("/login")

        # user reached route via GET
        else:
            return render_template("register.html")


    @app.route("/logout")
    def logout():
        """Log user out"""

        # Forget any user_id
        session.clear()

        # Redirect user to login form
        return redirect("/")


    @app.route("/services", methods=["GET", "POST"])
    @login_required
    def service():
        """Sevices you offer to clients"""
        # get user id
        user_id = session["user_id"]

        # create table services if it does not exist
        c.execute(
            "CREATE TABLE IF NOT EXISTS services (id INTEGER PRIMARY KEY, user_id INTEGER NOT NULL, service TEXT NOT NULL, rate INTEGER NOT NULL, description TEXT)"
        )

        if request.method == "GET":
            # get users data
            c.execute("SELECT * FROM services WHERE user_id = ?", (user_id,))
            rows = c.fetchall()

            return render_template("/services.html", rows=rows)
        else:
            # inputs from service.html
            service = request.form.get("service")
            rate = request.form.get("rate")
            description = request.form.get("description")

            # set input conditions
            if not service:
                return apology("must provide service name", 404)
            elif not rate:
                return apology("must provide service rate", 404)

            # insert into the service database
            try:
                c.execute(
                    "INSERT INTO services VALUES (NULL, ?, ?, ?, ?)",
                    (user_id, service, rate, description),
                )

                conn.commit()

                return redirect("/services")

            except (ValueError, TypeError):
                return render_template("/services.html")


    @app.route("/invoice", methods=["GET", "POST"])
    @login_required
    def invoice():
        """CREATE INVOICE"""
        # logged in user
        user_id = session["user_id"]

        # invoice date and number generators.
        now = datetime.now()
        time_stamp = now.strftime("%H%M")
        today = datetime.today().strftime("%A, %B %-d, %Y")
        date_year = datetime.today().strftime("%Y%m%d")
        invoice_number = f"inv_{date_year}-{time_stamp}"

        # business name
        from_dict = {
            "name": "Acme Consults LLC",
            "address": "456 Main St",
            "city": "City B",
            "state": "CA",
            "country": "USA",
        }

        # get username
        c.execute("SELECT username FROM users WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        username = row[0]

        if request.method == "POST":
            client_id = request.form.get("clientId")
            service_id = request.form.get("serviceId")
            rate = request.form.get("serviceRate")
            date = request.form.get("serviceDate")
            hours = request.form.get("hours")

            # get the total
            total = float(rate) * float(hours)

            # update the database
            c.execute(
                "UPDATE bookings SET hours = ?, invoice = ?, total = ? WHERE client_id = ? AND serviceId = ? AND date = ?",
                (hours, 2, total, client_id, service_id, date),
            )
            conn.commit()

            # get all bookings with invoice status inprogress
            c.execute(
                "SELECT * FROM bookings INNER JOIN users ON bookings.client_id = users.user_id WHERE attaches_name = ? AND invoice = ? AND user_id = ?",
                (username, 2, client_id),
            )
            rows = c.fetchall()

            clients = [row[2] for row in rows]

            # subtotal
            c.execute(
                "SELECT SUM(total) FROM bookings INNER JOIN users ON bookings.client_id = users.user_id WHERE attaches_name = ? AND invoice = ? AND user_id = ?",
                (username, 2, client_id),
            )
            subtotal = c.fetchone()

            return render_template(
                "invoice.html",
                date=today,
                inv=invoice_number,
                rows=rows,
                clients=clients,
                sender=from_dict,
                subtotal=subtotal[0],
            )
        # GET request
        else:
            # invoice date and number generators.
            now = datetime.now()
            time_stamp = now.strftime("%H%M")
            today = datetime.today().strftime("%A, %B %-d, %Y")
            date_year = datetime.today().strftime("%Y%m%d")
            invoice_number = f"inv_{date_year}-{time_stamp}"

            # get all bookings with invoice status inprogress
            c.execute(
                "SELECT * FROM bookings INNER JOIN users ON bookings.client_id = users.user_id WHERE attaches_name = ? AND invoice = ?",
                (username, 2),
            )
            rows = c.fetchall()

            clients = [row[2] for row in rows]

            # subtotal
            c.execute(
                "SELECT SUM(total) FROM bookings INNER JOIN users ON bookings.client_id = users.user_id WHERE attaches_name = ? AND invoice = ?",
                (username, 2),
            )
            subtotal = c.fetchone()

            return render_template(
                "invoice.html",
                date=today,
                inv=invoice_number,
                rows=rows,
                sender=from_dict,
                clients=clients,
                subtotal=subtotal[0],
            )


    @app.route("/dashboard")
    @login_required
    def dashboard():
        """USERS HISTORY"""
        # logged in user
        user_id = session["user_id"]

        # get username
        c.execute("SELECT username FROM users WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        username = row[0]

        # GET request
        if request.method == "GET":
            # create table if it doesnt already exist
            c.execute(
                "CREATE TABLE IF NOT EXISTS bookings (id INTEGER UNIQUE PRIMARY KEY, client_id INTEGER NOT NULL, client_name TEXT NOT NULL, email TEXT NOT NULL, attaches_name TEXT NOT NULL, date TEXT NOT NULL, invoice INTEGER NOT NULL, service TEXT NOT NULL, rate REAL NOT NULL, hours INTEGER, total INTEGER, Address TEXT NOT NULL, subtotal INTEGER, serviceId INTEGER NOT NULL)"
            )
            conn.commit()

            # get users services
            c.execute(
                "SELECT * FROM bookings INNER JOIN status ON bookings.invoice = status.id WHERE attaches_name = ? ORDER BY date",
                (username,),
            )
            rows = c.fetchall()

            if rows:
                rate = rows[0][8]
                hours = rows[0][9]

            else:
                # returns 0 if missing rows
                rate = hours = 0

            return render_template("/dashboard.html", rows=rows, rate=rate, hours=hours)


    @app.route("/booking")
    @login_required
    def booking():
        """SERVICES SHOWN TO ALL LOGGED IN USERS"""
        # logged in user
        user_id = session["user_id"]

        # Get username of logged in user
        c.execute("SELECT username FROM users WHERE user_id = ?", (user_id,))
        row = c.fetchone()

        if row:
            user = row[0]
        else:
            user = ""

        # get services
        if request.method == "GET":
            c.execute(
                "SELECT service, rate, username, description, id FROM SERVICES INNER JOIN users ON services.user_id = users.user_id;"
            )
            rows = c.fetchall()

            return render_template("/booking.html", rows=rows, user=user, id=user_id)


    @app.route("/thanks", methods=["GET", "POST"])
    @login_required
    def thanks():
        """THANK YOU PAGE AFTER BOOKING"""

        user_id = session["user_id"]

        if request.method == "POST":
            client_name = request.form.get("client")
            address = request.form.get("address")
            email = request.form.get("email")
            attache_name = request.form.get("attache")
            form_date = request.form.get("date")
            client_id = user_id
            service = request.form.get("service")
            serviceId = request.form.get("servId")
            rate_string = request.form.get("rate")
            rate = float(rate_string)

            # format date from the form
            try:
                serv_date = datetime.strptime(form_date, "%Y-%m-%dT%H:%M").strftime(
                    "%b/%d/%Y %I:%M %p"
                )
            except ValueError:
                return apology("No Date entered", 400)

            # add to database
            try:
                c.execute(
                    "INSERT INTO bookings VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (
                        client_id,
                        client_name,
                        email,
                        attache_name,
                        serv_date,
                        1,
                        service,
                        rate,
                        0,
                        0.00,
                        address,
                        0.00,
                        serviceId,
                        None,
                    ),
                )
                conn.commit()

                return render_template(
                    "/thanks.html",
                    client_name=client_name,
                    attache_name=attache_name,
                    serv_date=serv_date,
                    service=service,
                )
            except:
                return apology("appointment could not be created, contact company", 400)

        # redirected to index if browsed direcly
        else:
            return redirect("/booking")


    @app.route("/invoiced", methods=["GET", "POST"])
    @login_required
    def invoiced():
        """THANK YOU PAGE AFTER BOOKING"""

        user_id = session["user_id"]

        # invoice date and number generators.
        now = datetime.now()
        time_stamp = now.strftime("%H%M")
        today = datetime.today().strftime("%A, %B %-d, %Y")
        date_year = datetime.today().strftime("%Y%m%d")
        invoice_number = f"inv_{date_year}-{time_stamp}"

        # business name
        from_dict = {
            "name": "My Business",
            "address": "456 Main St",
            "city": "City B",
            "state": "CA",
            "country": "USA",
        }

        # get username
        c.execute("SELECT username FROM users WHERE user_id = ?", (user_id,))
        row = c.fetchone()
        username = row[0]

        if request.method == "POST":
            # get selected client
            client_name = request.form.get("client")

            # get users services
            c.execute(
                "SELECT * FROM bookings INNER JOIN status ON bookings.invoice = status.id WHERE attaches_name = ? AND bookings.invoice = ? AND client_name = ? ORDER BY date",
                (username, 2, client_name),
            )
            rows = c.fetchall()

            # get client info
            if rows:
                to_dict = {
                    "id": rows[0][1],
                    "name": rows[0][2],
                    "address": rows[0][11],
                    "email": rows[0][3],
                }
            else:
                to_dict = {"id": "", "name": "", "address": "", "email": ""}

            # subtotal
            c.execute(
                "SELECT SUM(total) FROM bookings INNER JOIN users ON bookings.client_id = users.user_id WHERE attaches_name = ? AND invoice = ? AND client_name = ?",
                (username, 2, client_name),
            )
            subtotal = c.fetchone()

            from_dict = {
                "name": "My Business",
                "address": "456 Main St",
                "city": "City B",
                "state": "CA",
                "country": "USA",
            }

            # update booking database
            # setting invoice status as invoiced (status id = 3)
            c.execute("UPDATE bookings SET invoice = ?, inv_num = ? WHERE attaches_name = ? AND client_name = ? AND invoice = ?", (3, invoice_number, username, client_name, 2))
            conn.commit()

            try:
                rendered = render_template(
                    "/invoiced.html",
                    rows=rows,
                    sender=from_dict,
                    client=to_dict,
                    subtotal=int(subtotal[0]),
                    date=today,
                    inv=invoice_number,
                )
            except TypeError:
                return apology("Client must be selected", 400)

            base_url = app.instance_path.replace("/instance", "/static")

            # generate the pdf
            html = HTML(string=rendered, base_url=base_url)
            html.write_pdf(
                "./output/invoice.pdf", stylesheets=["./static/invoice.css"]
            )
            return send_file("./output/invoice.pdf")
        else:
            if user_id:
                return render_template("/dashboard.html")
            else:
                return apology("unauthorized", 401)


if __name__ == "__main__":
    app.run(debug=True)