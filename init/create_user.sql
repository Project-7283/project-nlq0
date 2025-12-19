-- Create user with native password authentication
CREATE USER 'nlq_user'@'%' IDENTIFIED WITH caching_sha2_password BY 'nlq_pass';

-- Grant DBA-level privileges on the database
GRANT ALL PRIVILEGES ON *.* TO 'nlq_user'@'%' WITH GRANT OPTION;

-- Flush privileges
FLUSH PRIVILEGES;



