# Фильтр желтушных новостей

Данный сервис позволяет проводить анализ статей с новостных сайтов с целью определения степени желтушности статьи.
Под степенью желтушности подразумевается процентное содержание экспрессивных, ярко-негативных и восторженно-позитивных слов в статье (так называемых "заряженных" слов).
Список "заряженных" слов хранится в заранее подготовленном словаре.

Пока поддерживается только один новостной сайт - [ИНОСМИ.РУ](https://inosmi.ru/). 
Для него разработан специальный адаптер, умеющий выделять текст статьи на фоне остальной HTML разметки. 
Для других новостных сайтов потребуются новые адаптеры, все они будут находиться в каталоге `adapters`. 
Туда же помещен код для сайта ИНОСМИ.PУ: `adapters/inosmi_ru.py`.

## Как установить

Вам понадобится Python версии 3.7 или старше. Для установки пакетов рекомендуется создать виртуальное окружение.

Первым шагом установите пакеты:

```bash

$ pip install -r requirements.txt

```

## Как запустить

```bash

$ python server.py

```

Затем необходимо открыть браузер и выполнить GET-запрос следующего формата:

```

http://127.0.0.1:8080?urls=url1,url2,url3,...

```

где `url1,url2,url3,...` - URL'ы статей для анализа, разделённые через запятую (не больше 10).


Примеры запросов:

```

http://127.0.0.1:8080?urls=https://inosmi.ru/politic/20190713/245466415.html

http://127.0.0.1:8080?urls=https://inosmi.ru/politic/20190713/245466415.html,https://inosmi.ru/economic/20190713/245465884.html

```

## Формат ответа сервера

Результаты анализа статей будут представлены в формате JSON следующего вида:

```

[
  {
    "status": статус_операции,
    "url": url1,
    "score": степень_желтушности,
    "words_count": количество_слов
  },
  {
    "status": статус_операции,
    "url": url2,
    "score": степень_желтушности,
    "words_count": количество_слов
  },
  ...
]

```

где:

* **status** - статус операции по анализу статьи:
  * OK - анализ статьи успешно выполнен
  * FETCH_ERROR - не удалось скачать текст статьи
  * PARSING_ERROR - не удалось выполнить извлечение текста статьи из загруженной страницы
  * TIMEOUT - не удалось выполнить скачивание статьи или её анализ в заданный интервал времени (3 секунды)
* **url** - URL анализируемой статьи
* **score** - степень желтушности текста статьи (число от 0 до 100, только в случае успешного выполнения анализа, иначе null)
* **words_count** - количество слов в статье (только в случае успешного выполнения анализа, иначе null)

Примеры ответа сервера:

```json

[
  {
    "status": "OK",
    "url": "https://inosmi.ru/politic/20190713/245466415.html",
    "score": 0.47,
    "words_count": 643
  },
  {
    "status": "OK",
    "url": "https://inosmi.ru/economic/20190713/245465884.html",
    "score": 0.91,
    "words_count": 1104
  }
]

```

```json

[
  {
    "status": "PARSING_ERROR",
    "url": "https://lenta.ru/news/2019/07/14/huawei/",
    "score": null,
    "words_count": null
  }
]

```

## Как запустить тесты

Для тестирования используется [pytest](https://docs.pytest.org/en/latest/).
Команды для запуска тестов:

```bash

$ pytest adapters/inosmi_ru.py

```
```bash

$ pytest text_tools.py

```
```bash

$ pytest articles_processor.py

```

# Цели проекта

Код написан в учебных целях. Это урок из курса по веб-разработке — [Девман](https://dvmn.org).
