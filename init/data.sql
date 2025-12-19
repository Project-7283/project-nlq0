-- Create Database
CREATE DATABASE ecommerce_marketplace;
USE ecommerce_marketplace;

-- 1. Users Table
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(15),
    password_hash VARCHAR(255) NOT NULL,
    date_of_birth DATE,
    gender ENUM('Male', 'Female', 'Other'),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    email_verified BOOLEAN DEFAULT FALSE
);

-- 2. Categories Table
CREATE TABLE categories (
    category_id INT PRIMARY KEY AUTO_INCREMENT,
    category_name VARCHAR(100) NOT NULL,
    parent_category_id INT,
    description TEXT,
    image_url VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_category_id) REFERENCES categories(category_id)
);

-- 3. Sellers Table
CREATE TABLE sellers (
    seller_id INT PRIMARY KEY AUTO_INCREMENT,
    seller_name VARCHAR(100) NOT NULL,
    company_name VARCHAR(100),
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(15),
    gst_number VARCHAR(20),
    business_address TEXT,
    city VARCHAR(50),
    state VARCHAR(50),
    pincode VARCHAR(10),
    rating DECIMAL(3,2) DEFAULT 0.00,
    total_reviews INT DEFAULT 0,
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- 4. Products Table
CREATE TABLE products (
    product_id INT PRIMARY KEY AUTO_INCREMENT,
    product_name VARCHAR(200) NOT NULL,
    description TEXT,
    brand VARCHAR(100),
    model VARCHAR(100),
    category_id INT NOT NULL,
    seller_id INT NOT NULL,
    original_price DECIMAL(10,2) NOT NULL,
    selling_price DECIMAL(10,2) NOT NULL,
    discount_percentage DECIMAL(5,2) DEFAULT 0.00,
    stock_quantity INT DEFAULT 0,
    minimum_order_quantity INT DEFAULT 1,
    weight DECIMAL(8,2),
    dimensions VARCHAR(50),
    color VARCHAR(30),
    size VARCHAR(20),
    warranty_period INT, -- in months
    return_policy INT DEFAULT 7, -- in days
    is_featured BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    FOREIGN KEY (seller_id) REFERENCES sellers(seller_id)
);

-- 5. Product Images Table
CREATE TABLE product_images (
    image_id INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT NOT NULL,
    image_url VARCHAR(255) NOT NULL,
    alt_text VARCHAR(100),
    is_primary BOOLEAN DEFAULT FALSE,
    display_order INT DEFAULT 0,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);

-- 6. Addresses Table
CREATE TABLE addresses (
    address_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    address_type ENUM('Home', 'Work', 'Other') DEFAULT 'Home',
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(15) NOT NULL,
    address_line1 VARCHAR(255) NOT NULL,
    address_line2 VARCHAR(255),
    landmark VARCHAR(100),
    city VARCHAR(50) NOT NULL,
    state VARCHAR(50) NOT NULL,
    pincode VARCHAR(10) NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- 7. Cart Table
CREATE TABLE cart (
    cart_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    quantity INT NOT NULL DEFAULT 1,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_product (user_id, product_id)
);

-- 8. Orders Table
CREATE TABLE orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    order_number VARCHAR(50) UNIQUE NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10,2) NOT NULL,
    discount_amount DECIMAL(10,2) DEFAULT 0.00,
    tax_amount DECIMAL(10,2) DEFAULT 0.00,
    shipping_amount DECIMAL(10,2) DEFAULT 0.00,
    final_amount DECIMAL(10,2) NOT NULL,
    payment_method ENUM('COD', 'Credit Card', 'Debit Card', 'UPI', 'Net Banking', 'Wallet') NOT NULL,
    payment_status ENUM('Pending', 'Paid', 'Failed', 'Refunded') DEFAULT 'Pending',
    order_status ENUM('Placed', 'Confirmed', 'Shipped', 'Out for Delivery', 'Delivered', 'Cancelled', 'Returned') DEFAULT 'Placed',
    shipping_address_id INT NOT NULL,
    estimated_delivery_date DATE,
    actual_delivery_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (shipping_address_id) REFERENCES addresses(address_id)
);

-- 9. Order Items Table
CREATE TABLE order_items (
    order_item_id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT NOT NULL,
    product_id INT NOT NULL,
    seller_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,
    total_price DECIMAL(10,2) NOT NULL,
    discount_applied DECIMAL(10,2) DEFAULT 0.00,
    item_status ENUM('Placed', 'Confirmed', 'Shipped', 'Delivered', 'Cancelled', 'Returned') DEFAULT 'Placed',
    tracking_number VARCHAR(50),
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (seller_id) REFERENCES sellers(seller_id)
);

-- 10. Reviews Table
CREATE TABLE reviews (
    review_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    order_id INT,
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
    review_title VARCHAR(200),
    review_text TEXT,
    is_verified_purchase BOOLEAN DEFAULT FALSE,
    helpful_votes INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

-- 11. Wishlist Table
CREATE TABLE wishlist (
    wishlist_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    product_id INT NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_product_wishlist (user_id, product_id)
);

-- 12. Coupons Table
CREATE TABLE coupons (
    coupon_id INT PRIMARY KEY AUTO_INCREMENT,
    coupon_code VARCHAR(50) UNIQUE NOT NULL,
    coupon_name VARCHAR(100) NOT NULL,
    description TEXT,
    discount_type ENUM('Percentage', 'Fixed Amount') NOT NULL,
    discount_value DECIMAL(10,2) NOT NULL,
    minimum_order_amount DECIMAL(10,2) DEFAULT 0.00,
    maximum_discount_amount DECIMAL(10,2),
    usage_limit INT DEFAULT 1,
    used_count INT DEFAULT 0,
    valid_from DATE NOT NULL,
    valid_until DATE NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 13. User Coupons Table (Track which user used which coupon)
CREATE TABLE user_coupons (
    user_coupon_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    coupon_id INT NOT NULL,
    order_id INT,
    used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    discount_applied DECIMAL(10,2),
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (coupon_id) REFERENCES coupons(coupon_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

-- 14. Product Attributes Table (for filters like RAM, Storage, etc.)
CREATE TABLE product_attributes (
    attribute_id INT PRIMARY KEY AUTO_INCREMENT,
    product_id INT NOT NULL,
    attribute_name VARCHAR(50) NOT NULL,
    attribute_value VARCHAR(100) NOT NULL,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
);

-- 15. Payments Table
CREATE TABLE payments (
    payment_id INT PRIMARY KEY AUTO_INCREMENT,
    order_id INT NOT NULL,
    payment_method VARCHAR(50) NOT NULL,
    transaction_id VARCHAR(100) UNIQUE,
    payment_gateway VARCHAR(50),
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'INR',
    payment_status ENUM('Pending', 'Success', 'Failed', 'Cancelled', 'Refunded') DEFAULT 'Pending',
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    gateway_response TEXT,
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
);

-- Sample Data Insertions

-- Insert Categories
INSERT INTO categories (category_name, parent_category_id, description) VALUES
('Electronics', NULL, 'Electronic devices and accessories'),
('Clothing', NULL, 'Fashion and apparel'),
('Home & Kitchen', NULL, 'Home appliances and kitchen items'),
('Books', NULL, 'Books and literature'),
('Sports', NULL, 'Sports and fitness equipment'),
('Mobile Phones', 1, 'Smartphones and basic phones'),
('Laptops', 1, 'Laptops and notebooks'),
('Men Clothing', 2, 'Clothing for men'),
('Women Clothing', 2, 'Clothing for women'),
('Kitchen Appliances', 3, 'Kitchen equipment and appliances');

-- Insert Sellers
INSERT INTO sellers (seller_name, company_name, email, phone, business_address, city, state, pincode, rating, total_reviews, is_verified) VALUES
('TechWorld Store', 'TechWorld Pvt Ltd', 'contact@techworld.com', '9876543210', '123 Tech Street', 'Mumbai', 'Maharashtra', '400001', 4.2, 1250, TRUE),
('Fashion Hub', 'Fashion Hub Ltd', 'info@fashionhub.com', '9876543211', '456 Fashion Avenue', 'Delhi', 'Delhi', '110001', 4.5, 890, TRUE),
('Kitchen Master', 'Kitchen Master Co', 'sales@kitchenmaster.com', '9876543212', '789 Kitchen Lane', 'Bangalore', 'Karnataka', '560001', 4.1, 654, TRUE),
('Book Paradise', 'Book Paradise', 'hello@bookparadise.com', '9876543213', '321 Book Street', 'Chennai', 'Tamil Nadu', '600001', 4.6, 432, TRUE),
('Sports Zone', 'Sports Zone Inc', 'contact@sportszone.com', '9876543214', '654 Sports Complex', 'Pune', 'Maharashtra', '411001', 4.3, 321, TRUE);

-- Insert Sample Users
INSERT INTO users (first_name, last_name, email, phone, password_hash, date_of_birth, gender, email_verified) VALUES
('Amit', 'Sharma', 'amit.sharma@email.com', '9123456789', 'hashed_password_1', '1990-05-15', 'Male', TRUE),
('Priya', 'Singh', 'priya.singh@email.com', '9123456790', 'hashed_password_2', '1992-08-22', 'Female', TRUE),
('Rahul', 'Kumar', 'rahul.kumar@email.com', '9123456791', 'hashed_password_3', '1988-03-10', 'Male', TRUE),
('Sneha', 'Patel', 'sneha.patel@email.com', '9123456792', 'hashed_password_4', '1995-11-30', 'Female', FALSE),
('Vikram', 'Gupta', 'vikram.gupta@email.com', '9123456793', 'hashed_password_5', '1987-07-18', 'Male', TRUE);

-- Insert Sample Products
INSERT INTO products (product_name, description, brand, category_id, seller_id, original_price, selling_price, discount_percentage, stock_quantity, color, warranty_period) VALUES
('iPhone 13 128GB', 'Latest iPhone with A15 Bionic chip', 'Apple', 6, 1, 79900.00, 69900.00, 12.5, 50, 'Blue', 12),
('Samsung Galaxy S21', 'Android smartphone with great camera', 'Samsung', 6, 1, 69900.00, 59900.00, 14.3, 30, 'Black', 12),
('Dell Inspiron 15', 'Laptop for everyday computing', 'Dell', 7, 1, 55000.00, 49999.00, 9.1, 25, 'Silver', 12),
('Mens Cotton T-Shirt', 'Comfortable cotton t-shirt', 'Brand X', 8, 2, 999.00, 599.00, 40.0, 100, 'Blue', NULL),
('Womens Ethnic Dress', 'Traditional ethnic wear', 'Fashion Brand', 9, 2, 2999.00, 1999.00, 33.3, 75, 'Red', NULL),
('Mixer Grinder 750W', 'Powerful mixer grinder for kitchen', 'Kitchen Pro', 10, 3, 5999.00, 4499.00, 25.0, 40, 'White', 24),
('Fiction Novel - Bestseller', 'Popular fiction book', 'Famous Author', 4, 4, 499.00, 399.00, 20.0, 200, NULL, NULL),
('Cricket Bat Professional', 'Professional cricket bat', 'Sports Brand', 5, 5, 3999.00, 2999.00, 25.0, 15, 'Brown', 6);

-- Insert Sample Addresses
INSERT INTO addresses (user_id, address_type, full_name, phone, address_line1, city, state, pincode, is_default) VALUES
(1, 'Home', 'Amit Sharma', '9123456789', 'Flat 101, ABC Apartments, XYZ Road', 'Mumbai', 'Maharashtra', '400001', TRUE),
(2, 'Home', 'Priya Singh', '9123456790', 'House No 45, DEF Colony', 'Delhi', 'Delhi', '110001', TRUE),
(3, 'Work', 'Rahul Kumar', '9123456791', 'Office Complex, GHI Street', 'Bangalore', 'Karnataka', '560001', TRUE);

-- Insert Sample Orders
INSERT INTO orders (user_id, order_number, total_amount, final_amount, payment_method, payment_status, order_status, shipping_address_id) VALUES
(1, 'ORD001234567890', 69900.00, 69900.00, 'Credit Card', 'Paid', 'Delivered', 1),
(2, 'ORD001234567891', 1999.00, 1999.00, 'UPI', 'Paid', 'Shipped', 2),
(1, 'ORD001234567892', 4499.00, 4499.00, 'COD', 'Pending', 'Confirmed', 1);

-- Insert Sample Order Items
INSERT INTO order_items (order_id, product_id, seller_id, quantity, unit_price, total_price) VALUES
(1, 1, 1, 1, 69900.00, 69900.00),
(2, 5, 2, 1, 1999.00, 1999.00),
(3, 6, 3, 1, 4499.00, 4499.00);

-- Insert Sample Reviews
INSERT INTO reviews (user_id, product_id, order_id, rating, review_title, review_text, is_verified_purchase) VALUES
(1, 1, 1, 5, 'Excellent Phone!', 'Great performance and camera quality. Highly recommended!', TRUE),
(2, 5, 2, 4, 'Beautiful Dress', 'Nice fabric and design. Good value for money.', TRUE);

-- Insert Sample Coupons
INSERT INTO coupons (coupon_code, coupon_name, discount_type, discount_value, minimum_order_amount, valid_from, valid_until) VALUES
('SAVE10', '10% Off on Electronics', 'Percentage', 10.00, 5000.00, '2024-01-01', '2024-12-31'),
('FLAT500', 'Flat 500 Off', 'Fixed Amount', 500.00, 2000.00, '2024-01-01', '2024-12-31'),
('NEWUSER20', '20% Off for New Users', 'Percentage', 20.00, 1000.00, '2024-01-01', '2024-12-31');

-- Create some useful indexes for better performance
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_seller ON products(seller_id);
CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_reviews_product ON reviews(product_id);
CREATE INDEX idx_order_items_order ON order_items(order_id);

-- Create some useful views
CREATE VIEW popular_products AS
SELECT 
    p.product_id,
    p.product_name,
    p.brand,
    p.selling_price,
    AVG(r.rating) as avg_rating,
    COUNT(r.review_id) as review_count,
    SUM(oi.quantity) as total_sold
FROM products p
LEFT JOIN reviews r ON p.product_id = r.product_id
LEFT JOIN order_items oi ON p.product_id = oi.product_id
GROUP BY p.product_id, p.product_name, p.brand, p.selling_price
HAVING review_count > 0
ORDER BY avg_rating DESC, total_sold DESC;

CREATE VIEW user_order_summary AS
SELECT 
    u.user_id,
    CONCAT(u.first_name, ' ', u.last_name) as full_name,
    u.email,
    COUNT(o.order_id) as total_orders,
    SUM(o.final_amount) as total_spent,
    MAX(o.order_date) as last_order_date
FROM users u
LEFT JOIN orders o ON u.user_id = o.user_id
GROUP BY u.user_id, u.first_name, u.last_name, u.email;