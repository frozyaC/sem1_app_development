# Лабораторная работа 8: Taskiq, RabbitMQ и Планировщик отчётов

## Описание

В этой работе реализована асинхронная система создания отчётов по заказам с использованием:
- **Taskiq** — асинхронный task broker
- **RabbitMQ** — message broker для очередей
- **Scheduler** — планировщик для запуска задач по расписанию (cron)
- **FastStream** — обработка сообщений из RabbitMQ для заполнения БД

Система автоматически создаёт отчёты каждую минуту и позволяет получить отчёты по конкретной дате через REST API.

## Предварительные требования

- Docker и Docker Compose
- Порты 5432, 5672/15672, 6379, 8000 свободны

## Пошаговая инструкция запуска

### Шаг 1: Пересборка образа Docker с новыми файлами

```powershell
cd "C:\Users\Александр\Desktop\Maga\1st_sem\App_development\main\app_development"
docker compose build web
docker compose up -d
```

### Шаг 2: Запуск FastStream воркера (RabbitMQ consumer)

В **отдельном терминале** (терминал 1):

```powershell
docker exec -it app_web python rabbitmq.py
```

### Шаг 3: Запуск Taskiq Scheduler

В **новом терминале** (терминал 2):

```powershell
docker exec -it app_web taskiq scheduler app.scheduler:scheduler --skip-first-run
```

**Оставьте терминал открытым!**

---

### Шаг 4: Запуск Taskiq Worker

В **новом терминале** (терминал 3):

```powershell
docker exec -it app_web taskiq worker app.scheduler:broker
```

**Оставьте терминал открытым!**

---

### Шаг 5: Заполнение БД тестовыми данными

Теперь, когда все сервисы запущены, отправьте данные:

```powershell
# Создание пользователей и адресов
docker exec app_web python seed_postgres.py

# Создание продуктов
docker exec app_web python producer_products.py

# Создание заказов
docker exec app_web python producer_orders.py
```

### Шаг 6: Ожидание создания отчётов

Подождите **до 1 минуты**, пока scheduler (работает по расписанию `*/1 * * * *`) создаст отчёты.

В терминале с `taskiq worker` появится:
```
Created 3 order reports at 2025-12-15
```

---

### Шаг 7: Проверка результата через REST API

```powershell
curl "http://127.0.0.1:8000/report?report_date=2025-12-15"
```

Ожидаемый ответ:
```json
[
  {"id": 1, "report_at": "2025-12-15", "order_id": 1, "count_product": 2},
  {"id": 2, "report_at": "2025-12-15", "order_id": 2, "count_product": 2},
  {"id": 3, "report_at": "2025-12-15", "order_id": 3, "count_product": 1}
]
```

## Мониторинг RabbitMQ

Откройте в браузере: http://localhost:15672

Учётные данные: `guest` / `guest`

Выберите vhost: `local`

Здесь можно видеть очереди `product`, `order`, `cmd_order` и их статистику.

---

## Полный перезапуск с чистой БД

```powershell
docker compose down -v       # Удалить всё включая БД
docker compose build web     # Пересобрать образ
docker compose up -d         # Запустить заново
# Повторить шаги 2-7
```

---

## Диагностика проблем

### "No such file" при запуске seed_postgres.py или producer_*.py

**Причина:** Образ не пересобран после добавления новых файлов.

**Решение:**
```powershell
docker compose build web
docker compose up -d
```

**Или временно** (если нет времени пересобирать):
```powershell
docker cp seed_postgres.py app_web:/app/
docker cp producer_products.py app_web:/app/
docker cp producer_orders.py app_web:/app/
```

---

### ForeignKeyViolationError при создании заказов

**Причина:** В таблице `addresses` нет записей.

**Решение:** Запустите `seed_postgres.py` для создания пользователей и адресов:
```powershell
docker exec app_web python seed_postgres.py
```

---

### Scheduler создаёт 0 отчётов

**Причина:** В таблице `orders` нет записей.

**Решение:** 
Выполните шаг 5 полностью (seed, producer_products, producer_orders)

---

### Заказы отклоняются: "нет товаров [1, 2]"

**Причина:** Race condition — заказы обрабатываются до создания продуктов.

**Решение:** Разделены файлы `producer_products.py` и `producer_orders.py` — запускайте их последовательно с паузой 2-3 секунды.

---

## Структура файлов

```
app_development/
├── app/
│   ├── scheduler.py              # Scheduler и задачи Taskiq
│   ├── models/report.py          # OrderReport модель
│   ├── controller/report_controller.py  # GET /report endpoint
│   └── main.py                   # Litestar приложение
├── rabbitmq.py                    # FastStream воркер для RabbitMQ
├── seed_postgres.py               # Заполнение БД пользователями/адресами
├── producer_products.py           # Отправка продуктов в RabbitMQ
├── producer_orders.py             # Отправка заказов в RabbitMQ
├── docker-compose.yaml
├── Dockerfile
└── migrations/
```

---

## Как работает система

1. **seed_postgres.py** → создаёт пользователей и адреса в БД
2. **producer_products.py** → отправляет продукты в RabbitMQ (очередь `product`)
3. **rabbitmq.py** → читает очередь `product`, создаёт записи в таблице `products`
4. **producer_orders.py** → отправляет заказы в RabbitMQ (очередь `order`)
5. **rabbitmq.py** → читает очередь `order`, создаёт записи в таблице `orders`
6. **Scheduler** → каждую минуту отправляет задачу `my_scheduled_task` в очередь `cmd_order`
7. **Taskiq Worker** → выполняет задачу:
   - Получает все заказы из БД
   - Подсчитывает количество продуктов в каждом заказе
   - Создаёт отчёт в таблице `order_reports` (с проверкой дубликатов)
8. **REST API** → предоставляет `/report?report_date=YYYY-MM-DD` для получения отчётов

---

## Остановка сервисов

```powershell
docker compose down       # Остановить контейнеры, сохранить данные
docker compose down -v    # Остановить контейнеры и удалить БД
```

---

## Дополнительная информация

- **Cron формат**: `*/1 * * * *` = каждую минуту
- **VHost**: используется `local` вместо `/` по умолчанию
- **Database**: PostgreSQL через `DATABASE_URL`
- **Защита от дубликатов**: scheduler проверяет существование отчёта перед созданием
- **Порядок запуска важен**: scheduler/worker → отправка данных

---

## Ссылки

- [Taskiq документация](https://taskiq-python.github.io/)
- [FastStream документация](https://faststream.airt.ai/)
- [RabbitMQ документация](https://www.rabbitmq.com/)
- [Litestar документация](https://docs.litestar.dev/)
- [SQLAlchemy документация](https://docs.sqlalchemy.org/)
