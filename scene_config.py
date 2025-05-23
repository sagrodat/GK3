from pygame import Vector3

#USTAWIENIA RENDEROWNAIA 
rendering_res = 100
scale_factor = 8

#PARAMETRY KULI
sphere_radius = 0.5
sphere_pos = Vector3(0, 2, 0) # Y=2 oznacza 2 jednostki "przed" kamerą, jeśli kamera patrzy wzdłuż +Y.

#PARAMETRY ŚWIATŁA
light_pos = Vector3(1, -2.4, -2.4)
light_color = Vector3(1,1,1) 
light_strength = 10
light_radius = 5
light_move_speed = 2 #sensitivity