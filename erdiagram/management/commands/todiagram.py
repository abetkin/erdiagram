import os
import requests
import json

import sys
PY2 = sys.version_info[0] == 2


from django.core.management.base import BaseCommand

URL = 'https://django.editor.ponyorm.com'
# URL = 'http://localhost:5001'

class Command(BaseCommand):
    help = 'Export as a diagram to editor.ponyorm.com.'

    def add_arguments(self, parser):
        parser.add_argument('app_label', type=str)
        parser.add_argument(
            '--name', dest='diagram_name', default=None,
            help="Name of the imported diagram.",
        )

    def handle(self, *args, **options):
        app_label = options['app_label']
        diagram = make_diagram(app_label)
        diagram = json.dumps(diagram)
        with open('dia.json', 'w') as f:
            f.write(diagram)

        self.stdout.write('Please enter your credentials at {}'.format(URL))
        if PY2:
            input_ = raw_input
        else:
            input_ = input
        login = input_('Login: ')
        passwd = input('Password: ')
        diagram_name = options['diagram_name'] or app_label

        resp = requests.post(URL + '/import_project', json={
            'login': login, 'password': passwd, 'diagram': diagram,
            'diagram_name': diagram_name, 'private': True,
        })
        if resp.status_code != 200:
             self.stdout.write('Server returned {}'.format(resp.status_code))
             return
        resp = json.loads(resp.text)
        self.stdout.write('\nYour diagram is available at {URL}{link}'.format(URL=URL, link=resp['link']))


OPTIONS = (
    'verbose_name', 'verbose_name_plural', 'db_table', 'ordering',
    'unique_together', 'get_latest_by', 'order_with_respect_to',
    'app_label', 'db_tablespace', 'abstract', 'managed',
    'auto_created', 'index_together', 'default_permissions',
    'default_related_name', 'required_db_features',
    'required_db_vendor', 'base_manager_name', 'default_manager_name',
)


from math import ceil, sqrt

class Placing:

    SPACE_HEIGHT = 30
    SPACE_WIDTH = 20

    def __init__(self, entities):
        self.entities = entities

    def apply(self):
        size = int(ceil(sqrt(len(self.entities))))
        top = self.SPACE_HEIGHT
        height = 0
        for row in range(size):
            left = self.SPACE_WIDTH
            for col in range(size):
                index = row * size + col
                try:
                    entity = self.entities[index]
                    h = self.get_height(entity)
                    if h > height:
                        height = h
                except IndexError:
                    return
                w = self.get_width(entity)
                entity.update({
                    'left': left, 'top': top, 'width': round(w), 'height': round(h),
                })
                left += w + self.SPACE_WIDTH
            top += height + self.SPACE_HEIGHT

    def get_height(self, entity):
        rows_count = len(entity['attributes'])
        return 68 + 22.2 * rows_count

    def get_width(self, entity):
        return 250


def make_diagram(app_label):
    from django.apps import apps
    app_config = apps.get_app_config(app_label)
    entities = []
    for M in app_config.get_models():
        dic = to_dict(M)
        dic['name'] = M.__name__
        options = {}
        for name in OPTIONS:
            value = getattr(M._meta, name)
            if value is None:
                continue
            if hasattr(value, '_proxy____cast'):
                value = value._proxy____cast()
            if name == 'verbose_name':
                # This restriction is on the frontend
                value = M.__name__
            elif name == 'verbose_name_plural':
                value = value.capitalize()
            options[name] = value
            options['indexes'] = []
            for index in M._meta.indexes:
                index_dic = {
                    'fields': index.fields,
                }
                if index.name:
                    index_dic['name'] = index.name
                options['indexes'].append(index_dic)
        dic.update(options)
        entities.append(dic)

    placing = Placing(entities)
    placing.apply()
    dic = {
        'entities': entities,
        'state': {
            'scrollTop': 0,
            'scrollLeft': 0,
        },
    }
    if entities:
        dic['state'].update({
            'scrollTop': entities[0]['top'],
            'scrollLeft': entities[0]['left'],
        })
    return dic


def to_dict(model):
    def keyfunc(f):
        if hasattr(f, 'field'):
            f = f.field
        return f.creation_counter
    fields = sorted(model._meta.get_fields(), key=keyfunc)
    attrs = []
    
    parent = None
    parent_fields = []
    for parent in model._meta.parents:
        parent_fields = parent._meta.get_fields()
    for field in fields:
        if not hasattr(field, 'deconstruct'):
            continue
        if field in parent_fields:
            continue
        attr = Field.to_dict(field)
        if attr:
            attrs.append(attr)

    return {
        'name': model.__name__,
        'attributes': attrs,
        'inheritsFrom': parent and parent.__name__,
    }


import inspect

class Field:

    @classmethod
    def to_dict(cls, field):
        name, callable, args, kwargs = field.deconstruct()
        kwargs['name'] = name
        kwargs['type'] = callable.split('.')[-1]
        assert not args
        if kwargs['type'] == 'AutoField' and name == 'id':
            return None
        kwargs = cls.transform(kwargs, field)
        if kwargs is None:
            return None
        for k, v in tuple(kwargs.items()):
            if inspect.isfunction(v) and v.__name__.isupper():
                kwargs[k] = v.__name__
        kwargs.setdefault('objectType', 'attribute')
        return kwargs
    
    @classmethod
    def transform(cls, dic, field):
        if 'to' in dic:
            dic['to'] = dic['to'].split('.')[-1]
            if 'related_name' in dic:
                dic['is_related_name_implicit'] = False
            else:
                dic['related_name'] = field.rel.name
                dic['is_related_name_implicit'] = True
            dic['objectType'] = 'attributeRelationship'
        if dic.get('parent_link'):
            return None
        return dic
