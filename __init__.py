import bpy
from bpy_extras.object_utils import AddObjectHelper


from bpy_extras.image_utils import load_image

bl_info = {
    "name": "Image Importer",
    "author": "Your Name",
    "version": (1, 0),
    "blender": (2, 80, 0),
    "location": "View3D > Sidebar > Image Importer",
    "description": "Imports multiple images and creates image texture nodes in the active material.",
    "category": "Import-Export"
}

class ImportImagesPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Image Importer"
    bl_idname = "OBJECT_PT_image_importer"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Image Importer"

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.operator("image.import", text="Import Images")

class ImportImagesOperator(bpy.types.Operator, ImportHelper, AddObjectHelper):
    """Imports multiple images and creates image texture nodes in the active material."""
    bl_idname = "image.import"
    bl_label = "Import Images"

    files: bpy.props.CollectionProperty(type=bpy.types.OperatorFileListElement, options={'HIDDEN', 'SKIP_SAVE'})
    directory: bpy.props.StringProperty(maxlen=1024, subtype='FILE_PATH', options={'HIDDEN', 'SKIP_SAVE'})

    def execute(self, context):
        # Get active material
        material = bpy.context.active_object.active_material

        # Get selected images
        images = []
        for file in self.files:
            images.append(load_image(file.name, self.directory, check_existing=True, force_reload=False))

        for image in images:
            texture_node = material.node_tree.nodes.new('ShaderNodeTexImage')
            texture_node.image = image

        return {'FINISHED'}

def register():
    bpy.utils.register_class(ImportImagesPanel)
    bpy.utils.register_class(ImportImagesOperator)

def unregister():
    bpy.utils.unregister_class(ImportImagesOperator)
    bpy.utils.unregister_class(ImportImagesPanel)

if __name__ == "__main__":
    register()
