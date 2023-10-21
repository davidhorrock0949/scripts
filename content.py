import json
import sys
import os

def start_html():
    return '<html><head></head><body>'

def end_html():
    return '</body></html>'

def display_files_as_html(data):
    """Generates an HTML table with file names and their sizes."""
    html_content = '<table border="1">\n'
    html_content += '  <tr><th>File Name</th><th>Size (bytes)</th></tr>\n'
    
    for file in data.get("files", []):
        html_content += f'  <tr><td>{file["name"]}</td><td>{file["size"]}</td></tr>\n'
    
    html_content += '</table>'
    return html_content

def print_tree_structure(data):
    """Generates directory tree structure as an HTML list."""
    all_paths = [file['name'] for file in data.get("files", [])]
    unique_directories = set()

    for path in all_paths:
        parts = path.split('/')
        for i in range(len(parts) - 1):  # -1 to exclude file itself
            unique_directories.add('/'.join(parts[:i+1]))

    dirs = sorted(unique_directories)
    return '<br>'.join(dirs)

def main():
    print(start_html())

    if len(sys.argv) != 3:
        print("<p>Usage: script_name.py <path_to_json_file> <0_or_1></p>")
        print(end_html())
        sys.exit(1)

    json_path = sys.argv[1].split('=', 1)[1]
    action = sys.argv[2].split('=', 1)[1]

    if not os.path.exists(json_path):
        print(f"<p>File {json_path} not found.</p>")
        print(end_html())
        sys.exit(1)

    with open(json_path, 'r') as file:
        data = json.load(file)

    if action == "1":
        tree_html = print_tree_structure(data)
        print(tree_html)
    elif action == "0":
        files_html = display_files_as_html(data)
        print(files_html)
    else:
        print("<p>The second argument should be either 0 or 1.</p>")

    print(end_html())

if __name__ == "__main__":
    main()
