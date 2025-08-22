from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl.registries import registry
from .models import Dispatch


@registry.register_document
class DispatchDocument(Document):
    class Index:
        name = 'dispatch'
        settings = {'number_of_shards': 1,
                    'number_of_replicas': 0}

    class Django:
        model = Dispatch
        fields = [
            'client_name',
            'building_name',
            'escalation_type',
            'msp',
            'fdp',
            'sla_timer',
            'status',
            'comments',
        ]
