pip install -r requirements.txt
pip install pyinstaller
pyinstaller --onefile --noconsole --icon=icon.png --name=BestFlightOnAgodaInRange --add-data "icon.png;." --add-data "chromedriver-win64\\chromedriver.exe;chromedriver-win64" main.py
