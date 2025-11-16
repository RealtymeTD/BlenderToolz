import bpy
import random

# Get the active object, assuming it is an armature
obj = bpy.context.active_object

if obj is not None and obj.type == 'ARMATURE':
    armature = obj.data
    
    # Ensure we are in Object or Edit mode to access the correct bone properties
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    for bone in armature.bones:
        # Enable custom colors for the bone
        bone.color.palette = 'CUSTOM'
        
        # Set a random color (RGB values between 0.0 and 1.0)
        # You can replace this with a specific color tuple, e.g., (1.0, 0.0, 0.0) for red
        r = random.random()
        g = random.random()
        b = random.random()
        bone.color.custom.normal = (r, g, b)
        
        # Optional: Set selected and active colors (defaults might be fine)
        # bone.color.custom.select = (r * 0.8, g * 0.8, b * 0.8) 
        # bone.color.custom.active = (r * 1.2, g * 1.2, b * 1.2)
        
    print(f"Colored all bones in armature: {obj.name}")
else:
    print("Please select an armature object.")

