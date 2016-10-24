create database azure_leaf;
\c azure_leaf;

create extension pgcrypto;

drop table if exists users cascade;
create table users(
    username text not null,
    password text not null,
    is_dm bit not null,
    primary key(username)
);

drop table if exists characters cascade;
create table characters(
    -- Static data
    id serial not null,
    username text not null,
    name text not null,
    class text not null,
    race text not null,
    
    -- Variant data
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
    Sleight of Hand bit not null,
    Stealth bit not null,
    
    ---- Intelligence
    Arcana bit not null,
    History bit not null,
    Investigation bit not null,
    Nature bit not null,
    Religion bit not null,
    
    ---- Wisdom
    Animal Handling bit not null,
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

drop table if exists posts cascade;
create table posts(
    id serial not null,
    author text not null,
    title text not null,
    body text not null,
    date_posted timestamp not null,
    primary key(id),
    foreign key(author) references users(username)
);

drop table if exists messages cascade;
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

DROP USER IF EXISTS azure;
CREATE USER azure with password '123';
GRANT INSERT, SELECT ON users to azure;
