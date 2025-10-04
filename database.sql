-- database.sql

CREATE TABLE `users` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(100) NOT NULL,
  `phone` VARCHAR(15) NOT NULL UNIQUE,
  `password` VARCHAR(255) NOT NULL
);

CREATE TABLE `foods` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(100) NOT NULL,
  `description` TEXT,
  `price_per_unit` DECIMAL(10, 2) NOT NULL,
  `image_url` VARCHAR(255)
);

CREATE TABLE `custom_requests` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `food_name` VARCHAR(255) NOT NULL,
  `quantity` INT NOT NULL,
  `delivery_date` DATE NOT NULL,
  `delivery_time` TIME NOT NULL,
  `status` ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
  FOREIGN KEY (`user_id`) REFERENCES `users`(`id`)
);

CREATE TABLE `orders` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id` INT NOT NULL,
  `total_amount` DECIMAL(10, 2) NOT NULL,
  `order_date` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  `delivery_date` DATE NOT NULL,
  `delivery_time` TIME NOT NULL,
  `delivery_option` ENUM('pickup', 'delivery') NOT NULL,
  `payment_method` VARCHAR(50) NOT NULL,
  `status` VARCHAR(50) DEFAULT 'booked'
);


-- Insert some sample food items for the dashboard
INSERT INTO `foods` (`name`, `description`, `price_per_unit`, `image_url`) VALUES
('Chicken Biryani', 'Aromatic rice dish with tender chicken and spices.', 150.00, 'https://via.placeholder.com/300x200.png?text=Chicken+Biryani'),
('Paneer Butter Masala', 'Creamy and rich cottage cheese curry.', 120.00, 'https://via.placeholder.com/300x200.png?text=Paneer+Masala'),
('Vegetable Pulao', 'A medley of fresh vegetables and fragrant rice.', 100.00, 'https://via.placeholder.com/300x200.png?text=Veg+Pulao'),
('Gulab Jamun', 'Sweet milk-solid based dessert (per piece).', 15.00, 'https://via.placeholder.com/300x200.png?text=Gulab+Jamun');