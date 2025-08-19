#### Global string definitions


# for the wom propertyGroup
wom_axis_offset             = 'wom_axis_offset'
wom_defined_parent          = 'wom_defined_parent'
wom_driven                  = 'wom_driven'
wom_driven_armature         = 'wom_driven_armature'
wom_forward_axis            = 'forward_axis'
wom_id                      = 'wom_id'
wom_type                    = 'wom_type'
wom_position_old            = 'position_old'
wom_rotation_old            = 'rotation_old'


# for regular properties
wom_auto_rotation           = 'wom_auto_rotation'
wom_id_ui                   = 'wom_id_ui'
wom_radius                  = 'wom_radius' 
wom_rotation_power          = 'wom_auto_rotation_power' 


#### types of wom objects
type_auto_parent            = 'wom_auto_parent'
type_rotator                = 'wom_rotator'
type_target                 = 'target'


### driver_namespace key
dns_key                     = 'wom_locators'


#### UI hint strings
desc_auto_rot           =   'DO NOT EDIT! Doing so will break the wheel logic'
desc_auto_rot_power     =   'Strength of the auto rotation. 1 is default. 0 is no rotation. Negative values reverse rotation. Type in values to go beyond the limits'
desc_locator_scale      =   'Global scale for all of the wheel locators'
desc_override_defaults  =   'Override the default settings for automation'
desc_radius             =   'Radius of the wheel, adjust as needed. Use \'Toggle Locators\' in the Utilities section to visualize'
desc_show_tracker       =   'Show the wheel tracker. Usefull for visualizing radius and debuging wheels that act strange'
desc_wheel_obj          =   'Geo of the wheel. Select the outermost geo (like the tire) if wheel is in multiple pieces'


#### UI names/text
name_auto_rot_power     =   'Rotation Power'
name_auto_rotation      =   'Auto Rotation'
name_radius             =   'Radius'
name_show_tracker       =   'Show Tracker'
name_loc_scale_global   =   'Scale All Locators'

text_clear_rotation     =   'Clear Auto Rotation'
text_refresh_logic      =   'Refresh Wheel Logic'
text_remove_automation  =   'Remove Automation'
text_remove_stray       =   'Remove Stray Data'
text_toggle_locators    =   'Toggle Locators'

#### logging/printing/warning
automate_success        =   'Wheel-O-Matic automation complete!'
automate_fail           =   'Wheel-O-Matic was unable to complete the automation. Please make sure your selection is correct.'
invoke_warn             =   'Please use the Wheel-O-Matic UI for setting up automated wheels/bones. Cancelling.'
locator_remove_warn     =   'Unable to remove existing Wheel-O-Matic locator draw handler. Restarting Blender should fix that.'
no_3d_view              =   'No 3D view found, cannot draw locators.'