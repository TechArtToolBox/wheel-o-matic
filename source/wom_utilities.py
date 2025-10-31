import bpy
import mathutils
from . import wom_strings as ws



def wom_wheel_logic(self=None,parent_matrix=None):
    """
    This is the main logic for all Wheel-O-Matic wheels.
    It is loaded into the driver namespace, and then referenced
    by each wheel's driver to generate rotation information.
    """
    if not self:
        return 0
    
    if self.id_data.type == 'ARMATURE':
        obj = bpy.data.objects[self.id_data.name].pose.bones[self.name]
        armature = obj.id_data
        armature_matrix = armature.matrix_world
        if obj.parent:
            p_mtx = armature_matrix @ parent_matrix
        else:
            p_mtx = armature_matrix
    else:
        obj = bpy.data.objects[self.id_data.name]
        p_mtx = parent_matrix

    previous_pos =  mathutils.Vector(obj.wom.position_old)
    radius = obj.wom_radius
    r_mtx = mathutils.Matrix.Translation(mathutils.Vector((0,0,-radius)))
    g_mtx = p_mtx @ obj.wom.wom_axis_offset @ r_mtx
    current_pos = g_mtx.translation
    forward = mathutils.Vector((g_mtx[0][0], g_mtx[1][0], g_mtx[2][0]))
    if obj.wom.forward_axis == 'y':
        forward = mathutils.Vector((-g_mtx[0][1], -g_mtx[1][1], -g_mtx[2][1]))
    forward_mag = forward.magnitude
    forward = forward.normalized()
    change = mathutils.Vector(current_pos - previous_pos)
    traveled = (change.magnitude)
    change_direction = change.normalized()
    dot_scalar = change_direction.dot(forward)
    distance = (traveled*dot_scalar*obj.wom_auto_rotation_power)
    radians = distance/(radius*forward_mag) + obj.wom.rotation_old
    obj.wom.position_old = current_pos
    obj.wom.rotation_old = radians

    return radians



#### Automation Utilities

def mesh_wheel_bulk_setup():
    """
    Main hook for setting up mesh wheels. This parses
    all selected objects, finds valid meshes, then passes each valid mesh 
    to be automated via mesh_wheel_setup()"""

    wheels = []
    sel = bpy.context.selected_objects
    for asset in sel:
        if asset.type == 'MESH':
            wheels.append(asset)

    if len(wheels) == 0:
        return False
    
    wom_ui = bpy.context.scene.wom_ui
    forward_axis = wom_ui.world_forward_axis
    
    total_success = True
    for wheel in wheels:
        single_success = mesh_wheel_setup(wheel,forward_axis)
        if single_success == False:
            total_success = False

    # set forward axis back to auto just in case
    wom_ui.world_forward_axis = 'auto'

    # return results
    return total_success

   
def mesh_wheel_setup(wheel,forward_axis):
    """Automate rotation of a mesh wheel"""

    # remove any existing wom control
    remove_wom_control(wheel)

    # set unique wom id
    wom_id = set_wom_id(wheel)

    # get wheel geo information
    wheel_geo_info = WheelGeoInfo(wheel,forward_axis)

    # if no parent, see if there's a child of constraint
    wheel_parent = wheel.parent
    if not wheel_parent:
        wheel_constraints = wheel.constraints
        for constraint in wheel_constraints:
            if constraint.type == 'CHILD_OF':
                wheel_parent = constraint.target
                wheel_geo_info.parent = wheel_parent
                wheel_geo_info.child_of_const = True
                break

    # otherwise auto create a parent and connect it all to that
    auto_parent = None
    if not wheel_parent:
        auto_parent = create_auto_parent_geo(wheel_geo_info,wom_id)
        wheel_geo_info.parent = auto_parent

    # setup wheel logic
    drive_wheel(wheel,wheel_geo_info)

    # create rotation helper
    rotator = create_custom_empty(wheel.name,wom_id,ws.type_rotator,draw=False,hide=False)
    rotator.parent = wheel_geo_info.parent

    # drive rotation helper
    drive_wom_rotator(wheel,rotator,wheel_geo_info.rotation_axis)

    # make the final connection between wheel geo and rotation helper
    constraint = constraint_final_rotation(wheel,rotator,wheel_geo_info.rotation_axis)
    if wheel_geo_info.invert_rotation:
        setattr(constraint,f'invert_{wheel_geo_info.rotation_axis}', True)

    # make the wheel a child of the auto parent if it was created
    if auto_parent:
        parent_default(wheel,auto_parent)
        # put the auto parent and rotator in the same collection(s) as the wheel
        collection_match(wheel,[auto_parent,rotator])
    else:
        # put the rotator in the same collection(s) as the wheel
        collection_match(wheel_geo_info.parent,[rotator])

    # deselect
    wheel.select_set(False)

    # Add the wheel to the wom objects in scene for locator drawing
    wom_reference = bpy.context.scene.wom.wom_reference_collection.add()
    wom_reference.wom_object = wheel

    return True


def bone_setup():
    """
    Automate rotation of a pose bone. Bone argument is the
    active pose bone, reference wheel mesh is pulled from
    the UI via bpy.context.scene.wom_ui.p_wheel_obj
     """


    # get wheel info
    wom_ui = bpy.context.scene.wom_ui
    wheel = wom_ui.p_wheel_obj
    forward_axis = wom_ui.world_forward_axis
    if not wheel:
        return False
    else:
        wheel_info = WheelGeoInfo(wheel,forward_axis)

    # get selected pose bone
    selected_bone = bpy.context.active_pose_bone

    # get armature
    armature = None
    selected = bpy.context.selected_objects
    for sel in selected:
        if sel.type == 'ARMATURE':
            armature = sel
    
    if not armature or not selected_bone:
        return False
    
    # remove any old automation data
    if selected_bone.wom.get(ws.wom_id):
        remove_wom_control(selected_bone)

    # get local rotation and invert rotation info
    local_rotation_axis, invert_rotation = get_local_rotation_axis_bone(wheel_info,selected_bone,armature)
    
    
    # get world matrix of bone
    bone_matrix_world = selected_bone.id_data.matrix_world @ selected_bone.matrix

    # setup wom_id data
    wom_id = set_wom_id(selected_bone)

    # connect bone automation
    drive_wheel(selected_bone,wheel_info)

    # create rotation helper, make child of armature
    rotator = create_custom_empty(selected_bone.name,wom_id,ws.type_rotator,draw=False,hide=False)
    rotator.parent = armature

    # drive rotation helper
    drive_wom_rotator(selected_bone,rotator,local_rotation_axis,armature)

    # make final connection between rotation helper and pose bone
    constraint = constraint_final_rotation(selected_bone,rotator,local_rotation_axis)
    if invert_rotation:
        setattr(constraint,f'invert_{local_rotation_axis}', True)

    # clean up UI
    wom_ui['p_wheel_obj'] = None
    wom_ui.world_forward_axis = 'auto'

    # match collections
    collection_match(armature,rotator)

    # mark the armature as wom driven
    armature.wom[ws.wom_driven_armature] = True
    armature.wom[ws.wom_id] = wom_id

    # update the locators collection
    wom_reference = bpy.context.scene.wom.wom_reference_collection.add()
    wom_reference.wom_object = armature
    return True


def drive_wheel(target,wheel_geo_info):
    """ Create rotation driver for a wheel (handles both meshes and bones)"""

    # define the wom axis offset for the ground follower
    id_data = target.id_data
    wheel = wheel_geo_info.wheel_object

    is_bone = False
    # for bones
    if id_data.type =='ARMATURE':
        is_bone = True
        bone = target
        armature = bone.id_data
        wheel_geo_info.parent = armature

        # see if the wheel is skinned, and account for any animation
        is_skinned = False
        for modifier in wheel.modifiers:
            if modifier.type == 'ARMATURE':
                if modifier.object == armature:
                    is_skinned = True

        # if the wheel geo is skinned, it might be mid animation and deformed from its origin. account for that
        if is_skinned:
            wheel_matrix = get_armature_deformed_wheel_global_matrix(wheel,bone,armature)
            location_only_matrix = mathutils.Matrix.Translation(wheel_matrix.translation)

        # otherwise it's probably just parented to the bone, so use its world position
        else:
            location_only_matrix = mathutils.Matrix.Translation(wheel.matrix_world.translation)
            
        # now that we have the position under the wheel geo, setup the offset relative to the parent bone. Use the armature if no parent.
        parent_bone = bone.parent
        if parent_bone:
            parent_matrix_world = get_bone_matrix_world(parent_bone)
            offset = parent_matrix_world.inverted() @ location_only_matrix
        else:
            offset = armature.matrix_world.inverted() @ location_only_matrix


    # for meshes
    else:
        location_only_matrix = mathutils.Matrix.Translation(target.matrix_world.translation)

        # has existing direct parent
        if target.parent:
            offset = target.parent.matrix_world.inverted() @ location_only_matrix
        # no existing direct parent
        
        else:
            # is child of constrained
            if wheel_geo_info.child_of_const == True:
                offset = wheel_geo_info.parent.matrix_world.inverted() @ location_only_matrix

            # No parent, we're creating one. Do it manually though cuz the parent transform isn't accurate on creation
            else:
                fake_parent_matrix = location_only_matrix @ mathutils.Matrix.Translation(mathutils.Vector((0,0,-wheel_geo_info.radius)))
                offset = fake_parent_matrix.inverted() @ location_only_matrix

    # set wom axis offset for either
    offset_flat = matrix_flat(offset)
    target.wom[ws.wom_axis_offset] = offset_flat

    # define parent for either type
    wheel.wom.wom_defined_parent = wheel_geo_info.parent

    ## create driver 
    t=target
    w=wheel_geo_info
    fcurve = t.driver_add(ws.wom_auto_rotation)
    driver = fcurve.driver
    driver.use_self = True
    var = driver.variables.new()
    var.type = 'SINGLE_PROP'
    var.name = 'wom_parent_matrix'
    targets = var.targets
    if is_bone:
        armature = t.id_data
        # bone that has a parent bone
        if t.parent:
            targets[0].id = armature
            targets[0].data_path = f'pose.bones["{t.parent.name}"].matrix'
            driver.expression = 'wom_wheel_logic(self,wom_parent_matrix)'
        
        else:
            targets[0].id = armature
            targets[0].data_path = f'matrix_world'
            driver.expression = 'wom_wheel_logic(self,wom_parent_matrix)'
    else:
        targets[0].id = w.parent
        targets[0].data_path = 'matrix_world'
        driver.expression = 'wom_wheel_logic(self,wom_parent_matrix)'
    

    # update scene 
    bpy.context.view_layer.update()

    # set initial rotation to zero
    t[ws.wom_auto_rotation] = 0.0
    t.wom[ws.wom_rotation_old] = 0.0

    # Set property defaults
    setattr(t.wom,ws.wom_forward_axis,w.forward)
    setattr(t,ws.wom_radius,w.radius)
    setattr(t,ws.wom_rotation_power,1.0)



#### Connection Utilities

def constraint_final_rotation(item,driver,rotation_axis):  
    """Create rotation constraint that drives a wheel mesh or wheel bone"""

    constraint_name = 'Wheel-O-Matic Rotation Constraint'
    if type(rotation_axis) == int:
        axis_dict = {0:'x',1:'y',2:'z'}   
        rotation_axis = axis_dict[rotation_axis]

    constraint = item.constraints.new("COPY_ROTATION")
    constraint.name = constraint_name
    constraint.target = driver
    constraint.mix_mode = 'AFTER'
    ignore_axes = ['x','y','z']
    ignore_axes.remove(rotation_axis)
    for axis in ignore_axes: setattr(constraint, f'use_{axis}', False) 
    constraint.target_space = 'LOCAL'
    constraint.owner_space = 'LOCAL'

    return constraint


def drive_wom_rotator(source_obj,target_obj,axis,armature=None):
    """Create driver to drive the wom rotator from data generated by the global wheel logic. 
    This wom rotator's delta rotation is referenced by the rotation constraint on an automated wheel."""
    
    if type(axis) == str:
        axis_dict = {'x':0,'y':1,'z':2}
        axis = axis_dict[axis]

    # create driver
    fcurve = target_obj.driver_add('delta_rotation_euler', axis)
    driver = fcurve.driver
    driver.expression = 'wom_auto_rotation'
    var = driver.variables.new()
    var.type = 'SINGLE_PROP'
    var.name = 'wom_auto_rotation'
    targets = var.targets
    targets[0].transform_space = 'WORLD_SPACE'

    if armature:
        targets[0].id = armature
        targets[0].data_path = f'pose.bones["{source_obj.name}"].{ws.wom_auto_rotation}'
    else:
        targets[0].id = source_obj
        targets[0].data_path = f'{ws.wom_auto_rotation}'
        # targets[0].data_path = ws.wom_auto_rotation



#### Wheel Mesh Utilities

def get_world_rotation_axis(dimensions_ws,wheel_object,ignore_z = True):
    """Find the world rotation axis of a mesh based on it's local axes and its orientation in world space"""

    # the two similar length world bounds are the non rotation axes (think wheel length and height) We want the outlier (wheel width)
    dims = dimensions_ws
    yz = abs(dims[1] - dims[2])
    xz = abs(dims[0] - dims[2])
    xy = abs(dims[0] - dims[1])
    # outlier axis will be the one with the lowest number. This is the global rotation axis
    values_lookup = [yz,xz,xy]
    if ignore_z:
        values_lookup.pop()
    outlier = values_lookup.index(min(values_lookup))

    # handle default cylinder edge case. it's 1 unit in all directions, so need to figure out axis from mesh
    x_y_difference = abs(dimensions_ws[0] - dimensions_ws[1])
    
    if x_y_difference < 0.000001:
        x = mathutils.Vector((1.0,0.0,0.0))
        y = mathutils.Vector((0.0,1.0,0.0))

        more_than_4_verts = []
        polys = wheel_object.data.polygons
        matrix_ws = wheel_object.matrix_world
        matrix_ws_rot = matrix_ws.to_3x3().normalized()
        for poly in polys:
            vertices = poly.vertices
            if len(vertices) > 4:
                more_than_4_verts.append(poly)

        if len(more_than_4_verts) == 2:
            # probably the default cylinder cuz 2 faces with extra verts (cylinder caps), dot x on one of those polys to find rotation axis
            poly_normal_ws = matrix_ws_rot @ more_than_4_verts[0].normal
            dot_x = abs(x.dot(poly_normal_ws))
            if dot_x >0.5:
                outlier = 0
            else:
                outlier = 1

    return outlier


def get_dimensions_from_bounds(bounds):
    """Return simple XYZ values from the bounds of a mesh."""
    x_vals = []
    y_vals = []
    z_vals = []
    for bound in bounds:
        x_vals.append(bound[0])
        y_vals.append(bound[1])
        z_vals.append(bound[2])
    x_width = max(x_vals) - min(x_vals)
    y_width = max(y_vals) - min(y_vals)
    z_width = max(z_vals) - min(z_vals)
    dimensions = [x_width,y_width,z_width]

    return dimensions


def get_local_rotation_axis_mesh(matrix_world,global_rotation_axis):
    
    """
        Compare global rotation axis against the axis vectors of the object's matrix to find
        the local rotation axis. The one with the highest absolute value of the dot product is the matching axis. 
        If the dot product is negative, the rotation constraint needs to be inverted. 
    """

    if global_rotation_axis == 0:
        world_rotation_vector = mathutils.Vector((1.0,0.0,0.0))
    else:
        world_rotation_vector = mathutils.Vector((0.0,1.0,0.0))

    # get the normalized world orientation matrix of the object
    # also transpose the matrix because it's column based
    mtx_world_orientation_normalized = matrix_world.to_3x3().normalized().transposed()

    # use that and the world rotation vector to find out what axis to spin the wheel on
    local_rotation_axis, invert_rotation = __local_axis_and_inversion(mtx_world_orientation_normalized,world_rotation_vector)

    return local_rotation_axis, invert_rotation


def get_wheel_bottom(obj,bone = None):
    """ 
    Run through all vertices in a mesh to find the lowest point in the Z axis.
    This is done on a copy of the mesh from the depsgraph to account
    for any modifiers that may be changing the shape of the mesh.
    """

    # get evaluated mesh
    depsgraph = bpy.context.evaluated_depsgraph_get()
    object_eval = obj.evaluated_get(depsgraph)
    mesh_from_eval = object_eval.to_mesh()


    # see if the wheel is bound to an armature
    is_skinned = False
    for modifier in obj.modifiers:
        if modifier.type == 'ARMATURE':
                is_skinned = True
                break

    if is_skinned:
        # TODO Edge case fix for 1.0.1: if a mesh is skinned, using the evaluated mesh can 
        # sometimes cause an incorrect ground contact offset if any parent pose bone up the chain
        # has translation in the Z axis. Doing it this way, ground contact only has a 
        #  chance of being wrong if the mesh has modifiers that change
        # mesh shape. Easily solved by the user by adjusting wheel radius for now. 
        world_verts = [obj.matrix_world @ vertex.co for vertex in obj.data.vertices]
        all_z = []
        for v in world_verts:
            all_z.append(v[2])
            # wheel_matrix = get_armature_deformed_wheel_global_matrix(obj,bone,armature)
            # location_only_matrix = mathutils.Matrix.Translation(wheel_matrix.translation)

    else:
    # collect all vertices in world space
        world_verts = [obj.matrix_world @ vertex.co for vertex in mesh_from_eval.vertices]
        all_z = []
        for v in world_verts:
            all_z.append(v[2])

    # clear the temp mesh
    object_eval.to_mesh_clear()

    # return the result of the lowest vertex
    return (min(all_z))



#### Wheel Pose Bone Utilities

def get_armature_deformed_wheel_global_matrix(wheel,bone,armature):
    """ Returns the matrix of the object origin for a mesh that has been transformed by an armature and its bones"""
    wheel_mw = wheel.matrix_world
    bone_mw = bone.id_data.matrix_world @ bone.matrix
    bone_ml = bone.id_data.matrix_world @ armature.data.bones[bone.name].matrix_local
    matrix = bone_mw @ bone_ml.inverted() @ wheel_mw
    
    return matrix


def get_bone_matrix_world(bone):
    """Returns world matrix of a bone, accounting for any armature transformation."""

    # (id_data on a bone is a reference to the armature)
    return bone.id_data.matrix_world @ bone.matrix


def get_local_rotation_axis_bone(wheel_info,bone,armature):

    """
        compare global rotation axis against the world axis vectors of the bone to find
        the local rotation axis (armature orientation is also taken into account)
        The one with the highest absolute value of the dot product is the matching axis. 
        If the dot product is negative, the rotation constraint needs to be inverted. 

    """
    local_rotation_axis = None
    invert_rotation = False
    if wheel_info.global_rotation_axis == 0:
        world_rotation_vector = mathutils.Vector((1.0,0.0,0.0))
    else:
        world_rotation_vector = mathutils.Vector((0.0,1.0,0.0))

    # get armature relative world axes
    x = bone.x_axis
    y = bone.y_axis
    z = bone.z_axis
    axis_vectors = [x,y,z]

    # get the normalized world orientation of the armature
    mtx_world_orientation_normalized = armature.matrix_world.to_3x3().normalized()

    # multiply the axis vectors by the armature's normalized world rotation to get what directions they point in world space
    axis_vectors_ws = [mtx_world_orientation_normalized @ mathutils.Vector(axis) for axis in axis_vectors]
    local_rotation_axis, invert_rotation = __local_axis_and_inversion(axis_vectors_ws,world_rotation_vector)

    return local_rotation_axis, invert_rotation


def __local_axis_and_inversion(axis_vectors,world_rotation_vector):
    """ 
    Get the object rotation axis of a wheel (mesh or bone),
    as well as if rotation needs to be inverted for the rotation constraint. 
    Inversion is needed if the local rotation vector
    and world rotation vetor are opposite vectors.
    """
    invert_rotation = False
    local_rotation_axis = None
    dot_results = []
    abs_dot_results = []
    for vector in axis_vectors:
        dot = vector.dot(world_rotation_vector)
        dot_results.append(dot)
        abs_dot_results.append(abs(dot))

    axis_index = abs_dot_results.index(max(abs_dot_results))
    actual_value = dot_results[axis_index]
    lookup_dict = {0:'x',1:'y',2:'z'}
    local_rotation_axis = lookup_dict[axis_index]
    if actual_value < 0:
        invert_rotation = True

    return local_rotation_axis, invert_rotation



#### Utilities for all

def get_wom_id(item):
    """
    GET wom id. Wom id is a unique identifier string applied to 
    all assets related to the automation of a single wheel (mesh or bone).
    """
    if item:
        if item.type == 'MESH':
            sel_id =  item.wom.get(ws.wom_id)
            if sel_id:
                return sel_id

        elif item.type == 'ARMATURE':
            bone = bpy.context.active_pose_bone
            if bone:
                bone_id =  bone.wom.get(ws.wom_id)
                if bone_id:
                    return bone_id

        else:
            return None


def set_wom_id(obj):
    """
    SET wom id. Wom id is a unique identifier string that is generated and applied to
    all assets related to the automation of this wheel (mesh or bone).
    """
    obj_name = obj.name
    obj_id = id(obj)
    wom_id = f'wom_{obj_id}_{obj_name}'

    setattr(obj.wom,ws.wom_id,wom_id)
    setattr(obj.wom,ws.wom_driven,True)
    obj.wom[ws.wom_type] = ws.type_target
    return wom_id


def get_scene_wom_objects():
    """
    Get all things in the scene that are related to wheel automation
    """
    scene_wom_objects = []
    all_objects = bpy.context.scene.objects
    for obj in all_objects:
        if obj.type == 'MESH' or obj.type == 'CURVE':
            if obj.wom:
                wom_id = obj.wom.get(ws.wom_id)
                if wom_id:
                    scene_wom_objects.append(obj)

        if obj.type == 'ARMATURE':
            bones = obj.pose.bones
            for bone in bones:
                if bone.wom:
                    wom_id = bone.wom.get(ws.wom_id)
                    if wom_id:
                        scene_wom_objects.append(bone)

    return list(set(scene_wom_objects))


def get_scene_wom_targets():
    """
    Get all things in the scene that are direct tartgets of wom automation.
    These are the bones or meshes that have been automated.
    """
    targets = {}
    scene_wom_objects = get_scene_wom_objects()
    for item in scene_wom_objects:
        wom_type = item.wom.get(ws.wom_type)
        if wom_type:
            if wom_type == ws.type_target:
                wom_id = item.wom[ws.wom_id]
                targets[wom_id] = item

    return targets


def get_wom_driven_meshes():
    """Get the MESHES in the scene that are automated."""
    wom_meshes = []
    all_objects = bpy.context.scene.objects
    for obj in all_objects:
        if obj.type == 'MESH':
            if obj.wom:
                wom_driven =  obj.wom.get(ws.wom_driven)
                if wom_driven == True:
                    wom_meshes.append(obj)
    return wom_meshes


def get_wom_driven_armatures():
    """ Get the ARMATURES in the scene that are wom automated."""

    wom_armatures = []
    all_objects = bpy.context.scene.objects
    for obj in all_objects:
        if obj.type == 'ARMATURE':
            armature = obj
            wom_bones = get_wom_driven_bones_from_armature(armature)
            if wom_bones:
                wom_armatures.append(armature)
    return wom_armatures


def get_wom_driven_bones_from_armature(armature):
    """Get the BONES in a given armature that are wom automated."""
    wom_driven_bones = []
    bones = armature.pose.bones
    for bone in bones:
        if bone.wom:
            wom_driven = bone.wom.get(ws.wom_driven)
            if wom_driven:
                wom_driven_bones.append(bone)
    return wom_driven_bones


def remove_stray_wom_data_from_scene():
    """ Remove any wom data that is no longer driving a wheel or bone.
        This can occur when a user deletes a mesh or bone that is automated.
        The stray data is usually orphaned rotation helpers 
        or auto parent controls, but can also be invalid drivers.
        Invalid drivers happen on armatures if a driven bone is deleted 
        becasue the now missing bone's driver is still stored on the armature.
    """
    all_scene_wom_objects = get_scene_wom_objects()
    wom_bundles_by_id = {}
    for obj in all_scene_wom_objects:
        wom_id = obj.wom[ws.wom_id]
        if wom_id:
            if not wom_id in wom_bundles_by_id:
                wom_bundle = WomBundle(wom_id)
                wom_bundles_by_id[wom_id] = wom_bundle
            wom_bundle = wom_bundles_by_id[wom_id]
            # if this is the target object
            wom_type = obj.wom.get(ws.wom_type)
            if wom_type == ws.type_target:
                    wom_bundle.target = obj
            else:
                wom_bundle.other_data.append(obj)

    for wom_id in wom_bundles_by_id:
        bundle = wom_bundles_by_id[wom_id]
        if bundle.target == None:
            # remove the items from the scene
            for item in bundle.other_data:
                bpy.data.objects.remove(item, do_unlink=True)

    # clean up any stray auto rotation drivers on any armatures
    all_objects = bpy.context.scene.objects
    for item in all_objects:
        if item.type == 'ARMATURE':
            armature = item
            anim_data = armature.animation_data
            if anim_data:
                drivers = armature.animation_data.drivers
                if drivers:
                    for driver in drivers: 
                        if 'wheel_logic' in driver.driver.expression:
                            data_path = driver.data_path
                            driven_bone_name = data_path.split('"')[1]
                            if not driven_bone_name in armature.pose.bones:
                                # bone target no longer exists, delete the driver
                                armature.driver_remove(driver.data_path, -1)


def refresh_wheel_logic():
    """
    If the addon/extention is uninstalled while a file is open that
    has automated wheels, Blender will mark the expressions on the
    drivers for the wheels as invalid, breaking the automation. If the addon
    is then re-installed, the driver expressions will remain invalid and broken. 
    This brings them back to life. 
    """
    # Re-Register global logic
    register_wom_wheel_logic()

    # Re-apply reference to global logic (forces blender to re-evaluate if the expression is valid)
    wom_armatures = get_wom_driven_armatures()
    wom_meshes = get_wom_driven_meshes()

    wom_driven_items = wom_armatures + wom_meshes
    for item in wom_driven_items:
        drivers = item.animation_data.drivers
        for driver in drivers: 
            if 'wom_wheel_logic' in driver.driver.expression:
                driver.driver.expression = 'wom_wheel_logic(self,wom_parent_matrix)'


def matrix_flat(matrix):
    """Convert a matrix into a flat list of values."""
    dimension = len(matrix)
    return [matrix[j][i] for i in range(dimension) 
                    for j in range(dimension)]


def collection_match(target,wom_items):
    """ Move items to the same collection(s) of the target"""
    if not type(wom_items) == list:
        wom_items = [wom_items]
    
    # clear collections for wom items
    for wom_item in wom_items:
        #unlink current collections
        for col in list(wom_item.users_collection):
            col.objects.unlink(wom_item)
        
        # match each target collection
        for collection in target.users_collection:
            collection.objects.link(wom_item)


def clear_rotation():
    """
    Reset automated rotation back to zero for 
    any wom object in the current selection.
    """
    for item in bpy.context.selected_objects:
        if item.type == 'MESH':
            if item.get(ws.wom_auto_rotation):
                setattr(item,ws.wom_auto_rotation,0.0)
            if item.wom.get(ws.wom_rotation_old):
                setattr(item.wom,ws.wom_rotation_old,0.0)

        elif item.type == 'ARMATURE':
            bone = bpy.context.active_pose_bone
            if bone:
                if bone.get(ws.wom_auto_rotation):
                    setattr(bone,ws.wom_auto_rotation,0.0)
                if bone.wom.get(ws.wom_rotation_old):
                    setattr(bone.wom,ws.wom_rotation_old,0.0)

        # force update the driver expression so that it 
        # re-runs the logic to match zero rotation, thus redrawing the 3d view
        anim_data = item.animation_data
        if anim_data:
            drivers = item.animation_data.drivers
            if drivers:
                for driver in drivers: 
                    if 'wom_wheel_logic' in driver.driver.expression:
                        driver.driver.expression = 'wom_wheel_logic(self,wom_parent_matrix)'




def remove_automation_bulk():
    """
    Parse all selected items, and for anything 
    that is wom driven remove it's automation
    and any helpers that go along with it.
    """
    selection = bpy.context.selected_objects
    objects_to_clean = []
    for sel in selection:
        if sel.type == 'ARMATURE':
            bones = bpy.context.selected_pose_bones
            if bones:
                for b in bones:
                    objects_to_clean.append(b)

        elif sel.type == 'MESH':
            objects_to_clean.append(sel)

    for obj in objects_to_clean:
        if obj.wom.get(ws.wom_id):
            remove_wom_control(obj) 


def remove_wom_control(wheel_obj):
    """Remove wom automation of a mesh or bone"""
    all_scene_wom_objects = get_scene_wom_objects()
    wheel_obj_id = wheel_obj.wom.get(ws.wom_id)

    # Delete wheel o matic constraints
    remove_consts = []
    constraints = wheel_obj.constraints
    if constraints:
        for const in constraints:
            if hasattr(const,'target'):
                target = const.target
                if target:
                    if target.wom:
                        if target.wom.get(ws.wom_id):
                            remove_consts.append(const)
                elif 'Wheel-O-Matic' in const.name:
                    remove_consts.append(const)
    for const in remove_consts:
        wheel_obj.constraints.remove(const)

    # Get wom id
    id_data = wheel_obj.id_data

    # Remove driver for armature
    armature = None
    if id_data.type == 'ARMATURE':
        armature = id_data
        drivers = armature.animation_data.drivers
        for driver in drivers: 
            if 'wom_wheel_logic' in driver.driver.expression:
                data_path = driver.data_path
                driven_bone_name = data_path.split('"')[1]
                if wheel_obj.name == driven_bone_name:
                    armature.driver_remove(driver.data_path, -1)

    # Remove wom driver for mesh
    else:
        if wheel_obj.animation_data:
            drivers = wheel_obj.animation_data.drivers
            for driver in drivers: 
                if 'wom_wheel_logic' in driver.driver.expression:
                    wheel_obj.driver_remove(driver.data_path, -1)

    # Remove top level properties
    properties = [ws.wom_auto_rotation,ws.wom_radius,ws.wom_rotation_power]
    for prop in properties:
        value = wheel_obj.get(prop)
        if value is not None:
            del wheel_obj[prop] 
        
    # Clear properties in wom property group
    pg_properties = [ws.wom_id,ws.wom_driven,ws.wom_type]
    for pg_prop in pg_properties:
        pg_value = wheel_obj.wom.get(pg_prop)
        if pg_value is not None:
            del wheel_obj.wom[pg_prop] 

    # delete objects with matching wom id if it's not the object itself
    for item in all_scene_wom_objects:
        item_wom_id = item.wom.get(ws.wom_id)
        if item_wom_id == wheel_obj_id:
            if not item == wheel_obj:
                item_type = item.wom.get(ws.wom_type)
                if not item_type == ws.type_target:
                    bpy.data.objects.remove(item, do_unlink=True)

    # flag an armature as no longer wom driven if no bones are wom targets
    if armature:
        wom_driven_bones = get_wom_driven_bones_from_armature(armature)
        if not wom_driven_bones:
            armature.wom[ws.wom_driven_armature] = False


def parent_default(child,parent):
    """Non-ops version of default Blender parenting type"""
    child.parent = parent
    child.matrix_parent_inverse = parent.matrix_world.inverted()



#### Utilities for locator drawing

def scale_coords(coords):
    """
    Scale wom locators. Actual scale is pulled from the 
    UI property f_locator_scale.The coords argument is a list of 
    3d coordinates passed in from wom_render.py which handles locator drawing.
    """
    scaled_coords = []

    wom_ui = bpy.context.scene.wom_ui
    scalar = wom_ui.f_locator_scale
    for coord in coords:
        temp = []
        for axis in coord:
            scaled_axis = axis * scalar
            temp.append(scaled_axis)
        scaled_coords.append((temp[0],temp[1],temp[2]))
    return scaled_coords


def get_ground_matrix_for_wom_mesh(wom_object):
    """Return the calculated ground position and orientation of a wom driven MESH."""
    try:
        p = wom_object.wom.wom_defined_parent
        p_mtx = p.matrix_world
        o_mtx = wom_object.wom.wom_axis_offset
        r = getattr(wom_object,ws.wom_radius)
        r_mtx = mathutils.Matrix.Translation(mathutils.Vector((0,0,-r)))
        g_mtx = p_mtx @ o_mtx @ r_mtx
        return g_mtx
    except:
        return None


def get_ground_matrix_for_wom_bone(bone,armature):
    """Return the calculated ground position and orientation of a wom driven BONE."""
    parent_bone = bone.parent
    armature_mtx = armature.matrix_world
    if parent_bone:
        p_mtx = armature_mtx @ parent_bone.matrix
    else:
        p_mtx = armature_mtx
    o_mtx = bone.wom.wom_axis_offset
    r = getattr(bone,ws.wom_radius)
    r_mtx = mathutils.Matrix.Translation(mathutils.Vector((0,0,-r)))
    g_mtx = p_mtx @ o_mtx @ r_mtx
    return g_mtx


def get_transformed_3d_coords(matrix,coords):
    """Transform a list of 3d positions against a given matrix."""
    # coords should be a list of 3d coordinates: [(x1,Y1,Z1),(X2,Y2,Z2),...]
    transformed_coords = []
    for coord in coords:
        vector = mathutils.Vector(coord)
        # multiply by matrix to get transformation. Normalize to remove scale
        t_coord = matrix.normalized() @ vector
        transformed_coords.append(t_coord)
    return transformed_coords


def is_valid_reference(item):
    """
    Check to see if a memory reference to an object still exists.
    Also does a secondary check to make sure the item is part of this scene.
    """

    # inital test to see if the object even exists
    try:
        test = item.name
    except:
        return False
    
    # now do a scene check to make sure we don't draw for things that exist, but are not in this scene
    current_scene = bpy.context.scene
    item_scenes = item.users_scene
    for scene in item_scenes:
        if scene == current_scene:

            # and for visibilty toggles
            if not item.hide_viewport:
                hide = item.hide_get()
                if hide == False:
                    return True
        
    return False


def locator_draw_handler_exists():
    """ Check to see if the locator draw handler exists"""
    # Get the existing draw handler
    dns_key = ws.dns_key
    existing_class = bpy.app.driver_namespace.get(dns_key)
    if existing_class:
        return True
    else:
        return False

def locator_draw_handler_remove(operator):
    """ Remove the existing draw handler for wom locators. """
    # Get the existing draw handler
    dns_key = ws.dns_key
    existing_class = bpy.app.driver_namespace.get(dns_key)

    # Attempt to remove the draw handler with it's remove method.
    if existing_class:
        try:
            existing_class.remove_handler()
        except:
            pass

        # Completely remove the reference. 
        # If unable, inform the user they may need to restart Blender to remove the locators
        try:
            del bpy.app.driver_namespace[dns_key]
        except:
            operator.report({'WARNING'}, ws.locator_remove_warn)



#### Generators

def create_custom_empty(name,wom_id,suffix,draw=False,hide=False):
    """
        Create an empty curve object that is used 
        as the object for the rotation helper of a wheel.
        Acts like an empty that doesn't draw in the 3d view.
    """

    points = []
    if draw:
        points = [ (1,0,0),(-1,0,0),(0,0,0),(0,1,0),(0,-1,0),(0,0,0),(0,0,1),(0,0,-1)]


    # Create curve data
    curve_data = bpy.data.curves.new('curve', type='CURVE')
    curve_data.dimensions = '3D'

    # Create spline 
    polyline = curve_data.splines.new('POLY')

    # Add points to the spline ( if draw arg is False, the object will not be visible)
    polyline.points.add(len(points) - 1)
    for i, point in enumerate(points):
        polyline.points[i].co = (point[0], (point[1]), point[2], 1)


    # Create the curve from all the data
    curve_obj = bpy.data.objects.new('curve_obj', curve_data)
    bpy.context.collection.objects.link(curve_obj)
    custom_empty = curve_obj

    # assign name and wom_id
    custom_empty.name = name + '.' + suffix
    custom_empty.wom[ws.wom_id] = wom_id

    # locking
    if hide:
        custom_empty.hide_select = True
        custom_empty.hide_viewport = True
        custom_empty.hide_set(True)

    return custom_empty


def create_auto_parent_geo(wheel_info,wom_id):
    """Create an auto parent controller for a mesh wheel that has no parent."""
    w = wheel_info
    aol = arrow_outer_length = 1.3 * (w.length/2)
    aow = arrow_outer_width = 1.1 * (w.width)
    aiw = arrow_inner_width = 0.7 * (w.width)
    ail = arrow_inner_length = 0.4 * (w.length/2)

    points = [
                (aol,0,0),(ail,-aow,0),(ail,-aiw,0),(-ail,-aiw,0),(-ail,-aow,0),(-aol,0,0),
                (-ail,aow,0),(-ail,aiw,0),(ail,aiw,0),(ail,aow,0),(aol,0,0)
            ]

    # Create curve data
    curve_data = bpy.data.curves.new('curve', type='CURVE')
    curve_data.dimensions = '3D'

    # Create spline 
    polyline = curve_data.splines.new('POLY')

    # Add points to the spline
    polyline.points.add(len(points) - 1)
    for i, point in enumerate(points):
        if w.forward == 'x':
            polyline.points[i].co = (point[0], (point[1]), point[2], 1)
        else:
            polyline.points[i].co = (point[1], point[0], point[2], 1)

    # Create the curve from all the data
    curve_obj = bpy.data.objects.new('curve_obj', curve_data)
    bpy.context.collection.objects.link(curve_obj)
    curve_obj.location = w.location[0],w.location[1],w.location[2] - w.radius

    # set name, wom_id, and type
    curve_obj.name = f'{w.name}.{ws.type_auto_parent}'
    curve_obj.wom[ws.wom_id] =  wom_id
    curve_obj.wom[ws.wom_type] = ws.type_auto_parent

    return curve_obj


def register_wom_wheel_logic():
    """Register the global wheel logic driver expression for the current file."""
    bpy.app.driver_namespace['wom_wheel_logic'] = wom_wheel_logic



#### Helper Classes

class WheelGeoInfo():
    """This class gathers and stores all the necessary information related to a wheel"""
    def __init__(self,wheel,forward):
        self.wheel_object = wheel
        self.name = wheel.name
        self.parent = wheel.parent
        self.child_of_const = False
        self.forward = None
        self.rotation_axis = None
        self.global_rotation_axis = None
        self.invert_rotation = False
        self.width = None
        self.length = None
        self.location = None
        self.radius = None
        self.bounds_ws = None
        self.dimensions_ws = None
        self.matrix_world = None

        self.get_wheel_geo_data(wheel,forward)
        

    def get_wheel_geo_data(self,wheel,forward):
            
            # get world matrix and world space dimensions
            self.matrix_world = wheel.matrix_world
            self.location = self.matrix_world.translation
            bounds_ls = wheel.bound_box
            self.bounds_ws = [self.matrix_world @ mathutils.Vector(corner) for corner in bounds_ls]

            # get radius and world space dimensions
            self.dimensions_ws = get_dimensions_from_bounds(self.bounds_ws)
            lowest_point = get_wheel_bottom(wheel)
            self.radius = abs(lowest_point - self.location[2])

            if forward == 'auto':
                # get data about local rotation axis, global forward axis, and rotation inversion
                self.global_rotation_axis = get_world_rotation_axis(self.dimensions_ws, self.wheel_object)
                self.forward = 'x'
                if self.global_rotation_axis == 0:
                    self.forward = 'y'

            if forward == 'x':
                self.forward = 'x'
                self.global_rotation_axis = 1
            if forward == 'y':
                self.forward = 'y'
                self.global_rotation_axis = 0

            # get local rotation axis and invert info 
            self.rotation_axis, self.invert_rotation = get_local_rotation_axis_mesh(self.matrix_world,self.global_rotation_axis)

            # width/length data. Used for creating trackers and fake parent objects
            if self.forward == 'x':
                self.width = self.dimensions_ws[1]
                self.length = self.dimensions_ws[0]
            else:
                self.width = self.dimensions_ws[0]
                self.length = self.dimensions_ws[1]


class WomBundle():
    """
    Helper class to store all of the wom data related to this wom id. 
    Used for removing wom data when an automated wheel or bone
    has their automation removed.
    """
    def __init__(self,wom_id):
        self.wom_id = wom_id
        self.target = None
        self.other_data = []

