# 🔐 Blockchain-Based Educational Certificate Verification System

A secure web-based platform for **issuing, managing, and verifying educational certificates and qualifications using blockchain technology**.

The system provides different dashboards for **Students, Educational Institutions, Verifiers, and Administrators**, helping reduce certificate fraud and making qualification verification more reliable and transparent.

---

## 📌 Project Overview

Educational certificates are often exchanged as digital documents, making them vulnerable to:

* Certificate forgery
* Unauthorized modification
* Fake educational qualifications
* Difficult manual verification
* Lack of a centralized verification mechanism

This project addresses these challenges by combining **Blockchain technology with a Flask-based web application**.

Certificates issued through the system can be associated with blockchain records, allowing authorized users to verify whether a certificate is genuine and has not been tampered with.

---

## ✨ Key Features

### 👨‍🎓 Student

* Student registration and login
* Student dashboard
* View issued certificates
* Access educational qualification records
* Certificate verification support

### 🏫 Educational Institution

* Institution registration/login
* Institution dashboard
* Issue certificates to students
* Manage certificate information
* Maintain student qualification records

### 🔎 Verifier

* Verifier login
* Verify educational certificates
* Check certificate details
* Validate blockchain-backed certificate records

### 👨‍💼 Administrator

* Administrator dashboard
* Manage system users
* Monitor institutions and students
* Manage system-level records
* Support certificate and verification workflows

---

## ⛓️ Blockchain Integration

The project uses blockchain concepts to maintain the integrity of educational qualification records.

A certificate can be represented using a unique blockchain record/hash so that changes to the original certificate information can be detected.

### Simplified workflow

```text
Student
   │
   ▼
Educational Institution
   │
   │ Issue Certificate
   ▼
Blockchain Record
   │
   ▼
Certificate / Qualification
   │
   ▼
Verifier
   │
   ▼
Verification Result
```

---

## 🏗️ System Architecture

```text
                ┌──────────────────────┐
                │      Web Browser     │
                └──────────┬───────────┘
                           │
                           ▼
                ┌──────────────────────┐
                │    Flask Web App     │
                │      app3.py         │
                └──────────┬───────────┘
                           │
             ┌─────────────┼─────────────┐
             │             │             │
             ▼             ▼             ▼
       ┌──────────┐  ┌──────────┐  ┌────────────┐
       │ Database │  │Blockchain│  │   Users    │
       │          │  │  Module  │  │ Management │
       └──────────┘  └──────────┘  └────────────┘
                           │
                           ▼
                    Certificate Data
```

---

## 🛠️ Technologies Used

### Frontend

* HTML5
* CSS3
* JavaScript
* Jinja2 Templates

### Backend

* Python
* Flask

### Blockchain

* Python-based blockchain implementation
* Hashing
* Blockchain records
* Certificate verification

### Database

* SQL database
* SQL scripts for database management

### Development Tools

* Git
* GitHub
* Python Virtual Environment
* VS Code

---

## 📂 Project Structure

```text
blockchain-education-certificate-verification/
│
├── app3.py
├── blockchain.py
│
├── Database/
│   └── change.sql
│
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard_admin.html
│   ├── dashboard_institution.html
│   ├── dashboard_student.html
│   ├── dashboard_verifier.html
│   ├── issue_certificate.html
│   ├── verify_certificate.html
│   └── d.html
│
├── static/
│   └── songs/
│
└── README.md
```

---

## 🔄 Certificate Issuing Process

```text
1. Student registers with the platform
             ↓
2. Educational institution logs in
             ↓
3. Institution enters certificate details
             ↓
4. Certificate information is processed
             ↓
5. Blockchain record is created
             ↓
6. Certificate is associated with the blockchain record
             ↓
7. Student can access the certificate
```

---

## 🔍 Certificate Verification Process

```text
1. Verifier opens the verification page
             ↓
2. Certificate information is submitted
             ↓
3. System retrieves the corresponding record
             ↓
4. Blockchain data is checked
             ↓
5. Certificate information is validated
             ↓
6. Verification result is displayed
```

---

## 👥 User Roles

| Role           | Main Responsibilities                |
| -------------- | ------------------------------------ |
| 👨‍🎓 Student  | View qualifications and certificates |
| 🏫 Institution | Issue and manage certificates        |
| 🔎 Verifier    | Verify certificates                  |
| 👨‍💼 Admin    | Manage and monitor the platform      |

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/code-with-saikumar/blockchain-education-certificate-verification.git
```

Navigate into the project:

```bash
cd blockchain-education-certificate-verification
```

---

### 2. Create a Virtual Environment

Windows:

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate
```

---

### 3. Install Dependencies

If the project contains a `requirements.txt` file:

```bash
pip install -r requirements.txt
```

If dependencies need to be installed manually:

```bash
pip install flask
```

Install any additional packages required by your local configuration.

---

### 4. Configure the Database

Use the SQL file located at:

```text
Database/change.sql
```

Execute the required SQL statements in your configured database system.

Make sure the database connection settings in the Flask application match your local environment.

---

### 5. Run the Application

Run:

```bash
python app3.py
```

The Flask application should start on the configured local host and port.

Open the URL displayed in the terminal, commonly:

```text
http://127.0.0.1:5000/
```

---

## 🔐 Security Considerations

The system is designed around the following security concepts:

* Blockchain-based record integrity
* User authentication
* Role-based access
* Certificate verification
* Hash-based data validation
* Controlled certificate issuance

For a production deployment, additional protections such as secure password hashing, HTTPS, CSRF protection, input validation, secret management, and stronger blockchain infrastructure should be implemented.

---

## 🎯 Objectives

The primary objectives of this project are:

1. Reduce educational certificate fraud.
2. Provide a reliable certificate verification mechanism.
3. Maintain the integrity of qualification records.
4. Simplify certificate verification for authorized users.
5. Provide separate interfaces for different stakeholders.
6. Demonstrate the practical application of blockchain technology in education.

---

## 💡 Future Enhancements

Possible improvements include:

* 📱 Mobile application
* 🔗 Integration with a public blockchain
* 📜 QR-code based certificate verification
* 🤖 AI-powered document verification
* ☁️ Cloud deployment
* 🔐 Advanced identity verification
* 📧 Automated certificate notifications
* 📊 Analytics dashboard
* 🌐 Multi-institution support
* 📄 Digital certificate generation
* 🔑 Decentralized identity integration

---

## 🧪 Use Cases

The system can be adapted for:

* Universities
* Colleges
* Schools
* Training institutes
* Online certification platforms
* Government education departments
* Recruitment organizations
* Background verification companies

---

## 📸 Application Modules

The project includes interfaces for:

* Home Page
* User Registration
* User Login
* Student Dashboard
* Institution Dashboard
* Verifier Dashboard
* Administrator Dashboard
* Certificate Issuing
* Certificate Verification

---

## 🎓 Academic Project

This project demonstrates the integration of:

**Web Development + Database Management + Blockchain + Authentication + Certificate Verification**

It can be used as an academic project for demonstrating the practical application of blockchain technology to educational credential management.

---

## 👨‍💻 Author

**Sai Kumar**

GitHub:
https://github.com/code-with-saikumar

---

## 📄 License

This project is intended for educational and demonstration purposes.

You may modify and extend the project according to your requirements.
