-- This is a sample database structure for educational/project purposes

-- Create Database
CREATE DATABASE IF NOT EXISTS ecommerce_marketplace;
USE ecommerce_marketplace;

-- 1. Users Table
CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Unique identifier for each user',
    first_name VARCHAR(50) NOT NULL COMMENT 'User first name',
    last_name VARCHAR(50) NOT NULL COMMENT 'User last name',
    email VARCHAR(100) UNIQUE NOT NULL COMMENT 'Unique email address for user authentication and communication',
    phone VARCHAR(15) COMMENT 'Contact phone number',
    password_hash VARCHAR(255) NOT NULL COMMENT 'Hashed password for secure authentication',
    date_of_birth DATE COMMENT 'User birth date for age verification and personalization',
    gender ENUM('Male', 'Female', 'Other') COMMENT 'User gender information',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Account creation timestamp',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Last profile update timestamp',
    is_active BOOLEAN DEFAULT TRUE COMMENT 'Account status flag; TRUE=active, FALSE=deactivated/suspended',
    email_verified BOOLEAN DEFAULT FALSE COMMENT 'Email verification status for account security'
) COMMENT='Core user account table storing customer profile information, authentication credentials, and account status for the ecommerce marketplace platform';

-- 2. Categories Table
CREATE TABLE categories (
    category_id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Unique identifier for each category',
    category_name VARCHAR(100) NOT NULL COMMENT 'Name of the product category',
    parent_category_id INT COMMENT 'ID of the parent category for hierarchical structure',
    description TEXT COMMENT 'Detailed description of the category',
    image_url VARCHAR(255) COMMENT 'URL of the category image',
    is_active BOOLEAN DEFAULT TRUE COMMENT 'Flag indicating if the category is active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Timestamp when the category was created',
    FOREIGN KEY (parent_category_id) REFERENCES categories(category_id)
) COMMENT 'Table storing product categories in a hierarchical structure';

-- 3. Sellers Table
CREATE TABLE sellers (
    seller_id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Unique identifier for each seller',
    seller_name VARCHAR(100) NOT NULL COMMENT 'Name of the seller',
    company_name VARCHAR(100) COMMENT 'Name of the seller company',
    email VARCHAR(100) UNIQUE NOT NULL COMMENT 'Email address of the seller',
    phone VARCHAR(15) COMMENT 'Contact phone number of the seller',
    gst_number VARCHAR(20) COMMENT 'GST number for tax purposes',
    business_address TEXT COMMENT 'Business address of the seller',
    city VARCHAR(50) COMMENT 'City of the seller',
    state VARCHAR(50) COMMENT 'State of the seller',
    pincode VARCHAR(10) COMMENT 'Pincode of the seller location',
    rating DECIMAL(3,2) DEFAULT 0.00 COMMENT 'Average rating of the seller',
    total_reviews INT DEFAULT 0 COMMENT 'Total number of reviews for the seller',
    is_verified BOOLEAN DEFAULT FALSE COMMENT 'Flag indicating if the seller is verified',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Timestamp when the seller account was created',
    is_active BOOLEAN DEFAULT TRUE COMMENT 'Flag indicating if the seller account is active'
) COMMENT 'Table storing seller information and business details';

-- 4. Products Table
CREATE TABLE products (
    product_id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Unique identifier for each product',
    product_name VARCHAR(200) NOT NULL COMMENT 'Name of the product',
    description TEXT COMMENT 'Detailed description of the product',
    brand VARCHAR(100) COMMENT 'Brand name of the product',
    model VARCHAR(100) COMMENT 'Model number or name of the product',
    category_id INT NOT NULL COMMENT 'ID of the category this product belongs to',
    seller_id INT NOT NULL COMMENT 'ID of the seller offering this product',
    original_price DECIMAL(10,2) NOT NULL COMMENT 'Original price of the product before discount',
    selling_price DECIMAL(10,2) NOT NULL COMMENT 'Current selling price of the product',
    discount_percentage DECIMAL(5,2) DEFAULT 0.00 COMMENT 'Discount percentage applied to the product',
    stock_quantity INT DEFAULT 0 COMMENT 'Available stock quantity of the product',
    minimum_order_quantity INT DEFAULT 1 COMMENT 'Minimum quantity that can be ordered',
    weight DECIMAL(8,2) COMMENT 'Weight of the product in appropriate units',
    dimensions VARCHAR(50) COMMENT 'Dimensions of the product (length x width x height)',
    color VARCHAR(30) COMMENT 'Color of the product',
    size VARCHAR(20) COMMENT 'Size of the product',
    warranty_period INT COMMENT 'Warranty period in months',
    return_policy INT DEFAULT 7 COMMENT 'Return policy period in days',
    is_featured BOOLEAN DEFAULT FALSE COMMENT 'Flag indicating if the product is featured',
    is_active BOOLEAN DEFAULT TRUE COMMENT 'Flag indicating if the product is active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Timestamp when the product was added',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Timestamp when the product was last updated',
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    FOREIGN KEY (seller_id) REFERENCES sellers(seller_id)
) COMMENT 'Table storing detailed information about products available in the marketplace';

-- 5. Product Images Table
CREATE TABLE product_images (
    image_id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Unique identifier for each product image',
    product_id INT NOT NULL COMMENT 'ID of the product this image belongs to',
    image_url VARCHAR(255) NOT NULL COMMENT 'URL of the product image',
    alt_text VARCHAR(100) COMMENT 'Alternative text for the image for accessibility',
    is_primary BOOLEAN DEFAULT FALSE COMMENT 'Flag indicating if this is the primary image',
    display_order INT DEFAULT 0 COMMENT 'Order in which the image should be displayed',
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
) COMMENT 'Table storing images associated with products';

-- 6. Addresses Table
CREATE TABLE addresses (
    address_id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Unique identifier for each address',
    user_id INT NOT NULL COMMENT 'ID of the user this address belongs to',
    address_type ENUM('Home', 'Work', 'Other') DEFAULT 'Home' COMMENT 'Type of address',
    full_name VARCHAR(100) NOT NULL COMMENT 'Full name of the person at this address',
    phone VARCHAR(15) NOT NULL COMMENT 'Phone number for this address',
    address_line1 VARCHAR(255) NOT NULL COMMENT 'First line of the address',
    address_line2 VARCHAR(255) COMMENT 'Second line of the address',
    landmark VARCHAR(100) COMMENT 'Landmark near the address',
    city VARCHAR(50) NOT NULL COMMENT 'City of the address',
    state VARCHAR(50) NOT NULL COMMENT 'State of the address',
    pincode VARCHAR(10) NOT NULL COMMENT 'Pincode of the address',
    is_default BOOLEAN DEFAULT FALSE COMMENT 'Flag indicating if this is the default address',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Timestamp when the address was added',
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
) COMMENT 'Table storing user addresses for shipping and billing purposes';

-- 7. Cart Table
CREATE TABLE cart (
    cart_id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Unique identifier for each cart item',
    user_id INT NOT NULL COMMENT 'ID of the user who added the item to cart',
    product_id INT NOT NULL COMMENT 'ID of the product in the cart',
    quantity INT NOT NULL DEFAULT 1 COMMENT 'Quantity of the product in the cart',
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Timestamp when the item was added to cart',
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_product (user_id, product_id)
) COMMENT 'Table storing items added to user shopping carts';

-- 8. Orders Table
CREATE TABLE orders (
    order_id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Unique identifier for each order',
    user_id INT NOT NULL COMMENT 'ID of the user who placed the order',
    order_number VARCHAR(50) UNIQUE NOT NULL COMMENT 'Unique order number for reference',
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Date and time when the order was placed',
    total_amount DECIMAL(10,2) NOT NULL COMMENT 'Total amount of the order before discounts',
    discount_amount DECIMAL(10,2) DEFAULT 0.00 COMMENT 'Total discount applied to the order',
    tax_amount DECIMAL(10,2) DEFAULT 0.00 COMMENT 'Tax amount for the order',
    shipping_amount DECIMAL(10,2) DEFAULT 0.00 COMMENT 'Shipping cost for the order',
    final_amount DECIMAL(10,2) NOT NULL COMMENT 'Final amount to be paid after all calculations',
    payment_method ENUM('COD', 'Credit Card', 'Debit Card', 'UPI', 'Net Banking', 'Wallet') NOT NULL COMMENT 'Payment method used for the order',
    payment_status ENUM('Pending', 'Paid', 'Failed', 'Refunded') DEFAULT 'Pending' COMMENT 'Current status of the payment',
    order_status ENUM('Placed', 'Confirmed', 'Shipped', 'Out for Delivery', 'Delivered', 'Cancelled', 'Returned') DEFAULT 'Placed' COMMENT 'Current status of the order',
    shipping_address_id INT NOT NULL COMMENT 'ID of the shipping address for the order',
    estimated_delivery_date DATE COMMENT 'Estimated delivery date for the order',
    actual_delivery_date DATE COMMENT 'Actual delivery date of the order',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Timestamp when the order was created',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Timestamp when the order was last updated',
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (shipping_address_id) REFERENCES addresses(address_id)
) COMMENT 'Table storing order information and status';

-- 9. Order Items Table
CREATE TABLE order_items (
    order_item_id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Unique identifier for each order item',
    order_id INT NOT NULL COMMENT 'ID of the order this item belongs to',
    product_id INT NOT NULL COMMENT 'ID of the product in this order item',
    seller_id INT NOT NULL COMMENT 'ID of the seller for this product',
    quantity INT NOT NULL COMMENT 'Quantity of the product ordered',
    unit_price DECIMAL(10,2) NOT NULL COMMENT 'Price per unit of the product',
    total_price DECIMAL(10,2) NOT NULL COMMENT 'Total price for this order item',
    discount_applied DECIMAL(10,2) DEFAULT 0.00 COMMENT 'Discount applied to this order item',
    item_status ENUM('Placed', 'Confirmed', 'Shipped', 'Delivered', 'Cancelled', 'Returned') DEFAULT 'Placed' COMMENT 'Status of this order item',
    tracking_number VARCHAR(50) COMMENT 'Tracking number for shipment',
    FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (seller_id) REFERENCES sellers(seller_id)
) COMMENT 'Table storing individual items within orders';

-- 10. Reviews Table
CREATE TABLE reviews (
    review_id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Unique identifier for each review',
    user_id INT NOT NULL COMMENT 'ID of the user who wrote the review',
    product_id INT NOT NULL COMMENT 'ID of the product being reviewed',
    order_id INT COMMENT 'ID of the order associated with the review',
    rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5) COMMENT 'Rating given by the user (1-5)',
    review_title VARCHAR(200) COMMENT 'Title of the review',
    review_text TEXT COMMENT 'Detailed text of the review',
    is_verified_purchase BOOLEAN DEFAULT FALSE COMMENT 'Flag indicating if the review is from a verified purchase',
    helpful_votes INT DEFAULT 0 COMMENT 'Number of helpful votes for the review',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Timestamp when the review was created',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT 'Timestamp when the review was last updated',
    is_active BOOLEAN DEFAULT TRUE COMMENT 'Flag indicating if the review is active',
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (product_id) REFERENCES products(product_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
) COMMENT 'Table storing user reviews and ratings for products';

-- 11. Wishlist Table
CREATE TABLE wishlist (
    wishlist_id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Unique identifier for each wishlist item',
    user_id INT NOT NULL COMMENT 'ID of the user who added the item to wishlist',
    product_id INT NOT NULL COMMENT 'ID of the product in the wishlist',
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Timestamp when the item was added to wishlist',
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_product_wishlist (user_id, product_id)
) COMMENT 'Table storing products added to user wishlists';

-- 12. Coupons Table
CREATE TABLE coupons (
    coupon_id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Unique identifier for each coupon',
    coupon_code VARCHAR(50) UNIQUE NOT NULL COMMENT 'Unique code for the coupon',
    coupon_name VARCHAR(100) NOT NULL COMMENT 'Name of the coupon',
    description TEXT COMMENT 'Description of the coupon',
    discount_type ENUM('Percentage', 'Fixed Amount') NOT NULL COMMENT 'Type of discount offered by the coupon',
    discount_value DECIMAL(10,2) NOT NULL COMMENT 'Value of the discount',
    minimum_order_amount DECIMAL(10,2) DEFAULT 0.00 COMMENT 'Minimum order amount required to use the coupon',
    maximum_discount_amount DECIMAL(10,2) COMMENT 'Maximum discount amount that can be applied',
    usage_limit INT DEFAULT 1 COMMENT 'Maximum number of times the coupon can be used',
    used_count INT DEFAULT 0 COMMENT 'Number of times the coupon has been used',
    valid_from DATE NOT NULL COMMENT 'Start date of coupon validity',
    valid_until DATE NOT NULL COMMENT 'End date of coupon validity',
    is_active BOOLEAN DEFAULT TRUE COMMENT 'Flag indicating if the coupon is active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Timestamp when the coupon was created'
) COMMENT 'Table storing coupon information for discounts';

-- 13. User Coupons Table (Track which user used which coupon)
CREATE TABLE user_coupons (
    user_coupon_id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Unique identifier for each user coupon usage',
    user_id INT NOT NULL COMMENT 'ID of the user who used the coupon',
    coupon_id INT NOT NULL COMMENT 'ID of the coupon used',
    order_id INT COMMENT 'ID of the order where the coupon was used',
    used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Timestamp when the coupon was used',
    discount_applied DECIMAL(10,2) COMMENT 'Amount of discount applied using the coupon',
    FOREIGN KEY (user_id) REFERENCES users(user_id),
    FOREIGN KEY (coupon_id) REFERENCES coupons(coupon_id),
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
) COMMENT 'Table tracking coupon usage by users';

-- 14. Product Attributes Table (for filters like RAM, Storage, etc.)
CREATE TABLE product_attributes (
    attribute_id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Unique identifier for each product attribute',
    product_id INT NOT NULL COMMENT 'ID of the product this attribute belongs to',
    attribute_name VARCHAR(50) NOT NULL COMMENT 'Name of the attribute (e.g., RAM, Storage)',
    attribute_value VARCHAR(100) NOT NULL COMMENT 'Value of the attribute',
    FOREIGN KEY (product_id) REFERENCES products(product_id) ON DELETE CASCADE
) COMMENT 'Table storing additional attributes for products used in filtering and search';

-- 15. Payments Table
CREATE TABLE payments (
    payment_id INT PRIMARY KEY AUTO_INCREMENT COMMENT 'Unique identifier for each payment',
    order_id INT NOT NULL COMMENT 'ID of the order this payment is for',
    payment_method VARCHAR(50) NOT NULL COMMENT 'Method used for payment',
    transaction_id VARCHAR(100) UNIQUE COMMENT 'Unique transaction ID from payment gateway',
    payment_gateway VARCHAR(50) COMMENT 'Name of the payment gateway used',
    amount DECIMAL(10,2) NOT NULL COMMENT 'Amount of the payment',
    currency VARCHAR(3) DEFAULT 'INR' COMMENT 'Currency of the payment',
    payment_status ENUM('Pending', 'Success', 'Failed', 'Cancelled', 'Refunded') DEFAULT 'Pending' COMMENT 'Status of the payment',
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT 'Date and time of the payment',
    gateway_response TEXT COMMENT 'Response received from the payment gateway',
    FOREIGN KEY (order_id) REFERENCES orders(order_id)
) COMMENT 'Table storing payment information for orders';

-- Create some useful views

-- Popular Products View: View showing popular products based on ratings and sales
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

-- User Order Summary View: View summarizing user order history and spending
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

-- Seller Performance View: View showing seller performance metrics
CREATE VIEW seller_performance AS
SELECT
    s.seller_id,
    s.seller_name,
    COUNT(DISTINCT oi.order_id) as total_orders,
    SUM(oi.quantity) as total_units_sold,
    SUM(oi.total_price) as total_revenue,
    AVG(r.rating) as avg_product_rating
FROM sellers s
LEFT JOIN products p ON s.seller_id = p.seller_id
LEFT JOIN order_items oi ON p.product_id = oi.product_id
LEFT JOIN reviews r ON p.product_id = r.product_id
GROUP BY s.seller_id, s.seller_name;

