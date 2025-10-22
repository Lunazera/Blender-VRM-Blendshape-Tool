import bpy

from .scripts.VRMGenerator import *

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
        name="Clear blendshapes?",
        description="Remove all blendshapes before generating",
        default = False
        )

    option_combine: BoolProperty(
        name="Combine existing?",
        description="If blendshape proxy already exists, binds mesh into it",
        default = False
        )
    option_english: BoolProperty(
        name="Skip non-english shapekeys",
        description="Ignores shapekeys with non-english characters, which sometimes has problems in other programs",
        default = False
        )
    option_mute: BoolProperty(
        name="Skip muted shapekeys",
        description="Ignores shapekeys if they are muted (unchecked)",
        default = False
        )
    option_presets: BoolProperty(
        name="Match to VRM Presets",
        description="Will set blendshape to VRM preset if the name matches (only for main Mesh)",
        default = False
        )
    option_vroid: BoolProperty(
        name="Match VRoid names",
        description="Check and match for typical VRoid prefixes from blendshapes",
        default = False
        )
    option_stripvroid: BoolProperty(
        name="Remove VRoid names",
        description="Removes VRoid prefixes entirely (will still leave a prefix like 'brow_' or 'eye_' to differentiate)",
        default = False
        )


# ------------------------------------------------------------------------
#    Operators
# ------------------------------------------------------------------------

class WM_OT_Generate(Operator):
    bl_label = "Generate Blendshapes"
    bl_idname = "wm.generate" 

    def execute(self, context):
        scene = context.scene
        vrmtool = scene.vrm_tool
        
        armature = vrmtool.name_armature.lstrip()
        mesh = vrmtool.name_mesh.lstrip()
        clear = vrmtool.option_clear
        meshList = vrmtool.list_mesh
        combine = vrmtool.option_combine
        checkEnglish = vrmtool.option_english
        checkMute = vrmtool.option_mute
        checkPresets = vrmtool.option_presets
        checkVRoid = vrmtool.option_vroid
        stripVRoid = vrmtool.option_stripvroid
        
        if armature and mesh:
            if armature in bpy.data.objects and mesh in bpy.data.objects:
                armature_object = bpy.data.objects[armature] 
                mesh_object = bpy.data.objects[mesh]
                VRM0_Generate_Blendshapes(armature_object, mesh_object, clear, checkPresets, combine, checkEnglish, checkMute, checkVRoid, stripVRoid)  # Generate blendshapes from main mesh
                
                if meshList:
                    split_list_mesh = meshList.split(',') # Create list from comma-separated list string, removing leading whitespaces
                    for m in split_list_mesh:
                        if m.lstrip() in bpy.data.objects:
                            VRM0_Generate_Blendshapes(armature_object, bpy.data.objects[m.lstrip()], False, False, combine, checkEnglish, checkMute, checkVRoid, stripVRoid)  # generate blendshapes from additional meshes
            
            return {'FINISHED'}
        else:
            return {'CANCELLED'}



# ------------------------------------------------------------------------
#    Panel in Object Mode
# ------------------------------------------------------------------------

class OBJECT_PT_VRMBlendshapeTool(Panel):
    bl_label = "VRM Blendshape Tool"
    bl_idname = "OBJECT_PT_LZTools_VRMBlendshapeTool"
    bl_space_type = "VIEW_3D"   
    bl_region_type = "UI"
    bl_category = "LZTools"
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

        layout.label(text="Name of VRM Armature and main Mesh")
        layout.prop(vrmtool, "name_armature")
        layout.prop(vrmtool, "name_mesh")
        layout.prop(vrmtool, "option_clear")
        layout.prop(vrmtool, "option_presets")

        layout.separator(factor=3)
        layout.label(text="Add extra meshes in comma-separated list")
        layout.prop(vrmtool, "list_mesh")
        

        layout.separator(factor=1)
        layout.label(text="Additional options")
        layout.prop(vrmtool, "option_combine")
        layout.prop(vrmtool, "option_mute")
        layout.prop(vrmtool, "option_english")
        layout.prop(vrmtool, "option_vroid")
        layout.prop(vrmtool, "option_stripvroid")

        
        layout.separator(factor=3)
        layout.operator("wm.generate")
        layout.separator()


##################################

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