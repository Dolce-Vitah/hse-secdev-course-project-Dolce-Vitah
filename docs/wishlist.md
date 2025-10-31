### Строка из .csv файла:
```
9, Wishlist;Список желаемых вещей/наборов, "User; Wish(title, link, price_estimate, notes)", CRUD /wishes; GET /wishes?price<, AuthN/AuthZ; owner-only; numeric validation, Категории; сортировка; экспорт, Python/FastAPI + SQLite/Postgres + Pytest
```


### Главные сущности:
- **User**
  - username: str
  - password_hash: str
  - is_admin: bool
- **Wish**
  - title: str
  - link: optional str
  - price_estimate: optional float (валидировать > 0)
  - notes: optional str
  - owner_id: int (FK -> User.id)


### Endpoints:
- `POST /api/v1/auth/register` — регистрация (username + password)
- `POST /api/v1/auth/login` — получить JWT
- `POST /api/v1/auth/logout` — отозвать токен (revoked tokens)
- `POST /api/v1/wishes` — создать wish (owner-only)
- `GET /api/v1/wishes?price=<value>` — список собственных wishes (фильтр по цене)
- `GET /api/v1/wishes/{id}` — получить wish (owner-only)
- `PATCH /api/v1/wishes/{id}` — обновить (owner-only)
- `DELETE /api/v1/wishes/{id}` — удалить (owner-only)


### Stretch (опционально):
- Категории (Category модель, связь many-to-many)
- Сортировка / дополнительные фильтры (price_min / price_max / sort_by)
- Экспорт CSV/JSON `/api/v1/wishes/export`
- Админский интерфейс: просмотр всех пользователей / wishes
