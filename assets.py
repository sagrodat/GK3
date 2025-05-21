import math
# Upewnij się, że importy Vec3 są poprawne, jeśli zapisujesz Vec3.py w sposób wpływający na importy.
# Zakładając, że Vec3.py znajduje się w tym samym katalogu lub w ścieżce Pythona.
from Vec3 import Vec3, normalize, dot, cross, norm, mul_vec3


class Material:
    def __init__(self, name, color=Vec3(1,1,1), ambient_coeff=0.1, diffuse_coeff=0.9, specular_coeff=0.5, shininess=50):
        self.name = name
        self.color = color
        self.ambient_coeff = ambient_coeff
        self.diffuse_coeff = diffuse_coeff
        self.specular_coeff = specular_coeff
        self.shininess = shininess

class Ray:
    def __init__(self, o, d):
        self.o = o
        self.d = normalize(d)

#TODO: do zintegrowania
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
        if dist == 0: # Unikaj dzielenia przez zero, jeśli punkt znajduje się dokładnie w pozycji światła
            return self._strength 
        out = self._strength * min(self.radius*self.radius/(dist*dist), 1.0) # zapewnij dzielenie zmiennoprzecinkowe
        return out

class Sphere:
    def __init__(self, pos, radius, material): # Zamiast 'color'
        self.pos = pos
        self.radius = radius
        self.material = material


    @property
    def color(self):
        return self.material.color

        # print("Kula w {} o promieniu {} i kolorze {}".format(self.pos, self.radius, self.color)) # Opcjonalny wydruk

    def normal(self, v):
        return normalize(v - self.pos)

    def intersect(self, ray):
        # Upewnij się, że ray.o i self.pos są obiektami Vec3
        cam_sphere = self.pos - ray.o  # odległość kamera-kula
        
        # Sprawdź, czy początek promienia znajduje się wewnątrz kuli
        if norm(cam_sphere) < self.radius:
            # Obsługa sytuacji, gdy początek promienia jest wewnątrz kuli:
            # Dla uproszczenia możemy przyjąć, że przecina się w ray.o lub znaleźć punkt wyjścia.
            # Obecna logika może zawieść lub dać ujemną odległość.
            # Solidne rozwiązanie znalazłoby przednie przecięcie.
            # Na razie załóżmy, że początek promienia jest na zewnątrz lub na powierzchni.
            pass # Lub zaimplementuj specyficzną logikę dla początku wewnątrz

        len_cam_sphere = norm(cam_sphere)
        if len_cam_sphere == 0: # Początek promienia znajduje się w środku kuli
             i_point = ray.o + self.radius * ray.d
             return True, i_point

        # Rzut cam_sphere na kierunek promienia
        t_ca = dot(cam_sphere, ray.d)

        # Jeśli kula jest za początkiem promienia, a promień jest skierowany od niej
        # if t_ca < 0 and len_cam_sphere > self.radius: # Bardziej solidne sprawdzenie: rzutowany środek kuli jest za początkiem
        #     return False, None
        
        # Odległość od środka kuli do najbliższego punktu na linii promienia
        # d_sq = norm(cam_sphere - t_ca * ray.d)**2 # To jest (odległość_promień_kula)^2
        d_sq = len_cam_sphere**2 - t_ca**2


        if d_sq > self.radius*self.radius:
            return False, None # Promień omija kulę

        # Odległość od najbliższego punktu na promieniu do powierzchni przecięcia
        t_hc = math.sqrt(self.radius*self.radius - d_sq)

        # Odległości przecięcia wzdłuż promienia
        t0 = t_ca - t_hc
        t1 = t_ca + t_hc

        if t0 < 0 and t1 < 0: # Oba przecięcia są za początkiem promienia
            return False, None
        
        # Wybierz najbliższą dodatnią odległość przecięcia
        if t0 < 0:
            dist_ray_intersection = t1 # t0 jest z tyłu, t1 jest z przodu
        else:
            dist_ray_intersection = t0 # t0 jest pierwszym przecięciem

        if dist_ray_intersection < 1e-5: # Próg, aby uniknąć problemów z samo-przecięciem
             if t1 > 1e-5: # jeśli t0 jest zbyt blisko, spróbuj t1
                 dist_ray_intersection = t1
             else: # oba są zbyt blisko lub ujemne
                 return False, None


        i_point = ray.o + dist_ray_intersection * ray.d
        return True, i_point


class Triangle:
#TODO: przetestuj tę klasę
    def __init__(self, points):
        self.points = points
        # Upewnij się, że punkty są Vec3
        v0, v1, v2 = points[0], points[1], points[2]
        self.normal = normalize(cross(v1 - v0, v2 - v0))
        self.d_plane = dot(self.normal, v0) # d dla równania płaszczyzny N.X = d_plane

    def intersect(self, ray):
        # https://www.cs.princeton.edu/courses/archive/fall00/cs426/lectures/raycast/sld017.htm
        # Równanie płaszczyzny: dot(N, P) - d_plane = 0
        # Równanie promienia: P = ray.o + t * ray.d
        # dot(N, ray.o + t * ray.d) - d_plane = 0
        # dot(N, ray.o) + t * dot(N, ray.d) - d_plane = 0
        # t * dot(N, ray.d) = d_plane - dot(N, ray.o)
        
        denom = dot(ray.d, self.normal)
        if abs(denom) < 1e-6: # Promień jest równoległy do płaszczyzny trójkąta
            return False, None

        t = (self.d_plane - dot(ray.o, self.normal)) / denom

        if t < 1e-5: # Przecięcie jest za lub zbyt blisko początku promienia
            return False, None
            
        i_point = ray.o + t * ray.d
        
        # Sprawdź, czy punkt przecięcia znajduje się wewnątrz trójkąta (używając współrzędnych barycentrycznych lub sprawdzania krawędzi)
        # Ta część jest "todo" z oryginalnego kodu
        # Na razie zwraca True, jeśli trafi w płaszczyznę trójkąta.
        # To musi zostać zaimplementowane dla poprawnego renderowania trójkąta.

        # --- Sprawdzenie barycentryczne (przykład) ---
        p0, p1, p2 = self.points[0], self.points[1], self.points[2]
        edge0 = p1 - p0
        edge1 = p2 - p1
        edge2 = p0 - p2

        vp0 = i_point - p0
        vp1 = i_point - p1
        vp2 = i_point - p2

        # Normalna trójkąta (spójne nawinięcie)
        # self.normal
        
        # Sprawdź, czy punkt znajduje się po tej samej stronie wszystkich krawędzi
        c0 = cross(edge0, vp0)
        c1 = cross(edge1, vp1)
        c2 = cross(edge2, vp2)

        if dot(self.normal, c0) < 0 or \
           dot(self.normal, c1) < 0 or \
           dot(self.normal, c2) < 0:
            return False, None # Punkt jest na zewnątrz

        return True, i_point


class Mesh():

    def __init__(self, triangles):
        self.triangles = triangles

    def intersect(self, ray):
        closest_t = float('inf')
        hit_point = None
        hit_triangle = None # Może być przydatne do uzyskania normalnej z konkretnego trójkąta

        for t_obj in self.triangles:
            intersected, point = t_obj.intersect(ray)
            if intersected:
                dist = norm(point - ray.o)
                if dist < closest_t:
                    closest_t = dist
                    hit_point = point
                    # hit_triangle = t_obj # Jeśli potrzebujesz właściwości konkretnego trójkąta
        
        if hit_point is not None:
            return True, hit_point
        return False, None # Oryginał zwracał None, powinno być (False, None)

class Camera:

    def __init__(self, res):
        self.res_width = res[0]
        self.res_height = res[1]
        self.aspect_ratio = float(self.res_width) / self.res_height
        
        # Podejście oparte na FOV:
        self.vfov_degrees = 60 # Pionowe pole widzenia
        self.focal = (self.res_height / 2.0) / math.tan(math.radians(self.vfov_degrees / 2.0))
        
        # Oryginalny stały rozmiar płaszczyzny:
        # self.width = 1 # Szerokość płaszczyzny widzenia w jednostkach świata
        # self.height = 1 # Wysokość płaszczyzny widzenia w jednostkach świata
        # self.focal = 1 # Odległość od początku kamery do płaszczyzny widzenia

        # Użycie FOV do ustawienia wymiarów płaszczyzny widzenia na podstawie ogniskowej
        # Zakładając płaszczyznę widzenia w Z=self.focal (lub -self.focal w zależności od konwencji)
        # I kamera patrzy wzdłuż -Z lub +Z
        # Oryginalny promień Vec3(z, self.focal, -x) oznacza, że kamera patrzy wzdłuż +Y, jeśli Y jest kierunkiem ogniskowej.
        # Użyjmy oryginalnego pixel_to_meters z jego niejawną płaszczyzną widzenia.
        # Ogniskowa jest faktycznie odległością Z w krotce kierunku promienia.
        self.view_plane_width = 1.0 # Jak w oryginalnym kodzie
        self.view_plane_height = 1.0 # Jak w oryginalnym kodzie
        self.focal_length = 1.0      # Jak w oryginalnym kodzie


    def pixel_to_meters(self, i, j):
        # Konwertuje współrzędne pikseli (i, j) na współrzędne płaszczyzny widzenia (x, y_plane_coord)
        # (0,0) w lewym górnym rogu ekranu, (res_width-1, res_height-1) w prawym dolnym
        # Mapuj na płaszczyznę widzenia, gdzie środek to (0,0)
        # x zmienia się od -view_plane_width/2 do +view_plane_width/2
        # y_plane_coord zmienia się od +view_plane_height/2 do -view_plane_height/2 (od góry do dołu)
        
        x = (i + 0.5) / self.res_width * self.view_plane_width - (self.view_plane_width / 2.0)
        # Oryginalne obliczenie z: z = j*self.height/self.res_height - self.height/2
        # To mapuje j=0 na -height/2 i j=res_height na +height/2 (jeśli j to y piksela)
        # Jeśli Y ekranu jest skierowane w dół, oznacza to, że góra ekranu to ujemne z, a dół to dodatnie z.
        # Załóżmy, że "góra" kamery to dodatnie Y na jej płaszczyźnie sensora.
        # Więc wyższe j (niżej na ekranie) mapuje się na bardziej ujemną wartość y_sensor.
        y_sensor = -((j + 0.5) / self.res_height * self.view_plane_height - (self.view_plane_height / 2.0))
        
        # Oryginalne mapowanie:
        # x_orig = i*self.view_plane_width/self.res_width - self.view_plane_width/2
        # z_orig = j*self.view_plane_height/self.res_height - self.view_plane_height/2
        # A promień był Ray(Vec3(0,0,0), Vec3(z_orig, self.focal_length, -x_orig))
        # To oznacza:
        # ray_dir.x = z_orig (kontrolowane przez piksel j - wysokość)
        # ray_dir.y = self.focal_length (oś głębokości)
        # ray_dir.z = -x_orig (kontrolowane przez piksel i - szerokość, zanegowane)
        # To implikuje system kamery: Y jest do przodu, X to "pion sensora", Z to "poziom sensora" (zanegowane).
        # Trzymajmy się oryginalnych nazw parametrów z pixel_to_meters, aby zminimalizować zamieszanie.
        
        x_cam_plane = (i / self.res_width - 0.5) * self.view_plane_width # Wyśrodkowane, przeskalowane
        z_cam_plane = (j / self.res_height - 0.5) * self.view_plane_height # Wyśrodkowane, przeskalowane

        return x_cam_plane, z_cam_plane


    def shoot_ray(self, i, j):
        # i: poziomy indeks piksela (od 0 do res_width-1)
        # j: pionowy indeks piksela (od 0 do res_height-1)
        
        # Użycie oryginalnej logiki pixel_to_meters i konstrukcji promienia
        # x_mapped_on_plane, z_mapped_on_plane = self.pixel_to_meters(i, j)
        # ray_dir = Vec3(z_mapped_on_plane, self.focal_length, -x_mapped_on_plane)

        # Dostosujmy nieco pixel_to_meters dla wyśrodkowania i standardowej interpretacji
        # (i+0.5) dla środka piksela dla i, (j+0.5) dla środka piksela dla j
        # X ekranu (i) mapuje się na X kamery, Y ekranu (j) mapuje się na Y kamery (często odwrócone)
        # Typowa konfiguracja: kamera w początku, patrzy w dół -Z. Płaszczyzna widzenia w Z = -focal_length.
        # X_view = (i + 0.5 - res_width/2) * pixel_size_x
        # Y_view = (j + 0.5 - res_height/2) * pixel_size_y (often inverted: (res_height/2 - (j+0.5)))
        
        # Trzymając się generowania promieni z dostarczonego kodu:
        # pixel_to_meters zwraca x, z na podstawie i, j.
        # x jest pochodną i (szerokość), z jest pochodną j (wysokość)
        
        x_coord, z_coord = self.pixel_to_meters(i, j) # x_coord z i (szerokość), z_coord z j (wysokość)
                                                      # Na podstawie oryginału: x_coord jest poziome na sensorze, z_coord jest pionowe na sensorze
        
        # Oryginalny promień: Vec3(z_coord, self.focal_length, -x_coord)
        # To oznacza:
        # Światowe X kierunku promienia = z_coord (z Y ekranu / j)
        # Światowe Y kierunku promienia = focal_length (stała, czyni to osią "do przodu", jeśli kamera celuje wzdłuż Y)
        # Światowe Z kierunku promienia = -x_coord (z X ekranu / i, zanegowane)
        # Ta konfiguracja sprawia, że kamera patrzy wzdłuż swojej osi Y.
        # X ekranu (i) kontroluje światowe Z (zanegowane). Y ekranu (j) kontroluje światowe X.
        
        direction = normalize(Vec3(z_coord, self.focal_length, -x_coord))
        return Ray(Vec3(0,0,0), direction)


# Konwertuj float 0-1 na int 0-255
def floatto8bit(value):
    return int(max(0, min(value*255, 255)))