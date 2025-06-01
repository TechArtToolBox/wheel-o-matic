# Wheel-O-Matic
Blender add-on to automate wheel rotation in any direction. Works with meshes and bones.(Blender 3.0 and above)

## Installation
- [Download the latest version here](https://github.com/TechArtToolBox/wheel-o-matic/blob/main/wheel_o_matic_v1.0.0.zip). Save the Wheel-O-Matic zip file to your computer.
- Install like any other Blender add-on/extention.
- In the 3D View sidebar, there will be a tab called Wheel-O-Matic


## Mesh Wheels quickstart
- Be sure that your wheel(s) aim down either the Y or X global axis, and that they already rotate correctly on a single axis.
- Highly recomend applying any existing scale and rotation for best results, but it is optional.  
- Select the wheel(s) to be automated.
- In the Wheel-O-Matic tab, click 'Automate'
- If a wheel has no parent, a controller will be created. Use this controller to move the wheel around and roll automatically.
- If a wheel HAS a parent, the parent can be moved (or anything higher up the chain) to see the wheels rotate along with the movement.

## Bone Driven Wheel quickstart
- Select an armature, and enter Pose mode. The Wheel-O-Matic UI will adjust to match bone setup.
- In the 3D view, select a bone that drives a wheel.
- In the Wheel-O-Matic tab under 'Reference Wheel Geo' use the picker to select the mesh associated with this bone.
- click 'Automate' to automate the bone's rotation based on the wheel's dimensions.

## Adjusting
- With an automated mesh wheel or automated bone selected, twirl open the 'Adjust' panel in the Wheel-O-Matic tab to see the 'Rotation Power' and 'Radius' options.
  - **Rotation power** Changes automation strength. Zero means no rotation, negative values spin the wheel in reverse.
  - **Radius** Changes the radius of the wheel. This rarely needs to be changed.
- Both of these can be keyed as needed.
  
## Utilities
- In the Wheel-O-Matic tab twirl down the 'utilities' panel for general utilities related to wheel automation.
  - **Clear Auto Rotation**
    - This will zero out auto rotation for any automated mesh wheels or bones that are selected.
  - **Remove Automation**
    - This removes automation for any mesh wheels or bones that are selected.
  - **Toggle Locators**
    - Toggles the visibility of all locators that appear under automated wheels
  - **Scale Locators**
    - Scale all locators
  - **Remove Stray Data**
    - Finds and removes any unused automation data. This is rarely needed, only happens if a driven wheel or driven bone is deleted.
  - **Refresh Wheel Logic**
    - Brings back to life any automated wheels that are no longer automating. This is rare, usually only happens if a prompt to allow python is denied, or the addon is uninstalled and re-installed in the same session. 



