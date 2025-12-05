import bpy
import re
from pathlib import Path
import json
import sys

sys.path.append("C:/Python311/Lib/site-packages")
from pygltflib import GLTF2

"""
    December 1, 2025
    Broke and feeling not very motivated, but here I am as I have done nothing 
    the last 3 days, 2 more months and another year clocks in, is what we are 
    trying to achieve even worth it?

    NOTE
    Convert the GLB that already have meshes and bones to FBXs, so we don't
    have the empties as before! direct conversion is best

"""

folder_to_process = "Light_Sabers"

# ------

GLB_FOLDER = f"D:/RipAndTear/RipperReallusion/Motions/{folder_to_process}/Blender"

A_POSE = "D:/RealtymeFilmz/_CONSTANTS/BlenderToolz/Files/apose-533907.glb"

folder_path = Path(GLB_FOLDER)

animationLengthsJson = f"{GLB_FOLDER}/animation_lengths.json"

if not Path(animationLengthsJson).exists():
    animationLengths = {}
    for glb in Path(GLB_FOLDER).iterdir():
        if glb.suffix == ".glb":
            loadedGLB = GLTF2().load_binary(glb.as_posix() )

            # Check if any animations exist
            if not loadedGLB.animations:
                print("ℹ️ No animations found in the GLB file.")
                continue

            # We will analyze the first animation (loadedGLB.animations[0])
            animation = loadedGLB.animations[0]
            
            # 1. Find the accessor containing the time keyframes (input)
            # The 'input' property of a channel sampler points to the accessor for time data.
            if not animation.samplers:
                print("ℹ️ First animation has no samplers (no data).")
                continue
                
            # Get the accessor index from the first sampler's input
            time_accessor_index = animation.samplers[0].input
            
            # 2. Retrieve the Accessor object
            accessor = loadedGLB.accessors[time_accessor_index]
            
            # 3. Get the maximum time value (this is the duration)
            # The glTF spec stores the max/min values directly on the accessor for efficiency.
            # The maximum value array (max) contains [max_time]
            
            if accessor.max is None or len(accessor.max) == 0:
                print("⚠️ Time accessor is missing max bounds, calculation skipped.")
                continue
                
            duration = accessor.max[0]
            
            frameCount = int(duration * 30)
            animationLengths[glb.name] = frameCount

            # break


    with open(f"{GLB_FOLDER}/animation_lengths.json", 'w') as writeJson:
        json.dump(animationLengths, writeJson, indent = 2)

    print("Saved the animations lengths to disk")
else:
    with open(animationLengthsJson) as readJson:
        animationLengths = json.load(readJson)

folder_path = Path(GLB_FOLDER)
tracker_file = folder_path / "file_tracker.json"

if tracker_file.exists():
    tracker = json.loads(tracker_file.read_text())
else:
    # Scan folder for .glb files
    all_files = [f.name for f in folder_path.glob("*.glb")]
    tracker = {"not_done": all_files, "imported" : [], "done": []}
    tracker_file.write_text(json.dumps(tracker, indent = 4 ) )

if not tracker["not_done"]:
    print("All files processed!")
elif tracker["imported"]: # We have a previous export pending
    print("First export the current animation")  
else:
    # Clean up first
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global = True)

    # As they get to linger and get a .001, so annoying!
    for action in bpy.data.actions:
        bpy.data.actions.remove(action)

    next_file_name = tracker["not_done"][0]
    next_file_path = folder_path / next_file_name
    print(f"Processing: {next_file_name}")

    # Set the frame range so we don't have to look for it
    bpy.context.scene.frame_end = int(animationLengths[next_file_name])

    # Import GLB
    bpy.ops.import_scene.gltf( filepath = next_file_path.as_posix(), 
                                directory = next_file_path.parent.as_posix(), 
                                files = [{"name":next_file_name, "name":next_file_name}], 
                                loglevel = 20, 
                                disable_bone_shape = True,
                                guess_original_bind_pose = False,
                                import_merge_material_slots = False,
                                import_pack_images = False,
                                merge_vertices = True
                                )
    
    print(next_file_name)

    # Update Tracker what files we've worked on so far
    tracker["not_done"].remove(next_file_name)
    tracker["imported"].append(next_file_name)
    tracker_file.write_text(json.dumps(tracker, indent = 4))











# # Is not working, the export that is. Manual for now
# for glb in Path(GLB_FOLDER).iterdir():
#     if glb.suffix != ".glb":
#         continue

#     # Clean up first
#     if bpy.context.object and bpy.context.object.mode != 'OBJECT':
#         bpy.ops.object.mode_set(mode='OBJECT')

#     bpy.ops.object.select_all(action='SELECT')
#     bpy.ops.object.delete(use_global = True)

#     # As they get to linger and get a .001, so annoying!
#     for action in bpy.data.actions:
#         bpy.data.actions.remove(action)

#     # Set the frame range so we don't have to look for it
#     bpy.context.scene.frame_end = int(animationLengths[glb.name])

#     # Import 
#     bpy.ops.import_scene.gltf(  filepath = glb.as_posix(), 
#                                 directory = glb.parent.as_posix(), 
#                                 files = [{"name":glb.name, "name":glb.name}], 
#                                 loglevel = 20, 
#                                 disable_bone_shape = True,
#                                 guess_original_bind_pose = False,
#                                 import_merge_material_slots = False,
#                                 import_pack_images = False,
#                                 merge_vertices = True
#                                 )


#     fbxFile = glb.name.replace("glb", "fbx")
#     bpy.ops.export_scene.fbx(
#         filepath = Path(folder_path/fbxFile).as_posix(),
#         use_selection = False,  # export all objects
#         apply_scale_options = 'FBX_SCALE_ALL',
#         bake_space_transform = True,
#         use_space_transform = False,
#         bake_anim_use_all_actions = True,
#         add_leaf_bones = False,
#         use_armature_deform_only = True,

#         # primary_bone_axis = "X",
#         # secondary_bone_axis = "Y",
#         axis_forward='-Y', # Forward axis in your target app
#         axis_up='Z', 
#     )

#     break