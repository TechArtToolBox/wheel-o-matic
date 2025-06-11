import bpy
import gpu
from gpu_extras.batch import batch_for_shader
import time

from . import wom_strings as ws
from . import wom_utilities as wu

#### All things related to drawing on screen

# Drawing for locators
def locators_draw_callback(self, context,shader,color,x_coords,y_coords):
    """
    Callback to draw wom locators in the 3d View. 
    The locators are positioned where the automated mesh/bone 
    thinks the ground contact of the wheel is, 
    and oriented to match roll direction.
    """
    
    # This try/except is to exit out in case of inability to find any wom properties on the scene
    try:
        wom_ui = bpy.context.scene.wom_ui
        scene_wom = bpy.context.scene.wom
    except:
        return {'FINISHED'}
    
    ## PERF CHECK START, uncomment to debug draw performance
    # start_time = time.perf_counter()

    # Scale locators according to scalar in the UI
    x_coords = wu.scale_coords(x_coords)
    y_coords = wu.scale_coords(y_coords)


    # Get wom objects stored on the scene
    wom_driven_meshes = []
    wom_driven_armatures = []
    wom_references = bpy.context.scene.wom.wom_reference_collection
    for ref in wom_references:
        obj = ref.wom_object
        is_valid = wu.is_valid_reference(obj)
        if is_valid == True:
            if obj.type == 'ARMATURE':
                wom_driven_armatures.append(obj)
            elif obj.type =='MESH':
                wom_driven_meshes.append(obj)


    # get existing draw class
    dns_key = ws.dns_key
    existing_draw_class = bpy.app.driver_namespace.get(dns_key)
    if existing_draw_class:
        ws_coords = []
        all_coords = []

        # get world space oriented locator coords for meshes
        for mesh_obj in wom_driven_meshes:
            if mesh_obj:
                g_mtx = wu.get_ground_matrix_for_wom_mesh(mesh_obj)
                if g_mtx:
                    forward_axis = mesh_obj.wom.get(ws.wom_forward_axis)
                    if forward_axis == 'y':
                        coords = y_coords
                    else:
                        coords = x_coords
                    ws_coords = wu.get_transformed_3d_coords(g_mtx,coords)
                    all_coords += ws_coords

        # get world space oriented locator coords for bones
        for armature in wom_driven_armatures:
            driven_bones = wu.get_wom_driven_bones_from_armature(armature)
            for bone in driven_bones:
                g_mtx = wu.get_ground_matrix_for_wom_bone(bone,armature)
                if g_mtx:
                    forward_axis = bone.wom.get(ws.wom_forward_axis)
                    if forward_axis == 'y':
                        coords = y_coords
                    else:
                        coords = x_coords
                    ws_coords = wu.get_transformed_3d_coords(g_mtx,coords)
                    all_coords += ws_coords
        
        # Draw
        if len(all_coords) > 0:
            batch = batch_for_shader(shader, 'LINES', {"pos": all_coords})
            shader.bind()
            shader.uniform_float("color", color)
            batch.draw(shader)

    ## PERF CHECK END, uncomment to debug draw performance (make sure to uncomment perf check start above)
    # end_time = time.perf_counter()
    # elapsed_time = end_time - start_time
    # print(f"Elapsed time: {elapsed_time:.6f} seconds")


# Operator to START drawing locators
class OBJECT_OT_wom_draw_locators(bpy.types.Operator):
    """Toggle the drawing of Wheel-O-Matic locators.
 If they aren't turning off, restart Blender to fix"""

    bl_idname = 'object.wom_draw_locators'
    bl_label = 'Wheel-O-Matic: Draw locators'

    handle = None

    wom_mesh_targets_2 = None
    dns_key = ws.dns_key
    color = (1.0, 1.0, 0.0, 1.0)

    # coordinate system for locators
    z=0.125
    a2 = secondary_axis = 0.125

    # x rolling wheel
    x_coords = [
                # main crosshairs
                (0.5, 0, 0), (-0.5, 0, 0), (0, 0, z), (0, 0, -z),(0, a2, 0), (0, -a2, 0),
                # arrowheads
                (0.5,0,0),(0.35,-0.125,0),(0.5,0,0),(0.35,0.125,0),
                (-0.5,0,0),(-0.35,-0.125,0),(-0.5,0,0),(-0.35,0.125,0)]   
    
    # y rolling wheel
    y_coords = [
                # main crosshairs
                (a2, 0, 0), (-a2, 0, 0), (0, 0, z), (0, 0, -z),(0, 0.5, 0), (0, -0.5, 0),
                # arrowheads
                (0,0.5,0),(-0.125,0.35,0),(0,0.5,0),(0.125,0.35,0),
                (0,-0.5,0),(-0.125,-0.35,0),(0,-0.5,0),(0.125,-0.35,0)]  
    shader = None
    if bpy.app.version < (3,4,0):
        shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
    else:
        shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    

    def invoke(self, context, event):
        
        # Remove any existing handler
        wu.locator_draw_handler_remove(self)


        # register wom objects on scene
        wom_driven_meshes = wu.get_wom_driven_meshes()
        wom_driven_armatures = wu.get_wom_driven_armatures()

        for mesh in wom_driven_meshes:
            wom_reference = bpy.context.scene.wom.wom_reference_collection.add()
            wom_reference.wom_object = mesh

        for armature in wom_driven_armatures:
            wom_reference = bpy.context.scene.wom.wom_reference_collection.add()
            wom_reference.wom_object = armature

        # register this version of the class in the driver_namespace
        bpy.app.driver_namespace[self.dns_key] = self

        # update UI
        wom_ui = bpy.context.scene.wom_ui
        wom_ui.b_draw_locators = True

        if context.area.type == 'VIEW_3D':
            args = (self, context,self.shader,self.color,self.x_coords, self.y_coords)
            self.handle = bpy.types.SpaceView3D.draw_handler_add(locators_draw_callback, args, 'WINDOW', 'POST_VIEW')

            context.window_manager.modal_handler_add(self)
            return {'RUNNING_MODAL'}
        else:
            self.report({'WARNING'}, ws.no_3d_view)
            return {'CANCELLED'}
        

    def modal(self, context, event):
        if context:
            if context.area:
                context.area.tag_redraw()
        return {'PASS_THROUGH'}
        

    def remove_handler(self):
        if self.handle:
            try:
                bpy.types.SpaceView3D.draw_handler_remove(self.handle, 'WINDOW')
            except:
                pass
        return {'FINISHED'}


# Operator to STOP drawing locators
class OBJECT_OT_wom_remove_locators(bpy.types.Operator):
    """Toggle the drawing of Wheel-O-Matic locators.
 If they aren't turning off, restart Blender to fix"""

    bl_idname = 'object.wom_remove_locators'
    bl_label = 'Wheel-O-Matic: Remove locators'

    def execute(self,context):

        # Remove the handler
        wu.locator_draw_handler_remove(self)

        # redraw the 3d view, as it sometimes won't update 
        for area in bpy.context.window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

        # # update UI
        wom_ui = bpy.context.scene.wom_ui
        wom_ui.b_draw_locators = False

        return {'FINISHED'}



classes = [OBJECT_OT_wom_draw_locators,OBJECT_OT_wom_remove_locators]
