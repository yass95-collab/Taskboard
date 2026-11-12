CREATE TABLE IF NOT EXISTS tasks (
  id          SERIAL PRIMARY KEY,
  title       VARCHAR(255) NOT NULL CHECK (char_length(trim(title)) > 0),
  completed   BOOLEAN NOT NULL DEFAULT FALSE,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

INSERT INTO tasks (title, completed) VALUES
  ('Préparer la soutenance', FALSE),
  ('Écrire le Dockerfile', FALSE),
  ('Configurer PostgreSQL', TRUE);