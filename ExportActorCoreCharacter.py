from pathlib import Path
import json
import bpy

"""
    After retargetting export for Unreal to do the Metahuman retargetting!

    Blender Z-up, Y-forward
    Unreal Z Up, X Forward
"""

DIRECTORY = "D:/RealtymeFilmz/_CONSTANTS/BlenderToolz/working_directory.txt"

with open(DIRECTORY) as readPath:
    GLB_FOLDER = readPath.readline()

folder_path = Path(GLB_FOLDER)
tracker_file = folder_path / "file_tracker.json"

if tracker_file.exists():
    tracker = json.loads(tracker_file.read_text())
else:
    raise("We have a problem my G! File tracker is missing!")

# === Process Next File in NOT DONE ===
if not tracker["imported"]:
    print("✅ All files processed!")
else:
    next_file_name = tracker["imported"][0]
    next_file_path = folder_path / next_file_name
    print(f"File To Export : {next_file_name}")

    # Make sure we're in Object Mode
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    # Deselect everything first
    bpy.ops.object.select_all(action='DESELECT')
    obj = bpy.data.objects.get("Armature")

    def find_object_fuzzy(base_name):
        # Exact match first
        obj = bpy.data.objects.get(base_name)
        if obj:
            return obj

        # Try with suffix tolerance: "Armature.001", "Armature.002", etc.
        for o in bpy.data.objects:
            if o.name.startswith(base_name):
                print(f"⚠️ Using fuzzy match: found '{o.name}' for '{base_name}'")
                return o

        print(f"❌ No object found matching '{base_name}' or its variants.")
        return None

    # Delete the Armature or select
    rootObj = find_object_fuzzy("Source_Armature")

    if rootObj:
        # Collect all children recursively
        objs_to_delete = [rootObj] + list(rootObj.children_recursive)

        # Select all objects in the hierarchy
        if objs_to_delete:
            for obj in objs_to_delete:
                if obj.name in bpy.data.objects:
                    # Check if object is in the active view layer
                    if obj.name in bpy.context.view_layer.objects:
                        obj.select_set(True)
                    else:
                        print(f"⚠️ Skipping {obj.name} (not in current view layer)")

                # Delete them
        bpy.ops.object.delete()
    else:
        print(f"❌ Object Armature not found.")

    # Force delete! Because Blender loves to force issues, I think the name is 
    # based on what is selected when you press the bake
    for action in bpy.data.actions:
        if action.name == "Armature|Action":
            continue

        if action.name == "Take_001":
            continue

        print("Deleted Action : ", action.name)
        bpy.data.actions.remove(action)

    hasActionTake = False
    for action in bpy.data.actions:
        if action.name == "Take_001":
            hasActionTake = True

    if not hasActionTake:
        for action in bpy.data.actions:
            action.name = "Take_001"

            break

    bpy.ops.export_scene.fbx(
        filepath = Path(folder_path/next_file_name.replace("glb", "fbx")  ).as_posix(),
        use_selection = False,  # export all objects
        apply_scale_options = 'FBX_SCALE_ALL',
        bake_space_transform = True,
        use_space_transform = False,
        bake_anim_use_all_actions = True,

        # primary_bone_axis = "X",
        # secondary_bone_axis = "Y",
        axis_forward='Y', # Forward axis in your target app
        axis_up='Z', 
    )

    # Update Tracker what files we've worked on so far
    # tracker["imported"].remove(next_file_name)
    # tracker["done"].append(next_file_name)
    # tracker_file.write_text(json.dumps(tracker, indent = 4))

    # print(f"Exported {next_file_name}")

# NOTES :
"""
        primary_bone_axis = "Y",
        secondary_bone_axis = "X",
        axis_forward='X', # Forward axis in your target app
        axis_up='Z', 

        Nearly all the joints are messed up, but animation is OK

        --------------------------------------------------------------------------------
        
        primary_bone_axis = "X",
        secondary_bone_axis = "-Y",
        axis_forward='-Y', # Forward axis in your target app
        axis_up='Z', 

        As suggested by Google!Now completely messed up. LOL!

        --------------------------------------------------------------------------------

        When creating the empties, I matched the settings
        X > X
        Y > -Y
"""