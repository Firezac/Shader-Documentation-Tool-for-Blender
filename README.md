🌟 Blender Shader Documentation Tool 🌟

Tired of getting lost in your complex Blender shader node trees? Wish you had a clear, hierarchical overview of how your materials are built, node by node? Look no further! The Blender Shader Documentation Tool is here to save your day (and your sanity)! 🚀

📝 Synopsis

This Blender add-on is a game-changer for anyone working with intricate shader networks. It provides a simple yet powerful way to export a comprehensive, human-readable, pseudo-code representation of your Blender material's node tree into a .txt file. Perfect for quick reference, collaborative projects, or simply understanding the logic behind complex shaders without having to navigate the node editor. Get instant clarity on your material setups!

✨ Features

Easy Access: Integrates seamlessly into Blender's N-panel (Toolshelf) under its own "Shader Doc" tab.

Shader Selection: A convenient dropdown menu lists all materials in your Blender file, letting you pick exactly which shader you want to document.

Custom Output Path: Choose where your documentation file will be saved with a simple file path selector.

Clear Hierarchy: Generates a .txt file with a visually intuitive, indented structure, showing parent-child relationships, node types, and connection details. No more squinting at tiny node thumbnails!

Detailed Information: Displays node names, types, connected inputs, and even default values for unconnected inputs.

Node Group Support: Recursively dives into Node Groups to document their internal structure!

🛠️ Installation

Getting this awesome tool up and running in Blender is super easy!

Download the Add-on:

Copy the entire Python code from the blender-shader-doc-tool.py file (which you have from our conversation).

Open Blender.

Go to Text Editor workspace.

Click New to create a new text file.

Paste the copied Python code into this new text file.

Go to Text menu -> Save As... and save the file somewhere you can easily find it (e.g., your Desktop) as shader_documentation_tool.py.

Install in Blender:

In Blender, go to Edit -> Preferences.

Navigate to the Add-ons tab.

Click the Install... button in the top right corner.

Browse to the shader_documentation_tool.py file you just saved, select it, and click Install Add-on.

Activate the Add-on:

After installation, the add-on should appear in your add-ons list. Search for "Shader Documentation Tool".

Crucially, check the box next to "Shader Documentation Tool" to enable it.

You're Ready! 🎉 Close the Preferences window.

🚀 How to Use

Open the N-Panel: In any 3D Viewport in Blender, press the N key to open the N-panel (also known as the Toolshelf) on the right side of the screen.

Find the Tab: You'll now see a new tab labeled "Shader Doc". Click on it!

Select Your Shader:

Under "Select Shader", use the dropdown menu to choose the specific material (shader) whose node tree you want to document.

Choose Output Path:

Next to "Output Path", click the folder icon to browse to your desired directory and specify a filename (e.g., my_awesome_material_doc.txt).

Generate Documentation:

Click the "Start" button.

That's it! A .txt file containing your shader's beautifully formatted documentation will be generated at the specified location. Enjoy the clarity! 📄✨

💖 Contributing

Got ideas for improvements? Found a bug? Feel free to contribute! This tool is open-source and loves community input.

Happy Blending and Happy Documenting!
