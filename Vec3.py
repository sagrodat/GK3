import math


class Vec3:
    def __init__(self, x=0, y=0, z=0):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return "({} {} {})".format(self.x, self.y, self.z)

    def __eq__(self, other):
        return (self.x == other.x) & (self.y == other.y) & (self.z == other.z)

    def __add__(self, other):
        out = Vec3()
        out.x = self.x + other.x
        out.y = self.y + other.y
        out.z = self.z + other.z
        return out

    def __sub__(self, other):
        out = Vec3()
        out.x = self.x - other.x
        out.y = self.y - other.y
        out.z = self.z - other.z
        return out

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            out = Vec3()
            out.x = self.x * other
            out.y = self.y * other
            out.z = self.z * other
            return out
        # Ten operator obsługuje mnożenie przez skalar.
        # Do mnożenia element po elemencie z innym obiektem Vec3,
        # użyj dedykowanej funkcji mul_vec3(u,v), aby uniknąć niejednoznaczności.
        raise TypeError("Unsupported operand type(s) for *: 'Vec3' and '{}'".format(type(other)))


    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            out = Vec3()
            out.x = self.x / other
            out.y = self.y / other
            out.z = self.z / other
            return out
        raise TypeError("Unsupported operand type(s) for /: 'Vec3' and '{}'".format(type(other)))


def norm(v):
    return math.sqrt(v.x*v.x + v.y*v.y + v.z*v.z)

def normalize(u):
    n = norm(u)
    if n == 0:
        return Vec3(0,0,0) # Zwraca wektor zerowy, gdy norma wektora wynosi zero.
    return u / n

def cross(u, v):
    out = Vec3()
    out.x = u.y*v.z - v.y*u.z
    out.y = u.z*v.x - u.x*v.z # Poprawiona składowa Y dla standardowego iloczynu wektorowego
    out.z = u.x*v.y - u.y*v.x
    return out

def dot(u, v):
    return u.x*v.x + u.y*v.y + u.z*v.z

def mul_vec3(u, v): # Nazwa zmieniona z 'mul', aby uniknąć konfliktu z metodą __mul__ klasy Vec3 (mnożenie przez skalar).
    out = Vec3()
    out.x = u.x * v.x
    out.y = u.y * v.y
    out.z = u.z * v.z
    return out