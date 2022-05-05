if [[ "$OSTYPE" == "linux-gnu"* || "$OSTYPE" == "darwin"* ]]; then
    # Virtual Env.
    python3 -m venv venv
    source venv/bin/activate

    # Install Requirements
    pip install -r requirements.txt

    # Export Temporary Env. Variables
    # export FLASK_APP='run.py'
    # export FLASK_ENV='development'

    # Start Flask App
    flask run
elif [[ "$OSTYPE" == "msys" ]]; then
    # Export Permanent Env. Variables (Windows)
    # setx FLASK_APP 'run.py'
    # setx FLASK_ENV 'development'

    # Export Temporary Env. Variables (Windows)
    set FLASK_APP='run.py'
    set FLASK_ENV='development'
else
    echo "setup script did not run!"
fi
