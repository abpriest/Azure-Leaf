-- RESTRUCTURED 12/4/16

create database azure_leaf;
\c azure_leaf;

drop table if exists users cascade;
drop table if exists campaigns cascade;
drop sequence campaigns_id_seq;
drop table if exists messages cascade;
drop sequence messages_id_seq;
drop table if exists posts cascade;
drop sequence posts_id_seq;
drop table if exists characters cascade;
drop sequence characters_id_seq cascade;
drop extension pgcrypto;
drop role if exists azure cascade;

create extension pgcrypto;

create table users(
    username text not null,
    password text not null,
    is_dm bit not null,
    campaign int not null,
    primary key(username)
);

create table campaigns(
    id serial not null,
    title text not null,
    dm text not null,
    primary key(id),
    foreign key (dm) references users(username)
);

create table characters(
    -- Static data
    id serial not null,
    username text not null,
    name text not null,
    class text not null,
    race text not null,
    campaign int not null,
    
    -- Variant data
    level int not null,
    
    --- Ability Scores
    strength int not null,
    dexterity int not null,
    constitution int not null,
    intelligence int not null,
    wisdom int not null,
    charisma int not null,
    
    --- Skill proficiencies
    ---- Strength
    Athletics bit not null,
    
    ---- Dexterity
    Acrobatics bit not null,
    Sleight_of_Hand bit not null,
    Stealth bit not null,
    
    ---- Intelligence
    Arcana bit not null,
    History bit not null,
    Investigation bit not null,
    Nature bit not null,
    Religion bit not null,
    
    ---- Wisdom
    Animal_Handling bit not null,
    Insight bit not null,
    Medicine bit not null,
    Perception bit not null,
    Survival bit not null,
    
    ---- Charisma
    Deception bit not null,
    Intimidation bit not null,
    Performance bit not null,
    Persuasion bit not null,
    
    -- add more fields as needed
    -- (e.g. ability scores, levels, DMPC switch/bool)
    primary key(id),
    foreign key(username) references users(username)
);

create table posts(
    id serial not null,
    author text not null,
    title text not null,
    subtitle text not null,
    body text not null,
    img_url text,
    campaign int not null,
    date_posted timestamp not null,
    primary key(id),
    foreign key(author) references users(username),
    foreign key(campaign) references campaigns(id)
);

create table messages(
    id serial not null,
    author text not null,
    related_post int not null,
    body text not null,
    date_posted timestamp not null,
    primary key(id),
    foreign key(author) references users(username),
    foreign key(related_post) references posts(id)
);

INSERT INTO users (username, password, is_dm, campaign) VALUES ('default_user', crypt('12345', gen_salt('bf')), '1', 0);
INSERT INTO users (username, password, is_dm, campaign) VALUES ('demogm', crypt('demo', gen_salt('bf')), '1', 0);

INSERT INTO campaigns (id, title, dm) VALUES (0, 'default campaign', 'default_user');
INSERT INTO campaigns (title, dm) VALUES ('demo campaign', 'demogm');
ALTER TABLE users ADD CONSTRAINT users_foreign_key_fk1 foreign key(campaign) references campaigns(id);

INSERT INTO posts (campaign, author, title, subtitle, body, img_url, date_posted) VALUES (1, 'demogm', 'This is a Proof of Concept', 'A magical place that is unique from the other one.', 'You can do different stuff here independently of the other one. Demoes are hard.', 'http://www.desktopwallpaperhd.net/wallpapers/22/9/fantasy-background-wallpaper-space-222489.jpg', current_timestamp);
INSERT INTO posts (campaign, author, title, subtitle, body, img_url, date_posted) VALUES (1, 'demogm', 'This is a demo post', 'It is meant for a demo campaign made by a demogm for a demouser to see and talk to himself about', 'So do something, I guess.', 'https://images3.alphacoders.com/261/thumb-1920-26105.jpg', current_timestamp);
INSERT INTO posts (campaign, author, title, subtitle, body, img_url, date_posted) VALUES (0, 'default_user', 'Welcome to The Azure Leaf!', 'Sit ye down and let me tell you how things work `round these parts', 'If ye be an adventuring type, ye`ll be wantin` to join up with a group. If your leader hain`t made a group for you yet, go an` holler at `em yerself. Once you`re in a group, you should tell us all a bit about yourself on that sheet o`er there. Good Luck, Adventurer!', 'https://c1.staticflickr.com/5/4049/4380838791_b7a5b00220_b.jpg', current_timestamp);

CREATE USER azure with password '123';
GRANT INSERT, SELECT, UPDATE ON users to azure;
GRANT INSERT, SELECT, UPDATE ON characters to azure;
GRANT INSERT, SELECT ON posts to azure;
GRANT INSERT, SELECT ON messages to azure;
GRANT INSERT, SELECT on campaigns to azure;
GRANT USAGE, SELECT ON characters_id_seq to azure;
GRANT USAGE, SELECT ON messages_id_seq to azure;
GRANT USAGE, SELECT on campaigns_id_seq to azure;
GRANT USAGE, SELECT ON posts_id_seq to azure;
