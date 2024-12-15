create database if not exists neoed;
use neoed;

create table if not exists users (
    id varchar(50) primary key,
    user_name varchar(100) not null,
    gender enum('Male', 'Female', 'Other'),
	birthdate date,
    user_role enum('Teacher', 'Student', 'Admin'),
    email varchar(200),
    address varchar(200),
    user_passwd varchar(255),
    joined_at datetime
);


create table if not exists permissions (
	id int primary key,
    permission_name varchar(100)
);


create table if not exists users_permissions (
	user_id varchar(50),
    permission_id int,
    constraint pk primary key(user_id, permission_id),
    constraint fk_users_permissions_to_users foreign key (user_id) references users(id),
    constraint fk_users_permissions_to_permissions foreign key (permission_id) references permissions(id)
);


create table if not exists classes (
	id varchar(255) primary key,
    class_name varchar(100) not null,
	semester varchar(50),
    room_id varchar(50),
    subject_name varchar(100),
    class_schedule varchar(100),
    created_at datetime,
    updated_at datetime
);


create table if not exists users_classes (
	user_id varchar(50),
    class_id varchar(255),
    is_teacher bool,
    constraint pk primary key (user_id, class_id),
    constraint fk_users_classes_to_users foreign key (user_id) references users(id),
    constraint fk_users_classes_to_classes foreign key (class_id) references classes(id)
);