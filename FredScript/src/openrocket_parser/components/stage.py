"""
Stage Component related functionality
"""

from typing import List
from xml.etree.ElementTree import Element

from openrocket_parser.components.components import register_component, XMLComponent, component_factory


@register_component('stage')
class Stage(XMLComponent):
    """
    Stage component, created after the stage components in the xml
    """
    def __init__(self, element: Element, parent):
        super().__init__(element, parent)
        self.subcomponents: List[XMLComponent] = [
            component_factory(e, element) for e in self.element
        ]
    
    def getDictVals(self) -> dict:
        returnDict = {}
        # for subcomponent in self.subcomponents:
        #     print(f"Current component is: {subcomponent}")
        #     returnDict.update(subcomponent.getDictVals())
        return returnDict