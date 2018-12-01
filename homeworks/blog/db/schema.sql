CREATE TABLE IF NOT EXISTS users (
  id       SERIAL PRIMARY KEY,
  username VARCHAR(150) UNIQUE NOT NULL,
  f_name   VARCHAR(255)        NOT NULL,
  l_name   VARCHAR(255)        NOT NULL,
  password VARCHAR(255)        NOT NULL
);

CREATE TABLE IF NOT EXISTS sess (
  id      SERIAL PRIMARY KEY,
  user_id INT       NOT NULL REFERENCES users (id) ON DELETE SET NULL,
  sess    CHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS blogs (
  id            SERIAL PRIMARY KEY,
  title         VARCHAR(255) NOT NULL,
  author_id INT NOT NULL REFERENCES users (id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS blog_posts (
  post_id    INT     NOT NULL REFERENCES posts (id) ON DELETE SET NULL,
  blog_id    INT     NOT NULL REFERENCES blogs (id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS posts (
  id            SERIAL PRIMARY KEY,
  title         VARCHAR(255) NOT NULL,
  text          VARCHAR(255) NOT NULL,
  created       TIMESTAMP DEFAULT now(),
  author_id INT NOT NULL REFERENCES users (id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS comments (
  id         SERIAL PRIMARY KEY,
  text       VARCHAR(255) NOT NULL,
  created    TIMESTAMP DEFAULT now(),
  comment_id INT REFERENCES comments (id),
  post_id    INT          NOT NULL REFERENCES posts (id) ON DELETE SET NULL,
  author_id INT NOT NULL REFERENCES users (id)
);
