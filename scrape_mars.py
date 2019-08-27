# Import the necessary components
import pandas as pd
from bs4 import BeautifulSoup as bs
from splinter import Browser
from datetime import datetime
import time


def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {'executable_path': 'chromedriver.exe'}
    return Browser('chrome', **executable_path, headless=False)

def scrape_info():
    browser = init_browser()
    # Visit mars.nasa.gov/news/
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    time.sleep(1)

    # Scrape page into Soup
    html = browser.html
    soup = bs(html, 'html.parser')   
    
    results = soup.find_all('div', class_='list_text')

    # Set the start date time to the millenium 
    latest_time = pd.to_datetime(2000,format='%Y')

    for result in results:
        # Get the date from the news site and convert it to datetime, so that we can get the latest date
        cur_date = result.find(class_='list_date').text
        cur_time = datetime.strptime(cur_date, '%B %d, %Y')
        
        if (cur_time > latest_time):
            latest_date = cur_date
            latest_time = cur_time
            # Get the latest news_title and news_paragraph 
            news_title = result.find(class_='content_title').text
            news_p = result.find(class_='article_teaser_body').text

    # Close the browser after scraping
    browser.quit()


    # Visit jpl.nasa.gov/spaceimages
    browser = init_browser()
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    time.sleep(1)

    html = browser.html
    soup = bs(html, 'html.parser')

    results = soup.find_all("div", class_='img')  
    image_url = results[0].find("img")['src'] 

    base_mars_url = 'https://www.jpl.nasa.gov'
    featured_image_url = base_mars_url + image_url

    # Close the browser after scraping
    browser.quit()


    # Visit Mars twitter  
    browser = init_browser()
    url = 'https://twitter.com/marswxreport?lang=en'
    browser.visit(url)

    time.sleep(1)

    html = browser.html
    soup = bs(html, 'html.parser')

    results = soup.find_all('div', class_='js-tweet-text-container') 
    tweet_list = []

    for result in results:
        #Get the tweet data 
        p_text = result.p.text
        
        # Some of the p.txt has picture reference, take that out, and only get the text 
        if (result.p.a):
            pa_text = result.p.a.text
            tweet_text = p_text.replace(pa_text, "")
        else:
            tweet_text = p_text  
        
        # store the tweet text in the list
        if(p_text):
            tweet_list.append(tweet_text)

    # store the lestest tweet        
    mars_weather =  tweet_list[0]  

    # Close the browser after scraping
    browser.quit()




    url = 'https://space-facts.com/mars'
    tables = pd.read_html(url)
    time.sleep(1)

    # Data is separated in two tables, get the first table 
    df = tables[0]

    # Separate the Mars Data
    df = df.iloc[:,0:2]
    df.columns = ['Description', 'Value']

    # Use Pandas to write the table in HTML format
    html_table = df.to_html(header=True, index=False)
    html_table = html_table.replace('\n', '')



    # Visit astrogeology.usgs.gov
    browser = init_browser()
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)
    time.sleep(1)

    html = browser.html
    soup = bs(html, 'html.parser')

    results = soup.find_all('div', class_='description') 

    title_list = []

    for result in results:
        #Get the title data and add it to the title list 
        title_list.append(result.a.text)

    base_url = 'https://astrogeology.usgs.gov'
    child_url_list = []

    for result in results:
        # Get the relative href 
        child_sub_url = result.a['href']
        
        #Make the full href 
        child_url = base_url + child_sub_url
        
        #Append to the child url list
        child_url_list.append(child_url)

    image_url_list = []

    for sub_url in child_url_list:
        
        #visit the child URL to find the full image
        browser.visit(sub_url)
        html = browser.html
        soup = bs(html, 'html.parser')
        child_results = soup.find(class_='downloads').li 
        image_url = child_results.a['href']
        
        #append to the image URL list
        image_url_list.append(image_url)

    #Make the hemisphere_image_urls dictionary from title_list and image_url_list
    hemisphere_image_urls = []

    for i in range(len(title_list)):
        my_dict = {"title" : title_list[i], "img_url" : image_url_list[i]}
        hemisphere_image_urls.append(my_dict)  

    # Close the browser after scraping
    browser.quit()

    # Store data in a dictionary
    mars_data = {
        "news_title": news_title,
        "news_p": news_p,
        "featured_image_url": featured_image_url,
        "mars_weather":mars_weather,
        "mars_fact_table": html_table,
        "hemisphere_image_urls": hemisphere_image_urls
    }


    # Return results
    return mars_data
