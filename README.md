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

You will be asked to enter your credentials for http://django.datamodeling.online. Then you can login to the site and edit your diagram online. 
