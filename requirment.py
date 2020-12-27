import pip

try:
    pip.main(["install", "telethon"])
except SystemExit as e:
    pass