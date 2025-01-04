create database if not exists neoed;
use neoed;

create table if not exists users (
	id varchar(255) primary key,
    username varchar(50) collate utf8mb4_bin unique,
    fullname varchar(100) not null,
    gender enum('Male', 'Female', 'Other'),
	birthdate date,
    role enum('Teacher', 'Student'),
    email varchar(200),
    address varchar(200),
    hashed_password varchar(255),
    joined_at datetime
);


create table if not exists classes (
	id varchar(255) primary key,
    class_name varchar(100) not null,
    subject_name varchar(100),
    class_schedule varchar(100),
    description varchar(255),
    created_at datetime,
    updated_at datetime,
    owner_id varchar(255),
    hashed_password varchar(255),
    require_password bool,
    constraint fk_classes_to_users foreign key (owner_id) references users(id)
);


create table if not exists users_classes (
	user_id varchar(255),
    class_id varchar(255),
    joined_at datetime,
    constraint pk primary key (user_id, class_id),
    constraint fk_users_classes_to_users foreign key (user_id) references users(id),
    constraint fk_users_classes_to_classes foreign key (class_id) references classes(id) on delete cascade
);