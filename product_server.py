import re
from bs4 import BeautifulSoup
from datetime import datetime
import urllib3
from flask import Flask, render_template, request, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from apscheduler.schedulers.background import BackgroundScheduler

# Instantiate flask and pass the Current file name as an argument
app = Flask(__name__)

# Set secret key for session
app.secret_key = 'somesecretkey'

# Database Connection with SQl Alchemy
ENV = "production"
if ENV == "development":
    app.debug = True

    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:admin@localhost:5432/productcomparision'

else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = "postgres://axdfdgozgvatgr:126f4fad1a2af4e508fb5630093d4d987abb9ad8e41749de309bc8591137e5f0@ec2-3-231-16-122.compute-1.amazonaws.com:5432/d443qhchn2r0ls"

# Hide Warnings: we dont need to track modifications of the objects
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# To create a table and columns write command
# from product_server import db
# Create Models
class PriceData(db.Model):
    __tablename__ = 'pricedata'
    id = db.Column(db.Integer, primary_key=True)
    ser_name_cur_from_cur_to = db.Column(db.String(20), nullable=False)
    ser_name = db.Column(db.String(20), nullable=False)
    rate_from_to = db.Column(db.Float(15), nullable=False)

    cur_from_to = db.Column(db.String(6), nullable=False)
    system_time = db.Column(db.String(8), nullable=False)

    # Initialize the table
    def __init__(self, ser_name_cur_from_cur_to, ser_name, rate_from_to, cur_from_to, system_time):
        self.ser_name_cur_from_cur_to = ser_name_cur_from_cur_to
        self.ser_name = ser_name
        self.rate_from_to = rate_from_to

        self.cur_from_to = cur_from_to
        self.system_time = system_time


# Data Scrape Code to fetch prices
# DATA SCRAPING AREA
def get_prices():
    url_ext = ["germany/india/eur/inr/", "india/germany/inr/eur", "united-states/india/usd/inr/",
               "india/united-states/inr/usd/", "australia/india/aud/inr/", "india/australia/inr/aud/",
               "united-kingdom/india/gbp/inr", "india/united-kingdom/inr/gbp", "japan/india/jpy/inr",
               "india/japan/inr/jpy", "germany/united-states/eur/usd", "united-states/germany/usd/eur",
               "germany/united-kingdom/eur/gbp", "united-kingdom/germany/gbp/eur",
               "united-kingdom/united-states/gbp/usd", "united-states/united-kingdom/usd/gbp",
               "japan/united-kingdom/jpy/gbp", "united-kingdom/japan/gbp/jpy",
               "united-states/japan/usd/jpy", "japan/united-states/jpy/usd"]

    for k in range(0, len(url_ext)):

        # urllib is a http client to and and receive requests
        # We create a PoolManager() to generate a request, It handles all of the details of connection pooling

        http = urllib3.PoolManager()
        page_source = http.urlopen('GET', f"https://www.monito.com/send-money/{url_ext[k]}")

        # Soup operations : .find(""), .body, .title, .contents, find_all("")
        # Css Selectors(returns list) : .select(""), .select("")[index]
        # Attributes : .get("att_name"), .getText()

        # Note : list of service providers ( to be deleted manually first from here before deleting the values from
        # database on admin page list

        # DELETION HERE IF YOU DONT SUPPORT THESE SERVICES ANYMORE

        service_providers = ["TransferWise", "Money2India", "Skrill", "WorldRemit", "Remitly", "TransferGo",
                             "CurrencyFair", "Azimo", "PayPal", "Ria", "EasySend", "Xendpay"]

        """
        Making an object from BeautifulSoup and passing the string 'res' HTML document requested and parse it to lxml’s,HTML 
        parser

        """
        # Get data in utf 8 plain text format
        soup = BeautifulSoup(page_source.data.decode('utf-8'), "lxml")

        # Select class of exchange services providers and rates through CSS selector
        x = soup.select("div[class *= 'tc_2bdP']")

        # ReGex Patterns to match the text for extracting the currency rates
        pattern_rates = re.compile(r"(\d{1})+\.(\d{4})")

        # ReGex Pattern for extracting the currency
        pattern_currency = re.compile(r"[A-Z]{3}")

        # Looping through service providers in our dataset list and then matching if they exist in all
        # the service_providers list

        for i in range(0, len(service_providers)):

            # find all the service providers using same css selector

            for j in range(0, len(x)):

                if service_providers[i] in x[j].getText():

                    # Service Provider Name
                    s_n = service_providers[i]

                    # From_Currency_Name from

                    from_currency = pattern_currency.findall(x[j].getText())

                    # To_Currency_Name_to
                    to_currency = pattern_currency.findall(x[j].getText())

                    # Merge Currency Names

                    cur_fr_to = from_currency[0] + to_currency[1]

                    # Merge service_providers, currency from and currency to
                    service_providers_cur_from_cur_to = f"{service_providers[i]}_{from_currency[0]}_{to_currency[1]}"

                    # From_Currency to To_Currency Rate
                    rate = float(pattern_rates.search(x[j].getText()).group())
                    r = f"{rate:.4f}"

                    # System current time
                    system_time = datetime.now()
                    sys_time = system_time.strftime("%H:%M:%S")

                    # SQL Alchemy command to fetch 'first' values according to the condition column ='value' is True

                    name_data = PriceData.query.filter_by(ser_name_cur_from_cur_to=
                                                          service_providers_cur_from_cur_to).first()

                    # if name_data is None then add the data into the table
                    if name_data is None:
                        add_rates = PriceData(ser_name_cur_from_cur_to=service_providers_cur_from_cur_to,
                                              ser_name=s_n,
                                              rate_from_to=r, cur_from_to=cur_fr_to,
                                              system_time=sys_time)
                        db.session.add(add_rates)
                        db.session.commit()

                    # if data exists then just update the rate fields
                    else:
                        update = name_data
                        update.rate_from_to = r
                        update.system_time = sys_time
                        db.session.commit()

                    break

        page_source.close()


# If set to True, the scheduler will automatically terminate with the application otherwise manually shutdown it
scheduler = BackgroundScheduler(daemonic=True)

# continuous updating the database with job scheduler
scheduler.add_job(get_prices, trigger='interval', seconds=1800)
scheduler.start()


# If page not found
@app.errorhandler(404)
# e takes error as  parameter
def page_not_found(e):
    return render_template('404.html')


@app.route('/')
def index():
    # By default, HTML files are picked from templates folder , and other CSS, JS from static
    return render_template('compare.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/compare', methods=['POST', 'GET'])
def compare():
    # POST- to send data to server privately, in GET data is visible in URL
    if request.method == 'POST':
        cur_from = request.form['cf']
        cur_to = request.form['ct']
        amount = request.form['amt']
        cur_com = cur_from + cur_to
        r_f_t = []
        t_amt = []
        s_name = []
        e_msg = "Sorry, We Can't Find Service Providers For This Currency Conversion At The Moment"

        # return table with data
        row1 = "<th> Service Providers </th>"
        row2 = "<th> Exchange Rate </th>"
        row3 = "<th> Transfer Duration </th>"
        row4 = "<th> Recipient Gets (excluding transfer fees)</th>"

        # Querying the database to fetch all rows where column matches the given condition

        data = PriceData.query.filter_by(cur_from_to=cur_com).all()

        # fetch the data from the rows if above query returned any data
        if data:
            for row in data:
                r = row.rate_from_to
                r_f_t.append(r)

                q = float(amount) * row.rate_from_to
                q_a = f"{q:.2f}"
                t_amt.append(q_a)

                s = row.ser_name
                s_name.append(s)


        # if data is missing then 'service not available'
        else:
            return render_template('compare.html', e_msg=e_msg)

        # The zip() function returns a zip object, which is an iterator of tuples, 2 iterators are passed and paired
        # together
        return render_template('compare.html', row1=row1, row2=row2, row3=row3, row4=row4, cur_from=cur_from,
                               cur_to=cur_to, amount=amount, r_q_s=zip(r_f_t, t_amt,
                                                                       s_name))

    else:
        return render_template('compare.html')


# Admin Login functionality
# Admins
class AdminLogin:
    def __init__(self, login_id, username, password):
        self.login_id = login_id
        self.username = username
        self.password = password

    def __repr__(self):
        return f"<AdminLogin:{self.username}>"


# admins allowed
admins = [AdminLogin(login_id=1, username='admin1', password='admin1'),
          AdminLogin(login_id=2, username='admin2', password='admin2')]


@app.route('/login', methods=['GET', 'POST'])
def admin_log():
    v_err = "Invalid Username/Password Entered"
    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        # iterate and match username and password
        user_check = [a for a in admins if a.username == username and a.password == password]

        if user_check:
            # Create session key when user logs in and redirect user to admin page
            # Stores data in dict key : value
            session['username'] = username
            return redirect(url_for('admin_page'))

        else:
            return render_template('login.html', v_err=v_err)
    else:
        # if user is already in session be on the admin page
        if 'username' in session:
            return redirect(url_for('admin_page'))
        return render_template('login.html')


@app.route('/admin', methods=['POST', 'GET'])
def admin_page():
    # Check if user is in session
    if 'username' in session:
        username = session['username']

        # Saving the values in set for no duplicates
        s_list = set()
        error = "No Service Provider Exist"

        # Fetching all the service providers stored in database in a column if they exist
        lst = PriceData.query.order_by(PriceData.ser_name).all()
        if lst:
            for i in lst:
                j = i.ser_name
                s_list.add(j)
        else:
            # if no service provider are left in the table in database
            return render_template('admin.html', error=error, a_s=username)

        # get the service provider you want to delete
        if request.method == 'POST':

            s_name = request.form['slist']
            e_r = "Request Invalid : Refresh the Page"

            # if length of my request is > 1 Obvious no service provider has 1 char name, then return validations
            if len(s_name) > 1:

                # Delete from database where column name is value we get from post
                PriceData.query.filter_by(ser_name=s_name).delete()
                db.session.commit()
            else:
                return render_template('admin.html', err=e_r, a_s=username)

            s_p = f"{s_name} Deleted"
            s_n = "Refresh page to see the list"

            return render_template('admin.html', s_p=s_p, s_n=s_n, a_s=username)

        # returning first on landing on admin page , because the list of s providers are first fetched from database
        # then displayed on the admin page dropdown
        else:
            return render_template('admin.html', s_list=s_list, a_s=username)

    else:
        return redirect(url_for('admin_log'))


# Logout from the admin page
@app.route('/logout')
def logout():
    session.pop("username", None)
    return redirect(url_for('admin_log'))


# __main__ file is the first point of execution
if __name__ == '__main__':
    # to keep the server running continuous
    # app.debug = True
    # Run Server and Execute the code on server
    app.run()
