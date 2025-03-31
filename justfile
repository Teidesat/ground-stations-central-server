project := file_stem(justfile_directory())
venv-name := ".venv"
venv-path := join(justfile_directory(), venv-name)


# ==============================================================================
# DJANGO RECIPES
# ==============================================================================

# Launch development server
runserver: kill-runservers
    ./manage.py runserver

# Launch Django interactive shell
sh:
    ./manage.py shell

alias mm := makemigrations
# Make Django migrations
makemigrations:
    ./manage.py makemigrations
    
alias m := migrate
# Apply Django migrations
migrate:
    ./manage.py migrate

alias c := check
# Check if Django project is correct
check:
    ./manage.py check

# Add a new app and install it on settings.py
startapp app:
    #!/usr/bin/env bash
    python manage.py startapp {{ app }}
    APP_CLASS={{ app }}
    APP_CONFIG="apps.{{ app }}.apps.${APP_CLASS^}Config"
    perl -0pi -e "s/(INSTALLED_APPS *= *\[)(.*?)(\])/\1\2    '$APP_CONFIG',\n\3/smg" ./main/settings.py
    echo "✔ {{ app }} installed & added to settings.INSTALLED_APPS"

# ==============================================================================
# VIRTUALENV RECIPES
# ==============================================================================

# Create a Python virtualenv

# ==============================================================================
# DJANGO AUX RECIPES
# ==============================================================================

# Setup a Django project
setup: migrate create-su
    #!/usr/bin/env bash
    django-admin startproject main .
    sed -i -E "s/(TIME_ZONE).*/\1 = 'Atlantic\/Canary'/" ./main/settings.py
    echo "✔ Fixed TIME_ZONE='Atlantic/Canary' and LANGUAGE_CODE='es-es'"

# Create a superuser (or update it if already exists)
create-su username="admin" password="admin" email="admin@example.com":
    #!/usr/bin/env bash
    ./manage.py shell -c '
    from django.contrib.auth.models import User
    user, _ = User.objects.get_or_create(username="{{ username }}")
    user.email = "{{ email }}"
    user.set_password("{{ password }}") 
    user.is_superuser = True
    user.is_staff = True
    user.save()
    ' 
    echo "✔ Created superuser → {{ username }}:{{ password }}"

# https://medium.com/@mustahibmajgaonkar/how-to-reset-django-migrations-6787b2a1e723
# https://stackoverflow.com/a/76300128
# Remove migrations and database. Reset DB artefacts.
[confirm]
reset-db: && create-su
    #!/usr/bin/env bash
    find . -path "*/migrations/*.py" ! -path "./.venv/*" ! -name "__init__.py" -delete
    find . -path "*/migrations/*.pyc" ! -path "./.venv/*" -delete
    rm -f db.sqlite3
    ./manage.py makemigrations
    ./manage.py migrate
    echo

# Launch worker for Redis Queue (RQ)
rq: redis
    watchmedo auto-restart --pattern=tasks.py --recursive -- ./manage.py rqworker

# Generate fake data and populate Django database
[private]
@gen-data *args: clean-data
    #!/usr/bin/env bash
    ./manage.py gen_data {{ args }}

# Dump fixtures
[private]
dump-data: gen-data
    #!/usr/bin/env bash
    mkdir -p fixtures
    ./manage.py dumpdata --format json --indent 2 auth.User -o fixtures/auth.json
    for model in users categories platforms games orders; do
        ./manage.py dumpdata --format json --indent 2 $model -o fixtures/$model.json
    done

# Clean data
[private]
clean-data:
    #!/usr/bin/env bash
    for table in categories_category games_game games_review orders_order platforms_platform users_token; do
        sqlite3 db.sqlite3 "DELETE FROM $table; UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME='$table';"
    done
    sqlite3 db.sqlite3 "DELETE FROM auth_user WHERE is_superuser=0; UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME='auth_user';"

# Show current users on database
show-users:
    #!/usr/bin/env bash
    ./manage.py shell -c '
    from django.contrib.auth.models import User
    
    for user in User.objects.exclude(is_superuser=True):
        print(user.username)
    ' 

# Load fixtures into database
load-data: clean-data
    #!/usr/bin/env bash
    for model in auth users categories platforms games orders; do
        ./manage.py loaddata fixtures/$model.json
    done
    echo ---------------------------
    echo ↓ Users with password: 1234
    echo ---------------------------
    just show-users

# Kill all Django runserver processes
[private]
kill-runservers:
    #!/usr/bin/env bash
    for pid in $(ps aux | grep '[Pp]ython.*manage.py runserver' | awk '{ print $2 }')
    do
        kill -9 $pid
    done

# ==============================================================================
# MISC RECIPES
# ==============================================================================

# Enable testing with pytest inside VSCode
enable-vscode-pytest:
    #!/usr/bin/env bash
    mkdir -p .vscode
    cat << EOF > .vscode/settings.json
    {
      "python.testing.pytestArgs": ["tests"],
      "python.testing.unittestEnabled": false,
      "python.testing.pytestEnabled": true
    }
    EOF

# Start redis server
[private]
redis:
    #!/usr/bin/env bash
    if [[ $(grep -i redis $(find . -name settings.py)) ]]; then
        if   [[ $OSTYPE == "linux-gnu"* ]]; then
            pgrep -x redis &> /dev/null || sudo service redis start
        elif [[ $OSTYPE == "darwin"* ]]; then
            pgrep -x Redis &> /dev/null || (open /Applications/Redis.app && sleep 2)
        fi
    fi