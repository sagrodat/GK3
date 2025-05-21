import pygame
from Vec3 import Vec3, normalize, dot, cross, norm, mul_vec3 # Make sure mul_vec3 is imported
from assets import Camera, Sphere, Light, Material, floatto8bit, Ray # Added Ray for shadow rays
from materials import *

# Material parameters (constants from original)
ambient_color_effect = 0.4 * Vec3(0.4, 0.4, 1) # Renamed 'ambient' to avoid conflict if a light is named ambient
k_ambient = 1.0
k_diffuse = 2.0
k_specular = 10.0
n_specular = 50.0

def calculate_pixel_color(u, v, camera, light, asset, all_scene_assets, antialias_level=0): # Added all_scene_assets
    """
    Calculates the color for a pixel by shooting rays, including shadow checks.
    :param u: horizontal pixel coordinate
    :param v: vertical pixel coordinate
    :param camera: Camera object
    :param light: Light object
    :param asset: The primary asset this ray intersected
    :param all_scene_assets: A list of all assets in the scene for shadow checking
    :param antialias_level: level of antialiasing (0 for no AA)
    :return: Vec3 color for the pixel
    """
    
    num_subsamples_axis = 2 ** antialias_level
    total_color = Vec3(0, 0, 0)
    
    if num_subsamples_axis == 1: 
        offsets = [0.0] 
    else:
        offsets = [(2.0 * i / num_subsamples_axis) - (1.0 - 1.0 / num_subsamples_axis) for i in range(num_subsamples_axis)]

    for du_offset in offsets:
        for dv_offset in offsets:
            current_u = u + du_offset
            current_v = v + dv_offset
            
            ray = camera.shoot_ray(current_u, current_v)
            intersected, intersection_point = asset.intersect(ray)
            
            pixel_sample_color = Vec3(0, 0, 0) 
            if intersected:
                surface_normal = asset.normal(intersection_point)
                vec_to_light_source = light.pos - intersection_point
                
                light_dir_normalized = normalize(vec_to_light_source)
                view_dir_normalized = normalize(ray.o - intersection_point)

                # Shadow check
                in_shadow = False
                # Offset origin slightly along the normal to avoid self-intersection ("shadow acne")
                shadow_ray_origin = intersection_point + surface_normal * 1e-4 
                shadow_ray = Ray(shadow_ray_origin, light_dir_normalized)
                
                distance_to_light = norm(vec_to_light_source)

                for occluder in all_scene_assets:
                    # No need to check intersection if the occluder is the light source itself (if lights were assets)
                    # or if checking against a transparent object that doesn't cast full shadows.
                    shadow_intersected, shadow_hit_point = occluder.intersect(shadow_ray)
                    if shadow_intersected:
                        dist_to_shadow_hit = norm(shadow_hit_point - shadow_ray_origin)
                        # If the hit is between the point and the light
                        if dist_to_shadow_hit < distance_to_light:
                            in_shadow = True
                            break 
                
                # Ambient component (always present)
                color_ambient = k_ambient * ambient_color_effect
                
                color_diffuse = Vec3(0,0,0)
                color_specular = Vec3(0,0,0)

                if not in_shadow:
                    light_intensity_at_point = light.strength(intersection_point) * light.color
                    
                    # Diffuse component
                    diffuse_factor = max(dot(surface_normal, light_dir_normalized), 0.0)
                    color_diffuse = k_diffuse * diffuse_factor * light_intensity_at_point
                    
                    # Specular component
                    r_vec_orig_style = normalize(2 * surface_normal - vec_to_light_source) 
                    specular_factor = pow(max(dot(r_vec_orig_style, view_dir_normalized), 0.0), n_specular)
                    color_specular = k_specular * specular_factor * light_intensity_at_point
                                
                pixel_sample_color = mul_vec3(asset.color, color_ambient + color_diffuse + color_specular)

            total_color += pixel_sample_color
            
    return total_color / (num_subsamples_axis * num_subsamples_axis)


def main_realtime():
    pygame.init()

    available_materials = [metal_material, kreda_material,guma_material,plastik_material] 
    current_material_index = 0

    res = 200
    screen_width = res
    screen_height = res
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Real-time RayTracer - Light Pos: Arrows (XZ), PgUp/Dn (Y)")

    camera = Camera((res, res))
    sphere = Sphere(pos=Vec3(0, 2, 0), radius=0.5, material=available_materials[current_material_index])

    light = Light(pos=Vec3(1, -2.4, -2.4), color=Vec3(1, 1, 0.8), strength=1.5, radius=10)
    
    # List of all assets in the scene for rendering and shadow calculation
    # For now, it's just the sphere. If you add more objects, add them here.
    scene_assets = [sphere]
    asset_to_render = sphere 

    antialias_level = 0
    light_move_speed = 0.2

    running = True
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)

    print("Controls: Arrow keys to move light in XZ plane, PageUp/PageDown for Y.")
    print("ESC to quit. 'A' to toggle antialiasing.")

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
                if event.key == pygame.K_a:
                    antialias_level = (antialias_level + 1) % 2
                    print(f"Antialiasing level set to: {antialias_level}")

                if event.key == pygame.K_x:
                    current_material_index = (current_material_index + 1) % len(available_materials)
                    asset_to_render.material = available_materials[current_material_index]
                    print(current_material_index)
                    print(f"Sphere1 material switched to: {asset_to_render.material.name}")

        for u_pixel in range(camera.res_width):
            for v_pixel in range(camera.res_height):
                # For this simple setup, the first asset intersected is the one we render.
                # In a more complex scene, you'd find the closest intersection among all scene_assets.
                # Here, asset_to_render is the sphere.
                # The ray from camera.shoot_ray is the primary ray.
                primary_ray = camera.shoot_ray(u_pixel, v_pixel)
                closest_hit_asset = None
                closest_intersection_point = None
                min_dist = float('inf')

                intersected, intersection_point_candidate = asset_to_render.intersect(primary_ray)
                if intersected:
                    dist = norm(intersection_point_candidate - primary_ray.o)
                    if dist < min_dist:
                        min_dist = dist
                        closest_hit_asset = asset_to_render
                        closest_intersection_point = intersection_point_candidate
                
                final_color_vec3 = Vec3(0,0,0) # Background color if no hit
                if closest_hit_asset:
                    # Pass all scene_assets for shadow checking
                    final_color_vec3 = calculate_pixel_color(u_pixel, v_pixel, camera, light, closest_hit_asset, scene_assets, antialias_level)
                
                r = floatto8bit(final_color_vec3.x)
                g = floatto8bit(final_color_vec3.y)
                b = floatto8bit(final_color_vec3.z)
                screen.set_at((u_pixel, v_pixel), (r, g, b))

        fps = clock.get_fps()
        fps_text = font.render(f"FPS: {fps:.1f}", True, pygame.Color('white'), pygame.Color('black'))
        screen.blit(fps_text, (5, 5))
        
        light_pos_text = font.render(f"Light: ({light.pos.x:.1f}, {light.pos.y:.1f}, {light.pos.z:.1f})", True, pygame.Color('white'), pygame.Color('black'))
        screen.blit(light_pos_text, (5, 25))

        pygame.display.flip()
        clock.tick()

    pygame.quit()

if __name__ == '__main__':
    main_realtime()