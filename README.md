# erdiagram

**erdiagram** is a django application that allows you to export your django models
to the [online data modeling](django.datamodeling.com) site.

The application provides `erdiagram` django command.

## Setup

1. Install the package with pip:

```python
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

3. To export models for application `myapp`, use `erdiagram` command:

```python
python manage.py erdiagram myapp --name mydiagram
```

You will be asked to enter your credentials for django.datamodeling.com. Then you can login to the site and edit your diagram online. 