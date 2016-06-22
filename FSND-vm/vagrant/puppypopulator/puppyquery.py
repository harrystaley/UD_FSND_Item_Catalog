from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from puppies import Base, Shelter, Puppy
#from flask.ext.sqlalchemy import SQLAlchemy
import datetime


engine = create_engine('sqlite:///puppyshelter.db')

Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()


def query_1():
    """ Query all puppies and display them in ascending order """
    dbq = session.query(Puppy.name).order_by(Puppy.name.asc()).all()
    for item in dbq:
        print item[0]


def queery_2():
    """
    Get all puppies less than six months old and display them youngest
    to oldest.
    """
    today = datetime.date.today()
    if passesLeapDay(today):
        sixMonthsAgo = today - datetime.timedelta(days=183)
    else:
        sixMonthsAgo = today - datetime.timedelta(days=182)
    dbq = session.query(Puppy.name, Puppy.dateOfBirth)\
        .filter(Puppy.dateOfBirth >= sixMonthsAgo)\
        .order_by(Puppy.dateOfBirth.desc())

    # print the result with puppy name and dob
    for item in dbq:
        print "{name}: {dob}".format(name=item[0], dob=item[1])


def query_3():
    """Query all puppies by ascending weight"""
    result = session.query(Puppy.name, Puppy.weight)\
        .order_by(Puppy.weight.asc()).all()

    for item in result:
        print item[0], item[1]


def query_4():
    """Query all puppies grouped by the shelter in which they are staying"""
    result = session.query(Shelter, func.count(Puppy.id)).join(Puppy)\
        .group_by(Shelter.id).all()
    for item in result:
        print item[0].id, item[0].name, item[1]


# Helper Methods
def passesLeapDay(today):
    """
    Returns true if most recent February 29th occured after or exactly
    183 days ago (366 / 2)
    """
    thisYear = today.timetuple()[0]
    if isLeapYear(thisYear):
        sixMonthsAgo = today - datetime.timedelta(days=183)
        leapDay = datetime.date(thisYear, 2, 29)
        return leapDay >= sixMonthsAgo
    else:
        return False


def isLeapYear(thisYear):
    """
    Returns true iff the current year is a leap year.
    Implemented according to logic at
    https://en.wikipedia.org/wiki/Leap_year#Algorithm
    """
    if thisYear % 4 != 0:
        return False
    elif thisYear % 100 != 0:
        return True
    elif thisYear % 400 != 0:
        return False
    else:
        return True

# query_1()
# query_2()
# query_3()
# query_4()
