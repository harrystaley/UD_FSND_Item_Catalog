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
            if self.path.endswith("/restaurants"):
                self.send_response(200)
                self.send_header('content-type', 'text/html')
                self.end_headers()
                template = "/resturants"
                restaurants = session.query(Restaurant).all()
                output = ''
                output += "<html><body>"
                output += "Restaurants"
                for restaurant in restaurants:
                    output += restaurant.name
                    output += "<br>"

                output += "</body></html>"
                self.wfile.write(output)
                print "The page %s has been rendered." % template
                return

        except IOError:
            self.send_error(404, "File not found %s" % self.path)

    def do_POST(self):
        try:
            self.send_response(301)
            self.end_headers()
            ctype, pdict = cgi.parse_header(self.headers
                                            .getheader('content-type'))
            if ctype == 'multipart/form-data':
                fields = cgi.parse_multipart(self.rfile, pdict)
                messagecontent = fields.get('message')

            output = ""
            output += "<html><body>"
            output += " <h2> Okay, how about this: </h2>"
            output += "<h1> %s </h1>" % messagecontent[0]
            output += '''<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me to say?</h2><input name="message" type="text" ><input type="submit" value="Submit"> </form>'''
            output += "</body></html>"
            self.wfile.write(output)
            print output
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
