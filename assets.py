import math
# Ensure Vec3 imports are correct if you save Vec3.py in a way that affects imports.
# Assuming Vec3.py is in the same directory or Python path.
from Vec3 import Vec3, normalize, dot, cross, norm, mul_vec3 # Added mul_vec3 explicitly


class Ray:
    def __init__(self, o, d):
        self.o = o
        self.d = normalize(d) #

#Todo to be integrated
class Asset:
    def __init__(self, pos=Vec3(0, 0, 0), color=Vec3(1, 1, 1)):
        self.pos = pos
        self.color = color

class Light:
    def __init__(self, pos=Vec3(0,0,0), color=Vec3(1,1,1), strength=1, radius=10):
        self.pos = pos
        self.color = color
        self._strength = strength
        self.radius = radius

    def strength(self, point):
        dist = norm(self.pos - point)
        if dist == 0: # Avoid division by zero if point is exactly at light's position
            return self._strength 
        out = self._strength * min(self.radius*self.radius/(dist*dist), 1.0) # ensure float division
        return out

class Sphere:

    def __init__(self, pos, radius, color=Vec3(1,0,0)):
        self.pos = pos
        self.radius = radius
        self.color = color
        # print("Sphere at {} with radius {} and color {}".format(self.pos, self.radius, self.color)) # Optional print

    def normal(self, v):
        return normalize(v - self.pos) #

    def intersect(self, ray):
        # Ensure ray.o and self.pos are Vec3 objects
        cam_sphere = self.pos - ray.o  # camera sphere distance
        
        # Check if ray origin is inside sphere
        if norm(cam_sphere) < self.radius:
            # Handle ray origin inside sphere:
            # For simplicity, we can say it intersects at ray.o or find the exit point.
            # Current logic might fail or give negative distance.
            # A robust solution would find the forward intersection.
            # For now, let's assume ray origin is outside or on the surface.
            pass # Or implement specific logic for origin inside

        len_cam_sphere = norm(cam_sphere)
        if len_cam_sphere == 0: # Ray origin is at sphere center
             i_point = ray.o + self.radius * ray.d
             return True, i_point

        # Projection of cam_sphere onto ray direction
        t_ca = dot(cam_sphere, ray.d)

        # If sphere is behind the ray's origin and ray is pointing away
        # if t_ca < 0 and len_cam_sphere > self.radius: # More robust check: sphere center projected is behind origin
        #     return False, None
        
        # Distance from sphere center to closest point on ray line
        # d_sq = norm(cam_sphere - t_ca * ray.d)**2 # This is (dist_ray_sphere)^2
        d_sq = len_cam_sphere**2 - t_ca**2


        if d_sq > self.radius*self.radius:
            return False, None # Ray misses the sphere

        # Distance from closest point on ray to intersection surface
        t_hc = math.sqrt(self.radius*self.radius - d_sq)

        # Intersection distances along the ray
        t0 = t_ca - t_hc
        t1 = t_ca + t_hc

        if t0 < 0 and t1 < 0: # Both intersections are behind the ray origin
            return False, None
        
        # Choose the closest positive intersection distance
        if t0 < 0:
            dist_ray_intersection = t1 # t0 is behind, t1 is in front
        else:
            dist_ray_intersection = t0 # t0 is the first intersection

        if dist_ray_intersection < 1e-5: # Threshold to avoid self-intersection issues
             if t1 > 1e-5: # if t0 is too close, try t1
                 dist_ray_intersection = t1
             else: # both are too close or negative
                 return False, None


        i_point = ray.o + dist_ray_intersection * ray.d
        return True, i_point


class Triangle:
#todo test this class
    def __init__(self, points):
        self.points = points
        # Ensure points are Vec3
        v0, v1, v2 = points[0], points[1], points[2]
        self.normal = normalize(cross(v1 - v0, v2 - v0)) #
        self.d_plane = dot(self.normal, v0) # d for plane equation N.X = d_plane

    def intersect(self, ray):
        # https://www.cs.princeton.edu/courses/archive/fall00/cs426/lectures/raycast/sld017.htm
        # Plane equation: dot(N, P) - d_plane = 0
        # Ray equation: P = ray.o + t * ray.d
        # dot(N, ray.o + t * ray.d) - d_plane = 0
        # dot(N, ray.o) + t * dot(N, ray.d) - d_plane = 0
        # t * dot(N, ray.d) = d_plane - dot(N, ray.o)
        
        denom = dot(ray.d, self.normal)
        if abs(denom) < 1e-6: # Ray is parallel to the triangle plane
            return False, None

        t = (self.d_plane - dot(ray.o, self.normal)) / denom

        if t < 1e-5: # Intersection is behind or too close to the ray origin
            return False, None
            
        i_point = ray.o + t * ray.d
        
        # Check if intersection point is inside the triangle (using barycentric coordinates or edge checks)
        # This part is the "todo" from the original code
        # For now, returning True if it hits the plane of the triangle.
        # This needs to be implemented for correct triangle rendering.

        # --- Barycentric check (example) ---
        p0, p1, p2 = self.points[0], self.points[1], self.points[2]
        edge0 = p1 - p0
        edge1 = p2 - p1
        edge2 = p0 - p2

        vp0 = i_point - p0
        vp1 = i_point - p1
        vp2 = i_point - p2

        # Normal of the triangle (consistent winding)
        # self.normal
        
        # Check if point is on the same side of all edges
        c0 = cross(edge0, vp0)
        c1 = cross(edge1, vp1)
        c2 = cross(edge2, vp2)

        if dot(self.normal, c0) < 0 or \
           dot(self.normal, c1) < 0 or \
           dot(self.normal, c2) < 0:
            return False, None # Point is outside

        return True, i_point


class Mesh():

    def __init__(self, triangles):
        self.triangles = triangles

    def intersect(self, ray):
        closest_t = float('inf')
        hit_point = None
        hit_triangle = None # Could be useful to get normal from the specific triangle

        for t_obj in self.triangles:
            intersected, point = t_obj.intersect(ray)
            if intersected:
                dist = norm(point - ray.o)
                if dist < closest_t:
                    closest_t = dist
                    hit_point = point
                    # hit_triangle = t_obj # If you need the specific triangle's properties
        
        if hit_point is not None:
            return True, hit_point
        return False, None # Original returned None, should be (False, None)

class Camera:

    def __init__(self, res):
        self.res_width = res[0]
        self.res_height = res[1]
        self.aspect_ratio = float(self.res_width) / self.res_height
        
        # FOV approach:
        self.vfov_degrees = 60 # Vertical field of view
        self.focal = (self.res_height / 2.0) / math.tan(math.radians(self.vfov_degrees / 2.0))
        
        # Original fixed plane size:
        # self.width = 1 # Width of the view plane in world units
        # self.height = 1 # Height of the view plane in world units
        # self.focal = 1 # Distance from camera origin to view plane

        # Using FOV to set view plane dimensions based on focal length
        # Assuming view plane at Z=self.focal (or -self.focal depending on convention)
        # And camera looks along -Z or +Z
        # The original ray Vec3(z, self.focal, -x) means camera looks along +Y if Y is focal direction.
        # Let's use the original pixel_to_meters with its implicit view plane.
        # The focal length is effectively a Z-distance in the ray direction tuple.
        self.view_plane_width = 1.0 # As in original code
        self.view_plane_height = 1.0 # As in original code
        self.focal_length = 1.0      # As in original code


    def pixel_to_meters(self, i, j):
        # Converts pixel coordinates (i, j) to view plane coordinates (x, y_plane_coord)
        # (0,0) at top-left of screen, (res_width-1, res_height-1) at bottom-right
        # Map to view plane where center is (0,0)
        # x goes from -view_plane_width/2 to +view_plane_width/2
        # y_plane_coord goes from +view_plane_height/2 to -view_plane_height/2 (top to bottom)
        
        x = (i + 0.5) / self.res_width * self.view_plane_width - (self.view_plane_width / 2.0)
        # Original z calculation: z = j*self.height/self.res_height - self.height/2
        # This maps j=0 to -height/2 and j=res_height to +height/2 (if j is pixel y)
        # If screen Y is downwards, this means top of screen is negative z, bottom is positive z.
        # Let's assume camera's "up" is positive Y on its sensor plane.
        # So a higher j (lower on screen) maps to a more negative y_sensor value.
        y_sensor = -((j + 0.5) / self.res_height * self.view_plane_height - (self.view_plane_height / 2.0))
        
        # Original mapping:
        # x_orig = i*self.view_plane_width/self.res_width - self.view_plane_width/2
        # z_orig = j*self.view_plane_height/self.res_height - self.view_plane_height/2
        # And ray was Ray(Vec3(0,0,0), Vec3(z_orig, self.focal_length, -x_orig))
        # This means:
        # ray_dir.x = z_orig (controlled by pixel j - height)
        # ray_dir.y = self.focal_length (depth axis)
        # ray_dir.z = -x_orig (controlled by pixel i - width, negated)
        # This implies a camera system: Y is forward, X is "sensor vertical", Z is "sensor horizontal" (negated).
        # Let's stick to the original parameter names from pixel_to_meters for minimal confusion.
        
        x_cam_plane = (i / self.res_width - 0.5) * self.view_plane_width # Centered, scaled
        z_cam_plane = (j / self.res_height - 0.5) * self.view_plane_height # Centered, scaled

        return x_cam_plane, z_cam_plane


    def shoot_ray(self, i, j):
        # i: horizontal pixel index (from 0 to res_width-1)
        # j: vertical pixel index (from 0 to res_height-1)
        
        # Using the original pixel_to_meters logic and ray construction
        # x_mapped_on_plane, z_mapped_on_plane = self.pixel_to_meters(i, j) #
        # ray_dir = Vec3(z_mapped_on_plane, self.focal_length, -x_mapped_on_plane) #

        # Let's adjust pixel_to_meters slightly for centering and standard interpretation
        # (i+0.5) for pixel center for i, (j+0.5) for pixel center for j
        # Screen X (i) maps to camera X, Screen Y (j) maps to camera Y (inverted often)
        # Typical setup: camera at origin, looks down -Z. View plane at Z = -focal_length.
        # X_view = (i + 0.5 - res_width/2) * pixel_size_x
        # Y_view = (j + 0.5 - res_height/2) * pixel_size_y (often inverted: (res_height/2 - (j+0.5)))
        
        # Sticking to the provided code's ray generation:
        # pixel_to_meters returns x, z based on i, j.
        # x is derived from i (width), z is derived from j (height)
        # ray direction uses (z, focal, -x)
        
        x_coord, z_coord = self.pixel_to_meters(i, j) # x_coord from i (width), z_coord from j (height)
                                                     # Based on original: x_coord is horizontal on sensor, z_coord is vertical on sensor
        
        # Original ray: Vec3(z_coord, self.focal_length, -x_coord)
        # This means:
        # World X of ray dir = z_coord (from screen Y / j)
        # World Y of ray dir = focal_length (constant, makes this the "forward" axis if camera aims along Y)
        # World Z of ray dir = -x_coord (from screen X / i, negated)
        # This setup makes the camera look along its Y axis.
        # Screen X (i) controls world Z (negated). Screen Y (j) controls world X.
        
        direction = normalize(Vec3(z_coord, self.focal_length, -x_coord))
        return Ray(Vec3(0,0,0), direction)


# Convert 0-1 float to 0-255 int
def floatto8bit(value):
    return int(max(0, min(value*255, 255))) #