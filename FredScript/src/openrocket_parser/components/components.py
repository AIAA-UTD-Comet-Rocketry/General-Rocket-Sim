"""
Components collects a
"""

import logging
from typing import Type, List
from xml.etree.ElementTree import Element
from abc import ABC, abstractmethod

COMPONENT_REGISTRY = {}
def register_component(tag_name: str):
    """A decorator to automatically register component classes in the factory."""

    def decorator(cls: Type['XMLComponent']):
        print(f"Registering {tag_name} → {cls}")
        COMPONENT_REGISTRY[tag_name] = cls
        return cls

    return decorator


def component_factory(element: Element, parent) -> 'XMLComponent':
    """Creates a component instance based on the XML element's tag."""
    tag = element.tag
    component_class = COMPONENT_REGISTRY.get(tag)

    print("Component reg at this poitn:")
    print(COMPONENT_REGISTRY)
    print(f"Component we just came across: {tag}")
    print(f"Component class is {component_class}")

    if component_class:
        return component_class(element, parent)

    print(f"No specific class found for tag '{tag}'. Using default Subcomponent.")
    if(tag == "name" or tag == "id"):
        return None
    # Fallback to a generic component if the tag is not recognized.
    return Subcomponent(element, parent)


class XMLComponent(ABC):
    bodyTubeNumbah = 0
    """
    An improved base class for all XML-based components.

    It uses a declarative `_FIELDS` map to automatically parse and assign attributes,
    reducing boilerplate code in subclasses.
    """
    # Define fields to be parsed from XML.
    # Format: ('attribute_name', 'xml_path', type_conversion_function, default_value)
    _FIELDS = [
        ('name', './name', str, lambda e: e.tag),  # Use a lambda for dynamic default
        ('id', './id', str, None),
        ('configid', './configid', str, None),
    ]

    def __init__(self, element: Element, parent):
        if element is None:
            raise ValueError("Cannot initialize XMLComponent with a None element.")
        self.element: Element = element
        self.tag: str = element.tag
        self.parent = parent

        # Automatically parse all fields defined in the class hierarchy
        all_fields = []
        for cls in reversed(self.__class__.__mro__):
            if hasattr(cls, '_FIELDS'):
                all_fields.extend(cls._FIELDS)

        for attr_name, path, converter, default in all_fields:
            print(f"Also the tag is {self.tag} and the element is {self.element} and the path is {path}")
            self._parse_and_set_attr(attr_name, path, converter, default, self.tag)

    def _parse_and_set_attr(self, attr_name, path, converter, default, elemName):
        if(attr_name == "position"):
            actualElement = self.element.find(path)
            if actualElement is None:
                print(f"Couldn't find attribute! The path was {path}, the actual element name is {elemName}, and the parent is {self.parent}")
                return
            posType = actualElement.attrib.get("type")
            if(posType is not None):
                setattr(self, f"{elemName}_positionType", posType)
        elif(attr_name == "motorconfiguration"):
            actualElement = self.element.find(path)
            isDefault = actualElement.attrib.get("default")
            motorId = actualElement.attrib.get("configid")
            if(isDefault is not None and motorId is not None):
                setattr(self, f"{elemName}_isDefaultMotor", isDefault)
                setattr(self, f"{elemName}_motorIDConfig", motorId)
        elif(attr_name == "motor"):
            actualElement = self.element.find(path)
            id = actualElement.attrib.get("configid")
            if id is not None:
                setattr(self, "id", id)
        elif(elemName == "bodytube"):
            if(path != "./configid" and path != "./innerradius" and path != "./length" and path != "./outerradius"):
                print(f"Bodytube path is {path}, attribute name is {attr_name}")
                actualElement = self.element.find(path)
                id = actualElement.attrib.get("id")
                setattr(self, f"bbodyTube_{id}_Number", XMLComponent.bodyTubeNumbah)
                XMLComponent.bodyTubeNumbah += 1
        elif(elemName == "trapezoidfinset"):
            parentId = self.parent.get("id")            
            if parentId is not None:
                setattr(self, "finsParentId", parentId)

        """Finds text in XML, converts it, and sets it as an attribute."""
        raw_value = self.element.findtext(path)
        if raw_value is not None:
            try:
                value = converter(raw_value)
            except (ValueError, TypeError) as e:
                logging.error(
                    f"Could not convert value '{raw_value}' for '{attr_name}' using {converter.__name__}. Error: {e}")
                value = default() if callable(default) else default
        else:
            value = default(self.element) if callable(default) else default

        setattr(self, attr_name, value)

    def findall(self, path: str) -> List[Element]:
        """Convenience wrapper for element.findall."""
        return self.element.findall(path)
    
    @abstractmethod
    def getDictVals(self) -> dict:
        pass

    @staticmethod
    def get_float(value_str: str) -> float:
        """Robustly converts a string to a float, handling 'auto' values."""
        if value_str is None:
            return 0.0
        clean_str = value_str.strip().lower()
        # Handle the auto values so they don't break the entire conversion
        if clean_str.startswith('auto'):
            clean_str = clean_str.replace('auto', '').strip()
            if not clean_str:
                return 0.0
        return float(clean_str)

    @staticmethod
    def get_bool(value_str: str) -> bool:
        """Converts a string to a boolean."""
        if value_str is None:
            return False
        return value_str.strip().lower() in ['true', 'yes', '1']

@register_component('subcomponent')
class Subcomponent(XMLComponent):
    """"
    Subcomponents enables shared functionality for all components - such as length, radius, material, etc
    """
    _FIELDS = [
        ('length', './length', XMLComponent.get_float, 0.0),
        ('radius', './radius', XMLComponent.get_float, 0.0),
        ('position', './position', XMLComponent.get_float, 0.0),
        ('material', './material', str, 'Unknown'),
        ('thickness', './thickness', XMLComponent.get_float, 0.0),
        ('outerradius', './outerradius', XMLComponent.get_float, 0.0),
        ('innerradius', './innerradius', XMLComponent.get_float, 0.0),
    ]

    def __init__(self, element: Element, parent):
        super().__init__(element, parent)
        self.subcomponents: List[XMLComponent] = [
            component_factory(e, element) for e in self.findall('./subcomponents/*')
        ]

    def getDictVals(self) -> dict:
        return {}

@register_component('bulkhead')
class Bulkhead(Subcomponent):
    _FIELDS = [
        ('id', './id', str, 'none'),
        ('instancecount', './instancecount', int, 1),
        ('instanceseparation', './instanceseparation', XMLComponent.get_float, 0.0),
        ('axialoffset', './axialoffset', XMLComponent.get_float, 0.0),
        ('position', './position', XMLComponent.get_float, 0.0),
        ('overridemass', './overridemass', XMLComponent.get_float, 0.0),
        ('overridesubcomponentsmass', './overridesubcomponentsmass', XMLComponent.get_bool, False),
        ('material', './material', str, 'Unknown'),
        ('length', './length', XMLComponent.get_float, 0.0),
        ('radialposition', './radialposition', XMLComponent.get_float, 0.0),
        ('radialdirection', './radialdirection', XMLComponent.get_float, 0.0),
        ('outerradius', './outerradius', XMLComponent.get_float, 0.0),
    ]

    def getDictVals(self) -> dict:
        return {
            f"bulkhead_{self.id}_mass": self.overridemass
        }

@register_component('shockcord')
class ShockCord(Subcomponent):
    _FIELDS = [
        ('id', './id', str, 'none'),
        ('axialoffset', './axialoffset', XMLComponent.get_float, 0.0),
        ('position', './position', XMLComponent.get_float, 0.0),
        ('overridemass', './overridemass', XMLComponent.get_float, 0.0),
        ('overridesubcomponentsmass', './overridesubcomponentsmass', XMLComponent.get_bool, False),
        ('packedlength', './packedlength', XMLComponent.get_float, 0.0),
        ('packedradius', './packedradius', XMLComponent.get_float, 0.0),
        ('radialposition', './radialposition', XMLComponent.get_float, 0.0),
        ('radialdirection', './radialdirection', XMLComponent.get_float, 0.0),
        ('cordlength', './cordlength', XMLComponent.get_float, 0.0),
        ('material', './material', str, 'Unknown'),
    ]

    def getDictVals(self) -> dict:
        return {
            f"shockCord_{self.id}_mass": self.overridemass
        }

@register_component('tubecoupler')
class TubeCoupler(Subcomponent):
    _FIELDS = [
        ('axialoffset', './axialoffset', XMLComponent.get_float, 0.0),
        ('position', './position', XMLComponent.get_float, 0.0),
        ('overridemass', './overridemass', XMLComponent.get_float, 0.0),
        ('overridesubcomponentsmass', './overridesubcomponentsmass', XMLComponent.get_bool, False),
        ('material', './material', str, 'Unknown'),
        ('length', './length', XMLComponent.get_float, 0.0),
        ('radialposition', './radialposition', XMLComponent.get_float, 0.0),
        ('radialdirection', './radialdirection', XMLComponent.get_float, 0.0),
        ('outerradius', './outerradius', XMLComponent.get_float, 0.0),
        ('thickness', './thickness', XMLComponent.get_float, 0.0),
        ('id', './id', str, 'none'),
    ]

    def getDictVals(self) -> dict:
        return {
            f"coupler_{self.id}_mass": self.overridemass,
        }

@register_component('parachute')
class Parachute(Subcomponent):
    _FIELDS = [
        ('id', './id', str, 'none'),
        ('axialoffset', './axialoffset', XMLComponent.get_float, 0.0),
        ('position', './position', XMLComponent.get_float, 0.0),
        ('overridemass', './overridemass', XMLComponent.get_float, 0.0),
        ('overridesubcomponentsmass', './overridesubcomponentsmass', XMLComponent.get_bool, False),
        ('packedlength', './packedlength', XMLComponent.get_float, 0.0),
        ('packedradius', './packedradius', XMLComponent.get_float, 0.0),
        ('radialposition', './radialposition', XMLComponent.get_float, 0.0),
        ('radialdirection', './radialdirection', XMLComponent.get_float, 0.0),
        ('cd', './cd', XMLComponent.get_float, 0.0),
        ('material', './material', str, 'Unknown'),
        ('deployevent', './deployevent', str, 'ejection'),
        ('deployaltitude', './deployaltitude', XMLComponent.get_float, 0.0),
        ('deploydelay', './deploydelay', XMLComponent.get_float, 0.0),
        ('diameter', './diameter', XMLComponent.get_float, 0.0),
        ('linecount', './linecount', int, 0),
        ('linelength', './linelength', XMLComponent.get_float, 0.0),
        ('linematerial', './linematerial', str, 'Unknown'),
    ]

    def getDictVals(self) -> dict:
        triggerVal = None
        if(self.deployevent == "ejection" or self.deployevent == "apogee"):
            triggerVal = "apogee"
        elif(self.deployevent == "altitude"):
            triggerVal = self.deployaltitude
        return {
            "parachute_cd": self.cd,
            "parachute_trigger": triggerVal,
            "parachute_lag": self.deploydelay,
            f"parachute_{self.id}_mass": self.overridemass
        }
    

@register_component('railbutton')
class RailButton(Subcomponent):
    _FIELDS = [
        ('instancecount', './instancecount', int, 1),
        ('instanceseparation', './instanceseparation', XMLComponent.get_float, 0.0),
        ('angleoffset', './angleoffset', XMLComponent.get_float, 0.0),
        ('axialoffset', './axialoffset', XMLComponent.get_float, 0.0),
        ('position', './position', XMLComponent.get_float, 0.0),
        ('overridemass', './overridemass', XMLComponent.get_float, 0.0),
        ('overridesubcomponentsmass', './overridesubcomponentsmass', XMLComponent.get_bool, False),
        ('finish', './finish', str, 'smooth'),
        ('material', './material', str, 'Unknown'),
        ('outerdiameter', './outerdiameter', XMLComponent.get_float, 0.0),
        ('innerdiameter', './innerdiameter', XMLComponent.get_float, 0.0),
        ('height', './height', XMLComponent.get_float, 0.0),
        ('baseheight', './baseheight', XMLComponent.get_float, 0.0),
        ('flangeheight', './flangeheight', XMLComponent.get_float, 0.0),
        ('screwheight', './screwheight', XMLComponent.get_float, 0.0),
        ('rail_id', './id', str, "-1")
    ]

    def getDictVals(self) -> dict:
        return {
            "rail_id": self.rail_id,
            f"rail_{self.rail_id}_position": self.position,
            f"rail_{self.rail_id}_positionType": self.railbutton_positionType,
            f"rail_{self.rail_id}_angle": self.angleoffset,
            f"rail_{self.rail_id}_mass": self.overridemass
        }
    
@register_component('motorconfiguration')
class MotorConfig(Subcomponent):
    _FIELDS = [
        ('configid', './configid', str, "None"),
    ]

    def getDictVals(self) -> dict:        
        if hasattr(self, "motorconfiguration_isDefaultMotor"):
            return {
                "motor_config_id": self.motorconfiguration_motorIDConfig,
            }
        else:
            return {}
        
@register_component('masscomponent')
class MassComponent(Subcomponent):
    _FIELDS = [
        ('id', './id', str, "-1"),
        ('axialoffset', './axialoffset', XMLComponent.get_float, 0.0),
        ('position', './position', XMLComponent.get_float, 0.0),
        ('overridemass', './overridemass', XMLComponent.get_float, 0.0),
        ('overridesubcomponentsmass', './overridesubcomponentsmass', XMLComponent.get_bool, False),
        ('packedlength', './packedlength', XMLComponent.get_float, 0.0),
        ('packedradius', './packedradius', XMLComponent.get_float, 0.0),
        ('radialposition', './radialposition', XMLComponent.get_float, 0.0),
        ('radialdirection', './radialdirection', XMLComponent.get_float, 0.0),
        ('mass', './mass', XMLComponent.get_float, 0.0),
        ('masscomponenttype', './masscomponenttype', str, 'masscomponent'),
    ]

    def getDictVals(self) -> dict:        
        return {
                f"addedMass_{self.id}": self.overridemass,
            }

@register_component('innertube')
class InnerTube(Subcomponent):
    _FIELDS = [
        ('id', './id', str, "-1"),
        ('axialoffset', './axialoffset', XMLComponent.get_float, 0.0),
        ('position', './position', XMLComponent.get_float, 0.0),
        ('overridemass', './overridemass', XMLComponent.get_float, 0.0),
        ('overridesubcomponentsmass', './overridesubcomponentsmass', XMLComponent.get_bool, False),
        ('material', './material', str, 'Unknown'),
        ('length', './length', XMLComponent.get_float, 0.0),
        ('radialposition', './radialposition', XMLComponent.get_float, 0.0),
        ('radialdirection', './radialdirection', XMLComponent.get_float, 0.0),
        ('outerradius', './outerradius', XMLComponent.get_float, 0.0),
        ('thickness', './thickness', XMLComponent.get_float, 0.0),
        ('clusterconfiguration', './clusterconfiguration', str, 'single'),
        ('clusterscale', './clusterscale', XMLComponent.get_float, 1.0),
        ('clusterrotation', './clusterrotation', XMLComponent.get_float, 0.0),
    ]

    def getDictVals(self) -> dict:        
        return {
                f"innerTube_{self.id}_mass": self.overridemass
            }

@register_component('trapezoidfinset')
class TrapezoidFinSet(Subcomponent):
    _FIELDS = [
        ('instancecount', './instancecount', int, 1),
        ('fincount', './fincount', int, 0),
        ('radiusoffset', './radiusoffset', XMLComponent.get_float, 0.0),
        ('angleoffset', './angleoffset', XMLComponent.get_float, 0.0),
        ('rotation', './rotation', XMLComponent.get_float, 0.0),
        ('axialoffset', './axialoffset', XMLComponent.get_float, 0.0),
        ('position', './position', XMLComponent.get_float, 0.0),
        ('overridemass', './overridemass', XMLComponent.get_float, 0.0),
        ('overridesubcomponentsmass', './overridesubcomponentsmass', XMLComponent.get_bool, False),
        ('finish', './finish', str, 'smooth'),
        ('material', './material', str, 'Unknown'),
        ('thickness', './thickness', XMLComponent.get_float, 0.0),
        ('crosssection', './crosssection', str, 'square'),
        ('cant', './cant', XMLComponent.get_float, 0.0),
        ('tabheight', './tabheight', XMLComponent.get_float, 0.0),
        ('tablength', './tablength', XMLComponent.get_float, 0.0),
        ('tabposition', './tabposition', XMLComponent.get_float, 0.0),
        ('filletradius', './filletradius', XMLComponent.get_float, 0.0),
        ('filletmaterial', './filletmaterial', str, 'Unknown'),
        ('rootchord', './rootchord', XMLComponent.get_float, 0.0),
        ('tipchord', './tipchord', XMLComponent.get_float, 0.0),
        ('sweeplength', './sweeplength', XMLComponent.get_float, 0.0),
        ('height', './height', XMLComponent.get_float, 0.0),
    ]

    def getDictVals(self) -> dict:
        return {
            "fin_sweep_length": self.sweeplength,
            "fin_cant_angle": self.cant,
            "fin_span": self.height,
            "fin_position": self.position,
            "num_fins": self.fincount,
            "root_chord": self.rootchord,
            "tip_chord": self.tipchord,
            "fin_height": self.height,
            "position_version": self.trapezoidfinset_positionType,
            "fin_mass": self.overridemass
        }

@register_component('centeringring')
class CenteringRing(Subcomponent):
    _FIELDS = [
         ('id', './id', str, "-1"),
        ('instancecount', './instancecount', int, 1),
        ('instanceseparation', './instanceseparation', XMLComponent.get_float, 0.0),
        ('axialoffset', './axialoffset', XMLComponent.get_float, 0.0),
        ('position', './position', XMLComponent.get_float, 0.0),
        ('overridemass', './overridemass', XMLComponent.get_float, 0.0),
        ('overridesubcomponentsmass', './overridesubcomponentsmass', XMLComponent.get_bool, False),
        ('material', './material', str, 'Unknown'),
        ('length', './length', XMLComponent.get_float, 0.0),
        ('radialposition', './radialposition', XMLComponent.get_float, 0.0),
        ('radialdirection', './radialdirection', XMLComponent.get_float, 0.0),
        ('outerradius', './outerradius', XMLComponent.get_float, 0.0),
        ('innerradius', './innerradius', XMLComponent.get_float, 0.0),
    ]

    def getDictVals(self) -> dict:
        return {
            f"centeringRing_{self.id}_mass": self.overridemass
        }    