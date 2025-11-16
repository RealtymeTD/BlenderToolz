import bpy

scale_multiplier = 0.0085

# === Settings ===
source_xform = bpy.context.active_object
target_obj = bpy.data.objects.get("Gizmo")  # Change name as needed

if not source_xform:
    raise ValueError("❌ No active object selected as source.")
if not target_obj:
    raise ValueError("❌ Could not find target object 'Gizmo'.")

# Move source object to target's world location
target_obj.matrix_world = source_xform.matrix_world.copy()

target_obj.scale = [s * scale_multiplier for s in target_obj.scale]


print(f"✅ {source_xform.name} moved to {target_obj.name}'s location.")
