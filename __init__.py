import bpy
from bpy_extras.object_utils import AddObjectHelper
from bpy_extras.io_utils import ImportHelper

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

class ImportImagesOperator(bpy.types.Operator, AddObjectHelper, ImportHelper):
    """Imports multiple images and creates image texture nodes in the active material."""
    bl_idname = "image.import"
    bl_label = "Import Images"

    files: bpy.props.CollectionProperty(type=bpy.types.OperatorFileListElement, options={'HIDDEN', 'SKIP_SAVE'})
    directory: bpy.props.StringProperty(maxlen=1024, subtype='FILE_PATH', options={'HIDDEN', 'SKIP_SAVE'})

    def execute(self, context):
        
        if 'Pick Image' not in bpy.data.node_groups:
            create_pick_image_node_group()

        # Get selected images
        images = []
        for file in self.files:
            images.append(load_image(file.name, self.directory, check_existing=True, force_reload=False))

        create_image_sequence_node_group(images)

        return {'FINISHED'}

def create_pick_image_node_group():
    # Create a node group
    pick_node_group = bpy.data.node_groups.new("Pick Image", 'ShaderNodeTree')

    # Create nodes
    group_input_node = pick_node_group.nodes.new("NodeGroupInput")
    group_output_node = pick_node_group.nodes.new("NodeGroupOutput")
    math_node = pick_node_group.nodes.new('ShaderNodeMath')
    math_node.operation = 'GREATER_THAN'
    mix_node1 = pick_node_group.nodes.new('ShaderNodeMixRGB')
    mix_node2 = pick_node_group.nodes.new('ShaderNodeMixRGB')

    # Set node positions
    group_input_node.location = (-600, 0)
    group_output_node.location = (300, 0)
    math_node.location = (-300, 0)
    mix_node1.location = (0, 200)
    mix_node2.location = (0, -200)

    # Link nodes
    pick_node_group.links.new(math_node.outputs['Value'], mix_node1.inputs['Fac'])
    pick_node_group.links.new(math_node.outputs['Value'], mix_node2.inputs['Fac'])

    # Create inputs and outputs
    pick_node_group.inputs.new('NodeSocketFloat', 'Index')
    pick_node_group.inputs.new('NodeSocketColor', 'Color1')
    pick_node_group.inputs.new('NodeSocketFloat', 'Float1')
    pick_node_group.inputs.new('NodeSocketColor', 'Color2')
    pick_node_group.inputs.new('NodeSocketFloat', 'Float2')
    pick_node_group.inputs.new('NodeSocketFloat', 'Equal to')
    pick_node_group.outputs.new('NodeSocketColor', 'Color')
    pick_node_group.outputs.new('NodeSocketFloat', 'Alpha')

    # Link inputs
    pick_node_group.links.new(group_input_node.outputs['Index'], math_node.inputs[0])
    pick_node_group.links.new(group_input_node.outputs['Color1'], mix_node1.inputs['Color1'])
    pick_node_group.links.new(group_input_node.outputs['Float1'], mix_node2.inputs['Color1'])
    pick_node_group.links.new(group_input_node.outputs['Color2'], mix_node1.inputs['Color2'])
    pick_node_group.links.new(group_input_node.outputs['Float2'], mix_node2.inputs['Color2'])
    pick_node_group.links.new(group_input_node.outputs['Equal to'], math_node.inputs[1])

    pick_node_group.links.new(mix_node1.outputs['Color'], group_output_node.inputs['Color'])
    pick_node_group.links.new(mix_node2.outputs['Color'], group_output_node.inputs['Alpha'])

def create_image_sequence_node_group(images):
    # Create node group img_seq_group
    img_seq_group = bpy.data.node_groups.new("Image Sequence Group", 'ShaderNodeTree')
    img_seq_group.inputs.new('NodeSocketFloat', 'Frame')
    img_seq_group.outputs.new('NodeSocketColor', 'Color')
    img_seq_group.outputs.new('NodeSocketFloat', 'Alpha')

    # Set the location related things
    node_spacing = 300  
    node_x_pos = 0
    node_x_origin = 0
    node_y_pos = 0
    node_y_offset = 0
    node_x_wrap_max = 9000
    index = 0
    prev_pick_node = None

    # Create input, output, and ceil nodes
    group_input_node = img_seq_group.nodes.new("NodeGroupInput")
    group_output_node = img_seq_group.nodes.new("NodeGroupOutput")
    ceil_node = img_seq_group.nodes.new('ShaderNodeMath')
    ceil_node.operation = 'CEIL'

    # Define their location
    group_input_node.location = (node_x_pos, node_y_pos + 600)
    ceil_node.location = (node_x_pos + 300, node_y_pos + 600)
    group_output_node.location = (node_x_pos + 900, node_y_pos + 600)

    img_seq_group.links.new(group_input_node.outputs['Frame'], ceil_node.inputs[0])

    # Generate Pick Images and Image Textures per images
    for image in images:
        texture_node = img_seq_group.nodes.new('ShaderNodeTexImage')
        texture_node.image = image
        texture_node.interpolation = 'Closest'
        texture_node.location = (node_x_pos, node_y_pos - node_y_offset)

        pick_node = img_seq_group.nodes.new("ShaderNodeGroup")
        pick_node.node_tree = bpy.data.node_groups['Pick Image']
        pick_node.location = (node_x_pos + 100, node_y_pos + 300 - node_y_offset)
        pick_node.inputs[5].default_value = index

        # Wrap
        if node_x_pos >= node_x_wrap_max:
            node_x_pos = node_x_origin
            node_y_offset += 600
        node_x_pos += node_spacing

        # Link Pick Images and Image Textures
        img_seq_group.links.new(texture_node.outputs['Color'], pick_node.inputs['Color2'])
        img_seq_group.links.new(texture_node.outputs['Alpha'], pick_node.inputs['Float2'])

        img_seq_group.links.new(ceil_node.outputs['Value'], pick_node.inputs['Index'])

        if prev_pick_node is not None:
            img_seq_group.links.new(prev_pick_node.outputs['Color'], pick_node.inputs['Color1'])
            img_seq_group.links.new(prev_pick_node.outputs['Alpha'], pick_node.inputs['Float1'])
        
        prev_pick_node = pick_node
        index += 1

    img_seq_group.links.new(prev_pick_node.outputs['Color'], group_output_node.inputs['Color'])
    img_seq_group.links.new(prev_pick_node.outputs['Alpha'], group_output_node.inputs['Alpha'])

    bpy.context.active_object.active_material.node_tree.nodes.new("ShaderNodeGroup").node_tree = bpy.data.node_groups['Image Sequence Group']

def register():
    bpy.utils.register_class(ImportImagesPanel)
    bpy.utils.register_class(ImportImagesOperator)

def unregister():
    bpy.utils.unregister_class(ImportImagesOperator)
    bpy.utils.unregister_class(ImportImagesPanel)

if __name__ == "__main__":
    register()
