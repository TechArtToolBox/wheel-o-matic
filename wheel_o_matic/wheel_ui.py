import bpy


# get/set for custom ui elements in the property group class below
def get_invert_rotation(self):
    return bpy.context.object['scripted_rotation_invert']

def set_invert_rotation(self,value):
    bpy.context.object['scripted_rotation_invert'] = value

# Property group for custom ui elements 
class Wheel_UI_Properties(bpy.types.PropertyGroup):

    desc_invert_rot = 'Invert the AUTO rotation direction that the wheel currently rotates'                    
    b_invert_rotation   :   bpy.props.BoolProperty (name = 'Invert Auto Rotation', description = desc_invert_rot,
                            get=get_invert_rotation, set=set_invert_rotation)
    

class VIEW3D_PT_wheel_o_matic_init(bpy.types.Panel):
    """panel for the initial setup of controller based on selected wheel geo"""
    bl_label = "Create Controllers"
    # bl_parent_id = "VIEW3D_PT_wheel_o_matic"
    bl_category = 'Wheel-O-Matic'
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        col = self.layout.column()
        col.label(text='For Selected Wheel(s)')
        col = self.layout.column()
        col.operator('object.empty_add_wheel_locator', text='Create Wheel Controller')
        selection = selection_check()
        if not selection == 1:
            col.active=False

class VIEW3D_PT_wheel_o_matic_connect(bpy.types.Panel):
    """panel for connecting total rotation of driver to the rotation of another object"""
    bl_label = "Connect Controller"
    # bl_parent_id = "VIEW3D_PT_wheel_o_matic"
    bl_category = 'Wheel-O-Matic'
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        col = self.layout.column()
        selection = selection_check()

        col.label(text='Select 1 Controller And 1 Object')
        row = col.row()
        row.label(text='Drive Rotation On The:')
        row2 = self.layout.row()
        row2.operator('object.drive_x_rotation', text='X Axis') 
        row2.operator('object.drive_y_rotation', text='Y Axis')
        row2.operator('object.drive_z_rotation', text='Z Axis')
        if not selection == 2:
            row.enabled = False
            row2.enabled = False


class VIEW3D_PT_wheel_o_matic_settings(bpy.types.Panel):
    """panel to show settings for a wheel-o-matic driver"""
    bl_label = "Adjust Controllers"
    # bl_parent_id = "VIEW3D_PT_wheel_o_matic"
    bl_category = 'Wheel-O-Matic'
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_options = {"DEFAULT_CLOSED"}

    def draw(self, context):
        w_ui = bpy.context.scene.wheel_o_matic
        col = self.layout.column()
        col = col.column()
        selection_type = selection_check()
        if selection_type == 3:
            selected_objs = bpy.context.selected_objects
            sel0 = selected_objs[0]
            if sel0:
                col.prop(sel0,'["radius"]',text='Wheel Radius')
                col.prop(sel0,'["auto_rot_power"]',text='Auto Rotate Power')
                col.prop(sel0,'["manual_rotation"]',text='Manual Rotation')
                col.separator()
                col.prop(w_ui, 'b_invert_rotation')
                col.operator('object.zero_scripted_rotation', text='Clear Auto Rotation')
                col.separator()
                col.separator()
                col2 = self.layout.column()
                col2.enabled = False
                col2.prop(sel0,'["scripted_rotation"]',text='Total Rotation')
        else:
            for i in range(3):
                col.label(text='')
            row = col.row()
            row.alignment = 'CENTER'
            row.label(text='  Select Controller(s) To Adjust')
            for i in range(3):
                col.label(text='')


def selection_check():
    selected = bpy.context.selected_objects
    selection_index = 0
    """selection index is: 
        0 = nothing selected, or selection invalid 
        1 = only geo is selected
        2 = one wheel and one driver selected
        3 = only drivers are selected"""

    if len(selected) < 1:
        selection_index = 0

    else:
        wheel_locator_counter = 0
        for obj in selected:
            if obj.get('scripted_rotation') is not None:
                wheel_locator_counter +=1

        if wheel_locator_counter == 0:
            selection_index = 1
        elif len(selected) == 2 and wheel_locator_counter == 1:
            selection_index = 2

        elif wheel_locator_counter == len(selected):
            selection_index = 3


    return selection_index



classes = [Wheel_UI_Properties,VIEW3D_PT_wheel_o_matic_init,
           VIEW3D_PT_wheel_o_matic_connect,VIEW3D_PT_wheel_o_matic_settings]