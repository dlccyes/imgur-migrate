from re import findall, escape, sub
from requests import get as r_get
from os.path import join, exists
from os import walk
from argparse import ArgumentParser

available_modes = {"wikilink", "mdlink"}
available_modes_text = " or ".join(available_modes)

def find_all_imgur_links(text: str) -> list[tuple[str, str, str]]:
    """
    Find all embedded Imgur links in the file like ![text]()\n
    Only match links that start with https://i.imgur.com/\n
    Return a list of tuples, where each tuple is ("<text>", "https://i.imgur.com/<code>", ".<extension>")
    """
    imgur_pattern = r'!\[(.*?)\]\((https:\/\/i\.imgur\.com\/\w+)(\.\w+)?\)'

    imgur_links = findall(imgur_pattern, text)
    return imgur_links

def replace_external_url_link_with_internal_link(url: str, path: str, text: str, mode: str = "wikilink", alt_text: str = "") -> str:
    """replace ![](<imgur link>) with the ![[<local image path>]]"""
    if path.startswith("http"):
        raise ValueError("should be a local path")
    
    # match "![text](path)" and "![](path)"
    pattern = r"!\[([^\]]*)\]\((url)\)|!\[\]\((url)\)"
    escaped_url = escape(url)
    pattern = pattern.replace("url", escaped_url)
    if mode == "wikilink":
        target = f"![[{path}]]"
    elif mode == "mdlink":
        target = f"![{alt_text}]({path})"
    else:
        raise ValueError(f"mode should be {available_modes_text}")
    replaced_text = sub(pattern, target, text)
        
    return replaced_text

def dir_imgur_migrate(working_dir: str, mode: str = "wikilink") -> None:
    """go over every file in the directory recursively"""
    print(f"About to process all .md files under {working_dir}")
    for root, _, files in walk(working_dir):
        for file in files:
            if file.endswith(".md"):
                file_imgur_migrate(root, file, mode)
    print("All done!")

def file_imgur_migrate(working_dir: str, filename: str, mode: str = "wikilink") -> None:
    if not filename.endswith(".md"):
        print(f"Skipping {filename} because it's not a .md file")
        return
    file_path = join(working_dir, filename)
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
        alt_text, link_base, link_ext = link
        url = link_base + link_ext
        response = r_get(url)
        
        # use a snake-case file name
        safe_filename = filename.replace('.md', '').lower().replace(' ', '-')
        ind = i + 1
        image_name = f'{safe_filename}-{ind}{link_ext}'
        image_path = join(working_dir, image_name)
        
        # check if the image already exists
        while exists(image_path):
            ind += 1
            image_name = f'{safe_filename}-{ind}{link_ext}'
            image_path = join(working_dir, image_name)
        replaced_text = replace_external_url_link_with_internal_link(url, image_name, text, mode=mode, alt_text=alt_text)
        
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
    
def main():
    parser = ArgumentParser()
    parser.add_argument('directory', nargs='?', default=".", help='directory to process, default to current directory')
    parser.add_argument('filename', nargs='?', help='file name')
    parser.add_argument('--mode', '-m', nargs='?', default="wikilink", help='wikilink or mdlink')
    args, _ = parser.parse_known_args()
    
    working_dir = args.directory
    filename = args.filename
    mode = args.mode
    if mode not in available_modes:
        print(f"Error: mode should be {available_modes_text}")
        return
    
    # if no filename given
    if not filename:
        dir_imgur_migrate(working_dir, mode)
    else:
        file_imgur_migrate(working_dir, filename, mode=mode)

if __name__ == "__main__":
    main()