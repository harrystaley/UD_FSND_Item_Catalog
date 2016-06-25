import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from database_setup import Base, Restaurant, MenuItem


__author__ = "Harry Staley <staleyh@gmail.com>"
__version__ = "1.0"

engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


class WebserverHandler(BaseHTTPRequestHandler):
    """ Class instantiates a web server to handle HTTP requests """
    def do_GET(self):
        """ handles the get requests for the web server """
        try:
            # renders the /restaurants/new page
            if self.path.endswith("/restaurants/new"):
                self.send_response(200)
                self.send_header('content-type', 'text/html')
                self.end_headers()
                template = "/resturants/new"
                output = ''
                output += "<html><body>"
                output += "<h2>New Restaurant</h2>"
                output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/new'>"
                output += "<input name='RestaurantName' type='text'>"
                output += "<input type='submit' value='Submit'>"
                output += "</form>"
                output += "</body></html>"
                self.wfile.write(output)
                print "The page %s has been rendered." % template
                return

            # renders the /restaurants page
            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('content-type', 'text/html')
                self.end_headers()
                template = "/resturants"
                restaurants = session.query(Restaurant).all()
                output = ''
                output += "<html><body>"
                output += "Restaurants"
                output += "<br><br>"
                output += "<a href='/restaurants/new'>New Restaurant</a>"
                output += "<br>"
                for restaurant in restaurants:
                    output += restaurant.name
                    output += "<br><a href='#'>Edit</a>"
                    output += "<br><a href='#'>Delete</a>"
                    output += "<br><br>"

                output += "</body></html>"
                self.wfile.write(output)
                print "The page %s has been rendered." % template
                return

        except IOError:
            self.send_error(404, "File not found %s" % self.path)

    def do_POST(self):
        """ Handles the post requests for the HTTP server """
        try:
            # Handles the post request from /restaurants/new
            if self.path.endswith("/restaurants/new"):
                ctype, pdict = cgi.parse_header(self.headers
                                                .getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    restaurantform = fields.get('RestaurantName')

                newrestaurant = Restaurant(name=restaurantform[0])
                session.add(newrestaurant)
                session.commit()

                self.send_response(301)
                self.send_header('content-type', 'text/html')
                self.send_header('Location', '/restaurants')
                self.end_headers()
                return
        except:
            pass


def main():
    """ Main class for the web server responses from/to the user """
    try:
        port = 8080
        server = HTTPServer(('', port), WebserverHandler)
        print "Server running on port %s press ctrl+c to stop..." % port
        server.serve_forever()
    except KeyboardInterrupt:
        print "ctrl+c entered, stopping web server..."
        server.socket.close()


if __name__ == '__main__':
    main()
