DROP DATABASE IF EXISTS `husky-buddy-orig`;
CREATE DATABASE `husky-buddy-orig`;
USE `husky-buddy-orig`;


CREATE TABLE IF NOT EXISTS husky_user (
  student_id INT NOT NULL AUTO_INCREMENT,
  first_name varchar(50) NOT NULL,
  last_name varchar(50) NOT NULL,
  email varchar(75) NOT NULL,
  year ENUM('1st', '2nd', '3rd', '4th', '5th', 'Grad') NOT NULL,
  verification_status varchar(20),
  PRIMARY KEY (student_id),
  UNIQUE INDEX (email)


);
-- Husky Matching Ids
CREATE TABLE IF NOT EXISTS husky_match (
    match_id INT NOT NULL AUTO_INCREMENT,
    student1_id INT NOT NULL,
    student2_id INT NOT NULL,
    status ENUM('active', 'pending', 'removed', 'completed') NOT NULL,
    matched_on datetime NOT NULL,
    PRIMARY KEY (match_id),
    FOREIGN KEY (student1_id) REFERENCES husky_user(student_id),
    FOREIGN KEY (student2_id) REFERENCES husky_user(student_id),
    UNIQUE INDEX unique_pair (student1_id, student2_id)
);
-- Student Interest Tags
CREATE TABLE IF NOT EXISTS interest_tag(
   tag_id   INT NOT NULL AUTO_INCREMENT,
   tag_type VARCHAR(100) NOT NULL UNIQUE,
   PRIMARY KEY (tag_id)
);
-- Student Interests
CREATE TABLE IF NOT EXISTS student_interest(
   student_id  INT NOT NULL,
   interest_id INT NOT NULL,
   PRIMARY KEY (student_id, interest_id),
   FOREIGN KEY (student_id) REFERENCES husky_user(student_id) ON DELETE CASCADE,
   FOREIGN KEY (interest_id) REFERENCES interest_tag(tag_id) ON DELETE CASCADE
);
-- Majors
CREATE TABLE majors (
   major_id INT AUTO_INCREMENT,
   major_name VARCHAR(100) NOT NULL UNIQUE,
   PRIMARY KEY(major_id)
);
-- Major Tags
CREATE TABLE student_major_tags(
   student_id INT NOT NULL,
   major_id INT NOT NULL,
   PRIMARY KEY (student_id, major_id),
   FOREIGN KEY (student_id) REFERENCES husky_user(student_id) ON DELETE CASCADE,
   FOREIGN KEY (major_id) REFERENCES majors(major_id) ON DELETE CASCADE
);


-- Campus Spot
CREATE TABLE campus_spot(
   spot_id INT NOT NULL AUTO_INCREMENT,
   spot_name varchar(100),
   location varchar(100),
   PRIMARY KEY (spot_id)
);


-- Student Spots
CREATE TABLE student_spots(
   student_id INT NOT NULL,
   spot_id INT NOT NULL,
   PRIMARY KEY (student_id, spot_id),
   FOREIGN KEY (student_id) REFERENCES husky_user(student_id) ON DELETE CASCADE,
   FOREIGN KEY (spot_id) REFERENCES campus_spot(spot_id) ON DELETE CASCADE
);


-- icebreaker prompt
CREATE TABLE IF NOT EXISTS icebreaker_prompt (
   prompt_id INT NOT NULL AUTO_INCREMENT,
   prompt_text TEXT NOT NULL,
   category VARCHAR(50),
   PRIMARY KEY (prompt_id)
);


-- match icebreaker
CREATE TABLE IF NOT EXISTS match_icebreaker (
   match_id INT NOT NULL,
   prompt_id INT NOT NULL,
   shown_at DATETIME DEFAULT NOW(),
   PRIMARY KEY (match_id, prompt_id),
   FOREIGN KEY (match_id) REFERENCES husky_match(match_id) ON DELETE CASCADE,
   FOREIGN KEY (prompt_id) REFERENCES icebreaker_prompt(prompt_id) ON DELETE CASCADE
);


-- student availability
CREATE TABLE IF NOT EXISTS student_availability (
   availability_id INT NOT NULL AUTO_INCREMENT,
   student_id INT NOT NULL,
   day_of_week ENUM('Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday') NOT NULL,
   start_time TIME NOT NULL,
   end_time TIME NOT NULL,
   PRIMARY KEY (availability_id),
   FOREIGN KEY (student_id) REFERENCES husky_user(student_id) ON DELETE CASCADE,
   UNIQUE INDEX unique_slot (student_id, day_of_week, start_time, end_time)
);


-- meetup photo
CREATE TABLE IF NOT EXISTS meetup_photo (
   photo_id INT NOT NULL AUTO_INCREMENT,
   match_id INT NOT NULL,
   uploaded_by INT NOT NULL,
   photo_url VARCHAR(255) NOT NULL,
   caption TEXT,
   uploaded_at DATETIME DEFAULT NOW(),
   PRIMARY KEY (photo_id),
   FOREIGN KEY (match_id) REFERENCES husky_match(match_id) ON DELETE CASCADE,
   FOREIGN KEY (uploaded_by) REFERENCES husky_user(student_id) ON DELETE CASCADE
);


-- match feedback
CREATE TABLE IF NOT EXISTS match_feedback (
   feedback_id INT NOT NULL AUTO_INCREMENT,
   match_id INT NOT NULL,
   student_id INT NOT NULL,
   rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
   comment TEXT,
   created_at DATETIME DEFAULT NOW(),
   PRIMARY KEY (feedback_id),
   FOREIGN KEY (match_id) REFERENCES husky_match(match_id) ON DELETE CASCADE,
   FOREIGN KEY (student_id) REFERENCES husky_user(student_id) ON DELETE CASCADE,
   UNIQUE INDEX one_review_per_match (match_id, student_id)
);


-- admin
CREATE TABLE IF NOT EXISTS  admin(
   admin_id INT NOT NULL AUTO_INCREMENT,
   name VARCHAR(100) NOT NULL,
   email VARCHAR(100) NOT NULL,
   role VARCHAR(100) NOT NULL,
   PRIMARY KEY(admin_id)
);
-- create report
CREATE TABLE IF NOT EXISTS flag_report(
   report_id INT NOT NULL AUTO_INCREMENT,
   reporter_id INT NOT NULL,
   reported_id INT NOT NULL,
   reason text,
   status varchar(20),
   created_at TIMESTAMP,
   PRIMARY KEY (report_id),
   FOREIGN KEY (reporter_id) REFERENCES husky_user(student_id),
   FOREIGN KEY (reported_id) REFERENCES husky_user(student_id)
);




-- moderation action
CREATE TABLE  IF NOT EXISTS moderation_action(
   action_id INT AUTO_INCREMENT,
   admin_id INT,
   user_id INT,
   report_id INT,
   action_type ENUM('removed', 'kept', 'under review', 'warning issued'),
   action_date TIMESTAMP,
   notes TEXT,
   PRIMARY KEY (action_id),
   FOREIGN KEY (admin_id) REFERENCES admin(admin_id),
   FOREIGN KEY (user_id) REFERENCES husky_user(student_id),
   FOREIGN KEY (report_id) REFERENCES flag_report(report_id)
);

CREATE TABLE IF NOT EXISTS meetup (
    meetup_id INT NOT NULL AUTO_INCREMENT,
    match_id INT NOT NULL,
    meetup_status ENUM('scheduled', 'completed', 'cancelled') NOT NULL,
    meetup_date DATETIME NOT NULL,
    spot_id INT,
    PRIMARY KEY (meetup_id),
    FOREIGN KEY (match_id) REFERENCES husky_match(match_id) ON DELETE CASCADE,
    FOREIGN KEY (spot_id) REFERENCES campus_spot(spot_id)
);

CREATE TABLE IF NOT EXISTS chat_message (
    message_id   INT NOT NULL AUTO_INCREMENT,
    match_id     INT NOT NULL,
    sender_id    INT NOT NULL,
    content      TEXT NOT NULL,
    sent_at      DATETIME DEFAULT NOW(),
    PRIMARY KEY (message_id),
    FOREIGN KEY (match_id)  REFERENCES husky_match(match_id) ON DELETE CASCADE,
    FOREIGN KEY (sender_id) REFERENCES husky_user(student_id) ON DELETE CASCADE
);
-- ==================================================
-- Add in Northeastern majors for the dropdown
INSERT INTO majors (major_name) 
VALUES
   ('Africana Studies'),
   ('American Sign Language-English Interpreting'),
   ('Advanced Manufacturing Systems'),
   ('Analytics'),
   ('Applied Physics'),
   ('Architectural Studies'),
   ('Architecture'),
   ('Art'),
   ('Behavioral Neuroscience'),
   ('Biochemistry'),
   ('Bioengineering'),
   ('Biology'),
   ('Biomedical Physics'),
   ('Biotechnology'),
   ('Business Administration'),
   ('Cell and Molecular Biology'),
   ('Chemical Engineering'),
   ('Chemistry'),
   ('Civil Engineering'),
   ('Communication and Media Studies'),
   ('Communication Studies'),
   ('Computer Engineering'),
   ('Computer Science'),
   ('Cultural Anthropology'),
   ('Cybersecurity'),
   ('Data Science'),
   ('Design'),
   ('Digital Communication and Media'),
   ('Ecology and Evolutionary Biology'),
   ('Economics'),
   ('Electrical and Computer Engineering'),
   ('Electrical Engineering'),
   ('English'),
   ('Environmental and Sustainability Sciences'),
   ('Environmental Engineering'),
   ('Environmental Studies'),
   ('Finance and Accounting Management'),
   ('Game Art and Animation'),
   ('Game Design'),
   ('Global Asian Studies'),
   ('Health Science'),
   ('Healthcare Administration'),
   ('History'),
   ('History Culture and Law'),
   ('Human Services'),
   ('Industrial Engineering'),
   ('Information Technology'),
   ('Interdisciplinary Studies'),
   ('International Affairs'),
   ('International Business'),
   ('Journalism'),
   ('Landscape Architecture'),
   ('Linguistics'),
   ('Management'),
   ('Marine Biology'),
   ('Mathematics'),
   ('Mechanical Engineering'),
   ('Mechatronics'),
   ('Media and Screen Studies'),
   ('Media Arts'),
   ('Music'),
   ('Nursing'),
   ('Performance and Extended Realities'),
   ('Pharmaceutical Sciences'),
   ('Pharmacy Studies'),
   ('Philosophy'),
   ('Physics'),
   ('Political Science'),
   ('Politics Philosophy and Economics'),
   ('Project Management'),
   ('Psychology'),
   ('Public Health'),
   ('Public Relations'),
   ('Religious Studies'),
   ('Sociology'),
   ('Spanish'),
   ('Speech-Language Pathology and Audiology'),
   ('Studio Art'),
   ('Theatre'),
   ('Undeclared');


INSERT INTO interest_tag (tag_type) 
VALUES
   ('Sports and Fitness'),
   ('Arts and Creativity'),
   ('Tech'),
   ('Gaming'),
   ('Food and Social'),
   ('Careers and Academic'),
   ('Entertainment and Culture'),
   ('Wellness and Lifestyle');


-- =======================================
-- Sample Data
-- =======================================
-- User Data
INSERT INTO husky_user(`first_name`, `last_name`, `email`, `year`, `verification_status`)
VALUES
('Brandon', 'Heller', 'he.bra@northeastern.edu','1st', 'verified'),
('Natalie', 'Frost','fro.nat@northeastern.edu', '2nd', 'verified' ),
('Sarah', 'Miller','miller.sa@northeastern.edu','3rd','pending'),
('Ken', 'Carson', 'carson.ken@northeastern.edu', '4th', 'suspended');


-- Match Data
INSERT INTO husky_match(`student1_id`,`student2_id`, `status`,`matched_on`)
VALUES
(1,3,'active','2026-02-10');
-- Major Data
INSERT INTO student_major_tags(`student_id`, `major_id`)
VALUES
(1,26),
(1,15),
(2,56),
(2,26),
(3,26),
(3,15);


-- Interest Data
INSERT INTO student_interest(`student_id`, `interest_id`)
VALUES(1,1),
(1,6),
(2,3),
(2,6),
(3,1);


INSERT INTO campus_spot(`spot_name`,`location`)
VALUES
('Marino Recreation Center','369 Huntington Ave'),
('Snell Library','360 Huntington Ave'),
('Tatte Bakery','360 Huntington Ave'),
('Prudential Center','800 Boylston St'),
('Kigo Kitchen','360 Huntington Ave');


-- =======================================
-- Additional Sample Data for Remaining Tables
-- =======================================


-- Student Spots
INSERT INTO student_spots (student_id, spot_id)
VALUES
   (1, 1), -- Brandon likes Marino Recreation Center
   (2, 2), -- Natalie likes Snell Library
   (3, 3); -- Sarah likes Tatte Bakery


-- Icebreaker Prompts
INSERT INTO icebreaker_prompt (prompt_text, category)
VALUES
   ('What is your favorite place to study on the Boston campus?', 'Campus Life'),
   ('What club, sport, or activity at Northeastern have you enjoyed the most so far?', 'Student Life'),
   ('If you could grab food anywhere near campus right now, where would you go?', 'Food');


-- Match Icebreaker
INSERT INTO match_icebreaker (match_id, prompt_id, shown_at)
VALUES
   (1, 1, '2026-02-10 12:00:00'),
   (1, 2, '2026-02-10 12:05:00'),
   (1, 3, '2026-02-10 12:10:00');


-- Student Availability
INSERT INTO student_availability (student_id, day_of_week, start_time, end_time)
VALUES
   (1, 'Monday', '14:00:00', '16:00:00'),
   (2, 'Wednesday', '11:00:00', '13:00:00'),
   (3, 'Friday', '15:30:00', '18:00:00');


-- Meetup Photo
INSERT INTO meetup_photo (match_id, uploaded_by, photo_url, caption, uploaded_at)
VALUES
   (1, 1, 'https://huskybuddy.app/photos/marino-meetup-1.jpg', 'First meetup after working out at Marino.', '2026-02-10 17:30:00'),
   (1, 3, 'https://huskybuddy.app/photos/tatte-chat-1.jpg', 'Grabbed coffee and talked about classes at Tatte.', '2026-02-10 18:15:00');


-- Match Feedback
INSERT INTO match_feedback (match_id, student_id, rating, comment, created_at)
VALUES
   (1, 1, 5, 'Great match. Easy to talk to and we had a lot in common as Northeastern students.', '2026-02-11 10:00:00'),
   (1, 3, 4, 'Really positive experience. Would love better overlap in availability next time.', '2026-02-11 10:15:00');


-- Admin
INSERT INTO admin (name, email, role)
VALUES
   ('Adam Johnson', 'johnson.ad@northeastern.edu', 'IT admin'),
   ('Johanna Park', 'park.jo@northeastern.edu', 'Data lead');


-- Flag Report
INSERT INTO flag_report (reporter_id, reported_id, reason, status, created_at)
VALUES
   (2, 3, 'Missed meetup without sending a message in advance.', 'open', '2026-03-01 09:30:00'),
   (1, 2, 'Profile information seemed incomplete and possibly misleading.', 'reviewed', '2026-03-02 14:20:00');


-- Moderation Action
INSERT INTO moderation_action (admin_id, user_id, report_id, action_type, action_date, notes)
VALUES
   (1, 3, 1, 'warning issued', '2026-03-01 12:00:00', 'Sent reminder about meetup etiquette and communication expectations.'),
   (2, 2, 2, 'under review', '2026-03-02 16:00:00', 'Reviewed reported profile and requested clarification from the user.');




