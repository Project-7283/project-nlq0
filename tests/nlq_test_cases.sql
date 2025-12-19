-- ==========================================
-- NLQ TO SQL TEST CASES - 100 QUESTIONS
-- Categories: Basic, Intermediate, Advanced, Complex
-- Use for confusion matrix evaluation
-- ==========================================

-- ====================
-- CATEGORY 1: BASIC QUERIES (Questions 1-25)
-- Simple SELECT, WHERE, COUNT, SUM
-- ====================

-- Q1: How many total users are there?
SELECT COUNT(*) as total_users FROM users;

-- Q2: What is the total number of products?
SELECT COUNT(*) as total_products FROM products;

-- Q3: List all active sellers
SELECT seller_name, email, city FROM sellers WHERE is_active = 1;

-- Q4: Show all categories
SELECT category_name, description FROM categories WHERE parent_category_id IS NULL;

-- Q5: How many orders were placed?
SELECT COUNT(*) as total_orders FROM orders;

-- Q6: What is the total revenue?
SELECT SUM(final_amount) as total_revenue FROM orders WHERE payment_status = 'Paid';

-- Q7: List all products from Samsung
SELECT product_name, selling_price FROM products WHERE brand = 'Samsung';

-- Q8: Show all electronics products
SELECT p.product_name, p.selling_price 
FROM products p 
JOIN categories c ON p.category_id = c.category_id 
WHERE c.category_name = 'Electronics';

-- Q9: How many users are female?
SELECT COUNT(*) as female_users FROM users WHERE gender = 'Female';

-- Q10: List all products under 1000 rupees
SELECT product_name, selling_price FROM products WHERE selling_price < 1000 ORDER BY selling_price;

-- Q11: Show products with discount greater than 20%
SELECT product_name, original_price, selling_price, discount_percentage 
FROM products 
WHERE discount_percentage > 20;

-- Q12: How many orders are delivered?
SELECT COUNT(*) as delivered_orders FROM orders WHERE order_status = 'Delivered';

-- Q13: List all users from Delhi
SELECT first_name, last_name, email FROM users u 
JOIN addresses a ON u.user_id = a.user_id 
WHERE a.state = 'Delhi';

-- Q14: Show all coupons
SELECT coupon_code, coupon_name, discount_value FROM coupons WHERE is_active = 1;

-- Q15: How many products are featured?
SELECT COUNT(*) as featured_products FROM products WHERE is_featured = 1;

-- Q16: List all books
SELECT product_name, selling_price FROM products WHERE category_id = 4;

-- Q17: Show all orders with COD payment
SELECT order_number, final_amount, order_date FROM orders WHERE payment_method = 'COD';

-- Q18: How many sellers are verified?
SELECT COUNT(*) as verified_sellers FROM sellers WHERE is_verified = 1;

-- Q19: List products with warranty
SELECT product_name, warranty_period FROM products WHERE warranty_period IS NOT NULL;

-- Q20: Show users who joined in 2024
SELECT first_name, last_name, email, created_at 
FROM users 
WHERE YEAR(created_at) = 2024;

-- Q21: How many products are out of stock?
SELECT COUNT(*) as out_of_stock FROM products WHERE stock_quantity = 0;

-- Q22: List all fashion products
SELECT p.product_name, p.selling_price 
FROM products p 
JOIN categories c ON p.category_id = c.category_id 
WHERE c.category_name = 'Fashion' OR c.parent_category_id = 2;

-- Q23: Show pending orders
SELECT order_number, user_id, final_amount FROM orders WHERE order_status = 'Placed';

-- Q24: How many reviews are there?
SELECT COUNT(*) as total_reviews FROM reviews WHERE is_active = 1;

-- Q25: List all cities where we deliver
SELECT DISTINCT city, state FROM addresses ORDER BY state, city;

-- ====================
-- CATEGORY 2: INTERMEDIATE QUERIES (Questions 26-50)
-- JOINs, GROUP BY, HAVING, Aggregations
-- ====================

-- Q26: What is the average order value?
SELECT ROUND(AVG(final_amount), 2) as avg_order_value 
FROM orders 
WHERE payment_status = 'Paid';

-- Q27: Show total sales by seller
SELECT s.seller_name, SUM(o.final_amount) as total_sales
FROM sellers s
JOIN products p ON s.seller_id = p.seller_id
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'Delivered'
GROUP BY s.seller_id, s.seller_name
ORDER BY total_sales DESC;

-- Q28: How many orders per month?
SELECT 
    DATE_FORMAT(order_date, '%Y-%m') as month,
    COUNT(*) as order_count
FROM orders
GROUP BY month
ORDER BY month;

-- Q29: What are the top 5 selling products?
SELECT 
    p.product_name,
    COUNT(oi.order_item_id) as times_sold,
    SUM(oi.quantity) as total_quantity
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'Delivered'
GROUP BY p.product_id, p.product_name
ORDER BY times_sold DESC
LIMIT 5;

-- Q30: Show revenue by category
SELECT 
    c.category_name,
    SUM(oi.total_price) as category_revenue
FROM categories c
JOIN products p ON c.category_id = p.category_id
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'Delivered'
GROUP BY c.category_id, c.category_name
ORDER BY category_revenue DESC;

-- Q31: How many orders per user?
SELECT 
    u.first_name,
    u.last_name,
    COUNT(o.order_id) as order_count
FROM users u
LEFT JOIN orders o ON u.user_id = o.user_id
GROUP BY u.user_id, u.first_name, u.last_name
HAVING order_count > 0
ORDER BY order_count DESC;

-- Q32: What is the average rating per product?
SELECT 
    p.product_name,
    ROUND(AVG(r.rating), 2) as avg_rating,
    COUNT(r.review_id) as review_count
FROM products p
JOIN reviews r ON p.product_id = r.product_id
WHERE r.is_active = 1
GROUP BY p.product_id, p.product_name
ORDER BY avg_rating DESC;

-- Q33: Show total discount given per month
SELECT 
    DATE_FORMAT(order_date, '%Y-%m') as month,
    SUM(discount_amount) as total_discount
FROM orders
GROUP BY month
ORDER BY month;

-- Q34: Which payment method is most used?
SELECT 
    payment_method,
    COUNT(*) as usage_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM orders), 2) as percentage
FROM orders
GROUP BY payment_method
ORDER BY usage_count DESC;

-- Q35: Show sellers with more than 10 orders
SELECT 
    s.seller_name,
    COUNT(DISTINCT o.order_id) as order_count
FROM sellers s
JOIN products p ON s.seller_id = p.seller_id
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
GROUP BY s.seller_id, s.seller_name
HAVING order_count > 10
ORDER BY order_count DESC;

-- Q36: What is the total tax collected?
SELECT SUM(tax_amount) as total_tax FROM orders WHERE payment_status = 'Paid';

-- Q37: Show products by price range
SELECT 
    CASE 
        WHEN selling_price < 1000 THEN 'Under 1000'
        WHEN selling_price BETWEEN 1000 AND 10000 THEN '1000-10000'
        WHEN selling_price BETWEEN 10000 AND 50000 THEN '10000-50000'
        ELSE 'Above 50000'
    END as price_range,
    COUNT(*) as product_count
FROM products
GROUP BY price_range
ORDER BY MIN(selling_price);

-- Q38: How many orders per state?
SELECT 
    a.state,
    COUNT(DISTINCT o.order_id) as order_count
FROM addresses a
JOIN orders o ON a.address_id = o.shipping_address_id
GROUP BY a.state
ORDER BY order_count DESC;

-- Q39: Show average delivery time
SELECT 
    ROUND(AVG(DATEDIFF(actual_delivery_date, order_date)), 2) as avg_delivery_days
FROM orders
WHERE actual_delivery_date IS NOT NULL;

-- Q40: What is revenue per seller per month?
SELECT 
    s.seller_name,
    DATE_FORMAT(o.order_date, '%Y-%m') as month,
    SUM(oi.total_price) as monthly_revenue
FROM sellers s
JOIN products p ON s.seller_id = p.seller_id
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'Delivered'
GROUP BY s.seller_id, s.seller_name, month
ORDER BY s.seller_name, month;

-- Q41: Which brands are most popular?
SELECT 
    brand,
    COUNT(DISTINCT p.product_id) as product_count,
    SUM(oi.quantity) as units_sold
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'Delivered'
GROUP BY brand
ORDER BY units_sold DESC;

-- Q42: Show coupon usage statistics
SELECT 
    c.coupon_code,
    c.used_count,
    SUM(uc.discount_applied) as total_discount_given
FROM coupons c
LEFT JOIN user_coupons uc ON c.coupon_id = uc.coupon_id
GROUP BY c.coupon_id, c.coupon_code, c.used_count
ORDER BY total_discount_given DESC;

-- Q43: How many users per city?
SELECT 
    a.city,
    a.state,
    COUNT(DISTINCT a.user_id) as user_count
FROM addresses a
GROUP BY a.city, a.state
ORDER BY user_count DESC;

-- Q44: What is the order cancellation rate?
SELECT 
    COUNT(CASE WHEN order_status = 'Cancelled' THEN 1 END) as cancelled_orders,
    COUNT(*) as total_orders,
    ROUND(COUNT(CASE WHEN order_status = 'Cancelled' THEN 1 END) * 100.0 / COUNT(*), 2) as cancellation_rate
FROM orders;

-- Q45: Show products with low stock
SELECT 
    product_name,
    stock_quantity,
    seller_id
FROM products
WHERE stock_quantity < 50 AND is_active = 1
ORDER BY stock_quantity;

-- Q46: What is the gender distribution of buyers?
SELECT 
    u.gender,
    COUNT(DISTINCT o.order_id) as order_count
FROM users u
JOIN orders o ON u.user_id = o.user_id
GROUP BY u.gender;

-- Q47: Show weekly order trends
SELECT 
    YEARWEEK(order_date) as week,
    COUNT(*) as orders,
    SUM(final_amount) as revenue
FROM orders
WHERE order_status = 'Delivered'
GROUP BY week
ORDER BY week;

-- Q48: Which products have the most reviews?
SELECT 
    p.product_name,
    COUNT(r.review_id) as review_count,
    ROUND(AVG(r.rating), 2) as avg_rating
FROM products p
JOIN reviews r ON p.product_id = r.product_id
WHERE r.is_active = 1
GROUP BY p.product_id, p.product_name
ORDER BY review_count DESC
LIMIT 10;

-- Q49: Show revenue by payment method
SELECT 
    payment_method,
    SUM(final_amount) as total_revenue,
    COUNT(*) as order_count
FROM orders
WHERE payment_status = 'Paid'
GROUP BY payment_method
ORDER BY total_revenue DESC;

-- Q50: What is the average order value by month?
SELECT 
    DATE_FORMAT(order_date, '%Y-%m') as month,
    ROUND(AVG(final_amount), 2) as avg_order_value
FROM orders
WHERE payment_status = 'Paid'
GROUP BY month
ORDER BY month;

-- ====================
-- CATEGORY 3: ADVANCED QUERIES (Questions 51-75)
-- Subqueries, Window Functions, Complex JOINs
-- ====================

-- Q51: Who are the top 10 customers by revenue?
SELECT 
    u.first_name,
    u.last_name,
    u.email,
    SUM(o.final_amount) as total_spent,
    COUNT(o.order_id) as order_count
FROM users u
JOIN orders o ON u.user_id = o.user_id
WHERE o.payment_status = 'Paid'
GROUP BY u.user_id, u.first_name, u.last_name, u.email
ORDER BY total_spent DESC
LIMIT 10;

-- Q52: Show products that have never been ordered
SELECT 
    p.product_name,
    p.selling_price,
    s.seller_name
FROM products p
LEFT JOIN order_items oi ON p.product_id = oi.product_id
JOIN sellers s ON p.seller_id = s.seller_id
WHERE oi.order_item_id IS NULL;

-- Q53: What is the month-over-month growth rate?
SELECT 
    month,
    revenue,
    prev_month_revenue,
    ROUND((revenue - prev_month_revenue) * 100.0 / prev_month_revenue, 2) as growth_rate
FROM (
    SELECT 
        DATE_FORMAT(order_date, '%Y-%m') as month,
        SUM(final_amount) as revenue,
        LAG(SUM(final_amount)) OVER (ORDER BY DATE_FORMAT(order_date, '%Y-%m')) as prev_month_revenue
    FROM orders
    WHERE payment_status = 'Paid'
    GROUP BY month
) as monthly_data
WHERE prev_month_revenue IS NOT NULL;

-- Q54: Show products priced above category average
SELECT 
    p.product_name,
    p.selling_price,
    c.category_name,
    ROUND(AVG(p2.selling_price) OVER (PARTITION BY p.category_id), 2) as category_avg
FROM products p
JOIN categories c ON p.category_id = c.category_id
JOIN products p2 ON p.category_id = p2.category_id
WHERE p.selling_price > (
    SELECT AVG(selling_price) 
    FROM products 
    WHERE category_id = p.category_id
)
GROUP BY p.product_id, p.product_name, p.selling_price, c.category_name, p.category_id;

-- Q55: Find users who haven't ordered in last 30 days
SELECT 
    u.user_id,
    u.first_name,
    u.last_name,
    u.email,
    MAX(o.order_date) as last_order_date
FROM users u
LEFT JOIN orders o ON u.user_id = o.user_id
GROUP BY u.user_id, u.first_name, u.last_name, u.email
HAVING MAX(o.order_date) < DATE_SUB(NOW(), INTERVAL 30 DAY) OR MAX(o.order_date) IS NULL;

-- Q56: Show seller performance comparison
SELECT 
    s.seller_name,
    COUNT(DISTINCT o.order_id) as total_orders,
    SUM(oi.total_price) as total_revenue,
    ROUND(AVG(oi.total_price), 2) as avg_sale,
    RANK() OVER (ORDER BY SUM(oi.total_price) DESC) as revenue_rank
FROM sellers s
JOIN products p ON s.seller_id = p.seller_id
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'Delivered'
GROUP BY s.seller_id, s.seller_name;

-- Q57: What is the cart abandonment rate?
SELECT 
    COUNT(DISTINCT c.user_id) as users_with_cart,
    COUNT(DISTINCT o.user_id) as users_with_orders,
    COUNT(DISTINCT c.user_id) - COUNT(DISTINCT o.user_id) as abandoned_users,
    ROUND((COUNT(DISTINCT c.user_id) - COUNT(DISTINCT o.user_id)) * 100.0 / COUNT(DISTINCT c.user_id), 2) as abandonment_rate
FROM cart c
LEFT JOIN orders o ON c.user_id = o.user_id AND o.order_date > c.added_at;

-- Q58: Show products with best discount offers
SELECT 
    p.product_name,
    p.original_price,
    p.selling_price,
    p.discount_percentage,
    (p.original_price - p.selling_price) as discount_amount,
    s.seller_name
FROM products p
JOIN sellers s ON p.seller_id = s.seller_id
WHERE p.discount_percentage > 0
ORDER BY discount_amount DESC
LIMIT 10;

-- Q59: Find repeat customers
SELECT 
    u.user_id,
    u.first_name,
    u.last_name,
    COUNT(o.order_id) as order_count,
    SUM(o.final_amount) as total_spent
FROM users u
JOIN orders o ON u.user_id = o.user_id
WHERE o.payment_status = 'Paid'
GROUP BY u.user_id, u.first_name, u.last_name
HAVING order_count > 1
ORDER BY order_count DESC;

-- Q60: Show products with highest revenue per unit
SELECT 
    p.product_name,
    SUM(oi.quantity) as units_sold,
    SUM(oi.total_price) as total_revenue,
    ROUND(SUM(oi.total_price) / SUM(oi.quantity), 2) as revenue_per_unit
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'Delivered'
GROUP BY p.product_id, p.product_name
ORDER BY revenue_per_unit DESC
LIMIT 10;

-- Q61: What is the customer lifetime value?
SELECT 
    u.user_id,
    u.first_name,
    u.last_name,
    COUNT(o.order_id) as total_orders,
    SUM(o.final_amount) as lifetime_value,
    ROUND(AVG(o.final_amount), 2) as avg_order_value,
    DATEDIFF(MAX(o.order_date), MIN(o.order_date)) as customer_lifespan_days
FROM users u
JOIN orders o ON u.user_id = o.user_id
WHERE o.payment_status = 'Paid'
GROUP BY u.user_id, u.first_name, u.last_name
ORDER BY lifetime_value DESC
LIMIT 20;

-- Q62: Show order status distribution by month
SELECT 
    DATE_FORMAT(order_date, '%Y-%m') as month,
    order_status,
    COUNT(*) as status_count
FROM orders
GROUP BY month, order_status
ORDER BY month, order_status;

-- Q63: Find products frequently bought together
SELECT 
    oi1.product_id as product1,
    p1.product_name as product1_name,
    oi2.product_id as product2,
    p2.product_name as product2_name,
    COUNT(*) as times_together
FROM order_items oi1
JOIN order_items oi2 ON oi1.order_id = oi2.order_id AND oi1.product_id < oi2.product_id
JOIN products p1 ON oi1.product_id = p1.product_id
JOIN products p2 ON oi2.product_id = p2.product_id
GROUP BY oi1.product_id, p1.product_name, oi2.product_id, p2.product_name
HAVING times_together > 1
ORDER BY times_together DESC;

-- Q64: Calculate revenue contribution by category
SELECT 
    c.category_name,
    SUM(oi.total_price) as category_revenue,
    ROUND(SUM(oi.total_price) * 100.0 / (
        SELECT SUM(total_price) 
        FROM order_items oi2 
        JOIN orders o2 ON oi2.order_id = o2.order_id 
        WHERE o2.order_status = 'Delivered'
    ), 2) as revenue_percentage
FROM categories c
JOIN products p ON c.category_id = p.category_id
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'Delivered'
GROUP BY c.category_id, c.category_name
ORDER BY category_revenue DESC;

-- Q65: Show user engagement metrics
SELECT 
    DATE_FORMAT(u.created_at, '%Y-%m') as signup_month,
    COUNT(DISTINCT u.user_id) as new_users,
    COUNT(DISTINCT o.user_id) as active_users,
    ROUND(COUNT(DISTINCT o.user_id) * 100.0 / COUNT(DISTINCT u.user_id), 2) as activation_rate
FROM users u
LEFT JOIN orders o ON u.user_id = o.user_id AND MONTH(o.order_date) = MONTH(u.created_at) AND YEAR(o.order_date) = YEAR(u.created_at)
GROUP BY signup_month
ORDER BY signup_month;

-- Q66: Find high-value low-volume products
SELECT 
    p.product_name,
    p.selling_price,
    COUNT(oi.order_item_id) as times_ordered,
    SUM(oi.total_price) as total_revenue
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'Delivered'
GROUP BY p.product_id, p.product_name, p.selling_price
HAVING times_ordered < 10 AND p.selling_price > 50000
ORDER BY total_revenue DESC;

-- Q67: Show seasonal trends by category
SELECT 
    c.category_name,
    MONTH(o.order_date) as month,
    COUNT(o.order_id) as orders,
    SUM(oi.total_price) as revenue
FROM categories c
JOIN products p ON c.category_id = p.category_id
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'Delivered'
GROUP BY c.category_id, c.category_name, month
ORDER BY c.category_name, month;

-- Q68: Calculate customer retention rate
SELECT 
    first_order_month,
    COUNT(DISTINCT user_id) as cohort_size,
    COUNT(DISTINCT CASE WHEN months_since_first = 1 THEN user_id END) as retained_month_1,
    ROUND(COUNT(DISTINCT CASE WHEN months_since_first = 1 THEN user_id END) * 100.0 / COUNT(DISTINCT user_id), 2) as retention_rate
FROM (
    SELECT 
        u.user_id,
        DATE_FORMAT(MIN(o.order_date), '%Y-%m') as first_order_month,
        PERIOD_DIFF(DATE_FORMAT(o.order_date, '%Y%m'), DATE_FORMAT(MIN(o.order_date) OVER (PARTITION BY u.user_id), '%Y%m')) as months_since_first
    FROM users u
    JOIN orders o ON u.user_id = o.user_id
    WHERE o.payment_status = 'Paid'
) as cohort_data
GROUP BY first_order_month
ORDER BY first_order_month;

-- Q69: Show inventory turnover by seller
SELECT 
    s.seller_name,
    SUM(p.stock_quantity) as current_stock,
    SUM(oi.quantity) as units_sold,
    ROUND(SUM(oi.quantity) / SUM(p.stock_quantity), 2) as turnover_ratio
FROM sellers s
JOIN products p ON s.seller_id = p.seller_id
LEFT JOIN order_items oi ON p.product_id = oi.product_id
LEFT JOIN orders o ON oi.order_id = o.order_id AND o.order_status = 'Delivered'
GROUP BY s.seller_id, s.seller_name
HAVING current_stock > 0
ORDER BY turnover_ratio DESC;

-- Q70: Find products with declining sales
SELECT 
    p.product_name,
    DATE_FORMAT(o.order_date, '%Y-%m') as month,
    COUNT(oi.order_item_id) as monthly_orders,
    LAG(COUNT(oi.order_item_id)) OVER (PARTITION BY p.product_id ORDER BY DATE_FORMAT(o.order_date, '%Y-%m')) as prev_month_orders
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'Delivered'
GROUP BY p.product_id, p.product_name, month
HAVING prev_month_orders IS NOT NULL AND monthly_orders < prev_month_orders
ORDER BY p.product_name, month;

-- Q71: Show average basket size by user segment
SELECT 
    CASE 
        WHEN order_count = 1 THEN 'One-time'
        WHEN order_count BETWEEN 2 AND 5 THEN 'Regular'
        ELSE 'Loyal'
    END as customer_segment,
    COUNT(DISTINCT user_id) as customer_count,
    ROUND(AVG(avg_order_value), 2) as avg_basket_size
FROM (
    SELECT 
        u.user_id,
        COUNT(o.order_id) as order_count,
        AVG(o.final_amount) as avg_order_value
    FROM users u
    JOIN orders o ON u.user_id = o.user_id
    WHERE o.payment_status = 'Paid'
    GROUP BY u.user_id
) as user_segments
GROUP BY customer_segment;

-- Q72: Find cross-selling opportunities
SELECT 
    p1.product_name as anchor_product,
    p2.product_name as recommended_product,
    COUNT(*) as co_occurrence,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(DISTINCT order_id) FROM order_items WHERE product_id = p1.product_id), 2) as recommendation_strength
FROM order_items oi1
JOIN order_items oi2 ON oi1.order_id = oi2.order_id AND oi1.product_id != oi2.product_id
JOIN products p1 ON oi1.product_id = p1.product_id
JOIN products p2 ON oi2.product_id = p2.product_id
GROUP BY p1.product_id, p1.product_name, p2.product_id, p2.product_name
HAVING co_occurrence >= 2
ORDER BY co_occurrence DESC
LIMIT 20;

-- Q73: Calculate customer acquisition cost efficiency
SELECT 
    DATE_FORMAT(u.created_at, '%Y-%m') as signup_month,
    COUNT(DISTINCT u.user_id) as new_customers,
    COUNT(DISTINCT o.order_id) as orders_from_new_customers,
    SUM(o.final_amount) as revenue_from_new_customers,
    ROUND(SUM(o.final_amount) / COUNT(DISTINCT u.user_id), 2) as revenue_per_new_customer
FROM users u
LEFT JOIN orders o ON u.user_id = o.user_id AND DATE_FORMAT(o.order_date, '%Y-%m') = DATE_FORMAT(u.created_at, '%Y-%m')
WHERE o.payment_status = 'Paid' OR o.order_id IS NULL
GROUP BY signup_month
ORDER BY signup_month;

-- Q74: Show product performance matrix
SELECT 
    p.product_name,
    COUNT(oi.order_item_id) as order_frequency,
    SUM(oi.total_price) as total_revenue,
    ROUND(AVG(r.rating), 2) as avg_rating,
    CASE 
        WHEN COUNT(oi.order_item_id) > 10 AND SUM(oi.total_price) > 100000 THEN 'Star'
        WHEN COUNT(oi.order_item_id) > 10 THEN 'High Volume'
        WHEN SUM(oi.total_price) > 100000 THEN 'High Value'
        ELSE 'Regular'
    END as product_category
FROM products p
LEFT JOIN order_items oi ON p.product_id = oi.product_id
LEFT JOIN orders o ON oi.order_id = o.order_id AND o.order_status = 'Delivered'
LEFT JOIN reviews r ON p.product_id = r.product_id
GROUP BY p.product_id, p.product_name
ORDER BY total_revenue DESC;

-- Q75: Analyze shipping performance by state
SELECT 
    a.state,
    COUNT(o.order_id) as total_orders,
    ROUND(AVG(DATEDIFF(o.actual_delivery_date, o.order_date)), 2) as avg_delivery_days,
    COUNT(CASE WHEN DATEDIFF(o.actual_delivery_date, o.estimated_delivery_date) > 0 THEN 1 END) as delayed_deliveries,
    ROUND(COUNT(CASE WHEN DATEDIFF(o.actual_delivery_date, o.estimated_delivery_date) > 0 THEN 1 END) * 100.0 / COUNT(o.order_id), 2) as delay_rate
FROM addresses a
JOIN orders o ON a.address_id = o.shipping_address_id
WHERE o.actual_delivery_date IS NOT NULL
GROUP BY a.state
ORDER BY delay_rate DESC;

-- ====================
-- CATEGORY 4: COMPLEX BUSINESS QUERIES (Questions 76-100)
-- Multi-level subqueries, Complex analytics, Business metrics
-- ====================

-- Q76: RFM Analysis - Recency, Frequency, Monetary
SELECT 
    u.user_id,
    u.first_name,
    u.last_name,
    DATEDIFF(NOW(), MAX(o.order_date)) as recency_days,
    COUNT(o.order_id) as frequency,
    SUM(o.final_amount) as monetary_value,
    CASE 
        WHEN DATEDIFF(NOW(), MAX(o.order_date)) < 30 THEN 'Active'
        WHEN DATEDIFF(NOW(), MAX(o.order_date)) < 90 THEN 'At Risk'
        ELSE 'Dormant'
    END as customer_status
FROM users u
JOIN orders o ON u.user_id = o.user_id
WHERE o.payment_status = 'Paid'
GROUP BY u.user_id, u.first_name, u.last_name
ORDER BY monetary_value DESC;

-- Q77: Product affinity analysis by category
SELECT 
    c1.category_name as category1,
    c2.category_name as category2,
    COUNT(DISTINCT oi1.order_id) as orders_with_both,
    ROUND(AVG(o.final_amount), 2) as avg_order_value
FROM order_items oi1
JOIN order_items oi2 ON oi1.order_id = oi2.order_id AND oi1.product_id < oi2.product_id
JOIN products p1 ON oi1.product_id = p1.product_id
JOIN products p2 ON oi2.product_id = p2.product_id
JOIN categories c1 ON p1.category_id = c1.category_id
JOIN categories c2 ON p2.category_id = c2.category_id
JOIN orders o ON oi1.order_id = o.order_id
WHERE o.order_status = 'Delivered' AND c1.category_id != c2.category_id
GROUP BY c1.category_id, c1.category_name, c2.category_id, c2.category_name
HAVING orders_with_both > 2
ORDER BY orders_with_both DESC;

-- Q78: Customer churn prediction indicators
SELECT 
    u.user_id,
    u.first_name,
    u.last_name,
    MAX(o.order_date) as last_order_date,
    DATEDIFF(NOW(), MAX(o.order_date)) as days_since_last_order,
    COUNT(o.order_id) as total_orders,
    SUM(o.final_amount) as lifetime_value,
    ROUND(AVG(DATEDIFF(o2.order_date, o1.order_date)), 2) as avg_days_between_orders,
    CASE 
        WHEN DATEDIFF(NOW(), MAX(o.order_date)) > AVG(DATEDIFF(o2.order_date, o1.order_date)) * 2 THEN 'High Churn Risk'
        WHEN DATEDIFF(NOW(), MAX(o.order_date)) > AVG(DATEDIFF(o2.order_date, o1.order_date)) THEN 'Medium Churn Risk'
        ELSE 'Low Churn Risk'
    END as churn_risk
FROM users u
JOIN orders o ON u.user_id = o.user_id
LEFT JOIN orders o1 ON u.user_id = o1.user_id
LEFT JOIN orders o2 ON u.user_id = o2.user_id AND o2.order_date > o1.order_date
WHERE o.payment_status = 'Paid'
GROUP BY u.user_id, u.first_name, u.last_name
HAVING total_orders > 1
ORDER BY churn_risk DESC, days_since_last_order DESC;

-- Q79: Price elasticity analysis by category
SELECT 
    c.category_name,
    ROUND(AVG(p.discount_percentage), 2) as avg_discount,
    SUM(oi.quantity) as units_sold,
    ROUND(AVG(p.selling_price), 2) as avg_selling_price,
    ROUND(SUM(oi.total_price) / SUM(oi.quantity), 2) as revenue_per_unit
FROM categories c
JOIN products p ON c.category_id = p.category_id
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'Delivered'
GROUP BY c.category_id, c.category_name
ORDER BY units_sold DESC;

-- Q80: Seller market share analysis
SELECT 
    s.seller_name,
    COUNT(DISTINCT oi.order_id) as orders,
    SUM(oi.total_price) as revenue,
    ROUND(SUM(oi.total_price) * 100.0 / (
        SELECT SUM(total_price) 
        FROM order_items oi2 
        JOIN orders o2 ON oi2.order_id = o2.order_id 
        WHERE o2.order_status = 'Delivered'
    ), 2) as market_share_percent,
    RANK() OVER (ORDER BY SUM(oi.total_price) DESC) as market_rank
FROM sellers s
JOIN products p ON s.seller_id = p.seller_id
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'Delivered'
GROUP BY s.seller_id, s.seller_name
ORDER BY market_share_percent DESC;

-- Q81: Promotion effectiveness analysis
SELECT 
    c.coupon_code,
    c.discount_type,
    c.discount_value,
    COUNT(uc.user_coupon_id) as times_used,
    SUM(uc.discount_applied) as total_discount_given,
    SUM(o.final_amount) as revenue_generated,
    ROUND(SUM(o.final_amount) / SUM(uc.discount_applied), 2) as roi_ratio
FROM coupons c
JOIN user_coupons uc ON c.coupon_id = uc.coupon_id
JOIN orders o ON uc.order_id = o.order_id
WHERE o.payment_status = 'Paid'
GROUP BY c.coupon_id, c.coupon_code, c.discount_type, c.discount_value
ORDER BY roi_ratio DESC;

-- Q82: Geographic expansion opportunities
SELECT 
    a.state,
    COUNT(DISTINCT a.user_id) as registered_users,
    COUNT(DISTINCT o.order_id) as orders_placed,
    SUM(o.final_amount) as total_revenue,
    ROUND(COUNT(DISTINCT o.order_id) * 1.0 / COUNT(DISTINCT a.user_id), 2) as orders_per_user,
    ROUND(SUM(o.final_amount) / COUNT(DISTINCT a.user_id), 2) as revenue_per_user
FROM addresses a
LEFT JOIN orders o ON a.address_id = o.shipping_address_id AND o.payment_status = 'Paid'
GROUP BY a.state
ORDER BY revenue_per_user DESC;

-- Q83: Product launch performance tracking
SELECT 
    p.product_name,
    p.created_at as launch_date,
    DATEDIFF(NOW(), p.created_at) as days_since_launch,
    COUNT(oi.order_item_id) as times_ordered,
    SUM(oi.quantity) as units_sold,
    SUM(oi.total_price) as total_revenue,
    ROUND(SUM(oi.total_price) / DATEDIFF(NOW(), p.created_at), 2) as daily_revenue_rate
FROM products p
LEFT JOIN order_items oi ON p.product_id = oi.product_id
LEFT JOIN orders o ON oi.order_id = o.order_id AND o.order_status = 'Delivered'
WHERE p.created_at >= DATE_SUB(NOW(), INTERVAL 6 MONTH)
GROUP BY p.product_id, p.product_name, p.created_at
ORDER BY daily_revenue_rate DESC;

-- Q84: Payment failure analysis
SELECT 
    DATE_FORMAT(order_date, '%Y-%m') as month,
    payment_method,
    COUNT(CASE WHEN payment_status = 'Failed' THEN 1 END) as failed_payments,
    COUNT(*) as total_attempts,
    ROUND(COUNT(CASE WHEN payment_status = 'Failed' THEN 1 END) * 100.0 / COUNT(*), 2) as failure_rate,
    SUM(CASE WHEN payment_status = 'Failed' THEN final_amount ELSE 0 END) as lost_revenue
FROM orders
GROUP BY month, payment_method
ORDER BY month, failure_rate DESC;

-- Q85: Customer acquisition channel analysis (based on signup patterns)
SELECT 
    DATE_FORMAT(created_at, '%Y-%m') as signup_month,
    COUNT(*) as new_users,
    COUNT(CASE WHEN email LIKE '%@gmail.%' THEN 1 END) as gmail_users,
    COUNT(CASE WHEN email LIKE '%@yahoo.%' THEN 1 END) as yahoo_users,
    COUNT(CASE WHEN email NOT LIKE '%@gmail.%' AND email NOT LIKE '%@yahoo.%' THEN 1 END) as other_email_users
FROM users
GROUP BY signup_month
ORDER BY signup_month;

-- Q86: Inventory optimization recommendations
SELECT 
    p.product_name,
    p.stock_quantity as current_stock,
    COALESCE(SUM(oi.quantity), 0) as total_sold,
    ROUND(COALESCE(SUM(oi.quantity), 0) / 6, 2) as avg_monthly_sales,
    ROUND(p.stock_quantity / NULLIF(SUM(oi.quantity) / 6, 0), 2) as months_of_inventory,
    CASE 
        WHEN p.stock_quantity / NULLIF(SUM(oi.quantity) / 6, 0) < 1 THEN 'Restock Urgently'
        WHEN p.stock_quantity / NULLIF(SUM(oi.quantity) / 6, 0) < 2 THEN 'Restock Soon'
        WHEN p.stock_quantity / NULLIF(SUM(oi.quantity) / 6, 0) > 6 THEN 'Overstock'
        ELSE 'Optimal'
    END as stock_status
FROM products p
LEFT JOIN order_items oi ON p.product_id = oi.product_id
LEFT JOIN orders o ON oi.order_id = o.order_id AND o.order_status = 'Delivered'
WHERE p.is_active = 1
GROUP BY p.product_id, p.product_name, p.stock_quantity
ORDER BY months_of_inventory;

-- Q87: Brand loyalty analysis
SELECT 
    p.brand,
    COUNT(DISTINCT o.user_id) as unique_customers,
    COUNT(o.order_id) as total_orders,
    ROUND(COUNT(o.order_id) * 1.0 / COUNT(DISTINCT o.user_id), 2) as repeat_purchase_rate,
    SUM(o.final_amount) as total_revenue,
    ROUND(AVG(r.rating), 2) as avg_rating
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
LEFT JOIN reviews r ON p.product_id = r.product_id
WHERE o.payment_status = 'Paid' AND p.brand IS NOT NULL
GROUP BY p.brand
HAVING total_orders > 5
ORDER BY repeat_purchase_rate DESC;

-- Q88: Time-based purchase patterns
SELECT 
    HOUR(order_date) as hour_of_day,
    COUNT(*) as order_count,
    SUM(final_amount) as revenue,
    ROUND(AVG(final_amount), 2) as avg_order_value,
    COUNT(CASE WHEN payment_method = 'COD' THEN 1 END) as cod_orders,
    COUNT(CASE WHEN payment_method != 'COD' THEN 1 END) as online_payment_orders
FROM orders
WHERE payment_status = 'Paid'
GROUP BY hour_of_day
ORDER BY order_count DESC;

-- Q89: Customer segment profitability
SELECT 
    segment,
    COUNT(DISTINCT user_id) as customer_count,
    SUM(total_orders) as total_orders,
    SUM(total_revenue) as total_revenue,
    ROUND(AVG(total_revenue), 2) as avg_revenue_per_customer,
    ROUND(AVG(avg_order_value), 2) as avg_order_value
FROM (
    SELECT 
        u.user_id,
        CASE 
            WHEN COUNT(o.order_id) = 1 THEN 'One-time Buyer'
            WHEN COUNT(o.order_id) BETWEEN 2 AND 3 THEN 'Occasional Buyer'
            WHEN COUNT(o.order_id) BETWEEN 4 AND 6 THEN 'Regular Customer'
            ELSE 'VIP Customer'
        END as segment,
        COUNT(o.order_id) as total_orders,
        SUM(o.final_amount) as total_revenue,
        AVG(o.final_amount) as avg_order_value
    FROM users u
    JOIN orders o ON u.user_id = o.user_id
    WHERE o.payment_status = 'Paid'
    GROUP BY u.user_id
) as customer_segments
GROUP BY segment
ORDER BY avg_revenue_per_customer DESC;

-- Q90: Seller diversification analysis
SELECT 
    s.seller_name,
    COUNT(DISTINCT p.category_id) as categories_covered,
    COUNT(DISTINCT p.product_id) as total_products,
    SUM(oi.total_price) as total_revenue,
    ROUND(SUM(oi.total_price) / COUNT(DISTINCT p.product_id), 2) as revenue_per_product
FROM sellers s
JOIN products p ON s.seller_id = p.seller_id
LEFT JOIN order_items oi ON p.product_id = oi.product_id
LEFT JOIN orders o ON oi.order_id = o.order_id AND o.order_status = 'Delivered'
GROUP BY s.seller_id, s.seller_name
ORDER BY revenue_per_product DESC;

-- Q91: Revenue forecasting based on trends
SELECT 
    DATE_FORMAT(order_date, '%Y-%m') as month,
    SUM(final_amount) as actual_revenue,
    AVG(SUM(final_amount)) OVER (ORDER BY DATE_FORMAT(order_date, '%Y-%m') ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) as moving_avg_3month,
    LAG(SUM(final_amount), 1) OVER (ORDER BY DATE_FORMAT(order_date, '%Y-%m')) as prev_month_revenue,
    ROUND((SUM(final_amount) - LAG(SUM(final_amount), 1) OVER (ORDER BY DATE_FORMAT(order_date, '%Y-%m'))) * 100.0 / 
        LAG(SUM(final_amount), 1) OVER (ORDER BY DATE_FORMAT(order_date, '%Y-%m')), 2) as growth_rate
FROM orders
WHERE payment_status = 'Paid'
GROUP BY month
ORDER BY month;

-- Q92: Product cannibalization analysis
SELECT 
    p1.product_name as product1,
    p2.product_name as product2,
    p1.category_id,
    COUNT(DISTINCT o.user_id) as shared_customers,
    SUM(CASE WHEN oi1.order_id = oi2.order_id THEN 1 ELSE 0 END) as bought_together,
    ABS(p1.selling_price - p2.selling_price) as price_difference
FROM products p1
JOIN products p2 ON p1.category_id = p2.category_id AND p1.product_id < p2.product_id
JOIN order_items oi1 ON p1.product_id = oi1.product_id
JOIN order_items oi2 ON p2.product_id = oi2.product_id
JOIN orders o ON (oi1.order_id = o.order_id OR oi2.order_id = o.order_id)
WHERE o.order_status = 'Delivered'
GROUP BY p1.product_id, p1.product_name, p2.product_id, p2.product_name, p1.category_id, p1.selling_price, p2.selling_price
HAVING shared_customers > 2
ORDER BY shared_customers DESC;

-- Q93: Operational efficiency by seller
SELECT 
    s.seller_name,
    COUNT(DISTINCT o.order_id) as total_orders,
    ROUND(AVG(DATEDIFF(o.actual_delivery_date, o.order_date)), 2) as avg_fulfillment_days,
    COUNT(CASE WHEN o.order_status = 'Cancelled' THEN 1 END) as cancelled_orders,
    ROUND(COUNT(CASE WHEN o.order_status = 'Cancelled' THEN 1 END) * 100.0 / COUNT(o.order_id), 2) as cancellation_rate,
    ROUND(AVG(r.rating), 2) as avg_rating,
    SUM(oi.total_price) as total_revenue
FROM sellers s
JOIN products p ON s.seller_id = p.seller_id
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
LEFT JOIN reviews r ON p.product_id = r.product_id
GROUP BY s.seller_id, s.seller_name
ORDER BY total_revenue DESC;

-- Q94: Customer demographic insights
SELECT 
    u.gender,
    CASE 
        WHEN TIMESTAMPDIFF(YEAR, u.date_of_birth, CURDATE()) < 25 THEN 'Under 25'
        WHEN TIMESTAMPDIFF(YEAR, u.date_of_birth, CURDATE()) BETWEEN 25 AND 34 THEN '25-34'
        WHEN TIMESTAMPDIFF(YEAR, u.date_of_birth, CURDATE()) BETWEEN 35 AND 44 THEN '35-44'
        ELSE '45+'
    END as age_group,
    COUNT(DISTINCT u.user_id) as customer_count,
    COUNT(o.order_id) as total_orders,
    SUM(o.final_amount) as total_spent,
    ROUND(AVG(o.final_amount), 2) as avg_order_value
FROM users u
LEFT JOIN orders o ON u.user_id = o.user_id AND o.payment_status = 'Paid'
WHERE u.date_of_birth IS NOT NULL
GROUP BY u.gender, age_group
ORDER BY total_spent DESC;

-- Q95: Product review sentiment vs sales correlation
SELECT 
    p.product_name,
    ROUND(AVG(r.rating), 2) as avg_rating,
    COUNT(r.review_id) as review_count,
    SUM(oi.quantity) as units_sold,
    SUM(oi.total_price) as total_revenue,
    CASE 
        WHEN AVG(r.rating) >= 4.5 THEN 'Excellent'
        WHEN AVG(r.rating) >= 4.0 THEN 'Good'
        WHEN AVG(r.rating) >= 3.0 THEN 'Average'
        ELSE 'Poor'
    END as rating_category
FROM products p
LEFT JOIN reviews r ON p.product_id = r.product_id AND r.is_active = 1
LEFT JOIN order_items oi ON p.product_id = oi.product_id
LEFT JOIN orders o ON oi.order_id = o.order_id AND o.order_status = 'Delivered'
GROUP BY p.product_id, p.product_name
HAVING review_count > 0
ORDER BY total_revenue DESC;

-- Q96: Discount strategy effectiveness
SELECT 
    CASE 
        WHEN p.discount_percentage = 0 THEN 'No Discount'
        WHEN p.discount_percentage < 15 THEN 'Low (0-15%)'
        WHEN p.discount_percentage < 25 THEN 'Medium (15-25%)'
        ELSE 'High (25%+)'
    END as discount_tier,
    COUNT(DISTINCT p.product_id) as product_count,
    SUM(oi.quantity) as units_sold,
    SUM(oi.total_price) as revenue,
    ROUND(AVG(p.discount_percentage), 2) as avg_discount,
    ROUND(SUM(oi.total_price) / SUM(oi.quantity), 2) as avg_selling_price
FROM products p
LEFT JOIN order_items oi ON p.product_id = oi.product_id
LEFT JOIN orders o ON oi.order_id = o.order_id AND o.order_status = 'Delivered'
GROUP BY discount_tier
ORDER BY revenue DESC;

-- Q97: Customer journey analysis
SELECT 
    u.user_id,
    u.first_name,
    u.last_name,
    MIN(o.order_date) as first_order_date,
    MAX(o.order_date) as last_order_date,
    COUNT(o.order_id) as total_orders,
    ROUND(DATEDIFF(MAX(o.order_date), MIN(o.order_date)) / NULLIF(COUNT(o.order_id) - 1, 0), 2) as avg_days_between_orders,
    SUM(o.final_amount) as lifetime_value,
    COUNT(DISTINCT oi.product_id) as unique_products_purchased,
    COUNT(DISTINCT p.category_id) as unique_categories_purchased
FROM users u
JOIN orders o ON u.user_id = o.user_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
WHERE o.payment_status = 'Paid'
GROUP BY u.user_id, u.first_name, u.last_name
HAVING total_orders > 1
ORDER BY lifetime_value DESC
LIMIT 20;

-- Q98: Market basket size analysis
SELECT 
    items_per_order,
    COUNT(*) as order_count,
    ROUND(AVG(order_value), 2) as avg_order_value,
    SUM(order_value) as total_revenue,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM orders WHERE payment_status = 'Paid'), 2) as percentage_of_orders
FROM (
    SELECT 
        o.order_id,
        COUNT(oi.order_item_id) as items_per_order,
        o.final_amount as order_value
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.payment_status = 'Paid'
    GROUP BY o.order_id, o.final_amount
) as order_items_count
GROUP BY items_per_order
ORDER BY items_per_order;

-- Q99: Return and refund analysis
SELECT 
    DATE_FORMAT(o.order_date, '%Y-%m') as month,
    COUNT(CASE WHEN o.order_status = 'Returned' THEN 1 END) as returned_orders,
    COUNT(CASE WHEN o.payment_status = 'Refunded' THEN 1 END) as refunded_orders,
    COUNT(*) as total_orders,
    ROUND(COUNT(CASE WHEN o.order_status = 'Returned' THEN 1 END) * 100.0 / COUNT(*), 2) as return_rate,
    SUM(CASE WHEN o.payment_status = 'Refunded' THEN o.final_amount ELSE 0 END) as refund_amount
FROM orders o
GROUP BY month
ORDER BY month;

-- Q100: Comprehensive business health dashboard
SELECT 
    'Total Revenue' as metric,
    CONCAT('₹', FORMAT(SUM(final_amount), 2)) as value
FROM orders WHERE payment_status = 'Paid'
UNION ALL
SELECT 
    'Total Orders',
    CAST(COUNT(*) AS CHAR)
FROM orders WHERE payment_status = 'Paid'
UNION ALL
SELECT 
    'Active Customers',
    CAST(COUNT(DISTINCT user_id) AS CHAR)
FROM orders WHERE payment_status = 'Paid'
UNION ALL
SELECT 
    'Average Order Value',
    CONCAT('₹', FORMAT(AVG(final_amount), 2))
FROM orders WHERE payment_status = 'Paid'
UNION ALL
SELECT 
    'Conversion Rate',
    CONCAT(FORMAT(COUNT(DISTINCT CASE WHEN o.payment_status = 'Paid' THEN o.user_id END) * 100.0 / COUNT(DISTINCT u.user_id), 2), '%')
FROM users u LEFT JOIN orders o ON u.user_id = o.user_id
UNION ALL
SELECT 
    'Total Products',
    CAST(COUNT(*) AS CHAR)
FROM products WHERE is_active = 1
UNION ALL
SELECT 
    'Average Rating',
    CAST(ROUND(AVG(rating), 2) AS CHAR)
FROM reviews WHERE is_active = 1
UNION ALL
SELECT 
    'Active Sellers',
    CAST(COUNT(*) AS CHAR)
FROM sellers WHERE is_active = 1
UNION ALL
SELECT 
    'Order Fulfillment Rate',
    CONCAT(FORMAT(COUNT(CASE WHEN order_status = 'Delivered' THEN 1 END) * 100.0 / COUNT(*), 2), '%')
FROM orders
UNION ALL
SELECT 
    'Month-over-Month Growth',
    CONCAT(FORMAT(
        ((SELECT SUM(final_amount) FROM orders WHERE payment_status = 'Paid' AND DATE_FORMAT(order_date, '%Y-%m') = DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 1 MONTH), '%Y-%m')) -
         (SELECT SUM(final_amount) FROM orders WHERE payment_status = 'Paid' AND DATE_FORMAT(order_date, '%Y-%m') = DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 2 MONTH), '%Y-%m'))) * 100.0 /
        NULLIF((SELECT SUM(final_amount) FROM orders WHERE payment_status = 'Paid' AND DATE_FORMAT(order_date, '%Y-%m') = DATE_FORMAT(DATE_SUB(NOW(), INTERVAL 2 MONTH), '%Y-%m')), 0)
    , 2), '%');

-- ==========================================
-- END OF TEST CASES
-- ==========================================

-- EVALUATION METRICS FOR CONFUSION MATRIX:
-- True Positive (TP): System generates correct SQL for the question
-- False Positive (FP): System generates incorrect SQL but executes
-- True Negative (TN): System correctly identifies unparseable question
-- False Negative (FN): System fails to generate SQL for valid question
--
-- Accuracy = (TP + TN) / (TP + TN + FP + FN)
-- Precision = TP / (TP + FP)
-- Recall = TP / (TP + FN)
-- F1 Score = 2 * (Precision * Recall) / (Precision + Recall)
-- ==========================================