#!/usr/bin/env python3
"""Export current game data (KV files) into reference CSV tables in balance/reference/.

Read-only: does not change game files. Run from anywhere:
    python3 tools/export_reference.py
"""
import csv
import glob
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADDON = os.path.join(ROOT, "game", "dota_addons", "legion_td")
SCRIPTS = os.path.join(ADDON, "scripts")
OUT = os.path.join(ROOT, "balance", "reference")

TOKEN = re.compile(r'"((?:[^"\\]|\\.)*)"|([{}])|(//[^\n]*)|(#base[^\n]*)|(\S+)')


def parse_kv(text):
    """Minimal Valve KeyValues parser -> nested dicts (later keys win)."""
    stack = [{}]
    key = None
    for m in TOKEN.finditer(text):
        s, brace, comment, base, bare = m.groups()
        if comment or base:
            continue
        if brace == "{":
            new = {}
            if key is not None:
                stack[-1][key] = new
            stack.append(new)
            key = None
        elif brace == "}":
            if len(stack) > 1:
                stack.pop()
            key = None
        else:
            val = s if s is not None else bare
            if key is None:
                key = val
            else:
                stack[-1][key] = val
                key = None
    return stack[0]


def read(path):
    raw = open(path, "rb").read()
    for enc in ("utf-8-sig", "utf-16"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            pass
    return raw.decode("latin-1")


def load_dir(sub, top):
    result = {}
    for path in sorted(glob.glob(os.path.join(SCRIPTS, "npc", sub, "**", "*.txt"), recursive=True)):
        kv = parse_kv(read(path))
        block = kv.get(top, {})
        folder = os.path.basename(os.path.dirname(path))
        for name, data in block.items():
            if isinstance(data, dict):
                data["_folder"] = folder
                result[name] = data
    return result


def specials(ability):
    out = {}
    for block in (ability.get("AbilitySpecial", {}), ability.get("AbilityValues", {})):
        for k, v in block.items():
            if isinstance(v, dict):
                for kk, vv in v.items():
                    if kk != "var_type":
                        out[kk] = vv
            else:
                out[k] = v
    return out


def unit_ids():
    text = read(os.path.join(SCRIPTS, "vscripts", "config_unit.lua"))
    return {int(i): n for i, n in re.findall(r'\[(\d+)\]\s*=\s*"([^"]+)"', text)}


def localization():
    kv = parse_kv(read(os.path.join(ADDON, "resource", "addon_english.txt")))
    return kv.get("lang", {}).get("Tokens", {})


def num(v):
    try:
        f = float(v)
        return int(f) if f == int(f) else round(f, 2)
    except (TypeError, ValueError):
        return v if v is not None else ""


STAT_COLS = ["hp", "armor", "magic_resist", "dmg_min", "dmg_max", "attack_rate", "range",
             "attack_type", "defend_type", "move_speed", "model", "model_scale", "abilities"]


def unit_stats(u, skip_abilities=()):
    abilities = [u.get("Ability%d" % i, "") for i in range(1, 17)]
    abilities = [a for a in abilities if a and a not in skip_abilities
                 and not a.startswith(("ability_empty", "special_bonus", "sell"))]
    return {
        "hp": num(u.get("StatusHealth")),
        "armor": num(u.get("ArmorPhysical")),
        "magic_resist": num(u.get("MagicalResistance")),
        "dmg_min": num(u.get("AttackDamageMin")),
        "dmg_max": num(u.get("AttackDamageMax")),
        "attack_rate": num(u.get("AttackRate")),
        "range": num(u.get("AttackRange")),
        "attack_type": u.get("LegionAttackType", ""),
        "defend_type": u.get("LegionDefendType", ""),
        "move_speed": num(u.get("MovementSpeed")),
        "model": u.get("Model", ""),
        "model_scale": num(u.get("ModelScale")),
        "abilities": " ".join(abilities),
    }


def write(name, cols, rows):
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name)
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in cols})
    print("%-22s %4d rows" % (name, len(rows)))


def main():
    units = load_dir("units", "DOTAUnits")
    abilities = load_dir("abilities", "DOTAAbilities")
    heroes = load_dir("heroes", "DOTAHeroes")
    ids = unit_ids()
    loc = localization()

    def display(name):
        return loc.get(name, "")

    # ability -> (unit it creates, gold, food, tango, income)
    creates = {}
    for aname, a in abilities.items():
        sp = specials(a)
        if "unitID" in sp:
            uid = int(float(sp["unitID"]))
            creates[aname] = {
                "unit": ids.get(uid, "?id%d" % uid),
                "gold": num(a.get("AbilityGoldCost", "")),
                "food": num(sp.get("food_cost", "")),
                "tango": num(sp.get("tango_cost", "")),
                "income": num(sp.get("income", "")),
            }

    # --- builders + towers ---------------------------------------------------
    builders, towers = [], []
    tower_info = {}  # unit -> dict(builder, tier, from, gold, food)

    def walk(unit, builder, tier, parent, cost):
        if unit in tower_info:
            return
        tower_info[unit] = {"builder": builder, "upgrade_level": tier, "upgrade_from": parent,
                            "gold": cost["gold"], "food": cost["food"]}
        u = units.get(unit, {})
        for i in range(1, 17):
            a = u.get("Ability%d" % i, "")
            if a in creates and "upgrade" in a:
                walk(creates[a]["unit"], builder, tier + 1, unit, creates[a])

    for hname, h in heroes.items():
        spawns = []
        for i in range(1, 25):
            a = h.get("Ability%d" % i, "")
            if a in creates:
                spawns.append(creates[a]["unit"])
                walk(creates[a]["unit"], hname, 1, "", creates[a])
        builders.append({
            "builder": hname,
            "display_name": display(hname),
            "dota_hero": h.get("override_hero", ""),
            "fraction": h.get("LegionFraction", ""),
            "base_towers": " ".join(spawns),
            "other_abilities": " ".join(
                h.get("Ability%d" % i, "") for i in range(1, 10)
                if h.get("Ability%d" % i, "") and h.get("Ability%d" % i) not in creates),
        })

    upgrade_abilities = {a for a in creates if "upgrade" in a}
    for name, u in units.items():
        if not name.startswith("tower_"):
            continue
        info = tower_info.get(name, {"builder": u["_folder"], "upgrade_level": "", "upgrade_from": "", "gold": "", "food": ""})
        row = {"unit": name, "display_name": display(name), **info}
        row.update(unit_stats(u, upgrade_abilities))
        row["upgrades_to"] = " ".join(
            creates[u["Ability%d" % i]]["unit"] for i in range(1, 17)
            if u.get("Ability%d" % i, "") in upgrade_abilities)
        towers.append(row)
    towers.sort(key=lambda r: (r["builder"], str(r["upgrade_level"]), r["unit"]))
    write("towers.csv", ["builder", "upgrade_level", "unit", "display_name", "gold", "food", "upgrade_from",
                         "upgrades_to"] + STAT_COLS, towers)
    write("builders.csv", ["builder", "display_name", "dota_hero", "fraction", "base_towers",
                           "other_abilities"], builders)

    # --- sends (income units) -------------------------------------------------
    sends = []
    for aname, c in creates.items():
        if not aname.startswith("send_"):
            continue
        u = units.get(c["unit"], {})
        row = {"unit": c["unit"], "display_name": display(c["unit"]), "wood_cost": c["tango"],
               "income": c["income"], "bounty": num(u.get("BountyGoldMin"))}
        row.update(unit_stats(u))
        sends.append(row)
    sends.sort(key=lambda r: (float(r["wood_cost"] or 0), r["unit"]))
    write("sends.csv", ["unit", "display_name", "wood_cost", "income", "bounty"] + STAT_COLS, sends)

    # --- waves (per map) ------------------------------------------------------
    for mpath in sorted(glob.glob(os.path.join(SCRIPTS, "maps", "*.txt"))):
        mname = os.path.splitext(os.path.basename(mpath))[0]
        kv = parse_kv(read(mpath))
        rounds = next(iter(kv.values())).get("Rounds", {})
        rows = []
        for rnum in sorted(rounds, key=lambda x: int(x) if x.isdigit() else 0):
            r = rounds[rnum]
            unit = r.get("Unit", {}) if isinstance(r.get("Unit"), dict) else {}
            uname = unit.get("NPCName", "")
            u = units.get(uname, {})
            row = {"round": rnum, "type": r.get("round_type", ""), "title": display(r.get("round_title", "")) or r.get("round_title", ""),
                   "wave_bounty": num(r.get("bounty")), "unit": uname, "count": num(unit.get("UnitCount")),
                   "unit_bounty": num(u.get("BountyGoldMin"))}
            if u:
                row.update(unit_stats(u))
            rows.append(row)
        write("waves_%s.csv" % mname, ["round", "type", "title", "wave_bounty", "unit", "count",
                                       "unit_bounty"] + STAT_COLS, rows)

    # --- kings -------------------------------------------------------------------
    kings = []
    for name, u in units.items():
        if u["_folder"] == "kings":
            row = {"unit": name}
            row.update(unit_stats(u))
            kings.append(row)
    write("kings.csv", ["unit"] + STAT_COLS, kings)


if __name__ == "__main__":
    main()
