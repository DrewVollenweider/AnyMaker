"""Selected hydraulic chamber/geometry arithmetic from build 25904830.

This is not a force, pressure, structural-mount or native constraint solver.
Guards describe the ordinary model domain, not validation found in the game.
Capacity writes precede extension correction in the reviewed element update.
"""
from dataclasses import dataclass
from powertrain_models import clamp,number,positive,unit

VERSION='1.0.0'


@dataclass(frozen=True)
class ChamberProjection:
    extension:float
    capacity_a_written:float
    capacity_b_written:float


def hydraulic_chambers(quantity_a,quantity_b,total_capacity,measured_extension):
    """Preserve pre-correction chamber-capacity writes and corrected extension."""
    a,b=number(quantity_a),number(quantity_b);capacity=positive(total_capacity)
    if a<0 or b<0:raise ValueError('Nonnegative ordinary quantities required')
    measured=unit(measured_extension)
    if a+b<=capacity:
        extension=clamp(measured,a/capacity,1-b/capacity)
    else:
        extension=a/(a+b)
    return ChamberProjection(clamp(extension,0,1),capacity*measured,capacity*(1-measured))


def cylinder_geometry(length_cells,margin,litres_per_meter,extension):
    """Return native length, nominal capacity, distance target and stroke.

    length_cells is the saved maximum length field; default parser value is 8.
    Actual construction permissions and minimum/maximum UI lengths are separate.
    """
    if type(length_cells) is not int or length_cells<=0:raise ValueError('Positive integer length required')
    margin=positive(margin);litres_per_meter=positive(litres_per_meter);extension=unit(extension)
    length=length_cells*.08;stroke=length*.5-margin
    if stroke<=0:raise ValueError('Nonpositive stroke outside ordinary model domain')
    target=2*margin+stroke+stroke*extension
    return length,length*litres_per_meter,target,stroke


def measured_cylinder_extension(distance,length_cells,margin):
    """Invert the connector's geometry before the chamber correction/clamp."""
    length,_,minimum,stroke=cylinder_geometry(length_cells,margin,1,0)
    return (number(distance)-minimum)/stroke
