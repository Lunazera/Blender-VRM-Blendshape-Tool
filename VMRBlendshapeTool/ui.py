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


# ------------------------------------------------------------------------
#    Operators
# ------------------------------------------------------------------------

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
        combine = vrmtool.option_combine
        
        if armature and mesh:

            armature_object = bpy.data.objects[armature] 
            mesh_object = bpy.data.objects[mesh]
            
            VRM0_Generate_Blendshapes(armature_object, mesh_object, clear, True, combine)
            
            if meshList:

                split_list_mesh = meshList.split(',') # Create list from comma-separated list string, removing leading whitespaces
                for m in split_list_mesh:
                    if m.lstrip() in bpy.data.objects:
                        VRM0_Generate_Blendshapes(armature_object, bpy.data.objects[m.lstrip()], False, False, combine)
            
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

        layout.separator(factor=3)
        layout.label(text="Additional meshes in comma-separated list")
        layout.prop(vrmtool, "list_mesh")
        layout.prop(vrmtool, "option_combine")
        
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