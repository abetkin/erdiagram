# erdiagram

**erdiagram** is a django application that allows you to export your django models
to the [online data modeling](http://django.datamodeling.online) site.

The application provides `erdiagram` django command.

## Setup

1. Install the package with pip:

```
pip install erdiagram
```

2. Add `erdiagram` to `INSTALLED_APPS` in django settings:

```python
INSTALLED_APPS = [
    ...
    'erdiagram',
    ...
]
```

3. To export models for application `myapp`, use `todiagram` command:

```
python manage.py todiagram myapp --name mydiagram
```

You should see following output

```To finish import please open https://django.datamodeling.online/import/a5/04a616953d344b45b809878203944550 in your browser.```

Follow the link provided and you will be redirected to the diagram page.

The diagram created will be private by default. To make a public one pass the `--public` flag:

```
python manage.py todiagram myapp --public
```