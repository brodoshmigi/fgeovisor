import pathlib

a = pathlib.Path(__file__).resolve().parent

print(next(a.iterdir()))