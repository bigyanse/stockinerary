from scraper.Scraper import NYSE

nyse = NYSE(30)
nyse.get_company_profiles(scrape_links=False)
