import os

os.rename("env", ".env")
os.makedirs(
    os.path.join("{{ cookiecutter.bot_id.replace(' ', '_') }}", "framework", "resources"),
    exist_ok=True,
)