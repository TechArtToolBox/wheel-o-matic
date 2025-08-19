import bpy
from . import wom_strings as ws

#### UI Property Group
class WOM_UI_Properties(bpy.types.PropertyGroup):
    
    # filtered poll result for when picking mesh for bone setup
    def valid_wheel_object(self,object):
        """
        Limits the bone setup mesh picker dropdown and eyedropper 
        to the current scene, and limit to mesh objects.
        """
        for scene in object.users_scene:
            if scene.name == bpy.context.scene.name:
                if object.type == 'MESH':
                    return object

    # UI forward facing properties
    f_locator_scale         :   bpy.props.FloatProperty (name = ws.name_loc_scale_global, default=1.0,min=0.01,description = ws.desc_locator_scale)
    p_wheel_obj             :   bpy.props.PointerProperty(name = '', type=bpy.types.Object,poll=valid_wheel_object, description = ws.desc_wheel_obj)
    world_forward_axis      :   bpy.props.EnumProperty(
                                    name= '',
                                    description = "World forward axis of the wheel",
                                    items=  [('auto','Auto','Automatically detect forward axis (default)','',0),
                                            ('x','X','Wheel rolls forward on the world X axis','',1),
                                            ('y','Y','Wheel rolls forward  on the world Y axis','',2)],
                                    default = 'auto'
                                )
    
    # UI internal properties
    b_draw_locators         :   bpy.props.BoolProperty (default=False)



#### WOM object property group
class WOM_Object_Properties(bpy.types.PropertyGroup):

    # internal for wheel logic
    forward_axis            :   bpy.props.StringProperty()
    position_old            :   bpy.props.FloatVectorProperty()
    rotation_old            :   bpy.props.FloatProperty()
    wom_id                  :   bpy.props.StringProperty()
    wom_driven              :   bpy.props.BoolProperty()
    wom_driven_armature     :   bpy.props.BoolProperty()
    wom_type                :   bpy.props.StringProperty()
    wom_defined_parent      :   bpy.props.PointerProperty(type=bpy.types.Object)
    wom_axis_offset         :   bpy.props.FloatVectorProperty(size=16, subtype='MATRIX', default = [1,0,0,0,
                                                                                                    0,1,0,0,
                                                                                                    0,0,1,0,
                                                                                                    0,0,0,1])


#### classes to temporarily store WOM objects on the scene
class WOM_Reference(bpy.types.PropertyGroup):
    wom_object  :   bpy.props.PointerProperty(type=bpy.types.Object)

class WOM_Scene_References(bpy.types.PropertyGroup):
    wom_reference_collection : bpy.props.CollectionProperty(type=WOM_Reference)


#### Register Properties Not In a PropertyGroup
def register_top_level_properties():
    """
    Register wheel radius, rotation power, and auto rotation properties
    for meshes and pose bones. Rotation and radius are forward facing 
    in the UI, and auto rotation is accessed by the global wheel logic. 
    """

    # wom auto rotation
    setattr(bpy.types.Object,ws.wom_auto_rotation,bpy.props.FloatProperty(name=ws.name_auto_rotation,default = 0.0,description=ws.desc_auto_rot))
    setattr(bpy.types.PoseBone,ws.wom_auto_rotation,bpy.props.FloatProperty(name=ws.name_auto_rotation,default = 0.0,description=ws.desc_auto_rot))

    # wom auto rotation power
    setattr(bpy.types.Object,ws.wom_rotation_power,bpy.props.FloatProperty(name=ws.name_auto_rot_power,default = 1,soft_min=-5,soft_max=5,description=ws.desc_auto_rot_power))
    setattr(bpy.types.PoseBone,ws.wom_rotation_power,bpy.props.FloatProperty(name=ws.name_auto_rot_power,default = 1,soft_min=-5,soft_max=5,description=ws.desc_auto_rot_power))
    
    # wom radius
    setattr(bpy.types.PoseBone,ws.wom_radius,bpy.props.FloatProperty(name=ws.name_radius,min=0.001,default=1,description=ws.desc_radius))
    setattr(bpy.types.Object,ws.wom_radius,bpy.props.FloatProperty(name=ws.name_radius,min=0.001,default=1,description=ws.desc_radius))


classes = [WOM_UI_Properties,WOM_Object_Properties,WOM_Reference,WOM_Scene_References]