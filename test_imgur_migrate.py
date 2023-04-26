import unittest
from imgur_migrate import find_all_imgur_links, replace_external_url_link_with_internal_wiki_link

class TestImgurMigrate(unittest.TestCase):
    def test_find_all_imgur_links(self):
        mock_text = "This is a test string ![](https://i.imgur.com/1.png) containing an image link. Here's another ![example image](https://i.imgur.com/2xxXw2.jpg) with some text."
        expected_ans = [('https://i.imgur.com/1', '.png'), ('https://i.imgur.com/2xxXw2', '.jpg')]
        actual_ans = find_all_imgur_links(mock_text)
        self.assertEqual(expected_ans, actual_ans)
        
    def test_replace_md_link_with_wiki_link(self):
        target_url = "https://i.imgur.com/1.png"
        target_path = "Junior/os-1.png"
        another_path = "Senior/macro-2.png"
        mock_text = f"This is a test string ![]({target_url}) containing an image link. Here's another ![example image]({another_path}) with some text."
        expected_ans = f"This is a test string ![[{target_path}]] containing an image link. Here's another ![example image]({another_path}) with some text."
        actual_ans = replace_external_url_link_with_internal_wiki_link(target_url, target_path, mock_text)
        self.assertEqual(expected_ans, actual_ans)

if __name__ == "__main__":
    unittest.main()