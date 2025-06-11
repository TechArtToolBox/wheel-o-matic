import bpy

from . import wom_strings as ws
from . import wom_utilities as wu

    
# Automate meshes
class OBJECT_OT_wom_setup_mesh(bpy.types.Operator):
    """Automate rotation on the selected wheels"""
    bl_idname = 'object.wom_wheel_setup_mesh'
    bl_label = 'Wheel-O-Matic: Mesh setup'
    bl_options = {"REGISTER", "UNDO"}

    
    def execute(self,context):

        # re-register the global logic in case the user somehow deleted it
        wu.register_wom_wheel_logic()
        # apply setup
        success = wu.mesh_wheel_bulk_setup()
        if success == True:
            self.report({'INFO'}, ws.automate_success)
        else:
            self.report({'WARNING'}, ws.automate_fail)

        # turn on locators
        drawing_locators = wu.locator_draw_handler_exists()
        if not drawing_locators:
            bpy.ops.object.wom_draw_locators('INVOKE_DEFAULT')
        return {'FINISHED'}


# Automate pose bone
class OBJECT_OT_wom_setup_bone(bpy.types.Operator):
    """Automate rotation of selected bone"""
    bl_idname = 'object.wom_wheel_setup_bone'
    bl_label = 'Wheel-O-Matic: Bone setup'
    bl_options = {"REGISTER", "UNDO"}   


    def execute(self,context):
        
        # re-register the global logic in case the user somehow deleted it
        wu.register_wom_wheel_logic()

        success = wu.bone_setup()
        if success == True:
            self.report({'INFO'}, ws.automate_success)
        else:
            self.report({'WARNING'}, ws.automate_fail)

        # turn on locators
        drawing_locators = wu.locator_draw_handler_exists()
        if not drawing_locators:
            bpy.ops.object.wom_draw_locators('INVOKE_DEFAULT')
        return {'FINISHED'}


# Zero out auto rotation for the selected meshes/bones
class OBJECT_OT_wom_clear_rotation(bpy.types.Operator):
    """Reset automated wheel rotation to zero"""
    bl_idname = 'object.wom_wheel_clear_rotation'
    bl_label = 'Wheel-O-Matic: Clear automated rotation'
    bl_options = {"REGISTER", "UNDO"}

    def execute(self,context):
        wu.clear_rotation()
        return {'FINISHED'}


# Remove wom automation for the selected meshes/bones
class OBJECT_OT_wom_remove_automation(bpy.types.Operator):
    """Removes any Wheel-O-Matic automation/controls from the selected meshes/bones"""
    bl_idname = 'object.wom_wheel_remove_automation'
    bl_label = 'Wheel-O-Matic: Remove automation'
    bl_options = {"REGISTER", "UNDO"}

    
    def execute(self,context):
        wu.remove_automation_bulk()
        return {'FINISHED'}
    
    def invoke(self, context, event):
        title_txt = 'Remove autmation for the selected wheels/bones?'
        button_txt = 'Remove'

        try:
            return context.window_manager.invoke_props_dialog(self,confirm_text=button_txt,title=title_txt)
        except:
            return context.window_manager.invoke_props_dialog(self)


# Remove stray wom data (stray data occurs when a driven mesh/bone is deleted)
class OBJECT_OT_wom_remove_stray_data(bpy.types.Operator):
    """ Removes any stray Wheel-O-Matic data that no longer drives a wheel or bone"""
    bl_idname = 'object.wom_remove_stray_data'
    bl_label = 'Wheel-O-Matic: Remove stray data'
    bl_options = {"REGISTER", "UNDO"}

    def execute(self,context):
        wu.remove_stray_wom_data_from_scene()
        return {'FINISHED'}
    
    def invoke(self, context, event):
        title_txt = 'Remove stray Wheel-O-Matic data from the scene?'
        button_txt = 'Remove'

        try:
            return context.window_manager.invoke_props_dialog(self,confirm_text=button_txt,title=title_txt)
        except:
            return context.window_manager.invoke_props_dialog(self)


# Refresh global wheel logic 
class OBJECT_OT_refresh_wheel_logic(bpy.types.Operator):
    """Refresh Wheel-O-Matic automation logic for entire scene (Rarely needed)"""
    bl_idname = 'object.wom_refresh_wheel_logic'
    bl_label = 'Wheel-O-Matic: Refresh wheel logic'

    def execute(self,context):
        wu.refresh_wheel_logic()

        # turn on locators
        drawing_locators = wu.locator_draw_handler_exists()
        if not drawing_locators:
            bpy.ops.object.wom_draw_locators('INVOKE_DEFAULT')

        return{'FINISHED'}


classes = [OBJECT_OT_wom_setup_mesh,OBJECT_OT_wom_setup_bone,OBJECT_OT_wom_clear_rotation,
            OBJECT_OT_wom_remove_automation,OBJECT_OT_wom_remove_stray_data,OBJECT_OT_refresh_wheel_logic]