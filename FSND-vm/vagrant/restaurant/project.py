
from flask import Flask, render_template, request, redirect, url_for
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem


__author__ = "Harry Staley <staleyh@gmail.com>"
__version__ = "1.0"

app = Flask(__name__)
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/')
def GetRestaurants():
    """
    Get all of the restaurants in the database and display them in a web page.
    """
    restaurants = session.query(Restaurant).all()
    return render_template('restaurants.html', restaurants=restaurants)


@app.route('/restaurant/<int:restaurant_id>/')
def GetMenu(restaurant_id):
    """ This method gets all of the menu items for the selected restaurant """
    restaurant = session.query(Restaurant).filter_by(id=int(restaurant_id)
                                                     ).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id
                                              ).all()
    return render_template('menu.html', restaurant=restaurant,
                           items=items)


@app.route('/restaurant/<int:restaurant_id>/newitem', methods=['GET', 'POST'])
def NewMenuItem(restaurant_id):
    """ method to add a new menu item to the menu """
    restaurant = session.query(Restaurant).filter_by(id=int(restaurant_id)
                                                     ).one()
    if request.method == 'POST':
        newItem = MenuItem(name=request.form['name'],
                           restaurant_id=restaurant_id)
        session.add(newItem)
        session.commit()
        return redirect(url_for('GetMenu', restaurant_id=restaurant_id))
    else:
        return render_template('newmenuitem.html', restaurant=restaurant)


@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/edit',
           methods=['GET', 'POST'])
def EditMenuItem(restaurant_id, menu_id):
    """ method to edit a menu item """
    restaurant = session.query(Restaurant).filter_by(id=int(restaurant_id)
                                                     ).one()
    item = session.query(MenuItem).filter_by(id=int(menu_id)
                                             ).one()
    if request.method == 'POST':
        editItem = item
        if request.form['name']:
            editItem.name = request.form['name']
            session.add(editItem)
            session.commit()
        return redirect(url_for('GetMenu', restaurant_id=restaurant_id))
    else:
        return render_template('editmenuitem.html', restaurant=restaurant,
                               item=item)


# Task 3: Create a route for deleteMenuItem function here
@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/delete',
           methods=['GET', 'POST'])
def DeleteMenuItem(restaurant_id, menu_id):
    """ method to delete the menu item """
    restaurant = session.query(Restaurant).filter_by(id=int(restaurant_id)
                                                     ).one()
    item = session.query(MenuItem).filter_by(id=int(menu_id)
                                             ).one()
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        return redirect(url_for('GetMenu', restaurant_id=restaurant_id))
    else:
        return render_template('deletemenuitem.html', restaurant=restaurant,
                               item=item)

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
