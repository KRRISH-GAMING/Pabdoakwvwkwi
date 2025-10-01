# Standard Library
import logging
import logging.config
import glob
import asyncio
import importlib
import sys
import re
import traceback
import shutil
import random
import string
import time as pytime  # time module for timestamps
from datetime import datetime, date, time as dtime, timedelta, timezone
from typing import *

# Third-party libraries
import pytz
import motor.motor_asyncio
import qrcode
import imaplib
import email
import requests
import base64

# OS & Path
import os
from pathlib import Path

# BSON & IO
from bson import ObjectId
from io import BytesIO

# Pyrogram
from pyrogram import *
from pyrogram.types import *
from pyrogram.errors import *
from pyrogram.errors.exceptions.bad_request_400 import *

# aiohttp
from aiohttp import ClientSession, web, ClientTimeout, TCPConnector
from aiohttp.web_request import Request
from aiohttp.web_response import Response, json_response
