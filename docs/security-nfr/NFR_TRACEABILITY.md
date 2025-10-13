# NFR Traceability Matrix

| NFR ID | NFR кратко | Story / Task ID | Влияние на NFR | Приоритет NFR | Релизное окно |
|--------|------------|----------------|----------------|---------------|----------|
| NFR-01 | JWT TTL | AUTH-01 | Генерация access token при регистрации, TTL ≤ 15 мин | High | Sprint 1 |
| NFR-02 | Password hashing | AUTH-01 | Хеширование пароля через Argon2id | High | Sprint 1 |
| NFR-05 | SLA ошибок | AUTH-01 | Обработка commit/refresh ошибок при регистрации | High | Sprint 1 |
| NFR-08 | Logging & Audit | AUTH-01 | Логирование регистрации пользователей | Medium | Sprint 1 |
| NFR-01 | JWT TTL | AUTH-02 | Генерация access token при логине, TTL ≤ 15 мин | High | Sprint 1 |
| NFR-02 | Password hashing | AUTH-02 | Проверка пароля через Argon2id | High | Sprint 1 |
| NFR-05 | SLA ошибок | AUTH-02 | Единый формат ошибок при логине | High | Sprint 1 |
| NFR-07 | Rate limiting | AUTH-02 | Ограничение неудачных логинов / 15 мин | High | Sprint 1 |
| NFR-08 | Logging & Audit | AUTH-02 | Логирование успешных и неуспешных попыток логина | Medium | Sprint 1 |
| NFR-01 | JWT TTL | AUTH-03 | Отзыв access token через RevokedToken | High | Sprint 1 |
| NFR-05 | SLA ошибок | AUTH-03 | Обработка ошибок revoke token | High | Sprint 1 |
| NFR-08 | Logging & Audit | AUTH-03 | Логирование logout событий | Medium | Sprint 1 |
| NFR-03 | Owner-only access | AUTH-04 | Только админы могут промоцию пользователей | Critical | Sprint 1 |
| NFR-05 | SLA ошибок | AUTH-04 | AuthorizationError и InternalServerError корректно возвращаются | High | Sprint 1 |
| NFR-08 | Logging & Audit | AUTH-04 | Логирование промоции пользователя | Medium | Sprint 1 |
| NFR-03 | Owner-only access | WISH-01 | Проверка owner_id при создании wish | Critical | Sprint 1 |
| NFR-09 | Input validation / SQLi | WISH-01 | Валидация полей через Pydantic | Critical | Sprint 1 |
| NFR-05 | SLA ошибок | WISH-01 | Обработка commit/refresh ошибок | High | Sprint 1 |
| NFR-08 | Logging & Audit | WISH-01 | Логирование создания wish | Medium | Sprint 1 |
| NFR-03 | Owner-only access | WISH-02 | Owner-only для list wishes | Critical | Sprint 1 |
| NFR-04 | API latency | WISH-02 | Пагинация limit/offset, p95 < 200ms | Medium | Sprint 1 |
| NFR-09 | Input validation / SQLi | WISH-02 | Валидация query params | Critical | Sprint 1 |
| NFR-05 | SLA ошибок | WISH-02 | Обработка ошибок выборки | High | Sprint 1 |
| NFR-08 | Logging & Audit | WISH-02 | Логирование запроса списка wishes | Medium | Sprint 1 |
| NFR-03 | Owner-only access | WISH-03 | Owner-only / admin при get wish | Critical | Sprint 1 |
| NFR-09 | Input validation / SQLi | WISH-03 | Валидация входного wish_id | Critical | Sprint 1 |
| NFR-05 | SLA ошибок | WISH-03 | Обработка NotFoundError/AuthorizationError | High | Sprint 1 |
| NFR-08 | Logging & Audit | WISH-03 | Логирование получения wish | Medium | Sprint 1 |
| NFR-03 | Owner-only access | WISH-04 | Owner-only / admin при patch wish | Critical | Sprint 1 |
| NFR-09 | Input validation / SQLi | WISH-04 | Валидация полей wish_in | Critical | Sprint 1 |
| NFR-05 | SLA ошибок | WISH-04 | Обработка ошибок commit | High | Sprint 1 |
| NFR-08 | Logging & Audit | WISH-04 | Логирование обновления wish | Medium | Sprint 1 |
| NFR-03 | Owner-only access | WISH-05 | Owner-only / admin при delete wish | Critical | Sprint 1 |
| NFR-05 | SLA ошибок | WISH-05 | Обработка ошибок commit | High | Sprint 1 |
| NFR-08 | Logging & Audit | WISH-05 | Логирование удаления wish | Medium | Sprint 1 |
