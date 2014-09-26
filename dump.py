from ctypes import sizeof
from ctypes import byref
import re
from ctypes import c_ulong, create_string_buffer
from ctypes import windll
from ctypes import *

READ_PROCESS_MEMORY = windll.kernel32.ReadProcessMemory
VIRTUALQUERYEX = windll.kernel32.VirtualQueryEx

BYTE      = c_ubyte
WORD      = c_ushort
DWORD     = c_ulong
LPBYTE    = POINTER(c_ubyte)
LPTSTR    = POINTER(c_char)
HANDLE    = c_void_p
PVOID     = c_void_p
LPVOID    = c_void_p
UINT_PTR  = c_ulong
SIZE_T    = c_ulong

class PROC_STRUCT(Structure):
  _fields_ = [
    ("wProcessorArchitecture",    DWORD),
    ("wReserved",                 DWORD),]


class SYSTEM_INFO_UNION(Union):
  _fields_ = [
    ("dwOemId",    DWORD),
    ("sProcStruc", PROC_STRUCT),]


class SYSTEM_INFO(Structure):
  """
  kernel32.GetSystemInfo()
  """
  _fields_ = [
    ("uSysInfo", SYSTEM_INFO_UNION),
    ("dwPageSize", DWORD),
    ("lpMinimumApplicationAddress", LPVOID),
    ("lpMaximumApplicationAddress", LPVOID),
    ("dwActiveProcessorMask", DWORD),
    ("dwNumberOfProcessors", DWORD),
    ("dwProcessorType", DWORD),
    ("dwAllocationGranularity", DWORD),
    ("wProcessorLevel", WORD),
    ("wProcessorRevision", WORD),
]


class MEMORY_BASIC_INFORMATION(Structure):
  _fields_ = [
    ("BaseAddress", PVOID),
    ("AllocationBase", PVOID),
    ("AllocationProtect", DWORD),
    ("RegionSize", SIZE_T),
    ("State", DWORD),
    ("Protect", DWORD),
    ("Type", DWORD),
]

import win32security, win32con, win32api, pywintypes
import sys
import os
import win32pdh

rules = None

def AdjustPrivilege( priv ):
  flags = win32security.TOKEN_ADJUST_PRIVILEGES | win32security.TOKEN_QUERY
  htoken =  win32security.OpenProcessToken(win32api.GetCurrentProcess(), flags)
  id = win32security.LookupPrivilegeValue(None, priv)
  newPrivileges = [(id, win32security.SE_PRIVILEGE_ENABLED)]
  win32security.AdjustTokenPrivileges(htoken, 0, newPrivileges)

def ReadProcessMemory(ProcessID, rules):
  base = 0
  memory_basic_information = MEMORY_BASIC_INFORMATION()
  AdjustPrivilege("seDebugPrivilege")
  #pHandle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION | win32con.PROCESS_VM_READ | win32con.PROCESS_VM_OPERATION , 0, ProcessID)
  pHandle = win32api.OpenProcess(win32con.PROCESS_VM_READ | win32con.PROCESS_QUERY_INFORMATION, 0, ProcessID)
  versionFound = None
  localizationFound = None
  traitStringsFound = None
  while VIRTUALQUERYEX(pHandle.handle, base, byref(memory_basic_information), sizeof(memory_basic_information)) > 0:
    count = c_ulong(0)
    try:
      buff = create_string_buffer(memory_basic_information.RegionSize)
      if READ_PROCESS_MEMORY(pHandle.handle, base, buff, memory_basic_information.RegionSize, byref(count)):

        versionRegex = " ([^ ]*?);END_STATUS"
        f = re.findall(versionRegex, buff.raw, re.UNICODE)
        if f:
          if versionFound:
            print "INFO: OVERWRITING PRIOR VERSION STRING"
          if len(list(set(f))) > 1:
            print "WARNING: FOUND MORE THAN ONE VERSION."
          versionFound = f[0]

        localizationRegex = "<localization.*?</localization>"
        f = re.findall(localizationRegex, buff.raw, re.DOTALL|re.UNICODE)
        if f:
          if localizationFound:
            print "WARNING: OVERWRITING PRIOR LOCALIZATION" 
          localizationFound = '\n'.join([ x for i in f for x in i.split('\n') if not re.search('<column_[0-9]*/>',x) ])

        traitStringsRegex = "\n\n(Trait_.*?)\n\n"
        f = re.findall(traitStringsRegex, buff.raw, re.DOTALL|re.UNICODE)        
        if f:
          if traitStringsFound:
            print "WARNING: OVERWRITING PRIOR TRAIT STRINGS"
          if len(f) > 1:
            print "WARNING: FOUND MULTIPLE TRAITS STRINGS, IGNORING ALL BUT THE FIRST"
          traitStringsFound = f[0]


    except:
      pass
    base += memory_basic_information.RegionSize

  win32api.CloseHandle(pHandle)
  return (versionFound, localizationFound, traitStringsFound)

def GetProcessID( name ) :
  object = "Process"
  items, instances = win32pdh.EnumObjectItems( None, None, object, win32pdh.PERF_DETAIL_WIZARD )
  val = None
  if name in instances :
    hq = win32pdh.OpenQuery()
    hcs = [ ]
    item = "ID Process"
    path = win32pdh.MakeCounterPath( ( None, object, name, None, 0, item ) )
    hcs.append( win32pdh.AddCounter( hq, path ) )
    win32pdh.CollectQueryData( hq ) 
    for hc in hcs:
      type, val = win32pdh.GetFormattedCounterValue( hc, win32pdh.PDH_FMT_LONG )
      win32pdh.RemoveCounter( hc )
    win32pdh.CloseQuery( hq )
    return val


(version,localization,traitStrings) = ReadProcessMemory(GetProcessID("GoDFactoryWingmen"), rules)
def writeToFile(fileName,textToWrite):
  f = open(fileName,"w")
  f.write(textToWrite)
  f.close()

version = "1.0.2b"
writeToFile("localization."+version+".dump",localization)
writeToFile("traitStrings."+version+".dump",traitStrings)
  