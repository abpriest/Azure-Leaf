create database azure_leaf;

drop table if exists users cascade;
create table users(
    username text not null,
    password text not null,
    is_dm bit not null,
    primary key(username)
);

drop table if exists characters cascade;
create table characters(
    id serial not null,
    username text not null,
    name text not null,
    class text not null,
    race text not null,
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

