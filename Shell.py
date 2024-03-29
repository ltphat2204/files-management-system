import cmd
from typing import Union
from FAT32 import FAT32
from NTFS import NTFS
class Shell(cmd.Cmd):
  intro = "Welcome to Shelby the pseudo-shell! Type help or ? to list the commands.\n"
  prompt = ""
  def __init__(self, volume: Union[FAT32, NTFS]) -> None:
    super(Shell, self).__init__()
    self.vol = volume
    self.__update_prompt()
    self.output = ""

  def __update_prompt(self):
    Shell.prompt = f'┌──(LVL@OS1)-[{self.vol.get_cwd()}]\n└─$ '
  
  def do_pwd(self, arg):
    '''
    pwd: print current working directory
    '''
    self.output = self.vol.get_cwd()
  
  def do_ls(self, arg):
    '''
    ls: list out all files and folders in current directory
    ls <path>: list out all files and folders in specified path
    '''
    try:
      filelist = self.vol.get_dir(arg)
      self.output += (f"{'Mode':<10}  {'Sector':>10}  {'LastWriteTime':<20}  {'Length':>12}  {'Name'}") + "\n"
      self.output += (f"{'────':<10}  {'──────':>10}  {'─────────────':<20}  {'──────':>12}  {'────'}") + "\n"
      for file in filelist:
        flags = file['Flags']
        flagstr = list("-------")
        if flags & 0b1:
          flagstr[-1] = 'r'
        if flags & 0b10:
          flagstr[-2] = 'h'
        if flags & 0b100:
          flagstr[-3] = 's'
        if flags & 0b1000:
          flagstr[-4] = 'v'
        if flags & 0b10000:
          flagstr[-5] = 'd'
        if flags & 0b100000:
          flagstr[-6] = 'a'
        flagstr = "".join(flagstr)

        self.output += (f"{flagstr:<10}  {file['Sector']:>10}  {str(file['Date Modified']):<20}  {file['Size'] if file['Size'] else '':>12}  {file['Name']}") + "\n"
    except Exception as e:
      raise Exception(e)

  def do_cd(self, arg):
    '''
      cd <path>: change to directory specified in path
    '''
    try:
      self.vol.change_dir(arg)
      self.__update_prompt()
      self.output = self.vol.get_cwd()
    except Exception as e:
      raise Exception(e)

  def do_tree(self, arg):
    '''
      tree: print the tree of the current directory and it's sub-directory
      tree <path>: print the directory tree in the specified path
    '''
    def print_tree(entry, prefix="", last=False):
      self.output += (prefix + ("└── " if last else "├── ") + entry["Name"]) + "\n"
      # check if is archive
      if entry["Flags"] & 0b100000:
        return
      
      self.vol.change_dir(entry["Name"])
      entries = self.vol.get_dir()
      l = len(entries)
      for i in range(l):
        if entries[i]["Name"] in (".", ".."):
          continue
        prefix_char = "    " if last else "│   "
        print_tree(entries[i], prefix + prefix_char, i == l - 1)
      self.vol.change_dir("..")

    cwd = self.vol.get_cwd()
    try:
      if arg != "":
        self.vol.change_dir(arg)
        self.output += (self.vol.get_cwd()) + "\n"
      else:
        self.output += (cwd) + "\n"
      entries = self.vol.get_dir()
      l = len(entries)
      for i in range(l):
        if entries[i]["Name"] in (".", ".."):
          continue
        print_tree(entries[i], "", i == l - 1)
    except Exception as e:
      raise Exception(e)
    finally:
      self.vol.change_dir(cwd)

  def do_cat(self, arg):
    '''
      cat <path to file>: print content of file specified in path (text only)
    '''
    if arg == "":
      self.output = (f"[ERROR] No path provided")
      return
    try:
      self.output = (self.vol.get_text_file(arg))
    except Exception as e:
      raise Exception(e)

  def do_xxd(self, arg):
    '''
      xxd <path to file>: print hexdump of the file specified in path
    '''
    try: 
      raw_data = self.vol.get_file_content(arg)
    except Exception as e:
      raise Exception(e)

    for i in range(0, len(raw_data), 16):
      line = raw_data[i: i + 16]
      index = "%08X:" % i 
      ascii = ""
      hex_str = ""
      self.output += index + " "
      for j, c in enumerate(line, 1):
        if j % 9 == 0:
            hex_str += " "
        hex_str += "%02X " % c
        if c > 31 and c < 127:
            ascii += chr(c)
        else:
            ascii += '.'
      self.output += (f'{hex_str:<49} {ascii}') + "\n"

  def do_echo(self, arg):
    '''
      echo <anything>: print whatever you give it
    '''
    self.output = (arg)

  def do_fsstat(self, arg):
    '''
      fsstat: print volume information
    '''
    self.output = (self.vol)
    
  def do_bye(self, arg):
    '''
      bye: exit the shell
    '''
    self.output = "close"
    self.close()
    return True
  
  def close(self):
    if self.vol:
      del self.vol
      self.vol = None