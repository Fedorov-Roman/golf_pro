from .nature import make_tree, make_bush, make_rock, make_ice_block
from .ground import make_bunker, make_water_smooth, make_ice_surface
from .golf_objects import make_ball, make_flag, make_hole_gfx, make_colored_ball
from .zones import make_tee_texture, make_green_texture

def generate_all():
    return {
        'flag': make_flag(),
        'hole': make_hole_gfx()
    }
