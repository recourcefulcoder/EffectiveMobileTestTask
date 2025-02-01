![check-commit](https://github.com/recourcefulcoder/EffectiveMobileTestTask/actions/workflows/commit-check.yml/badge.svg)

# EffectiveMobileTestTask

### Инструкции по запуску проекта в dev-режиме

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
Пример см. в файле .env.example; DEBUG должен иметь значение True!

3. Перейдите в папку проекта и создайте базу данных; установите фикстуру 

```bash
cd dionysus
python manage.py migrate
python manage.py loaddata fixtures/fixture.json
```

3. Запустите сервер в dev-режиме
```bash
python manage.py runserver 
```

### Инструкции по запуску тестирования:

Для тестов используются стандартнеы инструменты Django - для запуска воспользуйтесь командой
[test](https://docs.djangoproject.com/en/5.1/topics/testing/overview/#running-tests)
утилиты manage.py:
```bash
python manage.py test
```

### Инструкция по применению

Наобр всех доступных действий следующий:
+ просмотр всех доступных заказов (а также поиск определённого по id/статусу)
+ просмотр деталей по некоторому заказу
+ редактирование заказа
+ удаление заказа
+ просмотр общей выручки по всем заказам в БД

Приложение локализовано, т.е. содержит перевод на русский и английский языки. Выбор языка Django
осуществляет в соответствии со значением переменной среды 
[LANGUAGE_CODE](https://docs.djangoproject.com/en/5.1/ref/settings/#language-code) 
('ru' для русского (без кавычек), 'en' для английского).

На главной странице приложения содержится список всех заказов; для каждого заказа справа присутствуют
три кнопки-манипулятора:
1. голубая, со значком восклицательного знака, показывает подробную информацию
о заказе, включая список блюд и их стоимость
2. синия, с карандашом в квадрате, перенаправляет на страницу для редактирования выбранного заказа
3. красная ответственна за удаление - вызывает всплывающее окно-подтверждение и 
удаляет заказ, если пользователь подтвердил своё намерение

Кроме того, на главной странице содержится строка для поиска заказов - в неё можно внести либо 
id искомого заказа, либо статус, после чего при нажатии на кнопку "поиск" страница обновляется, 
показывая выбранные заказы.

Для добавления заказа необходимо нажать кнопку "добавить заказ" в меню навигационной полоски 
сверху

Для просмотра выручки служит кнопка "Посмотреть выручку" там же, на верхней панели навигации

### Документация

Вся логика системы содержится в трёх приложениях: orders, api и дополнительное utils
> **orders** - содержит view, модели и формы, которые необходимы для существования 
> основного функционала системы   

> **api** - view/serializers, логику API, написано с применением 
> [Django REST Framework](https://www.django-rest-framework.org/)

> **utils** - вспомагательные функции/формы, которые не относятся ни к какому блоку
> системы непосредственно

##### orders-app
Обрабатывает пять endpoint'ов - на создание, редактирование, удаление и просмотр заказов, 
а также просмотр общей выручки. 

VIEW-функции

Из них только одна - функция, остальные endpoint'ы обрабатываются [Class-based view](https://docs.djangoproject.com/en/5.1/ref/class-based-views/#built-in-class-based-views-api)
* [delete_order(request, pk)](https://github.com/recourcefulcoder/EffectiveMobileTestTask/blob/7e02f2a8ff4e7212054f5d49c6eec20f26921f49/dionysus/orders/views.py#L26) - 
удаление заказа с данным pk



* [class OrderList](https://github.com/recourcefulcoder/EffectiveMobileTestTask/blob/7e02f2a8ff4e7212054f5d49c6eec20f26921f49/dionysus/orders/views.py#L36) - 
наследует стандартный django ListView, отображает все заказы в соответствии с параметрами их поиска. 
  + def get_queryset(self) - собирает queryset для показа в соответствии с параметрами запроса,
  реализуя таким образом функцию поиска на главной странице. Запрос передаётся в URL-запросе параметром q
  и, в соответствии с его значением, делается запрос в БД для получения QuerySet'a

* [class IncomeView](https://github.com/recourcefulcoder/EffectiveMobileTestTask/blob/7e02f2a8ff4e7212054f5d49c6eec20f26921f49/dionysus/orders/views.py#L63) -
по get-запросу делает запрос в БД и считает общую стоимость оплаченных заказов
* [class OrderProcessView](https://github.com/recourcefulcoder/EffectiveMobileTestTask/blob/7e02f2a8ff4e7212054f5d49c6eec20f26921f49/dionysus/orders/views.py#L140) - 
используеися как класс-родитель для view, отвечающих за изменение и добавление заказов. Добавляет в контекст необходимые для 
обработки заказов переменные _*formset*_ ([FormSet](https://docs.djangoproject.com/en/5.1/topics/forms/formsets/#formsets) 
для блюд заказа, используемая форма - [ItemForm]())

    Наследуется от классов:
    + стандартный django FormView
    + class [OrderProcessMixin](#mixins) (см. документацию ниже)

* [class AddOrder](https://github.com/recourcefulcoder/EffectiveMobileTestTask/blob/7e02f2a8ff4e7212054f5d49c6eec20f26921f49/dionysus/orders/views.py#L158C7-L158C15) - 
наследует OrderProcessView, обрабатывает добавление заказа
* [class EditOrder](https://github.com/recourcefulcoder/EffectiveMobileTestTask/blob/7e02f2a8ff4e7212054f5d49c6eec20f26921f49/dionysus/orders/views.py#L171) - 
наследует OrderProcessView, обрабатывает изменение заказа


#####Mixins
[OrderProcessMixin](https://github.com/recourcefulcoder/EffectiveMobileTestTask/blob/7e02f2a8ff4e7212054f5d49c6eec20f26921f49/dionysus/orders/views.py#L76C7-L76C28)

определяет следующие функции:
* **def get_items_formset(self, items: Optional[Dict[str, Union[int, str]]] = None)**:
  формирует formset по словарю с данными о товарах, возвращает FormSet


* **def process_post(self, request, success_message: str, force_update: bool = False) -> bool**:

  обрабатывает post-запрос на страницу единичного товара, решая в зависимости от значения аргумента force_update, 
  что именно происходит (обновление товара или создание нового), и выполняет соответствующий запрос в БД, добавляя
  в django.messages сообщение об успехе в случае успеха. 
  Вовзращает Bool, определяющий, успешно ли была совершена операция
  
### Документация API

К написанному приложению прилагается API, написанное на [Django REST Framework](https://www.django-rest-framework.org/).
Оно позволяет (без механизма авторизации) выполнять следующие действия:
+ получить в формате JSON список всех заказов в базе
+ создать новый заказ отправкой соответствующего запроса на эндпоинт API

А также 
+ получать
+ удалять
+ и редактировать единичный заказ по заданному id.

Запросы делаются на эндпоинты api/ (для просмотра списка/добавления новго заказа) и api/<int:id>/ - 
для RUD операций с единичным заказом.

Для реализации были использованы стандартные классы DRF - [ModelSerializer](https://www.django-rest-framework.org/api-guide/serializers/#modelserializer) 
и [generic class-based view](https://www.django-rest-framework.org/api-guide/generic-views/)

Вся логика реализации API содержиться в приложении "api"

