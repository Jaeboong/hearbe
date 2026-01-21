-- DDL for Shopping Assistant Project
-- Generated based on ERD documentation and legacy schema reference for ERDCloud compatibility

CREATE TABLE `users` (
    `user_id` int NOT NULL AUTO_INCREMENT,
    `login_id` varchar(50) NOT NULL,
    `username` varchar(50) NULL,
    `password` varchar(255) NULL,
    `phone_number` varchar(20) NOT NULL,
    `simple_password` varchar(255) NULL,
    `user_type` varchar(20) NOT NULL DEFAULT 'GENERAL',
    `gender` varchar(10) NULL,
    `email` varchar(100) NULL,
    `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `last_login_at` timestamp NULL
);

CREATE TABLE `profiles` (
    `profile_id` int NOT NULL AUTO_INCREMENT,
    `user_id` int NOT NULL,
    `height` float NULL DEFAULT 0,
    `weight` float NULL DEFAULT 0,
    `birth_date` varchar(20) NULL,
    `updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE `welfare_cards` (
    `welfare_card_id` int NOT NULL AUTO_INCREMENT,
    `user_id` int NOT NULL,
    `cvc` varchar(255) NULL COMMENT 'CVC 번호 (AES-256 암호화 필수)',
    `owner_name` varchar(50) NULL COMMENT '소유자 이름',
    `birth_date` varchar(6) NULL COMMENT '생년월일(주민번호 앞자리)',
    `gender` varchar(10) NULL COMMENT '성별',
    `issue_date` date NULL COMMENT '발급일자',
    `expiration_date` date NULL COMMENT '유효기간',
    `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` timestamp NULL
);

CREATE TABLE `platforms` (
    `platform_id` int NOT NULL AUTO_INCREMENT,
    `shop_name` varchar(100) NOT NULL,
    `base_url` varchar(255) NULL,
    `api_endpoint_url` varchar(255) NULL
);

CREATE TABLE `products` (
    `product_id` int NOT NULL AUTO_INCREMENT,
    `platform_id` int NOT NULL,
    `product_name` varchar(200) NOT NULL,
    `product_url` text NULL,
    `external_product_id` varchar(100) NULL,
    `last_synced_at` timestamp NULL,
    `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` timestamp NULL
);

CREATE TABLE `cart_items` (
    `cart_item_id` int NOT NULL AUTO_INCREMENT,
    `user_id` int NOT NULL,
    `product_id` int NOT NULL,
    `platform_id` int NOT NULL,
    `product_metadata` json NULL,
    `selected_options` json NULL,
    `quantity` integer NOT NULL DEFAULT 1,
    `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE `wishlist_items` (
    `wishlist_item_id` int NOT NULL AUTO_INCREMENT,
    `user_id` int NOT NULL,
    `product_id` int NOT NULL,
    `platform_id` int NOT NULL,
    `product_metadata` json NULL,
    `selected_options` json NULL,
    `liked_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `is_active` boolean NOT NULL DEFAULT true
);

CREATE TABLE `favorites` (
    `favorite_id` int NOT NULL AUTO_INCREMENT,
    `user_id` int NOT NULL,
    `product_id` int NOT NULL,
    `alias` varchar(100) NULL,
    `selected_options` json NULL,
    `automation_sequence` json NULL,
    `product_metadata` json NULL,
    `purchase_count_12m` integer NOT NULL DEFAULT 0,
    `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` timestamp NULL
);

CREATE TABLE `orders` (
    `order_id` int NOT NULL AUTO_INCREMENT,
    `user_id` int NOT NULL,
    `total_amount` integer NOT NULL DEFAULT 0,
    `pay_status` varchar(20) NOT NULL DEFAULT 'PAID',
    `order_detail_url` text NULL,
    `product_metadata` json NULL,
    `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `updated_at` timestamp NULL
);

CREATE TABLE `order_items` (
    `order_item_id` int NOT NULL AUTO_INCREMENT,
    `order_id` int NOT NULL,
    `user_id` int NOT NULL,
    `product_id` int NOT NULL,
    `platform_id` int NOT NULL,
    `product_name` varchar(200) NULL,
    `product_metadata` json NULL,
    `price_at_order` integer NOT NULL DEFAULT 0,
    `quantity` integer NOT NULL DEFAULT 1
);

CREATE TABLE `sharing_session_logs` (
    `sharing_session_id` int NOT NULL AUTO_INCREMENT,
    `host_user_id` int NOT NULL,
    `started_at` timestamp NULL,
    `ended_at` timestamp NULL,
    `duration_seconds` integer NULL DEFAULT 0,
    `meeting_code` varchar(10) NULL,
    `session_status` varchar(20) NOT NULL DEFAULT 'active',
    `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Primary Key Constraints
ALTER TABLE `users` ADD CONSTRAINT `PK_USERS` PRIMARY KEY (`user_id`);
ALTER TABLE `profiles` ADD CONSTRAINT `PK_PROFILES` PRIMARY KEY (`profile_id`);
ALTER TABLE `welfare_cards` ADD CONSTRAINT `PK_WELFARE_CARDS` PRIMARY KEY (`welfare_card_id`);
ALTER TABLE `platforms` ADD CONSTRAINT `PK_PLATFORMS` PRIMARY KEY (`platform_id`);
ALTER TABLE `products` ADD CONSTRAINT `PK_PRODUCTS` PRIMARY KEY (`product_id`);
ALTER TABLE `cart_items` ADD CONSTRAINT `PK_CART_ITEMS` PRIMARY KEY (`cart_item_id`);
ALTER TABLE `wishlist_items` ADD CONSTRAINT `PK_WISHLIST_ITEMS` PRIMARY KEY (`wishlist_item_id`);
ALTER TABLE `favorites` ADD CONSTRAINT `PK_FAVORITES` PRIMARY KEY (`favorite_id`);
ALTER TABLE `orders` ADD CONSTRAINT `PK_ORDERS` PRIMARY KEY (`order_id`);
ALTER TABLE `order_items` ADD CONSTRAINT `PK_ORDER_ITEMS` PRIMARY KEY (`order_item_id`);
ALTER TABLE `sharing_session_logs` ADD CONSTRAINT `PK_SHARING_SESSION_LOGS` PRIMARY KEY (`sharing_session_id`);

-- Unique Constraints
ALTER TABLE `users` ADD CONSTRAINT `UQ_USERS_LOGIN_ID` UNIQUE (`login_id`);
ALTER TABLE `users` ADD CONSTRAINT `UQ_USERS_PHONE` UNIQUE (`phone_number`);
ALTER TABLE `profiles` ADD CONSTRAINT `UQ_PROFILES_USER_ID` UNIQUE (`user_id`);
ALTER TABLE `welfare_cards` ADD CONSTRAINT `UQ_WELFARE_CARDS_USER_ID` UNIQUE (`user_id`);
ALTER TABLE `platforms` ADD CONSTRAINT `UQ_PLATFORMS_SHOP_NAME` UNIQUE (`shop_name`);
ALTER TABLE `sharing_session_logs` ADD CONSTRAINT `UQ_SHARING_SESSION_LOGS_MEETING_CODE` UNIQUE (`meeting_code`);

-- Foreign Key Constraints
ALTER TABLE `profiles` ADD CONSTRAINT `FK_PROFILES_USER_ID` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);
ALTER TABLE `welfare_cards` ADD CONSTRAINT `FK_WELFARE_CARDS_USER_ID` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);
ALTER TABLE `products` ADD CONSTRAINT `FK_PRODUCTS_PLATFORM_ID` FOREIGN KEY (`platform_id`) REFERENCES `platforms` (`platform_id`);
ALTER TABLE `cart_items` ADD CONSTRAINT `FK_CART_ITEMS_USER_ID` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);
ALTER TABLE `cart_items` ADD CONSTRAINT `FK_CART_ITEMS_PRODUCT_ID` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`);
ALTER TABLE `wishlist_items` ADD CONSTRAINT `FK_WISHLIST_ITEMS_USER_ID` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);
ALTER TABLE `wishlist_items` ADD CONSTRAINT `FK_WISHLIST_ITEMS_PRODUCT_ID` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`);
ALTER TABLE `wishlist_items` ADD CONSTRAINT `FK_WISHLIST_ITEMS_PLATFORM_ID` FOREIGN KEY (`platform_id`) REFERENCES `platforms` (`platform_id`);
ALTER TABLE `favorites` ADD CONSTRAINT `FK_FAVORITES_USER_ID` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);
ALTER TABLE `favorites` ADD CONSTRAINT `FK_FAVORITES_PRODUCT_ID` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`);
ALTER TABLE `orders` ADD CONSTRAINT `FK_ORDERS_USER_ID` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);
ALTER TABLE `order_items` ADD CONSTRAINT `FK_ORDER_ITEMS_ORDER_ID` FOREIGN KEY (`order_id`) REFERENCES `orders` (`order_id`);
ALTER TABLE `order_items` ADD CONSTRAINT `FK_ORDER_ITEMS_USER_ID` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);
ALTER TABLE `order_items` ADD CONSTRAINT `FK_ORDER_ITEMS_PRODUCT_ID` FOREIGN KEY (`product_id`) REFERENCES `products` (`product_id`);
ALTER TABLE `order_items` ADD CONSTRAINT `FK_ORDER_ITEMS_PLATFORM_ID` FOREIGN KEY (`platform_id`) REFERENCES `platforms` (`platform_id`);
ALTER TABLE `sharing_session_logs` ADD CONSTRAINT `FK_SHARING_SESSION_LOGS_HOST_USER_ID` FOREIGN KEY (`host_user_id`) REFERENCES `users` (`user_id`);