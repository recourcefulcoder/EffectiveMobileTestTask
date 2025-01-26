![check-commit](https://github.com/recourcefulcoder/EffectiveMobileTestTask/actions/workflows/commit-check.yml/badge.svg)

# EffectiveMobileTestTask

Инструкции по запуску проекта в dev-режиме

1. Создайте виртуальное окружение и активируйте его; установите зависимости
```bash
python -m venv venv
source venv/bin/activate
pip install requirements/dev.txt
```
2. Создайте файл .env в главной папке и установите 
по вашему усмотрению значения перемменных LANGUAGE_CODE, DEBUG и SECRET_KEY:

```bash
touch .env
```
Пример см. в файле .env.example

3. Перейдите в папку проекта и создайте базу данных; установите фикстуры 

```bash
cd dionysus
python manage.py migrate
python manage.py loaddata fixtures/fixture.json
```

3. Запустите сервер в dev-режиме
```bash
python manage.py runserver 
```
