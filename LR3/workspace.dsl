workspace {
    name "Домашнее задание, дедлайн 13 марта."
    !identifiers hierarchical

    model {
        user = person "Участник" {
            description "Участник конференции."
        }

        admin = person "Организатор конференции" {
            description "Отвечает за проверку поданных материалов."
        }

        mail_sys = softwareSystem "Система отправки сообщений" {
            description "Отправляет пользователям сообщения касательно статуса доклада, регистрации и статуса заявки."
        }

        store_sys = softwareSystem "Система хранения данных" {
            description "Система, хранящая в себе данные о всех поданных докладах и пользователях(Postgres)."
        }

        doc_sys = softwareSystem "База данных докладов" {
            description "Система, хранящая доклады (MongoDB)."
        }

        conference = softwareSystem "Сайт конференции" {
            description "Сайт конференции в интернете."


        doc_manage_sys = container "Система управления докладами" {
                technology "python fastapi"
                
            }

        lk_sys = container "Личный кабинет" {
                technology "SPA"
                -> doc_manage_sys "Загрузить или удалить доклад / доступ ко всем докладам конференции (орг.)" "REST API"
                
            }

        auth_database = container "База данных с активными сессиями" {
                technology "Redis"
            }

        registration_sys = container "Система регистрации" {
                technology "python fastapi"
                -> auth_database "Передать информацию о сессии пользователя." "Redis Protocol"
                -> lk_sys "Зайти в личный кабинет." "REST API"
            }

        web_application = container "Веб-приложение" {
                technology "HTML"                
                -> registration_sys "Зарегистрироваться." "HTTPS"
            }     

        }
  

        user -> conference.web_application "Перейти на сайт конференции." "HTTPS"
        admin -> conference.web_application "Рассмотреть поданные заявки/изменить статус заявки доклада" "HTTPS"
        conference.doc_manage_sys -> mail_sys "Команда отправить сообщение пользователю" "FAST API"
        conference.lk_sys -> store_sys "Поиск по маске/поиск по логину (орг.)/добавление доклада в конференцию (орг.)/получение списков докладов конференции" "PostgreSQL Queries"
        conference.doc_manage_sys -> doc_sys "Загрузить или удалить доклад / доступ ко всем докладам конференции (орг.)" "MongoDB Driver"
 
        mail_sys -> user "Передача сообщения пользователю." "SMTP"
        

    }

    views {
        themes default

        systemContext conference "c1_context" {
            include *
            autoLayout
        }

        container conference "c2" {
            include *
            autoLayout
        }

        dynamic conference "Adding_science_paper" {
        
        autoLayout lr   
        user -> conference.web_application "Зайти на сайт через веб приложение" "HTTPS"
        conference.web_application -> conference.registration_sys "Зарегистрироваться" "HTTPS"
        conference.registration_sys -> conference.lk_sys "Зайти в личный кабинет" "REST API"
        conference.lk_sys -> conference.doc_manage_sys "Добавить доклад" "REST API"
        conference.doc_manage_sys -> doc_sys "Добавление доклада" "MongoDB Driver"
}
    }
}