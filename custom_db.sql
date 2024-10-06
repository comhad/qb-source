CREATE TABLE sprites (
    id integer primary key asc,
    imagecontents text not null,
    name text,
    expression text,
);
CREATE TABLE aliases (
    id integer primary key asc,
    spritename text,
    alias text,
);