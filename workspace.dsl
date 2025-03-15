workspace {
    model {
        // Пользователь системы
        endUser = person "Конечный пользователь" {
            description "Человек, который использует сервис для управления файлами."
        }

        // Платформа хранения файлов
        FileStoragePlatform = softwareSystem "Платформа управления файлами" {
            description "Сервис для управления пользователями, папками и файлами."

            // Веб API
            WebAPI = container "Web API" {
                description "Обрабатывает запросы пользователей на управление файлами и папками."
                technology "Django (Python)"
            }
            
            // Сервисные модули
            UserService = container "Сервис пользователей" {
                description "Обрабатывает регистрацию, поиск и управление пользователями."
                technology "Flask (Python)"
            }
            
            FolderService = container "Сервис папок" {
                description "Управляет созданием и организацией папок."
                technology "Flask (Python)"
            }
            
            FileService = container "Сервис файлов" {
                description "Отвечает за загрузку, хранение и удаление файлов."
                technology "Flask (Python)"
            }

            // База данных
            StorageDB = container "База данных" {
                description "Хранит пользователей, папки и файлы."
                technology "PostgreSQL"
            }
            
            // Таблицы данных
            UserTable = container "Таблица пользователей" {
                description "Содержит данные о зарегистрированных пользователях."
            }

            FolderTable = container "Таблица папок" {
                description "Содержит данные о созданных папках."
            }

            FileTable = container "Таблица файлов" {
                description "Хранит метаданные о загруженных файлах."
            }
        }

        // Взаимодействия
        endUser -> WebAPI "Отправляет запросы" "HTTP JSON"

        WebAPI -> UserService "Вызывает"
        WebAPI -> FolderService "Вызывает"
        WebAPI -> FileService "Вызывает"

        UserService -> StorageDB "Сохраняет/Читает" "SQL"
        FolderService -> StorageDB "Сохраняет/Читает" "SQL"
        FileService -> StorageDB "Сохраняет/Читает" "SQL"
        
        StorageDB -> UserTable "Содержит данные о"
        StorageDB -> FolderTable "Содержит данные о"
        StorageDB -> FileTable "Содержит данные о"
    }
    
    views {
        systemContext FileStoragePlatform {
            include *
            autoLayout
        }
        
        container FileStoragePlatform {
            include *
            autoLayout
        }
        
        dynamic FileStoragePlatform {
            title "Регистрация пользователя"
            endUser -> WebAPI "Отправляет данные регистрации"
            WebAPI -> UserService "Создаёт пользователя"
            autoLayout
        }
        
        dynamic FileStoragePlatform {
            title "Добавление файла"
            endUser -> WebAPI "Загружает файл"
            WebAPI -> FileService "Сохраняет файл"
            autoLayout
        }
    
        dynamic FileStoragePlatform {
            title "Создание папки"
            endUser -> WebAPI "Создаёт папку"
            WebAPI -> FolderService "Сохраняет папку"
            autoLayout
        }

        theme default
    }
}
