# Лендинг «Дашборд руководителя ТСО»

Статический одностраничный лендинг для конкурса «Лучшие в Сбере» 2026, номинация «Лучший в Безопасности. Проект года».

## Запуск локально

Откройте `index.html` двойным кликом в браузере или через локальный сервер:

```powershell
cd landing
python -m http.server 8080
# → http://localhost:8080
```

## Деплой на GitHub Pages

Репозиторий настроен на автоматический деплой папки `landing/` через GitHub Actions (`.github/workflows/deploy-landing.yml`).

### Первичная настройка (один раз)

1. На GitHub откройте **Settings → Pages**.
2. В **Build and deployment → Source** выберите **GitHub Actions** (не «Deploy from a branch»).
3. Смержите workflow в `main` или запустите вручную: **Actions → Deploy landing to GitHub Pages → Run workflow**.

После успешного деплоя сайт будет доступен по адресу:

`https://yarik795.github.io/WisenetDiagnostic/`

Обновление: любой push в `main`, затрагивающий файлы в `landing/`, пересобирает сайт автоматически.

## Деплой на Netlify

1. Загрузите содержимое папки `landing/` как сайт (drag-and-drop или Git).
2. Publish directory: `landing` (или корень, если деплоите только эту папку).

## Замена заглушек на реальные скриншоты

| Файл-заглушка | Страница приложения | Что снять |
|---|---|---|
| `assets/screens/dashboard-summary.svg` | `/objects` или сводка | Сводный дашборд с объектами и светофором |
| `assets/screens/payments.svg` | `/payments` | Отчёт «Статус оплаты», вкладки Модернизация/РВР |
| `assets/screens/report-rvr.svg` | `/rvr-repeat` | Анализ повторных РВР с AI-вердиктами и подсветкой |
| `assets/screens/ai-chat.svg` | `/ai-chat` | Чат с вопросом, SQL и графиком |
| `assets/screens/arsenal.svg` | `/arsenal` | Дашборд АС Арсенал (опционально) |
| `assets/screens/forecast.svg` | — | Прогноз бюджета (после реализации) |

### Как заменить

1. Сделайте скриншот (PNG или WebP, ширина ~1280 px).
2. Положите файл в `assets/screens/` с тем же именем, но расширением `.png`.
3. В `index.html` замените `.svg` на `.png` в соответствующем `<img src="...">`.

## Редактирование цифр экономического эффекта

В секции `#economics` значения с атрибутом `data-editable="true"` — заглушки. Измените `data-count` у нужных `<span>`:

```html
<span data-count="107" data-suffix=" млн ₽" data-editable="true">0</span>
```

## Структура файлов

```
landing/
├── index.html          — разметка лендинга
├── styles.css          — editorial + инженерный пульт
├── script.js           — scroll-reveal, count-up
├── README.md           — эта инструкция
└── assets/screens/     — заглушки и будущие скриншоты
```

## Важно

- Название проекта: **«Дашборд руководителя ТСО»**
- В публичном лендинге не используются внутренние кодовые имена проекта
