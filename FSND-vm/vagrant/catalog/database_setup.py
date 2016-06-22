import sys

from sqlalchemy import
Column, ForeignKey, Integer, String

from sqlalchemy.ext.declarative import
declarative_base

from sqlalchemy.orm import relationship

from sqlalchemy import create_engine

base = declarative_base()
# end beginning config code
# place class defs between this and the end config code

    restraunt_id = Collumn(
        integer, ForeignKey('restraunt.id'))
    restraunt = relationship(Restraunt)


# begin end config code
engine = create_engine('sqlite:///restrauntmenu.db')
base.metadata.create_all(engine)
