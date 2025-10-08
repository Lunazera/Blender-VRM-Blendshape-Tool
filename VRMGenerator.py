# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####


bl_info = {
    "name": "VRM Blendshape Tool",
    "description": "Quickly generate blendshape proxies from shapekeys on your meshes",
    "author": "lunazera",
    "version": (0, 1),
    "blender": (3, 0, 0),
    "location": "3D View > Tools",
    "warning": "", # used for warning icon and text in addons panel
}

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


# ------------------------------------------------------------------------
#    Scene Properties
# ------------------------------------------------------------------------

class VRMTOOL_PG_SceneProperties(PropertyGroup):

    name_armature: StringProperty(
        name="Armature",
        description="Name of your Armature with your VRM metadata",
        default="",
        maxlen=1024,
        )
        
    name_mesh: StringProperty(
        name="Mesh",
        description="Name of your main mesh to add blendshapes from",
        default="",
        maxlen=1024,
        )
    
    list_mesh: StringProperty(
        name="List of Meshes",
        description="Comma separated list. Extra meshes to add blendshapes from",
        default="",
        maxlen=1024,
        )

    option_clear: BoolProperty(
        name="Clear Blendshapes?",
        description="Remove all blendshapes before generating",
        default = False
        )


# ------------------------------------------------------------------------
#    Operators
# ------------------------------------------------------------------------

def isEnglish(s):
        """Check if text is English (following utf-8 encoding)
        """
        try:
            s.encode(encoding='utf-8').decode('ascii')
        except UnicodeDecodeError:
            return False
        else:
            return True

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



class WM_OT_Generate(Operator):
    bl_label = "Generate Blendshapes"
    bl_idname = "wm.generate" 

    def execute(self, context):
        scene = context.scene
        vrmtool = scene.vrm_tool
        
        armature = vrmtool.name_armature
        mesh = vrmtool.name_mesh
        clear = vrmtool.option_clear
        meshList = vrmtool.list_mesh
        
        if armature and mesh:

            armature_object = bpy.data.objects[armature] 
            mesh_object = bpy.data.objects[mesh]
            
            add_vrm0_blendshape_proxy(armature_object, mesh_object, clear, True)
            
            if meshList:
                split_list_mesh = meshList.split(',')
                
                for m in split_list_mesh:
                    add_vrm0_blendshape_proxy(armature_object, bpy.data.objects[m], False, False, True)
            
            return {'FINISHED'}
        else:
            return {'CANCELLED'}



# ------------------------------------------------------------------------
#    Panel in Object Mode
# ------------------------------------------------------------------------

class OBJECT_PT_VRMBlendshapeTool(Panel):
    bl_label = "VRM Blendshape Tool"
    bl_idname = "OBJECT_PT_custom_panel"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "UI"
    bl_category = "Tools"
    bl_context = "objectmode"   

    @classmethod
    def poll(self,context):
        return context.object is not None

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False  # No animation.

        scene = context.scene
        vrmtool = scene.vrm_tool

        layout.label(text="""
        Generates your VRM model's blendshapes from your mesh shapekeys.
        """)
        layout.prop(vrmtool, "name_armature")
        layout.prop(vrmtool, "name_mesh")
        layout.prop(vrmtool, "option_clear")
        layout.label(text="Add additional meshes in a comma-separated list")
        layout.prop(vrmtool, "list_mesh")
        
        layout.separator(factor=3)
        layout.operator("wm.generate")
        layout.separator()


# ------------------------------------------------------------------------
#    Registration
# ------------------------------------------------------------------------

classes = (
    WM_OT_Generate,
    VRMTOOL_PG_SceneProperties,
    OBJECT_PT_VRMBlendshapeTool
)

def register():
    from bpy.utils import register_class
    for cls in classes:
        register_class(cls)

    bpy.types.Scene.vrm_tool = PointerProperty(type=VRMTOOL_PG_SceneProperties)

def unregister():
    from bpy.utils import unregister_class
    for cls in reversed(classes):
        unregister_class(cls)
    del bpy.types.Scene.vrm_tool


if __name__ == "__main__":
    register()
