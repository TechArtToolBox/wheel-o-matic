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
    



# Main hook for the UI
class VIEW3D_PT_wheel_o_matic(bpy.types.Panel):

    bl_region_type = 'UI'
    bl_space_type = 'VIEW_3D'
    bl_label = 'Wheel-O-Matic'
    bl_idname = 'VIEW3D_PT_wheel_o_matic'
    bl_category = 'Wheel-O-Matic'
    
    def draw(self, context):
        layout = self.layout
        w_ui = bpy.context.scene.wheel_o_matic
        
        selected = bpy.context.selected_objects

        #if nothing is selected
        if len(selected)< 1:
            col = self.layout.column()
            col.label(text ='select wheel(s) or wheel driver(s)')
        
        else:
            # get info from selection
            wheel_locator_counter = 0
            for obj in selected:
                if obj.get('scripted_rotation') is not None:
                    wheel_locator_counter +=1

            # if one locator and one item to drive is selected
            if len(selected) == 2 and wheel_locator_counter == 1:
                col = self.layout.column()
                col.label(text='Drive Rotation On The:')
                row = self.layout.row()
                row.operator('object.drive_x_rotation', text='X Axis') 
                row.operator('object.drive_y_rotation', text='Y Axis')
                row.operator('object.drive_z_rotation', text='Z Axis')

            else:
                # only locators are selected
                if len(selected) == wheel_locator_counter:
                    sel0 = selected[0]
                    col = self.layout.column()
                    col = col.column()
                    col.prop(sel0,'["radius"]',text='Wheel Radius')
                    col.prop(sel0,'["auto_rot_power"]',text='Auto Rotate Power')
                    col.prop(sel0,'["manual_rotation"]',text='Manual Rotation')
                    col.separator()
                    col.prop(w_ui, 'b_invert_rotation')
                    col.operator('object.zero_scripted_rotation', text='Clear Auto Rotation')
                    col.separator()
                    col.separator()
                    col = self.layout.column()
                    col.enabled = False
                    col.prop(sel0,'["scripted_rotation"]',text='Total Rotation')

                # handle all other selection
                else:
                    col = self.layout.column()
                    col.label(text = 'For The Selected Wheel(s)')
                    row = col.row()
                    row.operator('object.empty_add_wheel_locator', text='Create Wheel Locator')
                    if wheel_locator_counter > 0:
                        row.enabled = False 


classes = [Wheel_UI_Properties,VIEW3D_PT_wheel_o_matic]