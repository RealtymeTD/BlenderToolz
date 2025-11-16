from pathlib import Path
import json
import bpy
import re

"""
    November 13, 2025
    Houdini can't get the A pose properly, so that means we are going full Blender
    for retargetting
"""

actorCoreCharacter = "D:/RealtymeFilmz/_CONSTANTS/BlenderToolz/Files/ActorCore_APose_Character.fbx"

DIRECTORY = "D:/RealtymeFilmz/_CONSTANTS/BlenderToolz/working_directory.txt"

with open(DIRECTORY) as readPath:
    GLB_FOLDER = readPath.readline()

folder_path = Path(GLB_FOLDER)
tracker_file = folder_path / "file_tracker.json"

if tracker_file.exists():
    tracker = json.loads(tracker_file.read_text())
else:
    raise("We have a problem my G! File tracker is missing!")

# Some renaming is happening in between, I don't see how Industry standard is gonna accept this
armature = bpy.data.objects.get("Armature")
if not armature or armature.type != 'ARMATURE':
    raise ValueError("❌ Could not find an armature named 'Armature'")

# # Regex to match .### suffix (e.g. .001, .045, etc.)
# pattern = re.compile(r'\.\d{3}$')

# for bone in armature.data.bones:
#     new_name = pattern.sub('', bone.name)
#     if new_name != bone.name:
#         print(f"Renaming bone: {bone.name} ➜ {new_name}")
#         bone.name = new_name

# 

# if armature:
#     pattern = re.compile(r'\.\d{3}$')
#     for child in armature.children:
#         print(child.name)
#         if child.type == 'ARMATURE':
#             print(child.name, " - - - - - - - > ")
#             new_name = pattern.sub('', child.name)
#             if new_name != child.name:
#                 print(f"Renaming inner armature: {child.name} ➜ {new_name}")
#                 child.name = new_name
# else:
#     print("❌ No armature named 'Armature' found. Well, that is sad!")

# print("Done!")

armature.name = "Source_Armature"

# Process Next File in NOT DONE ===
if not tracker["imported"]:
    print("No need to import the ActorCore file")
else:
    # Import the file
    bpy.ops.import_scene.fbx(filepath = actorCoreCharacter,
                             use_anim = False,
                             automatic_bone_orientation = True,
                             )