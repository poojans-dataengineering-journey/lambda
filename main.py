import pandas as pd
from sqlalchemy import create_engine
import boto3
import json

# File path
csv_file_path = r'C:\Users\pooja\OneDrive\Desktop\RADE-Data-Engineering\Hackathons\Hackathon-1\IcebreakerHackathon\sales_rds_excercise_full.csv'

# AWS Secrets Manager details
secret_name = 'dev/database-1/salesdb'
region_name = 'us-east-1'

# Create a Secrets Manager client
client = boto3.client('secretsmanager', region_name=region_name)

# Retrieve the secret value
response = client.get_secret_value(SecretId=secret_name)
secrets = json.loads(response['SecretString'])

# MySQL RDS connection details
host = secrets['host']
user = secrets['username']
password = secrets['password']
database = secrets['dbname']

# Read CSV file into a pandas Dataframe
df = pd.read_csv(csv_file_path)

# Create sqlalchemy engine
engine = create_engine(f'mysql+pymysql://{user}:{password}@{host}/{database}')

# Table name
table_name = 'sales'

# Create table if not exists
df.to_sql(table_name, con=engine, index=False, if_exists='replace')

print('Data successfully loaded into MySQL RDS')