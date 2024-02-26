# Укажите необходимую версию python
FROM python:3.10

# Выберите папку, в которой будут размещаться файлы проекта внутри контейнера 
WORKDIR /opt/app

# Заведите необходимые переменные окружения
ENV DJANGO_SETTINGS_MODULE 'config.settings'

# Скопируйте в контейнер файлы, которые редко меняются
# COPY run_uwsgi.sh run_uwsgi.sh
COPY requirements.txt requirements.txt
# COPY uwsgi/uwsgi.ini uwsgi.ini

# Установите зависимости
RUN  pip install --upgrade pip \
     && pip install -r requirements.txt

# Скопируйте всё оставшееся. Для ускорения сборки образа эту команду стоит разместить ближе к концу файла. 
# COPY . .

# Укажите порт, на котором приложение будет доступно внутри Docker-сети
EXPOSE 8000

# Укажите, как запускать ваш сервис
ENTRYPOINT ["uwsgi", "--strict", "--ini", "uwsgi.ini"] 
# ENTRYPOINT ["uwsgi", "--module=config.wsgi", "--http", ":8000"] 