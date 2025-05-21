from assets import Material
from Vec3 import Vec3

metal_material = Material(
    name="metal",
    color=Vec3(0.4, 0.4, 0.5),  # Jasnoszary, lekko niebieskawy odcień dla stali
    ambient_coeff=0.25,
    diffuse_coeff=0.4,          # Stosunkowo niski, bo dużo światła odbija się zwierciadlanie
    specular_coeff=0.9,
    shininess=300               # Bardzo wysoka wartość dla ostrych odblasków
)

kreda_material = Material(
    name="kreda",
    color=Vec3(0.95, 0.95, 0.93),  # Lekko złamana biel
    ambient_coeff=0.2,
    diffuse_coeff=0.85,
    specular_coeff=0.05,
    shininess=10
)

guma_material = Material(
    name="guma",
    color=Vec3(0.1, 0.1, 0.1),    # Ciemnoszary/czarny
    ambient_coeff=0.1,
    diffuse_coeff=0.7,
    specular_coeff=0.2,          # Niewielki odblask
    shininess=15                 # Szeroki odblask
)

plastik_material = Material(
    name="plastik",
    color=Vec3(0.1, 0.6, 0.2),   # Zielony
    ambient_coeff=0.15,
    diffuse_coeff=0.7,
    specular_coeff=0.65,         # Wyraźny odblask
    shininess=80                 # Średnio-wysoka połyskliwość dla gładkich odblasków
)