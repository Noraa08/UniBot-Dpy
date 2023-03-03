CREATE TABLE Guilds (
   id BIGINT NOT NULL,
   prefixes TEXT[],
   language TEXT,
   PRIMARY KEY (id)
);

CREATE TABLE Tags (
   id BIGINT NOT NULL,
   name TEXT,
   owner_id BIGINT,
   position INT,
   PRIMARY KEY (id)
);