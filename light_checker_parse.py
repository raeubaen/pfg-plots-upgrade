from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from bs4 import BeautifulSoup
import time

# URL to fetch
url = "https://ecalmon.web.cern.ch/ecalmon/mirror/light-checker/"

# Firefox options
options = Options()
options.add_argument("--headless")                # explicitly headless
options.headless = True
options.binary_location = "/usr/bin/firefox"  # explicit Firefox binary path

# Explicit geckodriver path
service = Service(executable_path="/afs/cern.ch/work/r/rgargiul/gecko/geckodriver")

# Start WebDriver
driver = webdriver.Firefox(service=service, options=options)

try:
    driver.get(url)
    time.sleep(5)  # wait for JS
    html = driver.page_source
finally:
    driver.quit()

soup = BeautifulSoup(html, "html.parser")

p1 = "<p><b>Laser disk occupancy:</b></p>"

p2 = "<p><b>Last insertions in laser DB:</b></p>"

print(p1)
# Find the table by its ID
table = soup.find("table", id="disk_occupancy_table")

# Find all rows in the disk table
for row in table.find_all("tr"):
    # Get all cells in the row
    cells = row.find_all("td")
    # Skip empty rows
    if not cells:
        continue
    # Check if first column contains 'localdata/disk0'
    if "localdata/disk0" in cells[0].get_text():
        # Get 2nd and 3rd column text
        col2 = cells[1].get_text(strip=True)
        col3 = cells[2].get_text(strip=True)
        # Print them separated by a tab (or space)
        print(f"<p>srv-c2f38-10-01/localdata/disk0: {col2} {col3.replace(',','')}</p><br>")
        break  # stop after the first matching row

# Find the div containing the table
div = soup.find("div", id="db_wrting_lastRunProcessed")

# Find the table inside that div
table = div.find("table")
print(p2)
# Print full HTML of the table
print(table.prettify())
