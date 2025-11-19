"""
All Motor related functionality to represent OpenRocket motors and motor related subcomponents
"""

from xml.etree.ElementTree import Element

from openrocket_parser.components.components import register_component, XMLComponent, component_factory


@register_component('motor')
class Motor(XMLComponent):
    """
    Motor Subcomponent from OpenRocket, created when a motor xml element is found
    """
    _FIELDS = [
        ('designation', './/designation', str, ''),
        ('manufacturer', './/manufacturer', str, ''),
        ('diameter', './/diameter', XMLComponent.get_float, 0.0),
        ('length', './/length', XMLComponent.get_float, 0.0),
    ]

    def getDictVals(self) -> dict:
        return {
            "motor_name": self.designation,
            "motor_diameter": self.diameter,
            "motor_length": self.length

        }

@register_component('motormount')
class MotorMount(XMLComponent):
    """
    MotorMount Subcomponent from OpenRocket, created when a motormount xml element is found
    """
    _FIELDS = [
        ('ignition_event', './/ignitionevent', str, 'launch'),
        ('overhang', './/overhang', XMLComponent.get_float, 0.0),
        ('diameter', './/diameter', XMLComponent.get_float, 0.0),
        ('length', './/length', XMLComponent.get_float, 0.0),
    ]

    def __init__(self, element: Element, parent):
        super().__init__(element, parent)
        self.motors = [component_factory(e, element) for e in self.findall('.//motor')]
        if(len(self.motors > 1)):
            print("ATTENTION: THERE ARE MULTIPLE MOTORS! Thus, the dictionary mapping the right values may only pick one of the motors! Please change your openrocket to only contain one motor. Or don't, we'll handle it still by selecting whichever was labeled as the current one!")

    def getDictVals(self) -> dict:
        triggerVal = None
        if(self.deployevent == "ejection" or self.deployevent == "apogee"):
            triggerVal = "apogee"
        elif(self.deployevent == "altitude"):
            triggerVal = self.deployaltitude
        return {
            f"motor_{self.id}_diameter": self.cd,
            f"motor_{self.id}_length": self.length
        }