# Pseudo$tocks
#### Video Demo: 
#### Description:

"Pseudo$tocks" is a website that allows the users to manage stocks in a hypothetical
setting. Using real-time stock market data from IEX's API, the users have the ability
to obtain quotes on any company's stock value. From there, the users can buy and sell
stocks with a balance of $10,000 and their trading history is documented for reference.

#### Purpose:

The trading of stocks can be a very daunting task considering all the risks. The volatily 
of the stock market can make it hard for any person trying to break into the stock trading
world. However, I believe that this website not only provides a beginner-friendly introduction 
but a risk-free transition into that realm. 

#### Languages and Files:

- ##### Frameworks: 
    
    Frameworks utilized: Flask, Bootstrap

- ##### HTML (in the templates directory):

    -   **layout.html:**

        Layout.html, with the incorporation of jinja, was used as the template to all the webpages
        of the website. This file contains markup for the header and footer of the website that 
        includes the title, background color, navigation bar, and credits. The navigation bar has 
        different links depending on if the user is logged in or not. The jinja implementation of 
        flashing the users messages and the links to the Bootstrap frameworks are contained here. 

    -   **index.html:**

        Index.html is the implementation of the table that contains all of the stocks the users own.
        Information on the stocks includes the stock symbol, name, number of shares, price, and total
        value of all the shares of that stock combined. Also provided is the cash value the user has 
        and the accumulated value of the cash and stocks. 

    -   **login.html:**

        Login.html contains the markup for the username and password input boxes along with a submit
        button to log the user in if they are a returning user. 

    -   **register.html:**

        Register.html contains similar markup to login.html as far as a username and password box, 
        but it also contains the addition of a password confirmation box and register button. 

    -   **change_password.html:**

        Change_password.html contains similar markup to login.html as far as the username and password 
        box and log in button, but it also contains the addition of a new password box.

    -   **quote.html:**

        Quote.html contains the markup for the user to input a stock symbol into the box and search for 
        its value using IEX's API.

    -   **quoted.html:**

        Quoted.html shows the name of the stock, its symbol, and its value in US dollars.

    -   **buy.html:**
    
        Buy.html contains the markup for the user to search for a stock symbol and are then required to
        enter an amount of shares, minimum 1, of such stock they would like to buy. 
    
    -   **sell.html:**

        Sell.html contains the markup for the user to sell stocks. It contains a dropdown menu of all the 
        stocks the user owns, followed by a box where the user is required to input a minimum value of 1 
        share of the stock they would like to sell. 

    -   **history.html:**

        History.html contains the markup of a table that recorded all the users' previous stock transactions.
        It displays information such as the stock symbol, name, number of shares sold/bought, price of the 
        stock at the time, and date that the transaction occurred.

    -   **apology.html:**

        Apology.html contains the markup for the image, error code, and caption that displays when the user
        "makes a mistake". Mistakes such as not providing a username or password, or an incorrect version of 
        either. Also for cases such as trying to search for an invalid stock symbol, trying to buy shares of
        a stock with insufficient funds, or trying to sell shares of stocks that the users do not own.

- ##### CSS, Database, TXT, Icon:

    -   **CSS:**

        Styles.css contains the visual formatting for the navigation bar when it comes to its size and color. 
        A majority of the website's CSS was created by using the Bootstrap framework.

    -   **Database:**

        Using SQLite, finance.db was created and it contains two tables. One table is the "users" table which 
        contains the unique id, username, and password hash created for each user. The last column is the cash 
        column, showing that each user is given $10,000 upon registration. The other table is the "history" 
        table and this table contains the unique id and user id for each transaction an individual user makes. 
        Each transaction is recorded accounting for the stock symbol, name, number of shares bought/sold, price 
        at the time, and the date the transaction occurred.

    -   **TXT:**

        The requirements.txt file contains all of the pip-installable libraries or modules needed for this program.

    -   **Icon:**

        The favicon.ico file contains the moneybag icon seen in the tab of the website.

- ##### Python:

    -   **helpers.py:**

        Contains all the helper functions such as showing an error message to the user, requiring a login, 
        looking up a stock using IEX's API, and formatting money in USD format.

    -   **apology() and escape():**
    
        Escape function replaces special characters to ensure error message and code passes. Apology function
        renders apology.html that contains the markup for the image showing the error code and message.

    -   **login_required():**

        Login_required function decorated routes to require that user be logged in first.

    -   **lookup():**

        Lookup function obtained the quote for a stock. It contacted the IEX's API and parsed the JSON object 
        to return the stock's name, price, and symbol.

    -   **usd():**

        The usd function formatted money in US dollars format.

    
    -   **app.py:**

        Initially, a Flask and SQL object are created and the templates and sessions are configured. A temporary
        API Key is utilized and the program checks that the key is in place before starting.

    -   **@app.route("/"):**

         This route accesses the history database for the current user and retrieves information on the stocks
         the user currently owns. It also accesses the users database to get the amount cash they currently have.
         Ultimately, index.html is rendered.

    -   **@app.route("/buy"):**

        If it is a GET request, buy.html is rendered. Otherwise, for POST requests, error checking is done to ensure
        that the users inputted a valid stock symbol along with a whole number of shares that they are trying to
        buy. Error checking includes accessing the users database and validating that the current user has enough 
        money to buy said stock and number of shares. If a transaction is succesful, the user will be flashed a 
        message indicating as such and the user's cash value and time of purchase will be updated in the databases.
        Users are then redirected back to the homepage.

    -   **@app.route("/history"):**

        This route accesses all the information in the history database for the current user and renders history.html.

    -   **@app.route("/login"):**

        Session.clear() is called to forget any current user id. If it is a GET request, login.html is rendered.
        Otherwise, the users database is accessed and error checking is done to ensure that the inputted username
        and password exists. If it is a successful login, the user is redirected to the homepage.

    -   **@app.route("/logout"):**

        Session.clear() is called to forget/logout the current user. Then the user is redirected to the login page.

    -   **@app.route("/quote"):**
    
        If GET request, quote.html is rendered. Otherwise, the lookup() is called on the inputted stock symbol and 
        stored in a variable to check for validity. If stock symbol exists, then quoted.html is rendered.

    -   **@app.route("/register"):**

        If GET request, register.html is rendered. Otherwise, the user's inputted username, password, and password
        confirmation are stored in variables and checked for errors such as if the password and password confirmation
        match or not and if the username is already taken. If successful, then the password is hashed and stored
        along with the username in the users database. The user is then redirected to the homepage.
        
    -   **app.route("/sell"):**

        If GET request, the history database will be accessed and the stocks that the users currently own will be 
        iterated over and stored in a list for dropdown menu purposes located in sell.html. Sell.html is then rendered. Otherwise, if POST request, store the users inputted stock symbol and number of shares to sell in variables
        and put them through error checking. Error checking also includes seeing if the user has enough of the stock
        they are trying to sell. If successful, the user's cash value is updated in the users database. The user will
        be flashed a message indicating a successful sell and then the history database will be updated with the
        transaction along with the time of sell. The user is finally redirected back to the homepage.

    -   **app.route("/change_password"):**

        If GET request, change_password.html is rendered. Otherwise, error checking is done to ensure that the user
        inputted a username, password, and new password. The users database is accessed to ensure the correct
        username and password were inputted and if so, then a new hash will be created for the new password. The
        hash will be updated in the users database and the user will be redirected to the homepage.

