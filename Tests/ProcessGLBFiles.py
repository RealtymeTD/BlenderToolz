from pathlib import Path
import bpy

"""
    November 9, 2025
    Process all the GLBs in one go, we about to rip a whole website so 
    we need a way to quickly process all the shots
"""

folder = "D:/Downloads/iClone_ActorCore/Fight_Stunts"

counter = 0
for glb in Path(folder).iterdir():
    if glb.suffix == ".glb":
        # Clean up first, but only if we find a .glb, as we also have the enc and fbx files as well.
        bpy.ops.object.select_all(action='SELECT')
        bpy.ops.object.delete(use_global = True)

        bpy.ops.import_scene.gltf(filepath=glb.as_posix() , 
                                  directory=glb.parent.as_posix(), 
                                  files = [{"name":glb.name, "name":glb.name}], 
                                  loglevel = 20, 
                                  disable_bone_shape = True,
                                  guess_original_bind_pose = False,
                                  import_merge_material_slots = False,
                                  import_pack_images = False,
                                  merge_vertices = True )
        
        # Select 
        bpy.ops.object.select_all(action='DESELECT')
        for obj in bpy.data.objects:
            if "CC_Base_" in obj.name:
                obj.select_set(True)

        bpy.ops.object.delete(use_global=False, confirm=False)

        # EXPORT FBX 
        bpy.ops.export_scene.fbx(
            filepath = Path(glb.parent, glb.name.replace("glb", "fbx") ).as_posix(),
            use_selection = False,  # export all objects
            apply_scale_options = 'FBX_SCALE_ALL',
            bake_space_transform = True,
            use_space_transform = False,
            primary_bone_axis = "Y",
            secondary_bone_axis = "X",
            axis_forward='Z', # Forward axis in your target app
            axis_up='Y', 
        )

        print(f"Exported : {glb.name}")
        counter += 1

        # break # Don't do it once!

print(f"Processed {counter} files")