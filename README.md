Kowalski

Аналитический сервис на FastAPI для решения задач комбинаторики и сравнения поисковых конфигов в travel-tech.

FastAPI-based analytical service for solving combinatorics tasks and comparing search configurations in travel-tech.

Сервис помогает: The service helps to:

	•	расширять направления перелётов
    expand flight directions
	•	сравнивать выдачу разных API-ключей
    compare results from different API keys
	•	анализировать правила тарифов авиакомпаний
    analyze airline fare rules

---

🚀 Стек / Tech Stack

	•	FastAPI
	•	Python
	•	Pandas
	•	Docker
	•	PostgreSQL
	•	Elastic Search
---

📌 Эндпоинты / Endpoints

---

1️⃣ Расширение направлений (Combinatorics) Direction Expansion (Combinatorics)

Позволяет расширить список направлений перелётов. Expands a list of flight directions.

📥 Вход / Input

    .txt файл со списком направлений:
    .txt file containing flight directions:

    KHI-MCX
    KHI-LED
    LED-KHI
    LHE-KHI|KHI-LHE

📤 Выход / Output

Сервис генерирует все комбинации: The service generates all combinations:

		•	туда
    outbound
	  •	обратно
    inbound
	  •	туда-обратно
    round-trip
	  •	обратно-туда
    reverse round-trip

Пример результата: Example result:

    KHI-MCX
    MCX-KHI
    KHI-MCX|MCX-KHI
    MCX-KHI|KHI-MCX
    KHI-LED
    LED-KHI
    KHI-LED|LED-KHI
    LED-KHI|KHI-LED
    KHI-LHE
    LHE-KHI
    KHI-LHE|LHE-KHI
    LHE-KHI|KHI-LHE


---

2️⃣ Сравнение поисковых конфигов Search Configuration Comparison

Позволяет сравнить выдачу двух API-ключей по заданным параметрам.
Allows comparison of search results from two API keys based on selected parameters.

🔹 Обязательные параметры / Required parameters
	
    •	filter_airlines — авиакомпания
    airline filter
	  •	date — дата поиска
    search date
	  •	api_key_1 — первый API-ключ
    first API key
	  •	api_key_2 — второй API-ключ
    second API key
	  •	service_class — класс обслуживания
    cabin class

    A — все / all  
    E — эконом / economy  
    B — бизнес / business  
    F — первый / first  
    W — комфорт / premium economy  

🔹 Режимы работы / Modes
  
    1.	Передача направлений списком:
    Pass directions as a list:

    directions: [...]

    2.	Автоматическая генерация направлений:
    Automatic generation of directions:

    top_directions_from_date
    limit_directions

    Если используется второй вариант — передать:
    If using the second option — pass:

    directions: []

🔹 Опциональные параметры / Optional parameters
	
    •	avia_config_item_ids_1
	  •	avia_config_item_ids_2
	  •	filter_gds
	  •	exclude_gds
	  •	force_search: '1' — обход кеша
    bypass cache
	  •	max_segments

⚠️ Если параметр не используется — передавать пустую строку.

If a parameter is not used — pass an empty string.

---

3️⃣ Сравнение правил тарифов Fare Rules Comparison

Позволяет сравнить правила тарифов одной авиакомпании и определить необходимость их настройки.

Allows comparison of fare rules for a single airline and helps determine if configuration adjustments are required.

🔹 Обязательные параметры / Required parameters
	
    •	filter_airlines
	  • date
	  •	api_key
	  •	service_class

🔹 Режимы работы / Modes

Аналогично предыдущему эндпоинту: Same logic as previous endpoint:
	  
    •	directions
	  •	либо top_directions_from_date + limit_directions
    or top_directions_from_date + limit_directions

🔹 Опциональные параметры / Optional parameters
	
    •	avia_config_item_ids
	  •	filter_gds
	  •	exclude_gds
	  •	force_search
	  •	max_segments

Если не используется — передавать пустую строку. If not used — pass an empty string.

---

🧠 Что решает сервис / What the service solves
	
    •	Упрощает комбинаторные расчёты направлений
    Simplifies combinatorial direction calculations
	  •	Позволяет быстро находить расхождения в поисковой выдаче
    Helps quickly detect discrepancies in search results
	  •	Помогает контролировать корректность тарифных правил
    Helps control fare rule correctness
	  •	Автоматизирует ручную аналитику
    Automates manual analytics tasks

---

▶️ Запуск / Run

docker-compose up --build

или / or

uvicorn main:app --reload
---


# comands to use

## pylint

pylint --rcfile=.pylintrc src

## GIT

git add .
git commit -m "131952-add_pg_configs"
git push -u origin 131952-add_pg_configs

## Docker

- re-run & re-build your Docker Compose
docker-compose up --build
- shut down your Docker Compose
docker stop <container_id>
docker-compose down ?????????????

- check running dockers
docker ps
- check process
sudo lsof -i :4000
- kill process
kill -9 <PID>

docker exac -it <mycontainer> bash
