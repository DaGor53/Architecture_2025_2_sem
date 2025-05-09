1. Для данных, хранящихся в реляционной базе PotgreSQL реализуйте шаблон 
сквозное чтение и сквозная запись (Пользователь/Клиент …);
 2. В качестве кеша –используйте Redis
 3. Замерьте производительность запросов на чтение данных с и без кеша с 
использованием утилиты wrk https
 ://github.com/wg/wrk изменяя количество 
потоков из которых производятся запросы (1, 5, 10)
 4. Актуализируйте модель архитектуры в Structurizr DSL
 5. Ваши сервисы должны запускаться через docker-compose командой docker
compose up(создайте Docker файлы для каждого сервиса)
 Задание
 Рекомендации по C++--
 Используйте фреймворк Poco https
 ://docs.pocoproject.org/current/
 Пример по работе с Poco Web Servers и Redis 
https://github.com/DVDemon/arch_lecture_examples/tree/main/hl_mai_lab_05
 Рекомендации по Python:--
 Используйте FastAPI для построения интерфейсов
 Простой пример применения redis 
https://github.com/DVDemon/architecture_python/tree/main/07_redis
