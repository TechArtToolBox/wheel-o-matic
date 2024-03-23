    
import bpy
import math
import mathutils

BLENDER_VERSION = bpy.app.version

if BLENDER_VERSION < (3,0,0):
    from rna_prop_ui import rna_idprop_ui_prop_get
    # import rna_prop_ui

##### classes and operators for the wheel-O-matic ################

# wheel locator creator
class OBJECT_OT_create_wheel_logic_empty(bpy.types.Operator):

    """Create a wheel logic locator at the\nbase of the selected wheel(s)"""
    bl_idname = 'object.empty_add_wheel_locator'
    bl_label = 'Add wheel locator empty'
    bl_options = {"REGISTER", "UNDO"}

    
    def execute(self,context):
        # create global wheel logic if it doesn't exist
        self.create_global_wheel_logic()

        # create wheel locator
        self.create_wheel_locator()

        return {'FINISHED'}
    
    
    def create_global_wheel_logic(self):
        # global wheel logic
        text_name = 'wheel_logic'
        existing_text = bpy.data.texts.get(text_name)
        if not existing_text:
            new_text = bpy.data.texts.new(text_name)
            text_body = self.get_global_wheel_logic_string()
            new_text.write(text_body)
            new_text.use_module = True
            # execute the wheel logic for the first time
            bufferName = text_name
            wheel_logic = bpy.data.texts[bufferName].as_string()
            exec(wheel_logic)

    def get_global_wheel_logic_string(self):
        output = """import bpy
import mathutils
import math
def wheel_logic(mtx,self):
    current_pos = mtx.translation
    obj = bpy.data.objects[self.name]
    previous_pos =  mathutils.Vector(obj['position_old'])
    forward = mathutils.Vector((mtx[0][2], mtx[1][2], mtx[2][2]))
    forward_mag = forward.magnitude
    forward = forward.normalized()
    change = mathutils.Vector(current_pos - previous_pos)
    traveled = (change.magnitude)
    change_direction = change.normalized()
    dot_scalar = change_direction.dot(forward)
    inverter = 1
    manual_rot_inverter = 1
    if obj.delta_rotation_euler[0] < 0 or obj.delta_rotation_euler[1] < 0:
        inverter = -1
        manual_rot_inverter = -1
    if obj['scripted_rotation_invert'] == True:
        inverter = inverter*(-1)
    radius = obj['radius'] 
    rad_min = 0.001
    if radius < rad_min:
        radius = rad_min
        obj['radius'] = rad_min
    obj['position_old'] = current_pos
    distance = (traveled*dot_scalar*obj['auto_rot_power'])*inverter
    radians = distance/(radius*forward_mag) + obj['auto_rotation']
    obj['auto_rotation'] = radians
    radians += math.radians(obj['manual_rotation']*manual_rot_inverter)
    return radians
bpy.app.driver_namespace['wheel_logic'] = wheel_logic"""
        return output
              
    def create_wheel_locator(self):
        sel = bpy.context.selected_objects
        for asset in sel:
            is_wheel_locator = asset.get('auto_rotation') is not None
            if is_wheel_locator:
                pass
        # create wheel controller
            else:
                wheel = asset
                mtx = wheel.matrix_world
                loc = mtx.translation
                bounds = wheel.bound_box
                bounds_ws = [mtx @ mathutils.Vector(corner) for corner in bounds]

                x_vals = []
                y_vals = []
                z_vals = []
                for bound in bounds_ws:
                    x_vals.append(bound[0])
                    y_vals.append(bound[1])
                    z_vals.append(bound[2])
                x_width = max(x_vals) - min(x_vals)
                y_width = max(y_vals) - min(y_vals)
                z_width = max(z_vals) - min(z_vals)
                    
                z_offset = z_width/2
                bpy.ops.object.empty_add(type='SINGLE_ARROW')
                obj = bpy.context.object
                obj.name = wheel.name + '_locator'
                obj.location = loc[0],loc[1],loc[2] - z_offset
                if x_width <= y_width:
                    obj.delta_rotation_euler[0] = math.radians(-90)
                else:
                    obj.delta_rotation_euler[1] = math.radians(90)
                radius = z_offset
                obj.scale = [radius,radius,radius]
                bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

                # add custom properties
                obj['auto_rotation'] = 0.0
                obj['position_old'] = (0.0,0.0,0.0)
                obj['scripted_rotation_invert'] = False

                auto_strength = 'auto_rot_power'
                obj[auto_strength] = 1.0

                manual_rotation = 'manual_rotation'
                obj[manual_rotation] = 0.0
            
                radius_property = 'radius'
                obj[radius_property] = radius

                scripted_rotation = 'scripted_rotation'
                obj[scripted_rotation] = 0.0

                # define tool tips
                desc_radius = 'Radius of the wheel geo this controller drives. Adjust as needed to match geo'
                desc_auto_rot = 'Strength of the automatic rotation. Type in values to go beyond the -1 to 1 range if needed'
                desc_manual_rot = 'Manually rotate the wheel on top of the automatic rotation'
                desc_total_rot = 'Total rotation of the wheel in radians. (auto and manual rotation)'
                desc_invert_rot = 'Invert the AUTO rotation direction that the wheel currently rotates'


                # adjust custom property settings with legacy support

                if BLENDER_VERSION >= (3,0,0):
                    # for blender 3.0.0 and above
                    property_manager = obj.id_properties_ui(auto_strength)
                    property_manager.update(soft_min=-1, soft_max=1, description = desc_auto_rot)
                    property_manager = obj.id_properties_ui(manual_rotation)
                    property_manager.update(step=10, description = desc_manual_rot)
                    property_manager = obj.id_properties_ui(radius_property)
                    property_manager.update(min=0.001, description = desc_radius)
                    property_manager = obj.id_properties_ui(scripted_rotation)
                    property_manager.update(description = desc_total_rot)

                else:
                    # for anything older than 3.0.0
                    ui = rna_idprop_ui_prop_get(obj, radius_property)
                    ui['description'] = desc_radius
                    ui['min'] = 0.001
                    ui = rna_idprop_ui_prop_get(obj, auto_strength)
                    ui['description'] = desc_auto_rot
                    ui['use_soft_limits'] = True
                    ui['soft_min'] = -1
                    ui['soft_max'] = 1
                    ui = rna_idprop_ui_prop_get(obj, manual_rotation)
                    ui['description'] = desc_manual_rot
                    ui = rna_idprop_ui_prop_get(obj, scripted_rotation)
                    ui['description'] = desc_total_rot

                

                
    
                # scripted rotation driver
                fcurve = obj.driver_add('["scripted_rotation"]')
                driver = fcurve.driver
                driver.use_self = True
                driver.expression = 'wheel_logic(matrix_world,self)'
                var = driver.variables.new()
                var.type = 'SINGLE_PROP'
                var.name = 'matrix_world'
                targets = var.targets
                targets[0].transform_space = 'WORLD_SPACE'
                targets[0].id = obj
                targets[0].data_path = 'matrix_world'

                # force update total rotation to be zeroed out on creation
                currentFrame = bpy.data.scenes['Scene'].frame_current
                bpy.data.scenes['Scene'].frame_set(currentFrame)
                obj["auto_rotation"] = 0.0

class OBJECT_OT_zero_scripted_rotation(bpy.types.Operator):
    """Reset AUTO wheel rotation to zero"""
    bl_idname = 'object.zero_scripted_rotation'
    bl_label = 'Reset auto wheel rotation to zero'
    bl_options = {"REGISTER", "UNDO"}

    
    def execute(self,context):
        # reset auto rotation
        self.reset_auto_rotation()
        return {'FINISHED'}

    def reset_auto_rotation(self):
        # zero out any auto rotation of the wheel drivers
        selected = bpy.context.selected_objects
        for sel in selected:
            is_wheel_locator = sel.get('auto_rotation') is not None
            if is_wheel_locator:
                sel["auto_rotation"] = 0.0
                # force the 3d view to redraw the change by updating current frame to be the current frame
                currentFrame = bpy.data.scenes['Scene'].frame_current
                bpy.data.scenes['Scene'].frame_set(currentFrame)


class OBJECT_OT_drive_x_rotation(bpy.types.Operator):
    """Connect rotation info to the X rotation"""
    bl_idname = 'object.drive_x_rotation'
    bl_label = 'Connect rotation info to the X rotation'
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self,context):
        drive_rotation(0)
        return {'FINISHED'}


class OBJECT_OT_drive_y_rotation(bpy.types.Operator):
    """Connect rotation info to the Y rotation"""
    bl_idname = 'object.drive_y_rotation'
    bl_label = 'Connect rotation info to the Y rotation'
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self,context):
        # set up driver 
        drive_rotation(1)
        return {'FINISHED'}
    
class OBJECT_OT_drive_z_rotation(bpy.types.Operator):
    """Connect rotation info to the Z rotation"""
    bl_idname = 'object.drive_z_rotation'
    bl_label = 'Connect rotation info to the Z rotation'
    bl_options = {"REGISTER", "UNDO"}
    
    def execute(self,context):
        # set up driver 
        drive_rotation(2)
        return {'FINISHED'}


def drive_rotation(axis):
# connect the delta rotation of an object to a wheel driver
    selected = bpy.context.selected_objects
    locator = None
    target = None
    for sel in selected:
        is_wheel_locator = sel.get('auto_rotation') is not None
        if is_wheel_locator:
            locator = sel
        else:
            type = sel.type
            # handle driving a bone
            if type == 'ARMATURE':
                target = bpy.context.active_pose_bone

            # all other objects
            else:
                target = sel

    # if the selection is correct, do the connection
    if target and locator:
        # remove old drivers
        target.driver_remove('rotation_euler', axis)


        # create driver
        fcurve = target.driver_add('rotation_euler', axis)
        driver = fcurve.driver
        driver.expression = 'scripted_rotation'
        var = driver.variables.new()
        var.type = 'SINGLE_PROP'
        var.name = 'scripted_rotation'
        targets = var.targets
        targets[0].transform_space = 'WORLD_SPACE'
        targets[0].id = locator
        targets[0].data_path = '["scripted_rotation"]'


def find_drivers_by_expression(obj,expression):
    animation_data = obj.animation_data
    drivers = animation_data.drivers
    for fcurve in drivers:
        driver = fcurve.driver
        exp = driver.expression
        print(driver.expression)
        if exp == expression:
            #do stuff
            pass


classes = [OBJECT_OT_create_wheel_logic_empty,OBJECT_OT_zero_scripted_rotation,
           OBJECT_OT_drive_x_rotation,OBJECT_OT_drive_y_rotation,OBJECT_OT_drive_z_rotation]