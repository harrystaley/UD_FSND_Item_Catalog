import sys

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()
# END BEGINNING CONFIG CODE
# place class defs between this and the end config code


class Restaurant(Base):
    """ Class defines the table for the restraunts in the database """
    # defines the name of the table
    __tablename__ = 'restaurant'
    # mapper variables for each of the atributes of a restraunt
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)


class MenuItem(Base):
    """
    This class defines the table for the items that will be on the menu.
    """
    # defines the name of the table
    __tablename__ = 'menu_item'
    restaurant = relationship(Restaurant)

    # mapper variables for each of the atributes of a menu item
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    course = Column(String(250))
    description = Column(String(250))
    price = Column(String(8))
    restaurant_id = Column(Integer, ForeignKey('restaurant.id'))

# END CONFIG CODE
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.create_all(engine)
