import bpy

from bpy.props import (StringProperty,
                        CollectionProperty,
                       BoolProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       EnumProperty,
                       PointerProperty,
                       )
from bpy.types import (Panel,
                       Menu,
                       Operator,
                       PropertyGroup,
                       Object, Mesh, Armature
                       )
                       
                       
## VRM0 Blendshape Tool ##
# author: lunazera
# originally adapated from script by lumibnuuy


def add_vrm0_blendshape_proxy(armature: Armature, mesh_object: Object, clear=True, match_extra=False, combine=False) -> None:
    """Adds VRM Blendshape Clips to armature based on a mesh's shapekeys
    
    This will loop through all shapekeys on a mesh and create blendshape clips, checking to make sure
    the name is valid and matching to VRM's default blendshapes (like 'a', 'i', 'o'...)
    
    clear: Deletes existing blendshapes
    match_extra: Checks to match against basic expressions (joy, angry, look up, etc)
    combine: If the blendshape clip already exists, bind the mesh to it.
    
    """
    mesh = mesh_object.data
    if not isinstance(mesh, Mesh):
        return
    if not hasattr(mesh, "shape_keys"):
        return
    if not mesh.shape_keys:
        return
    if not hasattr(mesh.shape_keys, "key_blocks"):
        return
    if not mesh.shape_keys.key_blocks:
        return
    
    armature_data_extension = armature.data.vrm_addon_extension
    if not hasattr(armature_data_extension, "vrm0"):
        return
    vrm0 = armature_data_extension.vrm0
    if not hasattr(vrm0, "blend_shape_master"):
        return
    blend_shape_master = vrm0.blend_shape_master
    if not hasattr(blend_shape_master, "blend_shape_groups"):
        return
    blend_shape_groups = blend_shape_master.blend_shape_groups
    # dump(blend_shape_groups)

    shape_key = bpy.context.blend_data.shape_keys.get(mesh.shape_keys.name)

    proxy = bpy.data.objects.new(mesh_object.name + "_vrm_blendshape_proxy", None)
    proxy.empty_display_type = "SPHERE"
    proxy.parent = armature
    
    # Clear the current list if true
    if clear:
        print("Cleaning up blendshape clips")
        blend_shape_groups.clear()

    # For each shapekey on the mesh
    for i, key_block in enumerate(mesh.shape_keys.key_blocks):
        
        # Basic checks for the shapekey
        # Make sure it isn't the initial basis, that the text is in english, and that the shapekey isn't muted.
        if i == 0:
            continue
        if len(key_block.name) == 0:
            continue
        if not isEnglish(key_block.name):
            continue
        if key_block.mute:
            continue
        
        presetName = 'unknown' 
        # Match shapekeys to known VRM defaults
        match key_block.name.lower():
            case 'a':
                presetName = 'a'
            case 'e':
                presetName = 'e'
            case 'i':
                presetName = 'i'
            case 'o':
                presetName = 'o'
            case 'u':
                presetName = 'u'
            case 'neutral':
                presetName = 'neutral'
            case 'blink_l':
                presetName = 'blink_l'
            case 'blink_r':
                presetName = 'blink_r'
        
        if match_extra:
            match key_block.name.lower():
                case 'joy':
                    presetName = 'joy'
                case 'angry':
                    presetName = 'angry'
                case 'sorrow':
                    presetName = 'sorrow'
                case 'fun':
                    presetName = 'fun'
                case 'loop up':
                    presetName = 'loop up'
                case 'loop down':
                    presetName = 'loop down'
                case 'loop left':
                    presetName = 'loop left'
                case 'loop right':
                    presetName = 'loop right'
          
        print(key_block.name + " as " + presetName)
        
        # Check if the blendshape clip already exists with the same name. If it does, and we set to combine, then add the mesh into the bind. 
        # Otherwise make a new clip
        if combine:
            if key_block.name in blend_shape_groups:
                print("Found " + key_block.name)
                bind = blend_shape_groups[key_block.name].binds.add()
                bind.mesh.mesh_object_name = mesh_object.name
                bind.index = key_block.name
            else:
                blend_shape_group = blend_shape_groups.add()
                blend_shape_group.name = key_block.name.strip()        
                blend_shape_group.preset_name = presetName
                     
                bind = blend_shape_group.binds.add()
                bind.mesh.mesh_object_name = mesh_object.name
                bind.index = key_block.name            
        else:
            blend_shape_group = blend_shape_groups.add()
            blend_shape_group.name = key_block.name.strip()        
            blend_shape_group.preset_name = presetName
                 
            bind = blend_shape_group.binds.add()
            bind.mesh.mesh_object_name = mesh_object.name
            bind.index = key_block.name