CREATE TABLE users (
    user_id bigint NOT NULL AUTO_INCREMENT PRIMARY KEY,
    login_id varchar(50) NOT NULL UNIQUE,
    username varchar(50),
    password varchar(100),
    phone_number varchar(20) NOT NULL UNIQUE,
    simple_password varchar(100),
    user_type varchar(20),
    created_at timestamp DEFAULT now(),
    last_login_at timestamp
);

CREATE TABLE profiles (
    profile_id bigint NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id bigint NOT NULL UNIQUE,
    height float,
    weight float,
    birth_date varchar(10),
    updated_at timestamp DEFAULT now()
);

CREATE TABLE welfare_cards (
    welfare_card_id bigint NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id bigint NOT NULL UNIQUE,
    cvc varchar(100) COMMENT 'CVC 번호 (AES-256 암호호화 필수)',
    owner_name varchar(50) COMMENT,
    birth_date varchar(6) COMMENT '생년월일(주민번호 앞자리)',
    gender varchar(10) COMMENT '성별',
    issue_date date COMMENT '발급일자',
    expiration_date date COMMENT '유효기간',
    created_at timestamp DEFAULT now(),
    updated_at timestamp
);

CREATE TABLE platforms (
    platform_id bigint NOT NULL AUTO_INCREMENT PRIMARY KEY,
    shop_name varchar(100) NOT NULL UNIQUE,
    base_url varchar(500),
    api_endpoint_url varchar(500)
);

CREATE TABLE products (
    product_id bigint NOT NULL AUTO_INCREMENT PRIMARY KEY,
    platform_id bigint NOT NULL,
    product_name varchar(200),
    product_url text,
    external_product_id varchar(100),
    price integer COMMENT '상품 가격 (동기화 시점 기준)',
    last_synced_at timestamp,
    created_at timestamp DEFAULT now(),
    updated_at timestamp
);

CREATE TABLE cart_items (
    cart_item_id bigint NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id bigint NOT NULL,
    product_id bigint NOT NULL,
    platform_id bigint NOT NULL,
    product_metadata json,
    selected_options json,
    quantity integer DEFAULT 1,
    created_at timestamp DEFAULT now()
);

CREATE TABLE wishlist_items (
    wishlist_item_id bigint NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id bigint NOT NULL,
    product_id bigint NOT NULL,
    platform_id bigint NOT NULL,
    product_metadata json,
    selected_options json,
    liked_at timestamp DEFAULT now(),
    is_active boolean DEFAULT true
);

CREATE TABLE favorites (
    favorite_id bigint NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id bigint NOT NULL,
    product_id bigint NOT NULL,
    alias varchar(100),
    selected_options json,
    automation_sequence json,
    product_metadata json,
    purchase_count_12m integer DEFAULT 0,
    created_at timestamp DEFAULT now(),
    updated_at timestamp
);

CREATE TABLE orders (
    order_id bigint NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id bigint NOT NULL,
    total_amount integer,
    pay_status varchar(20) DEFAULT 'PAID',
    order_detail_url text,
    product_metadata json,
    created_at timestamp DEFAULT now(),
    updated_at timestamp
);

CREATE TABLE order_items (
    order_item_id bigint NOT NULL AUTO_INCREMENT PRIMARY KEY,
    order_id bigint NOT NULL,
    user_id bigint NOT NULL,
    product_id bigint NOT NULL,
    product_name varchar(150),
    product_metadata json,
    price_at_order integer,
    quantity integer
);

CREATE TABLE sharing_session_logs (
    sharing_session_id bigint NOT NULL AUTO_INCREMENT PRIMARY KEY,
    host_user_id bigint NOT NULL,
    started_at timestamp,
    ended_at timestamp,
    duration_seconds integer,
    meeting_code varchar(10) UNIQUE,
    session_status varchar(20) DEFAULT 'active',
    created_at timestamp DEFAULT now()
);

-- 외래키 연결
ALTER TABLE profiles ADD FOREIGN KEY (user_id) REFERENCES users (user_id);
ALTER TABLE welfare_cards ADD FOREIGN KEY (user_id) REFERENCES users (user_id);
ALTER TABLE products ADD FOREIGN KEY (platform_id) REFERENCES platforms (platform_id);
ALTER TABLE cart_items ADD FOREIGN KEY (user_id) REFERENCES users (user_id);
ALTER TABLE cart_items ADD FOREIGN KEY (product_id) REFERENCES products (product_id);
ALTER TABLE wishlist_items ADD FOREIGN KEY (user_id) REFERENCES users (user_id);
ALTER TABLE wishlist_items ADD FOREIGN KEY (product_id) REFERENCES products (product_id);
ALTER TABLE favorites ADD FOREIGN KEY (user_id) REFERENCES users (user_id);
ALTER TABLE favorites ADD FOREIGN KEY (product_id) REFERENCES products (product_id);
ALTER TABLE orders ADD FOREIGN KEY (user_id) REFERENCES users (user_id);
ALTER TABLE order_items ADD FOREIGN KEY (order_id) REFERENCES orders (order_id);
ALTER TABLE order_items ADD FOREIGN KEY (user_id) REFERENCES users (user_id);
ALTER TABLE order_items ADD FOREIGN KEY (product_id) REFERENCES products (product_id);
ALTER TABLE sharing_session_logs ADD FOREIGN KEY (host_user_id) REFERENCES users (user_id);