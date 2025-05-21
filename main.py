import pygame
from Vec3 import Vec3, normalize, dot, cross, norm, mul_vec3
from assets import Camera, Sphere, Light, Material, floatto8bit, Ray
from materials import *

# Parametry materiału
ambient_color_effect = 0.4 * Vec3(0.4, 0.4, 1)
k_ambient = 1.0
k_diffuse = 2.0
k_specular = 10.0
n_specular = 50.0

def calculate_pixel_color(u, v, camera, light, asset, all_scene_assets):
    """
    Oblicza kolor dla piksela poprzez wystrzelenie pojedynczego promienia, włączając sprawdzanie cieni.
    :param u: pozioma współrzędna piksela
    :param v: pionowa współrzędna piksela
    :param camera: obiekt Camera
    :param light: obiekt Light
    :param asset: główny obiekt, z którym ten promień się przeciął
    :param all_scene_assets: lista wszystkich obiektów na scenie do sprawdzania cieni
    :return: kolor Vec3 dla piksela
    """
    
    ray = camera.shoot_ray(u, v) # Wystrzel promień dla danego piksela
    intersected, intersection_point = asset.intersect(ray)
    
    pixel_color = Vec3(0, 0, 0) # Domyślny kolor tła
    if intersected:
        surface_normal = asset.normal(intersection_point)
        vec_to_light_source = light.pos - intersection_point
        
        light_dir_normalized = normalize(vec_to_light_source)
        view_dir_normalized = normalize(ray.o - intersection_point)

        # Sprawdzanie cienia
        in_shadow = False
        # Przesuń punkt początkowy nieco wzdłuż normalnej, aby uniknąć samo-przecięcia
        shadow_ray_origin = intersection_point + surface_normal * 1e-4 
        shadow_ray = Ray(shadow_ray_origin, light_dir_normalized)
        
        distance_to_light = norm(vec_to_light_source)

        for occluder in all_scene_assets:
            # Nie ma potrzeby sprawdzać przecięcia, jeśli obiekt zasłaniający jest samym źródłem światła
            # lub jeśli sprawdzamy z przezroczystym obiektem, który nie rzuca pełnych cieni.
            shadow_intersected, shadow_hit_point = occluder.intersect(shadow_ray)
            if shadow_intersected:
                dist_to_shadow_hit = norm(shadow_hit_point - shadow_ray_origin)
                # Jeśli trafienie jest między punktem a światłem
                if dist_to_shadow_hit < distance_to_light:
                    in_shadow = True
                    break 
        
        # Składowa otoczenia (zawsze obecna)
        color_ambient = k_ambient * ambient_color_effect
        
        color_diffuse = Vec3(0,0,0)
        color_specular = Vec3(0,0,0)

        if not in_shadow:
            light_intensity_at_point = light.strength(intersection_point) * light.color
            
            # Składowa rozproszenia
            diffuse_factor = max(dot(surface_normal, light_dir_normalized), 0.0)
            color_diffuse = k_diffuse * diffuse_factor * light_intensity_at_point
            
            # Składowa odbicia lustrzanego
            r_vec_orig_style = normalize(2 * surface_normal * dot(surface_normal, light_dir_normalized) - light_dir_normalized) # Poprawiony wektor odbicia (Blinn-Phong half-vector byłby alternatywą)
            specular_factor = pow(max(dot(r_vec_orig_style, view_dir_normalized), 0.0), n_specular)
            color_specular = k_specular * specular_factor * light_intensity_at_point
                        
        pixel_color = mul_vec3(asset.color, color_ambient + color_diffuse + color_specular)

    return pixel_color


def main_realtime():
    pygame.init()

    available_materials = [metal_material, kreda_material,guma_material,plastik_material] 
    current_material_index = 0

    res = 200
    screen_width = res
    screen_height = res
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("RayTracer Czasu Rzeczywistego - Pozycja Światła: Strzałki (XZ), PgUp/Dn (Y)")

    camera = Camera((res, res))
    sphere = Sphere(pos=Vec3(0, 2, 0), radius=0.5, material=available_materials[current_material_index])

    light = Light(pos=Vec3(1, -2.4, -2.4), color=Vec3(1, 1, 0.8), strength=1.5, radius=10)
    
    scene_assets = [sphere]
    asset_to_render = sphere 

    light_move_speed = 0.2

    running = True
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)

    print("Sterowanie: Klawisze strzałek do poruszania światłem w płaszczyźnie XZ, PageUp/PageDown dla osi Y.")
    print("ESC aby wyjść. 'X' aby zmienić materiał kuli.")

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                if event.key == pygame.K_LEFT:
                    light.pos.z += light_move_speed
                if event.key == pygame.K_RIGHT:
                    light.pos.z -= light_move_speed
                if event.key == pygame.K_UP:
                    light.pos.x -= light_move_speed
                if event.key == pygame.K_DOWN:
                    light.pos.x += light_move_speed
                if event.key == pygame.K_PAGEUP:
                    light.pos.y += light_move_speed
                if event.key == pygame.K_PAGEDOWN:
                    light.pos.y -= light_move_speed
                
                if event.key == pygame.K_x:
                    current_material_index = (current_material_index + 1) % len(available_materials)
                    asset_to_render.material = available_materials[current_material_index]
                    print(f"Materiał kuli zmieniony na: {asset_to_render.material.name}")


        for u_pixel in range(camera.res_width):
            for v_pixel in range(camera.res_height):
                primary_ray = camera.shoot_ray(u_pixel, v_pixel)
                closest_hit_asset = None
                # closest_intersection_point = None # Nie jest już potrzebne tutaj
                min_dist = float('inf')

                intersected, intersection_point_candidate = asset_to_render.intersect(primary_ray)
                if intersected:
                    dist = norm(intersection_point_candidate - primary_ray.o)
                    if dist < min_dist:
                        # min_dist = dist # Nie jest już potrzebne, bo mamy tylko jeden asset_to_render
                        closest_hit_asset = asset_to_render
                        # closest_intersection_point = intersection_point_candidate # Nie jest już potrzebne tutaj
                
                final_color_vec3 = Vec3(0,0,0) 
                if closest_hit_asset:
                    final_color_vec3 = calculate_pixel_color(u_pixel, v_pixel, camera, light, closest_hit_asset, scene_assets)
                
                r = floatto8bit(final_color_vec3.x)
                g = floatto8bit(final_color_vec3.y)
                b = floatto8bit(final_color_vec3.z)
                screen.set_at((u_pixel, v_pixel), (r, g, b))

        fps = clock.get_fps()
        fps_text = font.render(f"FPS: {fps:.1f}", True, pygame.Color('white'), pygame.Color('black'))
        screen.blit(fps_text, (5, 5))
        
        light_pos_text = font.render(f"Światło: ({light.pos.x:.1f}, {light.pos.y:.1f}, {light.pos.z:.1f})", True, pygame.Color('white'), pygame.Color('black'))
        screen.blit(light_pos_text, (5, 25))

        pygame.display.flip()
        clock.tick()

    pygame.quit()

if __name__ == '__main__':
    main_realtime()