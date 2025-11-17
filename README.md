# MovieLens Analytics

## Описание проекта
Анализ датасета MovieLens с созданием Python-модуля для работы с данными о фильмах, рейтингах и тегах. Проект включает автоматизированное тестирование и аналитический отчет.

## 📊 Компоненты проекта

### Основные классы
- **Ratings** - анализ рейтингов и пользователей
- **Movies** - работа с метаданными фильмов  
- **Links** - парсинг данных с IMDb/TMDB
- **Tags** - анализ пользовательских тегов
- **Tests** - комплексное тестирование

## 🔧 Технологии
- Python 3, Pandas, BeautifulSoup
- Pytest, Requests
- Jupyter Notebook

## 🚀 Запуск
```bash
# Установка зависимостей
pip install pandas beautifulsoup4 requests pytest jupyter

# Запуск тестов
pytest movielens_analysis.py -v

# Запуск отчета
jupyter notebook movielens_report.ipynb

# Структура
movielens_analysis.py    # Основной модуль
movielens_report.ipynb   # Аналитический отчет
data/                    # Дадасеты MovieLens
