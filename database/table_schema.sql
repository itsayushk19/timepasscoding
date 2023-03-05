CREATE TABLE articles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    domain VARCHAR(255) NOT NULL,
    keywords VARCHAR(255),
    url VARCHAR(255) NOT NULL,
    text TEXT NOT NULL,
    description TEXT,
    summary TEXT,
    category VARCHAR(255),
    top_image VARCHAR(255)
);
