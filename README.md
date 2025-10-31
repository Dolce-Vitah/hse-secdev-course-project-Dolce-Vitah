# Проект для курса по проектированию безопасного ПО "Wishlist"

Wishlist - приложение для хранения списка желаемых вещей, расставленных по приоритету. Каждый продукт имеет ссылку на сайт, где его можно приобрести.

## Содержание
- [Требования окружения](#требования-окружения)
- [Установка и запуск](#установка-и-запуск)
- [Тесты и качество](#тесты-и-качество)
- [CI](#ci)
- [Контейнеры](#контейнеры)
- [Эндпойнты](#эндпойнты)
- [Формат ошибок](#формат-ошибок)

## Требования окружения

Python >= 3.10, Git, make (опционально).

## Установка и запуск
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt -r requirements-dev.txt
pre-commit install
```

Запуск приложения
```bash
uvicorn app.main:app --reload
```

## Тесты и качество
```bash
ruff check --fix .
black .
isort .
pytest -q
pre-commit run --all-files
```

## CI
В репозитории настроен workflow **CI** (GitHub Actions) — required check для `main`.
Badge добавится автоматически после загрузки шаблона в GitHub.

## Контейнеры
```bash
docker build -t secdev-app .
docker run --rm -p 8000:8000 secdev-app
# или
docker compose up --build
```

## Эндпойнты
- `GET /health` → `{"status": "ok"}`
- `POST /items?name=...` — демо-сущность
- `GET /items/{id}`

## Формат ошибок
Все ошибки — JSON-обёртка:
```json
{
  "error": {"code": "not_found", "message": "item not found"}
}
```

См. также: `SECURITY.md`, `.pre-commit-config.yaml`, `.github/workflows/ci.yml`.
