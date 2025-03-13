Задание 01 

Целью работы является получение навыка в описании архитектуры в стиле Architecture As A Code и 
проектировании системы «сверху вниз». 

Необходимо создать описание архитектуры системы в формате Structurizr DSL: 
1. Изучите текст задания. 
2. Определите перечень ролей пользователей и перечень внешних систем. 
3. Создайте описание softwareSystem и диаграмму systemContext 
4. Продумайте основные задачи пользователей и как они могут быть реализованы 
5. Сформируйте перечень container отвечающих за обработку событий, связанных с объектами 
предметной области, определенной в задании (Клиентский сервис, Сервис управления 
доставкой, Сервис регистрации платежей …) 
6. Определите взаимодействие между контейнерами (создание пользователя, создание заказа на 
доставку …) 
7. Опишите модель container в Structurizr DSL и создайте диаграмму Container. 
8. Определите технологии и проставьте их на контейнерах и связях 
9. Создайте одну диаграмму dynamic для архитектурно значимого варианта использования 
(отправка сообщения между пользователями, покупка товара в магазине ….) 

Результат должен быть оформлен в виде следующих файлов, размещенных в вашем github:
- readme.md с текстом задания 
- workspace.dsl с моделью и view 

Полезный пример проекта в Structurizr DSL: 
https://github.com/DVDemon/architecture_python/tree/main/01_structurizr 
Справка по языку: https://docs.structurizr.com/dsl/language

Вариант 3.

Сайт конференции.

https://www.eventboost.com/ru-RU/  
 
Приложение должно содержать следующие данные:
- Пользователь
- Доклад
- Конференция 
 
Реализовать API:
- Создание нового пользователя
- Поиск пользователя по логину
- Поиск пользователя по маске имя и фамилии
- Создание доклада
- Получение списка всех докладов
- Добавление доклада в конференцию
- Получение списка докладов в конференции 