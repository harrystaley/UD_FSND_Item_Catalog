"""
This module is the main project for P4 of the udacity FSND Item Catalog
"""
import random
import string
import json
import httplib2
import requests
from flask import Flask, render_template, request, redirect, url_for, flash
from flask import jsonify, make_response
from flask import session as login_session
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError


__author__ = "Harry Staley <staleyh@gmail.com>"
__version__ = "1.0"

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']

app = Flask(__name__)
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DB_SESSION = sessionmaker(bind=engine)
session = DB_SESSION()


# JSON REQUEST HANDLERS
@app.route('/restaurant/JSON')
def restaurnts_json():
    restaurants = session.query(Restaurant).all()
    return jsonify(RestData=[rest.serialize for rest in restaurants])


@app.route('/restaurant/<int:restaurant_id>/JSON')
@app.route('/restaurant/<int:restaurant_id>/menu/JSON')
def menu_json(restaurant_id):
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant_id
                                              ).all()
    return jsonify(MenuItems=[item.serialize for item in items])


@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/JSON')
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def item_json(restaurant_id, menu_id):
    item = session.query(MenuItem).filter_by(id=menu_id
                                             ).one()
    return jsonify(MenuItem=item.serialize)


# MAIN HANDLERS
@app.route('/')
@app.route('/restaurant/')
def get_restaurants():
    """
    Get all of the restaurants in the database and display them in a web page.
    """
    restaurants = session.query(Restaurant).all()
    return render_template('restaurants.html', restaurants=restaurants)


@app.route('/login/')
def get_login():
    """
    Creates a state token and store it in a session for later retrieval to
    guard against cross site forgerty.
    """
    state = ''.join(random.choice(string.ascii_uppercase + string.digits
                                  ) for x in xrange(32))
    login_session['state'] = state
    print "LOGIN STATE: " + state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """ handles authentication and authorization for google authentication """
    # state token validation
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'
                                            ), 401)
        response.heeaders['content-type'] = 'application/json'
        return response
    code = request.data
    try:
        # try to upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        # exchanges the code for oauth credentials
        credentials = oauth_flow.step2_exchange(code)
    # if a flow exchange error exists dump to json and return error msg
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    http_ = httplib2.Http()
    result = json.loads(http_.request(url, 'GET')[1])
    # If an error exists in the access token info, abort operation.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify current app level access token validity.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    # if stored credentials exist and user ids match respond that user is
    # already logged in
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get google user data json
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()

    # access user data json for display
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # display welcome message for user
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px;'
    output += ' height: 300px;'
    output += 'border-radius: 150px;'
    output += '-webkit-border-radius: 150px;'
    output += '-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route('/gdisconnect')
def gdisconnect():
    """ handles the log out functions of the google acccount """
    # gets and displays the acccess token data in the console
    access_token = login_session['access_token']
    print 'In gdisconnect access token is %s' % access_token
    print 'User name is: ' + login_session['username']
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'
                                            ), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # gets the url to revoke the access token
    url = ('https://accounts.google.com/o/oauth2/revoke?token=%s'
           % login_session['access_token'])
    h = httplib2.Http()
    # gets the result of the url and displays it in the concole
    result = h.request(url, 'GET')[0]
    print result['status']
    # if the result status is confirmed then delete all session
    # data otherwise send error to jsaon
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/restaurant/<int:restaurant_id>/')
@app.route('/restaurant/<int:restaurant_id>/menu/')
def get_menu(restaurant_id):
    """ This method gets all of the menu items for the selected restaurant """
    restaurant = session.query(Restaurant).filter_by(id=int(restaurant_id)
                                                     ).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id
                                              ).all()
    return render_template('menu.html', restaurant=restaurant,
                           items=items)


@app.route('/restaurant/new/', methods=['GET', 'POST'])
def new_restaurant():
    """ method to add a new restaurant """
    if 'username' not in login_session:
        return redirect('/login')
    else:
        if request.method == 'POST':
            newRestaurant = Restaurant(name=request.form['name'])
            session.add(newRestaurant)
            session.commit()
            flash(str(newRestaurant.name) + " restaurant created.")
            return redirect(url_for('get_restaurants'))
        else:
            return render_template('newrestaurant.html')


@app.route('/restaurant/<int:restaurant_id>/edit/', methods=['GET', 'POST'])
def edit_restaurant(restaurant_id):
    """ method to edit a restaurant """
    # if user is not logged in redirect to login page
    if 'username' not in login_session:
        return redirect('/login')
    else:
        restaurant = session.query(Restaurant).filter_by(id=int(restaurant_id)
                                                         ).one()
        if request.method == 'POST':
            if request.form['name']:
                restaurant.name = request.form['name']
                session.add(restaurant)
                session.commit()
                flash(str(restaurant.name) + " restaurant updated.")
            return redirect(url_for('get_restaurants'))
        else:
            return render_template('editrestaurant.html',
                                   restaurant=restaurant)


@app.route('/restaurant/<int:restaurant_id>/delete/', methods=['GET', 'POST'])
def delete_restaurant(restaurant_id):
    """ method to delete a restaurant """
    # if user is not logged in redirect to login page
    if 'username' not in login_session:
        return redirect('/login')
    else:
        restaurant = session.query(Restaurant).filter_by(id=int(restaurant_id)
                                                         ).one()
        items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id
                                                  ).all()
        if request.method == 'POST':
            session.delete(restaurant, items)
            session.commit()
            flash(str(restaurant.name) + " restaurant deleted.")
            return redirect(url_for('get_restaurants'))
        else:
            return render_template('deleterestaurant.html',
                                   restaurant=restaurant)


@app.route('/restaurant/<int:restaurant_id>/newitem', methods=['GET', 'POST'])
def new_menu_item(restaurant_id):
    """ method to add a new menu item to the menu """
    # if user is not logged in redirect to login page
    if 'username' not in login_session:
        return redirect('/login')
    else:
        restaurant = session.query(Restaurant).filter_by(id=int(restaurant_id)
                                                         ).one()
        if request.method == 'POST':
            newItem = MenuItem(name=request.form['name'],
                               course=request.form['course'],
                               description=request.form['description'],
                               price=request.form['price'],
                               restaurant_id=restaurant_id)
            session.add(newItem)
            session.commit()
            flash(str(newItem.name) + " menu item created.")
            return redirect(url_for('get_menu', restaurant_id=restaurant_id))
        else:
            return render_template('newmenuitem.html', restaurant=restaurant)


@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/edit',
           methods=['GET', 'POST'])
def edit_menu_item(restaurant_id, menu_id):
    """ method to edit a menu item """
    # if user is not logged in redirect to login page
    if 'username' not in login_session:
        return redirect('/login')
    else:
        restaurant = session.query(Restaurant).filter_by(id=int(restaurant_id)
                                                         ).one()
        item = session.query(MenuItem).filter_by(id=int(menu_id)
                                                 ).one()
        if request.method == 'POST':
            editItem = item
            if request.form['name']:
                editItem.name = request.form['name']
                editItem.course = request.form['course']
                editItem.description = request.form['description']
                editItem.price = request.form['price']
                session.add(editItem)
                session.commit()
                flash(str(item.name) + " updated.")
            return redirect(url_for('get_menu', restaurant_id=restaurant_id))
        else:
            return render_template('editmenuitem.html', restaurant=restaurant,
                                   item=item)


@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/delete',
           methods=['GET', 'POST'])
def delete_menu_item(restaurant_id, menu_id):
    """ method to delete the menu item """
    # if user is not logged in redirect to login page
    if 'username' not in login_session:
        return redirect('/login')
    else:
        restaurant = session.query(Restaurant).filter_by(id=int(restaurant_id)
                                                         ).one()
        item = session.query(MenuItem).filter_by(id=int(menu_id)
                                                 ).one()
        if request.method == 'POST':
            session.delete(item)
            session.commit()
            flash("Menu item deleted.")
            return redirect(url_for('get_menu', restaurant_id=restaurant_id))
        else:
            return render_template('deletemenuitem.html',
                                   restaurant=restaurant,
                                   item=item)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
