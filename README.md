# Facial Recognition Attendance System
Project submission for Microsoft Engage 2022

This application allows users to keep track of attendance in classes taken by them by the means of a facial recognition system

## Steps to run the project

1. Clone this repo
    git clone https://github.com/richard1615/Facial-Recognition-Attendance-System.git

2. Set up and activate a python virtual environment

3. Run `pip install requirements.txt`

4. In settings.py, replace the following block of code 

    ```
    {
        DATABASES={
            'default':{
            'ENGINE':'django.db.backends.postgresql_psycopg2',
            'NAME':'postgres',
            'USER':'postgres',
            'PASSWORD':'',
            'HOST':'localhost',
            'PORT':'5432',
            }
        }
    }

    ```

   with this

```
   {
       DATABASES = {
            'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
            }
        }
   }
```

5. In facialrecognition/attendance/views.py

    replace line 244 with "{path to student images folder}/{student.pic.url}"

6. Run the following commands

```
{
    python manage.py makemigrations
    python manage.py migrate
    python manage.py runserver
}
```
7. Go to http://127.0.0.1:8000/ in your browser
## Credit

Facial recognition - https://www.youtube.com/watch?v=sz25xxF_AVE&t=2625s
