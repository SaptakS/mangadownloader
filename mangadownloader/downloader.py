import os
import requests
import re

from io import BytesIO
from difflib import SequenceMatcher as sm
from PIL import Image

from utils import get_content_size, get_link_data, get_total_pages


class MangaDownloader():

    def __init__(
        self,
        base_path,
        base_url,
        title_prefix="",
        proxy=None
    ):
        self.base_path = base_path
        self.base_url = base_url
        base_url_parts = re.split(r"/", self.base_url)
        self.base_host = base_url_parts[0] + "//" + base_url_parts[2]
        self.title_prefix = title_prefix
        self.proxy_dict = {}
        if proxy:
            self.proxy_dict = {
                "https": proxy,
                "http": proxy,
                "ftp": proxy,
            }

    def __repr__(self):
        return '<%s %r>' % (
            self.__class__.__name__,
            self.base_path,
        )


    def find_next_URL(self, image_obj):
        """ Finds the next page in the manga or comic by finding the URL that
        the enclosing anchor tag of the image of the current page has as a
        href.

        :param image_obj: BeautifulSoup image object of the current image
                          being downloaded
        """
        return image_obj.parent["href"]


    def get_valid_image_obj(self, img_objs):
        """ Find the valid BeautifulSoup image object from the various
        different image objects present in the current page or URL based
        on string matching of the image link and base_url, and the size of
        the image in the image obj.

        :param img_objs: List of all BeautifulSoup image objects present in the
                         current page
        """
        maxval = 0
        match_obj = None
        for img_obj in img_objs:
            img_size = get_content_size(
                img_obj['src'].strip(),
                self.proxy_dict
            )

            if 'alt' in img_obj.attrs:
                sequence_match_ratio = sm(
                    None,
                    str(img_obj['alt']),
                    self.base_url.replace("http", "")
                ).ratio()

                if sequence_match_ratio > maxval and img_size > 99999:
                    maxval = sm(
                        None,
                        str(img_obj['alt']),
                        self.base_url
                    ).ratio()
                    match_obj = img_obj

        return match_obj


    def save_img_from_bs_obj(self, matching_img_obj, image_title):
        """ Save image in the file from the most matching image
        object obtained.

        :param matching_img_obj: BeautifulSoup obj for matching image element
        :param image_title: name of the image file saved
        """
        matchin_url = ""
        if matching_img_obj:
            matchin_url = matching_img_obj['src'].strip()
        else:
            print("MatchingImageNotFound: " + 
                "Couldn\'t determine the matching image for given URL")

        if "http" not in matchin_url and matchin_url != "":
            matchin_url = self.base_host.split("//")[0] + matchin_url

        try:
            image = requests.get(matchin_url, proxies=self.proxy_dict)
        except:
            print ("Error: Couldn\'t get image content")
            exit(0)

        file = open(os.path.join(self.base_path, "%s.jpg") % image_title, 'wb')
        try:
            Image.open(BytesIO(image.content)).save(file, 'JPEG')
            print("Images Saved Successfully")
        except IOError as e:
            print("Couldnt Save:", e)
        finally:
            file.close()


    def download(self):
        """ Download all the pages of the issue based on the link provided
        and iterating over the next pages.
        """
        image_index = 0
        total_img = get_total_pages(self.base_url, self.proxy_dict)
        data = get_link_data(self.base_url, self.proxy_dict)
        img_objs = data.findAll("img")
        if not os.path.exists(self.base_path):
            os.makedirs(self.base_path)

        image_obj = self.get_valid_image_obj(img_objs)
        self.save_img_from_bs_obj(
            image_obj,
            self.title_prefix + str(image_index)
        )

        ctr = 0
        while ctr < total_img - 1:
            image_index = image_index + 1
            next_rel = self.find_next_URL(image_obj)
            if not "://" in next_rel:
                if next_rel.startswith("/"):
                    self.base_url = self.base_host + next_rel
                else:
                    self.base_url = re.sub(r"\w+.html", next_rel, self.base_url)
            else:
                self.base_url = next_rel

            print("Next page is", self.base_url)
            data = get_link_data(self.base_url, self.proxy_dict)
            img_objs = data.findAll("img")
            image_obj = self.get_valid_image_obj(img_objs)
            self.save_img_from_bs_obj(
                image_obj,
                self.title_prefix + str(image_index)
            )
            ctr = ctr + 1
        print("Total Pages Downloaded: ", (ctr + 1))
