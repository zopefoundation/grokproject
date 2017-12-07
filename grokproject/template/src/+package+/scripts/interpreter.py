import os, sys

def main():
    os.environ['PYTHONPATH'] = ':'.join(sys.path)
    os.execve(sys.executable, sys.argv, os.environ)
