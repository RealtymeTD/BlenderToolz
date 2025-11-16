import bpy
import mathutils
import math 

TARGET_ARMATURE_NAME = "MetaHuman_Skeleton"

BONE_MAP = {
    "BoneRoot": "root",
    "Pelvis": "pelvis",
}

START_FRAME = bpy.context.scene.frame_start
END_FRAME = bpy.context.scene.frame_end

FLIP_QUATERNION = mathutils.Quaternion((0.0, 0.0, 1.0), math.radians(180.0))

# X_FLIP_QUATERNION = mathutils.Quaternion((1.0, 0.0, 0.0), math.radians(180.0))

LOC_FLIP_VECTOR = mathutils.Vector((1.0, -1.0, 1.0)) 
# ------------------------------------

bpy.ops.object.mode_set(mode='OBJECT') # Just in case

def copy_animation_proportional():
    
    target_armature = bpy.data.objects.get(TARGET_ARMATURE_NAME)

    if not target_armature:
        print(f"ERROR: Could not find Target Armature '{TARGET_ARMATURE_NAME}'.")
        return

    # --- FIX APPLIED HERE: Ensure Armature is Active for Mode Switch ---
    bpy.ops.object.select_all(action='DESELECT') # 1. Deselect everything
    target_armature.select_set(True)             # 2. Select the armature
    bpy.context.view_layer.objects.active = target_armature # 3. Make it the active object

    # ------------------------------------------------------------------

    target_armature.animation_data_clear()
    
    # This line should now execute without error
    bpy.ops.object.mode_set(mode='POSE')
    
    inv_armature_matrix = target_armature.matrix_world.inverted()

    source_root_obj = bpy.data.objects.get("BoneRoot")
    source_pelvis_obj = bpy.data.objects.get("Hip")
    source_cog_obj = target_armature.pose.bones.get("COG")

    for source_name, target_name in BONE_MAP.items():
        source_obj = bpy.data.objects.get(source_name)
        target_obj = bpy.data.objects.get(target_name)
        
        if not source_obj:
            continue
    
        target_bone = target_armature.pose.bones.get(target_name)

        if not source_obj or not target_bone:
            continue

        for frame in range(START_FRAME, END_FRAME + 1):
            bpy.context.scene.frame_set(frame)
            
            source_loc, source_rot, source_scale = source_obj.matrix_world.decompose()

            if source_name == "BoneRoot": # Yes, We can be explicit ooz it is the only one
                flipped_source_loc = source_loc # * LOC_FLIP_VECTOR 
                compensated_rot = source_rot @ FLIP_QUATERNION
                new_bone_matrix_world = mathutils.Matrix.Translation(flipped_source_loc) @ compensated_rot.to_matrix().to_4x4()
                target_bone.matrix = inv_armature_matrix @ new_bone_matrix_world

                target_bone.keyframe_insert(data_path="location", frame=frame)
                target_bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)
            elif source_name == "Pelvis": # We doing something special here too! Haha!
                source_hip_loc, source_hip_rot, _ = source_pelvis_obj.matrix_world.decompose()

                cog_loc, _, _ = source_cog_obj.matrix.decompose()
                offset_vector = cog_loc - source_hip_loc #  * LOC_FLIP_VECTOR
                pelvis_local_offset = mathutils.Vector((
                    offset_vector.x, 
                    -offset_vector.z,  # Y becomes Z
                    offset_vector.y   # Z becomes Y
                ))

                target_bone.location = pelvis_local_offset
                target_bone.keyframe_insert(data_path="location", frame=frame)

                # compensated_hip_rot = source_hip_rot @ FLIP_QUATERNION

                # flipped_rot = mathutils.Quaternion()
                # flipped_rot.w = compensated_hip_rot.w
                # flipped_rot.x = compensated_hip_rot.y
                # flipped_rot.y = -compensated_hip_rot.x
                # flipped_rot.z = compensated_hip_rot.z
                # # compensated_hip_rot = mathutils.Quaternion((compensated_hip_rot_raw.w, compensated_hip_rot_raw.x, compensated_hip_rot_raw.y, compensated_hip_rot_raw.z))
                # # compensated_hip_rot.x *= -1.0 # Negate the X-axis (Pitch) component
                
                # target_bone.rotation_quaternion = flipped_rot
                # target_bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)

                # From ChatGPT
                rest_matrix = target_bone.bone.matrix_local
                rest_inv = rest_matrix.inverted()
                bone_space_rot = (rest_inv.to_quaternion() @ source_hip_rot)

                # Optional correction 180° around Z
                correction = mathutils.Quaternion((0, 0, 1), math.radians(270))
                final_rot = bone_space_rot @ correction

                target_bone.rotation_mode = 'QUATERNION'
                target_bone.rotation_quaternion = final_rot
                target_bone.keyframe_insert("rotation_quaternion", frame=frame)

    # root_bone = target_armature.pose.bones.get("root")
    # if root_bone:
    #     bpy.context.scene.frame_set(START_FRAME)
    #     root_bone.rotation_mode = 'QUATERNION'
    #     fix = mathutils.Quaternion((0, 0, 1), math.radians(-90))
    #     root_bone.rotation_quaternion = fix @ root_bone.rotation_quaternion
    #     root_bone.keyframe_insert("rotation_quaternion", frame=START_FRAME)


    bpy.ops.object.mode_set(mode='OBJECT')
    print("SUCCESS: Proportional animation copy complete.")

    bpy.context.scene.frame_set(17)

# --- EXECUTION ---
copy_animation_proportional()