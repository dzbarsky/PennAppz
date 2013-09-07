import sys

import requests
import simplejson as json
import MySQLdb

import pprint

class DatabasePopulater:
    def __init__(self, key):
        self.key = key

    # Retrieves an endpoint on the Penn Course Review API
    def get_data(self, endpoint):
        base_url = "http://api.penncoursereview.com/v1"
        url = base_url + endpoint + "?token=" + self.key
        r = requests.get(url)
        if hasattr(r, 'json'):
            return r.json()
        else:
            return json.loads(r.content)

    # Retrieve a list of course reviews for a given department
    def get_courses(self):
        course_ids = []
        departments = self.get_data("/depts")
        if True:
            dept = departments['result']['values'][0]
        #for dept in departments['result']['values']:
            courses = self.get_data(dept['path'])
            for course in courses['result']['coursehistories']:
                course_ids.append(course['id'])
        return course_ids

    def populate_database(self):
        db = MySQLdb.connect("localhost", "root", "", "PennApps" )
        cursor = db.cursor()

        #pp = pprint.PrettyPrinter(indent=4)

        for course_id in self.get_courses():
            course = self.get_data("/courses/" + str(course_id))
            #pp.pprint(course)

            # Prepare SQL query to INSERT a record into the database.
            sql = """INSERT INTO COURSES(id, name)
VALUES (%s, '%s')""" % (course_id, course['result']['name'])
            try:
                cursor.execute(sql)
                db.commit()
            except Exception as e:
                print e
                db.rollback()

        db.close()

def main(key):
    dp = DatabasePopulater(key)
    dp.populate_database()

if __name__ == "__main__":
    if (len(sys.argv) < 2):
        print "usage: scores.py <apikey>"
    else:
        main(*sys.argv[1:])
