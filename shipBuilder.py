#!/usr/bin/env python
APP_VERSION = "0.0.1"

from string import ascii_uppercase
from time import sleep
import urllib2
import os.path
import csv
import re
import sqlite3
import sys
from distutils.version import StrictVersion
from functools import partial
from collections import namedtuple
import kivy
kivy.require('1.8.0') # replace with your current kivy version !

from kivy.config import Config
Config.set("graphics","height",786)
Config.set("graphics","width",1024)
Config.write()
# Gotta do this here because kivy is INTERESTING

from kivy.app import App

from kivy.uix.label import Label
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader, StripLayout, TabbedPanelStrip, TabbedPanelContent, TabbedPanelHeader
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.popup import Popup
from kivy.clock import Clock
from kivy.uix.dropdown import DropDown
from kivy.uix.image import Image
from kivy.uix.scatter import ScatterPlane, Scatter
from kivy.graphics import Rotate
from kivy.core.window import Window
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.metrics import dp
from kivy.graphics import Color,Rectangle,Line
from kivy.uix.textinput import TextInput

ALPHA = "Alpha"
OMEGA = "Omega"

yyTrans={"Yin":ALPHA, "Yan":OMEGA}

weaponTypeTrans={"Gunship_PartKeyword_Cannon":"Cannon", "Gunship_PartKeyword_Satellite":"Satellite", "Gunship_PartKeyword_Mines":"Mines", "Gunship_PartKeyword_Beam":"Beam", "Gunship_PartKeyword_Wave":"Wave", "Gunship_PartKeyword_Scattergun":"Scattergun", "Gunship_PartKeyword_Homing":"Homing", "Gunship_PartKeyword_Bombing":"Bombing", "Gunship_PartKeyword_Machinegun":"Machine Gun"} 
HULL = "HULL"
COCKPIT = "COCKPIT"
WINGS = "WINGS"
THRUSTERS = "THRUSTERS"
POWER_CORE = "POWER_CORE"
SHIELD_GENERATOR = "SHIELD_GENERATOR"
MAIN_COMPUTER = "MAIN_COMPUTER"
WEAPON_CONTROL_UNIT = "WEAPON_CONTROL_UNIT"
DEVICE = "DEVICE"
ADD_ON = "ADD_ON"
MAIN_WEAPON = "MAIN_WEAPON"
WING_WEAPON = "WING_WEAPON"

GUNSHIP = "GUNSHIP"

partTypes=[HULL,COCKPIT,WINGS,THRUSTERS,POWER_CORE,SHIELD_GENERATOR,MAIN_COMPUTER,WEAPON_CONTROL_UNIT,DEVICE,ADD_ON,MAIN_WEAPON,WING_WEAPON]

damageTypes = [ 'Detonation', 'Overload', 'Ignition', 'Distortion', 'Decay', 'Perforation']

HUMAN = 1
GUANTRI = 2
AR = 3
CHORION = 4

races = [HUMAN, GUANTRI, AR, CHORION]

raceToStringMap = { HUMAN:"Human", GUANTRI:"Guantri", AR:"Ar",  CHORION:"Chorion" }
raceToColorMap = {HUMAN: (1,1,0,1), GUANTRI: (0,1,1,1), AR: (0,1,0,1), CHORION: (1,0,0,1)}

NO = "No"
YES = "Yes"
RESET = "Reset"
ADD = "Add"
SPREAD = "Spread"
DIVIDE = "Divide"
NA = "N/A"
UNKNOWN = "???"

projectilesPerTarget = { ALPHA: {214001: 1, 214002: 6,114007: 2,414000: 2,414005: 8,115002: 2,115007: 6,115010: 2,115011: 16,215001: 2,215007: 6,215013: 3,315003: 2,315010: 7,315012: 9,415005: 4,415006: 2,415002: 2,415014: 2}, OMEGA: { 214001: 2, 214002: 3 }}
lockRequired = { ALPHA : { 214001: YES,114005: RESET,314000: RESET,314005: YES,314006: RESET,314007: YES,414002: YES,414005: YES,414007: YES,115001: YES,115002: YES,115007: RESET,115010: YES,115012: RESET,115011: YES,215001: YES,215003: RESET,215013: YES,315003: YES,315012: RESET,315007: RESET,315004: YES,315005: YES,415005: YES,415002: YES,415007: RESET,415014: RESET }, OMEGA: {214001: NO}}
multiTargetMode = { ALPHA : {214003: NA, 114005: ADD,214005: SPREAD, 214002: DIVIDE,414005: DIVIDE,115002: DIVIDE,115010: DIVIDE,115011: DIVIDE,215001: DIVIDE,215003: ADD,215013: DIVIDE,315003: DIVIDE,315004: ADD,415005: DIVIDE }, OMEGA: {215001: DIVIDE,215003: ADD,215013: DIVIDE, 214002: ADD, 214003: SPREAD,214005: NA} }

# too lazy to hard code them all twice. Put placeholders for Guantri shit that's default in one mode but not in the other.
for aoDict in [projectilesPerTarget, lockRequired, multiTargetMode]:
  for key in aoDict[ALPHA]:
    if key not in aoDict[OMEGA]:
      aoDict[OMEGA][key] = aoDict[ALPHA][key] 

def partCompareAO(part):
  if len(part[OMEGA]) < len(part[ALPHA]):
    return True
  return reduce((lambda p, q: p and q),[ part[ALPHA][i].rawVals[0:16] == part[OMEGA][i].rawVals[0:16] and part[ALPHA][i].rawVals[17:] == part[OMEGA][i].rawVals[17:] for i in part[ALPHA].keys()],True)

def camelToReadable(camelString):
  if camelString.isupper():
    return camelString #Support acronyms. (DPS)
  return camelString[0].upper()+''.join([ c if c.islower() else " "+c for c in camelString[1:]])

AO=ALPHA
def getAO():
  global AO
  return AO

def swapAO():
  global AO
  AO =  OMEGA if AO == ALPHA else ALPHA

def aoInv(x):
  if x == ALPHA:
    return OMEGA
  if x == OMEGA:
    return ALPHA
  1/0 #Y'know, just in case.

def mkInt(x):
  return int(x) if re.match("^[0-9-]+$",x) else 0

def mkFlt(x):
  return float(x) if re.match("^[-.0-9]+$",x) else 0

class PartMark(dict):
  attribs = [ "id", "rawVals", "defaultRace", "type", "className", "weaponType", "rankRequired", "possibleRaces", "creditCosts", "expRequired", "prereqParts","traits", "isPrereqFor", "mark", "codeName", "alphaOmega", "damageTypes", "grade", "scoreGained", "weightCost", "weightCapacity", "powerCost", "powerCapacity", "heatCost", "heatCapacity", "shield", "shieldRecharge", "energy", "energyRegen", "perforationResist", "decayResist", "distortionResist", "ignitionResist", "overloadResist", "detonationResist", "comboResist", "handling", "numWingWeapons", "speed", "boost", "purgeCooldown", "abilityCooldown", "lockingSpeed", "targetingArea", "targetingRange", "minimumRange", "maximumRange", "accuracy", "shotCooldown", "projectileCount", "projectileRange", "ammo", "lockingTime", "maxTargets", "damage", "markOwned", "currentExp", "parentName", "displayName", "description", "range","multiTargetMode","projectilesPerTarget","lockRequired", "targets", "rawAmmo", "rawDamage", "mystery", "additionalWonders", "DPS","damagePerLoad","ammoLifesplan","fireRate","isBuyable"]
  def __getattr__(self, key):
    return self.__getitem__(key)

  def __setattr__(self, key, value, alphaOmega = None):
    if key in PartMark.attribs:
      self[getAO()][key] = value
    else:
      self.__dict__[key] = value

  def __contains__(self, key):
    alphaOmega = getAO()
    if key in PartMark.attribs:
      return alphaOmega in self and key in self[alphaOmega]
    else:
      return super(PartMark, self).__contains__(key)

  def __getitem__(self, key):
    alphaOmega = getAO()
    if key not in PartMark.attribs:
      return super(PartMark, self).__getitem__(key)
    if not key in self[alphaOmega] and alphaOmega == OMEGA:
      return self[ALPHA][key]
    else:
      return self[alphaOmega][key]

  def merge(self,other):
    if not self[ALPHA] and other[ALPHA]:
      self[ALPHA] = other[ALPHA]
    if not self[OMEGA] and other[OMEGA]:
      self[OMEGA] = other[OMEGA]

  def __init__(self, partVals,names, *args, **kw):    
    self[ALPHA] = {}
    self[OMEGA] = {}
    super(PartMark,self).__init__(*args,**kw)
    ao = yyTrans[partVals[17]]

    self.id = int(partVals[0])
    self.mark = int(partVals[15][2])
    self[ao]["id"] = int(partVals[0])
    self[ao]["defaultRace"] = int(partVals[1])
    self[ao]["type"] = partVals[2]
    self[ao]["className"] = partVals[3]
    self[ao]["weaponType"] = weaponTypeTrans[partVals[4]] if partVals[4] else None
    self[ao]["rankRequired"] = int(partVals[5])
    self[ao]["possibleRaces"] = map(mkInt,partVals[6].split(';'))
    self[ao]["mystery"] = mkInt(partVals[7])
    self[ao]["expRequired"] = [ int(pair.split(';')[0]) for pair in partVals[8:12] ]
    self[ao]["creditCosts"] = [ int(pair.split(';')[1]) for pair in partVals[8:12] ]
    self[ao]["prereqParts"] = map(mkInt, partVals[12].split(';'))
    self[ao]["isPrereqFor"] = map(mkInt, partVals[13].split(';')) # partID again, for no reason
    self[ao]["mark"] = int(partVals[15][2])
    self[ao]["codeName"] = partVals[16]
    self[ao]["alphaOmega"] = yyTrans[partVals[17]]
    self[ao]["traits"] = [traitsById[mkInt(t)] for t in partVals[18].split(';') if mkInt(t) > 0 and mkInt(t) in traitsById]
    self[ao]["damageTypes"] = [ dType for (dType, flag) in zip(damageTypes,bin(mkInt(partVals[19]))[2:].zfill(6)) if flag == '1' ]
    self[ao]["grade"] = mkInt(partVals[20])
    self[ao]["scoreGained"] = mkInt(partVals[21]) 
    self[ao]["weightCost"] = mkInt(partVals[22])
    self[ao]["weightCapacity"] = mkInt(partVals[23])
    self[ao]["powerCost"] = mkInt(partVals[24])
    self[ao]["powerCapacity"] = mkInt(partVals[25])
    self[ao]["heatCost"] = mkInt(partVals[26])
    self[ao]["heatCapacity"] = mkInt(partVals[27])
    self[ao]["shield"] = mkInt(partVals[28])
    self[ao]["shieldRecharge"] = mkInt(partVals[29])
    self[ao]["energy"] = mkInt(partVals[30])
    self[ao]["energyRegen"] = mkInt(partVals[31])
    self[ao]["perforationResist"] = mkInt(partVals[32])
    self[ao]["decayResist"] = mkInt(partVals[33])
    self[ao]["distortionResist"] = mkInt(partVals[34])
    self[ao]["ignitionResist"] = mkInt(partVals[35])
    self[ao]["overloadResist"] = mkInt(partVals[36])
    self[ao]["detonationResist"] = mkInt(partVals[37])
    self[ao]["comboResist"] = mkInt(partVals[38])
    self[ao]["handling"] = mkInt(partVals[39])
    self[ao]["numWingWeapons"] = mkInt(partVals[40])
    self[ao]["speed"] = mkInt(partVals[41])
    self[ao]["boost"] = mkInt(partVals[42])
    self[ao]["purgeCooldown"] = mkInt(partVals[43])
    self[ao]["abilityCooldown"] = mkInt(partVals[44])
    self[ao]["lockingSpeed"] = mkFlt(partVals[45])
    self[ao]["targetingArea"] = mkInt(partVals[46])
    self[ao]["targetingRange"] = mkInt(partVals[47])
    self[ao]["minimumRange"] = mkInt(partVals[48])
    self[ao]["maximumRange"] = mkInt(partVals[49])
    self[ao]["accuracy"] = mkFlt(partVals[50])
    self[ao]["shotCooldown"] = mkFlt(partVals[51])
    self[ao]["projectileCount"] = mkInt(partVals[52])
    self[ao]["projectileRange"] = mkInt(partVals[53])
    self[ao]["rawAmmo"] = mkFlt(partVals[54])
    self[ao]["lockingTime"] = mkFlt(partVals[55])
    self[ao]["maxTargets"] = mkInt(partVals[56])
    self[ao]["rawDamage"] = mkFlt(partVals[57])
    self[ao]["markOwned"] = [ mk == '1' for mk in partVals[58]]
    self[ao]["currentExp"] = partVals[59]
    self[ao]["additionalWonders"] = partVals[59:]
    # if len(partVals) == 60: Not super useful
    #   self["timesUsed"] = partVals[59]

    self[ao]["parentName"] = self[ao]["className"]
    self[ao]["displayName"] = self[ao]["codeName"]
    self[ao]["description"] = ""

    # postProcessing

    self[ao]["isBuyable"] = self[ao]["defaultRace"] > 0 and sum(self[ao]["possibleRaces"]) > 0 and sum(self[ao]["creditCosts"]) > 0 and self[ao]["rankRequired"] > 0
    if self[ao]["isBuyable"]:
      if self["id"] in names:
        self[ao]["parentName"] = names[self.id]["name"]
        self[ao]["displayName"] = names[self.id]["name"+str(self.mark)]
        self[ao]["description"] = names[self.id]["desc"+str(self.mark)]
      self.updateNumericAttributes(ao)

  def updateNumericAttributes(self,ao):
    if self[ao]["type"] in [MAIN_WEAPON, WING_WEAPON]:
 
      if self[ao]["maximumRange"]:
        self[ao]["range"] = (str(self[ao]["minimumRange"]) + " - " if self[ao]["minimumRange"] else "" ) + str(self[ao]["maximumRange"]) + (" ["+ str(self[ao]["projectileRange"]) + "]" if self[ao]["projectileRange"] and self[ao]["projectileRange"] != self[ao]["maximumRange"] else "" )

      self[ao]["multiTargetMode"] = multiTargetMode[ao][self.id] if self.id in multiTargetMode[ao] else UNKNOWN

      self[ao]["lockRequired"] = lockRequired[ao][self.id] if self.id in lockRequired[ao] else NO

      if self[ao]["lockRequired"] == RESET:
        self[ao]["shotCooldown"] = self[ao]["lockingTime"]

      if (self[ao]["shotCooldown"] < 1.0):
        self[ao]["fireRate"] = str(1.0/self[ao]["shotCooldown"]) +"/s"
      else:
        self[ao]["fireRate"] = "1 shot / " + str(self[ao]["shotCooldown"]) +"s"

      if self.id in projectilesPerTarget[ao]:
        self[ao]["projectilesPerTarget"] = projectilesPerTarget[ao][self.id]
        self[ao]["damage"] = str(self[ao]["rawDamage"]) + "x"+str(self[ao]["projectilesPerTarget"]) + " ("+str(self[ao]["rawDamage"]*self[ao]["projectilesPerTarget"])+")"
        self[ao]["ammo"]  = str(self[ao]["rawAmmo"]) + "/"+str(self[ao]["projectilesPerTarget"]) + " ("+str(self[ao]["rawAmmo"]/self[ao]["projectilesPerTarget"])+")"
      else:
        self[ao]["projectilesPerTarget"] = 1
        self[ao]["damage"] = str(self[ao]["rawDamage"])
        self[ao]["ammo"]  = str(self[ao]["rawAmmo"])

      if self[ao]["maxTargets"] > 1 and self[ao]["weaponType"] != "Wave":
        self[ao]["targets"] = str(self[ao]["maxTargets"])+"/"+self[ao]["multiTargetMode"]

      self[ao]["DPS"] = self[ao]["projectilesPerTarget"]*self[ao]["rawDamage"]/self[ao]["shotCooldown"]
      self[ao]["damagePerLoad"] = self[ao]["rawDamage"]*self[ao]["rawAmmo"] if self[ao]["weaponType"] != "Satellite" else "Infinite"
      self[ao]["ammoLifesplan"] = str(self[ao]["rawAmmo"]*self[ao]["shotCooldown"] if self[ao]["weaponType"] != "Satellite" else "Infinite") + "s"

      if(self[ao]["weaponType"] == "Beam"):
        self[ao]["damage"] += "/s"
        self[ao]["damagePerLoad"] /= 10.0
        self[ao]["fireRate"] = "Continuous"
        self[ao]["ammoLifesplan"] = str(self[ao]["rawAmmo"] / 10.0) + "s"

      if self.id == 315006:
        # Fuck. The. Mini.
        numMiniShots = int(self[ao]["rawAmmo"]-1)/5
        self[ao]["DPS"] = self[ao]["rawDamage"] / 5.0
        self[ao]["damagePerLoad"] = numMiniShots * self[ao]["rawDamage"]
        self[ao]["ammoLifesplan"] = str(numMiniShots*5) + " seconds"
        self[ao]["fireRate"] = "1 shot / 5s"




     # if self[ao]["projectilesPerTarget"] > 1:
      #   self[ao]["ammo"] = self[ao]["ammo"] / 

class Trait:
  triggerTypes = {'All Green', 'Passive', 'Contained', 'Warrior', 'Drift', 'Attacker', 'Savior', 'Response', 'Harvester', 'Vengeance', 'Velocity', 'Relentless', 'Weapon Mod', 'Sentinel', 'Defender', 'Red Alert'}
  def __init__(self, nameAndId, desc, effects):
    self.rawNameAndId = nameAndId
    self.rawEffects = effects
    self.id = mkInt(nameAndId[0])
    self.descStr = re.sub("Trait_Prop[a-zA-Z_]*",traitPropTrans, re.sub("\{([0-9])_([0-9])\}",lambda m: effects[int(m.group(1))-1][int(m.group(2))],desc).replace('\\n','\n'))
    self.displayStr = triggerTrans(nameAndId[1])


miscTraitPropTrans = {'Area': "Targeting Area",'Range': "Targeting Range",'Lock_Systems': "Targeting Area, Targeting Range & Locking Speed",'Amp_Dmg': "Damage",'Cooldown': "Ability Cooldown",'Dark_Dmg': "Perforation, Decay & Distortion Damage",'Dec_Dmg': "Decay Damage",'Energy': "Energy",'Energy_Regen': "Energy Regen",'EnR_Cld': "Energy Regen & Ability Cooldown",'Handling': "Handling",'Light_Dmg': "Ignition, Overload & Detonation Damage",'Lock': "Locking Speed",'Negative': "Negative Effects",'Ovr_Dmg': "Overload Damage",'Per_Dis_Dmg': "Perforation & Distortion Damage",'Purge': "Purge Cooldown",'Resistances': "All Resistances",'Rft_Dmg': "Reflect Damage",'Shield': "Shield",'Siphon': "Siphon",'Spd_Hnd': "Speed & Handling",'Spd_Boo': "Speed & Boost",'Speed': "Speed",'Terminus': "Targeting Area, Targeting Range & Locking Speed" }
triggerTypeTrans = {'Cnt':'Contained','Pas':'Passive', 'Dft': 'Drift', 'Rel': 'Relentless', 'Ven': 'Vengeance', 'Har': 'Harvester', 'Vel': 'Velocity', 'Red': 'Red Alert', 'War': 'Warrior', 'Rsp': 'Response', 'Att': 'Attacker', 'Def': 'Defender','All': 'All Green','Sen': 'Sentinel','Sav': 'Savior'}
firstWordTrans = {'Loc' : "Locking Speed",'Amp' : "Amplify",'Mob' : "Mobility",'Cld' : "Ability Cooldown",'Res' : "Resistances",'Spd' : "Speed",'Eng' : "Engines",'Nrg' : "Restore Energy",'ER'  : "Energy Regen",'Trn' : "Transmission",'Tgt' : "Targeting",'Sys' : "Systems",'Sur' : "Survival",'Rng' : "Targeting Range",'Area': "Targeting Area",'Hnd' : "Handling",'Amp' : "Amplify",'Dep' : "Deplete",'Rst' : "Restore",'Rft' : "Reflect",'Pur' : "Purge Cooldown",'Coo' : "Cooling"}
restWordTrans = {'Dec' : "Decay",'Shd' : "Shield",'Nrg' : "Energy",'Aur' : "Aura",'Aura': "Aura",'Dmg' : "Damage",'Ovr' : "Overload",'Bub' : "Bubble"}
debuffStrTrans = {"Nrg_Lk": "Energy Leak","Sta": "Stall","Shd_Bur": "Shield Burst","Vul": "Vulnerability","Shd_Lk": "Shield Leak","Amm_Brn": "Ammo Burn","Dys": "Dysfunction","Unb": "Unbalanced","Slo": "Slow","Mul": "Multiple","Rad_Jam": "Radar Jam"}
miscNameMap = {'Special': "Special",'Jnt_Ass': "Joint Assault",'Sca_Sht': "Scattered Shots",'Chn_Att': "Chain Attack",'Sph': "Siphon Shield",'Freefall_A': "Resitances-",'Freefall_O': "Handling-",'TB_60': "Area Blast 60"}

def traitPropTrans(traitProp):
  traitProp = traitProp.group(0)[11:]
  if traitProp in miscTraitPropTrans:
    return miscTraitPropTrans[traitProp]
  elif "Wpn_Mod" in traitProp:
    return camelToReadable(traitProp[8:])
  else:
    return traitProp.replace("_"," ")

def triggerTrans(triggerName):
  triggerName = triggerName[12:]
  if triggerName[0:3] in triggerTypeTrans:
    return triggerTypeTrans[triggerName[0:3]] + ": " + effectTrans(triggerName[4:])
  elif triggerName[0:3] == 'Wpn' and triggerName[4:] in debuffStrTrans :
    return "Weapon Mod: " + debuffStrTrans[triggerName[4:]]
  elif triggerName[0:2] == 'AB':
    return "Area Blast "+triggerName[3:]
  elif triggerName in miscNameMap:
    return miscNameMap[triggerName]
  else:
    1/0 #haha what's reasonable error handling

def effectTrans(effectName):
  sign,nameParts = ('-',effectName[:-1].split('_')) if effectName[-1] == '-' else ('+',effectName.split('_'))
  return firstWordTrans[nameParts[0]] + ( " " + " ".join([restWordTrans[part] for part in nameParts[1:]]) if nameParts[1:] else sign) 

version = ""

try:
  version = open('VERSION').read()
except:
  print "No version file found! Will attempt to grab one online."


#check for a new version of the app logic
try:
  shipBuilder = urllib2.urlopen('https://raw.githubusercontent.com/turntekGodhead/God-Factory-Ship-Builder/master/shipBuilder.py').readlines()
  appVersionFromRepo = re.match('APP_VERSION = "(.*)"',shipBuilder[1]).groups()[0]

  if StrictVersion(appVersionFromRepo) > StrictVersion(APP_VERSION):
    if os.path.isfile('new.shipBuilder.py'):
      os.remove('new.shipBuilder.py')
    with open('new.shipBuilder.py','w') as f:
      f.write(''.join(shipBuilder))
except:
  print "Failed check for new version. Application logic may be out of date. Are you connected to the internet?"

if(os.path.isfile('new.shipBuilder.py')):
  print "New version found! Restarting"
  # Call the batch file to update here 
  exit()


#check to see if there's a newer version of the data
try:
  newVersion = urllib2.urlopen('https://raw.githubusercontent.com/turntekGodhead/God-Factory-Ship-Builder/master/VERSION').read()
  if version != newVersion:
    version = newVersion
    if os.path.isfile('VERSION'):
      os.remove('VERSION')
    with open('VERSION','w') as f:
      f.write(version)
    for dumpFile in ['traitStrings','traits','localization','parts']:
      fileName = dumpFile + "."+version +".dump"
      if os.path.isfile(fileName):
        os.remove(fileName)
      with open(fileName,'w') as f:
        f.write(urllib2.urlopen('https://raw.githubusercontent.com/turntekGodhead/God-Factory-Ship-Builder/master/'+fileName).read())
except:
  print "Error getting new version. Information may be outdated, and the program may not run at all."


traitsById = {}
traitStrings={}
traitStringsDump = open('traitStrings.'+version+".dump").read()
for traitString in traitStringsDump.splitlines():
  (key,desc) = re.match("([^ \t]*).*= (.*)",traitString).groups()
  traitStrings[key]=desc

traitsDump = open('traits.'+version+'.dump').read()
(traitEffectValues,_,rawTraits) = traitsDump.partition('STATS_TRAITS')
traitEffectValuesByEffectId = {}

for row in traitEffectValues.replace('|','\n').splitlines():
  traitEffectValuesByEffectId[row.split(':')[0]]=row.split(':')

for row in rawTraits.replace('|','\n').splitlines():
  splitRows=row.split(':')
  traitsById[int(splitRows[0])] = Trait(splitRows,traitStrings[splitRows[2]],[traitEffectValuesByEffectId[effectId] for effectId in splitRows[3].split(';')])

partKeyToXml = {"name":"name", "name1":"name_mk1","name2":"name_mk2","name3":"name_mk3","name4":"name_mk4","desc1":"desc_mk1","desc2":"desc_mk2","desc3":"desc_mk3","desc4":"desc_mk4"}

partStrings = {}
localizationDump = open('localization.'+version+'.dump').read()
for parts in localizationDump.split("</part>"):
  part = {}
  match = re.search("<partID>([0-9]*)</partID>",parts)
  partId = 0
  if match:
    partId = int(match.group(1))

  for partKey,Xml in partKeyToXml.iteritems():
    match = re.search("<"+Xml+">([^<]*)</"+Xml+">",parts)
    if match:
      part[partKey]=match.group(1)
  if partId:
    partStrings[partId]=part
partRows = {}

partsDump = open('parts.'+version+'.dump').read()
for row in partsDump.replace('|','\n').splitlines():
  partRow = PartMark(row.split(':'),partStrings)
  if partRow.id not in partRows:
    partRows[partRow.id] = {}
  if partRow.mark not in partRows[partRow.id]:
    partRows[partRow.id][partRow.mark] = partRow
  else:
    partRows[partRow.id][partRow.mark].merge(partRow)

buyablePartsByTypeAndRace = {}
for partType in partTypes:
  buyablePartsByTypeAndRace[partType]={}
  for race in races:
    buyablePartsByTypeAndRace[partType][race]=[]

for row in partRows.values():
  part = row[1]
  for race in part.possibleRaces:
    if part.isBuyable:
      buyablePartsByTypeAndRace[part.type][race].append(row)

for mainWeapon in buyablePartsByTypeAndRace[WING_WEAPON][GUANTRI]:
  print mainWeapon[1].id, mainWeapon[1].parentName


def p(l):
  for i in l:
    print i
def s(l):
  r = {'0'}
  r.remove('0')
  for i in l:
    r.add(i)
  return r
def ps(l):
  p(s(l))

class Gunship(dict):

  PartSlot = namedtuple('PartSlot', 'name type part')
  partFields = ["hull","cockpit","wings","thrusters","powerCore","shieldGenerator","mainComputer","weaponControlUnit","device","addOn","mainWeapon","wingWeapon1","wingWeapon2"]
  partSlotsByField = { "hull": PartSlot("Hull", HULL, None), "cockpit": PartSlot("Cockpit", COCKPIT, None), "wings": PartSlot("Wings", WINGS, None), "thrusters": PartSlot("Thrusters", THRUSTERS, None), "powerCore": PartSlot("Power Core", POWER_CORE, None), "shieldGenerator": PartSlot("Shield Generator", SHIELD_GENERATOR, None), "mainComputer": PartSlot("Main Computer", MAIN_COMPUTER, None), "weaponControlUnit": PartSlot("WCU", WEAPON_CONTROL_UNIT, None), "device": PartSlot("Device", DEVICE, None), "addOn": PartSlot("Add-on", ADD_ON, None), "mainWeapon": PartSlot("Main Weapon", MAIN_WEAPON, None), "wingWeapon1": PartSlot("Wing Weapon 1", WING_WEAPON, None), "wingWeapon2": PartSlot("Wing Weapon 2", WING_WEAPON, None) }
  directSummableAttribs = [ "weightCost", "powerCost", "heatCost", "weightCapacity", "powerCapacity", "heatCapacity", "grade",  "shield", "shieldRecharge", "energy", "energyRegen", "perforationResist", "decayResist", "distortionResist", "ignitionResist", "overloadResist", "detonationResist", "comboResist", "handling", "speed", "boost", "purgeCooldown", "abilityCooldown"]
  def __getattr__(self, key):
    return self[key]

  def __setitem__(self, key, item):
    if key in Gunship.partFields and (isinstance(item,PartMark) or item == None):
      self.__setattr__(key,item)
    else:
      super(Gunship,self).__setitem__(key,item)

  def slots(self):
    return [ self[field] for field in Gunship.partFields ]

  def __setattr__(self, key, value):
    if(key in Gunship.partFields):
      if(isinstance(value,Gunship.PartSlot)):
        self[key]=value
        return
      partSlot = self[key]
      if(value != None): # Skip the checks if the value is None. We like Nones.
        if(not isinstance(value,PartMark)):
          raise ValueError(str(value) + " is not a part")
        if(self.race not in value.possibleRaces):
          raise ValueError("racism")
        if(value.type != partSlot.type):
          raise ValueError(value.displayName + " is not a " + partSlot.type)
      self[key] = Gunship.PartSlot(partSlot.name, partSlot.type, value)
      self.updateNumericValues()
    else:
      self[key]=value



  def updateNumericValues(self):
    self.numWingWeapons = self.wings.part.numWingWeapons if self.wings.part else 1

    if self.numWingWeapons == 1:
      self.wingWeapon2 = Gunship.PartSlot("Wing Weapon 2", WING_WEAPON, None)
    for attrib in Gunship.directSummableAttribs:
      self[attrib] = sum([ self[field].part[attrib] for field in Gunship.partFields if self[field].part])

    self.mainWeaponAmmo = self.mainWeapon.part.rawAmmo if self.mainWeapon.part else 0
    self.wingWeapon1Ammo = self.wingWeapon1.part.rawAmmo if self.wingWeapon1.part else 0
    self.wingWeapon2Ammo = self.wingWeapon2.part.rawAmmo if self.wingWeapon2.part else 0
    if self.numWingWeapons == 2:
      self.wingWeapon1Ammo *= .8
      self.wingWeapon2Ammo *= .8

    self["class"] = min(8,max(1,self.grade / 100))
    if self.weightCapacity > 0:
      weightRatio = float(self.weightCost) / float(self.weightCapacity)
      if weightRatio <= 1:
        self.mainWeaponAmmo  *= 1.0 + (1.0 - weightRatio)/2.0
        self.wingWeapon1Ammo *= 1.0 + (1.0 - weightRatio)/2.0
        self.wingWeapon2Ammo *= 1.0 + (1.0 - weightRatio)/2.0
      else:
        percentOver = (weightRatio - 1.0) * 100.0
        self.handling          *= 1.0-(16.0 + percentOver*44.0/20.0)/100.0
        self.comboResist       *= 1.0-(16.0 + percentOver*44.0/20.0)/100.0
        self.perforationResist *= 1.0-(1.0 + percentOver*49.0/20.0)/100.0
        self.distortionResist  *= 1.0-(1.0 + percentOver*49.0/20.0)/100.0

    if self.powerCapacity > 0:
      powerRatio = float(self.powerCost) / float(self.powerCapacity)
      if powerRatio <= 1:
        self.abilityCooldown *= 1.0 + (1.0 - powerRatio)/2.0
      else:
        percentOver = (powerRatio - 1.0) * 100.0
        self.speed          *= 1.0-(16.0 + percentOver*44.0/20.0)/100.0
        self.boost          *= 1.0-(8.0 + percentOver*22.0/20.0)/100.0
        self.decayResist    *= 1.0-(1.0 + percentOver*49.0/20.0)/100.0
        self.overloadResist *= 1.0-(1.0 + percentOver*49.0/20.0)/100.0

    if self.heatCapacity > 0:
      heatRatio = float(self.heatCost) / float(self.heatCapacity)
      if heatRatio <= 1:
        self.energy *= 1.0 + (1.0 - heatRatio)/2.0
      else:
        percentOver = (heatRatio - 1.0) * 100.0
        self.purgeCooldown    *= 1.0-(16.0 + percentOver*44.0/20.0)/100.0
        self.energyRegen      *= 1.0-(8.0 + percentOver*22.0/20.0)/100.0
        self.ignitionResist   *= 1.0-(1.0 + percentOver*49.0/20.0)/100.0
        self.detonationResist *= 1.0-(1.0 + percentOver*49.0/20.0)/100.0

    # round down
    for attrib in ["mainWeaponAmmo", "wingWeapon1Ammo", "wingWeapon2Ammo", "handling", "comboResist", "energy", "energyRegen", "perforationResist", "decayResist", "distortionResist", "ignitionResist", "overloadResist", "detonationResist", "speed", "boost", "abilityCooldown", "purgeCooldown"]:
      self[attrib] = int(self[attrib])


  def __init__(self, name, race, *args, **kw):
    super(Gunship,self).__init__(*args,**kw)
    if race not in races:
      raise ValueError("Invalid race")
    self.race = race
    self.name = name
    self.type = GUNSHIP
    for key,value in self.partSlotsByField.iteritems():
      self[key] = value
  def serialize(self):
    return ",".join([self.name,str(self.race)] + [(str(self[fieldKey].part.id)+'-'+str(self[fieldKey].part.mark) if self[fieldKey].part else "0-0") for fieldKey in self.partFields])

  @staticmethod
  def deserialize(serialShip):
    cols = serialShip.split(',')
    loadedShip = Gunship(name = cols[0], race = int(cols[1]))
    for key,partEntry in zip(loadedShip.partFields,cols[2:]):
      partId,_,mark = partEntry.partition('-')
      if int(partId):
        loadedShip[key] = partRows[int(partId)][int(mark)]
    loadedShip.updateNumericValues()
    return loadedShip

currentShip = None
currentPart = None
onShipUpdate = None
onPartUpdate = None

def walk(widget):
  return widget.children + [ grandchild for child in widget.children for grandchild in walk(child) ]

class PartNameList(GridLayout):
  def __init__(self,**kwargs):
    super(PartNameList,self).__init__(**kwargs)
    self.rows = 14
    self.cols = 1
    self.ship = None

  def updateDisplay(self):
    ship = self.ship
    self.clear_widgets()
    self.add_widget(AlignedLabel(text="Part List", color=raceToColorMap[ship.race], bold=True))
    for partField in ship.partFields:
      self.add_widget(AlignedLabel(text=ship[partField].part.displayName if ship[partField].part else "-"))

  def setPart(self,ship):
    self.ship = ship
    self.updateDisplay()

class StatDisplayGrid(GridLayout):

  def __init__(self,field = None,**kwargs):
    super(StatDisplayGrid, self).__init__(**kwargs)
    self.part = None

  def updateDisplay(self):
    map((lambda child : child.updateDisplay() if "updateDisplay" in dir(child) else 0), walk(self))

  def setPart(self,part):
    self.part = part
    map((lambda child : child.setPart(part) if "setPart" in dir(child) else 0), walk(self))


class StatsDisplay(GridLayout):
  sharedDisplayAttribs = [ "shield", "shieldRecharge", "energy", "energyRegen","speed", "boost", "handling", "purgeCooldown", "abilityCooldown", "lockingSpeed", "targetingArea", "targetingRange" ]
  extraAttribsByPart = {
    GUNSHIP: ["class"],
    HULL: ["weightCapacity"],
    POWER_CORE: ["powerCapacity"],
    COCKPIT: ["heatCapacity"],
    WINGS: ["numWingWeapons"],
    MAIN_WEAPON: ["weaponType", "range", "accuracy", "ammo", "lockingTime", "lockRequired", "targets", "damage","DPS","damagePerLoad","ammoLifesplan","fireRate", "damageTypes" ],
    WING_WEAPON: ["weaponType", "damage", "fireRate", "range", "accuracy", "ammo", "lockingTime", "lockRequired", "targets", "DPS", "damagePerLoad", "ammoLifesplan", "damageTypes" ]
  }
  def __init__(self, **kwargs):
    super(StatsDisplay, self).__init__(**kwargs)
    self.displayAttribs = StatsDisplay.sharedDisplayAttribs
    self.extraAttribs = []
    self.cols = 2
    self.part = None

  def updateDisplay(self):

    self.clear_widgets()
    if self.part:
      part = self.part
      for attrib in self.extraAttribs + self.displayAttribs:
        if not attrib in part:
          continue
        if not part[attrib]:
          continue
        if attrib == "DPS" and "weaponType" in part and part["weaponType"] == "Beam":
          continue
        self.add_widget(AlignedLabel(text=camelToReadable(attrib), halign='left'))  
        # sorry, not sorry
        if attrib == "damageTypes":
          self.add_widget(DamageTypeIcon(part[attrib]))
        else:
          self.add_widget(Label(text=str(part[attrib]), halign='right'))
    self.add_widget(Widget())
    self.add_widget(Widget())

  def setPart(self, part):
    self.part = part
    self.extraAttribs = StatsDisplay.extraAttribsByPart[part.type] if part and "type" in part and part.type in StatsDisplay.extraAttribsByPart else []
    self.updateDisplay()


def colorMarkupTranslate(text):
  return re.sub(r"\[([0-9a-fA-F]{6})\]",r"[color=#\1]",text).replace("[-]","[/color]").replace("\r","")

class DescriptionBox(GridLayout):
  def __init__(self,**kwargs):
    super(DescriptionBox,self).__init__(**kwargs)
    self.rows = 5
    self.cols = 1
    self.part = None
    self.nameLabel = Label(text = "", font_size = 14, bold = True, size_hint_y = None,height=16)
    self.descLabel = Label(text = "_", markup=True, size_hint_y = None, width=300) 
    self.traitLabel1 = TraitLabel(None,size_hint_y = None,height=16)
    self.traitLabel2 = TraitLabel(None,size_hint_y = None,height=16)
    self.add_widget(self.nameLabel)
    self.add_widget(self.descLabel)
    self.add_widget(self.traitLabel1)
    self.add_widget(self.traitLabel2)
    self.add_widget(Widget(size_hint_y = None))

  def updateDisplay(self):
    self.nameLabel.text = self.part.displayName if self.part and "displayName" in self.part else ""
    self.descLabel.text_size = (self.width * .9 if self.width and self.width != 100 else 300 ,None)
    self.descLabel.text = colorMarkupTranslate(self.part.description) if self.part and "description" in self.part else ""
    self.descLabel.texture_update()
    self.descLabel.size = self.descLabel.texture_size
    self.traitLabel1.setTrait(self.part.traits[0] if self.part and "traits" in self.part and 0 in range(len(self.part.traits)) else None)
    self.traitLabel2.setTrait(self.part.traits[1] if self.part and "traits" in self.part and 1 in range(len(self.part.traits)) else None)

  def setPart(self,part):
    self.part = part
    self.updateDisplay()

class TraitLabel(Label):

  def __init__(self,trait,**kwargs):
    self.trait = trait
    super(TraitLabel,self).__init__(**kwargs)
    self.setTrait(trait)
    self.visible = False
  def setTrait(self,trait):
    self.trait = trait
    if trait:
      self.text = trait.displayStr
      Window.bind(mouse_pos=self.on_mouse_move)
      self.traitDetailTooltip = ColorLabel(bgcolor = (.2, .2, .2), text_size = (400,None), size_hint = (None,None), markup=True,  text = colorMarkupTranslate(self.trait.descStr))
    else:
      Window.unbind(mouse_pos=self.on_mouse_move)
      self.text = ""
  def on_mouse_move(self,window,pos):
    toolTip = self.traitDetailTooltip
    rootWindow = self.get_root_window()
    if self.collide_point(*pos):
      if not self.visible:
        self.visible = True
        toolTip.top = pos[1]
        toolTip.x = pos[0]
        toolTip.texture_update()
        toolTip.size = [ 20 + c for c in toolTip.texture_size ]
        Clock.schedule_once(lambda dt: rootWindow.add_widget(toolTip),0)
    elif self.visible:
      Clock.schedule_once(lambda dt: rootWindow.remove_widget(toolTip),.1)
      self.visible = toolTip in rootWindow.children

class AlignedLabel(GridLayout):
  def __init__(self, halign="left", **kwargs):
    if halign not in ["left","right"]:
      raise ValueError(align +" not left or right")
    super(AlignedLabel, self).__init__(**kwargs)
    self.rows = 1
    self.cols = 2
    labelArgs = kwargs
    for badArg in ["pos","x","y","size","size_hint","size_hint_x","size_hint_y","pos_hint"]:
      if badArg in labelArgs:
        del labelArgs[badArg]
    self.label = Label(halign = halign,**labelArgs)
    self.spacer = Widget()

    if halign == "left":
      self.add_widget(self.label)
      self.add_widget(self.spacer)
    else:
      self.add_widget(self.spacer)
      self.add_widget(self.label)
  
  def on_size(self,*args):
    if self.width == 0:
      return
    labelSize = self.label.texture_size[0] / float(self.width)
    self.label.size_hint_x = labelSize
    self.spacer.size_hint_x = 1 - labelSize

class ColorLabel(Label):
  def redraw(self, *args):
    self.bg_rect.size = self.size
    self.bg_rect.pos = self.pos
  def __init__(self, bgcolor,  **kwargs):
    super(ColorLabel,self).__init__(**kwargs)
    with self.canvas.before:  
      Color(*bgcolor)    
      self.bg_rect = Rectangle(pos = self.pos, size = self.size)
    self.bind(pos=self.redraw,size=self.redraw)

class ColorBar(GridLayout):
  def __init__(self, bgcolor, percentFull, text,  **kwargs):
    super(ColorBar,self).__init__(**kwargs)
    self.rows = 1
    self.cols = 2
    self.add_widget(ColorLabel(bgcolor, size_hint_x = percentFull ))
    self.add_widget(Label(text = text, size_hint_x = 1 - percentFull))

class ResourceBar(GridLayout):
  resourceToPartType = {"Weight": "hull", "Heat": "cockpit", "Power": "power core"}
  def __init__(self, resource, cost, capacity, bgcolor, **kwargs):
    super(ResourceBar,self).__init__(**kwargs)
    self.spacing_vertical = 5
    if(capacity == 0):
      self.rows = 1
      self.cols = 2
      self.add_widget(Label(text = "Please select a " + self.resourceToPartType[resource]))
      self.add_widget(Label(text = str(cost)+"/"+str(capacity), color=(1,0,0,1), size_hint_x = .25)) #Spacer with usage
    elif(capacity >= cost):
      self.rows = 1
      self.cols = 4
      squishBar = GridLayout(rows=3,cols=1, size_hint_x = (cost-10)/2000.)
      squishBar.add_widget(Widget(size_hint_y = .1))
      squishBar.add_widget(ColorLabel(bgcolor,color=(0,0,0,1), text=resource, size_hint_y = .8))
      squishBar.add_widget(Widget(size_hint_y = .1))
      self.add_widget(squishBar)
      self.add_widget(Widget( size_hint_x = (capacity - cost) / 2000.)) #Spacer 1
      self.add_widget(ColorLabel((0,1,0,1), size_hint_x = 20/2000.))
      self.add_widget(Label(text = str(cost)+"/"+str(capacity), color=(0,1,0,1), size_hint_x = 1 - (capacity-10) / 2000.)) #Spacer with usage
    else:
      self.rows = 1
      self.cols = 4
      squishBar = GridLayout(rows=3,cols=1, size_hint_x = (capacity-10)/2000.)
      squishBar.add_widget(Widget(size_hint_y = .1))
      squishBar.add_widget(ColorLabel(bgcolor, size_hint_y = .8,color=(0,0,0,1), text=resource))
      squishBar.add_widget(Widget(size_hint_y = .1))
      self.add_widget(squishBar)
      self.add_widget(ColorLabel(bgcolor, size_hint_x = 20/2000., size_hint_y = 1))
      squishBar2 = GridLayout(rows=3,cols=1, size_hint_x = (cost - capacity)/2000.)
      squishBar2.add_widget(Widget(size_hint_y = .1))
      squishBar2.add_widget(ColorLabel((1,0,0,1), size_hint_y = .8))
      squishBar2.add_widget(Widget(size_hint_y = .1))
      self.add_widget(squishBar2)
      self.add_widget(Label(text = str(cost)+"/"+str(capacity),color=(1,0,0,1), size_hint_x = 1 - (cost-10) / 2000.)) #Spacer with usage

class BarResourceDisplay(GridLayout):
  def __init__(self, **kwargs):
    super(BarResourceDisplay,self).__init__(**kwargs)
    self.rows = 3
    self.cols = 1
    self.kwargs = kwargs

  def updateDisplay(self):
    self.clear_widgets()

    weightCost     = self.part["weightCost"]     if self.part and "weightCost" in self.part else 0
    weightCapacity = self.part["weightCapacity"] if self.part and "weightCapacity" in self.part else 0
    powerCost      = self.part["powerCost"]      if self.part and "powerCost" in self.part else 0
    powerCapacity  = self.part["powerCapacity"]  if self.part and "powerCapacity" in self.part else 0
    heatCost       = self.part["heatCost"]       if self.part and "heatCost" in self.part else 0
    heatCapacity   = self.part["heatCapacity"]   if self.part and "heatCapacity" in self.part else 0

    self.add_widget(ResourceBar("Weight",weightCost, weightCapacity, bgcolor = (1,1,1,1),**self.kwargs))
    self.add_widget(ResourceBar("Power",powerCost,powerCapacity,   bgcolor = (0,.8,1,1),**self.kwargs))
    self.add_widget(ResourceBar("Heat",heatCost, heatCapacity,   bgcolor = (1,.7,0,1), **self.kwargs))

  def setPart(self, part):
    self.part = part
    self.updateDisplay()

class IconResourceDisplay(GridLayout):
  def __init__(self, **kwargs):
    super(IconResourceDisplay,self).__init__(**kwargs)
    self.rows = 1
    self.cols = 8
    self.part = None

  def updateDisplay(self):
    self.clear_widgets()
    self.add_widget(ColorLabel(bgcolor = (1,1,1,1), color = (0,0,0,1), bold = True,text = "W", size_hint_x = .1))
    self.add_widget(Label( bold = True, color=(1,1,1,1), text = str(self.part["weightCost"] if self.part and "weightCost" in self.part else 0), size_hint_x = .15))
    self.add_widget(ColorLabel(bgcolor = (0,.8,1,1), color = (0,0,0,1), bold = True,text = "P", size_hint_x = .1))
    self.add_widget(Label( bold = True, color=(0,.8,1,1), text = str(self.part["powerCost"] if self.part and "powerCost" in self.part else 0), size_hint_x = .15))
    self.add_widget(ColorLabel(bgcolor = (1,.7,0,1), color = (0,0,0,1), bold = True,text = "H", size_hint_x = .1))
    self.add_widget(Label( bold = True, color=(1,.7,0,1), text = str(self.part["heatCost"] if self.part and "heatCost" in self.part else 0), size_hint_x = .15))
    self.add_widget(ColorLabel(bgcolor = (.5,.5,.5,1), color = (0,0,0,1), bold = True,text = "G", size_hint_x = .1))
    self.add_widget(Label( bold = True, color=(1,1,1,1), text = str(self.part["grade"] if self.part and "grade" in self.part else 0), size_hint_x = .15))

  def setPart(self, part):
    self.part = part
    self.updateDisplay()

class ResistsGrid(GridLayout):
  def __init__(self, **kwargs):
    self.normalResistAttribs = {"perforationResist", "decayResist", "distortionResist", "ignitionResist", "overloadResist", "detonationResist"}
    super(ResistsGrid,self).__init__(**kwargs)
    self.rows = 1
    self.cols = 2
    self.part = None

  def updateDisplay(self):
    self.clear_widgets()
    self.rows = 1
    self.cols = 2
    normalResists = GridLayout(size_hint_x=.75,rows=2,cols=6)
    for dType in self.normalResistAttribs:
      normalResists.add_widget(Image(source="icons/"+dType[:-6]+".png"))
      normalResists.add_widget(Label(text=str(self.part[dType]/10. if self.part and dType in self.part  else 0)))
    comboResist = GridLayout(size_hint_x=.25,rows=1,cols=2)

    comboResist.add_widget(Image(source="icons/genesis.png"))
    comboResist.add_widget(Label(text=str( self.part["comboResist"]/10. if self.part and "comboResist" in self.part  else 0)))
    self.add_widget(normalResists)
    self.add_widget(comboResist)

  def setPart(self, part):
    self.part = part
    self.updateDisplay()


class DamageTypeIcon(GridLayout):
  def __init__(self, damageTypes, **kwargs):
    super(DamageTypeIcon, self).__init__(**kwargs)
    self.rows = 1
    self.cols = 3
    self.add_widget(Widget(size_hint_x = .2))
    icons = [ Image(size_hint_y = 1, source="icons/"+dType.lower()+".png") for dType in damageTypes ]
    if len(icons) == 1:
      self.add_widget(icons[0])
    else:
      icons[0].texture = icons[0].texture.get_region(0,0,icons[0].texture.width / 2, icons[0].texture.height)
      icons[1].texture = icons[1].texture.get_region(icons[1].texture.width / 2,0,icons[1].texture.width / 2, icons[1].texture.height)
      splitIcon = GridLayout(spacing = 0, rows = 1, cols = 2)
      splitIcon.add_widget(icons[0])
      splitIcon.add_widget(icons[1])
      self.add_widget(splitIcon)

    self.add_widget(Widget(size_hint_x = .2))


class PartMarkButtons(GridLayout):
  def __init__(self, field, part, parentHash, **kwargs):
    self.field = field
    super(PartMarkButtons, self).__init__(**kwargs)
    self.cols = 5 if part[1].type not in ["MAIN_WEAPON","WING_WEAPON"] else 6
    self.rows = 1 
    self.part = part
    self.mark = 1
    if part[1].type in ["MAIN_WEAPON","WING_WEAPON"]: 
      self.add_widget(DamageTypeIcon(part[1].damageTypes, size_hint_x = .1))
    self.add_widget(AlignedLabel(text = part[1].parentName, halign = 'left', size_hint_x = .6))

    self.buttonsByMark = {}
    for i in range(1,5):
      btn = ToggleButton(text = str(i), group="markButtons"+str(parentHash), size_hint_x = .08)
      btn.bind(on_release=self.onButtonPress)
      self.buttonsByMark[i]=btn
      self.add_widget(btn)
    

  def onButtonPress(self, btn):
    global currentPart
    if(btn.state == 'down'):
      self.mark = (int(btn.text))
      currentPart = self.part[self.mark]
      currentShip[self.field] = currentPart
    else:
      currentPart = None
      currentShip[self.field] = currentPart
    self.parent.parent.parent.parent.parent.tabsBySlot[self.field].updateColor()
    onShipUpdate()
    onPartUpdate()

class PartSelectScrollView(ScrollView):

  def __init__(self,field, parts,**kwargs):
    super(PartSelectScrollView,self).__init__(**kwargs)
    self.bar_width = 5
    self.do_scroll_x = False
    with self.canvas:
      bar_alpha = 1

    self.layout = GridLayout(size_hint_y=None, spacing = 1)
    self.layout.cols = 1 
    self.layout.padding = 10
    self.layout.row_default_height = 20
    self.layout.row_force_default = True
    self.layout.bind(minimum_height=self.layout.setter('height'))
    self.buttonsByPartId = {}
    for part in parts:
      btn = PartMarkButtons(field, part, self.__hash__())
      self.buttonsByPartId[part[1].id] = btn
      self.layout.add_widget(btn)

    self.add_widget(self.layout)

  def setPart(self, part):
    print part.id, part.mark
    pmb = self.buttonsByPartId[part.id]
    btn = pmb.buttonsByMark[part.mark]
    btn.state = "down"
    pmb.onButtonPress(pmb.buttonsByMark[part.mark])

class PartTypeTab(TabbedPanelHeader):
  def __init__(self, partField,race,**kwargs):
    super(PartTypeTab,self).__init__(**kwargs)
    self.partField = partField
    (displayName, partType, _) = Gunship.partSlotsByField[partField]

    self.content = GridLayout(rows = 1, cols = 1)
    self.partsList = PartSelectScrollView(partField, buyablePartsByTypeAndRace[partType][race], size_hint = (.4,1))
    self.content.add_widget(self.partsList)

  def updateColor(self):
    if currentShip[self.partField].part:
      self.background_color = (0,1,0,.5)
    else:
      self.background_color = (1,0,0,1)

  def on_release(self, *args):
    global currentPart
    super(PartTypeTab,self).on_release(*args)
    self.updateColor()
    if currentShip[self.partField].part:
      self.partsList.setPart(currentShip[self.partField].part)
    currentPart = currentShip[self.partField].part
    onPartUpdate()

class PartPicker(TabbedPanel):

  def on_tab_height(self, *l):
    Clock.unschedule(self._update_tab_height)
    Clock.schedule_once(self._update_tab_height, 0)
  def on_tab_width(self, *l):
    self._tab_layout.width = self._tab_strip.width = self.tab_width
    self._reposition_tabs()  
  def _update_tab_height(self, *l):
    if self.tab_height:
      for tab in self.tab_list:
          tab.size_hint_y = 1
      tsh = self.tab_height * len(self._tab_strip.children)
    else:
      # tab_width = None
      tsh = 0
      for tab in self.tab_list:
        if tab.size_hint_y:
          # size_hint_x: x/.xyz
          tab.size_hint_y = 1
          #drop to default tab_height
          tsh += 40
        else:
          # size_hint_x: None
          tsh += tab.height
    self._tab_strip.height = tsh
    self._reposition_tabs()
  def add_widget(self, widget, index=0):
    content = self.content
    if content is None:
        return
    if isinstance(widget, TabbedPanelHeader):
      self_tabs = self._tab_strip
      self_tabs.add_widget(widget, index)
      widget.group = '__tab%r__' % self_tabs.uid
      self.on_tab_height()
    else:
      super(PartPicker, self).add_widget(widget, index)
  def _update_tabs(self, *l):
    self_content = self.content
    if not self_content:
        return
    # cache variables for faster access
    tab_pos = self.tab_pos
    tab_layout = self._tab_layout
    tab_layout.clear_widgets()
    scrl_v = ScrollView(size_hint=(None, 1))
    tabs = self._tab_strip
    tabs.rows = 99
    parent = tabs.parent
    if parent:
      parent.remove_widget(tabs)
    scrl_v.add_widget(tabs)
    scrl_v.pos = (0, 0)
    self_update_scrollview = self._update_scrollview


    # update scrlv width when tab width changes depends on tab_pos
    if self._partial_update_scrollview is not None:
        tabs.unbind(width=self._partial_update_scrollview)
    self._partial_update_scrollview = partial(
        self_update_scrollview, scrl_v)
    tabs.bind(width=self._partial_update_scrollview)

    # remove all widgets from the tab_strip
    self.clear_widgets(do_super=True)
    tab_width = self.tab_width

    widget_list = []
    tab_list = []
    pos_letter = tab_pos[0]
    # left ot right positions
    # one row containing the tab_strip and the content
    self.cols = 2
    self.rows = 1
    # tab_layout contains two blank dummy widgets for spacing
    # "vertically" and the scatter containing scrollview
    # containing tabs
    tab_layout.cols = 1
    tab_layout.rows = 3
    tab_layout.size_hint = (None, 1)
    tab_layout.width = tab_width
    scrl_v.width = tab_width
    self_update_scrollview(scrl_v)

    # rotate the scatter for vertical positions
    tab_list = (scrl_v, )

    widget_list = (tab_layout, self_content)

    # add widgets to tab_layout
    add = tab_layout.add_widget
    for widg in tab_list:
      add(widg)

    # add widgets to self
    add = self.add_widget
    for widg in widget_list:
      add(widg)
  def __init__(self,race,**kwargs):
    super(PartPicker,self).__init__(**kwargs)
    self.tabsBySlot = {}
    self.tab_width = 150
    self.tab_height = 20
    self._tab_layout = StripLayout(cols=1, rows=99)
    self.cols = 1
    self._tab_strip = TabbedPanelStrip(
                       tabbed_panel=self, rows=99,
                       cols=1, size_hint=(None, None),
                       height=self.tab_height, width=self.tab_width)

    self.do_default_tab = False
    for partField in Gunship.partFields:
      tab = PartTypeTab(partField,race,text=Gunship.partSlotsByField[partField].name)
      self.tabsBySlot[partField] = tab
      self.add_widget(tab)

class ShipNameInput(TextInput):
  pat = '[A-Za-z0-9_ -]'
  def insert_text(self, substring, from_undo=False):
    return super(ShipNameInput, self).insert_text("".join(re.findall(self.pat,substring)), from_undo=from_undo)

class ShipSelector(GridLayout):
  def __init__(self,onShipChange,**kwargs):
    global currentShip
    self.callback = onShipChange
    self.filePath = "ships.GODBUILDER"
    super(ShipSelector,self).__init__(**kwargs)
    self.listeners = []
    if not os.path.isfile(self.filePath):
      with open(self.filePath,'w') as f:
        defaultShip = Gunship("Ship 1",HUMAN)
        f.write("0\n" + defaultShip.serialize())
    with open(self.filePath,'r') as f:
      lines = f.read().splitlines()
      self.ships = [ Gunship.deserialize(rawShip) for rawShip in lines[1:] ]
    currentShip = self.ships[int(lines[0])]
    self.cols = 4

    self.dropdown = DropDown()
    for ship in self.ships:
      btn = Button(text= ship.name, color = raceToColorMap[ship.race], size_hint_y=None, height=20)
      btn.ship = ship
      btn.bind(on_release=lambda btn: self.dropdown.select(btn.ship))
      self.dropdown.add_widget(btn)
    self.mainbutton = Button(text='Select a ship', size_hint=(None, 1))
    self.mainbutton.bind(on_release=self.dropdown.open)

    self.dropdown.bind(on_select=lambda instance, ship: self.changeShip(ship))
    self.add_widget(self.mainbutton)
    self.dropdown.select(currentShip)
    nameChangeButton = Button(text = "rename",size_hint_y=1)
    nameChangeButton.bind(on_release = self.doRenamePopup)
    self.add_widget(nameChangeButton)
    newShipButton = Button(text = "New Ship",size_hint_y=1)
    newShipButton.bind(on_release = self.doNewShipPopup)
    self.add_widget(newShipButton)
    self.gModeBtn = Button(text = getAO(), size_hint_y = 1)
    self.gModeBtn.bind(on_release=self.alphaOmegaSwap)
    self.add_widget(self.gModeBtn)

    self._keyboard = Window.request_keyboard(self._keyboard_closed, self, 'text')
    self._keyboard.bind(on_key_down=self._on_keyboard_down)

  def _keyboard_closed(self):
    self._keyboard.unbind(on_key_down=self._on_keyboard_down)
    self._keyboard = None

  def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
    if keycode[1] == 'q':
      self.alphaOmegaSwap(self.gModeBtn)
      return True
    return False


  def alphaOmegaSwap(self, btn):
    if(currentShip.race != GUANTRI):
      if getAO() != ALPHA:
        swapAO()
        currentShip.updateNumericValues()
        onShipUpdate()
        onPartUpdate()
      btn.text = getAO()
      return
  
    btn.unbind(on_release=self.alphaOmegaSwap)
    swapAO()
    btn.text = getAO()
    currentShip.updateNumericValues()
    onShipUpdate()
    onPartUpdate()
    btn.bind(on_release=self.alphaOmegaSwap)

  def doNewShipPopup(self,*args):
    popupContent = GridLayout(rows = 2, cols = 1)
    newShipTextInput = ShipNameInput(focus=True, text="",multiline=False)
    newShipTextInput.race = HUMAN
    dropdown = DropDown()
    for race in races:
      btn = Button(text = raceToStringMap[race], color = raceToColorMap[race],size_hint_y = None, height=20)
      btn.race = race
      btn.bind(on_release=lambda btn:dropdown.select(btn))
      dropdown.add_widget(btn)
    mainbutton = Button(text=raceToStringMap[HUMAN], color=raceToColorMap[HUMAN])
    mainbutton.race = HUMAN
    mainbutton.bind(on_release=dropdown.open)
    dropdown.bind(on_select=lambda instance, btn: (map(lambda attr: mainbutton.__setattr__(attr,btn.__getattribute__(attr)), ["text","color","race"]) and False) or newShipTextInput.__setattr__("race",btn.race))
    popupContent.add_widget(mainbutton)
    popupContent.add_widget(newShipTextInput)

    self.newShipPopup = Popup(title="New Ship", content=popupContent, auto_dismiss=False, size_hint=(.2,.2))
    self.newShipPopup.open()
    newShipTextInput.bind(on_text_validate=self.doNewShip)

  def doNewShip(self,instance):
    global currentShip
    newName = instance.text
    if newName in [ship.name for ship in self.ships]:
      instance.parent.title="Error: Name in use"
      instance.parent.title_color=(1,0,0,1)
      instance.focus = True
    else:
      currentShip = Gunship(instance.text,instance.race)
      self.ships.append(currentShip)
      self.changeShip(currentShip)
      self.newShipPopup.dismiss()

  def doRenamePopup(self,*args):
    nameChangeTextInput = ShipNameInput(focus=True, text=currentShip.name,multiline=False)
    nameChangePopup = Popup(title="Rename Ship", content=nameChangeTextInput, auto_dismiss=False, size_hint=(.2,.2))
    nameChangePopup.open()
    nameChangeTextInput.bind(on_text_validate=self.doRename)

  def doRename(self,instance):
    newName = instance.text
    if newName in [ship.name for ship in self.ships]:
      instance.parent.title="Error: Name in use"
      instance.parent.title_color=(1,0,0,1)
      instance.focus = True
      return
    else:
      oldName = currentShip.name
      instance.parent.parent.parent.dismiss()
      currentShip.name = newName
      self.mainbutton.text = newName
      for btn in self.dropdown.children[0].children:
        if btn.ship.name == oldName:
          btn.text = newName
          btn.ship.name = newName
          return



  def saveShips(self):
    with open(self.filePath,'w') as f:
      f.write("\n".join([str(self.ships.index(currentShip))] + [ship.serialize() for ship in self.ships]))


  def changeShip(self,ship):
    global currentShip 
    currentShip = ship
    self.saveShips()
    self.mainbutton.text = ship.name
    self.mainbutton.color = raceToColorMap[ship.race]
    self.callback()

class ShipBuilder(GridLayout):
  def __init__(self,**kwargs):
    global onShipUpdate, onPartUpdate
    super(ShipBuilder,self).__init__(**kwargs)
    self.rows = 3
    self.cols = 1
    onShipUpdate = (lambda : self.shipDisplay.setPart(currentShip) )
    onPartUpdate = (lambda : self.partDisplay.setPart(currentPart) )


    self.partPickers = {}
    for race in races: 
      self.partPickers[race] = PartPicker(race = race,size_hint_x = .35)


    self.partDisplay = StatDisplayGrid(size_hint_x = .65, cols = 2, rows = 1) 
    self.partDisplay.add_widget(DescriptionBox(size_hint_x = .6))

    rightColumn = GridLayout(cols = 1, rows = 3, size_hint_x = .3)
    rightColumn.add_widget(ResistsGrid(size_hint_y = .2))
    rightColumn.add_widget(IconResourceDisplay(size_hint_y = .1))
    rightColumn.add_widget(StatsDisplay( row_default_height = 20, row_force_default = True, spacing = 2, padding = 5))
    self.partDisplay.add_widget(rightColumn)


    self.shipDisplay = StatDisplayGrid(cols = 2, rows = 3)
    self.shipDisplay.add_widget(BarResourceDisplay(row_default_height = 20, row_force_default = True, size_hint_x = .5))
    self.shipDisplay.add_widget(ResistsGrid(row_default_height = 40, row_force_default = True))
    self.shipDisplay.add_widget(PartNameList(row_default_height = 20, row_force_default = True))
    self.shipDisplay.add_widget(StatsDisplay(row_default_height = 20, row_force_default = True, spacing = 2, padding = 5))
    self.shipDisplay.add_widget(Widget(size_hint_y = 2))

    self.topHalf = GridLayout(pos_hint = {'top':1, 'x':1}, size_hint = (1,.45), rows = 1, cols = 2)
    self.bottomHalf = GridLayout(pos_hint = {'top':.45, 'x':1}, size_hint = (1,.5), rows = 1, cols = 1)
    self.bottomBar = GridLayout(pos_hint = {'top':.05, 'x':1}, size_hint = (1,.05), rows = 1, cols = 2)

    self.bottomHalf.add_widget(self.shipDisplay)

    self.add_widget(self.topHalf)
    self.add_widget(self.bottomHalf)
    self.add_widget(self.bottomBar)

    self.shipPicker = ShipSelector(self.onShipChange)
    self.bottomBar.add_widget(self.shipPicker)

 
#    Clock.schedule_once((lambda dt: Window.set_title("ship factory")),-1)
  

  def onShipChange(self):
    self.shipDisplay.setPart(currentShip)
    self.topHalf.clear_widgets()
    pickerForRace = self.partPickers[currentShip.race]
    self.topHalf.add_widget(pickerForRace)
    self.topHalf.add_widget(self.partDisplay)
    for tab in pickerForRace.tab_list:
      tab.updateColor()

    Clock.schedule_once((lambda dt: (pickerForRace.switch_to(pickerForRace.tab_list[-1]) and False) or pickerForRace.tab_list[-1].on_release()),1) 



class ShipBuilderApp(App):
  def build(self):
    self.shipBuilder = ShipBuilder(size = Window.size)
    return self.shipBuilder
  def on_stop(self):
    self.shipBuilder.shipPicker.saveShips()

if __name__ == '__main__':
  ShipBuilderApp().run()

