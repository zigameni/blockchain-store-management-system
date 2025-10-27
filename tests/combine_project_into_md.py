import os

def create_file_tree(startpath):
    """
    Generates a string representation of the file tree, excluding ignored directories.
    """
    tree_str = ""
    ignore_dirs = ['.git', '__pycache__', '.venv', 'node_modules', 'output', '.idea', 'my_tests']
    
    for root, dirs, files in os.walk(startpath):
        # Skip ignored directories
        dirs[:] = [d for d in dirs if d not in ignore_dirs]
        
        # Calculate current level to indent correctly
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * level
        tree_str += f"{indent}{os.path.basename(root)}/\n"
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            tree_str += f"{subindent}{f}\n"
    return tree_str

def bundle_code_to_markdown(project_root_dir, output_md_file):
    """
    Traverses the project directory, creates a file tree,
    and bundles all code content into a single Markdown file.
    """
    print(f"Starting to bundle code from: {project_root_dir}")

    if not output_md_file.endswith(".md"):
        output_md_file += ".md"

    # --- Generate the File Tree ---
    file_tree = create_file_tree(project_root_dir)
    print("File tree generated.")

    # --- Collect Code Content ---
    code_content = []
    ignore_extensions = ['.pyc', '.log', '.tmp', '.DS_Store', '.bin', '.abi']
    ignore_dirs = ['.git', '__pycache__', '.venv', 'node_modules', 'output', '.idea', 'my_tests']
    ignore_files = [os.path.basename(output_md_file), 'generate_key_store.py', 'test_blockchain.py', 'compile_contract.py', '.gitignore', 'temp.csv', 'test_main.py']

    # Directories to skip content, include only structure
    structure_only_dirs = ['etherwallet-v3.21.06']

    # Binary / image / media files
    binary_extensions = [
        '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.ico',
        '.svg', '.webp', '.mp3', '.wav', '.mp4', '.avi', '.mov',
        '.pdf', '.zip', '.tar', '.gz'
    ]

    extension_to_lang = {
        '.py': 'python', '.js': 'javascript', '.html': 'html', '.css': 'css',
        '.java': 'java', '.c': 'c', '.cpp': 'cpp', '.go': 'go',
        '.ts': 'typescript', '.jsx': 'jsx', '.tsx': 'tsx', '.json': 'json',
        '.yaml': 'yaml', '.yml': 'yaml', '.xml': 'xml', '.sh': 'bash',
        '.rb': 'ruby', '.php': 'php', '.swift': 'swift', '.kt': 'kotlin',
        '.rs': 'rust', '.vue': 'vue', '.md': 'markdown', '.sql': 'sql',
        '.dockerfile': 'dockerfile', '.sol': 'solidity', '.ps1': 'powershell',
        '.abi': 'json',
    }

    for root, dirs, files in os.walk(project_root_dir):
        dirs[:] = [d for d in dirs if d not in ignore_dirs]

        # If inside "structure-only" directory, just record names
        if any(struct_dir in root for struct_dir in structure_only_dirs):
            relative_root = os.path.relpath(root, project_root_dir)
            code_content.append(f"### Folder: `{relative_root}`\n\n")
            for file_name in files:
                code_content.append(f"- {file_name}\n")
            code_content.append("\n")
            continue

        for file_name in files:
            file_path = os.path.join(root, file_name)

            if file_name in ignore_files or any(file_name.endswith(ext) for ext in ignore_extensions):
                continue

            file_ext = os.path.splitext(file_name)[1].lower()

            # Handle binary/image files separately
            if file_ext in binary_extensions:
                relative_path = os.path.relpath(file_path, project_root_dir)
                code_content.append(f"## File: `{relative_path}`\n\n")
                code_content.append(f"*Binary/Image file: `{file_name}` (content not included)*\n\n")
                print(f"Listed binary file: {relative_path}")
                continue

            # Determine language
            if not file_ext and '.' not in file_name:
                lang = 'dockerfile' if file_name.lower() == 'dockerfile' else ''
            else:
                lang = extension_to_lang.get(file_ext, '')

            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                relative_path = os.path.relpath(file_path, project_root_dir)
                code_content.append(f"## File: `{relative_path}`\n\n")
                code_content.append(f"```{lang}\n{content}\n```\n\n")
                print(f"Added content from: {relative_path}")
            except Exception as e:
                print(f"Could not read file {file_path}: {e}")

    # --- Write to Markdown File ---
    try:
        with open(output_md_file, 'w', encoding='utf-8') as md_file:
            md_file.write(f"# Project Code Bundle\n\n")
            md_file.write("This document contains a file tree and the bundled code from the project.\n\n")

            md_file.write("## File Tree\n\n")
            md_file.write("```\n")
            md_file.write(file_tree)
            md_file.write("```\n\n")

            md_file.write("## Code Content\n\n")
            for block in code_content:
                md_file.write(block)
        print(f"Successfully created {output_md_file}")
    except Exception as e:
        print(f"Error writing to file {output_md_file}: {e}")

# --- Configuration ---
PROJECT_ROOT = './IEP_Projekat'
OUTPUT_FILENAME = 'project_bundle_IEP.md'

if __name__ == "__main__":
    bundle_code_to_markdown(PROJECT_ROOT, OUTPUT_FILENAME)