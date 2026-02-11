"""
Rocket component related functionality. This is the top level component,
and all other components and subcomponents will be within the Rocket
"""

from xml.etree.ElementTree import Element

from openrocket_parser.components.components import register_component, XMLComponent, component_factory

import openrocket_parser.components.bodytube
import openrocket_parser.components.finset
import openrocket_parser.components.motor
import openrocket_parser.components.nosecone
import openrocket_parser.components.stage

@register_component('rocket')
class Rocket(XMLComponent):
    """
    Rocket Main component, created once the rocket xml element is found in the .ork file
    Supports multi-stage setups
    """
    _FIELDS = [
        ("designer", ".//designer", str, "Unknown"),
        ("name", ".//name", str, "Unknown")
    ]


    def __init__(self, element: Element, parent):
        self.rocketpyElems = {}
        super().__init__(element, parent)

        self.stages = [component_factory(e, element) for e in self.findall('.//stage//')]

        self.stages.extend([component_factory(e, element) for e in self.findall('.//motorconfiguration')])

        tagSet = [e.tag for e in self.findall('.//stage//')]
        
        tagSet.extend([e.tag for e in self.findall('.//motorconfiguration')])

        print("IMAGES ARE:")
        print(tagSet)

        for stage in self.stages:
            if stage is None:
                print(f"THEY THIS ELEMENT DOESN'T EXIST! IT IS: {stage}")
            else:
                print(f"Element is: {stage.element}")
                self.rocketpyElems.update(stage.getDictVals())
                print(f"The elements at this stage are: {stage.getDictVals()}")

    def getDictVals(self) -> dict:
        return {}