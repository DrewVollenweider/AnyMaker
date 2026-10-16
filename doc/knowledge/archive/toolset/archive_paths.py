"""Paths for historical scripts. Set ANYMAKER_INSTALL for installation analysis."""
import os
from pathlib import Path

def creation(name=''):
    root = os.environ.get('ANYMAKER_CREATIONS')
    if not root:
        appdata = os.environ.get('APPDATA')
        if not appdata:
            raise RuntimeError('Set ANYMAKER_CREATIONS to your Anymaker creations folder')
        root = str(Path(appdata) / 'Anymaker/creations')
    return Path(root) / name

def appdata(name=''):
    return creation().parent / name

def install(name=''):
    root = os.environ.get('ANYMAKER_INSTALL')
    if not root:
        raise RuntimeError('Set ANYMAKER_INSTALL to your read-only Anymaker installation')
    return Path(root) / name
