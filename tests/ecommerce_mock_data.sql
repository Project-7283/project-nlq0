-- E-commerce Mock Data Generator
-- This generates data for 6 months with realistic patterns for analysis

-- Clear existing data (optional - uncomment if needed)
-- SET FOREIGN_KEY_CHECKS = 0;
-- TRUNCATE TABLE user_coupons;
-- TRUNCATE TABLE payments;
-- TRUNCATE TABLE order_items;
-- TRUNCATE TABLE orders;
-- TRUNCATE TABLE reviews;
-- TRUNCATE TABLE cart;
-- TRUNCATE TABLE wishlist;
-- TRUNCATE TABLE product_attributes;
-- TRUNCATE TABLE product_images;
-- TRUNCATE TABLE products;
-- TRUNCATE TABLE addresses;
-- TRUNCATE TABLE users;
-- TRUNCATE TABLE sellers;
-- TRUNCATE TABLE coupons;
-- TRUNCATE TABLE categories;
-- SET FOREIGN_KEY_CHECKS = 1;

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
