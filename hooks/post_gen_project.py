import os

os.rename("env", ".env")
os.makedirs(
    name="resources",
    exist_ok=True,
)