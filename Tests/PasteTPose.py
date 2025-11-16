import bpy

"""
    NOTE actually just import it automatically
    You need to import the character from the motion builder folder
"""

SOURCE_ARMATURE_NAME = "Armature"  # The T-pose armature
TARGET_ROOT_NAME = "RootNode"  # Root of the animated empties

ENABLE_FRAME = 0
DISABLE_FRAME = 1

# --- Get references ---
source_armature = bpy.data.objects.get(SOURCE_ARMATURE_NAME)
target_root = bpy.data.objects.get(TARGET_ROOT_NAME)

if not source_armature or not target_root:
    raise ValueError("❌ Could not find Armature_TPose or RootNode")

# --- Build lookup of bones by name ---
source_bones = {bone.name: bone for bone in source_armature.pose.bones}

# --- Recursively collect empties under RootNode ---
def collect_children(obj, found):
    found[obj.name] = obj
    for child in obj.children:
        collect_children(child, found)

target_empties = {}
collect_children(target_root, target_empties)

print(f"✅ Found {len(target_empties)} empties under {TARGET_ROOT_NAME}")

# --- Clear old constraints to avoid duplicates ---
for empty in target_empties.values():
    for c in empty.constraints:
        empty.constraints.remove(c)

# --- Create Copy Transforms from armature → empties ---
for name, empty in target_empties.items():
    bone = source_bones.get(name)
    if bone:
        con = empty.constraints.new('COPY_TRANSFORMS')
        con.name = f"CT_{name}"
        con.target = source_armature
        con.subtarget = bone.name

        # Enable at frame 0
        con.influence = 1.0
        con.keyframe_insert(data_path="influence", frame=ENABLE_FRAME)

        # Disable at frame 1
        con.influence = 0.0
        con.keyframe_insert(data_path="influence", frame=DISABLE_FRAME)

        print(f"✅ Constraint added: {name}")
    else:
        print(f"⚠️ No matching bone found for empty: {name}")

print("🎉 Done — empties now copy the armature's T-pose at frame 0 only.")

# Bake the animation into the nulls
START_FRAME = bpy.context.scene.frame_start
END_FRAME = bpy.context.scene.frame_end

def bake_hierarchy(root_name, start_frame, end_frame):
    root_obj = bpy.data.objects.get(root_name)
    if not root_obj:
        print(f"ERROR: Could not find root object '{root_name}'")
        return

    # Collect all objects in hierarchy
    objs_to_bake = [root_obj] + list(root_obj.children_recursive)

    # Deselect all
    bpy.ops.object.select_all(action='DESELECT')

    for obj in objs_to_bake:
        obj.select_set(True)

    bpy.context.view_layer.objects.active = root_obj

    # Bake location, rotation, scale
    bpy.ops.nla.bake(frame_start=start_frame,
                     frame_end=end_frame,
                     only_selected=True,
                     visual_keying=True,
                     clear_constraints=True,
                     use_current_action=True,
                     bake_types={'OBJECT'})

bake_hierarchy(TARGET_ROOT_NAME, START_FRAME, END_FRAME)
print("Baking complete. You can safely delete the armature now.")