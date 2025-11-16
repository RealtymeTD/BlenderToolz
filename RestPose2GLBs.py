import bpy
import re
from pathlib import Path
import json

"""
    November 12, 2025
    Finally got the thing to work. Took all my patience, but now that WETA position
    really looks like a possibility
"""

# PROCESS
# 1. Run the empties to bones command after importing so as to get the Armature


# Import the ActorCore Character


GLB_FOLDER = "D:/Downloads/iClone_ActorCore/Fight_Stunts/Run_Batch"

# ------

A_POSE = "D:/RealtymeFilmz/_CONSTANTS/BlenderToolz/Files/apose-533907.glb"

DIRECTORY = "D:/RealtymeFilmz/_CONSTANTS/BlenderToolz/working_directory.txt"

# Write out a file for our import and export so we just write the path once!
folder = Path(__file__).parent
with open(DIRECTORY, 'w') as workingPath:
    workingPath.write(GLB_FOLDER)

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
    print("✅ All files processed!")
else:
    # Clean up first
    if bpy.context.object and bpy.context.object.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')

    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global = True)
    
    next_file_name = tracker["not_done"][0]
    next_file_path = folder_path / next_file_name
    print(f"Processing: {next_file_name}")

    # Import GLB
    bpy.ops.import_scene.gltf( filepath = next_file_path.as_posix(), 
                                directory = next_file_path.parent.as_posix(), 
                                files = [{"name":next_file_name, "name":next_file_name}], 
                                loglevel = 20, 
                                disable_bone_shape = True,
                                guess_original_bind_pose = False,
                                import_merge_material_slots = False,
                                import_pack_images = False,
                                merge_vertices = True )
    
    # Update Tracker what files we've worked on so far
    tracker["not_done"].remove(next_file_name)
    tracker["imported"].append(next_file_name)
    tracker_file.write_text(json.dumps(tracker, indent = 4))

    # You import the A Pose second, then the animation after, that way the A Pose
    # gets the .001 suffix at the end, this is because the animation needs the name to 
    # be clean for the retargetting
    aPoseName = Path(A_POSE).name
    bpy.ops.import_scene.gltf(  filepath = A_POSE,
                                directory = Path(A_POSE).parent.as_posix(), 
                                files = [{"name":aPoseName, "name":aPoseName}], 
                                loglevel = 20, 
                                disable_bone_shape = True,
                                guess_original_bind_pose = False,
                                import_merge_material_slots = False,
                                import_pack_images = False,
                                merge_vertices = True )

    SOURCE_ROOT_NAME = "RootNode.001"   # The T-pose empties hierarchy
    TARGET_ROOT_NAME = "RootNode"    # The animated empties hierarchy

    ENABLE_FRAME = 0
    DISABLE_FRAME = 1

    bpy.context.scene.frame_start = 0 # Where we bake our animation

    # --- Get references ---
    source_root = bpy.data.objects.get(SOURCE_ROOT_NAME)
    target_root = bpy.data.objects.get(TARGET_ROOT_NAME)

    if not source_root or not target_root:
        raise ValueError("❌ Could not find source or target root nodes")

    # --- Collect all children recursively ---
    def collect_hierarchy(obj):
        result = {}
        result[obj.name] = obj
        for child in obj.children:
            result.update(collect_hierarchy(child))
        return result

    source_objs = collect_hierarchy(source_root)
    target_objs = collect_hierarchy(target_root)

    print(f"✅ Source: {len(source_objs)} empties | Target: {len(target_objs)} empties")

    # --- Helper to find best name match (accounts for Blender's .001 etc) ---
    def find_matching_source(name, source_dict):
        # Try exact match first
        if name in source_dict:
            return source_dict[name]
        # Try stripping suffixes like ".001"
        base = re.sub(r"\.\d{3}$", "", name)
        # Search for anything that starts with base name
        for src_name in source_dict.keys():
            if src_name == base or src_name.startswith(base + "."):
                return source_dict[src_name]
        return None

    # --- Clear existing constraints ---
    for obj in target_objs.values():
        for c in obj.constraints:
            obj.constraints.remove(c)

    # --- Add Copy Transforms constraints ---
    for name, target in target_objs.items():
        source = find_matching_source(name, source_objs)
        if not source:
            print(f"⚠️ No matching T-pose source found for: {name}")
            continue

        con = target.constraints.new('COPY_TRANSFORMS')
        con.name = f"CT_{name}"
        con.target = source

        # Enable at frame 0
        con.influence = 1.0
        con.keyframe_insert(data_path="influence", frame=ENABLE_FRAME)

        # Disable at frame 1
        con.influence = 0.0
        con.keyframe_insert(data_path="influence", frame=DISABLE_FRAME)

        print(f"✅ CopyTransforms added: {name} → {source.name}")

    print("🎯 Frame 0 T-pose matching complete (handles .001 suffixes).")

    # --- Bake into target ---
    START_FRAME = bpy.context.scene.frame_start
    END_FRAME = bpy.context.scene.frame_end

    def bake_hierarchy(root_name, start_frame, end_frame):
        root_obj = bpy.data.objects.get(root_name)
        if not root_obj:
            print(f"ERROR: Could not find root object '{root_name}'")
            return

        objs_to_bake = [root_obj] + list(root_obj.children_recursive)
        bpy.ops.object.select_all(action='DESELECT')
        for obj in objs_to_bake:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = root_obj

        bpy.ops.nla.bake(frame_start=start_frame,
                        frame_end=end_frame,
                        only_selected=True,
                        visual_keying=True,
                        clear_constraints=True,
                        use_current_action=True,
                        bake_types={'OBJECT'})

    bake_hierarchy(TARGET_ROOT_NAME, START_FRAME, END_FRAME)
    print("✅ Baking done — animated empties now have frame 0 T-pose baked.")

    # Delete the RootNode aka the A Pose as we don't need it anymore.
    root_obj = bpy.data.objects.get(SOURCE_ROOT_NAME)
    if not root_obj:
        raise ValueError(f"❌ Could not find object '{SOURCE_ROOT_NAME}'")

    # Select the root object
    bpy.ops.object.select_all(action='DESELECT')
    root_obj.select_set(True)

    # Recursively select all children
    def select_hierarchy(obj):
        for child in obj.children:
            child.select_set(True)
            select_hierarchy(child)

    select_hierarchy(root_obj)

    # Delete all selected objects
    bpy.ops.object.delete()

    bpy.context.scene.frame_set(0) # So we in the rest pose automatically
    
    # So that we can just press the Empties To Bone button
    bpy.ops.object.select_all(action='SELECT')