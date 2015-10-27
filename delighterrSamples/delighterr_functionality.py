import datetime
import clearbit
import urllib2
import json
### We need to use ssl to deactivate certificate verification to make fullcontact work ###
import ssl
from pprint import pprint
### Documentation for Pipl Objects and methods at https://pipl.com/dev/reference/ ###
import piplapis.search
from piplapis.search import SearchAPIRequest
from piplapis.data import Person 
from piplapis.data.fields import Name, Gender, Address, Email, Phone, Job, Education
### unirest is the Twitter Keyword finding API library ###
import unirest
### Browser and Scraping Libraries ###
import mechanize
from bs4 import BeautifulSoup
### Scraped Data Manipulation Functions from linkedin_scraper.py ###
from linkedin_scraper import initialize_strings, order_schools, education_summary_combine,\
                             order_companies, work_summary_combine, separate_interests 

#######################
### Support Objects ###
#######################

class SocialMedia():

    def __init__(self, url, service, username=None, bio=None):
        self.info = {
                        "service": None,
                        "url": None,
                        "username": None,
                        "bio": None
                    }

        self.info["service"] = service
        self.info["url"] = url
        self.info["username"] = username
        self.info["bio"] = bio

    def get_json_state(self):
        return self.info

### Used for JSON serializing our SocialMedia Class. Can be extended to other custom classes. ###
class SocialMediaEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, SocialMedia):
            return obj.get_json_state()
        else:
            return json.JSONEncoder.default(self, obj)

### Defines our Delighterr client Profile criteria ###
class Profile():

    id = 0
    
    def __init__(self):
        ## Simple and Dirty Trick to creating unique ID's ##
        ## Every time instance is created, id is incremented ##
        Profile.id += 1

        ## Profile Characteristics ##
        self.id = Profile.id

        self.pic_urls = []

        self.bio = {
    					"name": None,
    					"age": None, 
    					"gender": None,
    				}
    	
        self.location_info = {
    							"currently_lives": None,
    							"currently_works": None,
    							"previously_lived": []
    						 }

        self.education_info = {
                                    "summary": []
    						  }

        self.work_info = {
                            "summary": []
    					 }

        self.social_media = {
                                "accounts": []
                            }

        self.interests = {
                            "keywords": []
                         }
############################################################################################################################

##################
### Main Class ###
################## 

### Will be initialized upon creation of basic contact in App. Contains all the functionality of the Delighterr Service ###

class Contact(Profile):

    def __init__(self, first_name, last_name, email_address=None, phone_number=None):
        Profile.__init__(self)
        self.set_name(first_name, last_name)
        self.set_email(email_address)
        self.set_phone(phone_number)
        self.set_address()
        self.set_jobs()
        ## Creating an initial Query Object to pass to Pipl ##
        self.query_object = Person()
        ## Adding our base initial attributes to the query object ##
        self.query_object.names.extend([self.name])
        self.query_object.emails.extend(self.emails)
        self.query_object.phones.extend(self.phones)

    ## For FrontEnd compatibility, Contact object is evaluated into JSON format ## 
    ## We set the JSON Encoder to our custom encoder to handle serialization of Social Media Objects (We can expand compatibility to other custom objects as needed) ##
    def __repr__(self):
        return json.dumps({"id": self.id, "Personal Information": self.bio, "Location Information": self.location_info, 
                           "Education Info": self.education_info, "Work Info": self.work_info, "Social Media": self.social_media, "Interests": self.interests},
                            indent=2, cls=SocialMediaEncoder, sort_keys=True)

    #############
    ## Setters ##
    #############

    ## Section needs fixing. Empty arrays initialized but need to move the object creation and appending to an adder rather than a setter ##
    def set_name(self, first_name, last_name):
        self.name = Name(first=first_name, last=last_name)
        self.bio["name"] = first_name + " " + last_name

    def set_email(self, email_address):
        self.emails = []
        if email_address is not None:
            self.emails.append(Email(email_address))

    def set_phone(self, phone_number):
        self.phones = []
        if phone_number is not None:
            self.phones.append(Phone(number=phone_number))

    def set_address(self):
        self.addresses = []

    def set_jobs(self):
        self.jobs = []
##########################################################################################################################

    #######################################
    ## Configuring the Pipl Query Object ##
    #######################################

    def add_email_to_query(self, email_address):
        if email_address and email_address not in self.query_object.emails:
            self.query_object.emails.append(Email(email_address))
            self.emails.append(Email(email_address))

    def add_phone_to_query(self, phone_number):
        contains = False
        for item in self.query_object.phones:
            if item['number'] == phone_number:
                contains = True
        if not contains:
            self.query_object.phones.append(Phone(number=phone_number))

    def add_address_to_query(self, country=None, state=None, city=None):
        if country is not None:
            if state and city:
                self.addresses.append(Address(country=country, state=state, city=city))
                self.query_object.addresses.append(Address(country=country, state=state, city=city))
            elif state:
                self.addresses.append(Address(country=country, state=state, city=city))
                self.query_object.addresses.append(Address(country=country, state=state, city=city))
                                
    def add_job_to_query(self, title=None, organization=None):
        if title and organization:
            self.jobs.append(Job(title=title, organization=organization))
            self.query_object.jobs.append(Job(title=title, organization=organization))
        elif title:
            self.jobs.append(Job(title=title))
            self.query_object.jobs.append(Job(title=title))
        elif organization:
            self.jobs.append(Job(organization=organization))
            self.query_object.jobs.append(Job(organization=organization))
##########################################################################################################################

    #######################################
    ## Lookup and Autopopulation Methods ##
    #######################################

    ##################
    ## API Services ##
    ##################

    def person_lookup(self, service):
        if service == 'fullcontact':
            fullcontact_key = '50bd8e5a1133dd29'
            #context = ssl._create_unverified_context()
            try:
                email = self.query_object.emails[0].address.encode("utf-8")
            except IndexError:
                return None
            try:
                url = "https://api.fullcontact.com/v2/person.json?email=" + email + "&apiKey=" + fullcontact_key
                #response = urllib2.urlopen(url, context=context)
                response = urllib2.urlopen(url)
                data_obj = response.read()
                json_obj = json.loads(data_obj)
                return json_obj
            except urllib2.HTTPError as err:
                if err.code == 404:
                    return
        elif service == 'pipl':
            pipl_api_key ='wzcdrge37w2ktmrcnvy8gs8c'
            request = SearchAPIRequest(api_key=pipl_api_key, person=self.query_object)
            response = request.send()
            data = response.to_dict()
            return data
        else:
            return "Service not supported. Please Try Again"

    ## Auto-population assumes a priority of Pipl and then Fullcontact. This can be altered ##
    ## Pipl is much more comprehensive in terms of Personal Information ##
    def auto_populate_pipl(self):
        api_data = self.person_lookup("pipl")
        ## Name ##
        if not self.bio['name']: 
            try:
                self.bio['name'] = api_data['person']['names'][0]['display'].encode("utf-8")
            except KeyError:
                pass
        ## Age ##
        if not self.bio['age']: 
            try:
                self.bio['age'] = api_data['person']['dob']['display'][:2]
            except KeyError:
                try:
                    now_year = datetime.date.today().year
                    start_year = int(api_data['person']['dob']['date_range']['start'][:4])
                    end_year = int(api_data['person']['dob']['date_range']['end'][:4])
                    self.bio['age'] = str(now_year - end_year) + " - " + str(now_year - start_year)
                except KeyError:
                    pass
        ## Gender ##
        if not self.bio['gender']:    
            try:
                self.bio['gender'] = api_data['person']['gender']['content'].encode("utf-8")
            except KeyError:
                pass
        ## Current Location ##
        if not self.location_info['currently_lives']:    
            try:
                self.location_info['currently_lives'] = api_data['person']['addresses'][0]['display'].encode("utf-8")
            except KeyError:
                pass
            try:
                work_location = None
                for place in api_data['person']['addresses']:
                    if place['@type'] == 'work':
                        work_location = place['display'].encode("utf-8")
                        break
                self.location_info['currently_works'] = work_location
            except KeyError:
                pass
        ## Previous Locations ##
        if not self.location_info['previously_lived']:    
            try:
                for place in api_data['person']['addresses']:
                    if place['display'] not in self.location_info['previously_lived']:
                        self.location_info['previously_lived'].append(place['display'].encode("utf-8"))
            except KeyError:
                pass
        ## Education Info ##
        if not self.education_info['summary']:    
            try:
                for item in api_data['person']['educations']:
                    self.education_info['summary'].append(item['display'].encode("utf-8"))
            except KeyError:
                pass   
        ## Maybe need to break down summaries into individual fields for automation? Education object? ##
        ## Work Info ##
        if not self.work_info['summary']:    
            try:
                for job in api_data['person']['jobs']:
                    self.work_info['summary'].append(job['display'].encode("utf-8"))
            except KeyError:
                pass   
        ## Maybe need to break down summaries into individual fields for automation? Job object? ##
        ## For now commenting out Pipl Social Media collector because Fullcontact Always does at least as well ##
        ## Social Media ##
        """try:
            for account in api_data['person']['urls']:
                for existing in self.social_media['accounts']:
                    if existing.info['service'] == account['@name']:
                        break
                    else:
                        self.social_media['accounts'].append(SocialMedia(account['url'], account['@name']))
        except KeyError:
            pass"""

    ## FullContact works best for the tracking of Social Media Profiles, however this function has been implemented as a complete auto populator ##
    def auto_populate_fullcontact(self):
        api_data = self.person_lookup("fullcontact")
        if api_data:
            ## Bio Information ##
            try:
                self.bio['name'] = api_data['contactInfo']['fullName']
            except KeyError:
                pass
            try:
                self.bio['age'] = api_data['demographics']['age']
            except KeyError:
                try:
                    self.bio['age'] = api_data['demographics']['ageRange']
                except KeyError:
                    pass
            try:
                self.bio['gender'] = api_data['demographics']['gender']
            except KeyError:
                pass
            ## Location Information ##
            try:
                self.location_info['currently_lives'] = api_data['demographics']['locationGeneral']
            except KeyError:
                try:
                    self.location_info['currently_lives'] = api_data['demographics']['locationDeduced']['deducedLocation']
                except KeyError:
                    pass
            ## Employment Information ##
            try:
                for item in api_data['organizations']:
                    try:
                        title = item['title']
                    except KeyError:
                        title = ""
                    try:
                        company = item['name']
                    except KeyError:
                        company = ""
                    if title or company:
                        self.work_info['summary'].append(title + " " + "@ " + company)
                        if item['current'] == 'true':
                            self.location_info['currently_works'] = company
            except KeyError:
                pass
            ## Social Media Information ## 
            try:
                for item in api_data["socialProfiles"]:
                    ## Populate Initializer fields ##
                    try:
                        url = item["url"].encode("utf-8")
                    except KeyError:
                        url = None
                    try:
                        service = item["typeName"].encode("utf-8")
                    except KeyError:
                        service = None 
                    try:
                        username = item["username"].encode("utf-8")
                    except KeyError:
                        username = None
                    try:
                        bio = item["bio"].encode("utf-8")
                    except KeyError:
                        bio = "Not Provided"
                    ## Create Social Media Object ##
                    if service is not None:
                        social_media_object = SocialMedia(url, service, username, bio)
                        self.social_media["accounts"].append(social_media_object)
            except KeyError:
                pass

    ####################
    ## Field Checkers ##
    ####################

    ## These functions check if certain social media accounts exist and return True/False with the appropriate username ##
    ## Can use these methods to check how effective our Piple and FullContact searches were ##
    def has_twitter(self):
        has_twitter = False
        twitter_handle = None
        for account in self.social_media["accounts"]:
            if account.info["service"] == "Twitter":
                has_twitter = True
                twitter_handle = account.info["username"]
        return has_twitter, twitter_handle

    def has_linkedin(self):
        has_linkedin = False
        url = None
        for account in self.social_media["accounts"]:
            if account.info["service"] == "LinkedIn":
                has_linkedin = True
                url = account.info["url"]
        return has_linkedin, url

    ######################
    ## Add Social Media ##
    ######################

    def add_linkedin(self, linkedin_name):
        has_linkedin, linkedin_url = self.has_linkedin()
        if not has_linkedin:
            url = "https://www.linkedin.com/in/" + linkedin_name
            self.social_media["accounts"].append(SocialMedia(url, "LinkedIn", linkedin_name))

    def add_twitter(self, username):
        has_twitter, twitter_handle = self.has_twitter()
        if not has_twitter:
            url = "https://twitter.com/" + username
            self.social_media["accounts"].append(SocialMedia(url, "Twitter", username))

    ################################
    ## Scraping/Crawling Services ##
    ################################

    def linkedin_scrape_setup(self):
        ## Determine if user has linkedin account and find the username ##
        has_linkedin, linkedin_url = self.has_linkedin()
        ## If the user has linkedin, we initiate the scraping process ##        
        if has_linkedin:
            ## We configure a browser object from the mechanize library ##
            br = mechanize.Browser()
            br.set_handle_robots(False)
            br.addheaders=[('User-agent', 'Firefox')]
            ## Navigate to linkedin website and add credentials to view public profile info ##
            br.open("http://www.linkedin.com")
            br.form = list(br.forms())[0]
            br['session_key'] = 'arjungupta291@berkeley.edu'
            br['session_password'] = '*fake_password*'
            br.submit()
            response = br.response()
            ## Navigate to our user's page ##
            response = br.open(linkedin_url)
            html_response = response.read()
            ## Close Browser ##
            br.close()
            ## return an html object to be scraped ##
            return html_response

    def linkedin_personal_details_scraper(self):
        ## Collect the linkedin user HTML object ## 
        html_object = self.linkedin_scrape_setup()
        ## Only proceed if user has linkedin ##
        if html_object:
            ## Initialize our scraping object ##
            soup = BeautifulSoup(html_object, "html.parser")
            ## Find the HTML location of the personal details section ##
            personal_details_location = soup.find_all('table', {'id': 'personal-info-view'})
            ## Parse the table data to isolate the fields provided ##
            fields = [info.find_all('tr') for info in personal_details_location]
            ## Find the titles of the fields found ##
            try:
                headers_html = [field.find_all('th', {'scope': 'row'}) for field in fields[0]]
            except IndexError:
                return
            ## Extract the data corresponding to those titles ##
            try:
                information_html = [field.find_all('td') for field in fields[0]]
            except IndexError:
                return 
            ## Get text from the headers and information HTML extracted ##
            headers = [header[0].get_text() for header in headers_html]
            information = [item[0].get_text() for item in information_html]
            ## Add the personal details to our bio dictionary in our Profile object ##
            for header, info in zip(headers, information):
                self.bio[header] = info

    def linkedin_education_scraper(self):
        ## Collect the linkedin user HTML object ## 
        html_object = self.linkedin_scrape_setup()
        ## Only proceed if user has linkedin ##
        if html_object:
            ## Initialize our scraping object ##
            soup = BeautifulSoup(html_object, "html.parser")
            ## Find the HTML location of the schools info and extract the text into an array ##
            schools_location = soup.find_all('a', {'title': 'More details for this school'})
            schools = [school.get_text() for school in schools_location]
            ## Find the HTML location of the degrees info and extract the text into an array ##
            degree_location = soup.find_all('span', {'class': 'degree'})
            degrees = [degree.get_text() for degree in degree_location]
            ## Find the HTML location of the majors info and extract the text into an array ##
            major_location = soup.find_all('span', {'class': 'major'})
            majors = [major.get_text() for major in major_location]
            ## Filter the array of schools to account for multiple occurrences and other glitches in the linkedin HTML ##
            accurate_schools = order_schools(schools)
            ## Form education summaries by concatenating appropriate entries from the degrees, majors, schools arrays ##
            linkedin_education_array = education_summary_combine(degrees, majors, accurate_schools)
            ## Populate the education_info section of our profile with our extracted data ##
            self.education_info["summary"] = linkedin_education_array

    def linkedin_work_scraper(self):
        ## Collect the linkedin user HTML object ## 
        html_object = self.linkedin_scrape_setup()
        ## Only proceed if user has linkedin ##
        if html_object:
            ## Initialize our scraping object ##
            soup = BeautifulSoup(html_object, "html.parser")
            ## Find the HTML location of the employment summary section ##
            work_summary = soup.find_all('div', {'id': 'background-experience'})
            ## Find the specific sections for each position held ##
            work_items = [work.find_all('div', {'class': ['current-position', 'past-position']}) for work in work_summary]
            ## We need to flatten the nested array results are returned in ##
            try:
                flattened_work_items = [item for item in work_items[0]]
            except IndexError:
                return 
            ## The companies need to be ordered coreectly because of HTML setup differences for different companies ##
            companies_in_order = order_companies(flattened_work_items)
            ## Find the HTML location of the job titles and then grab the text ##
            try:
                work_titles_location = work_summary[0].find_all('a', {'title': 'Find others with this title'})
            except IndexError:
                return 
            work_titles = [work.get_text() for work in work_titles_location]
            ## Form our work entry summaries array by concatenating appropriate entries from titles, companies arrays ##
            linkedin_employment_array = work_summary_combine(work_titles, companies_in_order)
            ## Populate/Override the work_info section of our profile with linkedin data ##
            self.work_info["summary"] = linkedin_employment_array
            self.location_info["currently_works"] = linkedin_employment_array[0]

    ##################################
    ## Methods to Collect Interests ##
    ##################################

    def find_twitter_interests(self):
        ## Determine if user has twitter account and find the username ##
        has_twitter, twitter_handle = self.has_twitter()
        ## If the user has twitter, use the API to extract keywords ##
        if has_twitter:
            url = "https://twitter-vugraph.p.mashape.com/vugraph?app_key=dee1eb769deb1c7ed850fc2ab18c31e5&token=3hbv1ionxeoyl9pzsy49e7bl5yh45i830nxuono4vzq309ii80whj9mu022rwgd3&twitterhandle=" + twitter_handle
            response = unirest.get(url, 
                                   headers={"X-Mashape-Key": "phAoZJP1komshclw1bgnZ6jr459np1d0zpTjsn5euRlhVz2thw",
                                            "Accept": "application/json"})
            ## Parse the response object to obtain JSON object ##
            json_obj = response.body
            ## Add the keywords to the Contact profile object under interests ##
            for item in json_obj["keywords"]:
                if item["weight"] >= 15:
                    self.interests["keywords"].append(item["keyword"])

    def scrape_linkedin_interests(self):
        ## Gather the user specific HTML object we need ##
        html_object = self.linkedin_scrape_setup()
        ## Only proceed if the user has linkedin ##
        if html_object:
            ## Initialize our BeautifulSoup object to scrape/crawl ##
            soup = BeautifulSoup(html_object, "html.parser")
            ## Find the HTML location of the interest section ##
            interest_section = soup.find_all('li', {'id': 'interests'})
            ## Pick out the HTML location of the specific interest keywords ##
            interest_location = [section.find_all('a', {'title': 'Find users with this keyword'}) for section in interest_section]
            ## Flatten the nested nested array that results are returned in ##
            try:
                flattened_interest_location = [item for item in interest_section[0]]
            except IndexError:
                return 
            ## Omit the useless entries and grab the interest keywords ##
            try:
                one_string_array_interests = [interest.get_text() for interest in flattened_interest_location][1:]
            except IndexError:
                return
            ## We are returned one long string of interests so we parse it to separate the keywords ##
            try:
                linkedin_interests = separate_interests(one_string_array_interests[0])
            except IndexError:
                return
            ## Add the linkedin interest keywords to the existing array in our Profile ##
            self.interests["keywords"].extend(linkedin_interests)

    def scrape_linkedin_volunteering(self):
        ## Gather the user specific HTML object we need ##
        html_object = self.linkedin_scrape_setup()
        ## Only proceed if the user has linkedin ##
        if html_object:
            ## Initialize our BeautifulSoup object to scrape/crawl ##
            soup = BeautifulSoup(html_object, "html.parser")
            ## Find the HTML location of the volunteering/causes section ##
            volunteer_section = soup.find_all('ul', {'class': 'volunteering-listing'})
            ## Pick out the section of HTML which lists causes ##
            causes_html = [cause.find_all('li') for cause in volunteer_section]
            ## Extract the causes in text format ##
            try:
                causes = [item.get_text() for item in causes_html[0]]
            except IndexError:
                return
            ## Add the linkedin volunteering/cause keywords to our Profile interest section ##
            self.interests["keywords"].extend(causes)


## Module Tester being commented out for web app backend functionality ##
"""if __name__ == '__main__':

    first_name = str(raw_input("Enter First Name: "))
    last_name = str(raw_input("Enter Last Name: "))
    email = str(raw_input("Enter Email: "))
    person = Contact(first_name, last_name, email)
    person.auto_populate_fullcontact()
    person.auto_populate_pipl()
    person.find_twitter_interests()
    person.linkedin_personal_details_scraper()
    person.linkedin_education_scraper()
    person.linkedin_work_scraper()
    person.scrape_linkedin_interests()
    person.scrape_linkedin_volunteering()
    pprint(person, width=1)"""
                
