import math

class Vector:
    x, y, z = 0.0
    
    def __init__(self):
        pass
    
    def __init__(self, x: float, y:float, z: float):
        self.x = x
        self.y = y
        self.z = z
        
    def __add__(self, other: 'Vector') -> 'Vector':
        return Vector(self.x+other.x, self.y+other.y, self.z+other.z)
    
    def dot(self, other: 'Vector') -> float:
        return self.x*other.x + self.y*other.y + self.z*other.z
    
    def cross(self, other: 'Vector') -> 'Vector':
        x_new = self.y*other.z - self.z*other.y
        y_new = self.z*other.x - self.x*other.z
        z_new = self.x*other.y - self.y*other.x
        
        return Vector(x_new, y_new, z_new)
    
    def __mul__(self, num: float) -> 'Vector':
        return Vector(num*self.x, num*self.y, num*self.z)
    
    def __rmul__(self, num: float) -> 'Vector':
        return self.__mul__(num)
    
    def magnitude(self) -> float:
        return math.sqrt(self.x**2+self.y**2+self.z**2)
    
    def azimuth(self) -> float:
        return math.degrees(math.atan2(self.y, self.x))
    
    def inclination(self) -> float:
        return 90 - math.degrees(math.acos(self.z / self.magnitude()))

class Quaternion:
    a, b, c, d = 0.0
    
    def __init__(self):
        self.a = 1.0
        
    def __init__(self, vec: Vector):
        self.b = vec.x
        self.c = vec.y
        self.d = vec.z
    
    def __init__(self, a: float, b: float, c: float, d: float):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
    
    def asTuple(self) -> tuple:
        return (self.a, self.b, self.c, self.d)
    
    def getVector(self) -> Vector:
        return Vector(self.b, self.c, self.d)
    
    def __mul__(self, other: 'Quaternion') -> 'Quaternion':
        vec = self.getVector()
        vec1 = other.getVector()
        
        scalar_part = self.a*other.a - vec.dot(vec1)
        vector_part = self.a*vec1 + other.a*vec + vec.cross(vec1)
        return scalar_part + vector_part
    
    def __rmul__(self, other: 'Quaternion') -> 'Quaternion':
        return self.__mul__(other)
    
    def __add__(self, num: float) -> 'Quaternion':
        return Quaternion(self.a+num, self.b, self.c, self.d)
    
    def conjugate(self) -> 'Quaternion':
        return Quaternion(self.a, -self.b, -self.c, -self.c)

def normalize_angle(angle: float):
    """Normalize angle to between -180 and 180 degrees

    Args:
        angle (float): Angle in degrees
    """
    norm = angle % 360 # [-360,360]
    norm = (norm + 360) % 360 # [0,360]
    norm = (norm + 180) % 360 - 180 # [-180,180]
    return norm