import os
import requests
import re

from io import BytesIO
from difflib import SequenceMatcher as sm
from PIL import Image

from utils import get_content_size


class MangaDownloader():

    def __init__(
        self,
        base_path,
        base_url,
        proxy=None
    ):
        self.base_path = base_path
        self.base_url = base_url
        self.proxy_dict = {}
        if proxy:
            self.proxy_dict = {
                "https": proxy,
                "http": proxy,
                "ftp": proxy,
            }


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
