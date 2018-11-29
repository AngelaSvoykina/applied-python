CREATE INDEX users_id_index
  ON users (id);

CREATE INDEX sess_id_index
  ON sess (id);

CREATE INDEX sess_user_id_index
  ON sess (user_id);

CREATE INDEX blogs_id_index
  ON blogs (id);

CREATE INDEX blogs_thread_id_index
  ON blogs (blog_posts_id);

CREATE INDEX blog_posts_id_index
  ON blog_posts (id);
CREATE INDEX blog_posts_author_id_index
  ON blog_posts (author_id);

CREATE INDEX posts_id_index
  ON posts (id);
CREATE INDEX posts_blog_posts_id_index
  ON posts (blog_posts_id);

CREATE INDEX comments_id_index
  ON comments (id);
CREATE INDEX comments_post_id_index
  ON comments (post_id);
