from pygame import Vector3

class Material:
    def __init__(self, name:str, color: Vector3, ambient_coeff: float, diffuse_coeff: float, specular_coeff: float, shininess: float):
        self.name = name
        self.color = color
        self.ambient_coeff = ambient_coeff
        self.diffuse_coeff = diffuse_coeff
        self.specular_coeff = specular_coeff
        self.shininess = shininess

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
