This program is designed to find the ads on any webpage, and identify the company they belong to, then organize them into a dictionary. 
The dictionary then auto generates a pie chart.

This program was developed with python, selenium, and pytesseract.

CompanyNames.txt is the database this program uses to label ads according to their company. 
Each company name is the left most text on each new line. 
Variations are seperated by a comma afterwards (with no empty space)
For example:

    micro center,mico,MICRO Cente?

this is a line in the CompanyNames.txt file. Micro center is listed on the left most; it is the company being found. Pytesseract is not perfect, and sometimes reads micro center as mico. 
When this happens we add a variation to the database to tell it if it finds 'mico' or 'MICRO Cente?', that it is actually a micro center ad, so it knows to add it correctly to the dictionary. 
The actual name of the company should always be the first entry on the left. 


The documentation.txt file is simply a stratchpad of loose notes I had while creating this script. You can laugh at me if you like. 

List of queried websites.txt is the list of actual fake news websites this has been used on. Need more websites to run this program more. If you find some please email me at adrevealer@gmail.com

seleniumtest.py is the main py script, and what you should run to start the program. 

Test.py is for tweaking pytesseract. It continually runs on one image. I used this to play with the config of pytesseract to get the best transcription results. 

ad proof is a folder where a single screenshot of the entire page is saved for each unique ad it finds. Used for data validation and proof for companies. 

chart is where the pie chart is stored

dump is where the images are temporarly stored. They are auto deleted after being used. 

text is where the images and text transcribed are stored ONLY if a company is not found. Can use this to improve the CompanyNames.txt database

several .json files are created in this process. These can be ignored. They will overwrite when the program runs again. 

dbdata.py is created to upload the data gathered to s3, then to copy the data to redshift where long term storage can be easier achieved, as well as analytical possibilities. 

TO USE:

pip install

navigate to line 73 and 74 in seleniumtest.py, and set the website you want to use it on. https://speedtest.net/ is default because it has easy ads to review. 
You must also change the name_of_website variable if you want the folder structure in redshift to work properly.
navigate to line 59 and set d < the number of times you want the program to run. I usually do 50 when querying a major website. 

Make sure the dump, text, and ad proof folders are empty before using this. 

Create a folder name "AdRevealer" and put the contents of this program inside it 

Then just run selemniumtest.py. 


dbdata.py can be run to upload the data to a s3, then to a redshift server. 
If you want to use dbdata.py on your own s3 and redshift, create a .env file and change the relevent fields to your information. 


the following is the schema for the redshift server I am currently running this on. 

CREATE TABLE public.website (
    website_id integer NOT NULL identity(1,1) ENCODE az64,
    name character varying(256) NOT NULL ENCODE lzo,
    url character varying(256) NOT NULL ENCODE lzo,
    queried_time timestamp without time zone NULL ENCODE az64,
    PRIMARY KEY (website_id)
)
DISTSTYLE AUTO;	

CREATE TABLE public.data (
    data_id integer NOT NULL identity(1, 1) ENCODE az64,
    website_id integer ENCODE az64,
    company_name character varying(256) NOT NULL ENCODE lzo,
    amount integer NOT NULL ENCODE az64,
    image character varying(256) ENCODE lzo,
    data_time timestamp without time zone ENCODE az64,
    PRIMARY KEY (data_id),
    UNIQUE (website_id),
    FOREIGN KEY (website_id) REFERENCES website(website_id)
) 
DISTSTYLE AUTO;