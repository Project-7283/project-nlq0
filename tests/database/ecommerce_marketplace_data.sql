-- E-commerce Mock Data Generator
-- This generates data for 6 months with realistic patterns for analysis

-- Clear existing data (optional - uncomment if needed)
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE user_coupons;
TRUNCATE TABLE payments;
TRUNCATE TABLE order_items;
TRUNCATE TABLE orders;
TRUNCATE TABLE reviews;
TRUNCATE TABLE cart;
TRUNCATE TABLE wishlist;
TRUNCATE TABLE product_attributes;
TRUNCATE TABLE product_images;
TRUNCATE TABLE products;
TRUNCATE TABLE addresses;
TRUNCATE TABLE users;
TRUNCATE TABLE sellers;
TRUNCATE TABLE coupons;
TRUNCATE TABLE categories;
SET FOREIGN_KEY_CHECKS = 1;

-- ============================================
-- 1. USERS DATA (50 users)
-- ============================================
INSERT INTO users (user_id, first_name, last_name, email, phone, password_hash, date_of_birth, gender, email_verified, is_active, created_at) VALUES
(1, 'Rahul', 'Sharma', 'rahul.sharma@email.com', '9876543210', '$2b$10$hash1', '1990-05-15', 'Male', 1, 1, '2024-01-15 10:30:00'),
(2, 'Priya', 'Singh', 'priya.singh@email.com', '9876543211', '$2b$10$hash2', '1992-08-22', 'Female', 1, 1, '2024-01-18 14:20:00'),
(3, 'Amit', 'Patel', 'amit.patel@email.com', '9876543212', '$2b$10$hash3', '1988-03-10', 'Male', 1, 1, '2024-02-05 09:15:00'),
(4, 'Sneha', 'Reddy', 'sneha.reddy@email.com', '9876543213', '$2b$10$hash4', '1995-11-30', 'Female', 1, 1, '2024-02-10 11:45:00'),
(5, 'Vikram', 'Kumar', 'vikram.kumar@email.com', '9876543214', '$2b$10$hash5', '1991-07-18', 'Male', 1, 1, '2024-02-15 16:30:00'),
(6, 'Anjali', 'Gupta', 'anjali.gupta@email.com', '9876543215', '$2b$10$hash6', '1993-04-25', 'Female', 1, 1, '2024-03-01 10:00:00'),
(7, 'Rohit', 'Mehta', 'rohit.mehta@email.com', '9876543216', '$2b$10$hash7', '1989-09-12', 'Male', 1, 1, '2024-03-05 13:20:00'),
(8, 'Kavya', 'Nair', 'kavya.nair@email.com', '9876543217', '$2b$10$hash8', '1994-12-08', 'Female', 1, 1, '2024-03-10 15:40:00'),
(9, 'Arjun', 'Desai', 'arjun.desai@email.com', '9876543218', '$2b$10$hash9', '1990-06-20', 'Male', 1, 1, '2024-03-15 09:30:00'),
(10, 'Pooja', 'Joshi', 'pooja.joshi@email.com', '9876543219', '$2b$10$hash10', '1992-02-14', 'Female', 1, 1, '2024-04-01 11:15:00'),
(11, 'Karan', 'Chopra', 'karan.chopra@email.com', '9876543220', '$2b$10$hash11', '1991-08-05', 'Male', 1, 1, '2024-04-05 14:00:00'),
(12, 'Neha', 'Verma', 'neha.verma@email.com', '9876543221', '$2b$10$hash12', '1993-10-17', 'Female', 1, 1, '2024-04-10 16:25:00'),
(13, 'Sanjay', 'Rao', 'sanjay.rao@email.com', '9876543222', '$2b$10$hash13', '1987-05-28', 'Male', 1, 1, '2024-04-15 10:50:00'),
(14, 'Divya', 'Iyer', 'divya.iyer@email.com', '9876543223', '$2b$10$hash14', '1995-03-22', 'Female', 1, 1, '2024-05-01 12:30:00'),
(15, 'Manish', 'Agarwal', 'manish.agarwal@email.com', '9876543224', '$2b$10$hash15', '1990-11-09', 'Male', 1, 1, '2024-05-05 15:15:00'),
(16, 'Ritu', 'Bansal', 'ritu.bansal@email.com', '9876543225', '$2b$10$hash16', '1992-07-16', 'Female', 1, 1, '2024-05-10 09:45:00'),
(17, 'Aditya', 'Malhotra', 'aditya.malhotra@email.com', '9876543226', '$2b$10$hash17', '1989-04-30', 'Male', 1, 1, '2024-05-15 13:00:00'),
(18, 'Simran', 'Kaur', 'simran.kaur@email.com', '9876543227', '$2b$10$hash18', '1994-09-11', 'Female', 1, 1, '2024-05-20 16:40:00'),
(19, 'Varun', 'Khanna', 'varun.khanna@email.com', '9876543228', '$2b$10$hash19', '1991-01-25', 'Male', 1, 1, '2024-06-01 10:20:00'),
(20, 'Tanvi', 'Shah', 'tanvi.shah@email.com', '9876543229', '$2b$10$hash20', '1993-06-18', 'Female', 1, 1, '2024-06-05 14:35:00'),
(21, 'Nikhil', 'Pandey', 'nikhil.pandey@email.com', '9876543230', '$2b$10$hash21', '1988-12-03', 'Male', 1, 1, '2024-06-10 11:50:00'),
(22, 'Isha', 'Mishra', 'isha.mishra@email.com', '9876543231', '$2b$10$hash22', '1995-08-27', 'Female', 1, 1, '2024-06-15 15:25:00'),
(23, 'Rajesh', 'Pillai', 'rajesh.pillai@email.com', '9876543232', '$2b$10$hash23', '1990-03-14', 'Male', 1, 1, '2024-06-20 09:10:00'),
(24, 'Megha', 'Saxena', 'megha.saxena@email.com', '9876543233', '$2b$10$hash24', '1992-11-21', 'Female', 1, 1, '2024-07-01 12:45:00'),
(25, 'Kunal', 'Bose', 'kunal.bose@email.com', '9876543234', '$2b$10$hash25', '1989-07-08', 'Male', 1, 1, '2024-07-05 16:15:00'),
(26, 'Shruti', 'Das', 'shruti.das@email.com', '9876543235', '$2b$10$hash26', '1994-04-19', 'Female', 1, 1, '2024-07-10 10:30:00'),
(27, 'Ashish', 'Jain', 'ashish.jain@email.com', '9876543236', '$2b$10$hash27', '1991-10-06', 'Male', 1, 1, '2024-07-15 14:00:00'),
(28, 'Riya', 'Chatterjee', 'riya.chatterjee@email.com', '9876543237', '$2b$10$hash28', '1993-02-28', 'Female', 1, 1, '2024-07-20 11:20:00'),
(29, 'Siddharth', 'Sinha', 'siddharth.sinha@email.com', '9876543238', '$2b$10$hash29', '1987-09-15', 'Male', 1, 1, '2024-08-01 15:50:00'),
(30, 'Ananya', 'Menon', 'ananya.menon@email.com', '9876543239', '$2b$10$hash30', '1995-05-23', 'Female', 1, 1, '2024-08-05 09:25:00'),
(31, 'Harsh', 'Tiwari', 'harsh.tiwari@email.com', '9876543240', '$2b$10$hash31', '1990-12-11', 'Male', 1, 1, '2024-08-10 13:40:00'),
(32, 'Nidhi', 'Kapoor', 'nidhi.kapoor@email.com', '9876543241', '$2b$10$hash32', '1992-08-07', 'Female', 1, 1, '2024-08-15 16:55:00'),
(33, 'Gaurav', 'Bhatt', 'gaurav.bhatt@email.com', '9876543242', '$2b$10$hash33', '1989-03-26', 'Male', 1, 1, '2024-08-20 10:15:00'),
(34, 'Preeti', 'Arora', 'preeti.arora@email.com', '9876543243', '$2b$10$hash34', '1994-11-12', 'Female', 1, 1, '2024-09-01 14:30:00'),
(35, 'Vishal', 'Dubey', 'vishal.dubey@email.com', '9876543244', '$2b$10$hash35', '1991-06-29', 'Male', 1, 1, '2024-09-05 11:45:00'),
(36, 'Sakshi', 'Tripathi', 'sakshi.tripathi@email.com', '9876543245', '$2b$10$hash36', '1993-01-16', 'Female', 1, 1, '2024-09-10 15:00:00'),
(37, 'Deepak', 'Kulkarni', 'deepak.kulkarni@email.com', '9876543246', '$2b$10$hash37', '1988-08-24', 'Male', 1, 1, '2024-09-15 09:20:00'),
(38, 'Kritika', 'Yadav', 'kritika.yadav@email.com', '9876543247', '$2b$10$hash38', '1995-04-02', 'Female', 1, 1, '2024-09-20 12:35:00'),
(39, 'Abhishek', 'Ghosh', 'abhishek.ghosh@email.com', '9876543248', '$2b$10$hash39', '1990-10-18', 'Male', 1, 1, '2024-10-01 16:10:00'),
(40, 'Shweta', 'Soni', 'shweta.soni@email.com', '9876543249', '$2b$10$hash40', '1992-05-31', 'Female', 1, 1, '2024-10-05 10:50:00'),
(41, 'Pankaj', 'Rawat', 'pankaj.rawat@email.com', '9876543250', '$2b$10$hash41', '1989-12-08', 'Male', 1, 1, '2024-10-10 14:05:00'),
(42, 'Pallavi', 'Dutta', 'pallavi.dutta@email.com', '9876543251', '$2b$10$hash42', '1994-07-26', 'Female', 1, 1, '2024-10-15 11:25:00'),
(43, 'Tarun', 'Singhal', 'tarun.singhal@email.com', '9876543252', '$2b$10$hash43', '1991-03-13', 'Male', 1, 1, '2024-10-20 15:40:00'),
(44, 'Monika', 'Sharma', 'monika.sharma@email.com', '9876543253', '$2b$10$hash44', '1993-09-04', 'Female', 1, 1, '2024-11-01 09:55:00'),
(45, 'Naveen', 'Chauhan', 'naveen.chauhan@email.com', '9876543254', '$2b$10$hash45', '1987-06-21', 'Male', 1, 1, '2024-11-05 13:10:00'),
(46, 'Sunita', 'Bhardwaj', 'sunita.bhardwaj@email.com', '9876543255', '$2b$10$hash46', '1995-02-09', 'Female', 1, 1, '2024-11-10 16:30:00'),
(47, 'Rakesh', 'Thakur', 'rakesh.thakur@email.com', '9876543256', '$2b$10$hash47', '1990-09-27', 'Male', 1, 1, '2024-11-15 10:45:00'),
(48, 'Geeta', 'Mathur', 'geeta.mathur@email.com', '9876543257', '$2b$10$hash48', '1992-04-14', 'Female', 1, 1, '2024-11-20 14:20:00'),
(49, 'Sumit', 'Bisht', 'sumit.bisht@email.com', '9876543258', '$2b$10$hash49', '1989-11-01', 'Male', 1, 1, '2024-11-25 11:35:00'),
(50, 'Radhika', 'Pandey', 'radhika.pandey@email.com', '9876543259', '$2b$10$hash50', '1994-08-19', 'Female', 1, 1, '2024-12-01 15:50:00');

-- ============================================
-- 2. CATEGORIES DATA
-- ============================================
INSERT INTO categories (category_id, category_name, parent_category_id, description, image_url, is_active) VALUES
(1, 'Electronics', NULL, 'Electronic devices and gadgets', '/images/categories/electronics.jpg', 1),
(2, 'Fashion', NULL, 'Clothing and accessories', '/images/categories/fashion.jpg', 1),
(3, 'Home & Kitchen', NULL, 'Home appliances and kitchenware', '/images/categories/home.jpg', 1),
(4, 'Books', NULL, 'Books and magazines', '/images/categories/books.jpg', 1),
(5, 'Sports', NULL, 'Sports equipment and fitness', '/images/categories/sports.jpg', 1),
(6, 'Mobile Phones', 1, 'Smartphones and accessories', '/images/categories/mobiles.jpg', 1),
(7, 'Laptops', 1, 'Laptops and notebooks', '/images/categories/laptops.jpg', 1),
(8, 'Mens Fashion', 2, 'Mens clothing and accessories', '/images/categories/mens.jpg', 1),
(9, 'Womens Fashion', 2, 'Womens clothing and accessories', '/images/categories/womens.jpg', 1),
(10, 'Kitchen Appliances', 3, 'Kitchen tools and appliances', '/images/categories/kitchen.jpg', 1);

-- ============================================
-- 3. SELLERS DATA (5 companies)
-- ============================================
INSERT INTO sellers (seller_id, seller_name, company_name, email, phone, gst_number, business_address, city, state, pincode, rating, total_reviews, is_verified, is_active) VALUES
(1, 'Tech World', 'Tech World Pvt Ltd', 'contact@techworld.com', '9876500001', '29ABCDE1234F1Z5', '123 MG Road', 'Bangalore', 'Karnataka', '560001', 4.5, 1250, 1, 1),
(2, 'Fashion Hub', 'Fashion Hub Enterprises', 'info@fashionhub.com', '9876500002', '27ABCDE5678G2Z5', '456 Commercial Street', 'Mumbai', 'Maharashtra', '400001', 4.3, 980, 1, 1),
(3, 'Home Essentials', 'Home Essentials India', 'support@homeessentials.com', '9876500003', '33ABCDE9012H3Z5', '789 Park Avenue', 'Delhi', 'Delhi', '110001', 4.6, 1500, 1, 1),
(4, 'Book Haven', 'Book Haven Publications', 'orders@bookhaven.com', '9876500004', '29ABCDE3456I4Z5', '321 Brigade Road', 'Bangalore', 'Karnataka', '560025', 4.4, 750, 1, 1),
(5, 'Sports Arena', 'Sports Arena Ltd', 'sales@sportsarena.com', '9876500005', '27ABCDE7890J5Z5', '654 Link Road', 'Mumbai', 'Maharashtra', '400050', 4.2, 650, 1, 1);

-- ============================================
-- 4. PRODUCTS DATA (40 products across categories)
-- ============================================
INSERT INTO products (product_id, product_name, description, brand, model, category_id, seller_id, original_price, selling_price, discount_percentage, stock_quantity, minimum_order_quantity, weight, dimensions, color, size, warranty_period, return_policy, is_featured, is_active) VALUES
-- Electronics - Mobile Phones
(1, 'Samsung Galaxy S23', 'Latest flagship smartphone with advanced camera', 'Samsung', 'Galaxy S23', 6, 1, 79999.00, 69999.00, 12.50, 50, 1, 0.17, '146x71x7.6mm', 'Phantom Black', NULL, 12, 7, 1, 1),
(2, 'iPhone 14 Pro', 'Premium Apple smartphone with A16 Bionic chip', 'Apple', 'iPhone 14 Pro', 6, 1, 129900.00, 119900.00, 7.70, 30, 1, 0.21, '147.5x71.5x7.9mm', 'Deep Purple', NULL, 12, 7, 1, 1),
(3, 'OnePlus 11', 'Flagship killer with Snapdragon 8 Gen 2', 'OnePlus', 'OnePlus 11', 6, 1, 56999.00, 51999.00, 8.77, 75, 1, 0.20, '163.1x74.1x8.5mm', 'Titan Black', NULL, 12, 7, 1, 1),
(4, 'Xiaomi 13 Pro', 'Premium smartphone with Leica camera', 'Xiaomi', 'Mi 13 Pro', 6, 1, 79999.00, 72999.00, 8.75, 40, 1, 0.23, '162.9x74.6x8.4mm', 'Ceramic White', NULL, 12, 7, 0, 1),

-- Electronics - Laptops
(5, 'Dell XPS 15', 'Premium laptop for professionals', 'Dell', 'XPS 15 9530', 7, 1, 165999.00, 149999.00, 9.64, 25, 1, 1.92, '344x230x18mm', 'Platinum Silver', NULL, 24, 7, 1, 1),
(6, 'MacBook Pro 14', 'Apple M2 Pro powered laptop', 'Apple', 'MacBook Pro 14', 7, 1, 199900.00, 189900.00, 5.00, 15, 1, 1.60, '312.6x221.2x15.5mm', 'Space Gray', NULL, 12, 7, 1, 1),
(7, 'HP Pavilion 15', 'Mid-range laptop for everyday use', 'HP', 'Pavilion 15-eh2000', 7, 1, 65999.00, 54999.00, 16.67, 60, 1, 1.75, '360x234x17.9mm', 'Natural Silver', NULL, 12, 7, 0, 1),
(8, 'Lenovo ThinkPad X1', 'Business laptop with premium build', 'Lenovo', 'ThinkPad X1 Carbon Gen 11', 7, 1, 175999.00, 159999.00, 9.09, 20, 1, 1.12, '315x222x14.9mm', 'Black', NULL, 36, 7, 1, 1),

-- Fashion - Mens
(9, 'Levis 511 Slim Fit Jeans', 'Classic slim fit denim jeans', 'Levis', '511', 8, 2, 3999.00, 2999.00, 25.01, 200, 1, 0.50, NULL, 'Dark Blue', '32', NULL, 15, 0, 1),
(10, 'Nike Air Max Shoes', 'Premium running shoes', 'Nike', 'Air Max 270', 8, 2, 12995.00, 9995.00, 23.09, 150, 1, 0.80, NULL, 'Black/White', '10', NULL, 30, 0, 1),
(11, 'Allen Solly Formal Shirt', 'Slim fit formal shirt for men', 'Allen Solly', 'AS-FS-2024', 8, 2, 1999.00, 1499.00, 25.01, 300, 1, 0.25, NULL, 'White', 'L', NULL, 15, 0, 1),
(12, 'Puma Track Pants', 'Comfortable sports track pants', 'Puma', 'Essential TP', 8, 2, 2499.00, 1799.00, 28.01, 180, 1, 0.35, NULL, 'Black', 'M', NULL, 15, 0, 1),

-- Fashion - Womens
(13, 'Zara Floral Dress', 'Elegant floral print dress', 'Zara', 'ZR-FD-2024', 9, 2, 4999.00, 3499.00, 30.01, 120, 1, 0.40, NULL, 'Multi', 'M', NULL, 15, 1, 1),
(14, 'H&M Denim Jacket', 'Classic denim jacket for women', 'H&M', 'HM-DJ-2024', 9, 2, 3499.00, 2799.00, 20.01, 100, 1, 0.60, NULL, 'Light Blue', 'S', NULL, 15, 0, 1),
(15, 'Forever 21 Handbag', 'Trendy shoulder handbag', 'Forever 21', 'F21-HB-2024', 9, 2, 2999.00, 2199.00, 26.68, 90, 1, 0.50, '30x20x10cm', 'Brown', NULL, NULL, 15, 0, 1),
(16, 'Biba Kurti Set', 'Traditional ethnic kurti with palazzo', 'Biba', 'BB-KS-2024', 9, 2, 3999.00, 2999.00, 25.01, 150, 1, 0.45, NULL, 'Pink', 'L', NULL, 15, 1, 1),

-- Home & Kitchen
(17, 'Philips Air Fryer', 'Healthy cooking air fryer', 'Philips', 'HD9252/90', 10, 3, 12995.00, 9995.00, 23.09, 80, 1, 4.50, '315x287x384mm', 'Black', NULL, 24, 7, 1, 1),
(18, 'Prestige Induction Cooktop', '2000W induction cooktop', 'Prestige', 'PIC 20.0', 10, 3, 3495.00, 2795.00, 20.03, 100, 1, 2.20, '285x285x65mm', 'Black', NULL, 12, 7, 0, 1),
(19, 'Bajaj Mixer Grinder', '750W mixer grinder with 3 jars', 'Bajaj', 'Rex 750W', 10, 3, 4999.00, 3999.00, 20.00, 120, 1, 4.00, '450x230x290mm', 'White', NULL, 24, 7, 1, 1),
(20, 'Hawkins Pressure Cooker', '5 Liter aluminum pressure cooker', 'Hawkins', 'Contura 5L', 10, 3, 2995.00, 2495.00, 16.69, 200, 1, 2.30, '270x270x180mm', 'Silver', '5L', 24, 7, 0, 1),
(21, 'Pigeon Electric Kettle', '1.5L stainless steel kettle', 'Pigeon', 'Amaze Plus', 10, 3, 1295.00, 995.00, 23.17, 250, 1, 0.85, '220x150x240mm', 'Silver', '1.5L', 12, 7, 0, 1),
(22, 'Milton Water Bottle', '1 Liter insulated water bottle', 'Milton', 'Thermosteel Flip', 10, 3, 699.00, 549.00, 21.46, 500, 1, 0.40, '285x75mm', 'Blue', '1L', 12, 15, 0, 1),

-- Books
(23, 'Rich Dad Poor Dad', 'Personal finance bestseller', 'Plata Publishing', 'ISBN-9781612680194', 4, 4, 399.00, 299.00, 25.06, 300, 1, 0.35, '210x140x15mm', NULL, NULL, NULL, 7, 1, 1),
(24, 'Atomic Habits', 'Self-improvement guide by James Clear', 'Random House', 'ISBN-9780735211292', 4, 4, 599.00, 449.00, 25.04, 250, 1, 0.40, '210x140x20mm', NULL, NULL, NULL, 7, 1, 1),
(25, 'The Psychology of Money', 'Financial wisdom book', 'Harriman House', 'ISBN-9780857197689', 4, 4, 450.00, 349.00, 22.44, 200, 1, 0.32, '198x129x18mm', NULL, NULL, NULL, 7, 0, 1),
(26, 'Ikigai', 'Japanese secret to long life', 'Penguin', 'ISBN-9781786330895', 4, 4, 399.00, 299.00, 25.06, 280, 1, 0.28, '198x129x15mm', NULL, NULL, NULL, 7, 1, 1),
(27, 'Think Like a Monk', 'Training mind for peace', 'Simon & Schuster', 'ISBN-9781982134488', 4, 4, 499.00, 379.00, 24.05, 180, 1, 0.38, '210x140x18mm', NULL, NULL, NULL, 7, 0, 1),

-- Sports Equipment
(28, 'Cosco Cricket Bat', 'Kashmir willow cricket bat', 'Cosco', 'Century', 5, 5, 2499.00, 1999.00, 20.01, 100, 1, 1.20, '870x108mm', 'Natural', NULL, 3, 7, 0, 1),
(29, 'Nivia Football', 'Professional football size 5', 'Nivia', 'Storm', 5, 5, 1299.00, 999.00, 23.09, 200, 1, 0.45, '220mm dia', 'White/Blue', '5', NULL, 15, 0, 1),
(30, 'Yonex Badminton Racket', 'Professional badminton racket', 'Yonex', 'Nanoray 10F', 5, 5, 4999.00, 3999.00, 20.00, 80, 1, 0.09, '675x210mm', 'Red/Black', NULL, 6, 7, 1, 1),
(31, 'Adidas Gym Bag', 'Large capacity sports duffle bag', 'Adidas', 'Tiro', 5, 5, 2999.00, 2299.00, 23.34, 150, 1, 0.70, '550x250x250mm', 'Black', NULL, NULL, 15, 0, 1),
(32, 'Reebok Yoga Mat', 'Premium anti-slip yoga mat', 'Reebok', 'RBK-YM-2024', 5, 5, 1999.00, 1499.00, 25.01, 120, 1, 1.20, '1830x610x6mm', 'Purple', NULL, NULL, 15, 0, 1),
(33, 'Decathlon Treadmill', 'Home fitness treadmill', 'Decathlon', 'Run 100', 5, 5, 29999.00, 24999.00, 16.67, 30, 1, 35.00, '1500x700x1200mm', 'Gray', NULL, 12, 7, 1, 1),

-- Additional Electronics
(34, 'Sony Wireless Headphones', 'Noise cancelling headphones', 'Sony', 'WH-1000XM5', 1, 1, 29990.00, 24990.00, 16.67, 60, 1, 0.25, '190x152x92mm', 'Black', NULL, 12, 7, 1, 1),
(35, 'Samsung 55" 4K TV', 'Smart 4K UHD television', 'Samsung', 'UA55AU7700', 1, 1, 54990.00, 47990.00, 12.73, 40, 1, 15.50, '1232x711x59mm', 'Black', '55"', 12, 7, 1, 1),
(36, 'Canon EOS 1500D DSLR', 'Entry level DSLR camera', 'Canon', 'EOS 1500D', 1, 1, 39995.00, 32995.00, 17.50, 25, 1, 0.48, '129x101x78mm', 'Black', NULL, 12, 7, 1, 1),

-- Additional Fashion
(37, 'Titan Watch', 'Analog wristwatch for men', 'Titan', 'TT-1234', 8, 2, 5995.00, 4495.00, 25.02, 100, 1, 0.15, '42mm dia', 'Silver', NULL, 24, 15, 0, 1),
(38, 'Fastrack Sunglasses', 'UV protection sunglasses', 'Fastrack', 'FT-SG-2024', 9, 2, 1999.00, 1499.00, 25.01, 180, 1, 0.08, '145mm width', 'Black', NULL, 6, 15, 0, 1),

-- Additional Home
(39, 'Godrej Almirah', '2-door steel almirah', 'Godrej', 'Slimline', 3, 3, 12999.00, 10999.00, 15.39, 50, 1, 45.00, '1800x915x457mm', 'Gray', NULL, 12, 7, 0, 1),
(40, 'Havells Table Fan', '400mm high speed table fan', 'Havells', 'Velocity Neo', 3, 3, 2295.00, 1895.00, 17.43, 150, 1, 3.50, '520x300x460mm', 'White', NULL, 24, 7, 0, 1);

-- ============================================
-- 5. ADDRESSES DATA
-- ============================================
INSERT INTO addresses (address_id, user_id, address_type, full_name, phone, address_line1, address_line2, landmark, city, state, pincode, is_default) VALUES
(1, 1, 'Home', 'Rahul Sharma', '9876543210', 'A-101, Green Park Apartments', 'Sector 15', 'Near Metro Station', 'Delhi', 'Delhi', '110001', 1),
(2, 2, 'Home', 'Priya Singh', '9876543211', 'B-202, Lake View Residency', 'Bandra West', 'Opposite Mall', 'Mumbai', 'Maharashtra', '400050', 1),
(3, 3, 'Work', 'Amit Patel', '9876543212', '3rd Floor, Tech Park', 'Whitefield', 'Behind Bus Stop', 'Bangalore', 'Karnataka', '560066', 1),
(4, 4, 'Home', 'Sneha Reddy', '9876543213', 'Villa 25, Palm Grove', 'Jubilee Hills', 'Near School', 'Hyderabad', 'Telangana', '500033', 1),
(5, 5, 'Home', 'Vikram Kumar', '9876543214', 'Flat 5B, Silver Heights', 'Anna Nagar', 'Corner Plot', 'Chennai', 'Tamil Nadu', '600040', 1),
(6, 6, 'Home', 'Anjali Gupta', '9876543215', '12/A, Riverside Colony', 'Civil Lines', 'Near Park', 'Jaipur', 'Rajasthan', '302006', 1),
(7, 7, 'Work', 'Rohit Mehta', '9876543216', 'Office 401, Business Tower', 'MG Road', 'Metro Accessible', 'Gurgaon', 'Haryana', '122002', 1),
(8, 8, 'Home', 'Kavya Nair', '9876543217', 'House 18, Marine Drive', 'Fort Kochi', 'Beach Road', 'Kochi', 'Kerala', '682001', 1),
(9, 9, 'Home', 'Arjun Desai', '9876543218', 'Bungalow 7, Rose Garden', 'Satellite', 'Near Temple', 'Ahmedabad', 'Gujarat', '380015', 1),
(10, 10, 'Home', 'Pooja Joshi', '9876543219', 'Flat 3C, Sky Towers', 'Kothrud', 'Behind College', 'Pune', 'Maharashtra', '411038', 1),
(11, 1, 'Work', 'Rahul Sharma', '9876543210', 'Corporate Office', 'Cyber City', 'Tower B', 'Gurgaon', 'Haryana', '122003', 0),
(12, 2, 'Work', 'Priya Singh', '9876543211', 'IT Park Building 3', 'Powai', 'Floor 7', 'Mumbai', 'Maharashtra', '400076', 0),
(13, 11, 'Home', 'Karan Chopra', '9876543220', 'C-45, Valley View', 'Vasant Vihar', 'Main Road', 'Delhi', 'Delhi', '110057', 1),
(14, 12, 'Home', 'Neha Verma', '9876543221', 'Apt 801, Crown Plaza', 'Andheri East', 'Near Airport', 'Mumbai', 'Maharashtra', '400059', 1),
(15, 13, 'Home', 'Sanjay Rao', '9876543222', 'Plot 15, Sunshine Colony', 'Indiranagar', 'Bus Stop Nearby', 'Bangalore', 'Karnataka', '560038', 1);

-- ============================================
-- 6. COUPONS DATA
-- ============================================
INSERT INTO coupons (coupon_id, coupon_code, coupon_name, description, discount_type, discount_value, minimum_order_amount, maximum_discount_amount, usage_limit, used_count, valid_from, valid_until, is_active) VALUES
(1, 'WELCOME50', 'Welcome Discount', 'First order discount', 'Fixed Amount', 50.00, 500.00, 50.00, 1000, 234, '2024-01-01', '2024-12-31', 1),
(2, 'SAVE10', '10% Off', 'Get 10% discount on orders', 'Percentage', 10.00, 1000.00, 200.00, 5000, 1567, '2024-01-01', '2024-12-31', 1),
(3, 'MEGA20', 'Mega Sale', '20% discount on electronics', 'Percentage', 20.00, 5000.00, 1000.00, 2000, 456, '2024-06-01', '2024-12-31', 1),
(4, 'FASHION15', 'Fashion Fest', '15% off on fashion items', 'Percentage', 15.00, 2000.00, 500.00, 3000, 789, '2024-03-01', '2024-12-31', 1),
(5, 'SUMMER100', 'Summer Special', 'Flat 100 off', 'Fixed Amount', 100.00, 1500.00, 100.00, 1500, 523, '2024-04-01', '2024-08-31', 1);

-- ============================================
-- 7. ORDERS DATA (300+ orders across 6 months)
-- ============================================
-- This includes realistic order patterns with seasonal variations
-- JULY 2024 (40 orders)
INSERT INTO orders VALUES
(1,1,'ORD-JUL-001','2024-07-01 10:30',69999,0,12600,0,82599,'UPI','Paid','Delivered',1,'2024-07-06','2024-07-05',NOW(),NOW()),
(2,2,'ORD-JUL-002','2024-07-02 14:20',3499,50,621,40,4110,'Credit Card','Paid','Delivered',2,'2024-07-08','2024-07-07',NOW(),NOW()),
(3,3,'ORD-JUL-003','2024-07-03 09:15',149999,0,27000,0,176999,'Net Banking','Paid','Delivered',3,'2024-07-08','2024-07-07',NOW(),NOW()),
(4,4,'ORD-JUL-004','2024-07-05 16:45',2999,300,486,40,3225,'COD','Paid','Delivered',4,'2024-07-10','2024-07-09',NOW(),NOW()),
(5,5,'ORD-JUL-005','2024-07-06 11:20',9995,0,1799,0,11794,'UPI','Paid','Delivered',5,'2024-07-11','2024-07-10',NOW(),NOW()),
(6,6,'ORD-JUL-006','2024-07-08 15:30',2199,0,396,40,2635,'Wallet','Paid','Delivered',6,'2024-07-13','2024-07-12',NOW(),NOW()),
(7,7,'ORD-JUL-007','2024-07-09 10:00',24999,2500,4050,0,26549,'Credit Card','Paid','Delivered',7,'2024-07-14','2024-07-13',NOW(),NOW()),
(8,8,'ORD-JUL-008','2024-07-10 13:45',299,0,54,40,393,'UPI','Paid','Delivered',8,'2024-07-15','2024-07-14',NOW(),NOW()),
(9,9,'ORD-JUL-009','2024-07-11 09:30',51999,0,9360,0,61359,'Net Banking','Paid','Delivered',9,'2024-07-16','2024-07-15',NOW(),NOW()),
(10,10,'ORD-JUL-010','2024-07-12 16:20',3999,0,720,40,4759,'COD','Paid','Delivered',10,'2024-07-17','2024-07-16',NOW(),NOW()),
(11,11,'ORD-JUL-011','2024-07-13 11:15',449,0,81,40,570,'UPI','Paid','Delivered',11,'2024-07-18','2024-07-17',NOW(),NOW()),
(12,12,'ORD-JUL-012','2024-07-14 14:30',54999,0,9900,0,64899,'Credit Card','Paid','Delivered',12,'2024-07-19','2024-07-18',NOW(),NOW()),
(13,13,'ORD-JUL-013','2024-07-15 10:45',2799,0,504,40,3343,'Wallet','Paid','Delivered',13,'2024-07-20','2024-07-19',NOW(),NOW()),
(14,14,'ORD-JUL-014','2024-07-16 15:00',999,0,180,40,1219,'UPI','Paid','Delivered',14,'2024-07-21','2024-07-20',NOW(),NOW()),
(15,15,'ORD-JUL-015','2024-07-17 12:20',1999,0,360,40,2399,'COD','Paid','Delivered',15,'2024-07-22','2024-07-21',NOW(),NOW()),
(16,1,'ORD-JUL-016','2024-07-18 09:30',32995,0,5939,0,38934,'Net Banking','Paid','Delivered',1,'2024-07-23','2024-07-22',NOW(),NOW()),
(17,2,'ORD-JUL-017','2024-07-19 16:45',9995,0,1799,0,11794,'Credit Card','Paid','Delivered',2,'2024-07-24','2024-07-23',NOW(),NOW()),
(18,3,'ORD-JUL-018','2024-07-20 11:00',2495,0,449,40,2984,'UPI','Paid','Delivered',3,'2024-07-25','2024-07-24',NOW(),NOW()),
(19,4,'ORD-JUL-019','2024-07-21 14:15',549,0,99,40,688,'Wallet','Paid','Delivered',4,'2024-07-26','2024-07-25',NOW(),NOW()),
(20,5,'ORD-JUL-020','2024-07-22 10:30',119900,0,21582,0,141482,'Net Banking','Paid','Delivered',5,'2024-07-27','2024-07-26',NOW(),NOW()),
(21,6,'ORD-JUL-021','2024-07-23 15:50',299,50,45,40,334,'UPI','Paid','Delivered',6,'2024-07-28','2024-07-27',NOW(),NOW()),
(22,7,'ORD-JUL-022','2024-07-24 12:00',3999,0,720,40,4759,'COD','Paid','Delivered',7,'2024-07-29','2024-07-28',NOW(),NOW()),
(23,8,'ORD-JUL-023','2024-07-25 09:45',24990,0,4498,0,29488,'Credit Card','Paid','Delivered',8,'2024-07-30','2024-07-29',NOW(),NOW()),
(24,9,'ORD-JUL-024','2024-07-26 14:20',1499,0,270,40,1809,'UPI','Paid','Delivered',9,'2024-07-31','2024-07-30',NOW(),NOW()),
(25,10,'ORD-JUL-025','2024-07-27 11:30',72999,7300,11826,0,77525,'Net Banking','Paid','Delivered',10,'2024-08-01','2024-07-31',NOW(),NOW()),
(26,11,'ORD-JUL-026','2024-07-28 16:00',995,0,179,40,1214,'Wallet','Paid','Delivered',11,'2024-08-02','2024-08-01',NOW(),NOW()),
(27,12,'ORD-JUL-027','2024-07-29 10:15',2999,0,540,40,3579,'COD','Paid','Delivered',12,'2024-08-03','2024-08-02',NOW(),NOW()),
(28,13,'ORD-JUL-028','2024-07-29 13:40',47990,0,8638,0,56628,'Credit Card','Paid','Delivered',13,'2024-08-03','2024-08-02',NOW(),NOW()),
(29,14,'ORD-JUL-029','2024-07-30 09:55',1799,0,324,40,2163,'UPI','Paid','Delivered',14,'2024-08-04','2024-08-03',NOW(),NOW()),
(30,15,'ORD-JUL-030','2024-07-30 15:20',349,0,63,40,452,'Wallet','Paid','Delivered',15,'2024-08-04','2024-08-03',NOW(),NOW()),
(31,1,'ORD-JUL-031','2024-07-31 11:45',159999,0,28800,0,188799,'Net Banking','Paid','Delivered',1,'2024-08-05','2024-08-04',NOW(),NOW()),
(32,2,'ORD-JUL-032','2024-07-31 14:10',2299,0,414,40,2753,'COD','Paid','Delivered',2,'2024-08-05','2024-08-04',NOW(),NOW()),
(33,3,'ORD-JUL-033','2024-07-31 10:30',189900,0,34182,0,224082,'Credit Card','Paid','Delivered',3,'2024-08-05','2024-08-04',NOW(),NOW()),
(34,4,'ORD-JUL-034','2024-07-31 16:50',4495,0,809,40,5344,'UPI','Paid','Delivered',4,'2024-08-05','2024-08-04',NOW(),NOW()),
(35,5,'ORD-JUL-035','2024-07-31 12:15',379,0,68,40,487,'Wallet','Paid','Delivered',5,'2024-08-05','2024-08-04',NOW(),NOW()),
(36,6,'ORD-JUL-036','2024-07-31 15:40',999,0,180,40,1219,'COD','Paid','Delivered',6,'2024-08-05','2024-08-04',NOW(),NOW()),
(37,7,'ORD-JUL-037','2024-07-31 10:00',1499,0,270,40,1809,'UPI','Paid','Delivered',7,'2024-08-05','2024-08-04',NOW(),NOW()),
(38,8,'ORD-JUL-038','2024-07-31 13:25',10999,0,1980,40,13019,'Net Banking','Paid','Delivered',8,'2024-08-05','2024-08-04',NOW(),NOW()),
(39,9,'ORD-JUL-039','2024-07-31 16:55',2795,0,503,40,3338,'Credit Card','Paid','Delivered',9,'2024-08-05','2024-08-04',NOW(),NOW()),
(40,10,'ORD-JUL-040','2024-07-31 19:30',299,0,54,40,393,'UPI','Paid','Delivered',10,'2024-08-05','2024-08-04',NOW(),NOW());

-- AUGUST 2024 (50 orders - Peak Season)
INSERT INTO orders VALUES
(41,11,'ORD-AUG-041','2024-08-01 10:15',69999,0,12600,0,82599,'Net Banking','Paid','Delivered',11,'2024-08-06','2024-08-05',NOW(),NOW()),
(42,12,'ORD-AUG-042','2024-08-01 14:30',3499,0,630,40,4169,'COD','Paid','Delivered',12,'2024-08-07','2024-08-06',NOW(),NOW()),
(43,13,'ORD-AUG-043','2024-08-02 09:45',24999,0,4500,0,29499,'UPI','Paid','Delivered',13,'2024-08-07','2024-08-06',NOW(),NOW()),
(44,14,'ORD-AUG-044','2024-08-02 13:20',2999,50,531,40,3520,'Credit Card','Paid','Delivered',14,'2024-08-08','2024-08-07',NOW(),NOW()),
(45,15,'ORD-AUG-045','2024-08-03 11:00',1895,0,341,40,2276,'Wallet','Paid','Delivered',15,'2024-08-09','2024-08-08',NOW(),NOW()),
(46,1,'ORD-AUG-046','2024-08-04 15:35',449,0,81,40,570,'UPI','Paid','Delivered',1,'2024-08-10','2024-08-09',NOW(),NOW()),
(47,2,'ORD-AUG-047','2024-08-05 10:25',119900,0,21582,0,141482,'Net Banking','Paid','Delivered',2,'2024-08-10','2024-08-09',NOW(),NOW()),
(48,3,'ORD-AUG-048','2024-08-06 14:50',2999,300,486,40,3225,'COD','Paid','Delivered',3,'2024-08-12','2024-08-11',NOW(),NOW()),
(49,4,'ORD-AUG-049','2024-08-07 09:10',9995,0,1799,0,11794,'Credit Card','Paid','Delivered',4,'2024-08-12','2024-08-11',NOW(),NOW()),
(50,5,'ORD-AUG-050','2024-08-08 16:20',2199,0,396,40,2635,'UPI','Paid','Delivered',5,'2024-08-14','2024-08-13',NOW(),NOW()),
(51,6,'ORD-AUG-051','2024-08-09 11:40',51999,5200,8424,0,55223,'Wallet','Paid','Delivered',6,'2024-08-14','2024-08-13',NOW(),NOW()),
(52,7,'ORD-AUG-052','2024-08-10 15:05',299,0,54,40,393,'COD','Paid','Delivered',7,'2024-08-16','2024-08-15',NOW(),NOW()),
(53,8,'ORD-AUG-053','2024-08-11 10:30',72999,0,13140,0,86139,'Net Banking','Paid','Delivered',8,'2024-08-16','2024-08-15',NOW(),NOW()),
(54,9,'ORD-AUG-054','2024-08-12 14:45',3999,0,720,40,4759,'UPI','Paid','Delivered',9,'2024-08-18','2024-08-17',NOW(),NOW()),
(55,10,'ORD-AUG-055','2024-08-13 09:55',149999,0,27000,0,176999,'Credit Card','Paid','Delivered',10,'2024-08-18','2024-08-17',NOW(),NOW()),
(56,11,'ORD-AUG-056','2024-08-14 13:20',1499,0,270,40,1809,'Wallet','Paid','Delivered',11,'2024-08-20','2024-08-19',NOW(),NOW()),
(57,12,'ORD-AUG-057','2024-08-15 11:35',54999,0,9900,0,64899,'COD','Paid','Delivered',12,'2024-08-20','2024-08-19',NOW(),NOW()),
(58,13,'ORD-AUG-058','2024-08-16 15:50',2799,0,504,40,3343,'Net Banking','Paid','Delivered',13,'2024-08-22','2024-08-21',NOW(),NOW()),
(59,14,'ORD-AUG-059','2024-08-17 10:20',995,0,179,40,1214,'UPI','Paid','Delivered',14,'2024-08-23','2024-08-22',NOW(),NOW()),
(60,15,'ORD-AUG-060','2024-08-18 14:35',24990,0,4498,0,29488,'Credit Card','Paid','Delivered',15,'2024-08-23','2024-08-22',NOW(),NOW()),
(61,1,'ORD-AUG-061','2024-08-19 09:00',1799,0,324,40,2163,'Wallet','Paid','Delivered',1,'2024-08-25','2024-08-24',NOW(),NOW()),
(62,2,'ORD-AUG-062','2024-08-20 13:25',379,0,68,40,487,'COD','Paid','Delivered',2,'2024-08-26','2024-08-25',NOW(),NOW()),
(63,3,'ORD-AUG-063','2024-08-21 11:50',159999,0,28800,0,188799,'Net Banking','Paid','Delivered',3,'2024-08-26','2024-08-25',NOW(),NOW()),
(64,4,'ORD-AUG-064','2024-08-22 16:05',2299,0,414,40,2753,'UPI','Paid','Delivered',4,'2024-08-28','2024-08-27',NOW(),NOW()),
(65,5,'ORD-AUG-065','2024-08-23 10:30',189900,0,34182,0,224082,'Credit Card','Paid','Delivered',5,'2024-08-28','2024-08-27',NOW(),NOW()),
(66,6,'ORD-AUG-066','2024-08-24 14:45',4495,0,809,40,5344,'Wallet','Paid','Delivered',6,'2024-08-30','2024-08-29',NOW(),NOW()),
(67,7,'ORD-AUG-067','2024-08-25 09:15',999,0,180,40,1219,'COD','Paid','Delivered',7,'2024-08-31','2024-08-30',NOW(),NOW()),
(68,8,'ORD-AUG-068','2024-08-26 13:30',1499,0,270,40,1809,'Net Banking','Paid','Delivered',8,'2024-09-01','2024-08-31',NOW(),NOW()),
(69,9,'ORD-AUG-069','2024-08-27 11:55',10999,0,1980,40,13019,'UPI','Paid','Delivered',9,'2024-09-02','2024-09-01',NOW(),NOW()),
(70,10,'ORD-AUG-070','2024-08-28 16:10',2795,0,503,40,3338,'Credit Card','Paid','Delivered',10,'2024-09-03','2024-09-02',NOW(),NOW()),
(71,11,'ORD-AUG-071','2024-08-29 10:25',32995,0,5939,0,38934,'Wallet','Paid','Delivered',11,'2024-09-03','2024-09-02',NOW(),NOW()),
(72,12,'ORD-AUG-072','2024-08-30 14:40',47990,0,8638,0,56628,'COD','Paid','Delivered',12,'2024-09-05','2024-09-04',NOW(),NOW()),
(73,13,'ORD-AUG-073','2024-08-30 09:05',2495,0,449,40,2984,'Net Banking','Paid','Delivered',13,'2024-09-05','2024-09-04',NOW(),NOW()),
(74,14,'ORD-AUG-074','2024-08-31 13:20',549,0,99,40,688,'UPI','Paid','Delivered',14,'2024-09-06','2024-09-05',NOW(),NOW()),
(75,15,'ORD-AUG-075','2024-08-31 11:45',24999,0,4500,0,29499,'Credit Card','Paid','Delivered',15,'2024-09-05','2024-09-04',NOW(),NOW()),
(76,1,'ORD-AUG-076','2024-08-31 15:00',69999,0,12600,0,82599,'Wallet','Paid','Delivered',1,'2024-09-05','2024-09-04',NOW(),NOW()),
(77,2,'ORD-AUG-077','2024-08-31 10:30',3499,0,630,40,4169,'COD','Paid','Delivered',2,'2024-09-05','2024-09-04',NOW(),NOW()),
(78,3,'ORD-AUG-078','2024-08-31 14:15',9995,0,1799,0,11794,'Net Banking','Paid','Delivered',3,'2024-09-05','2024-09-04',NOW(),NOW()),
(79,4,'ORD-AUG-079','2024-08-31 09:50',2999,300,486,40,3225,'UPI','Paid','Delivered',4,'2024-09-05','2024-09-04',NOW(),NOW()),
(80,5,'ORD-AUG-080','2024-08-31 16:25',2199,0,396,40,2635,'Credit Card','Paid','Delivered',5,'2024-09-05','2024-09-04',NOW(),NOW()),
(81,6,'ORD-AUG-081','2024-08-31 11:40',51999,5200,8424,0,55223,'Wallet','Paid','Delivered',6,'2024-09-05','2024-09-04',NOW(),NOW()),
(82,7,'ORD-AUG-082','2024-08-31 15:05',299,0,54,40,393,'COD','Paid','Delivered',7,'2024-09-05','2024-09-04',NOW(),NOW()),
(83,8,'ORD-AUG-083','2024-08-31 10:30',72999,0,13140,0,86139,'Net Banking','Paid','Delivered',8,'2024-09-05','2024-09-04',NOW(),NOW()),
(84,9,'ORD-AUG-084','2024-08-31 14:45',3999,0,720,40,4759,'UPI','Paid','Delivered',9,'2024-09-05','2024-09-04',NOW(),NOW()),
(85,10,'ORD-AUG-085','2024-08-31 09:55',149999,0,27000,0,176999,'Credit Card','Paid','Delivered',10,'2024-09-05','2024-09-04',NOW(),NOW()),
(86,11,'ORD-AUG-086','2024-08-31 13:20',1499,0,270,40,1809,'Wallet','Paid','Delivered',11,'2024-09-05','2024-09-04',NOW(),NOW()),
(87,12,'ORD-AUG-087','2024-08-31 11:35',54999,0,9900,0,64899,'COD','Paid','Delivered',12,'2024-09-05','2024-09-04',NOW(),NOW()),
(88,13,'ORD-AUG-088','2024-08-31 15:50',2799,0,504,40,3343,'Net Banking','Paid','Delivered',13,'2024-09-05','2024-09-04',NOW(),NOW()),
(89,14,'ORD-AUG-089','2024-08-31 10:20',995,0,179,40,1214,'UPI','Paid','Delivered',14,'2024-09-05','2024-09-04',NOW(),NOW()),
(90,15,'ORD-AUG-090','2024-08-31 14:35',24990,0,4498,0,29488,'Credit Card','Paid','Delivered',15,'2024-09-05','2024-09-04',NOW(),NOW());

-- Continue in next message for Sep-Dec orders and order items...

-- SEPTEMBER 2024 (40 orders)
INSERT INTO orders VALUES
(91,1,'ORD-SEP-091','2024-09-02 10:15',119900,0,21582,0,141482,'UPI','Paid','Delivered',1,'2024-09-07','2024-09-06',NOW(),NOW()),
(92,2,'ORD-SEP-092','2024-09-03 14:30',3499,50,621,40,4110,'COD','Paid','Delivered',2,'2024-09-09','2024-09-08',NOW(),NOW()),
(93,3,'ORD-SEP-093','2024-09-04 09:45',24999,0,4500,0,29499,'Credit Card','Paid','Delivered',3,'2024-09-09','2024-09-08',NOW(),NOW()),
(94,4,'ORD-SEP-094','2024-09-05 13:20',2999,300,486,40,3225,'Net Banking','Paid','Delivered',4,'2024-09-11','2024-09-10',NOW(),NOW()),
(95,5,'ORD-SEP-095','2024-09-06 11:00',9995,0,1799,0,11794,'Wallet','Paid','Delivered',5,'2024-09-12','2024-09-11',NOW(),NOW()),
(96,6,'ORD-SEP-096','2024-09-07 15:35',2199,0,396,40,2635,'UPI','Paid','Delivered',6,'2024-09-13','2024-09-12',NOW(),NOW()),
(97,7,'ORD-SEP-097','2024-09-08 10:25',51999,5200,8424,0,55223,'COD','Paid','Delivered',7,'2024-09-13','2024-09-12',NOW(),NOW()),
(98,8,'ORD-SEP-098','2024-09-09 14:50',299,0,54,40,393,'Credit Card','Paid','Delivered',8,'2024-09-15','2024-09-14',NOW(),NOW()),
(99,9,'ORD-SEP-099','2024-09-10 09:10',72999,0,13140,0,86139,'Net Banking','Paid','Delivered',9,'2024-09-15','2024-09-14',NOW(),NOW()),
(100,10,'ORD-SEP-100','2024-09-11 16:20',3999,0,720,40,4759,'UPI','Paid','Delivered',10,'2024-09-17','2024-09-16',NOW(),NOW()),
(101,11,'ORD-SEP-101','2024-09-12 11:40',149999,0,27000,0,176999,'Wallet','Paid','Delivered',11,'2024-09-17','2024-09-16',NOW(),NOW()),
(102,12,'ORD-SEP-102','2024-09-13 15:05',1499,0,270,40,1809,'COD','Paid','Delivered',12,'2024-09-19','2024-09-18',NOW(),NOW()),
(103,13,'ORD-SEP-103','2024-09-14 10:30',54999,0,9900,0,64899,'Credit Card','Paid','Delivered',13,'2024-09-19','2024-09-18',NOW(),NOW()),
(104,14,'ORD-SEP-104','2024-09-15 14:45',2799,0,504,40,3343,'Net Banking','Paid','Delivered',14,'2024-09-21','2024-09-20',NOW(),NOW()),
(105,15,'ORD-SEP-105','2024-09-16 09:55',995,0,179,40,1214,'UPI','Paid','Delivered',15,'2024-09-22','2024-09-21',NOW(),NOW()),
(106,1,'ORD-SEP-106','2024-09-17 13:20',24990,0,4498,0,29488,'Wallet','Paid','Delivered',1,'2024-09-22','2024-09-21',NOW(),NOW()),
(107,2,'ORD-SEP-107','2024-09-18 11:35',1799,0,324,40,2163,'COD','Paid','Delivered',2,'2024-09-24','2024-09-23',NOW(),NOW()),
(108,3,'ORD-SEP-108','2024-09-19 15:50',379,0,68,40,487,'Credit Card','Paid','Delivered',3,'2024-09-25','2024-09-24',NOW(),NOW()),
(109,4,'ORD-SEP-109','2024-09-20 10:20',159999,0,28800,0,188799,'Net Banking','Paid','Delivered',4,'2024-09-25','2024-09-24',NOW(),NOW()),
(110,5,'ORD-SEP-110','2024-09-21 14:35',2299,0,414,40,2753,'UPI','Paid','Delivered',5,'2024-09-27','2024-09-26',NOW(),NOW()),
(111,6,'ORD-SEP-111','2024-09-22 09:00',189900,0,34182,0,224082,'Wallet','Paid','Delivered',6,'2024-09-27','2024-09-26',NOW(),NOW()),
(112,7,'ORD-SEP-112','2024-09-23 13:25',4495,0,809,40,5344,'COD','Paid','Delivered',7,'2024-09-29','2024-09-28',NOW(),NOW()),
(113,8,'ORD-SEP-113','2024-09-24 11:50',999,0,180,40,1219,'Credit Card','Paid','Delivered',8,'2024-09-30','2024-09-29',NOW(),NOW()),
(114,9,'ORD-SEP-114','2024-09-25 16:05',1499,0,270,40,1809,'Net Banking','Paid','Delivered',9,'2024-10-01','2024-09-30',NOW(),NOW()),
(115,10,'ORD-SEP-115','2024-09-26 10:30',10999,0,1980,40,13019,'UPI','Paid','Delivered',10,'2024-10-02','2024-10-01',NOW(),NOW()),
(116,11,'ORD-SEP-116','2024-09-27 14:45',2795,0,503,40,3338,'Wallet','Paid','Delivered',11,'2024-10-03','2024-10-02',NOW(),NOW()),
(117,12,'ORD-SEP-117','2024-09-28 09:15',32995,0,5939,0,38934,'COD','Paid','Delivered',12,'2024-10-03','2024-10-02',NOW(),NOW()),
(118,13,'ORD-SEP-118','2024-09-29 13:30',47990,0,8638,0,56628,'Credit Card','Paid','Delivered',13,'2024-10-05','2024-10-04',NOW(),NOW()),
(119,14,'ORD-SEP-119','2024-09-29 11:55',2495,0,449,40,2984,'Net Banking','Paid','Delivered',14,'2024-10-05','2024-10-04',NOW(),NOW()),
(120,15,'ORD-SEP-120','2024-09-30 16:10',549,0,99,40,688,'UPI','Paid','Delivered',15,'2024-10-06','2024-10-05',NOW(),NOW()),
(121,1,'ORD-SEP-121','2024-09-30 10:25',24999,0,4500,0,29499,'Wallet','Paid','Delivered',1,'2024-10-05','2024-10-04',NOW(),NOW()),
(122,2,'ORD-SEP-122','2024-09-30 14:40',69999,0,12600,0,82599,'COD','Paid','Delivered',2,'2024-10-05','2024-10-04',NOW(),NOW()),
(123,3,'ORD-SEP-123','2024-09-30 09:05',3499,0,630,40,4169,'Credit Card','Paid','Delivered',3,'2024-10-05','2024-10-04',NOW(),NOW()),
(124,4,'ORD-SEP-124','2024-09-30 13:20',9995,0,1799,0,11794,'Net Banking','Paid','Delivered',4,'2024-10-05','2024-10-04',NOW(),NOW()),
(125,5,'ORD-SEP-125','2024-09-30 11:45',2999,300,486,40,3225,'UPI','Paid','Delivered',5,'2024-10-05','2024-10-04',NOW(),NOW()),
(126,6,'ORD-SEP-126','2024-09-30 15:00',2199,0,396,40,2635,'Wallet','Paid','Delivered',6,'2024-10-05','2024-10-04',NOW(),NOW()),
(127,7,'ORD-SEP-127','2024-09-30 10:30',51999,5200,8424,0,55223,'COD','Paid','Delivered',7,'2024-10-05','2024-10-04',NOW(),NOW()),
(128,8,'ORD-SEP-128','2024-09-30 14:15',299,0,54,40,393,'Credit Card','Paid','Delivered',8,'2024-10-05','2024-10-04',NOW(),NOW()),
(129,9,'ORD-SEP-129','2024-09-30 09:50',72999,0,13140,0,86139,'Net Banking','Paid','Delivered',9,'2024-10-05','2024-10-04',NOW(),NOW()),
(130,10,'ORD-SEP-130','2024-09-30 16:25',3999,0,720,40,4759,'UPI','Paid','Delivered',10,'2024-10-05','2024-10-04',NOW(),NOW());

-- OCTOBER 2024 (55 orders - Festive Season Peak)
INSERT INTO orders VALUES
(131,11,'ORD-OCT-131','2024-10-01 10:00',149999,0,27000,0,176999,'Wallet','Paid','Delivered',11,'2024-10-06','2024-10-05',NOW(),NOW()),
(132,12,'ORD-OCT-132','2024-10-01 14:30',1499,0,270,40,1809,'COD','Paid','Delivered',12,'2024-10-07','2024-10-06',NOW(),NOW()),
(133,13,'ORD-OCT-133','2024-10-02 09:45',54999,0,9900,0,64899,'Credit Card','Paid','Delivered',13,'2024-10-07','2024-10-06',NOW(),NOW()),
(134,14,'ORD-OCT-134','2024-10-02 13:20',2799,0,504,40,3343,'Net Banking','Paid','Delivered',14,'2024-10-08','2024-10-07',NOW(),NOW()),
(135,15,'ORD-OCT-135','2024-10-03 11:00',995,0,179,40,1214,'UPI','Paid','Delivered',15,'2024-10-09','2024-10-08',NOW(),NOW()),
(136,1,'ORD-OCT-136','2024-10-03 15:35',24990,0,4498,0,29488,'Wallet','Paid','Delivered',1,'2024-10-09','2024-10-08',NOW(),NOW()),
(137,2,'ORD-OCT-137','2024-10-04 10:25',1799,0,324,40,2163,'COD','Paid','Delivered',2,'2024-10-10','2024-10-09',NOW(),NOW()),
(138,3,'ORD-OCT-138','2024-10-04 14:50',379,0,68,40,487,'Credit Card','Paid','Delivered',3,'2024-10-10','2024-10-09',NOW(),NOW()),
(139,4,'ORD-OCT-139','2024-10-05 09:10',159999,0,28800,0,188799,'Net Banking','Paid','Delivered',4,'2024-10-10','2024-10-09',NOW(),NOW()),
(140,5,'ORD-OCT-140','2024-10-05 16:20',2299,0,414,40,2753,'UPI','Paid','Delivered',5,'2024-10-11','2024-10-10',NOW(),NOW()),
(141,6,'ORD-OCT-141','2024-10-06 11:40',189900,0,34182,0,224082,'Wallet','Paid','Delivered',6,'2024-10-11','2024-10-10',NOW(),NOW()),
(142,7,'ORD-OCT-142','2024-10-07 15:05',4495,0,809,40,5344,'COD','Paid','Delivered',7,'2024-10-13','2024-10-12',NOW(),NOW()),
(143,8,'ORD-OCT-143','2024-10-08 10:30',999,0,180,40,1219,'Credit Card','Paid','Delivered',8,'2024-10-14','2024-10-13',NOW(),NOW()),
(144,9,'ORD-OCT-144','2024-10-09 14:45',1499,0,270,40,1809,'Net Banking','Paid','Delivered',9,'2024-10-15','2024-10-14',NOW(),NOW()),
(145,10,'ORD-OCT-145','2024-10-10 09:55',10999,0,1980,40,13019,'UPI','Paid','Delivered',10,'2024-10-16','2024-10-15',NOW(),NOW()),
(146,11,'ORD-OCT-146','2024-10-11 13:20',2795,0,503,40,3338,'Wallet','Paid','Delivered',11,'2024-10-17','2024-10-16',NOW(),NOW()),
(147,12,'ORD-OCT-147','2024-10-12 11:35',32995,0,5939,0,38934,'COD','Paid','Delivered',12,'2024-10-17','2024-10-16',NOW(),NOW()),
(148,13,'ORD-OCT-148','2024-10-13 15:50',47990,0,8638,0,56628,'Credit Card','Paid','Delivered',13,'2024-10-19','2024-10-18',NOW(),NOW()),
(149,14,'ORD-OCT-149','2024-10-14 10:20',2495,0,449,40,2984,'Net Banking','Paid','Delivered',14,'2024-10-20','2024-10-19',NOW(),NOW()),
(150,15,'ORD-OCT-150','2024-10-15 14:35',549,0,99,40,688,'UPI','Paid','Delivered',15,'2024-10-21','2024-10-20',NOW(),NOW()),
(151,1,'ORD-OCT-151','2024-10-16 09:00',24999,0,4500,0,29499,'Wallet','Paid','Delivered',1,'2024-10-21','2024-10-20',NOW(),NOW()),
(152,2,'ORD-OCT-152','2024-10-17 13:25',69999,0,12600,0,82599,'COD','Paid','Delivered',2,'2024-10-23','2024-10-22',NOW(),NOW()),
(153,3,'ORD-OCT-153','2024-10-18 11:50',3499,0,630,40,4169,'Credit Card','Paid','Delivered',3,'2024-10-24','2024-10-23',NOW(),NOW()),
(154,4,'ORD-OCT-154','2024-10-19 16:05',9995,0,1799,0,11794,'Net Banking','Paid','Delivered',4,'2024-10-25','2024-10-24',NOW(),NOW()),
(155,5,'ORD-OCT-155','2024-10-20 10:30',2999,300,486,40,3225,'UPI','Paid','Delivered',5,'2024-10-26','2024-10-25',NOW(),NOW()),
(156,6,'ORD-OCT-156','2024-10-21 14:45',2199,0,396,40,2635,'Wallet','Paid','Delivered',6,'2024-10-27','2024-10-26',NOW(),NOW()),
(157,7,'ORD-OCT-157','2024-10-22 09:15',51999,5200,8424,0,55223,'COD','Paid','Delivered',7,'2024-10-27','2024-10-26',NOW(),NOW()),
(158,8,'ORD-OCT-158','2024-10-23 13:30',299,0,54,40,393,'Credit Card','Paid','Delivered',8,'2024-10-29','2024-10-28',NOW(),NOW()),
(159,9,'ORD-OCT-159','2024-10-24 11:55',72999,0,13140,0,86139,'Net Banking','Paid','Delivered',9,'2024-10-30','2024-10-29',NOW(),NOW()),
(160,10,'ORD-OCT-160','2024-10-25 16:10',3999,0,720,40,4759,'UPI','Paid','Delivered',10,'2024-10-31','2024-10-30',NOW(),NOW()),
(161,11,'ORD-OCT-161','2024-10-26 10:25',149999,0,27000,0,176999,'Wallet','Paid','Delivered',11,'2024-10-31','2024-10-30',NOW(),NOW()),
(162,12,'ORD-OCT-162','2024-10-27 14:40',1499,0,270,40,1809,'COD','Paid','Delivered',12,'2024-11-02','2024-11-01',NOW(),NOW()),
(163,13,'ORD-OCT-163','2024-10-28 09:05',54999,0,9900,0,64899,'Credit Card','Paid','Delivered',13,'2024-11-03','2024-11-02',NOW(),NOW()),
(164,14,'ORD-OCT-164','2024-10-29 13:20',2799,0,504,40,3343,'Net Banking','Paid','Delivered',14,'2024-11-04','2024-11-03',NOW(),NOW()),
(165,15,'ORD-OCT-165','2024-10-30 11:45',995,0,179,40,1214,'UPI','Paid','Delivered',15,'2024-11-05','2024-11-04',NOW(),NOW()),
(166,1,'ORD-OCT-166','2024-10-30 15:00',24990,0,4498,0,29488,'Wallet','Paid','Delivered',1,'2024-11-04','2024-11-03',NOW(),NOW()),
(167,2,'ORD-OCT-167','2024-10-31 10:30',1799,0,324,40,2163,'COD','Paid','Delivered',2,'2024-11-06','2024-11-05',NOW(),NOW()),
(168,3,'ORD-OCT-168','2024-10-31 14:15',379,0,68,40,487,'Credit Card','Paid','Delivered',3,'2024-11-05','2024-11-04',NOW(),NOW()),
(169,4,'ORD-OCT-169','2024-10-31 09:50',159999,0,28800,0,188799,'Net Banking','Paid','Delivered',4,'2024-11-05','2024-11-04',NOW(),NOW()),
(170,5,'ORD-OCT-170','2024-10-31 16:25',2299,0,414,40,2753,'UPI','Paid','Delivered',5,'2024-11-05','2024-11-04',NOW(),NOW()),
(171,6,'ORD-OCT-171','2024-10-31 11:40',189900,0,34182,0,224082,'Wallet','Paid','Delivered',6,'2024-11-05','2024-11-04',NOW(),NOW()),
(172,7,'ORD-OCT-172','2024-10-31 15:05',4495,0,809,40,5344,'COD','Paid','Delivered',7,'2024-11-05','2024-11-04',NOW(),NOW()),
(173,8,'ORD-OCT-173','2024-10-31 10:30',999,0,180,40,1219,'Credit Card','Paid','Delivered',8,'2024-11-05','2024-11-04',NOW(),NOW()),
(174,9,'ORD-OCT-174','2024-10-31 14:45',1499,0,270,40,1809,'Net Banking','Paid','Delivered',9,'2024-11-05','2024-11-04',NOW(),NOW()),
(175,10,'ORD-OCT-175','2024-10-31 09:55',10999,0,1980,40,13019,'UPI','Paid','Delivered',10,'2024-11-05','2024-11-04',NOW(),NOW()),
(176,11,'ORD-OCT-176','2024-10-31 13:20',2795,0,503,40,3338,'Wallet','Paid','Delivered',11,'2024-11-05','2024-11-04',NOW(),NOW()),
(177,12,'ORD-OCT-177','2024-10-31 11:35',32995,0,5939,0,38934,'COD','Paid','Delivered',12,'2024-11-05','2024-11-04',NOW(),NOW()),
(178,13,'ORD-OCT-178','2024-10-31 15:50',47990,0,8638,0,56628,'Credit Card','Paid','Delivered',13,'2024-11-05','2024-11-04',NOW(),NOW()),
(179,14,'ORD-OCT-179','2024-10-31 10:20',2495,0,449,40,2984,'Net Banking','Paid','Delivered',14,'2024-11-05','2024-11-04',NOW(),NOW()),
(180,15,'ORD-OCT-180','2024-10-31 14:35',549,0,99,40,688,'UPI','Paid','Delivered',15,'2024-11-05','2024-11-04',NOW(),NOW()),
(181,1,'ORD-OCT-181','2024-10-31 09:00',24999,0,4500,0,29499,'Wallet','Paid','Delivered',1,'2024-11-05','2024-11-04',NOW(),NOW()),
(182,2,'ORD-OCT-182','2024-10-31 13:25',69999,0,12600,0,82599,'COD','Paid','Delivered',2,'2024-11-05','2024-11-04',NOW(),NOW()),
(183,3,'ORD-OCT-183','2024-10-31 11:50',3499,0,630,40,4169,'Credit Card','Paid','Delivered',3,'2024-11-05','2024-11-04',NOW(),NOW()),
(184,4,'ORD-OCT-184','2024-10-31 16:05',9995,0,1799,0,11794,'Net Banking','Paid','Delivered',4,'2024-11-05','2024-11-04',NOW(),NOW()),
(185,5,'ORD-OCT-185','2024-10-31 10:30',2999,300,486,40,3225,'UPI','Paid','Delivered',5,'2024-11-05','2024-11-04',NOW(),NOW());

-- NOVEMBER & DECEMBER 2024 (55 more orders)
INSERT INTO orders VALUES
(186,6,'ORD-NOV-186','2024-11-01 10:00',2199,0,396,40,2635,'Wallet','Paid','Delivered',6,'2024-11-06','2024-11-05',NOW(),NOW()),
(187,7,'ORD-NOV-187','2024-11-02 14:30',51999,5200,8424,0,55223,'COD','Paid','Delivered',7,'2024-11-07','2024-11-06',NOW(),NOW()),
(188,8,'ORD-NOV-188','2024-11-03 09:45',299,0,54,40,393,'Credit Card','Paid','Delivered',8,'2024-11-08','2024-11-07',NOW(),NOW()),
(189,9,'ORD-NOV-189','2024-11-04 13:20',72999,0,13140,0,86139,'Net Banking','Paid','Delivered',9,'2024-11-09','2024-11-08',NOW(),NOW()),
(190,10,'ORD-NOV-190','2024-11-05 11:00',3999,0,720,40,4759,'UPI','Paid','Delivered',10,'2024-11-10','2024-11-09',NOW(),NOW()),
(191,11,'ORD-NOV-191','2024-11-06 15:35',149999,0,27000,0,176999,'Wallet','Paid','Delivered',11,'2024-11-11','2024-11-10',NOW(),NOW()),
(192,12,'ORD-NOV-192','2024-11-07 10:25',1499,0,270,40,1809,'COD','Paid','Delivered',12,'2024-11-12','2024-11-11',NOW(),NOW()),
(193,13,'ORD-NOV-193','2024-11-08 14:50',54999,0,9900,0,64899,'Credit Card','Paid','Delivered',13,'2024-11-13','2024-11-12',NOW(),NOW()),
(194,14,'ORD-NOV-194','2024-11-09 09:10',2799,0,504,40,3343,'Net Banking','Paid','Delivered',14,'2024-11-14','2024-11-13',NOW(),NOW()),
(195,15,'ORD-NOV-195','2024-11-10 16:20',995,0,179,40,1214,'UPI','Paid','Delivered',15,'2024-11-15','2024-11-14',NOW(),NOW()),
(196,1,'ORD-NOV-196','2024-11-11 11:40',24990,0,4498,0,29488,'Wallet','Paid','Delivered',1,'2024-11-16','2024-11-15',NOW(),NOW()),
(197,2,'ORD-NOV-197','2024-11-12 15:05',1799,0,324,40,2163,'COD','Paid','Delivered',2,'2024-11-17','2024-11-16',NOW(),NOW()),
(198,3,'ORD-NOV-198','2024-11-13 10:30',379,0,68,40,487,'Credit Card','Paid','Delivered',3,'2024-11-18','2024-11-17',NOW(),NOW()),
(199,4,'ORD-NOV-199','2024-11-14 14:45',119900,0,21582,0,141482,'Net Banking','Paid','Delivered',4,'2024-11-19','2024-11-18',NOW(),NOW()),
(200,5,'ORD-NOV-200','2024-11-15 09:55',2299,0,414,40,2753,'UPI','Paid','Delivered',5,'2024-11-20','2024-11-19',NOW(),NOW()),
(201,6,'ORD-NOV-201','2024-11-18 13:20',69999,0,12600,0,82599,'Wallet','Paid','Delivered',6,'2024-11-23','2024-11-22',NOW(),NOW()),
(202,7,'ORD-NOV-202','2024-11-19 11:35',4495,0,809,40,5344,'COD','Paid','Delivered',7,'2024-11-24','2024-11-23',NOW(),NOW()),
(203,8,'ORD-NOV-203','2024-11-20 15:50',999,0,180,40,1219,'Credit Card','Paid','Delivered',8,'2024-11-25','2024-11-24',NOW(),NOW()),
(204,9,'ORD-NOV-204','2024-11-21 10:20',1499,0,270,40,1809,'Net Banking','Paid','Delivered',9,'2024-11-26','2024-11-25',NOW(),NOW()),
(205,10,'ORD-NOV-205','2024-11-22 14:35',10999,0,1980,40,13019,'UPI','Paid','Delivered',10,'2024-11-27','2024-11-26',NOW(),NOW()),
(206,11,'ORD-NOV-206','2024-11-25 09:00',2795,0,503,40,3338,'Wallet','Paid','Delivered',11,'2024-11-30','2024-11-29',NOW(),NOW()),
(207,12,'ORD-NOV-207','2024-11-26 13:25',32995,0,5939,0,38934,'COD','Paid','Delivered',12,'2024-12-01','2024-11-30',NOW(),NOW()),
(208,13,'ORD-NOV-208','2024-11-27 11:50',47990,0,8638,0,56628,'Credit Card','Paid','Delivered',13,'2024-12-02','2024-12-01',NOW(),NOW()),
(209,14,'ORD-NOV-209','2024-11-28 16:05',2495,0,449,40,2984,'Net Banking','Paid','Delivered',14,'2024-12-03','2024-12-02',NOW(),NOW()),
(210,15,'ORD-NOV-210','2024-11-29 10:30',549,0,99,40,688,'UPI','Paid','Delivered',15,'2024-12-04','2024-12-03',NOW(),NOW()),
(211,1,'ORD-NOV-211','2024-11-30 14:45',24999,0,4500,0,29499,'Wallet','Paid','Delivered',1,'2024-12-05','2024-12-04',NOW(),NOW()),
(212,2,'ORD-NOV-212','2024-11-30 09:15',69999,0,12600,0,82599,'COD','Paid','Delivered',2,'2024-12-05','2024-12-04',NOW(),NOW()),
(213,3,'ORD-NOV-213','2024-11-30 13:30',3499,0,630,40,4169,'Credit Card','Paid','Delivered',3,'2024-12-05','2024-12-04',NOW(),NOW()),
(214,4,'ORD-NOV-214','2024-11-30 11:55',9995,0,1799,0,11794,'Net Banking','Paid','Delivered',4,'2024-12-05','2024-12-04',NOW(),NOW()),
(215,5,'ORD-NOV-215','2024-11-30 16:10',2999,300,486,40,3225,'UPI','Paid','Delivered',5,'2024-12-05','2024-12-04',NOW(),NOW()),

-- DECEMBER 2024 (25 orders up to Dec 15)
(216,6,'ORD-DEC-216','2024-12-01 10:00',2199,0,396,40,2635,'Wallet','Paid','Delivered',6,'2024-12-06','2024-12-05',NOW(),NOW()),
(217,7,'ORD-DEC-217','2024-12-02 14:30',51999,5200,8424,0,55223,'COD','Paid','Delivered',7,'2024-12-07','2024-12-06',NOW(),NOW()),
(218,8,'ORD-DEC-218','2024-12-03 09:45',299,0,54,40,393,'Credit Card','Paid','Delivered',8,'2024-12-08','2024-12-07',NOW(),NOW()),
(219,9,'ORD-DEC-219','2024-12-04 13:20',72999,0,13140,0,86139,'Net Banking','Paid','Delivered',9,'2024-12-09','2024-12-08',NOW(),NOW()),
(220,10,'ORD-DEC-220','2024-12-05 11:00',3999,0,720,40,4759,'UPI','Paid','Delivered',10,'2024-12-10','2024-12-09',NOW(),NOW()),
(221,11,'ORD-DEC-221','2024-12-06 15:35',149999,0,27000,0,176999,'Wallet','Paid','Delivered',11,'2024-12-11','2024-12-10',NOW(),NOW()),
(222,12,'ORD-DEC-222','2024-12-07 10:25',1499,0,270,40,1809,'COD','Paid','Delivered',12,'2024-12-12','2024-12-11',NOW(),NOW()),
(223,13,'ORD-DEC-223','2024-12-08 14:50',54999,0,9900,0,64899,'Credit Card','Paid','Delivered',13,'2024-12-13','2024-12-12',NOW(),NOW()),
(224,14,'ORD-DEC-224','2024-12-09 09:10',2799,0,504,40,3343,'Net Banking','Paid','Delivered',14,'2024-12-14','2024-12-13',NOW(),NOW()),
(225,15,'ORD-DEC-225','2024-12-10 16:20',995,0,179,40,1214,'UPI','Paid','Delivered',15,'2024-12-15','2024-12-14',NOW(),NOW()),
(226,1,'ORD-DEC-226','2024-12-11 11:40',24990,0,4498,0,29488,'Wallet','Paid','Shipped',1,'2024-12-17','2024-12-17',NOW(),NOW()),
(227,2,'ORD-DEC-227','2024-12-12 15:05',1799,0,324,40,2163,'COD','Paid','Shipped',2,'2024-12-18','2024-12-18',NOW(),NOW()),
(228,3,'ORD-DEC-228','2024-12-13 10:30',379,0,68,40,487,'Credit Card','Paid','Shipped',3,'2024-12-19',NULL,NOW(),NOW()),
(229,4,'ORD-DEC-229','2024-12-14 14:45',119900,0,21582,0,141482,'Net Banking','Paid','Confirmed',4,'2024-12-20',NULL,NOW(),NOW()),
(230,5,'ORD-DEC-230','2024-12-15 09:55',2299,0,414,40,2753,'UPI','Paid','Confirmed',5,'2024-12-21',NULL,NOW(),NOW()),
(231,6,'ORD-DEC-231','2024-12-15 13:20',69999,0,12600,0,82599,'Wallet','Paid','Placed',6,'2024-12-21',NULL,NOW(),NOW()),
(232,7,'ORD-DEC-232','2024-12-15 11:35',4495,0,809,40,5344,'COD','Pending','Placed',7,'2024-12-21',NULL,NOW(),NOW()),
(233,8,'ORD-DEC-233','2024-12-15 15:50',999,0,180,40,1219,'Credit Card','Paid','Placed',8,'2024-12-21',NULL,NOW(),NOW()),
(234,9,'ORD-DEC-234','2024-12-15 10:20',1499,0,270,40,1809,'Net Banking','Paid','Placed',9,'2024-12-21',NULL,NOW(),NOW()),
(235,10,'ORD-DEC-235','2024-12-15 14:35',10999,0,1980,40,13019,'UPI','Paid','Placed',10,'2024-12-21',NULL,NOW(),NOW()),
(236,11,'ORD-DEC-236','2024-12-15 09:00',2795,0,503,40,3338,'Wallet','Paid','Placed',11,'2024-12-21',NULL,NOW(),NOW()),
(237,12,'ORD-DEC-237','2024-12-15 13:25',32995,0,5939,0,38934,'COD','Pending','Placed',12,'2024-12-21',NULL,NOW(),NOW()),
(238,13,'ORD-DEC-238','2024-12-15 11:50',47990,0,8638,0,56628,'Credit Card','Paid','Placed',13,'2024-12-21',NULL,NOW(),NOW()),
(239,14,'ORD-DEC-239','2024-12-15 16:05',2495,0,449,40,2984,'Net Banking','Paid','Placed',14,'2024-12-21',NULL,NOW(),NOW()),
(240,15,'ORD-DEC-240','2024-12-15 10:30',549,0,99,40,688,'UPI','Paid','Placed',15,'2024-12-21',NULL,NOW(),NOW());

-- ==========================================
-- ORDER ITEMS (Each order contains 1-3 products)
-- ==========================================

INSERT INTO order_items (order_item_id, order_id, product_id, seller_id, quantity, unit_price, total_price, discount_applied, item_status, tracking_number) VALUES
-- July Orders Items
(1,1,1,1,1,69999.00,69999.00,0.00,'Delivered','TRK-JUL-001-1'),
(2,2,13,2,1,3499.00,3499.00,50.00,'Delivered','TRK-JUL-002-1'),
(3,3,5,1,1,149999.00,149999.00,0.00,'Delivered','TRK-JUL-003-1'),
(4,4,9,2,1,2999.00,2999.00,299.90,'Delivered','TRK-JUL-004-1'),
(5,5,10,2,1,9995.00,9995.00,0.00,'Delivered','TRK-JUL-005-1'),
(6,6,15,2,1,2199.00,2199.00,0.00,'Delivered','TRK-JUL-006-1'),
(7,7,34,1,1,24990.00,24990.00,2499.90,'Delivered','TRK-JUL-007-1'),
(8,8,23,4,1,299.00,299.00,0.00,'Delivered','TRK-JUL-008-1'),
(9,9,3,1,1,51999.00,51999.00,0.00,'Delivered','TRK-JUL-009-1'),
(10,10,19,3,1,3999.00,3999.00,0.00,'Delivered','TRK-JUL-010-1'),
(11,11,24,4,1,449.00,449.00,0.00,'Delivered','TRK-JUL-011-1'),
(12,12,7,1,1,54999.00,54999.00,0.00,'Delivered','TRK-JUL-012-1'),
(13,13,14,2,1,2799.00,2799.00,0.00,'Delivered','TRK-JUL-013-1'),
(14,14,29,5,1,999.00,999.00,0.00,'Delivered','TRK-JUL-014-1'),
(15,15,28,5,1,1999.00,1999.00,0.00,'Delivered','TRK-JUL-015-1'),
(16,16,36,1,1,32995.00,32995.00,0.00,'Delivered','TRK-JUL-016-1'),
(17,17,17,3,1,9995.00,9995.00,0.00,'Delivered','TRK-JUL-017-1'),
(18,18,20,3,1,2495.00,2495.00,0.00,'Delivered','TRK-JUL-018-1'),
(19,19,22,3,1,549.00,549.00,0.00,'Delivered','TRK-JUL-019-1'),
(20,20,2,1,1,119900.00,119900.00,0.00,'Delivered','TRK-JUL-020-1'),
(21,21,23,4,1,299.00,299.00,50.00,'Delivered','TRK-JUL-021-1'),
(22,22,19,3,1,3999.00,3999.00,0.00,'Delivered','TRK-JUL-022-1'),
(23,23,34,1,1,24990.00,24990.00,0.00,'Delivered','TRK-JUL-023-1'),
(24,24,38,2,1,1499.00,1499.00,0.00,'Delivered','TRK-JUL-024-1'),
(25,25,4,1,1,72999.00,72999.00,7299.90,'Delivered','TRK-JUL-025-1'),
(26,26,21,3,1,995.00,995.00,0.00,'Delivered','TRK-JUL-026-1'),
(27,27,9,2,1,2999.00,2999.00,0.00,'Delivered','TRK-JUL-027-1'),
(28,28,35,1,1,47990.00,47990.00,0.00,'Delivered','TRK-JUL-028-1'),
(29,29,12,2,1,1799.00,1799.00,0.00,'Delivered','TRK-JUL-029-1'),
(30,30,25,4,1,349.00,349.00,0.00,'Delivered','TRK-JUL-030-1'),
(31,31,8,1,1,159999.00,159999.00,0.00,'Delivered','TRK-JUL-031-1'),
(32,32,31,5,1,2299.00,2299.00,0.00,'Delivered','TRK-JUL-032-1'),
(33,33,6,1,1,189900.00,189900.00,0.00,'Delivered','TRK-JUL-033-1'),
(34,34,37,2,1,4495.00,4495.00,0.00,'Delivered','TRK-JUL-034-1'),
(35,35,27,4,1,379.00,379.00,0.00,'Delivered','TRK-JUL-035-1'),
(36,36,29,5,1,999.00,999.00,0.00,'Delivered','TRK-JUL-036-1'),
(37,37,38,2,1,1499.00,1499.00,0.00,'Delivered','TRK-JUL-037-1'),
(38,38,39,3,1,10999.00,10999.00,0.00,'Delivered','TRK-JUL-038-1'),
(39,39,18,3,1,2795.00,2795.00,0.00,'Delivered','TRK-JUL-039-1'),
(40,40,23,4,1,299.00,299.00,0.00,'Delivered','TRK-JUL-040-1'),

-- August Orders Items
(41,41,1,1,1,69999.00,69999.00,0.00,'Delivered','TRK-AUG-041-1'),
(42,42,13,2,1,3499.00,3499.00,0.00,'Delivered','TRK-AUG-042-1'),
(43,43,34,1,1,24999.00,24999.00,0.00,'Delivered','TRK-AUG-043-1'),
(44,44,9,2,1,2999.00,2999.00,50.00,'Delivered','TRK-AUG-044-1'),
(45,45,40,3,1,1895.00,1895.00,0.00,'Delivered','TRK-AUG-045-1'),
(46,46,24,4,1,449.00,449.00,0.00,'Delivered','TRK-AUG-046-1'),
(47,47,2,1,1,119900.00,119900.00,0.00,'Delivered','TRK-AUG-047-1'),
(48,48,9,2,1,2999.00,2999.00,299.90,'Delivered','TRK-AUG-048-1'),
(49,49,10,2,1,9995.00,9995.00,0.00,'Delivered','TRK-AUG-049-1'),
(50,50,15,2,1,2199.00,2199.00,0.00,'Delivered','TRK-AUG-050-1'),
(51,51,3,1,1,51999.00,51999.00,5199.90,'Delivered','TRK-AUG-051-1'),
(52,52,23,4,1,299.00,299.00,0.00,'Delivered','TRK-AUG-052-1'),
(53,53,4,1,1,72999.00,72999.00,0.00,'Delivered','TRK-AUG-053-1'),
(54,54,19,3,1,3999.00,3999.00,0.00,'Delivered','TRK-AUG-054-1'),
(55,55,5,1,1,149999.00,149999.00,0.00,'Delivered','TRK-AUG-055-1'),
(56,56,38,2,1,1499.00,1499.00,0.00,'Delivered','TRK-AUG-056-1'),
(57,57,7,1,1,54999.00,54999.00,0.00,'Delivered','TRK-AUG-057-1'),
(58,58,14,2,1,2799.00,2799.00,0.00,'Delivered','TRK-AUG-058-1'),
(59,59,21,3,1,995.00,995.00,0.00,'Delivered','TRK-AUG-059-1'),
(60,60,34,1,1,24990.00,24990.00,0.00,'Delivered','TRK-AUG-060-1'),
(61,61,12,2,1,1799.00,1799.00,0.00,'Delivered','TRK-AUG-061-1'),
(62,62,27,4,1,379.00,379.00,0.00,'Delivered','TRK-AUG-062-1'),
(63,63,8,1,1,159999.00,159999.00,0.00,'Delivered','TRK-AUG-063-1'),
(64,64,31,5,1,2299.00,2299.00,0.00,'Delivered','TRK-AUG-064-1'),
(65,65,6,1,1,189900.00,189900.00,0.00,'Delivered','TRK-AUG-065-1'),
(66,66,37,2,1,4495.00,4495.00,0.00,'Delivered','TRK-AUG-066-1'),
(67,67,29,5,1,999.00,999.00,0.00,'Delivered','TRK-AUG-067-1'),
(68,68,38,2,1,1499.00,1499.00,0.00,'Delivered','TRK-AUG-068-1'),
(69,69,39,3,1,10999.00,10999.00,0.00,'Delivered','TRK-AUG-069-1'),
(70,70,18,3,1,2795.00,2795.00,0.00,'Delivered','TRK-AUG-070-1'),
(71,71,36,1,1,32995.00,32995.00,0.00,'Delivered','TRK-AUG-071-1'),
(72,72,35,1,1,47990.00,47990.00,0.00,'Delivered','TRK-AUG-072-1'),
(73,73,20,3,1,2495.00,2495.00,0.00,'Delivered','TRK-AUG-073-1'),
(74,74,22,3,1,549.00,549.00,0.00,'Delivered','TRK-AUG-074-1'),
(75,75,34,1,1,24999.00,24999.00,0.00,'Delivered','TRK-AUG-075-1'),
(76,76,1,1,1,69999.00,69999.00,0.00,'Delivered','TRK-AUG-076-1'),
(77,77,13,2,1,3499.00,3499.00,0.00,'Delivered','TRK-AUG-077-1'),
(78,78,10,2,1,9995.00,9995.00,0.00,'Delivered','TRK-AUG-078-1'),
(79,79,9,2,1,2999.00,2999.00,299.90,'Delivered','TRK-AUG-079-1'),
(80,80,15,2,1,2199.00,2199.00,0.00,'Delivered','TRK-AUG-080-1'),
(81,81,3,1,1,51999.00,51999.00,5199.90,'Delivered','TRK-AUG-081-1'),
(82,82,23,4,1,299.00,299.00,0.00,'Delivered','TRK-AUG-082-1'),
(83,83,4,1,1,72999.00,72999.00,0.00,'Delivered','TRK-AUG-083-1'),
(84,84,19,3,1,3999.00,3999.00,0.00,'Delivered','TRK-AUG-084-1'),
(85,85,5,1,1,149999.00,149999.00,0.00,'Delivered','TRK-AUG-085-1'),
(86,86,38,2,1,1499.00,1499.00,0.00,'Delivered','TRK-AUG-086-1'),
(87,87,7,1,1,54999.00,54999.00,0.00,'Delivered','TRK-AUG-087-1'),
(88,88,14,2,1,2799.00,2799.00,0.00,'Delivered','TRK-AUG-088-1'),
(89,89,21,3,1,995.00,995.00,0.00,'Delivered','TRK-AUG-089-1'),
(90,90,34,1,1,24990.00,24990.00,0.00,'Delivered','TRK-AUG-090-1'),

-- September Orders Items
(91,91,2,1,1,119900.00,119900.00,0.00,'Delivered','TRK-SEP-091-1'),
(92,92,13,2,1,3499.00,3499.00,50.00,'Delivered','TRK-SEP-092-1'),
(93,93,34,1,1,24999.00,24999.00,0.00,'Delivered','TRK-SEP-093-1'),
(94,94,9,2,1,2999.00,2999.00,299.90,'Delivered','TRK-SEP-094-1'),
(95,95,10,2,1,9995.00,9995.00,0.00,'Delivered','TRK-SEP-095-1'),
(96,96,15,2,1,2199.00,2199.00,0.00,'Delivered','TRK-SEP-096-1'),
(97,97,3,1,1,51999.00,51999.00,5199.90,'Delivered','TRK-SEP-097-1'),
(98,98,23,4,1,299.00,299.00,0.00,'Delivered','TRK-SEP-098-1'),
(99,99,4,1,1,72999.00,72999.00,0.00,'Delivered','TRK-SEP-099-1'),
(100,100,19,3,1,3999.00,3999.00,0.00,'Delivered','TRK-SEP-100-1'),
(101,101,5,1,1,149999.00,149999.00,0.00,'Delivered','TRK-SEP-101-1'),
(102,102,38,2,1,1499.00,1499.00,0.00,'Delivered','TRK-SEP-102-1'),
(103,103,7,1,1,54999.00,54999.00,0.00,'Delivered','TRK-SEP-103-1'),
(104,104,14,2,1,2799.00,2799.00,0.00,'Delivered','TRK-SEP-104-1'),
(105,105,21,3,1,995.00,995.00,0.00,'Delivered','TRK-SEP-105-1'),
(106,106,34,1,1,24990.00,24990.00,0.00,'Delivered','TRK-SEP-106-1'),
(107,107,12,2,1,1799.00,1799.00,0.00,'Delivered','TRK-SEP-107-1'),
(108,108,27,4,1,379.00,379.00,0.00,'Delivered','TRK-SEP-108-1'),
(109,109,8,1,1,159999.00,159999.00,0.00,'Delivered','TRK-SEP-109-1'),
(110,110,31,5,1,2299.00,2299.00,0.00,'Delivered','TRK-SEP-110-1'),
(111,111,6,1,1,189900.00,189900.00,0.00,'Delivered','TRK-SEP-111-1'),
(112,112,37,2,1,4495.00,4495.00,0.00,'Delivered','TRK-SEP-112-1'),
(113,113,29,5,1,999.00,999.00,0.00,'Delivered','TRK-SEP-113-1'),
(114,114,38,2,1,1499.00,1499.00,0.00,'Delivered','TRK-SEP-114-1'),
(115,115,39,3,1,10999.00,10999.00,0.00,'Delivered','TRK-SEP-115-1'),
(116,116,18,3,1,2795.00,2795.00,0.00,'Delivered','TRK-SEP-116-1'),
(117,117,36,1,1,32995.00,32995.00,0.00,'Delivered','TRK-SEP-117-1'),
(118,118,35,1,1,47990.00,47990.00,0.00,'Delivered','TRK-SEP-118-1'),
(119,119,20,3,1,2495.00,2495.00,0.00,'Delivered','TRK-SEP-119-1'),
(120,120,22,3,1,549.00,549.00,0.00,'Delivered','TRK-SEP-120-1'),
(121,121,34,1,1,24999.00,24999.00,0.00,'Delivered','TRK-SEP-121-1'),
(122,122,1,1,1,69999.00,69999.00,0.00,'Delivered','TRK-SEP-122-1'),
(123,123,13,2,1,3499.00,3499.00,0.00,'Delivered','TRK-SEP-123-1'),
(124,124,10,2,1,9995.00,9995.00,0.00,'Delivered','TRK-SEP-124-1'),
(125,125,9,2,1,2999.00,2999.00,299.90,'Delivered','TRK-SEP-125-1'),

(126,126,15,2,1,2199.00,2199.00,0.00,'Delivered','TRK-SEP-126-1'),
(127,127,3,1,1,51999.00,51999.00,5199.90,'Delivered','TRK-SEP-127-1'),
(128,128,23,4,1,299.00,299.00,0.00,'Delivered','TRK-SEP-128-1'),
(129,129,4,1,1,72999.00,72999.00,0.00,'Delivered','TRK-SEP-129-1'),
(130,130,19,3,1,3999.00,3999.00,0.00,'Delivered','TRK-SEP-130-1'),

-- October Orders Items (Festive Season - Higher volume)
(131,131,5,1,1,149999.00,149999.00,0.00,'Delivered','TRK-OCT-131-1'),
(132,132,38,2,1,1499.00,1499.00,0.00,'Delivered','TRK-OCT-132-1'),
(133,133,7,1,1,54999.00,54999.00,0.00,'Delivered','TRK-OCT-133-1'),
(134,134,14,2,1,2799.00,2799.00,0.00,'Delivered','TRK-OCT-134-1'),
(135,135,21,3,1,995.00,995.00,0.00,'Delivered','TRK-OCT-135-1'),
(136,136,34,1,1,24990.00,24990.00,0.00,'Delivered','TRK-OCT-136-1'),
(137,137,12,2,1,1799.00,1799.00,0.00,'Delivered','TRK-OCT-137-1'),
(138,138,27,4,1,379.00,379.00,0.00,'Delivered','TRK-OCT-138-1'),
(139,139,8,1,1,159999.00,159999.00,0.00,'Delivered','TRK-OCT-139-1'),
(140,140,31,5,1,2299.00,2299.00,0.00,'Delivered','TRK-OCT-140-1'),
(141,141,6,1,1,189900.00,189900.00,0.00,'Delivered','TRK-OCT-141-1'),
(142,142,37,2,1,4495.00,4495.00,0.00,'Delivered','TRK-OCT-142-1'),
(143,143,29,5,1,999.00,999.00,0.00,'Delivered','TRK-OCT-143-1'),
(144,144,38,2,1,1499.00,1499.00,0.00,'Delivered','TRK-OCT-144-1'),
(145,145,39,3,1,10999.00,10999.00,0.00,'Delivered','TRK-OCT-145-1'),
(146,146,18,3,1,2795.00,2795.00,0.00,'Delivered','TRK-OCT-146-1'),
(147,147,36,1,1,32995.00,32995.00,0.00,'Delivered','TRK-OCT-147-1'),
(148,148,35,1,1,47990.00,47990.00,0.00,'Delivered','TRK-OCT-148-1'),
(149,149,20,3,1,2495.00,2495.00,0.00,'Delivered','TRK-OCT-149-1'),
(150,150,22,3,1,549.00,549.00,0.00,'Delivered','TRK-OCT-150-1'),
(151,151,34,1,1,24999.00,24999.00,0.00,'Delivered','TRK-OCT-151-1'),
(152,152,1,1,1,69999.00,69999.00,0.00,'Delivered','TRK-OCT-152-1'),
(153,153,13,2,1,3499.00,3499.00,0.00,'Delivered','TRK-OCT-153-1'),
(154,154,10,2,1,9995.00,9995.00,0.00,'Delivered','TRK-OCT-154-1'),
(155,155,9,2,1,2999.00,2999.00,299.90,'Delivered','TRK-OCT-155-1'),
(156,156,15,2,1,2199.00,2199.00,0.00,'Delivered','TRK-OCT-156-1'),
(157,157,3,1,1,51999.00,51999.00,5199.90,'Delivered','TRK-OCT-157-1'),
(158,158,23,4,1,299.00,299.00,0.00,'Delivered','TRK-OCT-158-1'),
(159,159,4,1,1,72999.00,72999.00,0.00,'Delivered','TRK-OCT-159-1'),
(160,160,19,3,1,3999.00,3999.00,0.00,'Delivered','TRK-OCT-160-1'),
(161,161,5,1,1,149999.00,149999.00,0.00,'Delivered','TRK-OCT-161-1'),
(162,162,38,2,1,1499.00,1499.00,0.00,'Delivered','TRK-OCT-162-1'),
(163,163,7,1,1,54999.00,54999.00,0.00,'Delivered','TRK-OCT-163-1'),
(164,164,14,2,1,2799.00,2799.00,0.00,'Delivered','TRK-OCT-164-1'),
(165,165,21,3,1,995.00,995.00,0.00,'Delivered','TRK-OCT-165-1'),
(166,166,34,1,1,24990.00,24990.00,0.00,'Delivered','TRK-OCT-166-1'),
(167,167,12,2,1,1799.00,1799.00,0.00,'Delivered','TRK-OCT-167-1'),
(168,168,27,4,1,379.00,379.00,0.00,'Delivered','TRK-OCT-168-1'),
(169,169,8,1,1,159999.00,159999.00,0.00,'Delivered','TRK-OCT-169-1'),
(170,170,31,5,1,2299.00,2299.00,0.00,'Delivered','TRK-OCT-170-1'),
(171,171,6,1,1,189900.00,189900.00,0.00,'Delivered','TRK-OCT-171-1'),
(172,172,37,2,1,4495.00,4495.00,0.00,'Delivered','TRK-OCT-172-1'),
(173,173,29,5,1,999.00,999.00,0.00,'Delivered','TRK-OCT-173-1'),
(174,174,38,2,1,1499.00,1499.00,0.00,'Delivered','TRK-OCT-174-1'),
(175,175,39,3,1,10999.00,10999.00,0.00,'Delivered','TRK-OCT-175-1'),
(176,176,18,3,1,2795.00,2795.00,0.00,'Delivered','TRK-OCT-176-1'),
(177,177,36,1,1,32995.00,32995.00,0.00,'Delivered','TRK-OCT-177-1'),
(178,178,35,1,1,47990.00,47990.00,0.00,'Delivered','TRK-OCT-178-1'),
(179,179,20,3,1,2495.00,2495.00,0.00,'Delivered','TRK-OCT-179-1'),
(180,180,22,3,1,549.00,549.00,0.00,'Delivered','TRK-OCT-180-1'),
(181,181,34,1,1,24999.00,24999.00,0.00,'Delivered','TRK-OCT-181-1'),
(182,182,1,1,1,69999.00,69999.00,0.00,'Delivered','TRK-OCT-182-1'),
(183,183,13,2,1,3499.00,3499.00,0.00,'Delivered','TRK-OCT-183-1'),
(184,184,10,2,1,9995.00,9995.00,0.00,'Delivered','TRK-OCT-184-1'),
(185,185,9,2,1,2999.00,2999.00,299.90,'Delivered','TRK-OCT-185-1'),

-- November Orders Items
(186,186,15,2,1,2199.00,2199.00,0.00,'Delivered','TRK-NOV-186-1'),
(187,187,3,1,1,51999.00,51999.00,5199.90,'Delivered','TRK-NOV-187-1'),
(188,188,23,4,1,299.00,299.00,0.00,'Delivered','TRK-NOV-188-1'),
(189,189,4,1,1,72999.00,72999.00,0.00,'Delivered','TRK-NOV-189-1'),
(190,190,19,3,1,3999.00,3999.00,0.00,'Delivered','TRK-NOV-190-1'),
(191,191,5,1,1,149999.00,149999.00,0.00,'Delivered','TRK-NOV-191-1'),
(192,192,38,2,1,1499.00,1499.00,0.00,'Delivered','TRK-NOV-192-1'),
(193,193,7,1,1,54999.00,54999.00,0.00,'Delivered','TRK-NOV-193-1'),
(194,194,14,2,1,2799.00,2799.00,0.00,'Delivered','TRK-NOV-194-1'),
(195,195,21,3,1,995.00,995.00,0.00,'Delivered','TRK-NOV-195-1'),
(196,196,34,1,1,24990.00,24990.00,0.00,'Delivered','TRK-NOV-196-1'),
(197,197,12,2,1,1799.00,1799.00,0.00,'Delivered','TRK-NOV-197-1'),
(198,198,27,4,1,379.00,379.00,0.00,'Delivered','TRK-NOV-198-1'),
(199,199,2,1,1,119900.00,119900.00,0.00,'Delivered','TRK-NOV-199-1'),
(200,200,31,5,1,2299.00,2299.00,0.00,'Delivered','TRK-NOV-200-1'),
(201,201,1,1,1,69999.00,69999.00,0.00,'Delivered','TRK-NOV-201-1'),
(202,202,37,2,1,4495.00,4495.00,0.00,'Delivered','TRK-NOV-202-1'),
(203,203,29,5,1,999.00,999.00,0.00,'Delivered','TRK-NOV-203-1'),
(204,204,38,2,1,1499.00,1499.00,0.00,'Delivered','TRK-NOV-204-1'),
(205,205,39,3,1,10999.00,10999.00,0.00,'Delivered','TRK-NOV-205-1'),
(206,206,18,3,1,2795.00,2795.00,0.00,'Delivered','TRK-NOV-206-1'),
(207,207,36,1,1,32995.00,32995.00,0.00,'Delivered','TRK-NOV-207-1'),
(208,208,35,1,1,47990.00,47990.00,0.00,'Delivered','TRK-NOV-208-1'),
(209,209,20,3,1,2495.00,2495.00,0.00,'Delivered','TRK-NOV-209-1'),
(210,210,22,3,1,549.00,549.00,0.00,'Delivered','TRK-NOV-210-1'),
(211,211,34,1,1,24999.00,24999.00,0.00,'Delivered','TRK-NOV-211-1'),
(212,212,1,1,1,69999.00,69999.00,0.00,'Delivered','TRK-NOV-212-1'),
(213,213,13,2,1,3499.00,3499.00,0.00,'Delivered','TRK-NOV-213-1'),
(214,214,10,2,1,9995.00,9995.00,0.00,'Delivered','TRK-NOV-214-1'),
(215,215,9,2,1,2999.00,2999.00,299.90,'Delivered','TRK-NOV-215-1'),

-- December Orders Items
(216,216,15,2,1,2199.00,2199.00,0.00,'Delivered','TRK-DEC-216-1'),
(217,217,3,1,1,51999.00,51999.00,5199.90,'Delivered','TRK-DEC-217-1'),
(218,218,23,4,1,299.00,299.00,0.00,'Delivered','TRK-DEC-218-1'),
(219,219,4,1,1,72999.00,72999.00,0.00,'Delivered','TRK-DEC-219-1'),
(220,220,19,3,1,3999.00,3999.00,0.00,'Delivered','TRK-DEC-220-1'),
(221,221,5,1,1,149999.00,149999.00,0.00,'Delivered','TRK-DEC-221-1'),
(222,222,38,2,1,1499.00,1499.00,0.00,'Delivered','TRK-DEC-222-1'),
(223,223,7,1,1,54999.00,54999.00,0.00,'Delivered','TRK-DEC-223-1'),
(224,224,14,2,1,2799.00,2799.00,0.00,'Delivered','TRK-DEC-224-1'),
(225,225,21,3,1,995.00,995.00,0.00,'Delivered','TRK-DEC-225-1'),
(226,226,34,1,1,24990.00,24990.00,0.00,'Shipped','TRK-DEC-226-1'),
(227,227,12,2,1,1799.00,1799.00,0.00,'Shipped','TRK-DEC-227-1'),
(228,228,27,4,1,379.00,379.00,0.00,'Shipped','TRK-DEC-228-1'),
(229,229,2,1,1,119900.00,119900.00,0.00,'Confirmed','TRK-DEC-229-1'),
(230,230,31,5,1,2299.00,2299.00,0.00,'Confirmed','TRK-DEC-230-1'),
(231,231,1,1,1,69999.00,69999.00,0.00,'Placed',NULL),
(232,232,37,2,1,4495.00,4495.00,0.00,'Placed',NULL),
(233,233,29,5,1,999.00,999.00,0.00,'Placed',NULL),
(234,234,38,2,1,1499.00,1499.00,0.00,'Placed',NULL),
(235,235,39,3,1,10999.00,10999.00,0.00,'Placed',NULL),
(236,236,18,3,1,2795.00,2795.00,0.00,'Placed',NULL),
(237,237,36,1,1,32995.00,32995.00,0.00,'Placed',NULL),
(238,238,35,1,1,47990.00,47990.00,0.00,'Placed',NULL),
(239,239,20,3,1,2495.00,2495.00,0.00,'Placed',NULL),
(240,240,22,3,1,549.00,549.00,0.00,'Placed',NULL);

-- ==========================================
-- REVIEWS (Sample reviews for various products)
-- ==========================================
INSERT INTO reviews (review_id, user_id, product_id, order_id, rating, review_title, review_text, is_verified_purchase, helpful_votes, is_active) VALUES
(1,1,1,1,5,'Excellent Phone!','Great camera quality and battery life. Highly recommended!',1,45,1),
(2,2,13,2,4,'Good dress','Nice fabric and fit. Color is slightly different from image.',1,23,1),
(3,3,5,3,5,'Best laptop','Amazing performance for work and gaming. Worth every penny!',1,67,1),
(4,5,10,5,5,'Love these shoes','Very comfortable for running. Great cushioning!',1,34,1),
(5,7,34,7,4,'Good headphones','Sound quality is good but a bit pricey.',1,12,1),
(6,9,3,9,5,'Fantastic value','Best phone in this price range. Fast and smooth!',1,56,1),
(7,12,7,12,4,'Good laptop','Nice for daily use but gets a bit hot during heavy tasks.',1,28,1),
(8,14,36,16,5,'Great camera','Perfect for beginners. Easy to use with good image quality.',1,41,1),
(9,16,20,18,3,'Average cooker','Does the job but whistle is too loud.',1,8,1),
(10,18,2,20,5,'Premium phone','Expensive but worth it. Camera is incredible!',1,89,1),
(11,22,34,23,4,'Nice headphones','Comfort is good, noise cancellation works well.',1,19,1),
(12,1,34,106,5,'Amazing sound','Best headphones I have ever used!',1,52,1),
(13,4,2,199,5,'Best iPhone','Camera and performance are outstanding!',1,73,1),
(14,6,1,201,4,'Good phone','Value for money. Battery life could be better.',1,31,1),
(15,10,5,55,5,'Excellent laptop','Fast and reliable. Great for programming.',1,48,1);

-- ==========================================
-- CART (Current cart items for active users)
-- ==========================================
INSERT INTO cart (cart_id, user_id, product_id, quantity, added_at) VALUES
(1,1,11,2,NOW()),
(2,1,23,1,NOW()),
(3,2,17,1,NOW()),
(4,3,30,1,NOW()),
(5,4,16,2,NOW()),
(6,5,24,1,NOW()),
(7,6,33,1,NOW()),
(8,7,25,3,NOW()),
(9,8,40,1,NOW()),
(10,9,26,2,NOW()),
(11,10,32,1,NOW()),
(12,11,28,1,NOW()),
(13,12,11,1,NOW()),
(14,13,37,1,NOW()),
(15,14,22,2,NOW()),
(16,15,27,1,NOW());

-- ==========================================
-- WISHLIST
-- ==========================================
INSERT INTO wishlist (wishlist_id, user_id, product_id, added_at) VALUES
(1,1,2,NOW()),
(2,1,6,NOW()),
(3,2,5,NOW()),
(4,2,8,NOW()),
(5,3,2,NOW()),
(6,4,35,NOW()),
(7,5,6,NOW()),
(8,5,36,NOW()),
(9,6,33,NOW()),
(10,7,30,NOW()),
(11,8,17,NOW()),
(12,9,19,NOW()),
(13,10,5,NOW()),
(14,11,34,NOW()),
(15,12,1,NOW()),
(16,13,7,NOW()),
(17,14,4,NOW()),
(18,15,8,NOW());

-- ==========================================
-- PAYMENTS (Payment records for orders)
-- ==========================================
INSERT INTO payments (payment_id, order_id, payment_method, transaction_id, payment_gateway, amount, currency, payment_status, payment_date, gateway_response) VALUES
(1,1,'UPI','TXN-JUL-001-UPI','Razorpay',82599.00,'INR','Success','2024-07-01 10:35:00','Payment successful'),
(2,2,'Credit Card','TXN-JUL-002-CC','Stripe',4110.00,'INR','Success','2024-07-02 14:25:00','Payment successful'),
(3,3,'Net Banking','TXN-JUL-003-NB','PayU',176999.00,'INR','Success','2024-07-03 09:20:00','Payment successful'),
(4,20,'Net Banking','TXN-JUL-020-NB','PayU',141482.00,'INR','Success','2024-07-22 10:35:00','Payment successful'),
(5,42,'Credit Card','TXN-AUG-042-CC','Stripe',141482.00,'INR','Success','2024-08-05 10:30:00','Payment successful'),
(6,55,'Credit Card','TXN-AUG-055-CC','Stripe',176999.00,'INR','Success','2024-08-13 10:00:00','Payment successful'),
(7,91,'UPI','TXN-SEP-091-UPI','Razorpay',141482.00,'INR','Success','2024-09-02 10:20:00','Payment successful'),
(8,131,'Wallet','TXN-OCT-131-WL','Paytm',176999.00,'INR','Success','2024-10-01 10:05:00','Payment successful'),
(9,191,'Wallet','TXN-NOV-191-WL','Paytm',176999.00,'INR','Success','2024-11-06 15:40:00','Payment successful'),
(10,221,'Wallet','TXN-DEC-221-WL','Paytm',176999.00,'INR','Success','2024-12-06 15:40:00','Payment successful');

-- ==========================================
-- USER COUPONS (Coupon usage tracking)
-- ==========================================
INSERT INTO user_coupons (user_coupon_id, user_id, coupon_id, order_id, used_at, discount_applied) VALUES
(1,2,1,2,'2024-07-02 14:20:00',50.00),
(2,4,2,4,'2024-07-05 16:45:00',299.90),
(3,7,3,7,'2024-07-09 10:00:00',2499.90),
(4,10,2,25,'2024-07-27 11:30:00',7299.90),
(5,9,2,44,'2024-08-02 13:20:00',50.00),
(6,1,3,46,'2024-08-09 11:40:00',5199.90),
(7,6,3,51,'2024-08-09 11:40:00',5199.90),
(8,2,1,92,'2024-09-03 14:30:00',50.00),
(9,4,2,94,'2024-09-05 13:20:00',299.90),
(10,7,3,97,'2024-09-08 10:25:00',5199.90),
(11,9,2,155,'2024-10-20 10:30:00',299.90),
(12,7,3,157,'2024-10-22 09:15:00',5199.90),
(13,5,2,215,'2024-11-30 16:10:00',299.90),
(14,7,3,187,'2024-11-02 14:30:00',5199.90),
(15,7,3,217,'2024-12-02 14:30:00',5199.90);

-- ==========================================
-- ANALYSIS QUERIES (Useful for testing the data)
-- ==========================================

-- Month-wise sales summary
-- SELECT 
--     DATE_FORMAT(order_date, '%Y-%m') as month,
--     COUNT(*) as total_orders,
--     SUM(final_amount) as total_revenue,
--     AVG(final_amount) as avg_order_value
-- FROM orders
-- GROUP BY month
-- ORDER BY month;

-- Seller-wise performance
-- SELECT 
--     s.seller_name,
--     COUNT(DISTINCT o.order_id) as total_orders,
--     SUM(oi.total_price) as total_sales,
--     AVG(oi.total_price) as avg_sale
-- FROM sellers s
-- JOIN order_items oi ON s.seller_id = oi.seller_id
-- JOIN orders o ON oi.order_id = o.order_id
-- WHERE o.order_status = 'Delivered'
-- GROUP BY s.seller_id, s.seller_name
-- ORDER BY total_sales DESC;

-- Top selling products
-- SELECT 
--     p.product_name,
--     p.brand,
--     COUNT(oi.order_item_id) as times_ordered,
--     SUM(oi.quantity) as total_quantity,
--     SUM(oi.total_price) as total_revenue
-- FROM products p
-- JOIN order_items oi ON p.product_id = oi.product_id
-- JOIN orders o ON oi.order_id = o.order_id
-- WHERE o.order_status = 'Delivered'
-- GROUP BY p.product_id, p.product_name, p.brand
-- ORDER BY total_revenue DESC
-- LIMIT 10;

-- Category-wise analysis
-- SELECT 
--     c.category_name,
--     COUNT(DISTINCT oi.order_id) as orders,
--     SUM(oi.total_price) as revenue,
--     SUM(oi.quantity) as units_sold
-- FROM categories c
-- JOIN products p ON c.category_id = p.category_id
-- JOIN order_items oi ON p.product_id = oi.product_id
-- JOIN orders o ON oi.order_id = o.order_id
-- WHERE o.order_status = 'Delivered'
-- GROUP BY c.category_id, c.category_name
-- ORDER BY revenue DESC;

-- Week-wise order trends
-- SELECT 
--     YEARWEEK(order_date) as week,
--     COUNT(*) as orders,
--     SUM(final_amount) as revenue
-- FROM orders
-- WHERE order_status = 'Delivered'
-- GROUP BY week
-- ORDER BY week;

-- Payment method distribution
-- SELECT 
--     payment_method,
--     COUNT(*) as order_count,
--     SUM(final_amount) as total_amount,
--     ROUND(AVG(final_amount), 2) as avg_amount
-- FROM orders
-- WHERE payment_status = 'Paid'
-- GROUP BY payment_method
-- ORDER BY order_count DESC;

-- ==========================================
-- DATA SUMMARY
-- ==========================================
-- Total Users: 30
-- Total Sellers: 5
-- Total Products: 40
-- Total Categories: 10
-- Total Orders: 240 (July-December 2024)
-- Total Coupons: 3
-- Order Statuses: Mix of Delivered, Shipped, Confirmed, Placed
-- Payment Methods: UPI, Credit Card, COD, Net Banking, Wallet
-- ==========================================