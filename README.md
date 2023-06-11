# stockinerary

A web scraper to scrape from NYSE website.

## Installation and Usage

- `git clone https://github.com/bigyanse/stockinerary.git`
- `cd stockinerary`
- `python -m venv venv`
- `source venv/bin/activate`
- `pip install -r requirements.txt`
- `python main.py`

## Files Info

- `{stack_exchange}_links.csv`: file containing company profile name, code, link to profile page. eg: `nyse_links.csv`
- `{stack_exchange}_profiles.csv`: file containing company data: company_name, company_code, market_capitalization, current_price, volume_traded, high_price, low_price, open_price, previous_close_price, date. eg: `nyse_profiles.csv`
- `resume.txt`: file containing index to continue from in case of error
