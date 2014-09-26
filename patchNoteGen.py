#!/usr/bin/env python

# if True blocks denote logical separations of global level code. I use them so I can collapse them using my editor. 
if True: # Imports
  from string import ascii_uppercase
  from time import sleep
  import os.path
  import re
  import sqlite3
  import sys
  from distutils.version import StrictVersion
  from functools import partial
  from collections import namedtuple

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

  # def partCompareAO(part):
  #   if len(part[OMEGA]) < len(part[ALPHA]):
  #     return True
  #   return reduce((lambda p, q: p and q),[ part[ALPHA][i].rawVals[0:16] == part[OMEGA][i].rawVals[0:16] and part[ALPHA][i].rawVals[17:] == part[OMEGA][i].rawVals[17:] for i in part[ALPHA].keys()],True)

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
  attribs = set([ "id", "defaultRace", "type", "className", "weaponType", "rankRequired", "possibleRaces", "creditCosts", "expRequired", "prereqParts","traits", "isPrereqFor", "mark", "codeName", "alphaOmega", "damageTypes", "grade", "scoreGained", "weightCost", "weightCapacity", "powerCost", "powerCapacity", "heatCost", "heatCapacity", "shield", "shieldRecharge", "energy", "energyRegen", "perforationResist", "decayResist", "distortionResist", "ignitionResist", "overloadResist", "detonationResist", "protection", "handling", "numWingWeapons", "speed", "boost", "purgeCooldown", "abilityCooldown", "lockingSpeed", "targetingArea", "targetingRange", "minimumRange", "maximumRange", "accuracy", "shotCooldown", "projectileCount", "projectileRange", "ammo", "lockingTime", "maxTargets", "damage", "markOwned", "currentExp", "parentName", "displayName", "description", "range","multiTargetMode","projectilesPerTarget","lockRequired", "targets", "rawAmmo", "rawDamage", "mystery", "additionalWonders", "DPS","damagePerLoad","ammoLifespan","fireRate","isBuyable","locking","cooldown"])
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

def getPartsForVersion(version): 
  global traitsById,traitStrings
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
  partsById = {}

  partsDump = open('parts.'+version+'.dump').read()
  for row in partsDump.replace('|','\n').splitlines():
    partRow = PartMark().init(row.split(':'),partStrings)
    if partRow.id not in partsById:
      partsById[partRow.id] = {}
    if partRow.mark not in partsById[partRow.id]:
      partsById[partRow.id][partRow.mark] = partRow
    else:
      partsById[partRow.id][partRow.mark].merge(partRow)

  partsByTypeAndRace = {}

  for (partId,row) in partsById.iteritems():
    part = row[1]
    race = part.defaultRace
    if part.type not in partsByTypeAndRace:
      partsByTypeAndRace[part.type] = {}
    if race not in partsByTypeAndRace[part.type]:
      partsByTypeAndRace[part.type][race] = {}
    partsByTypeAndRace[part.type][race][partId] = row
      

  return partsByTypeAndRace

oldParts = getPartsForVersion("1.0.2b")
newParts = getPartsForVersion("1.0.4")

skipCompareAttribs = set(["additionalWonders","markOwned","currentExp","traits","description","damage","rawAmmo","locking","DPS","damagePerLoad","ammoLifespan"])

# changedMap={}
# def noteChange(partId,attribute):
#   if partId not in changedMap:
#     changedMap[partId] = []
#   changedMap[partId].append(attrib)  

#def traitCompare(t1,t2):


for partType in partTypes:
  for race in races:
    if set(newParts[partType][race].keys()) != set(oldParts[partType][race].keys()):
      print partType,race,""
    for partId in newParts[partType][race].iterkeys():
      changedAttribs=set([])
      for (oldPartMark,newPartMark) in zip(oldParts[partType][race][partId].itervalues(),newParts[partType][race][partId].itervalues()):
        for attrib in PartMark.attribs - skipCompareAttribs:
          if (attrib in oldPartMark or attrib in newPartMark) and oldPartMark[attrib] != newPartMark[attrib]:
            changedAttribs.add(attrib)
        # if "description" in oldPartMark and oldPartMark.description.replace("\n","") != newPartMark.description.replace("\n",""):
        #   changedAttribs.add(attrib)
      if changedAttribs:
        print newParts[partType][race][partId].values()[0].parentName
        print changedAttribs
      for attrib in changedAttribs:
        print attrib
        if not "attrib" in oldPartMark:
          oldPartMark[attrib]=0
        if not "attrib" in newPartMark:
          newPartMark[attrib]=0
        print '->'.join([' / '.join([ str(part[attrib]) for part in parts[partType][race][partId].itervalues()]) for parts in [oldParts,newParts]])
