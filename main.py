import contextlib
with contextlib.redirect_stdout(None): # aby nie wyswietlać przywitania od biblioteki pygame
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
            if occluder is asset and not asset.material.casts_self_shadow: # Example: don't self-shadow if material says so
                continue
            shadow_intersected, shadow_hit_point = occluder.intersect(shadow_ray)
            if shadow_intersected:
                dist_to_shadow_hit = norm(shadow_hit_point - shadow_ray_origin)
                # Jeśli trafienie jest między punktem a światłem
                if dist_to_shadow_hit < distance_to_light:
                    in_shadow = True
                    break 
        
        # Składowa otoczenia (zawsze obecna)
        # Use material properties for ambient color
        color_ambient = asset.material.k_ambient * asset.material.ambient_color_effect
        
        color_diffuse = Vec3(0,0,0)
        color_specular = Vec3(0,0,0)

        if not in_shadow:
            light_intensity_at_point = light.strength(intersection_point) * light.color
            
            # Składowa rozproszenia
            diffuse_factor = max(dot(surface_normal, light_dir_normalized), 0.0)
            color_diffuse = asset.material.k_diffuse * diffuse_factor * light_intensity_at_point
            
            # Składowa odbicia lustrzanego
            r_vec_orig_style = normalize(2 * surface_normal * dot(surface_normal, light_dir_normalized) - light_dir_normalized)
            specular_factor = pow(max(dot(r_vec_orig_style, view_dir_normalized), 0.0), asset.material.n_specular)
            color_specular = asset.material.k_specular * specular_factor * light_intensity_at_point
                        
        pixel_color = mul_vec3(asset.material.base_color, color_ambient + color_diffuse + color_specular)

    return pixel_color


def main_realtime():
    pygame.init()

    #informacje o materialach
    available_materials = [metal_material, kreda_material,guma_material,plastik_material] 
    current_material_index = 0

    # ustawienia okna
    rendering_res = 200 # Internal rendering resolution
    scale_factor = 3 # How many times to scale up the rendered image
    
    display_width = rendering_res * scale_factor
    display_height = rendering_res * scale_factor
    
    screen = pygame.display.set_mode((display_width, display_height))
    pygame.display.set_caption(f"RayTracer Czasu Rzeczywistego (Render: {rendering_res}x{rendering_res}, Display: {display_width}x{display_height})")

    # Create an off-screen surface for rendering
    render_surface = pygame.Surface((rendering_res, rendering_res))

    # ustawienia kamery
    camera = Camera((rendering_res, rendering_res)) # pozycja 0,0,0

    # PARAMETRY OBIEKTU
    sphere_radius = 0.5
    sphere_pos = Vec3(0, 2, 0) # Adjusted Y to be further from camera for better view
    sphere = Sphere(pos=sphere_pos, radius=sphere_radius, material=available_materials[current_material_index])

    # PARAMETRY ŚWIATŁA
    light_pos = Vec3(1, -2.4, -2.4)
    light_color = Vec3(1,1,1) # White light for more general material appearance
    light_strength = 1.5
    light_radius = 10 # This radius is for attenuation, not physical size
    light = Light(pos=light_pos, color=light_color, strength=light_strength, radius=light_radius)

    light_move_speed = 0.2 # szybkość poruszania światłem

    scene_assets = [sphere]
    # asset_to_render = sphere # This will be determined per pixel now

    running = True
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24) # Font size might need adjustment for larger display

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
    Pozycja (X, Y, Z): ({sphere.pos.x}, {sphere.pos.y}, {sphere.pos.z})
    Promień:           {sphere.radius}
    Materiał:          {initial_sphere_material_name}

    Parametry początkowe światła:
    Pozycja (X, Y, Z): ({light.pos.x}, {light.pos.y}, {light.pos.z})
    Kolor (R, G, B):   ({light.color.x}, {light.color.y}, {light.color.z})
    Siła:              {light._strength}
    Promień działania: {light.radius}

    Ustawienia renderowania:
    Rozdzielczość renderowania: {rendering_res}x{rendering_res} pikseli
    Rozdzielczość wyświetlania: {display_width}x{display_height} pikseli
    Skala wyświetlania:         {scale_factor}x
    Pozycja kamery:             (0, 0, 0) (domyślna)
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
                    # Assuming all assets in scene_assets that can change material should change
                    for asset_in_scene in scene_assets:
                        if isinstance(asset_in_scene, Sphere): # Or some other check if needed
                            asset_in_scene.material = available_materials[current_material_index]
                    print(f"Materiał kul zmieniony na: {available_materials[current_material_index].name}")

        # --- Rendering phase (to off-screen render_surface) ---
        for u_pixel in range(camera.res_width): # camera.res_width is rendering_res
            for v_pixel in range(camera.res_height): # camera.res_height is rendering_res
                primary_ray = camera.shoot_ray(u_pixel, v_pixel)
                closest_hit_asset = None
                min_dist = float('inf')
                
                # Find closest intersected asset
                # (This part was simplified in your original code to only check asset_to_render)
                # For a more general ray tracer, you'd loop through all scene_assets here.
                # For now, we'll stick to the single sphere for simplicity, but use the list.
                temp_intersection_point = None # To store the intersection point of the closest hit

                for asset_in_scene in scene_assets:
                    intersected, intersection_point_candidate = asset_in_scene.intersect(primary_ray)
                    if intersected:
                        dist = norm(intersection_point_candidate - primary_ray.o)
                        if dist < min_dist:
                            min_dist = dist
                            closest_hit_asset = asset_in_scene
                            # temp_intersection_point = intersection_point_candidate # Not needed directly here, calculate_pixel_color re-calculates intersection

                final_color_vec3 = Vec3(0,0,0) 
                if closest_hit_asset:
                    # Pass u_pixel, v_pixel corresponding to the render_surface resolution
                    final_color_vec3 = calculate_pixel_color(u_pixel, v_pixel, camera, light, closest_hit_asset, scene_assets)
                
                r = floatto8bit(final_color_vec3.x)
                g = floatto8bit(final_color_vec3.y)
                b = floatto8bit(final_color_vec3.z)
                render_surface.set_at((u_pixel, v_pixel), (r, g, b))

        # --- Scaling and Display phase ---
        # Scale the render_surface to the display size
        scaled_surface = pygame.transform.scale(render_surface, (display_width, display_height))
        
        # Blit the scaled surface to the main screen
        screen.blit(scaled_surface, (0, 0))

        # --- UI Overlay (draw on top of the scaled image) ---
        fps = clock.get_fps()
        fps_text = font.render(f"FPS: {fps:.1f}", True, pygame.Color('white'), pygame.Color('black'))
        screen.blit(fps_text, (10, 10)) # Adjusted position slightly
        
        light_pos_text = font.render(f"Światło: ({light.pos.x:.1f}, {light.pos.y:.1f}, {light.pos.z:.1f})", True, pygame.Color('white'), pygame.Color('black'))
        screen.blit(light_pos_text, (10, 35)) # Adjusted position

        current_material_name = available_materials[current_material_index].name
        material_text = font.render(f"Materiał: {current_material_name}", True, pygame.Color('white'), pygame.Color('black'))
        screen.blit(material_text, (10, 60))


        pygame.display.flip()
        clock.tick(60) # Cap FPS if desired, or leave empty for max

    pygame.quit()

if __name__ == '__main__':
    main_realtime()