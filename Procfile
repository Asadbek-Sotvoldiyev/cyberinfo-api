[build]
  builder = "python"
  version = "3.9"

[setup]
  packages = ["python3", "gcc"]

[install]
  cmd = "python -m venv --copies /opt/venv && . /opt/venv/bin/activate && pip install -r requirements.txt"

[start]
  cmd = "gunicorn --workers 3 --bind 0.0.0.0:8000 app:app"
