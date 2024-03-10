
# add on meta data 
bl_info = {
    'name' : 'Wheel-O-Matic',
    'author' : 'Tech Art Tool Box',
    'version' : (1,0,0),
    'blender' : (2,83,0),
    'location' : '3D Viewport sidebar',
    'description' : 'Utility for automatic wheel rotation',
    'doc_url': 'https://www.youtube.com/@techarttoolbox',
    'category' : 'Development'
    }

import bpy
from wheel_o_matic import wheel_utilities as wu
from wheel_o_matic import wheel_ui as ui

def register():
    for cls in ui.classes:
        bpy.utils.register_class(cls)
        
    bpy.types.Scene.wheel_o_matic = bpy.props.PointerProperty(type=ui.Wheel_UI_Properties)

    for cls in wu.classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(ui.classes):
        bpy.utils.unregister_class(cls)
        
    del bpy.types.Scene.wheel_o_matic

    for cls in reversed(wu.classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()