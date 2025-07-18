<drac2>
cargs = &ARGS&[1:&ARGS&.index("*")] if '*' in &ARGS& else &ARGS&[1:]  # make a list of our casting args, splitting on * if supplied
aargs = &ARGS&[&ARGS&.index("*")+1:] if '*' in &ARGS& else []  # make a list of our arcana roll args

ma ='Mizzium Apparatus'
ch = character()

# parse custom name override
cparse = argparse(cargs)

# Custom for dragon form
c = combat()
if c:
    com = c.get_combatant(ch.name)
    if com and com.get_effect("Starry Form: Dragon", True):
        aargs.append("-mc")  # -mc 10 is a minimum roll for the !roll command
        aargs.append("10")  # -mc 10 is a minimum roll for the !roll command

a  = argparse(aargs)
g  = load_json(get_gvar('c7fac1dc-a814-4b1e-81b0-f3ee6abec1cf'))
i  = argparse(&ARGS&).get('i')

# racial & guidance bonuses
racialBonus = "+1d4[Artisan's Intuition]" if "Mark of Making" in ch.race else "+1d4[Tireless Precision]" if "Vedalken" in ch.race and "precision" in aargs else ''
rollstring = ["1d20","2d20kh1","2d20kl1"][a.adv()]
rollstring += ("mi" + a.last("mc") if a.last("mc") else "mi10" if character().csettings.get('talent',0) and ch.skills.arcana.prof >= 1 else "")
rollstring += "+" + str(ch.skills.arcana.value)
rollstring += ("+" + a.join("b","+") if a.last("b") else "")
rollstring += ("+1d4" if "guidance" in aargs else "")
rollstring += racialBonus
aRoll = vroll(rollstring)  # our arcana roll

# -- HOMEBREW SPELLS -- #

exampleDict = '''!svar MAHomebrew {
        "0": ["vicious mockeries"],
        "1": ["which bolt?"],
        "2": [],
        "3": ["wind break"],
        "4": ["aura of stank"],
        "8": ["dom ate monster"]
  }'''

hbDict = {}

if hbSpells := get_svar('MAHomebrew', get_uvar('MAHomebrew', '{}')):
  try:
    hbDict = load_json(hbSpells)
    for x in range(10):
      if (more_spells := hbDict.get(str(x), [])) and typeof(more_spells)=='SafeList':
        g.sp[str(x)].extend(more_spells)

  except:
    return f'''embed -title "Your {ma} begins to smoke and a flag pops out the end reading ERROR!" -desc «There is an issue with your Homebrew spells for this alias!  Check your `!svar MAHomebrew` and your `!uvar MAHomebrew` to insure it is a [properly formatted JSON](<https://jsonlint.com>) with spells in lists according to their level _exactly_ as shown below, but with your homebrew spell names:```json\n!svar MAHomebrew {exampleDict}```\n\nYou can use an empty list or remove spell levels for which you have no homebrew spells.\n\nIf you can't figure it out, head to the [Avrae Development Server](<https://support.avrae.io/>) for help.»   '''


# -- PARTIAL SPELL NAME MATCHING -- #

# make a list of all possible spells 
fullSpellList = []
for x in range(10):
  fullSpellList += g.sp[str(x)]

# try for an exact match
fullSpellName = [x for x in fullSpellList if "&1&".lower()==x.lower()]

# try for partial match 
if not fullSpellName:
  fullSpellName = [x for x in fullSpellList if "&1&".lower() in x.lower()]

# if we matched multiple spells
if len(fullSpellName)>1:
  return f"""embed -title "Your entry `&1&` matches more than one possible spell name."  -desc 《Possible matches: `{'`, `'.join(fullSpellName)}`\n\n**Command ran:**\n\n`{ctx.prefix+ctx.alias} &*&`》  """

# if we still didn't match anything
elif not fullSpellName:
  return f"""embed -title "Your {ma} has a breakdown!" -desc 《Your entry `&1&` doesn't match any known spell.  Check your spelling and try again.\n\n**Command ran:**\n\n`{ctx.prefix+ctx.alias} &*&`》  """ if &ARGS& else f'''embed -title "{name} reads the manual on their {ma}!" -desc "You can use `!mizapp` just like `!cast` with arguments and targets as per usual.  If you get a bonus or advantage to your arcana check, add those after `*` like in this example:\n`!mizapp 'spell name' [spell args] [-t targets] * [arcana args]`\n\nExample casting 'fire bolt' with disadvantage to hit GO1, but with advantage and bonus 1d4 to the arcana roll:\n `!mizapp 'fire bolt' dis -t GO1 * adv -b 1d4`" '''

# we ended up with only one match 《 》
else:
  fullSpellName = fullSpellName[0]

# Custom cast args
name_override = cparse.last("n")  # use -n "Custom Name"
displayName = name_override if name_override else fullSpellName
vc_arg       = cparse.last("vc")   # -vc "Verbal Component"
vc_field    = f"-f \"Verbal Component|{vc_arg}\"" if vc_arg else ''

# -- Casting the spell -- #

# grab our spell level
slevel = ([lvl for lvl in g.sp if fullSpellName in g.sp[lvl]]+[None])[0]

# handle upcasting, verify user has a slot at the correct level
if slevel in ['0','1','2','3','4','5','6','7','8','9']:
  upcast = min(cparse.last("l", 0, int), 9)  # grab our upcast or default to 0, cap the max at 9 to avoid level 10+ spell nonsense
  slevel = str(max(int(slevel),int(upcast)))  # adjust our level we're casting at
  x      = ch.spellbook.get_slots(int(slevel))>0 if not i else True  # do we have unused slots at this level or are we ignoring slots
  mslot  = ch.spellbook.get_max_slots(int(slevel))>0  # did we ever have slots at this level?
  dc     = 10+(int(slevel)*2)  # calculate our dc based off spell level
  rslevel= slevel if slevel in ['0','1','2','3','4','5'] else '5'  # random spell has a max level 5 on fail
  v      = dc <= aRoll.total
  fail_spell = '' if slevel == '0' else g.fspell[rslevel][randint(len(g.fspell[rslevel]))]

  if slevel=='0':  # cantrip casting
    if v:
      return f'''cast "{fullSpellName}" i {' '.join(f'"{carg}"' if " " in carg else carg for carg in cargs)} -title "{name} casts __{displayName }__ with their {ma}!" -phrase "*Arcana roll:** {aRoll}\n**DC: {dc}** *Success!" {vc_field} -f "{g.miz}" '''
    else:
      return f'''embed -title "Your ineptitude has caused your {ma} to malfunction!" -desc "_**Arcana roll:** {aRoll}_\n_**DC: {dc}** Failure!_\n\n If you try to cast a cantrip you don't know, the DC for the Intelligence (Arcana) check is 10, and on a failed check, there is no effect." -f "{g.miz}" '''
  elif slevel!='0':  # non-cantrip casting
    if x:
      ch.spellbook.use_slot(int(slevel)) if not i else ''
      if v:  # we beat the dc and are casting the spell we wanted
        return f'''cast "{fullSpellName}" i {' '.join(f'"{carg}"' if " " in carg else carg for carg in cargs)} -title "{name} casts __{displayName}__ with their {ma}!" -phrase "*Arcana roll:** {aRoll}\n**DC: {dc}** *Success!" {vc_field} -f "{g.miz}" -f "Spell Slots {'(-1)' if not i else ''}|{character().spellbook.slots_str(int(slevel))}" '''
      else:  # we failed the dc and are casting a random spell for this level
        return f'''cast "{fail_spell}" i {' '.join(f'"{carg}"' if " " in carg else carg for carg in cargs)} -title "{name} tries to cast __{displayName}__ with their {ma} but casts __{fail_spell}__ instead!" -phrase "*Arcana roll:** {aRoll}\n**DC:** {dc} *Failure!*\n\n*On a successful check, you cast the spell as normal, using your spell save DC and spellcasting ability modifier. On a failed check, you cast a different spell from the one you intended. If the slot is 6th level or higher, roll on the table for 5th-level spells." -f "{g.miz}" -f "Spell Slots {'(-1)' if not i else ''}|{character().spellbook.slots_str(int(slevel))}" '''
    elif mslot and not x:  # we're out of slots at this level
      return f'''embed -title "{name} does not have any slots left at level {slevel}!" -desc "You need a level {slevel} spell slot in order to use your {ma} like this!\n\nCast again at a different level or have a nap." -f "Spell Slots|{character().spellbook.slots_str(int(slevel))}" '''
    elif not mslot:  # we never had a slot this high
      return f'''embed -title "{name} has clearly never cast a spell this high a level in their life!" -desc "You'll need to level up a bit more if you want to cast a level {slevel} spell with your {ma}." '''
else:  # display the help if things went wrong or nothing was input
  return f'''embed -title "{name} reads the manual on their {ma}!" -desc "You can use `!mizapp` just like `!cast` with arguments and targets as per usual.  If you get a bonus or advantage to your arcana check, add those after `*` like in this example:\n`!mizapp 'spell name' [spell args] [-t targets] * [arcana args]`\n\nExample casting 'fire bolt' with disadvantage to hit GO1, but with advantage and bonus 1d4 to the arcana roll:\n `!mizapp 'fire bolt' dis -t GO1 * adv -b 1d4`" '''
</drac2> -thumb 'https://cdn.discordapp.com/attachments/709738212209197189/776857816107450368/tenor.gif' -footer '{{ctx.prefix+ctx.alias}} "<spell name>" [casting args] * [arcana args]'
