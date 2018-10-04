Прикладной Python
=================

Это основной репозиторий курса.
Пожалуйста, присылайте мердж-реквесты только с исправлениями, но не со сделанными домашними заданиями.

## Для работы с материалами курса необходимо
* Установить Python [отсюда](https://www.python.org)
* Установить git и склонировать репозиторий

> git clone https://github.com/VadimPushtaev/applied-python.git

* В папке с репозиторием создать виртуальное окружение и активировать его

> python3.6 -m venv venv

> source venv/bin/activate

* Установить jupyter и запустить (браузер должен открыться автоматически)

> pip install notebook

> jupyter-notebook

* Запуск тестов в домашке

> python -m unittest -v tests.test_grep

* Работа с гитом

> git add .

Закоммитить изменения 
> git commit -m "Add invert and ignore_case"

Отправить коммиты в репозиторий на сайте
> git push