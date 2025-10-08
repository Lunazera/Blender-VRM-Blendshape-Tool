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

def register():
    from . import ui
    ui.register()

def unregister():
    from . import ui
    ui.unregister()


if __name__ == "__main__":
    register()