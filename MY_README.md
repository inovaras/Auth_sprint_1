

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
comment sqlalchemy.url = driver://user:pass@localhost/dbname
uncomment file_template = %%(year)d_%%(month).2d_%%(day).2d_%%(hour).2d%%(minute).2d-%%(rev)s_%%(slug)s
меняем скрипт локации script_location = auth_service/src/db/alembic
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
