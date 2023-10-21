import os
import json
import csv
import sys
import urllib.parse

def format_size(size):
    """Converts bytes to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024

def truncate(data, length=50):
    """Truncate a string to a specified length."""
    return (data[:length] + '..') if len(data) > length else data

def process_json_files(limit=None, sort_by_size=False, csv_output=None, html_output=None):
    all_data = []
    
    for root, dirs, files in os.walk("."):
        for file in files:
            if file.endswith(".json"):
                with open(os.path.join(root, file), 'r') as f:
                    try:
                        data = json.load(f)
                        if all(key in data for key in ["files_count", "files_size", "name"]):
                            path = os.path.abspath(os.path.join(root, file))
                            all_data.append([truncate(data["name"]), data["files_count"], data["files_size"], path])
                    except json.JSONDecodeError:
                        pass
    
    if sort_by_size:
        all_data.sort(key=lambda x: x[2], reverse=True)

    for item in all_data:
        item[2] = format_size(item[2])
    
    if limit:
        all_data = all_data[:limit]

    if csv_output:
        with open(csv_output, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(["Name", "Files Count", "Files Size", "Path"])
            writer.writerows(all_data)
    elif html_output:
        with open(html_output, 'w') as f:
            f.write("<html><body><table border='1'>")
            f.write("<tr><th>Name</th><th>Files Count</th><th>Files Size</th><th>Path</th></tr>")
            for row in all_data:
                encoded_filepath = urllib.parse.quote(row[3])
                f.write(f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td><a href=\"/run/content?path={encoded_filepath}&format=0\">{row[3]}</a></td></tr>")
            f.write("</table></body></html>")
    else:
        for row in all_data:
            print(f"{row[0]:<52} {row[1]:<12} {row[2]:<15} {row[3]}")

def display_help():
    print("""
Usage: 
  -csv [filename]   : Outputs data to a CSV file named [filename].
  -html [filename]  : Outputs data in HTML format to a file named [filename].
  -s                : Sorts output by file size.
  -l [limit]        : Limits the number of results to [limit].
  -h                : Displays this help message.
""")

if __name__ == "__main__":
    csv_file = None
    html_file = None
    limit = None
    sort_flag = False

    for i, arg in enumerate(sys.argv[1:]):
        if arg == "-csv":
            csv_file = sys.argv[i+2]
        elif arg == "-html":
            html_file = sys.argv[i+2]
        elif arg == "-s":
            sort_flag = True
        elif arg == "-l":
            limit = int(sys.argv[i+2])
        elif arg == "-h":
            display_help()
            sys.exit(0)

    process_json_files(limit, sort_flag, csv_file, html_file)
