"""Build-25904830 plate geometry models, using explicit local metre coordinates.

Pure calculations only: no game access or creation writes. These helpers model
selected source operations, not native convex-hull construction, placement
validity, glass/opening states, edge strips, GPU output, or collision margins.
"""
import math

VERSION = '1.0.0'
GRID_METRES = 0.08
PLATE_THICKNESS_METRES = 0.01


def _vectors(values, dimensions):
    result = [tuple(float(x) for x in value) for value in values]
    if any(len(p) != dimensions or not all(math.isfinite(x) for x in p) for p in result):
        raise ValueError('Expected finite vectors of the stated dimension')
    return result


def _normal(value):
    normal, = _vectors([value], 3)
    if not math.isclose(sum(x*x for x in normal), 1.0, rel_tol=1e-12, abs_tol=1e-12):
        raise ValueError('Supply the plate unit normal, not its integer facing vector')
    return normal


def clip_polygon(points, planes, coords=None):
    """Clip a closed 2D loop to dot(point-position, normal) <= 0 per plane.

    Each plane is (position, outward_normal). Optional parallel vec2 coordinates
    are interpolated with the same crossing fraction. Returns (points, coords),
    with coords=None when omitted. Preserves the source's boundary duplicates;
    does not validate convexity, repair polygons, or change the caller's lists.
    Mismatched coordinate counts raise here; native error termination is open.
    """
    output = _vectors(points, 2)
    payload = None if coords is None else _vectors(coords, 2)
    if payload is not None and len(payload) != len(output):
        raise ValueError('Point and coordinate counts must match')
    checked_planes = []
    for position, normal in planes:
        position, normal = _vectors([position, normal], 2)
        if normal == (0.0, 0.0):
            raise ValueError('A clipping plane needs a nonzero normal')
        checked_planes.append((position, normal))
    for position, normal in checked_planes:
        clipped = []
        clipped_payload = None if payload is None else []
        origin_distance = sum(p*n for p, n in zip(position, normal))
        for i, start in enumerate(output):
            j = (i+1) % len(output)
            end = output[j]
            d0 = sum(p*n for p, n in zip(start, normal)) - origin_distance
            d1 = sum(p*n for p, n in zip(end, normal)) - origin_distance
            if d0 <= 0:
                clipped.append(start)
                if payload is not None:
                    clipped_payload.append(payload[i])
            if d0 <= 0 < d1:
                a, b, fraction = i, j, d0/(d0-d1)
            elif d1 <= 0 < d0:
                a, b, fraction = j, i, d1/(d1-d0)
            else:
                continue
            clipped.append(tuple(x+(y-x)*fraction for x, y in zip(output[a], output[b])))
            if payload is not None:
                clipped_payload.append(tuple(x+(y-x)*fraction for x, y in zip(payload[a], payload[b])))
        output, payload = clipped, clipped_payload
    return output, payload


def solid_faces(node_positions_m, surface_offset_m, normal):
    """Return two oppositely wound triangle fans for a solid plate's faces.

    Supply the separately calculated support offset explicitly. This is the
    inner-solid surface helper only; it does not add any perimeter strips.
    """
    points = _vectors(node_positions_m, 3)
    offset, = _vectors([surface_offset_m], 3)
    normal = _normal(normal)
    if len(points) < 3:
        raise ValueError('At least three nodes required by the upstream caller')
    front = [tuple(p+o for p, o in zip(point, offset)) for point in points]
    back = [tuple(p-n*PLATE_THICKNESS_METRES for p, n in zip(point, normal)) for point in front]
    return {
        'front': [(front[0], front[i+1], front[i]) for i in range(1, len(front)-1)],
        'back': [(back[0], back[i], back[i+1]) for i in range(1, len(back)-1)],
    }


def collision_point_cloud(node_positions_m, normal):
    """Return server convex-hull INPUTS for an eligible physics plate.

    Eligibility must be checked separately. The source offsets both copies by
    normal*GRID*(0.35,0.45), independent of the visible support-offset selector.
    Does not compute a hull, contacts, mass, inertia, or native shape margins.
    """
    points = _vectors(node_positions_m, 3)
    normal = _normal(normal)
    if len(points) < 3:
        raise ValueError('At least three valid plate nodes required')
    return [tuple(p+n*GRID_METRES*f for p, n in zip(point, normal))
            for point in points for f in (0.35, 0.45)]
