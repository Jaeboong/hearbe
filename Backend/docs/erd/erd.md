CREATE TABLE `platforms` (
	`platform_id` int NOT NULL AUTO_INCREMENT,
	`platform_name` varchar(100) NULL,
	`base_url` varchar(500) NOT NULL
);

CREATE TABLE `wishlist_items` (
	`wishlist_item_id` int NOT NULL AUTO_INCREMENT,
	`user_id` varchar(30) NOT NULL,
	`product_metadata` json NULL,
	`created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`platform_id` int NOT NULL
);

CREATE TABLE `welfare_cards` (
	`welfare_card_id` int NOT NULL AUTO_INCREMENT,
	`user_id` varchar(30) NOT NULL,
	`cvc` varchar(5) NULL COMMENT 'CVC 번호 (AES-256 암호화 필수)',
	`issue_date` date NOT NULL COMMENT '발급일자',
	`expiration_date` date NOT NULL COMMENT '유효기간',
	`created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE `cart_items` (
	`cart_item_id` int NOT NULL AUTO_INCREMENT,
	`user_id` varchar(30) NOT NULL,
	`product_metadata` json NULL,
	`quantity` int NOT NULL DEFAULT 1,
	`created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE `users` (
	`user_id` varchar(30) NOT NULL,
	`username` varchar(15) NULL,
	`password` varchar(255) NULL,
	`phone_number` varchar(20) NOT NULL,
	`simple_password` varchar(6) NULL,
	`user_type` enum('BLIND', 'LOW_VISION', 'GUARDIAN', 'GENERAL') NOT NULL DEFAULT 'BLIND',
	`last_login_at` timestamp NULL,
	`created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE `sharing_session_logs` (
	`sharing_session_id` int NOT NULL AUTO_INCREMENT,
	`host_user_id` varchar(30) NOT NULL,
	`started_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`ended_at` timestamp NULL,
	`session_status` enum('active', 'completed', 'cancelled') NOT NULL DEFAULT 'active'
);

CREATE TABLE `order_items` (
	`order_item_id` int NOT NULL AUTO_INCREMENT,
	`order_id` int NOT NULL,
	`product_name` varchar(100) NULL,
	`metadata` json NULL,
	`price` varchar(100) NOT NULL,
	`quantity` int NOT NULL DEFAULT 1
);

CREATE TABLE `profiles` (
	`profile_id` int NOT NULL AUTO_INCREMENT,
	`user_id` varchar(30) NOT NULL,
	`gender` varchar(1) NULL,
	`height` float NULL,
	`weight` float NULL,
	`birth_date` date NULL,
	`updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE `orders` (
	`order_id` int NOT NULL AUTO_INCREMENT,
	`user_id` varchar(30) NOT NULL,
	`order_detail_url` varchar(1000) NULL,
	`created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Primary Key Constraints
ALTER TABLE `platforms` ADD CONSTRAINT `PK_PLATFORMS` PRIMARY KEY (`platform_id`);
ALTER TABLE `wishlist_items` ADD CONSTRAINT `PK_WISHLIST_ITEMS` PRIMARY KEY (`wishlist_item_id`);
ALTER TABLE `welfare_cards` ADD CONSTRAINT `PK_WELFARE_CARDS` PRIMARY KEY (`welfare_card_id`);
ALTER TABLE `cart_items` ADD CONSTRAINT `PK_CART_ITEMS` PRIMARY KEY (`cart_item_id`);
ALTER TABLE `users` ADD CONSTRAINT `PK_USERS` PRIMARY KEY (`user_id`);
ALTER TABLE `sharing_session_logs` ADD CONSTRAINT `PK_SHARING_SESSION_LOGS` PRIMARY KEY (`sharing_session_id`);
ALTER TABLE `order_items` ADD CONSTRAINT `PK_ORDER_ITEMS` PRIMARY KEY (`order_item_id`);
ALTER TABLE `profiles` ADD CONSTRAINT `PK_PROFILES` PRIMARY KEY (`profile_id`);
ALTER TABLE `orders` ADD CONSTRAINT `PK_ORDERS` PRIMARY KEY (`order_id`);

-- Unique Constraints
ALTER TABLE `users` ADD CONSTRAINT `UQ_USERS_PHONE` UNIQUE (`phone_number`);
ALTER TABLE `profiles` ADD CONSTRAINT `UQ_PROFILES_USER_ID` UNIQUE (`user_id`);
ALTER TABLE `welfare_cards` ADD CONSTRAINT `UQ_WELFARE_CARDS_USER_ID` UNIQUE (`user_id`);

-- Foreign Key Constraints
ALTER TABLE `profiles` ADD CONSTRAINT `FK_PROFILES_USER_ID` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);
ALTER TABLE `welfare_cards` ADD CONSTRAINT `FK_WELFARE_CARDS_USER_ID` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);
ALTER TABLE `cart_items` ADD CONSTRAINT `FK_CART_ITEMS_USER_ID` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);
ALTER TABLE `cart_items` ADD CONSTRAINT `FK_CART_ITEMS_PLATFORM_ID` FOREIGN KEY (`platform_id`) REFERENCES `platforms` (`platform_id`);
ALTER TABLE `wishlist_items` ADD CONSTRAINT `FK_WISHLIST_ITEMS_USER_ID` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);
ALTER TABLE `wishlist_items` ADD CONSTRAINT `FK_WISHLIST_ITEMS_PLATFORM_ID` FOREIGN KEY (`platform_id`) REFERENCES `platforms` (`platform_id`);
ALTER TABLE `orders` ADD CONSTRAINT `FK_ORDERS_USER_ID` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);
ALTER TABLE `order_items` ADD CONSTRAINT `FK_ORDER_ITEMS_ORDER_ID` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`);
ALTER TABLE `sharing_session_logs` ADD CONSTRAINT `FK_SHARING_SESSION_LOGS_HOST_USER_ID` FOREIGN KEY (`host_user_id`) REFERENCES `users` (`user_id`);
