#!/usr/bin/env python3
"""P43 S90 exact rational polyhedral kernel.

Standard library only, exact `Fraction` arithmetic everywhere.  No floating
point value ever enters a decision.  The kernel knows nothing about P43
semantics: it provides convex polytopes, their boundaries, exact volumes and
the perpendicular-bisector construction used by C033.
"""

from __future__ import annotations

from fractions import Fraction as Q
from itertools import combinations
from math import gcd
from typing import Iterable, Sequence


Point = tuple[Q, Q, Q]
Plane = tuple[tuple[int, int, int], Q]  # primitive integer normal, offset


# --------------------------------------------------------------------------
# vector arithmetic
# --------------------------------------------------------------------------


def add(first: Sequence[Q], second: Sequence[Q]) -> Point:
    return (first[0] + second[0], first[1] + second[1], first[2] + second[2])


def subtract(first: Sequence[Q], second: Sequence[Q]) -> Point:
    return (first[0] - second[0], first[1] - second[1], first[2] - second[2])


def scale(factor: Q, vector: Sequence[Q]) -> Point:
    return (factor * vector[0], factor * vector[1], factor * vector[2])


def dot(first: Sequence[Q], second: Sequence[Q]) -> Q:
    return first[0] * second[0] + first[1] * second[1] + first[2] * second[2]


def cross(first: Sequence[Q], second: Sequence[Q]) -> Point:
    return (
        first[1] * second[2] - first[2] * second[1],
        first[2] * second[0] - first[0] * second[2],
        first[0] * second[1] - first[1] * second[0],
    )


def squared_norm(vector: Sequence[Q]) -> Q:
    return dot(vector, vector)


def average(points: Iterable[Sequence[Q]]) -> Point:
    rows = list(points)
    total = (Q(0), Q(0), Q(0))
    for row in rows:
        total = add(total, row)
    return scale(Q(1, len(rows)), total)


def is_zero(vector: Sequence[Q]) -> bool:
    return vector[0] == 0 and vector[1] == 0 and vector[2] == 0


# --------------------------------------------------------------------------
# planes
# --------------------------------------------------------------------------


def primitive(vector: Sequence[Q]) -> tuple[int, int, int]:
    """Smallest integer vector positively proportional to `vector`."""
    if is_zero(vector):
        raise ValueError("zero vector has no primitive representative")
    denominator = 1
    for value in vector:
        denominator = denominator * value.denominator // gcd(
            denominator, value.denominator
        )
    integers = [int(value * denominator) for value in vector]
    divisor = 0
    for value in integers:
        divisor = gcd(divisor, abs(value))
    integers = [value // divisor for value in integers]
    return (integers[0], integers[1], integers[2])


def plane_key(normal: Sequence[Q], offset: Q) -> Plane:
    """Canonical oriented plane `normal . x = offset`.

    The orientation is retained: `(n, h)` and `(-n, -h)` are different keys,
    because a halfspace needs its side.
    """
    integer_normal = primitive(normal)
    factor = None
    for index in range(3):
        if normal[index] != 0:
            factor = Q(integer_normal[index]) / normal[index]
            break
    return integer_normal, offset * factor


def unoriented_plane_key(normal: Sequence[Q], offset: Q) -> Plane:
    """Canonical plane forgetting the side, used to group coplanar patches."""
    key_normal, key_offset = plane_key(normal, offset)
    negated = (-key_normal[0], -key_normal[1], -key_normal[2])
    if negated < key_normal:
        return negated, -key_offset
    return key_normal, key_offset


def plane_through(first: Point, second: Point, third: Point) -> tuple[Point, Q]:
    normal = cross(subtract(second, first), subtract(third, first))
    if is_zero(normal):
        raise ValueError("collinear triple has no plane")
    return normal, dot(normal, first)


def outward_plane(facet_points: Sequence[Point], interior: Point) -> tuple[Point, Q]:
    """Supporting plane of a facet, oriented away from `interior`."""
    for triple in combinations(range(len(facet_points)), 3):
        try:
            normal, offset = plane_through(*(facet_points[i] for i in triple))
        except ValueError:
            continue
        if dot(normal, interior) > offset:
            normal, offset = scale(Q(-1), normal), -offset
        if dot(normal, interior) == offset:
            continue
        return normal, offset
    raise ValueError("facet points are collinear")


def reflect_point(point: Point, normal: Sequence[Q], offset: Q) -> Point:
    """Mirror `point` in the plane `normal . x = offset`."""
    factor = 2 * (offset - dot(normal, point)) / squared_norm(normal)
    return add(point, scale(factor, normal))


def bisector_halfspace(center: Point, site: Point) -> tuple[Point, Q]:
    """`{x : |x - center| <= |x - site|}` as `normal . x <= offset`."""
    normal = scale(Q(2), subtract(site, center))
    offset = squared_norm(site) - squared_norm(center)
    return normal, offset


# --------------------------------------------------------------------------
# convex polytopes from points
# --------------------------------------------------------------------------


def hull_facets(points: Sequence[Point]) -> list[tuple[tuple[Point, Q], list[int]]]:
    """Exact facet list of `conv(points)` for a small full-dimensional set.

    Returns oriented outward planes with the index list of the points lying on
    them.  Brute force over triples: intended for the small configurations of
    this project, not for large inputs.
    """
    count = len(points)
    interior = average(points)
    seen: dict[Plane, list[int]] = {}
    for triple in combinations(range(count), 3):
        try:
            normal, offset = plane_through(*(points[i] for i in triple))
        except ValueError:
            continue
        above = False
        below = False
        for index in range(count):
            value = dot(normal, points[index])
            if value > offset:
                above = True
            elif value < offset:
                below = True
        if above and below:
            continue
        if not above and not below:
            raise ValueError("point set is not full dimensional")
        if above:
            normal, offset = scale(Q(-1), normal), -offset
        on_plane = [
            index
            for index in range(count)
            if dot(normal, points[index]) == offset
        ]
        seen[plane_key(normal, offset)] = on_plane
    facets = []
    for (integer_normal, offset), on_plane in seen.items():
        normal = (Q(integer_normal[0]), Q(integer_normal[1]), Q(integer_normal[2]))
        if dot(normal, interior) >= offset:
            raise ValueError("interior point is not strictly inside")
        facets.append(((normal, offset), sorted(on_plane)))
    facets.sort(key=lambda row: row[1])
    return facets


def cyclic_order(points: Sequence[Point], normal: Sequence[Q]) -> list[int]:
    """Cyclic order of coplanar points around their centroid, exactly."""
    center = average(points)
    first = None
    for index, point in enumerate(points):
        if not is_zero(subtract(point, center)):
            first = subtract(point, center)
            break
    if first is None:
        raise ValueError("degenerate polygon")
    second = cross(normal, first)

    def sector(index: int) -> tuple[int, Q, Q]:
        vector = subtract(points[index], center)
        x_value = dot(vector, first)
        y_value = dot(vector, second)
        if y_value > 0 or (y_value == 0 and x_value > 0):
            half = 0
        else:
            half = 1
        return half, x_value, y_value

    def less(left: int, right: int) -> bool:
        left_key = sector(left)
        right_key = sector(right)
        if left_key[0] != right_key[0]:
            return left_key[0] < right_key[0]
        determinant = left_key[1] * right_key[2] - left_key[2] * right_key[1]
        return determinant > 0

    order = list(range(len(points)))
    for outer in range(1, len(order)):
        position = outer
        while position > 0 and less(order[position], order[position - 1]):
            order[position - 1], order[position] = (
                order[position],
                order[position - 1],
            )
            position -= 1
    return order


# --------------------------------------------------------------------------
# convex polytopes from halfspaces
# --------------------------------------------------------------------------


class Polytope:
    """Bounded intersection of halfspaces `normal . x <= offset`."""

    def __init__(self, halfspaces: Sequence[tuple[Point, Q]]):
        self.halfspaces = [
            (normal, offset) for normal, offset in halfspaces
        ]
        self.vertices: list[Point] = []
        self.active: list[int] = []
        self.bounded = False
        self._solve()

    def _solve(self) -> None:
        count = len(self.halfspaces)
        if count < 4:
            return
        if not self._is_bounded():
            return
        found: dict[tuple[str, str, str], Point] = {}
        for triple in combinations(range(count), 3):
            point = self._corner(triple)
            if point is None:
                continue
            if not self.contains(point):
                continue
            found[tuple(str(value) for value in point)] = point
        self.vertices = sorted(found.values())
        if len(self.vertices) < 4:
            return
        self.bounded = True
        self.active = [
            index
            for index in range(count)
            if len(self.on_plane(index)) >= 3
        ]

    def _corner(self, triple: tuple[int, int, int]) -> Point | None:
        (n0, h0), (n1, h1), (n2, h2) = (self.halfspaces[i] for i in triple)
        determinant = dot(n0, cross(n1, n2))
        if determinant == 0:
            return None
        term = add(
            add(scale(h0, cross(n1, n2)), scale(h1, cross(n2, n0))),
            scale(h2, cross(n0, n1)),
        )
        return scale(Q(1, 1) / determinant, term)

    def _is_bounded(self) -> bool:
        """True when `{d : n_k . d <= 0 for all k}` is trivial.

        Every extreme ray of that cone lies on at least two of the bounding
        planes, so testing the cross products of all normal pairs (and the
        normals themselves) is exhaustive.
        """
        normals = [normal for normal, _ in self.halfspaces]
        candidates: list[Point] = []
        for left, right in combinations(range(len(normals)), 2):
            direction = cross(normals[left], normals[right])
            if not is_zero(direction):
                candidates.append(direction)
                candidates.append(scale(Q(-1), direction))
        for normal in normals:
            candidates.append(scale(Q(-1), normal))
        for direction in candidates:
            if all(dot(normal, direction) <= 0 for normal in normals):
                return False
        return True

    def contains(self, point: Point) -> bool:
        return all(
            dot(normal, point) <= offset for normal, offset in self.halfspaces
        )

    def interior_contains(self, point: Point) -> bool:
        return all(
            dot(normal, point) < offset for normal, offset in self.halfspaces
        )

    def on_plane(self, index: int) -> list[Point]:
        normal, offset = self.halfspaces[index]
        return [
            vertex for vertex in self.vertices if dot(normal, vertex) == offset
        ]

    def volume(self) -> Q:
        if not self.bounded:
            raise ValueError("unbounded polytope has no finite volume")
        apex = self.vertices[0]
        total = Q(0)
        counted: set[Plane] = set()
        for index in self.active:
            normal, offset = self.halfspaces[index]
            key = plane_key(normal, offset)
            if key in counted:
                continue  # a repeated halfspace must not contribute twice
            counted.add(key)
            face = self.on_plane(index)
            if len(face) < 3:
                continue
            if dot(normal, apex) == offset:
                continue
            order = cyclic_order(face, normal)
            ordered = [face[position] for position in order]
            for step in range(1, len(ordered) - 1):
                total += abs(
                    dot(
                        subtract(ordered[0], apex),
                        cross(
                            subtract(ordered[step], apex),
                            subtract(ordered[step + 1], apex),
                        ),
                    )
                )
        return total / 6


def convex_hull_volume(points: Sequence[Point]) -> Q:
    """Exact volume of `conv(points)` for a small full-dimensional set."""
    interior = average(points)
    total = Q(0)
    for (normal, offset), indices in hull_facets(points):
        face = [points[index] for index in indices]
        order = cyclic_order(face, normal)
        ordered = [face[position] for position in order]
        for step in range(1, len(ordered) - 1):
            total += abs(
                dot(
                    subtract(ordered[0], interior),
                    cross(
                        subtract(ordered[step], interior),
                        subtract(ordered[step + 1], interior),
                    ),
                )
            )
    return total / 6


def intersection_volume(
    left: Sequence[tuple[Point, Q]], right: Sequence[tuple[Point, Q]]
) -> Q:
    """Exact volume of the intersection of two bounded halfspace systems."""
    joint = Polytope(list(left) + list(right))
    if not joint.bounded:
        return Q(0)
    return joint.volume()


# --------------------------------------------------------------------------
# exact polygon comparison
# --------------------------------------------------------------------------


def point_key(point: Sequence[Q]) -> tuple[str, str, str]:
    return (str(point[0]), str(point[1]), str(point[2]))


def point_set_key(points: Iterable[Sequence[Q]]) -> tuple[tuple[str, str, str], ...]:
    return tuple(sorted(point_key(point) for point in points))
