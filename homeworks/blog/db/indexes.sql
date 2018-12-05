CREATE INDEX users_username_index ON users (username);
CREATE INDEX users_username_password_index ON users (username, password);

CREATE INDEX sess_user_id_index ON sess (user_id);
CREATE INDEX sess_index ON sess (sess);

CREATE INDEX blogs_thread_id_index ON blogs (author_id);

CREATE INDEX blog_posts_id_index ON blog_posts (post_id);
CREATE INDEX blog_posts_id_index ON blog_posts (blog_id);

CREATE INDEX comments_post_id_index ON comments (post_id);
CREATE INDEX comments_auth_id_index ON comments (author_id);