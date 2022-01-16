from distutils.errors import LinkError
import requests
from bs4 import BeautifulSoup as bs
import tqdm

userAgent = "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.111 Safari/537.36"
headers = {'User-Agent': userAgent}
dict_href_links = {}
words = dict()
ALO = False

def rm_polish(w):
    return w.replace('ą', 'a').replace('ć', 'c').replace('ę', 'e').replace('ł', 'l').replace('ń', 'n').replace('ó', 'o').replace('ś', 's').replace('ź', 'z').replace('ż', 'z')

def find_third_slash(url) :
    occur = 0;
    for i in range(len(url)) :
        if(url[i] == "/") :
            occur += 1;
        if (occur == 3) :
            return i;
    return -1;

def get_links(website_link):
    try:
        page = requests.get(website_link, headers = headers, timeout = 1, verify = (not ALO))
        page.raise_for_status()
    except:
        if(ALO):
            page = requests.get(website_link, headers = headers, timeout = 1, verify = (not ALO))
            if(bs(page.content, 'html.parser').get_text() == ''):
                return -1
    effect = bs(page.content, 'html.parser')
    for link in effect.find_all("a", href = True):
        if(str(link["href"]).find('#') == -1):
            if(str(link["href"]).startswith(website_link)):
                if(link["href"] not in dict_href_links):
                    dict_href_links[link["href"]] = "Not-checked"
            elif(str(link["href"]).startswith("/")):
                if(website_link + link["href"][1:] not in dict_href_links):
                    dict_href_links[website_link[:find_third_slash(website_link)] + link["href"]] = "Not-checked"
            else:
                if(not str(link["href"]).startswith("https://") and not str(link["href"]).startswith("http://") and not str(link["href"]).startswith("#") and website_link + link["href"] not in dict_href_links):
                    dict_href_links[website_link[:find_third_slash(website_link)] + '/' + link["href"]] = "Not-checked"
    return 0

def remove_broken_urls():
    for link in tqdm.tqdm(list(dict_href_links)):
        try:
            page = requests.get(link, headers=headers, timeout=0.5, verify = (not ALO))
            page.raise_for_status()
        except:
            if(ALO):
                page = requests.get(link, headers=headers, timeout=0.5, verify = (not ALO))
                if(bs(page.content, 'html.parser').get_text() == ''):
                    dict_href_links.pop(link)

def find_all_links(depth):
    for i in range(depth):
        print("Recursion level:", i)
        for link in tqdm.tqdm(list(dict_href_links)):
            if(dict_href_links[link] == "Not-checked"):
                if(get_links(link) != -1):
                    dict_href_links[link] = "Checked"
                else:
                    dict_href_links.pop(link)
        print()
    print("Removing broken urls:")
    remove_broken_urls()

inp = input("Enter the website address for analysis: ")
depth = input("Enter maximum depth of recursion (recommended value is from 0 to 3): ")
depth = int(depth)
if(inp[:8] != "https://" and inp[:7] != "http://"):
    inp = "https://" + inp
if(not inp.endswith('/')):
    inp += '/'
page_url = inp
if(page_url.startswith("https://liceum.pwr.edu.pl/")):
    ALO = True

try:
    r = requests.get(page_url)
except:
    page_url = "http://" + page_url[8:]

try:
    r = requests.get(page_url)
except:
    print("Please enter existing url address!")
    exit()

dict_href_links[page_url] = "Not-checked"
print()
print()
print("   SCRAPING URLS:")
find_all_links(depth)
print()
print("   COUNTING WORDS:")
for link in tqdm.tqdm(list(dict_href_links)):
    page = requests.get(link, headers=headers, verify = (not ALO))
    effect = bs(page.content, 'html.parser').get_text(separator=' ').rstrip()
    splitted = effect.split()
    for word in splitted:
        word = rm_polish(word.lower())
        word = ''.join(filter(str.isalpha, word))
        if(len(word) <= 1):
            continue
        if(word in words):
            words[word] += 1
        else:
            words[word] = 1

sorted_keys = sorted(words, key = words.get)
print("10 most used words on ", page_url)
print()
for i in range(min(50, len(sorted_keys))):
    print('#', end='')
    print(i+1, '\t', words[sorted_keys[-i-1]], 'times\t', sorted_keys[-i-1])
