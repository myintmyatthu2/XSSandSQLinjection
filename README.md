# XSSandSQLinjection
# Web Security Education Lab 🔒

A intentionally vulnerable Flask web application designed for educational purposes to demonstrate common web security vulnerabilities.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Flask-2.3.3-green)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

## 🚨 Important Warning

**This application contains intentional vulnerabilities for educational purposes only.**

- ✅ **DO** use it for learning and testing in controlled environments
- ✅ **DO** run it locally on your own machine
- ✅ **DO** use it to understand web security concepts
- ❌ **DO NOT** deploy it to production environments
- ❌ **DO NOT** expose it to the internet
- ❌ **DO NOT** use it against systems without permission

## 📋 Features

### 🎯 Demonstrated Vulnerabilities
- **Cross-Site Scripting (XSS)** - Stored and reflected
- **SQL Injection** - Union-based and boolean-based
- **Business Logic Flaws** - Price tampering
- **Information Disclosure** - Credential leakage
- **Session Management Issues** - Cookie manipulation

### 🛡️ Security Mechanisms
- Toggleable security protections
- Security event logging
- Educational tutorials
- Real-time vulnerability demonstrations

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/myintmyatthu2/XSSandSQLinjection.git
   cd aod_security_lab

2. **Run the automated setup**

bash
chmod +x run.sh
./run.sh

### Or manually:

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py

3. **Open http://localhost:5000 in your browser**
4. **Default Credentials**
   Role      :admin,user,user
   Username  :admin,alice,bob
   Password  :admin123,alice123,bob123
   Access    :Fullaccess,shop access, shop access

5. **Special Markers: Use built-in shortcuts:**

<XSS_DEMO> - Auto-generates XSS payload

<LEAK_ADMIN> - Shows admin credentials

<LEAK_USERS> - Shows user credentials

<LEAK_ALL> - Shows all credentials

project_name/
├── app.py # Main Flask application
├── run.sh # Automated setup script
├── requirements.txt # Python dependencies
├── README.md # This file
├── .gitignore # Git ignore rules
└── templates/ # HTML templates
├── base.html # Base template
├── login.html # Login page
├── feedback.html # Feedback form
├── admin_review.html # Admin review (vulnerable)
├── admin_dashboard.html # Product management
├── admin_orders.html # Order history
├── shop.html # User shop
├── success.html # Purchase confirmation
└── attacker.html # Leaked credentials view
    
## login as admin and go to admin_review you can try
type this in searchbar 
1.  ' OR 1=1; --
2.  'UNION SELECT username, password, NULL , NULL from users --
