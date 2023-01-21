import os
from dotenv import load_dotenv, find_dotenv
import psycopg2
#import pandas as pd
import boto3
import json
from datetime import datetime

#uses .env for database information
#https://gist.github.com/DanyshMushtaq/12e4960098c4c7b118112c4a7b964b66
class Redshift:
    def __init__(self):
        ''' Constructor for this class. '''
        # Create some members
		# find .env automagically by walking up directories until it's found
        dotenv_path = find_dotenv()
        # load up the entries as environment variables
        load_dotenv(dotenv_path)
		#credentials
        self.database_endpoint = os.environ.get("DATABASE_ENDPOINT")
        self.database_name = os.environ.get("DATABASE_NAME")
        self.database_user = os.environ.get("DATABASE_USER")
        self.database_password = os.environ.get("DATABASE_PASSWORD")
        self.port = os.environ.get("PORT")

    def connect(self):	        
        #connect using psycopg2
        connection = psycopg2.connect(dbname=self.database_name, host=self.database_endpoint,
                                           port=self.port, user=self.database_user, password=self.database_password)

        return connection
	


class S3:
    def __init__(self):
        ''' Constructor for this class. '''
        # Create some members
		# find .env automagically by walking up directories until it's found
        dotenv_path = find_dotenv()
        # load up t`he entries as environment variables
        load_dotenv(dotenv_path)
		#credentials
        self.AWS_KEY = os.environ.get("AWS_ACCESS_KEY")
        self.AWS_SECRET = os.environ.get("AWS_SECRET_ACCESS_KEY")		
        self.AWS_BUCKET = os.environ.get("AWS_BUCKET")
        
     

    def connect(self):         		
      client = boto3.client('s3', aws_access_key_id=self.AWS_ACCESS_KEY,aws_secret_access_key=self.AWS_SECRET_ACCESS_KEY)
      return client
	
    def read_file(self,file_name):        
        client = self.connect()		
        file_nm=client.get_object(Bucket=self.AWS_BUCKET, Key=file_name)
        df=pd.read_csv(file_nm['Body'],header=0)
        return df

a = Redshift().connect()

con = a.cursor()
con.execute("SELECT * FROM website;")
con.execute("SELECT max(website_id) FROM website LIMIT 1;")
current_time = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")

#the path for the http images stored in the s3. 
image_url = 'https://adrevealerbucket.s3.us-east-2.amazonaws.com/images/'
#imports the dictionary given from the seleniumtest.py file. sets it equal to data
with open('dictExport.json') as json_file:
    data = json.load(json_file)

formatted_data = {}
zipped_list = []

with open('websiteExport.json') as json_file:
    website = json.load(json_file)

#reformats the imported dictionary into a convertable form to redshift. creates a list of the dictionary entries. then creates a file named dataExport.json for copying. 
for key, value in data.items():
    formatted_data = ({'company_name': key, 'amount': value, 'image': image_url + website['name'] + "/" + current_time + "/" + key + '.png'})
    zipped_list.append(formatted_data)

#sanatizes the dataExport.json file to a format redshift likes
with open('dataExport.json', 'w') as file:
    file.write(json.dumps(zipped_list).replace("]","").replace("[","").replace("},","}"))

#file paths and joins
a1 = os.path.abspath(os.path.dirname(__file__))
r1 = 'ad proof'
r2 = 'websiteExport.json'
r3 = 'dataExport.json'
imagesupload = os.path.join(a1, r1)
websiteExportUpload = os.path.join(a1, r2)
dataExportUpload = os.path.join(a1, r3)
s3 = boto3.resource('s3')
s3C = boto3.client('s3')
bname = 'adrevealerbucket'

#uploads everything in the ad proof folder to s3. used for uploading the images
#https://stackoverflow.com/questions/25380774/upload-a-directory-to-s3-with-boto
def uploadDirectory(path,bucketname):
        for root,dirs,files in os.walk(path):
            for file in files:
                s3C.upload_file(os.path.join(root,file),bucketname,'images/' + website['name'] + '/' + current_time + '/' + file)

uploadDirectory(imagesupload,'adrevealerbucket')
s3.Bucket(bname).upload_file(websiteExportUpload, "websiteExport.json")
s3.Bucket(bname).upload_file(dataExportUpload, "dataExport.json")

#COPY TO REDSHIFT
conn = a.cursor()
#copies the websiteExport json file to the website table
conn.execute("COPY website (name, url) FROM 's3://adrevealerbucket/websiteExport.json' iam_role 'arn:aws:iam::345087817673:role/service-role/AmazonRedshift-CommandsAccessRole-20221216T115930' REGION 'us-east-2' FORMAT AS json 'auto';")
#copies the dataExport json file to the data table
conn.execute("COPY data FROM 's3://adrevealerbucket/dataExport.json' iam_role 'arn:aws:iam::345087817673:role/service-role/AmazonRedshift-CommandsAccessRole-20221216T115930' REGION 'us-east-2' FORMAT AS json 'auto';")
a.commit()
#grabs the most recent data_ids enterting into the data base, and limits them to the amount of items found in the length of dictExport.json
#then sanitizes it into a comma delimited list
#then updates the rows inserted website_id with the foreign key of the website_id it found
conn.execute("SELECT data_id FROM data ORDER BY data_id DESC LIMIT " + str(len(data.items())))
lastId = conn.fetchall()
lastId = [str(x[0]) for x in lastId]
lastId = ','.join(lastId)
conn.execute("UPDATE data SET website_id = (SELECT max(website_id) FROM website) WHERE data_id IN (" + lastId + ");")
a.commit()