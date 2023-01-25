import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# For current real time
import datetime

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Temporary API
os.environ["API_KEY"] = "pk_f00e67c1a30747a2aa0c13cdf911df7b"

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    # For current user
    user_id = session["user_id"]
    # Sum of shares to get all shares of single symbol
    stocks = db.execute("SELECT symbol, name, SUM(shares) AS shares, price FROM history WHERE user_id = ? GROUP BY symbol HAVING SUM(shares) > 0", user_id)
    # Determine how much cash a user currently has
    cash_dict = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
    # Should be only user returned in dict. Get cash value from cash key.
    cash = cash_dict[0]["cash"]
    # Set variable total.
    total = cash
    # Create for loop to add stock cash value to pure cash value.
    for stock in stocks:
        total += stock["shares"] * stock["price"]
    return render_template("index.html", stocks=stocks, cash=cash, total=total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "GET":
        return render_template("buy.html")
    else:
        # Declare variables to connect with html file
        symbol = request.form.get("symbol").upper()
        shares = request.form.get("shares")
        # Make sure number of shares is numeric and non-fractional
        if not shares.isdigit():
            return apology("Whole number shares only")
        # Make sure symbol is provided
        if not symbol:
            return apology("Stock symbol needed")
        # Declare quote variable and make sure stock exists
        quote = lookup(symbol)
        if not quote:
            return apology("Stock symbol does not exist")
        # For current user
        user_id = session["user_id"]
        # Turn string "shares" into float for total cost
        total_cost = float(shares) * quote["price"]
        # Get user's current cash value
        cash_dict = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        cash = cash_dict[0]["cash"]
        # Set 'if statement' to compare user's cash value to total cost of stocks to buy
        if cash < total_cost:
            return apology("Insufficient funds")
        # Update user's cash value
        updated_cash = cash - total_cost
        # Update user's cash in database
        db.execute("UPDATE users SET cash = ? WHERE id = ?", updated_cash, user_id)
        # Create variable for current time of buying
        date = datetime.datetime.now()
        # Record into history database to keep track of user's history of transactions
        db.execute("INSERT INTO history (user_id, symbol, name, shares, price, date) VALUES (?, ?, ?, ?, ?, ?)",
                   user_id, symbol, quote["name"], shares, quote["price"], date)
        # Indicate to the user visually a successful buy
        flash("Bought!")
        # Return to index page
        return redirect("/")


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    # For current user
    user_id = session["user_id"]
    # Connect history database with history html to update table
    stocks = db.execute("SELECT * FROM history WHERE user_id = ?", user_id)
    return render_template("history.html", stocks=stocks)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "GET":
        return render_template("quote.html")
    else:
        # Declare variables to connect with html file
        symbol = request.form.get("symbol").upper()
        quote = lookup(symbol)
        # Make sure stock exist
        if not quote:
            return apology("Stock symbol does not exist")
        # If exists, return quote
        else:
            return render_template("quoted.html", quote=quote)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        # Access form data
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")
        # Check for possible errors
        if not username or not password or not confirmation:
            return apology("Missing field")
        if password != confirmation:
            return apology("Password and confirmation do not match")
        # Insert new user into users table
        hash = generate_password_hash(password)
        try:
            # Create variable for new user
            new_user = db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, hash)
        # If username exists in database, then db.execute will not work
        except:
            return apology("Username taken")
        # Log user in
        session["user_id"] = new_user
        # Go to index page
        return redirect("/")
    # For GET request
    else:
        # Go to register page
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "GET":
        # For current user
        user_id = session["user_id"]
        # Only show stocks having a sum of shares greater than 0
        current_symbols = db.execute("SELECT symbol FROM history WHERE user_id = ? GROUP BY symbol HAVING SUM(shares) > 0", user_id)
        # Use 'for loop' to access rows in dict of stocks able to sell
        return render_template("sell.html", symbols=[row["symbol"] for row in current_symbols])
    else:
        # Declare variables to connect with html
        symbol = request.form.get("symbol")
        # Turn string "shares" into int to compare mathematically with user's actual count of shares
        shares = int(request.form.get("shares"))
        # Check for user's input of symbol
        if not symbol:
            return apology("Need to select a stock symbol")
        # Declare quote variable
        quote = lookup(symbol)
        # For current user
        user_id = session["user_id"]
        # Attain user's total shares for each stock
        shares_dict = db.execute(
            "SELECT SUM(shares) as shares FROM history WHERE user_id = ? AND symbol = ? GROUP BY symbol", user_id, symbol)
        # Turn string "shares" into int to compare mathematically
        current_shares = int(shares_dict[0]["shares"])
        # Compare number of shares user is trying to sell with actual amount of shares that user owns
        # If user has less shares owned than the amount they are trying to sell, return apology
        if current_shares < shares:
            return apology("You don't have that many shares")
        # Turn string "shares" into float to get total cash attained from sell
        total_sold = float(shares) * quote["price"]
        # Attain user's current cash value
        cash_dict = db.execute("SELECT cash FROM users WHERE id = ?", user_id)
        cash = cash_dict[0]["cash"]
        # Update user's cash value
        updated_cash = cash + total_sold
        # Update user's cash value in users database
        db.execute("UPDATE users SET cash = ? WHERE id = ?", updated_cash, user_id)
        # Record current real time of selling
        date = datetime.datetime.now()
        # Record selling in history database
        # "-shares" to subtract sold shares from original amount of shares owned
        db.execute("INSERT INTO history (user_id, symbol, name, shares, price, date) VALUES (?, ?, ?, ?, ?, ?)",
                   user_id, symbol, quote["name"], -shares, quote["price"], date)
        # Indicate to the user visually that sell was successful
        flash("Sold!")
        # Return user to index page
        return redirect("/")


@app.route("/change_password", methods=["GET", "POST"])
def change_password():
    """Allows the user to change password"""
    if request.method == "GET":
        return render_template("change_password.html")
    else:
        # User reached route via POST (as by submitting a form via POST)
        # Declare new_password variable to connect with html
        new_password = request.form.get("new_password")
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)
        # Ensure a new password was submitted
        elif not new_password:
            return apology("must provide new password", 403)
        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Create variable and generate hash for new password
        new_hash = generate_password_hash(new_password)
        # Update user's hash in users database
        db.execute("UPDATE users SET hash = ? WHERE username = ?", new_hash, request.form.get("username"))

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")
