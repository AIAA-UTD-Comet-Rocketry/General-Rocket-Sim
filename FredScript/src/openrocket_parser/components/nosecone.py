"""
NoseCone functionality for generic nosecones. Each shape of nosecone may extend this one if it needs
to read completely different fields
"""

from openrocket_parser.components.components import XMLComponent, register_component, Subcomponent


@register_component('nosecone')
class NoseCone(Subcomponent):
    """
    NoseCone Subcomponent from OpenRocket, created when a nosecone xml element is found
    """
    _FIELDS = [
        ('shape', './/shape', str, 'ogive'),
        ('length', '../length', XMLComponent.get_float, 0),
        ('mass', '../overridemass', XMLComponent.get_float, 0)
    ]

    def getDictVals(self) -> dict:
        return {
            "nose_shape": self.shape,
            "nose_length": self.length,
            "nose_mass": self.mass
        }

