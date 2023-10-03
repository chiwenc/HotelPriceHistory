create table history (
	id int auto_increment primary key,
    hotel_name varchar(255),
    checkin_date date,
    checkout_date date,
	agency varchar(255),
    twd_price int,
    crawl_time datetime   
);
create table all_history (
    id int auto_increment primary key,
    region varchar(255),
    hotel_name varchar(255),
    twd_price int,
    crawl_time datetime
);
create table user_request (
    id int auto_increment primary key,
    user_id int,
    hotel_name varchar(255),
    checkin_date date,
    checkout_date date,
);
create table user_info (
    id int auto_increment primary key,
    name varchar(255),
    email varchar(255),
    password varchar(255)
)
