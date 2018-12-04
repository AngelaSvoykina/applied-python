# Задание на оптимизацию запросов, разбор нескольких запросов с помощью explain
 
## Разбор запросов
```sql
EXPLAIN SELECT id FROM users WHERE username='ora994';
```
Получаем:
           id: 1  
           select_type: SIMPLE  
        table: users  
         type: const  
possible_keys: username,users_username_index  
          key: username  
      key_len: 152  
          ref: const  
         rows: 1  
        Extra: Using index
```sql
EXPLAIN SELECT * FROM sess WHERE user_id=5982;
```
Получаем:
            id: 1  
  select_type: SIMPLE  
        table: sess  
         type: ref  
possible_keys: sess_user_id_index  
          key: sess_user_id_index  
      key_len: 4  
          ref: const  
         rows: 1  
        Extra:   
 
Здесь оптимизировано с помощью индекса sess_user_id_index.
```sql
EXPLAIN SELECT id FROM users WHERE id = 1900;
```
Получаем:  
           id: 1  
  select_type: SIMPLE  
        table: users  
         type: const  
possible_keys: PRIMARY,id  
          key: PRIMARY  
      key_len: 8  
          ref: const  
         rows: 1  
        Extra: Using index  

Здесь можно заметить, что индекс users_id_index не нужен, так как уже есть встроенный индекс по id. (я его и подобные убрала)  

Эти запросы оптимизированы с помощью индексов blogs_thread_id_index, blog_posts_id_index:
```sql
EXPLAIN SELECT id, title FROM blogs WHERE blogs.author_id = 5079;
```
Получаем:  
           id: 1  
  select_type: SIMPLE  
        table: blogs  
         type: ref  
possible_keys: blogs_thread_id_index  
          key: blogs_thread_id_index  
      key_len: 4  
          ref: const  
         rows: 1  
        Extra  : 
```sql
EXPLAIN SELECT * from blog_posts WHERE post_id = 20000;  
```
Получаем:  
           id: 1  
  select_type: SIMPLE  
        table: blog_posts  
         type: ref  
possible_keys: blog_posts_id_index  
          key: blog_posts_id_index  
      key_len: 4  
          ref: const  
         rows: 1  
        Extra:  


## Оптимизация запросов

Среди запросов наиболее сложным является запрос на получение всех комментариев для 1 или нескольких пользователей в указанном блоге.


```sql
 EXPLAIN SELECT c.text, c.created, c.author_id, c.post_id, c.comment_id FROM comments AS c
 JOIN posts  AS p ON c.post_id = p.id JOIN blog_posts AS b_p ON p.id = b_p.post_id 
 WHERE blog_id = 200 AND (c.author_id = 1996 OR c.author_id=1997) ORDER BY c.id;
```

Выполняя его с EXPLAIN, получаем:  
           id: 1  
  select_type: SIMPLE  
        table: с  
         type: index  
possible_keys: NULL  
          key: PRIMARY  
      key_len: 8  
          ref: NULL  
         rows: 18624  
        Extra: Using where  
*************************** 2. row ***************************  
           id: 1  
  select_type: SIMPLE  
        table: p  
         type: eq_ref  
possible_keys: PRIMARY,id  
          key: PRIMARY  
      key_len: 8  
          ref: sys_base.c.post_id  
         rows: 1  
        Extra: Using where; Using index  
*************************** 3. row ***************************  
           id: 1  
  select_type: SIMPLE  
        table: b_p  
         type: ref  
possible_keys: blog_posts_id_index  
          key: blog_posts_id_index  
      key_len: 4  
          ref: sys_base.p.id  
         rows: 1  
        Extra: Using where  
3 rows in set (0.00 sec)  

           
Очевидно, что первая часть запроса выглядит крайне неоптимизированно: в качестве индекса используется PRIMARY, тип index, значит сканируется все дерево индексов, еще и строчек на выходе 10031.

Добавим индексы по post_id, author_id:  
id: 1  
  select_type: SIMPLE  
        table: c  
         type: range  
possible_keys: comments_post_id_index,comments_auth_id_index  
          key: comments_auth_id_index  
      key_len: 4  
          ref: NULL  
         rows: 22   
        Extra: Using where; Using filesort  
*************************** 2. row ***************************  
           id: 1  
  select_type: SIMPLE  
        table: p  
         type: eq_ref  
possible_keys: PRIMARY,id  
          key: PRIMARY  
      key_len: 8  
          ref: sys_base.c.post_id  
         rows: 1  
        Extra: Using where; Using index  
*************************** 3. row ***************************  
           id: 1  
  select_type: SIMPLE  
        table: b_p  
         type: ref  
possible_keys: blog_posts_id_index  
          key: blog_posts_id_index  
      key_len: 4  
          ref: sys_base.p.id  
         rows: 1  
        Extra: Using where  
3 rows in set (0.00 sec)  

Теперь уже получше. Используется созданный нами индекс, строчек уже 21, а не 18624.



