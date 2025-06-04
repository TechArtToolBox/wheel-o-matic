# Wheel-O-matic v 1.0.0 
# Blender addon for automatic wheel rotation
# Any reference in script to 'wom' is shorthand for Wheel-O-Matic related data

# Legacy Support for BLENDER_VERSION < (4,2,0)
bl_info = {
    'name' : 'Wheel-O-Matic',
    'author' : 'Tech Art Tool Box',
    'version' : (1,0,0),
    'blender' : (3,0,0),
    'location' : '3D Viewport > Sidebar > Wheel-O-Matic',
    'description' : 'Automatic wheel rotation in any direction. Works with meshes and bones.',
    'doc_url': 'https://github.com/TechArtToolBox/wheel-o-matic/',
    'category' : 'Rigging'
    }


import bpy
from bpy.app.handlers import persistent

from . import wom_operators
from . import wom_properties
from . import wom_render
from . import wom_ui
from . import wom_utilities


def register():

    #### Register Classes

    # Properties
    for cls in wom_properties.classes:
        bpy.utils.register_class(cls)

    # UI 
    for cls in wom_ui.classes:
        bpy.utils.register_class(cls)

    # Operators
    for cls in wom_operators.classes:
        bpy.utils.register_class(cls)

    # Draw logic for wom locators
    for cls in wom_render.classes:
        bpy.utils.register_class(cls)

    

    #### Register Properties

    # UI PropertyGroup
    bpy.types.Scene.wom_ui = bpy.props.PointerProperty(type=wom_properties.WOM_UI_Properties)

    # Object PropertyGroup 
    bpy.types.Object.wom = bpy.props.PointerProperty(type=wom_properties.WOM_Object_Properties)
    
    # Pose Bones PropertyGroup 
    bpy.types.PoseBone.wom = bpy.props.PointerProperty(type=wom_properties.WOM_Object_Properties)

    # Scene PropertyGroup (referenced by locator logic for drawing locators, used to store wom driven objects)
    bpy.types.Scene.wom = bpy.props.PointerProperty(type=wom_properties.WOM_Scene_References)

    # Properties Not In A PropertyGroup
    wom_properties.register_top_level_properties()



    #### Register Wheel Logic In The Driver Namespace

    # On install
    bpy.app.driver_namespace['wom_wheel_logic'] = wom_utilities.wom_wheel_logic

    # When Blender opens
    bpy.app.handlers.load_post.append(custom_load_handling)


def unregister():

    # Remove global wheel logic 
    driver_logic = bpy.app.driver_namespace.get('wom_wheel_logic')
    if driver_logic:
        del bpy.app.driver_namespace['wom_wheel_logic']

    # Remove locator draw handler
    locator_draw_handler_key = 'wom_locators'
    locator_draw_logic = bpy.app.driver_namespace.get(locator_draw_handler_key)
    if locator_draw_logic:
        del bpy.app.driver_namespace[locator_draw_handler_key]

    # Unregister classes
    for cls in reversed(wom_properties.classes):
        bpy.utils.unregister_class(cls)

    for cls in reversed(wom_ui.classes):
        bpy.utils.unregister_class(cls)
        
    for cls in reversed(wom_operators.classes):
        bpy.utils.unregister_class(cls)

    for cls in reversed(wom_render.classes):
        bpy.utils.unregister_class(cls)

    # Delete wom property groups
    del bpy.types.Object.wom
    del bpy.types.PoseBone.wom
    del bpy.types.Scene.wom
    del bpy.types.Scene.wom_ui


#### Post load handling (called above for global wheel logic)
@persistent
def custom_load_handling(scene):
    """Add wheel logic to the driver_namespace once Blender has loaded."""
    bpy.app.driver_namespace['wom_wheel_logic'] = wom_utilities.wom_wheel_logic


if __name__ == "__main__":
    register()