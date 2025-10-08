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

def isEnglish(s):
        """Check if text is English (following utf-8 encoding)
        """
        try:
            s.encode(encoding='utf-8').decode('ascii')
        except UnicodeDecodeError:
            return False
        else:
            return True

classes = (
    WM_OT_Generate,
    VRMTOOL_PG_SceneProperties,
    OBJECT_PT_VRMBlendshapeTool
)

def register():
    from . import ui
    ui.register()

def unregister():
    from . import ui
    ui.unregister()


if __name__ == "__main__":
    register()