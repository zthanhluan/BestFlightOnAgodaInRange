import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QLineEdit, QPushButton, QDateEdit, QTextBrowser, QRadioButton, QButtonGroup
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QPalette, QColor
from datetime import datetime, timedelta
from scrapePrice import get_price
from sendMail import send_email
from urllib.parse import urlparse, parse_qs
import re
from PyQt5.QtGui import QIcon
import os

def resource_path(relative_path):
    """ Get the absolute path to the resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temporary folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def extract_url_info(url):
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"  # Extract base URL (e.g., https://www.agoda.com)
    query_params = parse_qs(parsed_url.query)  # Extract query parameters as a dictionary

    return {
        "Website": base_url,
        "flightType": query_params.get("searchType", [""])[0],
        "departureFrom": query_params.get("departureFrom", [""])[0],
        "arrivalTo": query_params.get("arrivalTo", [""])[0],
        "departDate": query_params.get("departDate", [""])[0],
        "returnDate": query_params.get("returnDate", [""])[0],
        "adults": query_params.get("adults", [""])[0],
    }

def generate_html_list(url):
    info = extract_url_info(url)

    html_list = f"""
        <li><strong>Website</strong>: <a href="{info['Website']}">{info['Website']}</a></li>
        <li><strong>Flight Type</strong>: {"One-way" if info['flightType'] == "1" else "Round-trip"}</li>
        <li><strong>Departure From</strong>: {info['departureFrom']}</li>
        <li><strong>Arrival To</strong>: {info['arrivalTo']}</li>
        <li><strong>Departure Date</strong>: {info['departDate']}</li>
        {f'<li><strong>Return Date</strong>: {info["returnDate"]}</li>' if info['flightType'] != "1" else ""}
        <li><strong>Adults</strong>: {info['adults']}</li>
    """
    return html_list
    
def format_price_vnd(price):
    # Check if the price is infinity
    if price == float('inf'):
        return "No price available"  # or any other string you'd prefer

    # Convert to integer and format with dots if it's a valid price
    return f"{int(price):,}".replace(",", ".")
    
# Email validation function
def is_valid_email(email: str) -> bool:
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(email_regex, email))

class BestPriceApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Best Price on Agoda in Range")
        self.setWindowIcon(QIcon(resource_path("icon.png")))
        self.setStyleSheet(self.get_styles())
        
        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout()

        # Flight type selection
        flight_type_layout = QHBoxLayout()
        self.one_way_radio = QRadioButton("One-way")
        self.round_trip_radio = QRadioButton("Round-trip")
        self.round_trip_radio.setChecked(True)

        flight_type_group = QButtonGroup(self)
        flight_type_group.addButton(self.one_way_radio)
        flight_type_group.addButton(self.round_trip_radio)

        flight_type_layout.addWidget(QLabel("Flight type:"))
        flight_type_layout.addWidget(self.one_way_radio)
        flight_type_layout.addWidget(self.round_trip_radio)

        # Flying from and to
        airport_layout = QHBoxLayout()

        self.from_combo = QComboBox()
        self.from_combo.addItems([
            "HAN - Noi Bai Airport", "SGN - Tan Son Nhat Airport", "DAD - Da Nang Airport", "CXR - Cam Ranh Airport", "PQC - Phu Quoc Airport",
            "BKK - Suvarnabhumi Airport", "DMK - Don Mueang Airport", "CNX - Chiang Mai Airport", "HKT - Phuket Airport", "CEI - Chiang Rai Airport",
            "LPQ - Luang Prabang Airport", "VTE - Wattay Airport", "PKZ - Pakse Airport",
            "PNH - Phnom Penh Airport", "REP - Siem Reap Airport", "KOS - Sihanoukville Airport",
            "RGN - Yangon Airport", "MDL - Mandalay Airport", "NYT - Naypyidaw Airport",
            "KIX - Kansai International Airport", "NRT - Narita International Airport", "HND - Haneda Airport", "CTS - New Chitose Airport", "FUK - Fukuoka Airport",
            "ICN - Incheon International Airport", "GMP - Gimpo Airport",
            "PVG - Shanghai Pudong Airport", "PEK - Beijing Capital Airport", "CAN - Guangzhou Baiyun Airport", "HKG - Hong Kong International Airport", "SZX - Shenzhen Bao'an Airport"
        ])
        self.from_combo.setCurrentText("HAN - Noi Bai Airport")  # Default selection

        self.to_combo = QComboBox()
        self.to_combo.addItems([
            "HAN - Noi Bai Airport", "SGN - Tan Son Nhat Airport", "DAD - Da Nang Airport", "CXR - Cam Ranh Airport", "PQC - Phu Quoc Airport",
            "BKK - Suvarnabhumi Airport", "DMK - Don Mueang Airport", "CNX - Chiang Mai Airport", "HKT - Phuket Airport", "CEI - Chiang Rai Airport",
            "LPQ - Luang Prabang Airport", "VTE - Wattay Airport", "PKZ - Pakse Airport",
            "PNH - Phnom Penh Airport", "REP - Siem Reap Airport", "KOS - Sihanoukville Airport",
            "RGN - Yangon Airport", "MDL - Mandalay Airport", "NYT - Naypyidaw Airport",
            "KIX - Kansai International Airport", "NRT - Narita International Airport", "HND - Haneda Airport", "CTS - New Chitose Airport", "FUK - Fukuoka Airport",
            "ICN - Incheon International Airport", "GMP - Gimpo Airport",
            "PVG - Shanghai Pudong Airport", "PEK - Beijing Capital Airport", "CAN - Guangzhou Baiyun Airport", "HKG - Hong Kong International Airport", "SZX - Shenzhen Bao'an Airport"
        ])
        self.to_combo.setCurrentText("SGN - Tan Son Nhat Airport")  # Default selection

        airport_layout.addWidget(QLabel("Flying from:"))
        airport_layout.addWidget(self.from_combo)
        airport_layout.addWidget(QLabel("Flying to:"))
        airport_layout.addWidget(self.to_combo)

        # Date selection
        date_layout = QHBoxLayout()

        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDate(QDate.currentDate())

        self.end_date_edit = QDateEdit()
        self.end_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDate(QDate.currentDate().addDays(2))

        date_layout.addWidget(QLabel("Start date:"))
        date_layout.addWidget(self.start_date_edit)
        date_layout.addWidget(QLabel("End date:"))
        date_layout.addWidget(self.end_date_edit)
        
        # Duration input
        duration_layout = QHBoxLayout()
        self.duration_combo = QComboBox()
        self.duration_combo.addItems([str(i) for i in range(1, 11)])
        self.duration_combo.setCurrentIndex(1)  # Default is 2 days

        duration_layout.addWidget(QLabel("Durations:"))
        duration_layout.addWidget(self.duration_combo)

        # Passenger input
        passenger_layout = QHBoxLayout()
        self.passenger_combo = QComboBox()
        self.passenger_combo.addItems([str(i) for i in range(1, 11)])
        self.passenger_combo.setCurrentIndex(1)  # Default is 2 passengers

        passenger_layout.addWidget(QLabel("Passengers:"))
        passenger_layout.addWidget(self.passenger_combo)

        # Email input
        email_layout = QHBoxLayout()
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Enter your email address")
        self.email_input.setText("")  # Default email

        email_layout.addWidget(QLabel("Email:"))
        email_layout.addWidget(self.email_input)

        # Search button
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.handle_search)

        # Search result area
        self.result_area = QTextBrowser()
        self.result_area.setPlaceholderText("Search results will appear here...")
        self.result_area.setReadOnly(True)  # Keep it read-only
        self.result_area.setOpenExternalLinks(True)  # Enable clickable links
        self.result_area.setFixedHeight(500)

        # Adding widgets to main layout
        main_layout.addLayout(flight_type_layout)
        main_layout.addLayout(airport_layout)
        main_layout.addLayout(date_layout)
        main_layout.addLayout(duration_layout)
        main_layout.addLayout(passenger_layout)
        main_layout.addLayout(email_layout)
        main_layout.addWidget(self.search_button)
        main_layout.addWidget(self.result_area)

        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)

    def get_styles(self):
        return """
        QMainWindow {
            background-color: #f0f0f5;
        }
        QLabel {
            font-size: 14px;
            color: #333333;
        }
        QComboBox, QLineEdit, QDateEdit, QTextEdit {
            font-size: 14px;
            padding: 4px;
            border: 1px solid #cccccc;
            border-radius: 4px;
            background-color: #ffffff;
        }
        QComboBox::drop-down {
            border: 0px;
        }
        QRadioButton {
            font-size: 14px;
            color: #333333;
        }
        QPushButton {
            font-size: 14px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 4px;
            padding: 6px 12px;
        }
        QPushButton:hover {
            background-color: #45a049;
        }
        QPushButton:pressed {
            background-color: #3e8e41;
        }
        QTextEdit {
            font-family: "Courier New", Courier, monospace;
            background-color: #f9f9f9;
        }
        """
    def generate_url(self):
        url_template = (
            "https://www.agoda.com/vi-vn/flights/results?cid=1922896&tag=7adbeb35-4108-414c-9559-32893b4cdfe5"
            "&gclid=Cj0KCQiAqL28BhCrARIsACYJvkdMTm0k-55NDmbqFAgGnYpZ0N0Mx_57G_F24Z6T2EhrmMPj2za7XhYaAvgtEALw_wcB"
            "&departureFrom={flyingFrom}&departureFromType=1&arrivalTo={flyingTo}&arrivalToType=1"
            "&departDate={departDate}&returnDate={returnDate}&searchType={flightType}&cabinType=Economy"
            "&adults={passengers}&sort={sortType}"
        )
        
        # Get flyingFrom and flyingTo from combo boxes (extracting the airport code)
        flying_from = self.from_combo.currentText().split(" - ")[0]
        flying_to = self.to_combo.currentText().split(" - ")[0]
        
        # Get dates from date editors
        start_date = self.start_date_edit.date().toPyDate()
        end_date = self.end_date_edit.date().toPyDate()
        
        # Get flight type (1 for One-way, 2 for Round-trip)
        flight_type = "1" if self.one_way_radio.isChecked() else "2"
        
        sort_type = "1" if self.one_way_radio.isChecked() else "8"

        # Get passengers from combo box
        passengers = self.passenger_combo.currentText()
        
        duration = int(self.duration_combo.currentText())
        if flight_type == "1":
            duration = 0
        # Generate URLs for different departDate and returnDate combinations
        urls = []

        current_date = start_date
        while current_date <= end_date:
            # Calculate return dates for some days duration
            return_date = current_date + timedelta(days=duration)
            if return_date <= end_date:
                url = url_template.format(sortType=sort_type, flyingFrom=flying_from, flyingTo=flying_to, flightType=flight_type, passengers=passengers, departDate=current_date.strftime('%Y-%m-%d'), returnDate=return_date.strftime('%Y-%m-%d'))
                urls.append(url)
            
            current_date += timedelta(days=1)

        return urls
        
    def handle_search(self):
        urls = self.generate_url()
        self.find_lowest_price(urls)
    
    def find_lowest_price(self, urls):
        lowest_price = float('inf')  # Start with a very large value
        lowest_price_url = ""

        for url in urls:
            #print(url)
            current_price = get_price(url)  # Get the price for the current URL
            if current_price is None:  # Check if the price is None
                continue
            # Compare current price with the lowest price so far
            if current_price < lowest_price:
                lowest_price = current_price
                lowest_price_url = url
                
        body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    line-height: 1.6;
                }}
                .price {{
                    font-size: 18px;
                    font-weight: bold;
                }}
                .new-price {{
                    font-size: 22px;
                    color: #FF5733; /* Highlight color for New Price */
                    font-weight: bold;
                }}
                .header {{
                    font-size: 20px;
                    font-weight: bold;
                    margin-bottom: 10px;
                }}
                .footer {{
                    margin-top: 20px;
                    font-size: 14px;
                    color: #555;
                }}
            </style>
        </head>
        <body>
            <p>Dear Valued Customer,</p>

            <p>We are pleased to notify you a lowest price in range. Please find the details below:</p>

            <p class="header">🛒 Product Information:</p>
            <ul>
                {generate_html_list(lowest_price_url)}
                <li><span class="new-price">New Price: {format_price_vnd(lowest_price)} VND / Adult</span></li>
            </ul>

            <p>🌐 To view the item, click the link below.</p>
            <a href="{lowest_price_url}">Click here</a>
            <p>Thank you for choosing our service to keep you updated on price changes.</p>

            <p class="footer">
                Best regards,<br>
                The Price Tracker Team<br>
                📩 Need help? Contact us at <a href="mailto:support@pricetracker.com">support@pricetracker.com</a>
            </p>
        </body>
        </html>
        """

        self.result_area.clear()
        self.result_area.setHtml(body)
        
        
        email = self.email_input.text()
        if is_valid_email(email):
            if lowest_price_url != "":
                subject = "Best Price Information Alert"
                send_email(
                    sender_email="ZGllbnR1MDc4QGdtYWlsLmNvbQ==", 
                    receiver_email=email, 
                    password="emRvdyBnd2FsIHh0cGogYnB6bg==", 
                    subject=subject, 
                    body=body
                )
                print("Sent mail sucessful!")
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BestPriceApp()
    window.show()
    sys.exit(app.exec_())
