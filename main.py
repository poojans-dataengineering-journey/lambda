import boto3
import pandas as pd
from sqlalchemy import create_engine
from botocore.exceptions import ClientError
import json


# AWS Secrets Manager details
SECRET_NAME = "dev/database-1/salesdb"  # Replace with the name of your secret
AWS_REGION = "us-east-1"  # Replace with your AWS region (e.g., "us-west-2")

# Table name for RDS insertion
TABLE_NAME = 'sales'

# SNS topic name
TOPIC_NAME = 'dehtopic'

# CSV file name
FILE_NAME = 'sales_rds_excercise_full.csv'

def read_csv_from_s3(s3_path):
    """
    Read a CSV file from an S3 location into a pandas DataFrame.

    Parameters:
    - s3_path (str): S3 path to the CSV file (e.g., 's3://your-bucket/your-path/file.csv').

    Returns:
    - pd.DataFrame: A pandas DataFrame containing the CSV data.
    """
    s3_client = boto3.client('s3')
    bucket, key = s3_path.replace('s3://', '').split('/', 1)
    
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        df = pd.read_csv(response['Body'])
        return df
    except Exception as e:
        raise Exception(f"Error reading CSV from S3: {e}")

def get_database_secrets():
    """
    Retrieve database credentials from AWS Secrets Manager.

    :return: A dictionary containing the database credentials (username, password, host, dbname).
    :raises: Exception if unable to retrieve secrets from AWS Secrets Manager.
    """
    try:
        # Initialize a session using boto3
        session = boto3.session.Session()
        client = session.client(service_name="secretsmanager", region_name=AWS_REGION)
        
        # Get the secret value
        secret_value = client.get_secret_value(SecretId=SECRET_NAME)
        secrets = json.loads(secret_value["SecretString"])
        
        print("Successfully retrieved database secrets from Secrets Manager.")
        return secrets
    except Exception as e:
        print(f"Error retrieving secrets: {e}")
        raise


def get_database_engine(secrets):
    """
    Create a SQLAlchemy database engine using retrieved secrets.

    :param secrets: A dictionary containing database credentials.
    :return: SQLAlchemy engine for the database connection.
    :raises: Exception if unable to create a database engine.
    """
    try:
        connection_string = (
            f"mysql+pymysql://{secrets['username']}:{secrets['password']}@"
            f"{secrets['host']}/{secrets['dbname']}"
        )
        engine = create_engine(connection_string, echo=False)
        print("Successfully connected to the database using SQLAlchemy.")
        return engine
    except Exception as e:
        print(f"Error creating database engine: {e}")
        raise


def insert_into_rds(engine, df):
    """
    Insert data into the RDS MySQL table.

    :param engine: The SQLAlchemy engine to connect to the database.
    :param df: The pandas DataFrame containing the data to insert.
    :raises: Exception if there is an error inserting data into the RDS.
    """
    try:
        with engine.connect() as connection:
            with connection.begin():
                # Insert data into the specified table
                df.to_sql(TABLE_NAME, con=engine, index=False, if_exists='replace')
                print(f"Inserted {len(df)} rows into the database.")
    except Exception as e:
        print(f"Error inserting into RDS: {e}")
        raise


def publish_failure_message(job_name, error_message, sns_topic_arn):
    """
    Publish a failure message to an SNS topic when a job fails.

    :param job_name: The name of the job that failed.
    :param error_message: The error message or details of the failure.
    :param sns_topic_arn: The ARN of the SNS topic to send the message to.
    """
    sns_client = boto3.client('sns')  # Initialize SNS client
    
    # Prepare the message to be sent
    subject = f"Job {job_name} Failed"
    message = f"The job '{job_name}' has failed with the following error:\n\n{error_message}"
    
    try:
        # Publish the failure message to SNS
        response = sns_client.publish(
            TopicArn=sns_topic_arn,
            Message=message,
            Subject=subject
        )
        print(f"Message successfully sent to SNS. Message ID: {response['MessageId']}")
    except ClientError as e:
        print(f"Error occurred while publishing message to SNS: {e}")


def get_aws_account_id():
    """
    Get the AWS account ID using Boto3's STS service.

    :return: AWS Account ID (string).
    :raises: Exception if unable to retrieve AWS account ID.
    """
    # Create an STS client
    sts_client = boto3.client('sts')
    
    try:
        # Call the get_caller_identity API
        response = sts_client.get_caller_identity()
        
        # Extract the account ID from the response
        account_id = response['Account']
        
        return account_id
    except Exception as e:
        print(f"Error occurred while fetching AWS account ID: {e}")
        return None


def lambda_handler(event, context):
    """
    AWS Lambda handler function.

    :param event: Event data passed to the Lambda function (not used here).
    :param context: Context information about the invocation, function, and execution environment (not used here).
    :return: A dictionary containing the status code and response body.
    """
    try:
        # Read the CSV file into a DataFrame
        S3_csv_file_path = f's3://dehlive-sales-{get_aws_account_id()}-{AWS_REGION}/raw/maze/{FILE_NAME}'
        df = read_csv_from_s3(S3_csv_file_path)
        print(f"Read {len(df)} rows from the CSV file.")
        
        # Retrieve database credentials from Secrets Manager
        secrets = get_database_secrets()
        
        # Create a database engine using the retrieved credentials
        engine = get_database_engine(secrets)
        
        # Insert data into the RDS MySQL table
        insert_into_rds(engine, df)
        
        return {"statusCode": 200, "body": "Data successfully inserted into RDS"}
    
    except Exception as e:
        # AWS SNS details
        sns_topic_arn = f'arn:aws:sns:{AWS_REGION}:{get_aws_account_id()}:{TOPIC_NAME}'
        job_name = 'Sales job to load RDS table'
        error_message = f'The job encountered an unexpected error during processing: {e}'
        
        # Publish failure message to SNS
        publish_failure_message(job_name, error_message, sns_topic_arn)

        print(f"Error: {e}")
        return {"statusCode": 500, "body": str(e)}


if __name__ == "__main__":
    # Invoke the Lambda handler for testing purposes
    lambda_handler(None, None)
