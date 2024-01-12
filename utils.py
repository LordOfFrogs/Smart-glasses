import math

class Vector:
    x, y, z = 0, 0, 0
    
    def __init__(self, *args):
        if (len(args) == 3 and isinstance(args[0], (int, float))
            and isinstance(args[1], (int, float)) and isinstance(args[2], (int, float))):
            
            self.init_vector(*args)
    
    def init_vector(self, x: float, y:float, z: float):
        self.x = x
        self.y = y
        self.z = z
        
    def asTuple(self):
        return (self.x, self.y, self.z)
        
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
    
    def __str__(self):
        return f"({self.x}, {self.y}, {self.z})"

class Quaternion:
    a, b, c, d = 0, 0, 0, 0
    
    def __init__(self, *args):
        if len(args) == 0:
            self.init_default()
            
        elif len(args) == 1 and isinstance(args[0], Vector):
            self.init_vector(*args)
            
        elif len(args) == 1 and isinstance(args[0], Quaternion):
            self.init_quat(*args[0].asTuple())
            
        elif (len(args) == 2 and isinstance(args[0], (int, float))
              and isinstance(args[1], Vector)):
            self.init_scalar_vector(*args)
            
        elif (len(args) == 4 
            and isinstance(args[0], (int, float)) and isinstance(args[1], (int, float))
            and isinstance(args[2], (int, float))
            and isinstance(args[3], (int, float))):
            
            self.init_quat(*args)
    
    def init_default(self):
        self.a = 1.0    
    
    def init_vector(self, vec: Vector):
        self.b = vec.x
        self.c = vec.y
        self.d = vec.z
    
    def init_scalar_vector(self, num: float, vec: Vector):
        self.a = num
        self.b = vec.x
        self.c = vec.y
        self.d = vec.z
    
    def init_quat(self, a: float, b: float, c: float, d: float):
        self.a = a
        self.b = b
        self.c = c
        self.d = d
    
    def asTuple(self) -> tuple:
        return (self.a, self.b, self.c, self.d)
    
    def getVector(self) -> Vector:
        return Vector(self.b, self.c, self.d)
    
    def __mul__(self, other: 'Quaternion') -> 'Quaternion':
        other = Quaternion(other)
        
        a_new = self.a*other.a - self.b*other.b - self.c*other.c - self.d*other.d
        b_new = self.a*other.b + self.b*other.a + self.c*other.d - self.d*other.c
        c_new = self.a*other.c - self.b*other.d + self.c*other.a + self.d*other.b
        d_new = self.a*other.d + self.b*other.c - self.c*other.b + self.d*other.a

        return Quaternion(a_new, b_new, c_new, d_new)
    
    def __rmul__(self, other: 'Quaternion') -> 'Quaternion':
        return other.__mul__(self)
    
    def __add__(self, num: float) -> 'Quaternion':
        return Quaternion(self.a+num, self.b, self.c, self.d)
    
    def conjugate(self) -> 'Quaternion':
        return Quaternion(self.a, -self.b, -self.c, -self.c)
    
    def __str__(self):
        return f"({self.a}, {self.b}, {self.c}, {self.d})"