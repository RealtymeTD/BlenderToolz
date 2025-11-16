import bpy
import mathutils
import math 

SOURCE_ARMATURE_NAME = "Armature"
TARGET_ARMATURE_NAME = "MetaHuman_Skeleton"

BONE_MAP = {
    "BoneRoot": "root",
    "Pelvis": "pelvis",
    
    "R_Thigh" : "thigh_r",
    "R_Calf" : "calf_r",
    "R_Foot" : "foot_r",
    "R_ToeBase" : "ball_r",

    "L_Thigh" : "thigh_l",
    "L_Calf" : "calf_l",
    "L_Foot" : "foot_l",
    "L_ToeBase" : "ball_l",
}



bpy.ops.object.mode_set(mode='OBJECT') # Just in case

def fix_local_rotation(raw_rot):
    # The confirmed fix for internal bone orientations: X/Y swap and Y negation
    fixed_rot = mathutils.Quaternion()
    fixed_rot.w = raw_rot.w   
    fixed_rot.x = raw_rot.y    # Source Roll -> Target Pitch
    fixed_rot.y = -raw_rot.x   # Source Pitch -> -Target Roll
    fixed_rot.z = raw_rot.z    # Source Yaw -> Target Yaw
    return fixed_rot

def retargetAnimation():
    source_armature = bpy.data.objects.get(SOURCE_ARMATURE_NAME)

    target_armature = bpy.data.objects.get(TARGET_ARMATURE_NAME)

    if not source_armature:
        print(f"ERROR: Could not find Source Armature '{SOURCE_ARMATURE_NAME}'.")
        return
    
    if not target_armature:
        print(f"ERROR: Could not find Target Armature '{TARGET_ARMATURE_NAME}'.")
        return

    # TODO
    # Change the oriention of the metahuman 180 on the Z
    # Apply transforms

    START_FRAME = bpy.context.scene.frame_start
    END_FRAME = bpy.context.scene.frame_end

    FLIP_QUATERNION = mathutils.Quaternion((0.0, 0.0, 1.0), math.radians(0.0))

    LOC_FIX_VECTOR = mathutils.Vector((1.0, 1.0, -1.0))

    bpy.ops.object.select_all(action='DESELECT') # 1. Deselect everything
    target_armature.select_set(True)             # 2. Select the armature
    bpy.context.view_layer.objects.active = target_armature # 3. Make it the active object
    target_armature.animation_data_clear()
    bpy.ops.object.mode_set(mode='POSE')

    target_armature.animation_data_clear()

    # Ensure source is also in Pose mode for bone matrix access
    bpy.context.view_layer.objects.active = source_armature
    bpy.ops.object.mode_set(mode='POSE')

    inv_armature_matrix = target_armature.matrix_world.inverted()

    source_cog_bone = target_armature.pose.bones.get("COG")

    for source_name, target_name in BONE_MAP.items():
        source_bone = source_armature.pose.bones.get(source_name)
        target_bone = target_armature.pose.bones.get(target_name)

        if not source_bone or not target_bone:
            print(f"Missing either the Source Bone {source_bone} or Target bone {target_bone}")

            continue

        for frame in range(START_FRAME, END_FRAME + 1):
            bpy.context.scene.frame_set(frame)

            if source_name == "BoneRoot":
                source_loc, source_rot, source_scale = (source_armature.matrix_world @ source_bone.matrix).decompose()
                flipped_source_loc = source_loc # * LOC_FIX_VECTOR
                remap_loc = source_rot @ FLIP_QUATERNION
                new_bone_matrix_world = mathutils.Matrix.Translation(flipped_source_loc) @ remap_loc.to_matrix().to_4x4()
                target_bone.matrix = inv_armature_matrix @ new_bone_matrix_world
                
                target_bone.keyframe_insert(data_path="location", frame=frame)
                target_bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)

            elif source_name == "Pelvis":
                source_hip_loc, source_hip_rot, _ = source_bone.matrix.decompose()
                cog_loc, _, _ = source_cog_bone.matrix.decompose()

                offset_vector = cog_loc - source_hip_loc #  * LOC_FLIP_VECTOR
                pelvis_local_offset = mathutils.Vector((
                    offset_vector.x, 
                    -offset_vector.z,  # Y becomes Z
                    offset_vector.y   # Z becomes Y
                ))

                target_bone.location = pelvis_local_offset
                target_bone.keyframe_insert(data_path="location", frame=frame)

                # Now deal with rotations
                source_loc, source_rotation, source_scale = (source_armature.matrix_world @ source_bone.matrix).decompose()

                X_PELVIS_CORRECTION = mathutils.Quaternion((1, 0, 0), math.radians(90))
                Z_PELVIS_CORRECTION = mathutils.Quaternion((0, 0, 1), math.radians(90))

                source_rot_1 = X_PELVIS_CORRECTION @ Z_PELVIS_CORRECTION @ source_rotation

                FLIP_180 = mathutils.Quaternion((0, 1, 0), math.radians(180))
                source_rot_2 = FLIP_180 @ source_rot_1

                FLIP_X_180 = mathutils.Quaternion((0, 0, 1), math.radians(180))
                source_rot = FLIP_X_180 @ source_rot_2

                remapped_rot = mathutils.Quaternion((   source_rot.w,
                                                        source_rot.z,
                                                        source_rot.x,
                                                        source_rot.y
                                                        ))
    
                new_bone_matrix_world = (   target_armature.matrix_world.inverted() @
                                            mathutils.Matrix.Translation( (target_armature.matrix_world @ target_bone.head) ) @
                                            remapped_rot.to_matrix().to_4x4())
    
                target_bone.matrix =  new_bone_matrix_world # inv_armature_matrix @
                target_bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)
            else: # It is just a regular bone
                if source_bone.rotation_mode == "XYZ": # Euler
                    raw_rot = source_bone.rotation_euler.to_quaternion()
                    target_bone.rotation_quaternion = raw_rot

                elif source_bone.rotation_mode == 'QUATERNION' or source_bone.rotation_mode == 'WXYZ':
                    raw_rot = source_bone.rotation_quaternion
                    target_bone.rotation_quaternion = raw_rot

                target_bone.rotation_mode = 'QUATERNION'
                target_bone.keyframe_insert(data_path="location", frame=frame)
                target_bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)

    bpy.context.scene.frame_set(100)

retargetAnimation()