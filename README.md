# Wheel-O-Matic
Automatic wheel rotation add-on for Blender (2.83 and above)

## Installation
- [Find the latest version here](https://github.com/TechArtToolBox/wheel-o-matic/releases/latest). Save the wheel_o_matic zip file to your computer.
- Install like any other Addon.
- The addon interface can be found in the sidebar of the 3d viewport once installed. 

## Initial wheel setup
- Create Controller
  - Select the geo of your wheel. 
  - IMPORTANT: apply rotation and scale to the wheel geo before using the addon for best results. (ctrl+a hotkey, then choose Rotation & Scale from the menu)
  - Click the "Wheel-O-matic" tab in the 3d view sidebar to bring up the "Wheel-o-Matic" UI.
  - Under the "Create Controllers" section of the UI, click the "Create Wheel Controller" button to create a wheel controller.
  - This will create a wheel controller at the base of your wheel. (It looks like an arrow).
    This controller outputs rotation information that matches the geo of your wheel as it moves through the scene as long as the wheel controller moves along with the wheel. 
 
- Connect Controller
  The wheel controller now needs to know what rotation to drive. Rotation can be connected to the geo directly, or to part of a larger rig.
  The rotation information can be connected to any one of the following:
  - wheel geo directly
  - bone that controls the wheel
  - some other object that controls the wheel



