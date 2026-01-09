Set-Location -Path (Resolve-Path "$PSScriptRoot\..")
$exclude = @("venv", ".env", ".gitignore", "temp", "output", "build", "{{ cookiecutter.bot_id.replace(' ', '_') }}.zip")
$files = Get-ChildItem -Path . -Exclude $exclude
Compress-Archive -Path $files -DestinationPath "{{ cookiecutter.bot_id.replace(' ', '_') }}.zip" -Force