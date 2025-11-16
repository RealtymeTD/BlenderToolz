import bpy

armature_name = "Armature"  # change to your armature's name
arm_obj = bpy.data.objects.get(armature_name)

if arm_obj and arm_obj.type == 'ARMATURE':
    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode='EDIT')

    arm_data = arm_obj.data
    bones_to_delete = [
        b for b in arm_data.edit_bones
        if "twist" in b.name.lower() and "necktwist" not in b.name.lower()
    ]

    for bone in bones_to_delete:
        arm_data.edit_bones.remove(bone)

    print(f"🦴 Deleted {len(bones_to_delete)} bones with 'twist' (excluding 'neckTwist').")

    bones_to_delete = [b for b in arm_data.edit_bones if "share" in b.name.lower() ]
    
    for bone in bones_to_delete:
        arm_data.edit_bones.remove(bone)
    
    print(f"Deleted {len(bones_to_delete)} bones with 'Share' in their name.")
else:
    print("❌ Armature not found or not an armature object.")