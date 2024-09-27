

## sqlalchemy
```bash
pip install "sqlalchemy[asyncio]"
```
## postgres
```bash
pip install asyncpg
```
## alembic
 создание директории alembic; переместили директорию alembic куда нам удобнее, при этом alembic.ini остается в root(./auth_sprint_1)
```bash
pip install alembic &&\
alembic init -t async alembic &&\
mv ./alembic ./auth_service/src/db
```
#### alembic.ini
Закомменитровать sqlalchemy.url - для указания своего драйвера, например postgresql+asyncpg
Раскомменитровать file_template - для указания красивого формата ревизии (миграции)
Поменять скрипт расположения директории alembic с ./alembic на auth_service/src/db/alembic (вкусовщина)
```ini
#sqlalchemy.url = driver://user:pass@localhost/dbname
file_template = %%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d%%(minute).2d-%%(rev)s_%%(slug)s
script_location = auth_service/src/db/alembic
```
#### alembic/env.py
добавить перед функциями
```python
from auth_service.src.core.config import settings
from auth_service.src.db.postgres import Base
from auth_service.src.models import user, role # обязательно импортировать сюда новую модель после ее создания в models
target_metadata = Base.metadata
config.set_main_option("sqlalchemy.url",settings.POSTGRES_DSN)
```

### alembic commands
alembic revision --autogenerate -m "Initial migration" -создать новую ревизию (python manage.py makemigrations)
alembic upgrade head - применить миграцию к базе данных  (python manage.py migrate)
