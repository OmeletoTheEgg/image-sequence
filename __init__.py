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

def create_pick_image_node_group():
        # Create a node group
        node_group = bpy.data.node_groups.new("Pick Image", 'ShaderNodeTree')

        # Create nodes
        group_input_node = node_group.nodes.new("NodeGroupInput")
        group_output_node = node_group.nodes.new("NodeGroupOutput")
        math_node = node_group.nodes.new('ShaderNodeMath')
        math_node.operation = 'GREATER_THAN'
        mix_node1 = node_group.nodes.new('ShaderNodeMixRGB')
        mix_node2 = node_group.nodes.new('ShaderNodeMixRGB')

        # Set node positions
        group_input_node.location = (-600, 0)
        group_output_node.location = (300, 0)
        math_node.location = (-300, 0)
        mix_node1.location = (0, 200)
        mix_node2.location = (0, -200)

        # Link nodes
        node_group.links.new(math_node.outputs['Value'], mix_node1.inputs['Fac'])
        node_group.links.new(math_node.outputs['Value'], mix_node2.inputs['Fac'])

        # Create inputs and outputs
        node_group.inputs.new('NodeSocketFloat', 'Index')
        node_group.inputs.new('NodeSocketColor', 'Color1')
        node_group.inputs.new('NodeSocketFloat', 'Float1')
        node_group.inputs.new('NodeSocketColor', 'Color2')
        node_group.inputs.new('NodeSocketFloat', 'Float2')
        node_group.inputs.new('NodeSocketFloat', 'Equal to')
        node_group.outputs.new('NodeSocketColor', 'Color')
        node_group.outputs.new('NodeSocketFloat', 'Alpha')

        # Link inputs
        node_group.links.new(group_input_node.outputs['Index'], math_node.inputs[0])
        node_group.links.new(group_input_node.outputs['Color1'], mix_node1.inputs['Color1'])
        node_group.links.new(group_input_node.outputs['Float1'], mix_node2.inputs['Color1'])
        node_group.links.new(group_input_node.outputs['Color2'], mix_node1.inputs['Color2'])
        node_group.links.new(group_input_node.outputs['Float2'], mix_node2.inputs['Color2'])
        node_group.links.new(group_input_node.outputs['Equal to'], math_node.inputs[1])

        node_group.links.new(mix_node1.outputs['Color'], group_output_node.inputs['Color'])
        node_group.links.new(mix_node2.outputs['Color'], group_output_node.inputs['Alpha'])

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
        # Get active material
        material = bpy.context.active_object.active_material
        
        # Get selected images
        images = []
        for file in self.files:
            images.append(load_image(file.name, self.directory, check_existing=True, force_reload=False))

        # Create texture nodes for each image
        node_spacing = 500  
        node_x_pos = 0      
        node_y_pos = 0      
        for image in images:
            texture_node = material.node_tree.nodes.new('ShaderNodeTexImage')
            texture_node.image = image
            texture_node.location = (node_x_pos, node_y_pos)  # Set the node location
            node_x_pos += node_spacing  # Update the x position for the next node

        if 'Pick Image' not in bpy.data.node_groups:
            create_pick_image_node_group()

        return {'FINISHED'}

    



def register():
    bpy.utils.register_class(ImportImagesPanel)
    bpy.utils.register_class(ImportImagesOperator)

def unregister():
    bpy.utils.unregister_class(ImportImagesOperator)
    bpy.utils.unregister_class(ImportImagesPanel)

if __name__ == "__main__":
    register()
