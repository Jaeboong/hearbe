-- DDL for Ear Shopping (영문 컬럼명, products 테이블 제거)
-- 시각장애인용 AI 음성 쇼핑 플랫폼

-- ========================================
-- 테이블 생성
-- ========================================

CREATE TABLE `platforms` (
	`id` int NOT NULL AUTO_INCREMENT,
	`platform_name` varchar(50) NULL,
	`base_url` varchar(500) NOT NULL,
	PRIMARY KEY (`id`)
);

CREATE TABLE `users` (
	`id` int NOT NULL AUTO_INCREMENT,
	`login_id` varchar(30) NOT NULL,
	`email` varchar(100) NULL,
	`password` varchar(255) NOT NULL,
	`phone_number` varchar(20) NOT NULL,
	`simple_password` varchar(6) NULL,
	`username` varchar(15) NULL,
	`user_type` ENUM('BLIND', 'BIG', 'COMMON', 'SHARING') NOT NULL DEFAULT 'BLIND',
	`created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (`id`),
	UNIQUE KEY `UQ_LOGIN_ID` (`login_id`),
	UNIQUE KEY `UQ_PHONE` (`phone_number`)
);

CREATE TABLE `profiles` (
	`id` int NOT NULL AUTO_INCREMENT,
	`user_id` int NOT NULL,
	`gender` ENUM('M', 'F') NULL,
	`height` float NULL,
	`weight` float NULL,
	`birth_date` date NULL,
	`updated_at` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	PRIMARY KEY (`id`),
	UNIQUE KEY `UQ_PROFILE_USER` (`user_id`)
);

CREATE TABLE `welfare_cards` (
	`id` int NOT NULL AUTO_INCREMENT,
	`user_id` int NOT NULL,
	`cvc` varchar(5) NULL COMMENT 'CVC 번호 (AES-256 암호화 필수)',
	`issue_date` date NOT NULL,
	`expiration_date` date NOT NULL,
	`created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	PRIMARY KEY (`id`),
	UNIQUE KEY `UQ_WELFARE_USER` (`user_id`)
);

CREATE TABLE `cart_items` (
	`id` int NOT NULL AUTO_INCREMENT,
	`user_id` int NOT NULL,
	`product_metadata` json NULL,
	`quantity` int NOT NULL DEFAULT 1,
	`created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (`id`),
	KEY `idx_cart_user` (`user_id`)
);

CREATE TABLE `wishlist_items` (
	`id` int NOT NULL AUTO_INCREMENT,
	`user_id` int NOT NULL,
	`platform_id` int NOT NULL,
	`product_metadata` json NULL,
	`created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
	PRIMARY KEY (`id`),
	KEY `idx_wishlist_user_platform` (`user_id`, `platform_id`)
);

CREATE TABLE `orders` (
	`id` int NOT NULL AUTO_INCREMENT,
	`user_id` int NOT NULL,
	`order_detail_url` varchar(1000) NULL,
	`created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`updated_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	PRIMARY KEY (`id`),
	KEY `idx_orders_user_created` (`user_id`, `created_at`)
);

CREATE TABLE `order_items` (
	`id` int NOT NULL AUTO_INCREMENT,
	`order_id` int NOT NULL,
	`product_name` varchar(100) NULL,
	`metadata` json NULL,
	`price` varchar(100) NOT NULL,
	`quantity` int NOT NULL DEFAULT 1,
	PRIMARY KEY (`id`),
	KEY `idx_order_items_order` (`order_id`)
);

CREATE TABLE `sharing_session_logs` (
	`id` int NOT NULL AUTO_INCREMENT,
	`user_id` int NOT NULL COMMENT 'host user id',
	`started_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
	`ended_at` timestamp NULL,
	`session_status` ENUM('active', 'completed', 'terminated') NOT NULL DEFAULT 'active',
	PRIMARY KEY (`id`)
);

-- ========================================
-- Foreign Key 제약조건
-- ========================================

-- profiles
ALTER TABLE `profiles` 
	ADD CONSTRAINT `FK_profiles_user` 
	FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

-- welfare_cards
ALTER TABLE `welfare_cards` 
	ADD CONSTRAINT `FK_welfare_cards_user` 
	FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

-- cart_items
ALTER TABLE `cart_items` 
	ADD CONSTRAINT `FK_cart_items_user` 
	FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

-- wishlist_items
ALTER TABLE `wishlist_items` 
	ADD CONSTRAINT `FK_wishlist_items_user` 
	FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
	ADD CONSTRAINT `FK_wishlist_items_platform` 
	FOREIGN KEY (`platform_id`) REFERENCES `platforms` (`id`) ON DELETE CASCADE;

-- orders
ALTER TABLE `orders` 
	ADD CONSTRAINT `FK_orders_user` 
	FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;

-- order_items
ALTER TABLE `order_items` 
	ADD CONSTRAINT `FK_order_items_order` 
	FOREIGN KEY (`order_id`) REFERENCES `orders` (`id`) ON DELETE CASCADE;

-- sharing_session_logs
ALTER TABLE `sharing_session_logs` 
	ADD CONSTRAINT `FK_sharing_session_logs_host` 
	FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;
