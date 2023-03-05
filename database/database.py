import mysql.connector, sys, validators, datetime
from mysql.connector import pooling
from urllib.parse import urlparse

# Set up the connection pool
config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "articles",
}

connection_pool = mysql.connector.pooling.MySQLConnectionPool(pool_size=int(sys.argv[2]), **config)

# Define a function to get a connection from the pool
def get_connection():
    return connection_pool.get_connection()

# Use the connection pool to execute queries
def save_article_to_db(article):
    if article.url is None or not validators.url(article.url):
        # Save rejected URL to a text file
        with open('rejected_urls_{timestamp}.txt', 'a') as f:
            f.write(article.url + '\n')
        return

    if len(article.title.split()) < 6:
        # Save rejected URL to a text file
        with open('rejected_urls.txt', 'a') as f:
            f.write(article.url + '\n')
        return
    
    parsed_url = urlparse(article.url)
    domain_name = parsed_url.netloc

    connection = get_connection()
    cursor = connection.cursor()
    sql = "INSERT INTO articles (title, domain, keywords, url, text, description, summary, category, top_image) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    val = (article.title, domain_name, ','.join(article.keywords), article.url, article.text, article.meta_description, article.summary, ','.join(article.tags), article.top_image)
    cursor.execute(sql, val)
    connection.commit()
    cursor.close()
    connection.close()
