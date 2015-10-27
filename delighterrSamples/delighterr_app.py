from flask import Flask, jsonify, make_response, flash, abort, request, redirect, url_for, get_flashed_messages, render_template
from delighterr_functionality import Contact
from piplapis.search import SearchAPIError
import json
import sys

app = Flask(__name__)


app.config['SECRET_KEY'] = 'super-secret'

import logging
from logging import Formatter, FileHandler

app = Flask(__name__)

app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.DEBUG)


@app.route("/delighterr/search", methods = ['GET', 'POST'])
def people_search():
	if request.method == 'POST':
                app.logger.debug("in people_search post")
		## Essentials ##
		first_name = request.form["first_name"]
		last_name = request.form["last_name"]
		email = request.form["email"]
		## Optional social media 
		linkedin_name = request.form["linkedin_name"]
		twitter_handle = request.form["twitter_handle"]
		if first_name and last_name and email:
			## Create and configure the Contact object and the Pipl query object ##
			person = Contact(first_name, last_name)
			person.add_email_to_query(email)
			person.add_linkedin(linkedin_name)
			person.add_twitter(twitter_handle)
			## Populate the Profile ##
			person.auto_populate_fullcontact()
			try:
				person.auto_populate_pipl()
			except SearchAPIError:
				pass
			person.find_twitter_interests()
			person.linkedin_personal_details_scraper()
			person.linkedin_education_scraper()
			person.linkedin_work_scraper()
			person.scrape_linkedin_interests()
			person.scrape_linkedin_volunteering()
			## Return JSON representation of person object ##
			return person.__repr__()
		else:
			return redirect(url_for('people_search'))
	else:
		return render_template('person_search.html')


if __name__ == '__main__':
	app.run(debug = True)
