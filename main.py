from flask import Flask, render_template, flash, request, url_for, jsonify, redirect, session
from modules.DBController import DBController
app = Flask(__name__)
app.secret_key = "2e1dt3476rtfghudigyugqwwu2w8190qoidj"

username = "user"
password = "12345"
scraping_status = ""

db = DBController()


@app.route('/login', methods=['POST'])
def do_admin_login():
    global db
    if db.check_login_details(request.form['username'], request.form['password']):
        session['logged_in'] = True
    else:
        flash('wrong password!')
        return render_template('pages-login.html', title='Login Page')
    return redirect(url_for('table_details'))


@app.route("/logout")
def logout():
    session['logged_in'] = False
    return redirect(url_for('table_details'))


@app.route('/', methods=['GET'])
@app.route('/inputPage', methods=['GET'])
@app.route('/tableDetails', methods=['GET', 'POST'])
def table_details():
    if not session.get('logged_in'):
        return render_template('pages-login.html', title='Login Page')
    if request.method == "POST":
        print("Coming in here")
        all_filtered_rows, brokerages = db.filter_records(brokerage_list=request.form.getlist('brokerage'),
                                              listing_category_list=request.form.getlist('listing_category'),
                                              property_status_list=request.form.getlist('listing_status'),
                                              price_min=request.form['minPrice'],
                                              price_max=request.form['maxPrice'],
                                              bathrooms_min=request.form['minBathrooms'],
                                              bathrooms_max=request.form['maxBathrooms'],
                                              bedrooms_min=request.form['minBedrooms'],
                                              bedrooms_max=request.form['maxBedrooms'],
                                              )
    else:
        all_filtered_rows, brokerages = db.get_all_properties()

    return render_template('tableDetails.html', title='Table Details Page', tableData=all_filtered_rows,
                           brokerage_list=brokerages)


if __name__ == '__main__':
    app.run(debug=True)

""" brokerage, url, listing_status, listing_category, price, bedrooms, bathrooms, total_area_sq_ft """
