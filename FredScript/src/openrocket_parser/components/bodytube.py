"""
BodyTube Component related functionality
"""


from xml.etree.ElementTree import Element
import math
from openrocket_parser.components.components import (
    XMLComponent, register_component, Subcomponent, component_factory
)


@register_component('bodytube')
class BodyTube(Subcomponent):
    """
    BodyTube Subcomponent from OpenRocket, created when a bodytube xml element is found
    """
    _FIELDS = [
        ('id', './id', str, 'none'),
        ('length', './length', XMLComponent.get_float, 0),
        ('mass', './overridemass', XMLComponent.get_float, 0),
        ('radius', './radius', XMLComponent.get_float, 0)
    ]


    motormount = None
    def __init__(self, element: Element, parent):
        super().__init__(element, parent)
        motor_mount_element = self.element.find('.//motormount')
        if motor_mount_element is not None:
            self.motormount = component_factory(motor_mount_element, element)

    def getDictVals(self) -> dict:
        density = int(float(self.bbodyTube_density))

        alt_mass = density * math.pi * self.length * (self.radius ** 2 - (self.radius - self.thickness) ** 2)
        
        return {
            "rocket_radius": self.radius,
            f"bodyTube_{self.id}_length": self.length,
            f"bodyTube_{self.id}_mass": self.mass,
            f"bodyTube_{self.id}_altMass": alt_mass if self.mass == 0 else 0,
            f"bodyTube_{self.id}_density": density
        }
