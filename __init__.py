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

class ImportImagesOperator(bpy.types.Operator, AddObjectHelper):
    """Imports multiple images and creates image texture nodes in the active material."""
    bl_idname = "image.import"
    bl_label = "Import Images"

    files: bpy.props.CollectionProperty(type=bpy.types.OperatorFileListElement, options={'HIDDEN', 'SKIP_SAVE'})
    directory: bpy.props.StringProperty(maxlen=1024, subtype='FILE_PATH', options={'HIDDEN', 'SKIP_SAVE'})

    def execute(self, context):
        # # Get active material
        # material = bpy.context.active_object.active_material

        # # Get selected images
        # images = []
        # for file in self.files:
        #     images.append(load_image(file.name, self.directory, check_existing=True, force_reload=False))

        # # Create texture nodes for each image
        # node_spacing = 200  # Set the spacing between nodes
        # node_x_pos = 0      # Set the initial x position
        # node_y_pos = 0      # Set the initial y position
        # for image in images:
        #     texture_node = material.node_tree.nodes.new('ShaderNodeTexImage')
        #     texture_node.image = image
        #     texture_node.location = (node_x_pos, node_y_pos)  # Set the node location
        #     node_x_pos += node_spacing  # Update the x position for the next node

        node_group_name = "Pick Image"
        node_group = bpy.data.node_groups.new(node_group_name, 'ShaderNodeTree')

        # Create nodes
        math_node = node_group.nodes.new('ShaderNodeMath')
        mix_node1 = node_group.nodes.new('ShaderNodeMixRGB')
        mix_node2 = node_group.nodes.new('ShaderNodeMixRGB')

        # Set node positions
        math_node.location = (-300, 0)
        mix_node1.location = (0, 200)
        mix_node2.location = (0, -200)

        # # Link nodes
        # node_group.links.new(math_node.outputs['Value'], mix_node1.inputs['Fac'])
        # node_group.links.new(math_node.outputs['Value'], mix_node2.inputs['Fac'])

        # # Set input sockets
        # input_names = ['Index', 'Color1', 'Float1', 'Color2', 'Float2', 'Equal to']
        # input_links = [
        #     (math_node.inputs['Value'], 'Index'),
        #     (mix_node1.inputs['Color1'], 'Color1'),
        #     (mix_node2.inputs['Color1'], 'Float1'),
        #     (mix_node1.inputs['Color2'], 'Color2'),
        #     (mix_node2.inputs['Color2'], 'Float2'),
        #     (math_node.inputs['Threshold'], 'Equal to')
        # ]
        # for i in range(len(input_names)):
        #     input_socket_name = input_names[i]
        #     input_socket_link = input_links[i]
        #     input_socket_link[0].name = input_socket_name
        #     node_group.inputs.new('NodeSocket' + input_socket_link[0].type, input_socket_name)
        #     node_group.links.new(input_socket_link[0], input_socket_link[1])

        # # Set output sockets
        # output_names = ['Color', 'Alpha']
        # output_links = [
        #     (mix_node1.outputs['Color'], 'Color'),
        #     (mix_node2.outputs['Alpha'], 'Alpha')
        # ]
        # for i in range(len(output_names)):
        #     output_socket_name = output_names[i]
        #     output_socket_link = output_links[i]
        #     output_socket_link[0].name = output_socket_name
        #     node_group.outputs.new('NodeSocket' + output_socket_link[0].type, output_socket_name)
        #     node_group.links.new(output_socket_link[0], output_socket_link[1])

        return {'FINISHED'}


def register():
    bpy.utils.register_class(ImportImagesPanel)
    bpy.utils.register_class(ImportImagesOperator)

def unregister():
    bpy.utils.unregister_class(ImportImagesOperator)
    bpy.utils.unregister_class(ImportImagesPanel)

if __name__ == "__main__":
    register()
