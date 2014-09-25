#!/usr/bin/env python
APP_VERSION = "0.0.5" #Don't change this if you want patching to work properly
screenWidth,ScreenHeight=1024,786 #I'm not saying that you can't change these, I'm just saying that if you do, the window layout might break forever and leave you sobbing uncontrollably.

# if True blocks denote logical separations of global level code. I use them so I can collapse them using my editor. 
if True: # Imports
  from string import ascii_uppercase
  from time import sleep
  import urllib2
  import subprocess
  import os.path
  import csv
  import re
  import sqlite3
  import sys
  from distutils.version import StrictVersion
  from functools import partial
  from collections import namedtuple
  import kivy
  import cProfile
  kivy.require('1.8.0') # It's funny because kivy 1.8.1 has all sorts of new features I won't get to use.

  from kivy.config import Config
  Config.set("graphics","width",screenWidth)
  Config.set("graphics","height",ScreenHeight)
  Config.write()
  # Gotta do this here because kivy is INTERESTING

  from kivy.app import App
  from kivy.uix.label import Label
  from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelHeader, StripLayout, TabbedPanelStrip, TabbedPanelContent, TabbedPanelHeader
  from kivy.uix.floatlayout import FloatLayout
  from kivy.uix.gridlayout import GridLayout
  from kivy.uix.anchorlayout import AnchorLayout
  from kivy.uix.stacklayout import StackLayout
  from kivy.uix.boxlayout import BoxLayout
  from kivy.uix.button import Button
  from kivy.uix.togglebutton import ToggleButton
  from kivy.uix.checkbox import CheckBox
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
  from kivy.graphics.instructions import Callback
  from kivy.uix.textinput import TextInput
if True: # Global defs
  ALPHA = "Alpha"
  OMEGA = "Omega"

  yyTrans={"Yin":ALPHA, "Yan":OMEGA}

  CANNON="Cannon"
  SATELLITE="Satellite"
  MINES="Mines"
  BEAM="Beam"
  WAVE="Wave"
  SCATTERGUN="Scattergun"
  HOMING="Homing"
  BOMBING="Bombing"
  MACHINE_GUN="Machine Gun"

  weaponTypeTrans={"Gunship_PartKeyword_Cannon":CANNON, "Gunship_PartKeyword_Satellite":SATELLITE, "Gunship_PartKeyword_Mines":MINES, "Gunship_PartKeyword_Beam":BEAM, "Gunship_PartKeyword_Wave":WAVE, "Gunship_PartKeyword_Scattergun":SCATTERGUN, "Gunship_PartKeyword_Homing":HOMING, "Gunship_PartKeyword_Bombing":BOMBING, "Gunship_PartKeyword_Machinegun":MACHINE_GUN} 
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

  damageTypes = [ 'detonation', 'overload', 'ignition', 'distortion', 'decay', 'perforation']

  HUMAN = 1
  GUANTRI = 2
  AR = 3
  CHORION = 4

  races = [HUMAN, GUANTRI, AR, CHORION]

  raceToStringMap = { HUMAN:"Human", GUANTRI:"Guantri", AR:"Ar",  CHORION:"Chorion" }
  raceToColorMap = {HUMAN: (1,1,0,1), GUANTRI: (0,1,1,1), AR: (0,1,0,1), CHORION: (1,0,0,1)}

  INFINITY = u"\u221E".encode('utf-8')

  OPTIONAL = "Optional"
  REQUIRED = "Required"
  RESET = "Reset"
  ADD = "Add"
  SPREAD = "Spread"
  DIVIDE = "Divide"
  NA = "N/A"
  UNKNOWN = "???"

  projectilesPerTarget = { ALPHA: {214001: 1, 214002: 6,114007: 2,414000: 2,414005: 8,115002: 2,115007: 6,115010: 2,115011: 16,215001: 2,215007: 6,215013: 3,315003: 2,315010: 7,315012: 9,415005: 4,415006: 2,415002: 2,415014: 2}, OMEGA: { 214001: 2, 214002: 3 }}
  lockRequired = { ALPHA : { 214001: REQUIRED,114005: RESET,314000: RESET,314005: REQUIRED,314006: RESET,314007: REQUIRED,414002: REQUIRED,414005: REQUIRED,414007: REQUIRED,115001: REQUIRED,115002: REQUIRED,115007: RESET,115010: REQUIRED,115012: RESET,115011: REQUIRED,215001: REQUIRED,215003: RESET,215013: REQUIRED,315003: REQUIRED,315012: RESET,315007: RESET,315004: REQUIRED,315005: REQUIRED,415005: REQUIRED,415002: REQUIRED,415007: RESET,415014: RESET }, OMEGA: {214001: OPTIONAL}}
  multiTargetMode = { ALPHA : {214003: NA, 114005: ADD, 114005: ADD, 314005: ADD, 214005: SPREAD, 214002: DIVIDE,414005: DIVIDE,115002: DIVIDE,115010: DIVIDE,115011: DIVIDE,215001: DIVIDE,215003: ADD,215013: DIVIDE,315003: DIVIDE,315004: ADD,415005: DIVIDE }, OMEGA: {215001: DIVIDE,215003: ADD,215013: DIVIDE, 214002: ADD, 214003: SPREAD,214005: NA} }
   
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

  def setAO(x):
    global AO
    if x in [ALPHA, OMEGA]:
      AO = x

  def aoInv(x):
    if x == ALPHA:
      return OMEGA
    if x == OMEGA:
      return ALPHA
    return ALPHA #The inverse of bad data is the beginning.

  def mkInt(x,default=0):
    return int(x) if re.match("^[0-9-]+$",x) else default

  def mkFlt(x,default=0.0):
    return float(x) if re.match("^[-.0-9]+$",x) else default

  def rstr(x):
    return str(round(x,2)) if x.__class__ == float else str(x)

  currentShip = None
  currentPart = None
  onShipUpdate = None
  onPartUpdate = None

class PartMark(dict): # The full set of info available about a specific ship part at a given mark. Includes both alpha and omega data.  
  attribs = [ "id", "rawVals", "defaultRace", "type", "className", "weaponType", "rankRequired", "possibleRaces", "creditCosts", "expRequired", "prereqParts","traits", "isPrereqFor", "mark", "codeName", "alphaOmega", "damageTypes", "grade", "scoreGained", "weightCost", "weightCapacity", "powerCost", "powerCapacity", "heatCost", "heatCapacity", "shield", "shieldRecharge", "energy", "energyRegen", "perforationResist", "decayResist", "distortionResist", "ignitionResist", "overloadResist", "detonationResist", "protection", "handling", "numWingWeapons", "speed", "boost", "purgeCooldown", "abilityCooldown", "lockingSpeed", "targetingArea", "targetingRange", "minimumRange", "maximumRange", "accuracy", "shotCooldown", "projectileCount", "projectileRange", "ammo", "lockingTime", "maxTargets", "damage", "markOwned", "currentExp", "parentName", "displayName", "description", "range","multiTargetMode","projectilesPerTarget","lockRequired", "targets", "rawAmmo", "rawDamage", "mystery", "additionalWonders", "DPS","damagePerLoad","ammoLifespan","fireRate","isBuyable","locking","cooldown"]
  cooldownFinder = re.compile(""".*Cooldown\[-\]: ([0-9]*) secs""",flags=re.MULTILINE|re.DOTALL)
  def __getattr__(self, key):
    return self.__getitem__(key)

  def __setattr__(self, key, value):
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

  def __init__(self, *args, **kw):
    self[ALPHA] = {}
    self[OMEGA] = {}
    super(PartMark,self).__init__(*args,**kw)

  def copy(self):
    retval = PartMark()
    retval[ALPHA] = self[ALPHA].copy()
    retval[OMEGA] = self[OMEGA].copy()
    return PartMark(Alpha = self[ALPHA].copy(), Omega = self[OMEGA].copy())

  def init(self,partVals,names):
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
    self[ao]["protection"] = mkInt(partVals[38])
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
        self[ao]["description"] = re.sub("""\n[^a-zA-Z]*\n""","\n",names[self.id]["desc"+str(self.mark)])

        cooldownMatch = re.match(PartMark.cooldownFinder,self[ao]["description"])
        if cooldownMatch:
          self[ao]["cooldown"] = mkFlt(cooldownMatch.group(1))

      self.updateNumericValues(ao)
    return self

  def updateNumericValues(self,ao):
    if self[ao]["type"] in [MAIN_WEAPON, WING_WEAPON]:

      # 0 accuracy = perfect
      self[ao]["accuracy"] = str(self[ao]["accuracy"]) if self[ao]["accuracy"] else "Perfect"

      self[ao]["range"] = (rstr(self[ao]["minimumRange"]) + " - " if self[ao]["minimumRange"] else "" ) + rstr(self[ao]["maximumRange"]) + (" ["+ rstr(self[ao]["projectileRange"]) + "]" if self[ao]["projectileRange"] and self[ao]["projectileRange"] != self[ao]["maximumRange"] else "" )

      self[ao]["multiTargetMode"] = multiTargetMode[ao][self.id] if self.id in multiTargetMode[ao] else UNKNOWN

      self[ao]["lockRequired"] = lockRequired[ao][self.id] if self.id in lockRequired[ao] else OPTIONAL

      self[ao]["locking"] = rstr(self[ao]["lockingTime"])+"/"+self[ao]["lockRequired"] if self[ao]["lockingTime"] else "None"

      if self[ao]["lockRequired"] == RESET:
        self[ao]["shotCooldown"] = self[ao]["lockingTime"]

      if (self[ao]["shotCooldown"] < 1.0):
        self[ao]["fireRate"] = rstr(1.0/self[ao]["shotCooldown"]) +"/s"
      else:
        self[ao]["fireRate"] = "1 shot / " + rstr(self[ao]["shotCooldown"]) +"s"

      if self.id in projectilesPerTarget[ao]:
        self[ao]["projectilesPerTarget"] = projectilesPerTarget[ao][self.id]
        self[ao]["damage"] = rstr(self[ao]["rawDamage"]) + "x"+str(self[ao]["projectilesPerTarget"]) + " ("+rstr(self[ao]["rawDamage"]*self[ao]["projectilesPerTarget"])+")"
        self[ao]["ammo"]  = rstr(self[ao]["rawAmmo"]) + "/"+str(self[ao]["projectilesPerTarget"]) + " ("+rstr(self[ao]["rawAmmo"]/self[ao]["projectilesPerTarget"])+")"
      else:
        self[ao]["projectilesPerTarget"] = 1
        self[ao]["damage"] = rstr(self[ao]["rawDamage"])
        self[ao]["ammo"]  = rstr(self[ao]["rawAmmo"])

      if self[ao]["maxTargets"] > 1 and self[ao]["weaponType"] != WAVE:
        self[ao]["targets"] = str(self[ao]["maxTargets"])+"/"+self[ao]["multiTargetMode"]

      self[ao]["DPS"] = self[ao]["projectilesPerTarget"]*self[ao]["rawDamage"]/self[ao]["shotCooldown"]
      self[ao]["damagePerLoad"] = self[ao]["rawDamage"]*self[ao]["rawAmmo"] if self[ao]["weaponType"] != SATELLITE else INFINITY
      self[ao]["ammoLifespan"] = rstr(self[ao]["rawAmmo"]*self[ao]["shotCooldown"] / (self[ao]["projectilesPerTarget"] if "projectilesPerTarget" in self[ao] else 1)) + "s"if self[ao]["weaponType"] != SATELLITE else INFINITY

      if(self[ao]["weaponType"] == BEAM):
        self[ao]["damage"] += "/s"
        self[ao]["DPS"] = self[ao]["rawDamage"]
        self[ao]["damagePerLoad"] /= 10.0
        self[ao]["fireRate"] = "Continuous"
        self[ao]["ammoLifespan"] = rstr(self[ao]["rawAmmo"] / 10.0) + "s"

      if self.id == 315006:
        # Fuck. The. Mini.
        numMiniShots = int(self[ao]["rawAmmo"]-1)/5
        self[ao]["DPS"] = self[ao]["rawDamage"] / 5.0
        self[ao]["damagePerLoad"] = numMiniShots * self[ao]["rawDamage"]
        self[ao]["ammoLifespan"] = rstr(numMiniShots*5) + "s"
        self[ao]["fireRate"] = "1 shot / 5s" 
class Trait: # The full set of info available about a trait. 
  triggerTypes = {'All Green', 'Passive', 'Contained', 'Warrior', 'Drift', 'Attacker', 'Savior', 'Response', 'Harvester', 'Vengeance', 'Velocity', 'Relentless', 'Sentinel', 'Defender', 'Red Alert'}
  # Strings for getting trait names and descriptions. I didn't feel like scanning memory for these strings and getting the localized versions. Instead we do this bullshit. You're welcome, everyone!
  miscTraitPropTrans = {'Area': "Targeting Area",'Range': "Targeting Range",'Lock_Systems': "Targeting Area, Targeting Range & Locking Speed",'Amp_Dmg': "Damage",'Cooldown': "Ability Cooldown",'Dark_Dmg': "Perforation, Decay & Distortion Damage",'Dec_Dmg': "Decay Damage",'Energy': "Energy",'Energy_Regen': "Energy Regen",'EnR_Cld': "Energy Regen & Ability Cooldown",'Handling': "Handling",'Light_Dmg': "Ignition, Overload & Detonation Damage",'Lock': "Locking Speed",'Negative': "Negative Effects",'Ovr_Dmg': "Overload Damage",'Per_Dis_Dmg': "Perforation & Distortion Damage",'Purge': "Purge Cooldown",'Resistances': "All Resistances",'Rft_Dmg': "Reflect Damage",'Shield': "Shield",'Siphon': "Siphon",'Spd_Hnd': "Speed & Handling",'Spd_Boo': "Speed & Boost",'Speed': "Speed",'Terminus': "Targeting Area, Targeting Range & Locking Speed" }
  triggerTypeTrans = {'Cnt':'Contained','Pas':'Passive', 'Dft': 'Drift', 'Rel': 'Relentless', 'Ven': 'Vengeance', 'Har': 'Harvester', 'Vel': 'Velocity', 'Red': 'Red Alert', 'War': 'Warrior', 'Rsp': 'Response', 'Att': 'Attacker', 'Def': 'Defender','All': 'All Green','Sen': 'Sentinel','Sav': 'Savior'}
  firstWordTrans = {'Loc' : "Locking Speed",'Amp' : "Amplify",'Mob' : "Mobility",'Cld' : "Ability Cooldown",'Res' : "Resistances",'Spd' : "Speed",'Eng' : "Engines",'Nrg' : "Restore Energy",'ER'  : "Energy Regen",'Trn' : "Transmission",'Tgt' : "Targeting",'Sys' : "Systems",'Sur' : "Survival",'Rng' : "Targeting Range",'Area': "Targeting Area",'Hnd' : "Handling",'Amp' : "Amplify",'Dep' : "Deplete",'Rst' : "Restore",'Rft' : "Reflect",'Pur' : "Purge Cooldown",'Coo' : "Cooling"}
  restWordTrans = {'Dec' : "Decay",'Shd' : "Shield",'Nrg' : "Energy",'Aur' : "Aura",'Aura': "Aura",'Dmg' : "Damage",'Ovr' : "Overload",'Bub' : "Bubble"}
  debuffStrTrans = {"Nrg_Lk": "Energy Leak","Sta": "Stall","Shd_Bur": "Shield Burst","Vul": "Vulnerability","Shd_Lk": "Shield Leak","Amm_Brn": "Ammo Burn","Dys": "Dysfunction","Unb": "Unbalanced","Slo": "Slow","Mul": "Multiple","Rad_Jam": "Radar Jam"}
  miscNameMap = {'Special': "Special",'Jnt_Ass': "Joint Assault",'Sca_Sht': "Scattered Shots",'Chn_Att': "Chain Attack",'Sph': "Siphon Shield",'Freefall_A': "Resitances-",'Freefall_O': "Handling-",'TB_60': "Area Blast 60"}

  def __init__(self):
    pass

  def predef(self, **kvargs):
    for (key,val) in kvargs.iteritems():
      self.__setattr__(key,val)

  def init(self, nameAndId, desc, effects):
    self.rawNameAndId = nameAndId
    self.rawEffects = effects
    self.id = mkInt(nameAndId[0])
    self.descStr = re.sub("Trait_Prop[a-zA-Z_]*",self.traitPropTrans, re.sub("\{([0-9])_([0-9])\}",lambda m: effects[int(m.group(1))-1][int(m.group(2))],desc).replace('\\n','\n'))
    self.displayStr = self.triggerTrans(nameAndId[1])
    self.calcStatMods()
    self.isActive = self.triggerType in ['Passive'] 
    return self

  def traitPropTrans(self,traitProp):
    traitProp = traitProp.group(0)[11:]
    if traitProp in Trait.miscTraitPropTrans:
      return Trait.miscTraitPropTrans[traitProp]
    elif "Wpn_Mod" in traitProp:
      return camelToReadable(traitProp[8:])
    else:
      return traitProp.replace("_"," ")

  def changedStats(self,rawEffect):
    traitProp = [x  for x in rawEffect if "Trait_Prop_" in x][0][11:]
    preSplit = ""
    if traitProp in Trait.miscTraitPropTrans:
      preSplit = Trait.miscTraitPropTrans[traitProp]
    else:
      preSplit = traitProp.replace("_"," ")
    return [ stat[0].lower() + "".join([ c for c in stat[1:] if c != " " ]) for stat in re.split(" *, *| *& *",preSplit)]

  def calcStatMods(self):
    self.statMods = {}
    self.triggerType = self.displayStr.partition(':')[0]
    if self.triggerType in Trait.triggerTypes:
      sign = '-' if ("Deplete" in self.displayStr or self.displayStr[-1] == "-") else ''
      for rawEffect in self.rawEffects:
        for stat in self.changedStats(rawEffect):
          val = sign+(rawEffect[2] if stat!='reflect' else rawEffect[1])
          valPair = (mkFlt(val[:-1])/100. if val and val[-1]=="%" else mkFlt(val), mkFlt(rawEffect[3]))
          if "Damage" == stat[-6:]:
            stat = stat[:-6]
          if stat in ["damage"] + damageTypes:
            stat += "Mult"
          if stat in ["energy", "shield"]:
            stat+="PerSec"
          if stat == "allResistances":
            for dType in damageTypes:
              self.statMods[dType+"Resist"] = valPair
          else:
            self.statMods[stat] = valPair
    else:
      self.triggerType = ""

  def triggerTrans(self,triggerName):
    triggerName = triggerName[12:]
    if triggerName[0:3] in Trait.triggerTypeTrans:
      return Trait.triggerTypeTrans[triggerName[0:3]] + ": " + self.effectTrans(triggerName[4:])
    elif triggerName[0:3] == 'Wpn' and triggerName[4:] in Trait.debuffStrTrans :
      return "Weapon Mod: " + Trait.debuffStrTrans[triggerName[4:]]
    elif triggerName[0:2] == 'AB':
      return "Area Blast "+triggerName[3:]
    elif triggerName in Trait.miscNameMap:
      return Trait.miscNameMap[triggerName]
    else:
      print "Warning: Could not decode trigger name '" + triggerName +"'. Returned 'Special' instead."
      return "Special"

  def effectTrans(self,effectName):
    sign,nameParts = ('-',effectName[:-1].split('_')) if effectName[-1] == '-' else ('+',effectName.split('_'))
    return Trait.firstWordTrans[nameParts[0]] + ( " " + " ".join([Trait.restWordTrans[part] for part in nameParts[1:]]) if nameParts[1:] else sign) 

if True: # Version checking and patching.

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
    subprocess.call(['shipBuilder.exe'])
    exit()

  #check to see if there's a newer version of the data
  try:
    newVersion = urllib2.urlopen('https://raw.githubusercontent.com/turntekGodhead/God-Factory-Ship-Builder/master/VERSION').read().replace("\n","")
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
if True: # Convert the raw data into code objects. 
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
    traitsById[int(splitRows[0])] = Trait().init(splitRows,traitStrings[splitRows[2]],[traitEffectValuesByEffectId[effectId] for effectId in splitRows[3].split(';')])

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
    partRow = PartMark().init(row.split(':'),partStrings)
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

  print "done parsing"

class Gunship(dict):

  PartSlot = namedtuple('PartSlot', 'name type part')
  partFields = ["hull","cockpit","wings","thrusters","powerCore","shieldGenerator","mainComputer","weaponControlUnit","device","addOn","mainWeapon","wingWeapon1","wingWeapon2"]
  partSlotsByField = { "hull": PartSlot("Hull", HULL, None), "cockpit": PartSlot("Cockpit", COCKPIT, None), "wings": PartSlot("Wings", WINGS, None), "thrusters": PartSlot("Thrusters", THRUSTERS, None), "powerCore": PartSlot("Power Core", POWER_CORE, None), "shieldGenerator": PartSlot("Shield Generator", SHIELD_GENERATOR, None), "mainComputer": PartSlot("Main Computer", MAIN_COMPUTER, None), "weaponControlUnit": PartSlot("WCU", WEAPON_CONTROL_UNIT, None), "device": PartSlot("Device", DEVICE, None), "addOn": PartSlot("Add-on", ADD_ON, None), "mainWeapon": PartSlot("Main Weapon", MAIN_WEAPON, None), "wingWeapon1": PartSlot("Wing Weapon 1", WING_WEAPON, None), "wingWeapon2": PartSlot("Wing Weapon 2", WING_WEAPON, None) }
  directSummableAttribs = [ "weightCost", "powerCost", "heatCost", "weightCapacity", "powerCapacity", "heatCapacity", "grade",  "shield", "shieldRecharge", "energy", "energyRegen", "perforationResist", "decayResist", "distortionResist", "ignitionResist", "overloadResist", "detonationResist", "protection", "handling", "speed", "boost", "purgeCooldown", "abilityCooldown", "lockingSpeed", "targetingRange", "reflect", "shieldPerSec", "energyPerSec", "damageMult", "perforationMult", "decayMult", "distortionMult", "ignitionMult", "overloadMult", "detonationMult"]
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
    self.ammoMod = 1.0
    self.wingAmmoMod = 1.0
    if self.numWingWeapons == 1:
      self.wingWeapon2 = Gunship.PartSlot("Wing Weapon 2", WING_WEAPON, None)

    self.traits =  [ (trait,self[field].part.displayName) for field in Gunship.partFields if self[field].part for trait in self[field].part.traits ]

    for attrib in Gunship.directSummableAttribs:
      self[attrib] = sum([ self[field].part[attrib] for field in Gunship.partFields if self[field].part and attrib in self[field].part]) + \
                     sum([trait.statMods[attrib][0] for trait,_ in self.traits if trait.isActive and attrib in trait.statMods])

    if self.numWingWeapons == 2 && self.wingWeapon1.part and self.wingWeapon2.part:
      self.wingAmmoMod *= .8


    self["class"] = min(8,max(1,self.grade / 100))
    if self.weightCapacity > 0:
      weightRatio = float(self.weightCost) / float(self.weightCapacity)
      if weightRatio <= 1:
        self.ammoMod     *= 1.0 + (1.0 - weightRatio)/2.0
        self.wingAmmoMod *= 1.0 + (1.0 - weightRatio)/2.0
      else:
        percentOver = (weightRatio - 1.0) * 100.0
        self.handling          *= 1.0-(16.0 + percentOver*44.0/20.0)/100.0
        self.protection       *= 1.0-(16.0 + percentOver*44.0/20.0)/100.0
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
    for attrib in ["handling", "protection", "energy", "energyRegen", "perforationResist", "decayResist", "distortionResist", "ignitionResist", "overloadResist", "detonationResist", "speed", "boost", "abilityCooldown", "purgeCooldown"]:
      self[attrib] = int(self[attrib])

    #TODO: Check to see if stuff like ability cooldown is calculated before display rounding by the game.
    self.purge = 180 * 100.0 / self.purgeCooldown if self.purgeCooldown else INFINITY
    self.deviceCooldown = self.device.part.cooldown * 100.0 / (self.abilityCooldown if self.abilityCooldown else 100) if self.device.part else None
    self.addOnCooldown = self.addOn.part.cooldown   * 100.0 / (self.abilityCooldown if self.abilityCooldown else 100) if self.addOn.part else None


  def updateSubPartValues(self):
    self.mainWeaponCopy = self.mainWeapon.part.copy() if self.mainWeapon.part else None
    self.wingWeapon1Copy = self.wingWeapon1.part.copy() if self.wingWeapon1.part else None
    self.wingWeapon2Copy = self.wingWeapon2.part.copy() if self.wingWeapon2.part else None
    wingWeapons = [ww for ww in [self.wingWeapon1Copy, self.wingWeapon2Copy] if ww and ww.weaponType != MINES ] #Mines aren't really a relevant part of DPS or ammo lifespan.
    
    for weapon in [self.mainWeaponCopy, self.wingWeapon1Copy, self.wingWeapon2Copy]:
      if weapon:
        weapon.rawDamage *= 1.0 + (self.damageMult if "damageMult" in self else 0) + sum([self[dType+"Mult"] / len(weapon.damageTypes) for dType in weapon.damageTypes if dType+"Mult" in self])
        weapon.rawAmmo *= self.ammoMod if weapon.type == MAIN_WEAPON else self.wingAmmoMod
        weapon.lockingTime *= 100.0/self.lockingSpeed if self.lockingSpeed else 1.0
        weapon.maximumRange *= self.targetingRange/100.0 if self.targetingRange else 1.0
        weapon.updateNumericValues(getAO())


    if self.mainWeaponCopy and wingWeapons:
      mainLS = mkFlt(self.mainWeaponCopy.ammoLifespan[:-1])
      wingLS = [ mkFlt(ww.ammoLifespan[:-1]) for ww in wingWeapons if ww.weaponType != SATELLITE ]

      if SATELLITE in [weapon.weaponType for weapon in wingWeapons]:
        self.ammoLifespan = str(mainLS)+"s/" + (str(max(wingLS)) + "s/" if wingLS and max(wingLS) > mainLS else "") + INFINITY
      else:
        self.ammoLifespan = str(min(mainLS,sum(wingLS)))+"s/" + str(max(mainLS,sum(wingLS)))+"s"

      mainDPS = self.mainWeaponCopy.DPS
      self.DPS = [(mainDPS+ww[0],[(mainDPS,self.mainWeaponCopy.damageTypes), ww]) for ww in sorted([(weapon.DPS,weapon.damageTypes) for weapon in wingWeapons], key=lambda x: x[0], reverse=True)]
      dplList = [(weapon.damagePerLoad,weapon.damageTypes) for weapon in ([self.mainWeaponCopy] + wingWeapons)]
      self.damagePerLoad = (sum([dpl[0] for dpl in dplList if dpl[0] != INFINITY]),dplList)


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

if True: #Kivy helper functions.
  TwoNone = (None,None) 
  def walk(widget):
    return widget.children + [ grandchild for child in widget.children for grandchild in walk(child) ]

  def colorMarkupTranslate(text):
    return re.sub(r"\[([0-9a-fA-F]{6})\]",r"[color=#\1]",text).replace("[-]","[/color]").replace("\r","")

  def getColorByAO():
    if currentShip.race == GUANTRI:
      if getAO() == ALPHA:
        return (0, 1, 1, 1)
      else:
        return (1, .647, 0, 1)
    else:
        return (0, 0, 1, 1)

  def drawGridAndBorder(gL,color=None, clear=True):
    draw_grid(gL,color,clear)
    draw_border(gL,color,False)

  def draw_grid(gL,color=None, clear = True):
    if not color:
      color = getColorByAO()
    x,y,top,right = gL.x,gL.y,gL.top,gL.right
    cols = gL.cols if gL.cols else (len(gL.children)-1) / gL.rows +1
    colXList = [ child.x for child in gL.children[-2:-(cols+1):-1]]
    rowYList = [ child.y for child in gL.children[:(cols-1):-cols]]
    if clear:
      gL.canvas.after.clear()
    with gL.canvas.after:
      Color(*color)
      for colX in colXList:
        Line(points=[colX,y,colX,top],width=1)
      for rowY in rowYList:
        Line(points=[x,rowY,right,rowY],width=1)

  def draw_border(widget,color=None, clear = True):
    if not color:
      color = getColorByAO()
    x,y,top,right = widget.x,widget.y,widget.top,widget.right
    if clear:
      widget.canvas.after.clear()
    with widget.canvas.after:
      Color(*color)
      Line(points=[x,y, right,y, right,top, x,top, x,y],width=1)
if True: #Kivy helper classes. None of these have GoD Factory-specific logic.
  class SaneLabel(Label):
    def _callback(self,*args):
      if self.texture_size:
        self.width = self.texture_size[0]

    def __init__(self,  **kwargs):
      super(SaneLabel, self).__init__(**kwargs)
      self.size_hint_x = None
      self.bind(texture_size=self._callback)

  class AlignedLabel(GridLayout):
    def __init__(self, halign="left", padding=[2,0,2,0], size_hint_x=None, **kwargs):
      if halign not in ["left","right"]:
        raise ValueError(halign +" not left or right")
      super(AlignedLabel, self).__init__(padding=padding,**kwargs)
      self.rows = 1
      self.cols = 2
      self.size_hint_x=size_hint_x
      labelArgs = kwargs.copy()
      for badArg in ["pos","x","y","size","size_hint","size_hint_x","size_hint_y","pos_hint"]:
        if badArg in labelArgs:
          del labelArgs[badArg]
      self.label = SaneLabel(halign = halign,**labelArgs)
      self.spacer = Widget()
      self.label.bind(width=self._callback,texture_size=self._callback,text=self._callback)
      if halign == "left":
        self.add_widget(self.label)
        self.add_widget(self.spacer)
      else:
        self.add_widget(self.spacer)
        self.add_widget(self.label)
    def _callback(self,*args):
      if self.label.texture_size[0] != self.width:
        self.width = self.label.texture_size[0]

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

  class DumbRow(GridLayout):
    def __init__(self,widgets,**kwargs):
      super(DumbRow,self).__init__(rows=1, **kwargs)
      for widget in widgets:
        self.add_widget(widget)

  class SmartRow(GridLayout):
    def __init__(self,widgets,**kwargs):
      super(SmartRow,self).__init__(rows=1,cols=len(widgets), **kwargs)
      self.size_hint_x=None
      for widget in widgets:
        widget.bind(width=self._callback)
        self.add_widget(widget)
    def _callback(self,*args):
      self.width = sum([child.width for child in self.children ])

  class SmartGrid(GridLayout):
    def __init__(self,**kwargs):
      if "rows" in kwargs and "cols" not in kwargs:
        print "warning, rows but no cols given: picking large number of cols" 
        cols=99
      super(SmartGrid,self).__init__(**kwargs)
      self.size_hint=(None,None)

    def add_widget(self,widget, index=0):
      widget.bind(size=self._callback,pos=self._callback)
      super(SmartGrid,self).add_widget(widget,index)
      self._callback()

    def _callback(self,*args):
      if not self.width or not self.height:
        #not worth
        return
      cols = self.cols if self.cols else (len(self.children)-1) / self.rows +1
      childWidth  = sum([ child.width  + self.spacing[0] for child in self.children[-1:-(cols+1):-1]] ) - self.spacing[0] + self.padding[0]+self.padding[2]
      childHeight = sum([ child.height + self.spacing[1] for child in self.children[::-cols]])          - self.spacing[1] + self.padding[1]+self.padding[3]
      if abs(1.0-float(childWidth)/float(self.width)) > .01:
        self.width = childWidth
      if abs(1.0-float(childHeight)/float(self.height)) > .01:
        self.height = childHeight

class StatDisplayGrid(GridLayout):

  def __init__(self,field = None,**kwargs):
    super(StatDisplayGrid, self).__init__(**kwargs)
    self.part = None

  def updateDisplay(self):
    map((lambda child : child.updateDisplay() if "updateDisplay" in dir(child) else 0), walk(self))

  def setPart(self,part):
    self.part = part
    map((lambda child : child.setPart(part) if "setPart" in dir(child) else 0), walk(self))

class StatsDisplay(SmartGrid):
  sharedDisplayAttribs = [ "shield", "shieldRecharge", "energy", "energyRegen","speed", "boost", "handling", "purgeCooldown", "abilityCooldown", "lockingSpeed", "targetingArea", "targetingRange" ]
  extraAttribsByPart = {
    GUNSHIP: ["class"],
    DEVICE: ["cooldown"], ADD_ON: ["cooldown"],
    HULL: ["weightCapacity"], POWER_CORE: ["powerCapacity"], COCKPIT: ["heatCapacity"],
    WINGS: ["numWingWeapons"],
    MAIN_WEAPON: ["weaponType", "damage", "fireRate", "range", "ammo", "accuracy", "locking", "targets", "DPS", "damagePerLoad", "ammoLifespan" ]
  }

  extraAttribsByPart[WING_WEAPON] = extraAttribsByPart[MAIN_WEAPON]

  def __init__(self, overrideDisplayAttribs = None, **kwargs):
    super(StatsDisplay, self).__init__(**kwargs)
    self.displayAttribs = StatsDisplay.sharedDisplayAttribs
    self.extraAttribs = []
    self.overrideDisplayAttribs = overrideDisplayAttribs
    self.cols = 2
    self.part = None
    self.bind(pos=(lambda *args: Clock.schedule_once(lambda dt:drawGridAndBorder(self,clear=True),0)))

  def updateDisplay(self):

    self.clear_widgets()
    if self.part:
      part = self.part
      for attrib in (self.overrideDisplayAttribs if self.overrideDisplayAttribs else self.extraAttribs + self.displayAttribs):
        if not attrib in part:
          if self.overrideDisplayAttribs:
            self.add_widget(AlignedLabel(text=camelToReadable(attrib), halign='left', size_hint_x=None))
            self.add_widget(AlignedLabel(text=NA, halign='left', size_hint_x=None))
          continue
        if not part[attrib]:
          if self.overrideDisplayAttribs:
            self.add_widget(AlignedLabel(text=camelToReadable(attrib), halign='left', size_hint_x=None))
            self.add_widget(AlignedLabel(text=rstr(part[attrib]), halign='left', size_hint_x=None))
          continue
        if attrib == "DPS" and "weaponType" in part and part.weaponType == BEAM:
          if self.overrideDisplayAttribs:
            attrib = "damage"
          else:
            continue

        self.add_widget(AlignedLabel(text=camelToReadable(attrib), halign='left', size_hint_x=None))
        # sorry, not sorry
        if attrib in ["DPS", "damage"] and "damageTypes" in part:
          self.add_widget(SmartRow([AlignedLabel(text=rstr(part[attrib])),DamageTypeIcon(part.damageTypes,size=(20,20),size_hint=(None,None))],spacing=[5,0]))
        elif attrib == "damageTypes":
          self.add_widget(DamageTypeIcon(part[attrib],size_hint_x=None))
        else:
          self.add_widget(AlignedLabel(text=rstr(part[attrib]), halign='left', size_hint_x=None))

  def setPart(self, part):
    self.part = part
    self.extraAttribs = StatsDisplay.extraAttribsByPart[part.type] if part and "type" in part and part.type in StatsDisplay.extraAttribsByPart else []
    self.updateDisplay()

if True: # Ship Display classes
  class ShipDisplay(StatDisplayGrid):

    def __init__(self, **kwargs):
      super(ShipDisplay,self).__init__(**kwargs)
      self.cols = 2
      self.rows = 1
      
      leftColumn = GridLayout(rows=2,cols=1,size_hint_x = .7)
      topLeft    = SmartGrid(rows=1,cols=2)
      topLeftLeft = SmartGrid(rows=2,cols=1)
      topLeftRight = GridLayout(rows=1,cols=2)
      bottomLeft = GridLayout(rows=1,cols=2, size_hint_x = None, spacing=[5,0])
      rightColumn = GridLayout(rows=3,cols=1, size_hint_x = .3)

      topLeftLeft.add_widget(BarResourceDisplay(width = Window.width*.35, height=60, size_hint_x = None))
      topLeftLeft.add_widget(ResistsGrid(height=40, size_hint=(None,None)))
      topLeftRight.add_widget(StatsDisplay(padding = [5,1,5,1], spacing=[5,1], row_default_height = 20, row_force_default = True,overrideDisplayAttribs=["shield","energy","speed","handling"]))
      topLeftRight.add_widget(StatsDisplay(padding = [5,1,5,1], spacing=[5,1], row_default_height = 20, row_force_default = True,overrideDisplayAttribs=["shieldRecharge","energyRegen","boost","class"]))
      topLeft.add_widget(topLeftLeft)
      topLeft.add_widget(topLeftRight)

      partNameList=PartNameList(row_default_height = 20, row_force_default = True, size_hint_x = None, padding=[5,0,5,0])
      bottomLeft.add_widget(partNameList)
      bottomLeft.add_widget(ShipSpecial(size_hint_x = None))

      leftColumn.add_widget(topLeft)
      leftColumn.add_widget(bottomLeft)

      rightColumn.add_widget(TraitList(size_hint_y=None))
      rightColumn.add_widget(StatsDisplay(padding = [5,1,5,1], spacing=[5,1], row_default_height = 20, row_force_default = True,overrideDisplayAttribs=["shieldPerSec","energyPerSec","reflect"]))
      rightColumn.add_widget(Widget())
      # rightColumn.add_widget(Widget())
      self.add_widget(leftColumn)
      self.add_widget(rightColumn)
      # leftColumn.bind(pos=(lambda *args: Clock.schedule_once(lambda dt: draw_border(leftColumn,color=(1,0,0,1)),.1)))
      # leftColumn.bind(pos=(lambda *args: Clock.schedule_once(lambda dt: draw_border(leftColumn,color=(1,0,0,1)),.1)))
      # partNameList.bind(pos=(lambda *args: Clock.schedule_once(lambda dt: draw_border(partNameList,color=(0,1,0,1)),.1)))
      # Clock.schedule_once(lambda dt: [ draw_border(w,color=(0,1,0,1),clear=False) for w in [leftColumn,topLeft,topLeftLeft,topLeftRight,bottomLeft,rightColumn,self]])
  class PartNameList(SmartGrid):
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
  class ShipSpecial(GridLayout):
    def __init__(self, **kwargs):
      super(ShipSpecial,self).__init__(**kwargs)
      self.cols = 1

    def updateDisplay(self):
      self.clear_widgets()
      ship = self.part
      if ship:
        ship.updateNumericValues()
        ship.updateSubPartValues()
        cooldownGrid = SmartGrid(row_default_height = 20, row_force_default = True, cols = 2, spacing=[5,0], padding=[5,0,5,0])
        # if ship.device.part:
        #   cooldownGrid.add_widget(AlignedLabel(text=ship.device.part.displayName, halign='left'))
        #   cooldownGrid.add_widget(AlignedLabel(text=rstr(ship.deviceCooldown)+"s", halign='left'))
        cooldownGrid.add_widget(AlignedLabel(text="Purge", halign='left'))
        cooldownGrid.add_widget(AlignedLabel(text=rstr(ship.purge)+"s"+(" (" + str(ship.purgeCooldown) + " purge cooldown)" if "purgeCooldown" in ship else ""), width=0, halign='left'))

        if ship.device.part:
          cooldownGrid.add_widget(AlignedLabel(text=ship.device.part.displayName, halign='left'))
          cooldownGrid.add_widget(AlignedLabel(text=rstr(ship.deviceCooldown)+"s"+(" (" + str(ship.abilityCooldown) + " ability cooldown)" if "abilityCooldown" in ship else ""), halign='left'))
        else: 
          cooldownGrid.add_widget(AlignedLabel(text="Select a device"))
          cooldownGrid.add_widget(AlignedLabel(text=NA))

        if ship.addOn.part:
          cooldownGrid.add_widget(AlignedLabel(text=ship.addOn.part.displayName, halign='left'))
          cooldownGrid.add_widget(AlignedLabel(text=rstr(ship.addOnCooldown)+"s"+(" (" + str(ship.abilityCooldown) + " ability cooldown)" if "abilityCooldown" in ship else ""), halign='left'))
        else: 
          cooldownGrid.add_widget(AlignedLabel(text="Select an Add-on"))
          cooldownGrid.add_widget(AlignedLabel(text=NA))

        weaponOverview = SmartGrid(row_default_height = 20, row_force_default = True, cols = 2, spacing=[5,0], padding=[5,0,5,0])

        weaponOverview.add_widget(AlignedLabel(text="Ammo Lifespans", halign='left'))
        if "ammoLifespan" in ship:
          weaponOverview.add_widget(AlignedLabel(text=ship.ammoLifespan, halign='left'))
        else:
          weaponOverview.add_widget(AlignedLabel(text="<Select multiple weapons>"))
        if "DPS" in ship:
          dpsAppend = 1 if len(ship.DPS) == 2 else ""
          for (total,partsWithIcons) in ship.DPS:
            weaponOverview.add_widget(AlignedLabel(text="DPS" + (" (Main + Wing "+str(dpsAppend)+")" if dpsAppend else ""), halign='left'))
            # weaponOverview.add_widget(AlignedLabel(text = rstr(total)))
            if dpsAppend:
              dpsAppend+=1

            stack = []
            stack.append(SaneLabel(text = rstr(total)))
            stack.append(SaneLabel(text = ' ('))
            for (part,damageType) in partsWithIcons:
              stack.append(SaneLabel(text = rstr(part)))
              stack.append(DamageTypeIcon(damageType))
              stack.append(SaneLabel(text = '+'))
            stack.pop()
            stack.append(SaneLabel(text = ')'))
            dpsLine = GridLayout(rows = 1, size_hint_x = .7)
            [ dpsLine.add_widget(w) for w in stack ]
            weaponOverview.add_widget(dpsLine)
        else:
          weaponOverview.add_widget(AlignedLabel(text="DPS", halign='left'))
          weaponOverview.add_widget(AlignedLabel(text="<Select multiple weapons>"))


        weaponOverview.add_widget(AlignedLabel(text="Total Damage", halign = 'left'))
        if "damagePerLoad" in ship:
          weaponOverview.add_widget(AlignedLabel(text=rstr(ship.damagePerLoad[0])))
        else:
          weaponOverview.add_widget(AlignedLabel(text="<Select multiple weapons>"))

        # dplLine = GridLayout(rows = 1, size_hint_x = .7)
        # for (part,damageType) in ship.damagePerLoad[1]:
        #   dplLine.add_widget(Label(text = rstr(part)))
        #   dplLine.add_widget(DamageTypeIcon(damageType))
        # weaponOverview.add_widget(dplLine)
        # self.add_widget(Widget(size_hint_x=.3))

        self.add_widget(cooldownGrid)
        self.add_widget(weaponOverview)
        validWeapons = [w for w in [ship.mainWeaponCopy, ship.wingWeapon1Copy, ship.wingWeapon2Copy] if w]
        weaponValGrid = SmartGrid(row_default_height=20,row_force_default=True, spacing=[5,0], padding=[5,0,5,0], cols = 1+len(validWeapons))
        weaponValGrid.add_widget(AlignedLabel(text="Weapon", halign='left',  size_hint_x = None))
        for weapon in validWeapons:
          weaponValGrid.add_widget(AlignedLabel(text=weapon.displayName, halign='left',  size_hint_x = None))
        for attrib in ["DPS","fireRate", "range", "ammo", "locking", "damagePerLoad", "ammoLifespan" ]:
          weaponValGrid.add_widget(AlignedLabel(text=camelToReadable(attrib), halign='left',  size_hint_x = None))
          for weapon in validWeapons:
            if attrib == "DPS" and "weaponType" in weapon and weapon.weaponType == BEAM:
              attrib = "damage"
            if not attrib in weapon:
              weaponValGrid.add_widget(AlignedLabel(text=NA, size_hint_x = None))
              continue
            if not weapon[attrib]:
              weaponValGrid.add_widget(AlignedLabel(text=NA, size_hint_x = None))
              continue
            # sorry, not sorry
            if attrib in ["DPS", "damage"] and "damageTypes" in weapon:
              weaponValGrid.add_widget(SmartRow([AlignedLabel(text=rstr(weapon[attrib])),DamageTypeIcon(weapon.damageTypes,size=(20,20),size_hint=(None,None))],spacing=[5,0]))
            else:
              weaponValGrid.add_widget(AlignedLabel(text=rstr(weapon[attrib]), size_hint_x = None))
        self.add_widget(weaponValGrid)
        # Clock.schedule_once(lambda dt: weaponValGrid._callback(),.04)
        # Clock.schedule_once(lambda dt: self._trigger_layout(),.05)
        weaponValGrid.bind(pos=(lambda *args: Clock.schedule_once(lambda dt: drawGridAndBorder(weaponValGrid,clear=False),0)))
        cooldownGrid.bind(pos=(lambda *args: Clock.schedule_once(lambda dt: draw_border(cooldownGrid),0)))
        # Clock.schedule_once(lambda dt: draw_border(weaponOverview),0)

        # Clock.schedule_once(lambda dt: draw_grid(self),0)
        # Clock.schedule_once(lambda dt: draw_border(self,color=(1,0,0,1),clear=False),0)

    def setPart(self, part):
      self.part = part
      self.updateDisplay()
  class TraitList(GridLayout):

    def __init__(self, **kwargs):
      super(TraitList, self).__init__(**kwargs)
      self.cols = 1
      self.rows = 2
      self.ship = None
      self.traitLabels = SmartGrid(cols=1)
      self.add_widget(SaneLabel(text="Traits (Mouseover for details)",size_hint_y=None,height=20))
      self.add_widget(self.traitLabels)
      self.traitLabels.bind(height=lambda *args: self.__setattr__('height',self.traitLabels.height+20))

    def updateDisplay(self):
      [l.children[0].setVisible(False) for l in self.traitLabels.children if self.traitLabels.children]
      self.traitLabels.clear_widgets()
      
      if "traits" in self.ship:
        for (trait, sourceName) in self.ship.traits:
          if trait.statMods:
            cb = CheckBox(size_hint = TwoNone, size=(20,20),active=trait.isActive)
            cb.trait = trait
            cb.bind(active=self.onCB)
          else:
            cb = Widget(size_hint = TwoNone, size=(20,20))
          self.traitLabels.add_widget(SmartRow([cb,TraitLabel(trait,source=sourceName,size_hint = TwoNone,height=20)],size_hint_y = None,height=20))
    def onCB(self,cb,value):
      cb.trait.isActive = value
      if set(cb.trait.statMods.keys()) & set(Gunship.directSummableAttribs):
        self.ship.updateNumericValues()
        self.ship.updateSubPartValues()
        self.parent.parent.updateDisplay()
        # onPartUpdate()

    def setPart(self, part):
      self.ship = part
      self.updateDisplay()

class DescriptionBox(GridLayout):
  def __init__(self,**kwargs):
    super(DescriptionBox,self).__init__(**kwargs)
    self.padding=[5,0,5,0]
    self.spacing=[0,10]
    self.rows = 5
    self.cols = 1
    self.part = None
    self.nameLabel = SaneLabel(text = "", font_size = 14, bold = True, size_hint_y = None,height=16)
    self.descLabel = SaneLabel(text = "_", markup=True, size_hint_y = None, width=300) 
    self.traitLabel1 = TraitLabel(None,size_hint_y = None,height=16)
    self.traitLabel2 = TraitLabel(None,size_hint_y = None,height=16)
    self.add_widget(self.nameLabel)
    self.add_widget(self.descLabel)
    self.add_widget(self.traitLabel1)
    self.add_widget(self.traitLabel2)
    self.add_widget(Widget(size_hint_y = None))
    self.bind(pos=self._callback,size=self._callback)
    # self.bind(pos=(lambda *args: Clock.schedule_once(lambda dt: draw_border(self,color=(1,0,0,1)),.1)))
    # self.bind(pos=(lambda *args: Clock.schedule_once(lambda dt: draw_grid(self,color=(1,0,0,1),clear=False),.1)))


  def _callback(self,*args):
    self.descLabel.text_size = (self.width * .95 if self.width and self.width != 100 else 300 ,None)
    self.descLabel.text = colorMarkupTranslate(self.part.description) if self.part and "description" in self.part else ""
    self.descLabel.texture_update()
    self.descLabel.size = self.descLabel.texture_size


  def updateDisplay(self):
    self.nameLabel.text = self.part.displayName if self.part and "displayName" in self.part else ""
    self.traitLabel1.setTrait(self.part.traits[0] if self.part and "traits" in self.part and 0 < len(self.part.traits) else None)
    self.traitLabel2.setTrait(self.part.traits[1] if self.part and "traits" in self.part and 1 < len(self.part.traits) else None)
    self._callback()

  def setPart(self,part):
    self.part = part
    self.updateDisplay()

class TraitLabel(SaneLabel):

  def __init__(self,trait,source="",**kwargs):
    super(TraitLabel,self).__init__(**kwargs)
    self.source = source
    self.traitDetailTooltip = None
    self.visible=True
    self.popupVisible = False
    self.setTrait(trait)

  def setVisible(self,newVis):
    self.visible=newVis

  def setTrait(self,trait):
    self.trait = trait
    if self.traitDetailTooltip:
      Window.remove_widget(self.traitDetailTooltip)
    if trait:
      self.text = trait.displayStr
      self.traitDetailTooltip = ColorLabel(bgcolor = (.2, .2, .2), text_size = (400,None), size_hint = (None,None), markup=True,  text = ("[color=#CC00FF]Source: "+self.source+"[/color]\n" if self.source else "") + colorMarkupTranslate(self.trait.descStr))
      Window.bind(mouse_pos=self.on_mouse_move)
    else:
      Window.unbind(mouse_pos=self.on_mouse_move)
      self.text = ""
  def on_mouse_move(self,window,pos):
    if not self.visible:
      if self.popupVisible:
        window.remove_widget(toolTip)
      return
    toolTip = self.traitDetailTooltip
    if self.collide_point(*pos):
      if not self.popupVisible:

        self.popupVisible = True
        toolTip.texture_update()
        toolTip.size = [ 20 + c for c in toolTip.texture_size ]
        newPos = (pos[0]-toolTip.size[0],pos[1]-toolTip.size[1] if pos[1]-toolTip.size[1]>0 else 0)
        toolTip.pos = newPos
        window.add_widget(toolTip)
        # Clock.schedule_once(lambda dt: toolTip.setter("pos")(self,newPos),.1)
        # Clock.schedule_once(lambda dt: window.add_widget(toolTip) if window else None,.1)
    elif self.popupVisible:
      window.remove_widget(toolTip)
      self.popupVisible = False
      # Clock.schedule_once(lambda dt: window.remove_widget(toolTip)if window else None,0)
      # self.visible = toolTip in window.children if window else self.visibler

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
  def __init__(self, height=60, **kwargs):
    super(BarResourceDisplay,self).__init__(height=height,**kwargs)
    self.rows = 3
    self.cols = 1
    self.size_hint_y = None
    self.kwargs = kwargs

  def updateDisplay(self):
    self.clear_widgets()

    weightCost     = self.part["weightCost"]     if self.part and "weightCost" in self.part else 0
    weightCapacity = self.part["weightCapacity"] if self.part and "weightCapacity" in self.part else 0
    powerCost      = self.part["powerCost"]      if self.part and "powerCost" in self.part else 0
    powerCapacity  = self.part["powerCapacity"]  if self.part and "powerCapacity" in self.part else 0
    heatCost       = self.part["heatCost"]       if self.part and "heatCost" in self.part else 0
    heatCapacity   = self.part["heatCapacity"]   if self.part and "heatCapacity" in self.part else 0

    self.add_widget(ResourceBar("Weight",weightCost, weightCapacity, bgcolor = (1,1,1,1)))
    self.add_widget(ResourceBar("Power",powerCost,powerCapacity,     bgcolor = (0,.8,1,1)))
    self.add_widget(ResourceBar("Heat",heatCost, heatCapacity,       bgcolor = (1,.7,0,1)))

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
    normalResists = GridLayout(size_hint_x=.75,rows=2,cols=6)
    for dType in self.normalResistAttribs:
      #normalResists.add_widget(SmartRow([DamageTypeIcon([dType[:-6]]),SaneLabel(text=str(self.part[dType]/10. if self.part and dType in self.part  else 0))]))
      normalResists.add_widget(Image(source="icons/"+dType[:-6]+".png"))
      normalResists.add_widget(Label(text=str(self.part[dType]/10. if self.part and dType in self.part  else 0)))
    protection = GridLayout(size_hint_x=.25,rows=1,cols=2)

    protection.add_widget(Image(source="icons/genesis.png"))
    protection.add_widget(Label(text=str( self.part["protection"]/10. if self.part and "protection" in self.part  else 0)))
    self.add_widget(normalResists)
    self.add_widget(protection)

  def setPart(self, part):
    self.part = part
    self.updateDisplay()

class SplitIcon(Widget):

  def __init__(self, icon1, icon2, **kwargs):
    super(SplitIcon, self).__init__(**kwargs)
    self.texture1 = icon1.texture.get_region(0,0,32, 64)
    self.texture2 = icon2.texture.get_region(32,0,32, 64)
    with self.canvas:
      Callback(self.drawMe)

  def drawMe(self,*args):
    minDim = min(self.width,self.height)
    x = self.x + (self.width-minDim)/2
    y = self.y + (self.height-minDim)/2
    self.canvas.add(Rectangle(texture=self.texture1,pos=(x,y),size=(minDim/2,minDim)))
    self.canvas.add(Rectangle(texture=self.texture2,pos=(x+minDim/2,y),size=(minDim/2,minDim)))

class DamageTypeIcon(GridLayout):
  def __init__(self, damageTypes, **kwargs):
    super(DamageTypeIcon, self).__init__(**kwargs)
    self.size_hint_x = None
    self.rows = 1
    self.cols = 1
    icons = [ Image(size_hint_y = 1, source="icons/"+dType.lower()+".png") for dType in damageTypes ]
    if len(icons) == 1:
      self.add_widget(icons[0])
    else:
      splitIcon = SplitIcon(icons[0],icons[1])
      self.add_widget(splitIcon)
    self.bind(height=self._callback)

  def _callback(self,*args):
    self.width = self.children[0].width = self.children[0].height = self.height

if True: #Part Picker classes
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

    def _start_decrease_alpha(self, *l):
      pass


    def __init__(self,field, parts,**kwargs):
      super(PartSelectScrollView,self).__init__(**kwargs)
      self.bar_width = 5
      self.do_scroll_x = False
      # self.scroll_type = ['bars','content']
      # with self.canvas:
      #   bar_alpha = 1

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
      self.partsList = PartSelectScrollView(partField, buyablePartsByTypeAndRace[partType][race])
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
      self._tab_layout = StripLayout(rows=13)
      self.cols = 1
      self._tab_strip = TabbedPanelStrip(
                         tabbed_panel=self, rows=13,
                         size_hint=(None, None),
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

  def refreshDropdown(self):
    self.dropdown.clear_widgets()
    for ship in self.ships:
      btn = Button(text= ship.name, color = raceToColorMap[ship.race], size_hint_y=None, height=20)
      btn.ship = ship
      btn.bind(on_release=lambda btn: self.dropdown.select(btn.ship))
      self.dropdown.add_widget(btn)

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
    self.refreshDropdown()
    self.mainbutton = Button(text='Select a ship', size_hint=(None, 1))
    self.mainbutton.bind(on_release=self.dropdown.open)

    self.dropdown.bind(on_select=lambda instance, ship: self.changeShip(ship))
    self.add_widget(self.mainbutton)
    self.dropdown.select(currentShip)
    newShipButton = Button(text = "New Ship",size_hint_y=1)
    newShipButton.bind(on_release = self.doNewShipPopup)
    nameChangeButton = Button(text = "Rename",size_hint_y=1)
    nameChangeButton.bind(on_release = self.doRenamePopup)

    self.deleteShipButton = Button(text = "Delete", disabled = (len(self.ships) <= 1))
    self.deleteShipButton.bind(on_release = self.doDeletePopup)
    self.add_widget(newShipButton)
    self.add_widget(nameChangeButton)
    self.add_widget(self.deleteShipButton)

  def doDeletePopup(self,*args):
    popupContent = GridLayout(rows = 2, cols = 1)
    popupContent.add_widget(Label(text = "Data will be lost forever! D:"))
    confirmCancel = GridLayout(rows = 1, cols = 2)
    confirm = Button(text = "Delete")
    confirm.bind(on_release=self.doDelete)
    cancel = Button(text = "Cancel")
    cancel.bind(on_release=lambda btn: self.deleteShipPopup.dismiss())
    self.deleteShipPopup = Popup(title="Delete ship "+currentShip.name +"?", content=popupContent, auto_dismiss=False, size_hint=(.2,.2))
    confirmCancel.add_widget(confirm)
    confirmCancel.add_widget(cancel)
    popupContent.add_widget(confirmCancel)
    self.deleteShipPopup.open()

  def doDelete(self, btn):
    global currentShip
    if currentShip:
      self.ships.remove(currentShip)
      currentShip = self.ships[0]
      self.changeShip(currentShip)
      self.deleteShipButton.disabled = (len(self.ships) <= 1)
      self.deleteShipPopup.dismiss()
      self.refreshDropdown()

  def doNewShipPopup(self,*args):
    popupContent = GridLayout(rows = 2, cols = 1)
    newShipTextInput = ShipNameInput(focus=True, text="",multiline=False,height=20)
    newShipTextInput.race = HUMAN
    dropdown = DropDown()
    for race in races:
      btn = Button(text = raceToStringMap[race], color = raceToColorMap[race],size_hint_y = None, height=20)
      btn.race = race
      btn.bind(on_release=lambda btn:dropdown.select(btn))
      dropdown.add_widget(btn)
    mainbutton = Button(text=raceToStringMap[HUMAN], color=raceToColorMap[HUMAN], height = 20)
    mainbutton.race = HUMAN
    mainbutton.bind(on_release=dropdown.open)
    dropdown.bind(on_select=lambda instance, btn: (map(lambda attr: mainbutton.__setattr__(attr,btn.__getattribute__(attr)), ["text","color","race"]) and False) or newShipTextInput.__setattr__("race",btn.race))
    popupContent.add_widget(mainbutton)
    popupContent.add_widget(newShipTextInput)

    self.newShipPopup = Popup(title="New Ship", content=popupContent, auto_dismiss=False, size_hint=(.3,.2))
    self.newShipPopup.open()
    newShipTextInput.bind(on_text_validate=self.doNewShip)

  def doNewShip(self,instance):
    global currentShip
    newName = instance.text
    if not newName:
      instance.parent.title="Error: Name cannot be empty"
      instance.parent.title_color=(1,0,0,1)
      instance.focus = True
    if newName in [ship.name for ship in self.ships]:
      instance.parent.title="Error: Name in use"
      instance.parent.title_color=(1,0,0,1)
      instance.focus = True
    else:
      currentShip = Gunship(instance.text,instance.race)
      self.ships.append(currentShip)
      self.changeShip(currentShip)
      self.deleteShipButton.disabled = (len(self.ships) <= 1)
      self.newShipPopup.dismiss()
      self.refreshDropdown()

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
      self.refreshDropdown()



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

    self.gModeBtn = Button(text = getAO(), size_hint_y = 1, size_hint_x = .5, disabled = True)
    self.gModeBtn.bind(on_release=self.alphaOmegaSwap)

    self._keyboard = Window.request_keyboard(self._keyboard_closed, self, 'text')
    self._keyboard.bind(on_key_down=self._on_keyboard_down)

    self.partPickers = {}

    self.partDisplay = StatDisplayGrid(size_hint_x = .65, cols = 2, rows = 1) 
    self.partDisplay.add_widget(DescriptionBox(size_hint_x = .7))

    rightColumn = SmartGrid(cols = 1, rows = 4, spacing=[0,5])
    rightColumn.add_widget(ResistsGrid(row_default_height = 40, height=40, row_force_default = True, size_hint = (None,None)))
    rightColumn.add_widget(IconResourceDisplay(size_hint = (None,None), row_default_height = 20, height=20, row_force_default = True))
    rightColumn.add_widget(StatsDisplay( row_default_height = 20, row_force_default = True, spacing = 2, padding = 2))
    rightColumn.add_widget(Widget(width=220, size_hint = (None,None)))
    self.partDisplay.add_widget(rightColumn)

    self.shipDisplay = ShipDisplay()
    # self.shipDisplay.add_widget(BarResourceDisplay(row_default_height = 20, row_force_default = True, size_hint_x = .5))
    # self.shipDisplay.add_widget(ResistsGrid(row_default_height = 40, row_force_default = True))
    # self.shipDisplay.add_widget(PartNameList(row_default_height = 20, row_force_default = True))
    # self.shipDisplay.add_widget(StatsDisplay(row_default_height = 20, row_force_default = True, spacing = 2, padding = 5))
    # self.shipDisplay.add_widget(Widget(size_hint_y = 2))

    self.topHalf = GridLayout(pos_hint = {'top':1, 'x':1}, size_hint = (1,.45), rows = 1, cols = 2)
    self.bottomHalf = GridLayout(pos_hint = {'top':.47, 'x':1}, size_hint = (1,.52), rows = 1, cols = 1)
    self.bottomBar = GridLayout(pos_hint = {'top':.03, 'x':1}, size_hint = (1,.03), rows = 1, cols = 2)

    self.bottomHalf.add_widget(self.shipDisplay)

    self.add_widget(self.topHalf)
    self.add_widget(self.bottomHalf)
    self.add_widget(self.bottomBar)

    self.shipPicker = ShipSelector(self.onShipChange)
    self.bottomBar.add_widget(self.shipPicker)
    self.bottomBar.add_widget(self.gModeBtn)

  def _keyboard_closed(self):
    self._keyboard.unbind(on_key_down=self._on_keyboard_down)
    self._keyboard = None

  def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
    print "button press!",
    if keycode[1] == 'q' and currentShip.race == GUANTRI:
      print "change"
      self.alphaOmegaSwap(self.gModeBtn)
      return True
    print "no change"
    return False

  def alphaOmegaSwap(self, btn):
    btn.unbind(on_release=self.alphaOmegaSwap)
    swapAO()
    btn.text = getAO()
    currentShip.updateNumericValues()
    onShipUpdate()
    onPartUpdate()
    btn.bind(on_release=self.alphaOmegaSwap) 
  

  def onShipChange(self):
    setAO(ALPHA)
    race = currentShip.race
    self.gModeBtn.txt = ALPHA
    self.gModeBtn.disabled = (race != GUANTRI)
    self.shipDisplay.setPart(currentShip)
    self.topHalf.clear_widgets()

    if race not in self.partPickers:
      self.partPickers[race] = PartPicker(race = race,size_hint_x = .35)

    pickerForRace = self.partPickers[race]
    self.topHalf.add_widget(pickerForRace)
    self.topHalf.add_widget(self.partDisplay)
    for tab in pickerForRace.tab_list:
      tab.updateColor()

    Clock.schedule_once((lambda dt: (pickerForRace.switch_to(pickerForRace.tab_list[-1]) and False) or pickerForRace.tab_list[-1].on_release()),1) 


class ShipBuilderApp(App):
  def build(self):
    self.shipBuilder = ShipBuilder(size = Window.size,padding=[2,2,2,2])
    Clock.schedule_once(lambda dt: Window.set_title("Eiko's Ship Builder v"+APP_VERSION + " (GoD Factory Patch "+version+")"),0)
    return self.shipBuilder
  def on_stop(self):
    self.shipBuilder.shipPicker.saveShips()

testRun=False


# testRun = True

if __name__ == '__main__' and not testRun:
  ShipBuilderApp().run()
else:

  for race in races:
    print race
    cProfile.run('PartPicker(race = '+str(race)+')')

  with open("ships.GODBUILDER",'r') as f:
    lines = f.read().splitlines()
    ships = [ Gunship.deserialize(rawShip) for rawShip in lines[1:] ]
  x = ships[0]
  x.updateNumericValues()
  x.updateSubPartValues()
