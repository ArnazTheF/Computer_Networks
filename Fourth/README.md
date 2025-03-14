Чекаем че происходит с psql
brew services list

Запускаем psql
brew services start postgresql

Там зарегаться надо, но эт ладно, readme больше про себя пишу. 
К тому же там всегда есть суперпользователь, если лень нового делать
psql -U your_username -d your_database

Это если надо ручками почистить
DELETE FROM guitars;
SELECT * FROM guitars;

Если совсем туго:
DROP TABLE guitars;

Запускаем API-шку (я там иногда порт менял, потому что на 8000 иногда ломалось, я хз почему):
python3 API.py

А потом curl "http://127.0.0.1:5000(мб другой хз)/parse?url=https://www.muztorg.ru/category/elektrogitary"

