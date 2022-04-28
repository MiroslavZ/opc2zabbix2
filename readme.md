# Универсальный OPC-шлюз

Мониторинг OPC-серверов и выдача показателей узлов сторонним сервисам через api

При запуске приложения происходит чтение excel документа и конфигурационного файла.
- В excel документе содержатся листы. 
  Имя листа соответствует имени OPC-сервера и совпадает с таковым в .env файле. 
  В листе таблица из трех столбцов Item, Key и Node.
  - Item - имя узла
  - Key - ключ для получения измерений узла через API
  - Node - node id адрес узла в OPC-сервере
- В конфигурационном файле находятся словарь серверов в виде JSON-строки 
  `SERVERS='{"MyServer1":"opc.tcp://localhost:54000"}'` 
  и три уровня логирования: 
  - для шлюза `LOG_LEVEL='WARNING'`, 
  - для библиотеки asyncua `ASYNCUA_LOG_LEVEL='WARNING'` 
  - для веб-сервера uvicorn `UVICORN_LOG_LEVEL='WARNING'`

Далее осуществляется планирование задач на подключение и поддержку связи с серверами. 
Повторное подключение реализовано через бесконечный цикл, state-машину со следующими состояниями:
1. Подключение к серверу:
   - Переход к состоянию 2 или повторные попытки подключиться
2. Получение узлов и подписка на них:
   - Формирование объектов узлов из строковых представлений node id
   - Подписка на узлы, сохранение объекта подписки и handles (понадобятся далее)
   - Переход к состоянию 3
3. Циклическая проверка состояния сервера:
   - Проверка service level узла сервера
   - Результат проверки — флаги can_check_service_level, 
     service_level_is_normal.
   - Если все нормально — повтор проверки  
   - Если service level ненормальный или соединение потеряно переход в состояние 4
4. В случае проблем — отписка от узлов, удаление подписки, 
   отключение OPC-клиента, возврат к состоянию 1


## Методы API

Получение последнего измерения для узла по ключу. Ключ соответствует полю Key из excel документа.  
`@app.get("/measurements/{key}")`

```
curl -X 'GET' \
  'http://127.0.0.1:8000/measurements/TestTag1' \
  -H 'accept: application/json'
```
Пример ответа:
```  
{
  "node_id": "ns=1;s=PN_SIMULATOR.PD_SIMULATOR.TestTag1",
  "display_name": "TestTag1",
  "value_type": 6,
  "last_value": 3,
  "health_is_good": true
}
``` 
Получение статуса сервера по его имени. Статус включает в себя наличие подключения и значение service level узла сервера. При отсутствии service level узла значение "unknown"  
`@app.get("/servers/{name}")`

```
curl -X 'GET' \
  'http://127.0.0.1:8000/servers/MyServer1' \
  -H 'accept: application/json'
```
Пример ответа:
```
{
  "connected": true,
  "service_level": "unknown"
}  
```
Управление соединением шлюза осуществляется с помощью отправки команд stop, start, restart  
`@app.get("/control/{command}")`

Изменение уровня логирования через API. Передается имя логгер и новый уровень логирования. Имя — имя модуля шлюза / библиотеки. 

Модули шлюза — app.main, app.server_interactions, app.subscription_handler. 

Логгеры из сторонних библиотек — asyncua, uvicorn.access, uvicorn.error

Уровни логирования - "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"
`@app.post("/control/logs")`

```
curl -X 'POST' \
  'http://127.0.0.1:8000/control/logs?logger_name=app.server_interactions' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "log_level": "INFO"
}'
```
Пример ответа:
```
"Log level for logger app.server_interactions updated to INFO"
```

## Запуск в Docker

`docker-compose up`