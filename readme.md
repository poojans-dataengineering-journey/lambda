
# ETL Project Using AWS Services

## Overview

This project demonstrates an **Extract, Transform, and Load (ETL)** pipeline leveraging **AWS services** such as S3, Lambda, RDS, Secrets Manager, and SNS. The pipeline extracts data from AWS S3, processes it using **Pandas**, and loads it into an RDS MySQL database using **SQLAlchemy**. Additionally, it includes error-handling mechanisms with notifications via AWS SNS.

### Key Features
- **Data Extraction**: Read CSV files stored in an S3 bucket.
- **Data Transformation**: Use **Pandas** for preprocessing and cleaning.
- **Data Loading**: Insert transformed data into an RDS MySQL table.
- **Secrets Management**: Securely retrieve database credentials using AWS Secrets Manager.
- **Error Notifications**: Publish failure notifications to an AWS SNS topic.
- **Scalability**: Designed to run as an AWS Lambda function for serverless execution.

---

## Prerequisites

Before setting up this project, ensure you have:
- Python 3.7 or above installed.
- An AWS account with appropriate permissions for:
  - S3
  - RDS
  - Secrets Manager
  - SNS
  - Lambda
- AWS CLI installed and configured with credentials.
- **IAM Roles**: Proper IAM roles with permissions for the Lambda function to access the above services.

---

## Project Structure

```
lambda/
│
├── main.py                 # Main Python script for the ETL process
├── requirements.txt        # Python dependencies
├── README.md               # Project documentation
```

---

## Setup Instructions

### 1. Clone the Repository
```bash
# Clone the repository
$ git clone <repository-url>

# Navigate to the project directory
$ cd <project-directory>
```

### 2. Set Up a Virtual Environment
It is recommended to use a virtual environment to manage dependencies.

#### On Windows
```bash
# Create a virtual environment
$ python -m venv venv

# Activate the virtual environment
$ .\venv\Scripts\activate
```

#### On macOS/Linux
```bash
# Create a virtual environment
$ python3 -m venv venv

# Activate the virtual environment
$ source venv/bin/activate
```

### 3. Install Dependencies
Install the required Python packages:
```bash
$ pip install -r requirements.txt
```

### 4. AWS Configuration
- **S3 Bucket**: Upload your CSV file to an S3 bucket. Note the bucket name and file path.
- **Secrets Manager**: Store your RDS database credentials in AWS Secrets Manager. Example secret JSON structure:
  ```json
  {
    "username": "your_db_username",
    "password": "your_db_password",
    "host": "your_db_host",
    "dbname": "your_db_name"
  }
  ```
- **RDS MySQL**: Set up an RDS MySQL instance and note the connection details.
- **SNS Topic**: Create an SNS topic to receive error notifications.

---

## Usage

### Running Locally
1. Update the script configuration (e.g., AWS region, secret name, S3 path, and SNS topic).
2. Run the script:
   ```bash
   $ python main.py
   ```

### Deploying to AWS Lambda
1. Package the script and dependencies as a ZIP file.
   ```bash
   $ zip -r etl_lambda_pipeline.zip main.py venv/
   ```
2. Upload the ZIP file to AWS Lambda.
3. Configure the Lambda environment variables:
   - `SECRET_NAME`: AWS Secrets Manager secret name.
   - `AWS_REGION`: AWS region.
   - `TABLE_NAME`: Name of the target table in RDS.
   - `TOPIC_NAME`: Name of the SNS topic.
4. Test the Lambda function with a sample event.

---
