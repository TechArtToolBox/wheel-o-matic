# Wheel-O-Matic
Blender add-on to automate wheel rotation for any wheel, in any direction. Works on any vehicle, works on splines, works with meshes and bones.(Blender 3.0 and above)

![one_wheel_demo](https://github.com/user-attachments/assets/2480f7b2-eaab-451c-9092-4c1ab9def830)


## Installation
- [Download the latest Wheel-O-Matic version here](https://github.com/TechArtToolBox/wheel-o-matic/blob/main/wheel_o_matic_v1.0.0.zip)
- Install like any other Blender add-on/extension.
- Wheel-O-Matic will be located in the 3D View sidebar

  ![wheel_o_matic_tab](https://github.com/user-attachments/assets/5e1d31bb-f879-495a-bf90-538cbc7a61d0) 


## Mesh Wheels quickstart
**1. Preflight check:**
  - Be sure that your wheel(s) and/or your vehicle are parallel to either the Y or X global axis, sit flat on the XY plane, and that the wheels already rotate correctly on a single axis (see good/bad images below)
  - Also highly recommended to apply any existing scale and rotation for best results. (totally optional, but it can help prevent Gimbal Lock later on with complex movements)
    - <sub>If unfamiliar with applying transforms, you can do so by selecting the geo and pressing ctrl+a on the keyboard to bring up the apply menu. From the dropdown select Rotation and Scale</sub>

     ![image](https://github.com/user-attachments/assets/cb4695f1-98cf-46c4-8ede-151ed8db7034) ![image](https://github.com/user-attachments/assets/bcda90f1-e15d-4e85-bc38-936dac23d3ed)


**2. Automate the Wheels**
  - Select the wheel(s) to be automated.
  - In the Wheel-O-Matic tab, click '**Automate**' to finish and apply the automation.

**3. Test the Results**
  - If a wheel has no parent, a controller will be created. Use this controller to move the wheel around and check that it rolls correctly.
  - If a wheel HAS a parent, the parent (or anything higher up the chain) can be moved to see the wheels rotate along with the movement.
  - Locators will also be created. These can be used to make sure the wheel is setup correctly. The locator(s) should be at the base of the wheel(s), and have arrows that point in the forward and reverse direction of the wheel(s).


## Bone Driven Wheels quickstart
- Be sure that the bone(s) can already rotate the wheel(s) they control correctly, and that they do so on a single axis.
- Select an armature, and enter Pose mode. The Wheel-O-Matic UI will adjust to match bone setup.
- For each bone that drives a wheel:
  - Select the pose bone in the 3D view.
  - In the Wheel-O-Matic tab, under 'Reference Wheel Geo' use the picker to select the mesh associated with this bone.
  - click 'Automate' to automate the bone's rotation based on the wheel's dimensions.
  - Locators will also be created. These can be used to make sure the wheel is setup correctly. The locator should be at the base of the wheel, and have arrows that point in the forward and reverse direction of the wheel.

## Adjust Panel
These options become available when a single automated mesh wheel, or single automated bone is selected. Both values can be keyed as needed.
- **Rotation power**
  - Changes automation strength. Zero means no rotation, negative values spin the wheel in reverse.
- **Radius**
  - Changes the radius of the wheel. Use the locators as a guide to match radius to the size of the wheel. This rarely needs to be changed.
  
## Utilities Panel
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



