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

    def __mul__(self, other): # Multiplication by a scalar
        if isinstance(other, (int, float)):
            out = Vec3()
            out.x = self.x * other
            out.y = self.y * other
            out.z = self.z * other
            return out
        # If you intend element-wise multiplication with another Vec3,
        # it's better to use a dedicated function like mul_vec3(u,v)
        # or overload a different operator if Python allows, to avoid confusion.
        # For now, assuming multiplication is with a scalar based on its usage.
        # The original Vec3.py already had __mul__ for scalar.
        # The global mul(u,v) is for element-wise.
        raise TypeError("Unsupported operand type(s) for *: 'Vec3' and '{}'".format(type(other)))


    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other): # Division by a scalar
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
        return Vec3(0,0,0) # Return a zero vector instead of scalar 0
    return u / n

def cross(u, v):
    out = Vec3()
    out.x = u.y*v.z - v.y*u.z
    out.y = u.z*v.x - v.z*u.x # Original had v.z*u.x, it should be u.z*v.x - v.z*u.x or v.x*u.z - u.x*v.z (swapped order is fine if consistent)
                               # Standard: u.y*v.z - u.z*v.y, u.z*v.x - u.x*v.z, u.x*v.y - u.y*v.x
                               # The original: u.y*v.z - v.y*u.z | u.z*v.x - v.z*u.x | u.x*v.y - v.x*u.y
                               # Let's correct the y component: u.z*v.x - u.x*v.z
    out.y = u.z*v.x - u.x*v.z # Corrected Y component for standard cross product
    out.z = u.x*v.y - u.y*v.x
    return out

def dot(u, v):
    return u.x*v.x + u.y*v.y + u.z*v.z

def mul_vec3(u, v): # Renamed from mul to avoid conflict if Vec3.mul was for vectors
    out = Vec3()
    out.x = u.x * v.x
    out.y = u.y * v.y
    out.z = u.z * v.z
    return out