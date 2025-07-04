bl_info = {
    "name": "Shader Documentation Tool",
    "description": "Document your shaders on a .txt file.",
    "author": "Erick Firezac",
    "version": (1,0),
    "blender": (4, 4, 1),
    "location": "VIEW3D > Sidebar",
    "wiki_url": "",
    "category": "Shader"   
}

import bpy
import os

# --- 1. Panel Definition ---
class SHADER_PT_DocumentationPanel(bpy.types.Panel):
    """Creates a Panel in the N-panel (Toolshelf)"""
    bl_label = "Shader Documentation Tool"
    bl_idname = "SHADER_PT_documentation_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Shader Doc' # This will be the name of the tab in the N-panel

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Select Shader Dropdown
        row = layout.row()
        row.label(text="Select Shader:")
        # Use a pointer property to link to the selected material
        row.prop(scene, "shader_doc_material", text="")

        # Path Selection
        row = layout.row()
        row.label(text="Output Path:")
        row.prop(scene, "shader_doc_filepath", text="")

        # Start Button
        row = layout.row()
        # The button calls our custom operator
        row.operator("shader.document_shader", text="Start")

# --- 2. Operator Definition ---
class SHADER_OT_DocumentShader(bpy.types.Operator):
    """Documents the selected shader's node tree"""
    bl_idname = "shader.document_shader"
    bl_label = "Document Shader"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        material = scene.shader_doc_material
        filepath = scene.shader_doc_filepath

        # --- Validation ---
        if not material:
            self.report({'ERROR'}, "No shader selected. Please select a material from the dropdown.")
            return {'CANCELLED'}

        if not material.use_nodes:
            self.report({'ERROR'}, f"Selected material '{material.name}' does not use nodes.")
            return {'CANCELLED'}

        if not filepath:
            self.report({'ERROR'}, "No output path specified. Please choose a directory and filename.")
            return {'CANCELLED'}

        # Ensure the directory exists
        output_dir = os.path.dirname(filepath)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except OSError as e:
                self.report({'ERROR'}, f"Could not create directory '{output_dir}': {e}")
                return {'CANCELLED'}

        # --- Core Logic: Traverse Node Tree and Generate Documentation ---
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"--- Shader Documentation for: {material.name} ---\n\n")

                # Find the 'Material Output' node or the first output node if it's a node group
                output_node = None
                for node in material.node_tree.nodes:
                    if node.bl_idname == 'ShaderNodeOutputMaterial':
                        output_node = node
                        break
                # Fallback for node groups or other custom setups if Material Output isn't found
                if not output_node and material.node_tree.nodes:
                    # Try to find any node that doesn't have outputs linked to other nodes within the tree
                    # This is a heuristic and might not always be perfect for complex setups
                    potential_output_nodes = []
                    for node in material.node_tree.nodes:
                        is_output = True
                        for output_socket in node.outputs:
                            if output_socket.is_linked:
                                for link in output_socket.links:
                                    # Check if the link goes to another node in the same tree
                                    if link.to_node in material.node_tree.nodes:
                                        is_output = False
                                        break
                                if not is_output:
                                    break
                        if is_output:
                            potential_output_nodes.append(node)
                    
                    # Prioritize nodes with 'Output' in their name or type, or just pick the first one
                    if potential_output_nodes:
                        output_node = potential_output_nodes[0]
                        for node in potential_output_nodes:
                            if 'Output' in node.name or 'Output' in node.bl_idname:
                                output_node = node
                                break


                if not output_node:
                    self.report({'ERROR'}, f"Could not find a suitable output node for material '{material.name}'.")
                    return {'CANCELLED'}

                # Start the recursive documentation from the output node
                # Use a set to keep track of processed nodes to prevent infinite loops in cyclic graphs
                self.document_node_recursive(f, output_node, 0, processed_nodes=set(), is_linked_child=False)

            self.report({'INFO'}, f"Shader documentation saved to: {filepath}")
            return {'FINISHED'}

        except Exception as e:
            self.report({'ERROR'}, f"An error occurred during documentation: {e}")
            return {'CANCELLED'}

    def document_node_recursive(self, file_handle, node, indent_level, processed_nodes, is_linked_child):
        node_type = node.bl_idname
        node_name = node.name

        # --- Indentation Logic ---
        # Each level of indentation is 4 characters wide.
        # The vertical bar '|' appears at the first character of each 4-char block
        # for all preceding levels, and for the current level's branch.

        INDENT_LEVEL_WIDTH = 4 # Total width of one indentation level
        VERTICAL_BAR_AND_SPACES = "|   " # '|' followed by 3 spaces to make up 4 chars
        BRANCH_NODE_CHAR = "|_"
        BRANCH_INPUT_CHAR = "|-"
        DETAIL_SPACES = "    " # 4 spaces for details/attributes alignment

        # Calculate the base indentation string for the current level's vertical lines
        # This string will be prepended to all lines at this indent_level
        base_vertical_indent = VERTICAL_BAR_AND_SPACES * indent_level

        # Calculate prefix for the current node's line (e.g., "|_NodeName" or "NodeName" for root)
        node_line_prefix = ""
        if indent_level == 0:
            node_line_prefix = "" # Root node has no prefix
        else:
            # If this node is a child of a linked input, it needs an extra indent for its branch
            if is_linked_child:
                # The vertical line for this level is already included in base_vertical_indent
                # We just need to add the branch character after the base indent.
                node_line_prefix = base_vertical_indent + BRANCH_NODE_CHAR
            else:
                # For regular children (e.g., from group outputs), use the previous indent_level's vertical line
                # then add the branch character for the current level.
                node_line_prefix = (VERTICAL_BAR_AND_SPACES * (indent_level - 1)) + BRANCH_NODE_CHAR

        # Calculate prefix for inputs of the current node
        input_line_prefix = base_vertical_indent + BRANCH_INPUT_CHAR

        # Calculate prefix for details/attributes of the current node
        detail_line_prefix = base_vertical_indent + DETAIL_SPACES


        is_already_processed = node in processed_nodes
        if not is_already_processed:
            processed_nodes.add(node)

            file_handle.write(f"{node_line_prefix}{node_name} ({node_type})\n")

            # Handle specific node types for properties that are NOT inputs
            if node_type == 'ShaderNodeTexImage' and node.image:
                file_handle.write(f"{detail_line_prefix}Image: \"{os.path.basename(node.image.filepath)}\"\n")
            elif node_type == 'ShaderNodeMath':
                file_handle.write(f"{detail_line_prefix}Operation: {node.operation.replace('_', ' ').title()}\n")
            elif node_type == 'ShaderNodeMixRGB':
                file_handle.write(f"{detail_line_prefix}Blend Type: {node.blend_type.replace('_', ' ').title()}\n")
            elif node_type == 'ShaderNodeGroup': # Handle Node Groups
                file_handle.write(f"{detail_line_prefix}--- Group Contents ---\n")
                if node.node_tree:
                    group_output_node = None
                    for n_in_group in node.node_tree.nodes:
                        if n_in_group.bl_idname == 'NodeGroupOutput':
                            group_output_node = n_in_group
                            break
                    if group_output_node:
                        # Recursive call for group contents, not a linked child
                        self.document_node_recursive(file_handle, group_output_node, indent_level + 1, set(), is_linked_child=False)
                    else:
                        file_handle.write(f"{detail_line_prefix}(No output node found in group)\n")
                file_handle.write(f"{detail_line_prefix}--- End Group Contents ---\n")

            # Document inputs
            for input_socket in node.inputs:
                input_name = input_socket.name
                file_handle.write(f"{input_line_prefix}{input_name}: ")

                if input_socket.is_linked:
                    from_node = input_socket.links[0].from_node
                    from_socket_name = input_socket.links[0].from_socket.name
                    file_handle.write(f"Connected from '{from_node.name}' ({from_socket_name})\n")
                    # Recursive call to document the connected node, marking it as a linked child
                    self.document_node_recursive(file_handle, from_node, indent_level + 1, processed_nodes, is_linked_child=True)
                else:
                    if hasattr(input_socket, 'default_value'):
                        default_val = input_socket.default_value
                        if isinstance(default_val, (float, int)):
                            file_handle.write(f"Value: {default_val:.4f}\n")
                        elif hasattr(default_val, '__len__') and len(default_val) in (3, 4): # Color or Vector
                            file_handle.write(f"Value: ({', '.join(f'{v:.4f}' for v in default_val)})\n")
                        else:
                            file_handle.write(f"Value: {default_val}\n")
                    else:
                        file_handle.write("Not Connected\n")
        else:
            # If the node was already processed, just print its line to show the connection,
            # but don't recurse into its children again.
            # Use the same current_node_prefix calculation as if it were a new node at this level.
            # This ensures consistent alignment for "ALREADY DOCUMENTED ABOVE" lines.
            node_line_prefix_for_processed = ""
            if indent_level == 0:
                node_line_prefix_for_processed = ""
            elif is_linked_child:
                node_line_prefix_for_processed = base_vertical_indent + BRANCH_NODE_CHAR
            else:
                node_line_prefix_for_processed = (VERTICAL_BAR_AND_SPACES * (indent_level - 1)) + BRANCH_NODE_CHAR
            
            file_handle.write(f"{node_line_prefix_for_processed}{node_name} (ALREADY DOCUMENTED ABOVE)\n")


# --- 3. Registration ---
classes = (
    SHADER_PT_DocumentationPanel,
    SHADER_OT_DocumentShader,
)

def register():
    # Register custom properties to the Scene
    bpy.types.Scene.shader_doc_material = bpy.props.PointerProperty(
        type=bpy.types.Material,
        name="Material",
        description="Select the material (shader) to document"
    )
    bpy.types.Scene.shader_doc_filepath = bpy.props.StringProperty(
        name="File Path",
        subtype='FILE_PATH',
        description="Path to save the shader documentation (.txt file)"
    )

    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    
    # Delete custom properties
    del bpy.types.Scene.shader_doc_material
    del bpy.types.Scene.shader_doc_filepath

if __name__ == "__main__":
    register()

