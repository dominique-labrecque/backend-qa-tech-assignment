import requests
import unittest
import os
  
"""
== General ==
The objective of this exercise is to create automated tests to validate some basic functionalities of
Discogs' artists search mechanism.
  
The search function required credential. We use the basic key/secret in this case to simplify the
process. The key/secret values are provided in the test class setup function.
  
Search endpoint documentation API:
    https://www.discogs.com/developers#page:database,header:database-search
 
 
== Test Framework ==
 
The test will use the Python's unit test framework
 
Python unit Test :
    https://docs.python.org/3/library/unittest.html
 
== Tests Objectives ==
 
As per the search API specs, we want to cover the following basic tests cases.
 
- Access :
    - Successful search when authorize.
    - Check no success if credential are bad or invalid.
 
- Per page result pagination validation
    - If no limit specified, we return default number of record per pages.
    - If a specific limit is specified, the api must return the requested number of record per pages.
    - The api will return a maximun number of result per pages, even if we provide a large limit value.

== IMPORTANT ==

A key/secret pair will be share upon request to do the challenge.

Otherwise it's possible to get a personnal one upon registering with Discogs.

"""
 
class TestDiscogs(unittest.TestCase):
 
    key = os.environ['DISCOGS_KEY']
    secret = os.environ['DISCOGS_SECRET']
    discog_url = "https://api.discogs.com/database"
    default_per_page = 50
    max_per_page = 100
 
    @classmethod
    def setUpClass(self):
        auth = "Discogs key={}, secret={}".format(self.key, self.secret)
        self.headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": auth
            }

    def test_successful_search_when_authorized(self):
        res = requests.get("{}/search".format(self.discog_url), headers=self.headers)
        self.assertEqual(res.status_code, 200, 'status code = {}'.format(res.status_code))
        self.assertIn('pagination', res.json())
        self.assertIn('results', res.json())

    def test_unsuccessful_without_auth(self):
        local_headers = self.headers
        local_headers.pop("Authorization")
        res = requests.get("{}/search".format(self.discog_url), headers=local_headers)
        self.assertEqual(res.status_code, 401, f'status code = {res.status_code}')
        self.assertEqual(res.json()['message'], 'You must authenticate to access this resource.')

    def test_unsuccessful_bad_credentials(self):
        local_headers = self.headers
        local_headers['Authorization'] = "Discogs key=badkey123, secret=badsecret456"
        res = requests.get("{}/search".format(self.discog_url), headers=local_headers)
        self.assertEqual(res.status_code, 401, f'status code = {res.status_code}')
        self.assertRegex(res.json()['message'], r'Invalid consumer key/secret')

    def test_per_page_return_default_if_not_specified(self):
        res = requests.get("{}/search".format(self.discog_url), headers=self.headers)
        pagination = res.json()["pagination"]
        results = res.json()["results"]
        self.assertEqual(pagination["per_page"], self.default_per_page)
        self.assertEqual(len(results), self.default_per_page)

    def test_per_page_return_specified(self):
        res = requests.get(f"{self.discog_url}/search?per_page={self.max_per_page}", headers=self.headers)
        pagination = res.json()["pagination"]
        results = res.json()["results"]
        self.assertEqual(pagination["per_page"], self.max_per_page)
        self.assertEqual(len(results), self.max_per_page)

    def test_per_page_return_max_if_specified_exceeds_max(self):
        per_page = self.max_per_page + 1
        res = requests.get(f"{self.discog_url}/search?per_page={per_page}", headers=self.headers)
        pagination = res.json()["pagination"]
        results = res.json()["results"]
        self.assertEqual(pagination["per_page"], self.max_per_page)
        self.assertEqual(len(results), self.max_per_page)

 
if __name__ == '__main__':
    unittest.main()
