# PHPTravels UI Automation

## English

A UI automation project for testing the [PHPTravels](https://phptravels.net/) demo website.

**Tech Stack:**
* Python
* Playwright
* Pytest

**How to run the Happy Path test:**
```bash
pytest flights_happy_path.py -v -s
```

**Project Structure:**
* `conftest.py` — Test setup, session login, and logging.
* `flight_booking_happy_path.py` — E2E test for booking a flight (1 Adult).

*(More tests are coming soon...)*

---

## 🇷🇺 Русский

Проект по автоматизации тестирования UI демонстрационного сайта [PHPTravels](https://phptravels.net/).

**Стек технологий:**
* Python
* Playwright
* Pytest

**Как запустить тест (Happy Path):**
```bash
pytest flights_happy_path.py.py -v -s
```

**Структура проекта:**
* `conftest.py` — Настройка тестов, авторизация на всю сессию и логирование.
* `flight_booking_happy_path.py` — E2E тест покупки авиабилета (1 взрослый).

*(В планах написание других тестов...)*