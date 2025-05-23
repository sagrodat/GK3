import contextlib
with contextlib.redirect_stdout(None): # aby nie wyswietlać przywitania od biblioteki pygame
    import pygame
from pygame.math import Vector3
import math # Used in Camera for a more robust shoot_ray

# --- Helper function (from original assets.py) ---
def floatto8bit(value):
    """Converts a float (0.0-1.0) to an 8-bit integer (0-255)."""
    return max(0, min(255, int(value * 255)))

# --- Class Definitions (modified from original assets.py) ---
class Ray:
    def __init__(self, origin: Vector3, direction: Vector3):
        self.o = origin
        if direction.length_squared() > 0: # Ensure direction is not zero vector before normalizing
            self.d = direction.normalize()
        else:
            self.d = Vector3(0,0,0) # Or handle as an error

class Material:
    def __init__(self, name:str, color: Vector3, ambient_coeff: float, diffuse_coeff: float, specular_coeff: float, shininess: float):
        self.name = name
        self.color = color # Base color of the material
        self.ambient_coeff = ambient_coeff
        self.diffuse_coeff = diffuse_coeff
        self.specular_coeff = specular_coeff
        self.shininess = shininess

class Camera:
    def __init__(self, resolution, pos: Vector3 = None, focal_length=1.0, fov_degrees=60.0):
        self.res_width, self.res_height = resolution
        self.pos = pos if pos is not None else Vector3(0, 0, 0)
        self.focal_length = focal_length # Can be used if not using FOV method

        # FOV related calculations for shoot_ray
        self.aspect_ratio = self.res_width / self.res_height
        # Convert FOV from degrees to radians for math.tan
        fov_radians = math.radians(fov_degrees)
        self.sensor_height_fov_scaled = 2.0 * math.tan(fov_radians / 2.0)
        self.sensor_width_fov_scaled = self.sensor_height_fov_scaled * self.aspect_ratio


    def shoot_ray(self, u_pixel, v_pixel):
        # Camera at origin (self.pos), looking along +Y axis.
        # Image plane (XZ) is at Y = self.focal_length (or implicitly defined by FOV).
        # u_pixel (horizontal) maps to X, v_pixel (vertical) maps to Z.

        # Normalized Device Coordinates (NDC): map pixel coords from [0, res-1] to [-1, 1]
        # Add 0.5 to sample center of pixel
        ndc_x = (u_pixel + 0.5) / self.res_width * 2.0 - 1.0
        ndc_y = (v_pixel + 0.5) / self.res_height * 2.0 - 1.0 # Ranges from -1 (top) to 1 (bottom)

        # Screen/Camera space coordinates using FOV
        # Y-axis is forward, X-axis is right, Z-axis is up (for a typical setup looking down an axis)
        # If camera looks along +Y:
        #   X on screen -> X world
        #   Y on screen -> Z world (Y is depth)
        # We flip ndc_y because typically positive Y in screen space is downwards.
        camera_space_x = ndc_x * self.sensor_width_fov_scaled / 2.0
        camera_space_z = -ndc_y * self.sensor_height_fov_scaled / 2.0 # Negative because v_pixel increases downwards

        # Direction vector in camera space (camera looks along +Y)
        # If focal_length is 1, sensor_..._scaled already includes the tan(FOV/2) factor.
        # The "forward" component for direction is effectively 1 unit if FOV scaling is applied to X and Z.
        ray_dir_camera_space = Vector3(camera_space_x, 1.0, camera_space_z)

        
        if ray_dir_camera_space.length_squared() > 0:
            return Ray(self.pos, ray_dir_camera_space.normalize())
        else:
            return Ray(self.pos, Vector3(0,1,0)) # Default ray if direction is zero

class Sphere:
    def __init__(self, pos: Vector3, radius: float, material: Material):
        self.pos = pos
        self.radius = radius
        self.material = material

    def intersect(self, ray: Ray):
        oc = ray.o - self.pos
        a = ray.d.length_squared() # ray.d is normalized, so this should be 1.0
        b = 2.0 * oc.dot(ray.d)
        c = oc.length_squared() - self.radius * self.radius
        
        discriminant = b*b - 4*a*c
        if discriminant < 0:
            return False, None
        else:
            sqrt_discriminant = discriminant**0.5
            t1 = (-b - sqrt_discriminant) / (2.0*a)
            t2 = (-b + sqrt_discriminant) / (2.0*a)
            
            t = -1.0
            # Check for smallest positive t (intersection in front of ray origin)
            # Use a small epsilon (e.g., 1e-4) to avoid self-intersection issues
            epsilon = 1e-4
            if t1 > epsilon and (t1 < t2 or t2 <= epsilon):
                t = t1
            elif t2 > epsilon:
                t = t2
            else:
                return False, None # Both intersections are behind or too close
            
            intersection_point = ray.o + ray.d * t
            return True, intersection_point

    def normal(self, surface_point: Vector3):
        if (surface_point - self.pos).length_squared() > 0:
            return (surface_point - self.pos).normalize()
        return Vector3(0,1,0) # Should not happen for valid surface_point

class Light:
    def __init__(self, pos: Vector3, color: Vector3, strength: float, radius: float):
        self.pos = pos
        self.color = color
        self._strength = strength
        self.radius = radius # Used for attenuation falloff

    def strength(self, point: Vector3):
        # Calculate distance squared for attenuation
        vec_to_light = self.pos - point
        dist_sq = vec_to_light.length_squared()
        
        # Attenuation model (prevents division by zero and gives falloff)
        # Original: self._strength / (1 + dist_sq / self.radius**2)
        if self.radius > 0:
            attenuation = 1.0 / (1.0 + dist_sq / (self.radius * self.radius))
        else: # Avoid division by zero if radius is 0, simpler attenuation
            attenuation = 1.0 / (1.0 + dist_sq) 
            
        return self._strength * attenuation

# --- Material Definitions (from original materials.py) ---
kreda_material = Material(
    name="Kreda", color=Vector3(0.9, 0.9, 0.9),
    ambient_coeff=0.2, diffuse_coeff=0.8, specular_coeff=0.1, shininess=5
)
metal_material = Material(
    name="Metal", color=Vector3(0.75, 0.75, 0.8),
    ambient_coeff=0.3, diffuse_coeff=0.6, specular_coeff=0.9, shininess=100
)
guma_material = Material(
    name="Guma", color=Vector3(0.1, 0.1, 0.1),
    ambient_coeff=0.1, diffuse_coeff=0.7, specular_coeff=0.3, shininess=10
)
plastik_material = Material(
    name="Plastik", color=Vector3(0.3, 0.3, 0.8),
    ambient_coeff=0.2, diffuse_coeff=0.7, specular_coeff=0.6, shininess=30
)


# --- Main Raytracing Logic ---
def calculate_pixel_color(u, v, camera, light, asset, all_scene_assets):
    """
    Oblicza kolor dla piksela poprzez wystrzelenie pojedynczego promienia, włączając sprawdzanie cieni.
    :param u: pozioma współrzędna piksela
    :param v: pionowa współrzędna piksela
    :param camera: obiekt Camera
    :param light: obiekt Light
    :param asset: główny obiekt, z którym ten promień się przeciął
    :param all_scene_assets: lista wszystkich obiektów na scenie do sprawdzania cieni
    :return: kolor Vector3 dla piksela
    """
    
    ray = camera.shoot_ray(u, v) 
    intersected, intersection_point = asset.intersect(ray)
    
    pixel_color = Vector3(0, 0, 0) # Domyślny kolor tła
    if intersected:
        surface_normal = asset.normal(intersection_point)
        vec_to_light_source = light.pos - intersection_point
        
        # Normalize vectors if they are not zero vectors
        light_dir_normalized = Vector3(0,0,0)
        if vec_to_light_source.length_squared() > 0:
            light_dir_normalized = vec_to_light_source.normalize()
        
        view_dir_vec = ray.o - intersection_point
        view_dir_normalized = Vector3(0,0,0)
        if view_dir_vec.length_squared() > 0:
            view_dir_normalized = view_dir_vec.normalize()


        # Sprawdzanie cienia
        in_shadow = False
        shadow_ray_origin = intersection_point + surface_normal * 1e-4 
        shadow_ray = Ray(shadow_ray_origin, light_dir_normalized)
        
        distance_to_light = vec_to_light_source.length()

        for occluder in all_scene_assets:
            if occluder is asset: # Don't check self-shadowing with the primary asset here, shadow_ray_origin handles it
                # This check might be too simple if occluder can be partially transparent etc.
                # but for opaque objects, this avoids re-intersecting the same surface immediately.
                # However, the primary asset *can* cast a shadow on itself from another part.
                # The 1e-4 offset is the main guard against immediate self-intersection.
                pass # Allow checking self-shadowing from other parts of the same complex object (if applicable)

            shadow_intersected, shadow_hit_point = occluder.intersect(shadow_ray)
            if shadow_intersected:
                dist_to_shadow_hit = (shadow_hit_point - shadow_ray_origin).length()
                if dist_to_shadow_hit < distance_to_light:
                    in_shadow = True
                    break 
        
        # Składowa otoczenia (zawsze obecna)
        # Corrected to use current asset's material
        color_ambient = asset.material.color * asset.material.ambient_coeff
        
        color_diffuse = Vector3(0,0,0)
        color_specular = Vector3(0,0,0)

        if not in_shadow:
            # Calculate light intensity at the intersection point (considering attenuation)
            # light.strength already includes attenuation. light.color is the light's color.
            light_intensity_at_point = light.color * light.strength(intersection_point)
            
            # Składowa rozproszenia
            diffuse_factor = max(surface_normal.dot(light_dir_normalized), 0.0)
            color_diffuse = light_intensity_at_point * (asset.material.diffuse_coeff * diffuse_factor)
            
            # Składowa odbicia lustrzanego
            # Blinn-Phong reflection model (uses halfway vector) is often more efficient/stable
            # Original Phong: R = 2 * N * dot(N, L) - L
            if light_dir_normalized.length_squared() > 0: # Ensure L is not zero
                reflection_vec_phong = (2 * surface_normal * surface_normal.dot(light_dir_normalized) - light_dir_normalized)
                if reflection_vec_phong.length_squared() > 0:
                    reflection_vec_phong = reflection_vec_phong.normalize()
                    specular_factor = pow(max(reflection_vec_phong.dot(view_dir_normalized), 0.0), asset.material.shininess)
                    color_specular = light_intensity_at_point * (asset.material.specular_coeff * specular_factor)
                        
        # Combine lighting components and modulate by material's base color
        total_illumination = color_ambient + color_diffuse + color_specular
        
        # Component-wise multiplication for color modulation
        pixel_color = Vector3(
            asset.material.color.x * total_illumination.x,
            asset.material.color.y * total_illumination.y,
            asset.material.color.z * total_illumination.z
        )

    return pixel_color


def main_realtime():
    pygame.init()

    available_materials = [metal_material, kreda_material, guma_material, plastik_material] 
    current_material_index = 0

    rendering_res = 100
    scale_factor = 8
    
    display_width = rendering_res * scale_factor
    display_height = rendering_res * scale_factor
    
    screen = pygame.display.set_mode((display_width, display_height))
    pygame.display.set_caption(f"RayTracer Czasu Rzeczywistego (Render: {rendering_res}x{rendering_res}, Display: {display_width}x{display_height})")

    render_surface = pygame.Surface((rendering_res, rendering_res))

    # Camera: pos (0,0,0), looking +Y, FOV 60 degrees.
    camera = Camera(resolution=(rendering_res, rendering_res), pos=Vector3(0,0,0), fov_degrees=60.0)

    sphere_radius = 0.5
    sphere_pos = Vector3(0, 2, 0) # Y=2 means 2 units "in front" of camera if camera looks +Y
    sphere = Sphere(pos=sphere_pos, radius=sphere_radius, material=available_materials[current_material_index])

    light_pos = Vector3(1, -2.4, -2.4) # Relative to world origin
    light_color = Vector3(1,1,1) 
    light_strength = 1.5
    light_radius = 10 
    light = Light(pos=light_pos, color=light_color, strength=light_strength, radius=light_radius)

    light_move_speed = 2 # Adjusted for finer control

    scene_assets = [sphere]

    running = True
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)

    initial_sphere_material_name = available_materials[current_material_index].name

    info_string = f"""
    ----------------------------------------------------
            INFORMACJE O SYMULACJI
    ----------------------------------------------------
    Sterowanie światłem:
    Strzałka GÓRA:    Przesuń światło w kierunku -X
    Strzałka DÓŁ:     Przesuń światło w kierunku +X
    Strzałka LEWO:    Przesuń światło w kierunku +Z
    Strzałka PRAWO:   Przesuń światło w kierunku -Z
    Page UP:          Przesuń światło w kierunku +Y
    Page DOWN:        Przesuń światło w kierunku -Y

    Inne sterowanie:
    Klawisz ESC:      Wyjście z programu
    Klawisz X:        Zmiana materiału kuli (cyklicznie)

    Parametry początkowe kuli:
    Pozycja (X, Y, Z): ({sphere.pos.x:.1f}, {sphere.pos.y:.1f}, {sphere.pos.z:.1f})
    Promień:           {sphere.radius}
    Materiał:          {initial_sphere_material_name}

    Parametry początkowe światła:
    Pozycja (X, Y, Z): ({light.pos.x:.1f}, {light.pos.y:.1f}, {light.pos.z:.1f})
    Kolor (R, G, B):   ({light.color.x:.2f}, {light.color.y:.2f}, {light.color.z:.2f})
    Siła:              {light._strength}
    Promień działania: {light.radius}

    Ustawienia renderowania:
    Rozdzielczość renderowania: {rendering_res}x{rendering_res} pikseli
    Rozdzielczość wyświetlania: {display_width}x{display_height} pikseli
    Skala wyświetlania:         {scale_factor}x
    Pozycja kamery:             ({camera.pos.x:.1f}, {camera.pos.y:.1f}, {camera.pos.z:.1f}) (FOV: {60} deg)
    ----------------------------------------------------
        """
    print(info_string)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_UP: # Move light +Z
                    light.pos.z += light_move_speed
                if event.key == pygame.K_DOWN: # Move light -Z
                    light.pos.z -= light_move_speed
                if event.key == pygame.K_LEFT: # Move light -X
                    light.pos.x -= light_move_speed
                if event.key == pygame.K_RIGHT: # Move light +X
                    light.pos.x += light_move_speed
                if event.key == pygame.K_PAGEUP: # Move light +Y
                    light.pos.y += light_move_speed
                if event.key == pygame.K_PAGEDOWN: # Move light -Y
                    light.pos.y -= light_move_speed
                
                if event.key == pygame.K_x:
                    current_material_index = (current_material_index + 1) % len(available_materials)
                    for asset_in_scene in scene_assets:
                        if isinstance(asset_in_scene, Sphere): 
                            asset_in_scene.material = available_materials[current_material_index]
                    print(f"Materiał kul zmieniony na: {available_materials[current_material_index].name}")

        for u_pixel in range(camera.res_width):
            for v_pixel in range(camera.res_height):
                # Find closest intersected asset
                # For this simple scene, there's only one sphere.
                # A more general ray tracer would iterate all_scene_assets here for primary rays.
                closest_hit_asset = None
                min_dist = float('inf')
                
                # This loop is a bit redundant if calculate_pixel_color re-shoots ray and re-intersects.
                # However, it's needed if we want to find THE asset to shade.
                # Original code passed 'asset_to_render' which was just 'sphere'.
                # This structure is better for multiple objects.
                primary_ray_for_selection = camera.shoot_ray(u_pixel, v_pixel)
                
                temp_intersection_point_candidate = None # Not strictly needed if re-intersecting in calc_pixel_color

                for asset_in_scene in scene_assets: # Currently only one sphere
                    intersected, intersection_point_candidate = asset_in_scene.intersect(primary_ray_for_selection)
                    if intersected:
                        # dist = (intersection_point_candidate - primary_ray_for_selection.o).length()
                        # For primary ray, intersection_point_candidate.y (if camera looks along Y)
                        # or .z (if camera looks along Z) can be used as depth.
                        # Or simply distance.
                        dist_sq = (intersection_point_candidate - primary_ray_for_selection.o).length_squared()
                        if dist_sq < min_dist:
                            min_dist = dist_sq
                            closest_hit_asset = asset_in_scene
                            # temp_intersection_point_candidate = intersection_point_candidate # Store if needed

                final_color_vec3 = Vector3(0,0,0) 
                if closest_hit_asset:
                    # calculate_pixel_color will re-shoot the ray and re-intersect.
                    # This is slightly inefficient but keeps calculate_pixel_color self-contained.
                    final_color_vec3 = calculate_pixel_color(u_pixel, v_pixel, camera, light, closest_hit_asset, scene_assets)
                
                r = floatto8bit(final_color_vec3.x)
                g = floatto8bit(final_color_vec3.y)
                b = floatto8bit(final_color_vec3.z)
                render_surface.set_at((u_pixel, v_pixel), (r, g, b))

        scaled_surface = pygame.transform.scale(render_surface, (display_width, display_height))
        screen.blit(scaled_surface, (0, 0))

        fps = clock.get_fps()
        fps_text = font.render(f"FPS: {fps:.1f}", True, pygame.Color('white'), pygame.Color('black'))
        screen.blit(fps_text, (10, 10))
        
        light_pos_text = font.render(f"Światło: ({light.pos.x:.1f}, {light.pos.y:.1f}, {light.pos.z:.1f})", True, pygame.Color('white'), pygame.Color('black'))
        screen.blit(light_pos_text, (10, 35))

        sphere_pos_text = font.render(f"Kula: ({sphere_pos.x:.1f}, {sphere_pos.y:.1f}, {sphere_pos.z:.1f}) R={sphere_radius:.1f}", True, pygame.Color('white'), pygame.Color('black'))
        screen.blit(sphere_pos_text, (10, 60)) 

        current_material_name = available_materials[current_material_index].name
        material_text = font.render(f"Materiał: {current_material_name}", True, pygame.Color('white'), pygame.Color('black'))
        screen.blit(material_text, (10, 85))

        pygame.display.flip()
        clock.tick(0) # 0 for uncapped FPS, or e.g. 60 for 60 FPS cap

    pygame.quit()

if __name__ == '__main__':
    main_realtime()