import re
import requests
import os
import sys

def find_all_imgur_links(text: str) -> list[tuple[str, str]]:
    """
    Find all Imgur links in the file\n
    Only match links that start with https://i.imgur.com/\n
    Return a list of tuples, where each tuple is (https://i.imgur.com/<code>, .<extension>)
    """
    imgur_pattern = r'(https:\/\/i\.imgur\.com\/\w+)(\.\w+)?'
    imgur_links = re.findall(imgur_pattern, text)
    return imgur_links

def replace_external_url_link_with_internal_wiki_link(url: str, path: str, text: str) -> str:
    """replace ![](<imgur link>) with the ![[<local image path>]]"""
    if path.startswith("http"):
        raise ValueError("should be a local path")
    
    # match "![text](path)" and "![](path)"
    pattern = r"!\[([^\]]*)\]\((url)\)|!\[\]\((url)\)"
    escaped_url = re.escape(url)
    pattern = pattern.replace("url", escaped_url)
    replaced_text = re.sub(pattern, f"![[{path}]]", text)
    return replaced_text

def dir_imgur_migrate(working_dir: str) -> None:
    """go over every file in the directory recursively"""
    print(f"About to process all .md files under {working_dir}")
    for root, _, files in os.walk(working_dir):
        for file in files:
            if file.endswith(".md"):
                file_imgur_migrate(root, file)
    print("All done!")

def file_imgur_migrate(working_dir: str, file_name: str) -> None:
    file_path = os.path.join(working_dir, file_name)
    print(f"Processing {file_path}...")

    with open(file_path, "r") as file:
        text = file.read()

    imgur_links = find_all_imgur_links(text)
    print(f"Found {len(imgur_links)} imgur links in {file_path}")
    if len(imgur_links) == 0:
        return
    
    # Download each image to the current directory
    print("Downloading images from imgur...")
    for i, link in enumerate(imgur_links):
        link_base, link_ext = link
        url = link_base + link_ext
        response = requests.get(url)
        
        # use a snake-case file name
        safe_file_name = file_name.replace('.md', '').lower().replace(' ', '-')
        ind = i + 1
        image_name = f'{safe_file_name}-{ind}{link_ext}'
        image_path = os.path.join(working_dir, image_name)
        
        # check if the image already exists
        while os.path.exists(image_path):
            ind += 1
            image_name = f'{safe_file_name}-{ind}{link_ext}'
            image_path = os.path.join(working_dir, image_name)
        replaced_text = replace_external_url_link_with_internal_wiki_link(url, image_name, text)
        
        # don't save image if no links are replaced
        if text == replaced_text:
            continue
        
        # save image
        text = replaced_text
        with open(image_path, 'wb') as f:
            f.write(response.content)
        
    print(f"All {len(imgur_links)} images downloaded to {working_dir}")
        
    # Write the modified text back to the file
    print("Replacing links...")
    with open(file_path, "w") as file:
        file.write(text)
    print("Done!")
    
def print_helper_info():
    print(
        "Usage:\n\
        python3 imgur_migrate.py\n\
        python3 imgur_migrate.py <directory>\n\
        python3 imgur_migrate.py <directory> <file_name>")

def main():
    if len(sys.argv) == 1:
        working_dir = "."
        dir_imgur_migrate(working_dir)
    elif len(sys.argv) == 2:
        if sys.argv[1] in ("--help", "-h"):
            print_helper_info()
            return
        working_dir = sys.argv[1]
        dir_imgur_migrate(working_dir)
    elif len(sys.argv) == 3:
        working_dir = sys.argv[1]
        file_name = sys.argv[2]
        file_imgur_migrate(working_dir, file_name)
    else:
        print_helper_info()

if __name__ == "__main__":
    main()