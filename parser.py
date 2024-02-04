import requests
import json
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
import time


api_key = "[GOOGLE API KEY]"
search_engine_id = "[GOOGLE SEARCH ENGINE ID]"

def search_for_website(company_name):
	search_url = "https://www.googleapis.com/customsearch/v1"
	params = {
		"q": company_name + "Providence official website",
		"key": api_key,
		"cx": search_engine_id,
		"num": 3
	}

	response = requests.get(search_url, params=params)

	if response.status_code == 200:
		result = json.loads(response.text)
		if 'items' in result and len(result['items']) > 0:
			return result['items'][0]['link']
		else:
			print(f"No results found for {company_name}")
			return None
	else:
		print(f"Search API Error for {company_name}")
		return None

email_regex = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
social_media_domains = ["facebook.com", "twitter.com", "linkedin.com", "instagram.com"]

def find_contact_methods(url, visited=None, max_depth=2, current_depth=0,):

	contact_methods = {"emails": set(), "forms": set(), "socials": set()}
	if visited is None:
		visited = set()
	if url in visited or current_depth > max_depth:
		return contact_methods
	visited.add(url)

	try:
		response = requests.get(url)
		if response.status_code == 200:
			soup = BeautifulSoup(response.text, 'html.parser')
			text = soup.get_text()

			# emails
			# print("EMAIL")
			emails = set(re.findall(email_regex, text))
			contact_methods["emails"].update(emails)

			# forms
			forms = set(soup.find_all('form'))
			for form in forms:
				action = form.get('action')
				if action:
					contact_methods["forms"].add(urljoin(url, action))

			# social media
			links = soup.find_all('a', href=True)

			for link in links:
				
				href = link['href']
				if any(domain in href for domain in social_media_domains):
					# print("SOCIAL")
					contact_methods["socials"].add(href)
				else:
					next_page = urljoin(url, href)
					if not next_page.startswith(('http://', 'https://')) or name not in next_page:
						break
					deeper_contacts = find_contact_methods(next_page, visited, max_depth, current_depth+1)
					for key in contact_methods:
						contact_methods[key].update(deeper_contacts[key])

			return contact_methods
		else:
			print(f"Failed to access {url}")
			return set()
	except requests.RequestException as e:
		print(f"Error during reqest to {url}: {str(e)}")
		return set()

site_names = [
"jahunger"
]

for name in site_names:
	website = search_for_website(name)
	contacts = find_contact_methods(website)
	print(name)
	print(website)
	print(contacts)

