create database if not exists neoed;
use neoed;


create table if not exists users (
	id varchar(20) primary key,
    user_name varchar(100) not null,
    gender enum('Male', 'Female', 'Other'),
	birthdate date,
    user_role enum('Teacher', 'Student', 'Admin'),
    address varchar(200),
    email varchar(200),
    user_passwd varchar(255),
    joined_at datetime
);


create table if not exists permissions (
	id int primary key,
    permission_name varchar(100)
);


create table if not exists users_permissions (
	user_id varchar(20),
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


create table if not exists students_classes (
	student_id varchar(20),
    class_id varchar(255),
    regular float(2),
    mid_term float(2),
    final_term float(2),
    constraint pk primary key (student_id, class_id),
    constraint fk_students_classes_to_users foreign key (student_id) references users(id),
    constraint fk_students_classes_to_classes foreign key (class_id) references classes(id)
);


create table if not exists teachers_classes (
	teacher_id varchar(20),
    class_id varchar(255),
    constraint pk primary key(teacher_id, class_id),
    constraint fk_teachers_classes_to_users foreign key (teacher_id) references users(id),
    constraint fk_teachers_classes_to_classes foreign key (class_id) references classes(id)
);

create table if not exists assignments (
	id varchar(255) primary key,
    title varchar(255),
    class_id varchar(255),
    author varchar(20) not null,
    descriptions text,
    created_at datetime,
    updated_at datetime,
    start_at datetime,
    end_at datetime,
    constraint fk_assignments_to_classes foreign key (class_id) references classes(id),
    constraint fk_assignments_to_users foreign key (author) references users(id)
);


create table if not exists assgn_attachments(
	id varchar(255) primary key,
    assgn_id varchar(255),
    author varchar(20),
    descriptions text,
	dir varchar(255),
    created_at datetime,
    last_modified datetime,
    constraint fk_assgn_attachments_to_assignments foreign key (assgn_id) references assignments(id),
    constraint fk_assgn_attachments_to_users foreign key (author) references users(id)
);


create table if not exists submissions(
	id varchar(255) primary key,
    student_id varchar(20),
    assgn_id varchar(255),
    class_id varchar(255),
    grade float,
    created_at datetime,
    constraint fk_submissions_to_users foreign key (student_id) references users(id),
    constraint fk_submissions_to_classes foreign key (class_id) references classes(id),
    constraint fk_submissions_to_students_classes foreign key (student_id, class_id) references students_classes(student_id, class_id)
);


create table if not exists submission_attachments(
	id varchar(255) primary key,
    submission_id varchar(255),
    dir varchar(255),
    constraint fk_to_submissions foreign key (submission_id) references submissions(id)
);


create table if not exists posts(
	id varchar(255) primary key,
    title varchar(255),
    class_id varchar(255),
    author varchar(20),
    created_at datetime,
    updated_at datetime,
    content text,
    constraint fk_posts_to_classes foreign key (class_id) references classes(id),
    constraint fk_posts_to_users foreign key (author) references users(id)
);


create table if not exists post_attachments(
	id varchar(255) primary key,
    post_id varchar(255),
    author varchar(20),
    descriptions text,
    dir varchar(255),
    created_at datetime,
    updated_at datetime,
    constraint fk_post_attachments_to_posts foreign key (post_id) references posts(id),
    constraint fk_post_attachments_to_users foreign key (author) references users(id)
);


create table if not exists comments(
	id varchar(255) primary key,
    post_id varchar(255),
    author varchar(20),
    content text,
    created_at datetime,
    updated_at datetime,
    upvote int,
    downvote int,
    constraint fk_comments_to_users foreign key (author) references users(id),
    constraint fk_comments_to_posts foreign key (post_id) references posts(id)
);


create table if not exists attendence_sessions(
	id varchar(255) primary key,
    class_id varchar(255),
    author varchar(20),
    for_date date,
    created_at datetime,
    ended_at datetime,
    constraint fk_attendence_sessions_to_users foreign key (author) references users(id),
    constraint fk_attendence_sessions_to_classes foreign key (class_id) references classes(id)
);


create table if not exists students_attendences(
	student_id varchar(20),
    attendence_id varchar(255),
    present enum('Absent', 'Present', 'Absent with permisison'),
    created_at datetime,
    constraint pk primary key (student_id, attendence_id),
    constraint fk_students_attendences_to_attendence_sessions foreign key (attendence_id) references attendence_sessions(id),
    constraint fk_students_attendences_to_users foreign key (student_id) references users(id)
);


create table if not exists absent_request(
	id varchar(255) primary key,
    student_id varchar(20),
    class_id varchar(255),
    for_date date,
    created_at datetime,
	reason text,
    attachments varchar(255),
    _status enum('Pending', 'Accepted', 'Rejected'),
    constraint fk_absent_request_to_users foreign key (student_id) references users(id),
    constraint fk_absent_request_to_classes foreign key (class_id) references classes(id)
);


create table if not exists announcements(
	id varchar(255) primary key,
    author varchar(20),
    class_id varchar(255),
    content text,
    created_at datetime,
    updated_at datetime,
    constraint fk_announcement_to_classes foreign key (class_id) references classes(id),
    constraint fk_announcement_to_users foreign key (author) references users(id)
);

create table if not exists announce_receiver(
	announce_id varchar(255),
    receiver_id varchar(20),
    seen_at datetime,
    constraint pk primary key (announce_id, receiver_id),
    constraint fk_announce_receiver_to_users foreign key (receiver_id) references users(id),
    constraint fk_announce_receiver_to_announcements foreign key (announce_id) references announcements(id)
);
