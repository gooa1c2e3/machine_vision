# -*- coding: utf-8 -*-
import cv2
import numpy as np
import os
from collections import namedtuple
from PIL import ImageGrab, Image
import sys
import pyocr
import pyocr.builders
from argparse import ArgumentParser


__version__ = "0.0.1"

ntp = namedtuple("img_slice", ("x_start","x_end", "y_start", "y_end"))
slice_list = []

# text of Element
#ele_slice = ntp(884, 951, 231, 265)  
#slice_list.append(("ele", ele_slice))

# text of Percentage
pct_slice = ntp(952, 1104, 231, 265)
slice_list.append(("percent", pct_slice))
    
# text of standard error
std_slice = ntp(1105, 1315, 231, 265)
slice_list.append(("std", std_slice))


tools = pyocr.get_available_tools()
if len(tools) == 0:
    print("No OCR tool found, exit")
    sys.exit(1)
# The tools are returned in the recommended order of usage
tool = tools[0]
#print("Will use tool '%s'" % (tool.get_name()))
# Ex: Will use tool 'libtesseract'

langs = tool.get_available_languages()
#print("Available languages: %s" % ", ".join(langs))
lang = langs[0]
#print("Will use lang '%s'" % (lang))


def grayImg(img):
    if not isinstance(img, np.ndarray):
        raise TypeError('Input image type is not numpy.ndarray.')
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    

def get_screenshot():
    printscreen_pil = ImageGrab.grab()
    return np.array(printscreen_pil.getdata(),dtype='uint8').reshape((printscreen_pil.size[1],printscreen_pil.size[0],3))
    
 
def img2string(img):
    image = Image.fromarray(img)
    txt = tool.image_to_string(
        image,
        lang='eng',
        builder=pyocr.builders.TextBuilder()
    )
    return txt
    

def _main(show=False):
    _anser_list = []
    desktop = get_screenshot()
    gray_img = grayImg(desktop)
    
    text_list = []
    for name, img_slice in slice_list:
        _slice = gray_img[
                img_slice.y_start:img_slice.y_end,
                img_slice.x_start:img_slice.x_end
            ]
        
        # Convert img to 'white on black'
        #ret, bin_img = cv2.threshold(_slice, 127, 255, cv2.THRESH_BINARY_INV)
        
        # Convert img to 'black on white' 
        ret, bin_img = cv2.threshold(_slice, 127, 255, cv2.THRESH_BINARY)
        
        if show:
            cv2.imshow('text_image', bin_img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        
        _ans = img2string(bin_img)
        _anser_list.append(_ans)
    return _anser_list

    
def get_parser():
    """ To parse arguments from command line input """
    class Options:
        def __init__(self):
            self._parser = self.__init__parser()
            
        def __init__parser(self):
            _usage = """ RCR program of XRF """
            _parser = ArgumentParser(description=_usage)
            
            _parser.add_argument(
                '-s', '--show', 
                help="Show text images for debug", 
                action="store_true",
                dest='show'
                )

            _parser.add_argument(
                '-v', '--version', 
                help='show version', 
                action="version", 
                version='version= {}'.format(__version__)
                )
            return _parser
                            
    option = Options()
    return option._parser

def extract_xrf_value():
    return _main()

if __name__=="__main__":
    parser = get_parser()
    args = parser.parse_args()
    anser_list = _main(show=args.show)
    print "Percentage:", anser_list[0], ", Standard error:", anser_list[1]