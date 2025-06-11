import bpy
from . import wom_strings as ws
from . import wom_utilities as wu
  

class VIEW3D_PT_wheel_o_matic(bpy.types.Panel):
    """Main panel for Wheel-O-Matic"""
    bl_label = "Wheel-O-Matic"
    bl_category = 'Wheel-O-Matic'
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_order = 10

    # only draw if mode and selection is correct
    @classmethod
    def poll(cls, context):
        allow_draw_result = allow_draw(context)
        return allow_draw_result

    # draw panel
    def draw(self, context):
        wom_ui = context.scene.wom_ui
        layout = self.layout
        col = layout.column()


        # ui for when in object mode
        if bpy.context.mode == 'OBJECT':
            valid_selection = automate_panel_logic_geo()
            box = col.box()
            box.label(text='For Selected Wheel(s)')
            row = box.row()
            row.label(text='Forward Axis:')
            row.prop(wom_ui,'world_forward_axis', expand=False)
            automate_row = box.row()
            automate_row.operator('object.wom_wheel_setup_mesh', text='Automate')
            if not valid_selection:
                automate_row.enabled=False

        # ui for when in pose mode
        if bpy.context.mode == 'POSE':
            col.label(text='Selected Bone:')
            bone_text,valid_bone_selection = automate_panel_logic_bones()
            col2 = col.column()
            c_box = centered_box(col2)
            c_box.label(text=f'{bone_text}')

            col2.label(text= 'Reference Wheel Geo:')
            col2.prop(wom_ui,'p_wheel_obj',text = '')
            col2.separator()
            col2.enabled = valid_bone_selection

            col3 = col.column()
            row = col3.row()
            row.label(text='Forward Axis:')
            row.prop(wom_ui,'world_forward_axis', expand=False)
            col3.operator('object.wom_wheel_setup_bone', text='Automate')
            if not valid_bone_selection or not wom_ui.p_wheel_obj:
                col3.enabled = False


class VIEW3D_PT_wheel_o_matic_adjust(bpy.types.Panel):
    """Adjust panel for Wheel-O-Matic"""
    bl_label = "Adjust"
    bl_category = 'Wheel-O-Matic'
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = 'VIEW3D_PT_wheel_o_matic'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        wom_ui = context.scene.wom_ui
        obj = bpy.context.object
        if obj:
            if obj.type == 'ARMATURE':
                bone = bpy.context.active_pose_bone
                if bone:
                    obj = bone
        layout = self.layout
        allow_adjust, selection_text = adjust_panel_logic()
        col = layout.column()
        col.enabled = allow_adjust

        c_box = centered_box(col)
        c_box.label(text=selection_text)
        if allow_adjust:
            grid = col.grid_flow(columns=1, align=True)
            grid.prop(obj, ws.wom_rotation_power)
            grid.prop(obj, ws.wom_radius)


class VIEW3D_PT_wheel_o_matic_utilities(bpy.types.Panel):
    f"""Utilities panel for Wheel-O-Matic"""
    bl_label = "Utilities"
    bl_category = 'Wheel-O-Matic'
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_parent_id = 'VIEW3D_PT_wheel_o_matic'
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):
        wom_ui = context.scene.wom_ui
        layout = self.layout
        col = layout.column()
        box_selected = col.box()
        box_selected.label(text='For Selected Wheels/Bones:')
        col2 = box_selected.column()
        col2.operator('object.wom_wheel_clear_rotation', text=ws.text_clear_rotation)
        col2.operator('object.wom_wheel_remove_automation', text=ws.text_remove_automation)
        allow_adjust = utilities_panel_logic()
        col2.enabled = allow_adjust
        col.separator()
        box_locators = col.box()
        col3 = box_locators.column()
        col3.label(text='For Locators:')
        locator_draw = wu.locator_draw_handler_exists()
        if locator_draw == True:
            col3.operator('object.wom_remove_locators',text=ws.text_toggle_locators,icon='HIDE_OFF')
        else:
            col3.operator('object.wom_draw_locators',text=ws.text_toggle_locators,icon='HIDE_ON')
        col3.prop(wom_ui,'f_locator_scale')
        col.separator()
        box_scene = col.box()
        col4 = box_scene.column()
        col4.label(text='For Entire Scene:')
        col4.operator('object.wom_remove_stray_data',text=ws.text_remove_stray)
        col4.operator('object.wom_refresh_wheel_logic',text=ws.text_refresh_logic)



def allow_draw(context):
    """ Only draw the UI in object mode or pose mode."""
    valid = False
    mode = bpy.context.mode
    if mode == 'OBJECT':
        valid = True
    if mode == 'POSE':
        valid = True
    return valid

def centered_box(ui_parent):
    """ Draw a UI box that will have centered text."""
    box = ui_parent.box()
    col = box.column()
    row = col.row()
    row.alignment = 'CENTER'
    return row

def automate_panel_logic_geo():
    """Returns True if in object mode and a meshes are selected."""
    selection = bpy.context.selected_objects
    if not selection:
        return False
    else:
        for sel in selection:
            if not sel.mode == 'OBJECT':
                return False
            if not sel.type == 'MESH':
                return False
    return True

def automate_panel_logic_bones():
    """Returns True if in pose mode, and a single bone is selected."""
    pose_bones = bpy.context.selected_pose_bones
    if len(pose_bones) == 0:
        return 'None Selected',False
    if len(pose_bones) == 1:
        return pose_bones[0].name,True
    else:
        return 'Too Many Bones Selected',False

def adjust_panel_logic():
    """
    Return True if the current selection contains 
    a single wom driven mesh or pose bone.
    Needs to be a single item because only one item can be adjusted at a time. 
    """
    no_selection = 'Not Automated'
    multiple_selected = 'Multiple Selected'
    no_wom_data = 'Not Automated'

    if bpy.context.mode == 'POSE':
        active_obj = bpy.context.active_pose_bone
        selected = bpy.context.selected_pose_bones

    if bpy.context.mode == 'OBJECT':
        selected = bpy.context.selected_objects
        active_obj = bpy.context.object

    count = len(selected)
    if count == 0:
        return False, no_selection
    elif count > 1:
        return False, multiple_selected
    elif count == 1:
        for sel in selected:
            if sel == active_obj:
                wom_driven = active_obj.wom.get(ws.wom_driven)
                if wom_driven:
                    return True, sel.name
        return False, no_wom_data

    else:
        return False, no_selection


def utilities_panel_logic():
    """Returns true if the current selection contains any wom driven meshes or pose bones."""
    selected = bpy.context.selected_objects
    if selected:
        for sel in selected:
            wom_driven = sel.wom.get(ws.wom_driven)
            if wom_driven:
                return True
            if sel.type == 'ARMATURE':
                pose_bones = bpy.context.selected_pose_bones
                if pose_bones:
                    for bone in pose_bones:
                        wom_driven = bone.wom.get(ws.wom_driven)
                        if wom_driven:
                            return True
    return False



classes = [VIEW3D_PT_wheel_o_matic,VIEW3D_PT_wheel_o_matic_adjust,VIEW3D_PT_wheel_o_matic_utilities]