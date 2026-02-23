import traceback

try:
  from selenium import webdriver
  from selenium.webdriver.firefox.options import Options
  from selenium.webdriver.firefox.service import Service
  from bs4 import BeautifulSoup
  import time
  import sys
  import re
  from datetime import datetime, timedelta

  DISK_PERC = 90
  DELTA_MAX = 240

  oms_string = sys.argv[1]

  # Extract start datetime
  start_match = re.search(r"Start:\s+(\d{2}/\d{2}/\d{2})\s+(\d{2}:\d{2})", oms_string)
  duration_match = re.search(r"Duration:\s+(\d+)\s+min", oms_string)

  if not start_match or not duration_match:
      raise ValueError("Could not parse input string")

  start_str = f"{start_match.group(1)} {start_match.group(2)}"
  duration_minutes = int(duration_match.group(1))

  # Convert to datetime
  start_dt = datetime.strptime(start_str, "%d/%m/%y %H:%M")

  # Compute end time
  end_dt = start_dt + timedelta(minutes=duration_minutes)

  print("DEBUG Start:", start_dt)
  print("DEBUG End:", end_dt)


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
          print(f"DEBUG <p>srv-c2f38-10-01/localdata/disk0: {col2} {col3.replace(',','')}</p><br>")
          if int(col3.replace("% used,", "")) > DISK_PERC:
            print(f"<br><p> WARNING: srv-c2f38-10-01/localdata/disk0 occupancy >= {DISK_PERC}%</p>")
            print(p1)
            print(table.prettify())

          break  # stop after the first matching row

  # Find the div containing the table
  div = soup.find("div", id="db_wrting_lastRunProcessed")

  # Find the table inside that div
  table = div.find("table")

  # --- Extract last laser sequence timestamp ---

  rows = table.find_all("tr")

  # Remove header row if present
  data_rows = [r for r in rows if r.find_all("td")]

  if not data_rows:
      raise ValueError("No data rows found in laser DB table")

  last_row = data_rows[-1]
  cells = last_row.find_all("td")

  # Adjust index depending on actual column structure.
  laser_time_str = cells[2].get_text(strip=True)

  print("DEBUG Last laser insertion time (raw):", laser_time_str)

  # ---- Parse timestamp ----
  # IMPORTANT: adjust format string to match actual table format
  # Example formats you might encounter:
  #   2026-02-22 07:35:12
  #   22/02/26 07:35
  #   2026-02-22 07:35

  try:
      laser_dt = datetime.strptime(laser_time_str, "%Y-%m-%d %H:%M:%S")
  except ValueError:
      try:
          laser_dt = datetime.strptime(laser_time_str, "%Y-%m-%d %H:%M")
      except ValueError:
          try:
              laser_dt = datetime.strptime(laser_time_str, "%y/%m/%d %H:%M")
          except ValueError:
              raise ValueError(f"Unknown datetime format: {laser_time_str}")

  print(" DEBUG Parsed laser insertion datetime:", laser_dt)

  # ---- Compare with run end time ----

  delta = end_dt - laser_dt

  print("DEBUG Time difference:", int(delta.total_seconds()/60.))

  if abs(delta) > timedelta(minutes=DELTA_MAX):
      print(f"<br><p>WARNING: Last laser sequence is more than {DELTA_MAX} minutes delayed, or laser uploads stopped for more then {DELTA_MAX} minutes</p>")
      print(p2)
      print(table.prettify())

except Exception as e:
    print("EXCEPTION!", e)
    traceback.print_exc(file=sys.stdout)  # prints full traceback
