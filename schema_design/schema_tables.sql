CREATE TABLE "content".genre (
	id uuid NOT NULL,
	"name" text NULL,
	descrption text NULL,
	created timestamptz NULL,
	modified timestamptz NULL,
	CONSTRAINT genre_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS content.film_work (
    id uuid PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    creation_date DATE,
    rating FLOAT,
    type TEXT not null,
    created timestamp with time zone,
    modified timestamp with time zone
);

CREATE TABLE IF NOT EXISTS content.genre_film_work (
    id uuid PRIMARY KEY,
    genre_id uuid,
    film_work_id uuid, 
    created timestamp with time zone,
    CONSTRAINT fk_genre
      FOREIGN KEY(genre_id) 
        REFERENCES genre(id),
    CONSTRAINT fk_film_work
      FOREIGN KEY(film_work_id) 
        REFERENCES film_work(id)
);


CREATE TABLE IF NOT EXISTS content.person (
    id uuid PRIMARY KEY,
    full_name TEXT NOT NULL,
    created timestamp with time zone,
    modified timestamp with time zone
);

CREATE TABLE IF NOT EXISTS content.person_film_work (
    id uuid PRIMARY KEY,
    film_work_id uuid NOT NULL,
    person_id uuid NOT NULL,
    role TEXT NOT NULL,
    created timestamp with time zone
);

CREATE INDEX film_work_creation_date_idx ON content.film_work(creation_date);


CREATE UNIQUE INDEX film_work_person_idx ON content.person_film_work (film_work_id, person_id);
