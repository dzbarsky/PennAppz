import sys

import requests
import simplejson as json
import MySQLdb

import pprint
import nltk
import string

class DatabasePopulater:
    def __init__(self, key):
        self.key = key
        self.db = MySQLdb.connect("localhost", "root", "", "PennApps" )

    def executeQuery(self, sql):
        cursor = self.db.cursor()
        try:
            cursor.execute(sql)
            self.db.commit()
            return True
        except Exception as e:
            print "\n~~~~~~~~FAILED: " + sql
            print e
            self.db.rollback()
            return False

    def create_tags(self, description, course_id):
        # Strip punctuation
        text = ''.join(ch for ch in description if ch not in string.punctuation)
        text = nltk.word_tokenize(text)
        output_tuple = nltk.pos_tag(text);
        self.find_nouns(output_tuple, course_id)

    def find_nouns(self, output_tuples, course_id):
        occurrences = dict()
        for item in output_tuples:
            if item[1] in ("NN", "NNP", "NNS"):
                prev = 0
                if item[0] in occurrences:
                    prev = occurrences[item[0]]
                occurrences[item[0]] = prev + 1

                # Insert word into database
                sql="""INSERT IGNORE INTO courseAdvisor_keyword(word)
VALUES ('%s')""" % item[0]
                self.executeQuery(sql)

        for item in occurrences:
            print item
            print occurrences[item]
            # Add keyword to the keyword list for the current course
            sql="""INSERT INTO courseAdvisor_courses_keywords(course_id, number, keyword_id)
SELECT %s, %s, id FROM courseAdvisor_keyword WHERE word='%s'""" % (course_id,
                                                                   occurrences[item],
                                                                   item)
            self.executeQuery(sql)

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
        def escape(val):
            return val.replace("'", "\\'")

        pp = pprint.PrettyPrinter(indent=4)

        for course_id in self.get_courses():
            course = self.get_data("/courses/" + str(course_id))
            #pp.pprint(course)

            # Insert a course into the courses table
            sql = """INSERT INTO courseAdvisor_course(id, courseCodes, title, description, preSearched)
VALUES (%s, '%s', '%s', '%s', FALSE)""" % (course_id,
                                           escape(json.dumps(course['result']['aliases'])),
                                           escape(course['result']['name']),
                                           escape(course['result']['description']))
            self.executeQuery(sql)

            aliases = course['result']['aliases']
            for alias in aliases:
                # Make sure all the departments exist in the database
                dept = alias[0:alias.find('-')]
                sql = """INSERT IGNORE INTO courseAdvisor_department(code)
VALUES ('%s')""" % dept
                self.executeQuery(sql)

                sql = """INSERT IGNORE INTO courseAdvisor_course_departments(course_id, department_id)
SELECT %s, id FROM courseAdvisor_department WHERE code='%s'""" % (course_id,
                                                                  dept)

                #print sql
                self.executeQuery(sql)
            self.create_tags(course['result']['description'], course_id)

        self.db.close()

def main(key):
    dp = DatabasePopulater(key)
    dp.populate_database()

if __name__ == "__main__":
    if (len(sys.argv) < 2):
        print "usage: scores.py <apikey>"
    else:
        main(*sys.argv[1:])
