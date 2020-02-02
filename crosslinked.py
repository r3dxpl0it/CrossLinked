#!/usr/bin/env python3

import argparse
import requests
from sys import exit
from time import sleep
from random import choice
from threading import Thread
from bs4 import BeautifulSoup
from unidecode import unidecode
requests.packages.urllib3.disable_warnings()

USER_AGENTS = [line.strip() for line in open('user_agents.txt')]

########################################################
# Class to scrape Google and Bing search engine looking
# for Linkedin employees at a certain organization
########################################################
class ScrapeEngine():
    URL = {'google': 'https://www.google.com/search?q=site:linkedin.com/in+"{}"&num=100&start={}',
           'bing': 'https://www.bing.com/search?q=site:linkedin.com/in+"{}"&first={}'}

    def __init__(self):
        self.linkedin = {}
        self.running = True

    def timer(self, time):
        sleep(time)
        self.running = False

    def search(self, search_engine, company_name, timeout, jitter):
        self.running = True  # Define search as "running" after init(), not used in DNS_Enum

        Thread(target=self.timer, args=(timeout,), daemon=True).start()  # Start timeout thread

        self.search_links = 0  # Total Links found by search engine
        self.name_count   = 0  # Total names found from linkedin
        found_names       = 0  # Local count to detect when no new names are found
        self.attempts     = 0
        while self.running:
            # End on timeout OR when no more LinkedIn names are found
            if self.search_links > 0 and found_names == self.name_count:
                if self.attempts > 30 : 
                    return self.linkedin
                else : 
                    self.attempts += 1 


            found_names = self.name_count
            try:
                self.name_search(search_engine, self.search_links, company_name, jitter)
            except KeyboardInterrupt:
                print("[!] Key event detected, closing...")
                exit(0)
            except Exception as e:
                if debug:
                    print("[!] Debug: {}".format(str(e)))
        return self.linkedin

    def name_search(self, search_engine, count, company_name, jitter):
        # Search for links in HTML
        url = self.URL[search_engine].format(company_name, count)
        print("[*] {} : {}".format(self.name_count, url))

        for link in get_links(get_request(url, 3)):
            # Count search result links to increment URL?num= counter
            url = str(link.get('href')).lower()
            # Identify LinkedIn data and parse names
            if (search_engine+".com") not in url and not url.startswith("/"):
                self.search_links += 1
                if "linkedin.com/in" in url and self.extract_linkedin(link, company_name) :
                    self.name_count += 1
        sleep(jitter)

    def extract_linkedin(self, link, company_name):
       

        if safe and company_name.lower() not in link.text.lower():
            return False
        try:
            # Sanitize input
            x = link.text.split("|")[0]
            x = x.split("...")[0]
            x = unidecode(x)

            # Extract Name (if title provided)
            if "–" in x:
                name = link.text.split("–")[0].rstrip().lstrip()
            elif "-" in x:
                name = link.text.split("-")[0].rstrip().lstrip()
            elif "|" in x:
                name = link.text.split("|")[0].rstrip().lstrip()
            else:
                name = x

            try:
                # Quick split to extract title, but focus on name
                title = link.text.split("-")[1].rstrip().lstrip()
                if "..." in title:
                    title = title.split("...")[0].rstrip().lstrip()
                if "|" in title:
                    title = title.split("|")[0].rstrip().lstrip()
            except:
                title = "N/A"


            tmp = name.split(' ')
            name = ''.join(e for e in tmp[0] if e.isalnum()) + " " + ''.join(e for e in tmp[1] if e.isalnum())

            # Catch 1st letter last name: Fname L.
            tmp = name.split(' ')
            if len(tmp[0]) <= 1 or len(tmp[-1]) <=1:
                raise Exception("\'{}\' Failed name parsing".format(link.text))
            elif tmp[0].endswith((".","|")) or tmp[-1].endswith((".","|")):
                raise Exception("\'{}\' Failed name parsing".format(link.text))

            if name not in self.linkedin:
                
                       
                linkedin_link = link.text.split('linkedin.com/')

                try : 
                    linkedin_link = str(link).split('href="')[1].split('">')[0]
                except : 
                    linkedin_link = None 
                if debug : 
                    print("[*] Found: {}".format(name) ,linkedin_link)
                
                self.linkedin[name] = {}
                self.linkedin[name]['link'] = linkedin_link

                return True

        except Exception as e:
            if debug:
                print("[!] Debug: {}".format(str(e)))
        return False

def get_links(raw_response):
    # Returns a list of links from raw requests input
    links = []
    soup = BeautifulSoup(raw_response.content, 'html.parser')
    for link in soup.findAll('a'):
        try:
            links.append(link)
        except:
            pass
    return links

def get_request(link, timeout):
    # HTTP(S) GET request w/ user defined timeout
    head = {
        'User-Agent': '{}'.format(choice(USER_AGENTS)),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'}
    return requests.get(link, headers=head, verify=False, timeout=timeout)

import json 

def main(args):
    found_names = {}
    search = ['bing']
    for site in search:
        print("[*] Searching {} for valid employee names at {}".format(site, args.company_name))
        lkin = ScrapeEngine().search(site, args.company_name, args.timeout, args.jitter)
        if lkin:
            for name, data in lkin.items():
                try:
                    if name not in found_names:
                        found_names[name] = data['link']

                except Exception as e:
                    if debug:
                        print("[!] Debug: {}".format(str(e)))
    
    print("[+] {} unique names found!".format(len(found_names)))
    with open(args.outfile, 'w') as outfile:
        json.dump(found_names, outfile)

if __name__ == '__main__':
    VERSION = "0.0.5"
    args = argparse.ArgumentParser(description="", formatter_class=argparse.RawTextHelpFormatter, usage=argparse.SUPPRESS)
    args.add_argument('--debug', dest="debug", action='store_true',help=argparse.SUPPRESS)
    args.add_argument('-t', dest='timeout', type=int, default=25,help='Timeout [seconds] for search threads (Default: 25)')
    args.add_argument('-j', dest='jitter', type=float, default=0,help='Jitter for scraping evasion (Default: 0)')
    args.add_argument('-o', dest='outfile', type=str, required = True ,help='Change name of output file (default: names.txt')
    args.add_argument('-s', "--safe", dest="safe", action='store_true',help="Only parse names with company in title (Reduces false positives)")
    args.add_argument('-v', dest="verbose", action='store_true', help="Show names and titles recovered after enumeration")
    args.add_argument(dest='company_name', nargs='+', help='Target company name')
    args = args.parse_args()

    if '.json' not in args.outfile : 
        args.outfile = args.outfile + '.json'

    safe = args.safe
    debug = args.debug
    args.company_name = args.company_name[0]

    try:
        main(args)
    except KeyboardInterrupt:
        print("[!] Key event detected, closing...")
        exit(0)