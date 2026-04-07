# -*- coding: utf-8 -*-
"""
SnowRunner OP Mod - MODIO MODS
Aplica as mesmas modificacoes OP do build_winrar_v6 em todos os mods baixados do mods.io.
Copia os paks modificados para a pasta de mods manuais para nao perder com auto-update.
"""
import zipfile
import os
import re
import sys
import shutil
import subprocess
from collections import defaultdict

MODIO_DIR = r"C:\Users\ferna\Documents\My Games\SnowRunner\base\Mods\.modio\mods"
WINRAR    = r"C:\Program Files\WinRAR\WinRAR.exe"
TEMP_DIR  = r"c:\Users\ferna\Downloads\_op_modio_temp"
BACKUP_DIR = r"C:\Users\ferna\Downloads\_modio_backup"

# ============================================================
# MESMAS CONSTANTES DO build_winrar_v6.py
# ============================================================
LEVELS = [
    ("op1", "FURIOSO"),
    ("op2", "DEVASTADOR"),
    ("op3", "APOCALIPSE"),
    ("op4", "TITA"),
    ("op5", "DEUS"),
]

ENGINE_STATS = [
    {"id": "eco",       "Torque": "80000",   "Fuel": "0.3", "Damage": "50000", "Resp": "0.15",
     "Tag": "ECO",      "Name": "Motor ECO 80K",        "Desc": "Motor ultra economico. 80K Nm. Consumo quase zero. Viagem longa."},
    {"id": "city",      "Torque": "150000",  "Fuel": "1.0", "Damage": "30000", "Resp": "0.2",
     "Tag": "CITY",     "Name": "Motor CITY 150K",      "Desc": "Motor urbano. 150K Nm. Leve, economico, bom pra estrada."},
    {"id": "street",    "Torque": "200000",  "Fuel": "2.0", "Damage": "30000", "Resp": "0.2",
     "Tag": "STREET",   "Name": "Motor STREET 200K",    "Desc": "Motor de rua. 200K Nm. Resposta suave, bom pra asfalto."},
    {"id": "rally",     "Torque": "250000",  "Fuel": "3.5", "Damage": "25000", "Resp": "0.35",
     "Tag": "RALLY",    "Name": "Motor RALLY 250K",     "Desc": "Motor rally. 250K Nm. Resposta agressiva, feito pra velocidade."},
    {"id": "offroad",   "Torque": "350000",  "Fuel": "3.0", "Damage": "40000", "Resp": "0.2",
     "Tag": "OFFROAD",  "Name": "Motor OFFROAD 350K",   "Desc": "Motor offroad. 350K Nm. Equilibrio entre torque e consumo."},
    {"id": "turbo",     "Torque": "400000",  "Fuel": "5.0", "Damage": "35000", "Resp": "0.4",
     "Tag": "TURBO",    "Name": "Motor TURBO 400K",     "Desc": "Motor turbo. 400K Nm. Resposta rapida, gasta mais combustivel."},
    {"id": "mud",       "Torque": "500000",  "Fuel": "4.0", "Damage": "50000", "Resp": "0.15",
     "Tag": "MUD",      "Name": "Motor LAMA 500K",      "Desc": "Motor pra lama. 500K Nm. Torque bruto, resposta lenta e controlada."},
    {"id": "tow",       "Torque": "550000",  "Fuel": "3.0", "Damage": "65000", "Resp": "0.18",
     "Tag": "TOW",      "Name": "Motor REBOQUE 550K",   "Desc": "Motor de reboque. 550K Nm. Feito pra puxar cargas pesadas. Resistente."},
    {"id": "diesel",    "Torque": "600000",  "Fuel": "3.5", "Damage": "60000", "Resp": "0.2",
     "Tag": "DIESEL",   "Name": "Motor DIESEL 600K",    "Desc": "Motor diesel pesado. 600K Nm. Torque alto, muito resistente."},
    {"id": "v6t",       "Torque": "650000",  "Fuel": "4.5", "Damage": "45000", "Resp": "0.3",
     "Tag": "V6T",      "Name": "Motor V6 TURBO 650K",  "Desc": "Motor V6 turbo. 650K Nm. Rapido e potente, gasta bastante."},
    {"id": "v8",        "Torque": "700000",  "Fuel": "6.0", "Damage": "45000", "Resp": "0.3",
     "Tag": "V8",       "Name": "Motor V8 700K",        "Desc": "Motor V8 bruto. 700K Nm. Potencia absurda, bebe combustivel."},
    {"id": "superv8",   "Torque": "800000",  "Fuel": "5.0", "Damage": "55000", "Resp": "0.25",
     "Tag": "SUPERV8",  "Name": "Motor SUPER V8 800K",  "Desc": "Motor V8 reforcado. 800K Nm. Mais resistente que o V8, menos consumo."},
    {"id": "beast",     "Torque": "850000",  "Fuel": "4.0", "Damage": "80000", "Resp": "0.2",
     "Tag": "BEAST",    "Name": "Motor BEAST 850K",     "Desc": "Motor monstro. 850K Nm. Quase indestrutivel, puxa qualquer coisa."},
    {"id": "war",       "Torque": "900000",  "Fuel": "3.0", "Damage": "85000", "Resp": "0.18",
     "Tag": "WAR",      "Name": "Motor WAR 900K",       "Desc": "Motor militar. 900K Nm. Blindado, consumo controlado, torque brutal."},
    {"id": "titan",     "Torque": "1000000", "Fuel": "2.0", "Damage": "90000", "Resp": "0.2",
     "Tag": "TITAN",    "Name": "Motor TITAN 1M",       "Desc": "Motor titan. 1M Nm. Torque maximo com consumo baixo."},
    {"id": "nuclear",   "Torque": "1200000", "Fuel": "0.5", "Damage": "95000", "Resp": "0.2",
     "Tag": "NUCLEAR",  "Name": "Motor NUCLEAR 1.2M",   "Desc": "Motor nuclear. 1.2M Nm. Quase nao gasta combustivel. Potencia insana."},
    {"id": "predator",  "Torque": "1500000", "Fuel": "3.0", "Damage": "85000", "Resp": "0.35",
     "Tag": "PREDATOR", "Name": "Motor PREDATOR 1.5M",  "Desc": "Motor predador. 1.5M Nm. Resposta agressiva, torque extremo."},
    {"id": "god",       "Torque": "2000000", "Fuel": "0.1", "Damage": "99999", "Resp": "0.2",
     "Tag": "GOD",      "Name": "Motor DEUS 2M",        "Desc": "Motor divino. 2M Nm. Torque infinito, nao quebra, nao gasta."},
    {"id": "omega",     "Torque": "3000000", "Fuel": "0.1", "Damage": "99999", "Resp": "0.15",
     "Tag": "OMEGA",    "Name": "Motor OMEGA 3M",       "Desc": "Motor omega. 3M Nm. Alem do divino. Resposta suave, poder absoluto."},
    {"id": "infinity",  "Torque": "5000000", "Fuel": "0.01","Damage": "99999", "Resp": "0.1",
     "Tag": "INFINITY", "Name": "Motor INFINITO 5M",    "Desc": "Motor infinito. 5M Nm. O mais forte que existe. Consumo zero. Eterno."},
]

GB_STATS = [
    {"MaxVel": 50,  "Damage": "99999"},
]

SUSP_STATS = [
    {"H": "0.06", "S": "0.06", "D": "0.28", "Damage": "5000",  "Tag": "STOCK_PLUS",  "Name": "Suspensao STOCK+"},
    {"H": "0.09", "S": "0.06", "D": "0.32", "Damage": "8000",  "Tag": "BAIXA_1",     "Name": "Suspensao BAIXA 1"},
    {"H": "0.12", "S": "0.07", "D": "0.36", "Damage": "12000", "Tag": "BAIXA_2",     "Name": "Suspensao BAIXA 2"},
    {"H": "0.15", "S": "0.07", "D": "0.40", "Damage": "16000", "Tag": "MEDIA_1",     "Name": "Suspensao MEDIA 1"},
    {"H": "0.19", "S": "0.08", "D": "0.44", "Damage": "22000", "Tag": "MEDIA_2",     "Name": "Suspensao MEDIA 2"},
    {"H": "0.23", "S": "0.09", "D": "0.48", "Damage": "30000", "Tag": "ALTA_1",      "Name": "Suspensao ALTA 1"},
    {"H": "0.28", "S": "0.10", "D": "0.52", "Damage": "38000", "Tag": "ALTA_2",      "Name": "Suspensao ALTA 2"},
    {"H": "0.33", "S": "0.10", "D": "0.56", "Damage": "48000", "Tag": "LIFTED_1",    "Name": "Suspensao LIFTED 1"},
    {"H": "0.39", "S": "0.11", "D": "0.60", "Damage": "58000", "Tag": "LIFTED_2",    "Name": "Suspensao LIFTED 2"},
    {"H": "0.46", "S": "0.12", "D": "0.64", "Damage": "68000", "Tag": "MONSTER_1",   "Name": "Suspensao MONSTER 1"},
    {"H": "0.54", "S": "0.13", "D": "0.68", "Damage": "80000", "Tag": "MONSTER_2",   "Name": "Suspensao MONSTER 2"},
    {"H": "0.65", "S": "0.13", "D": "0.72", "Damage": "92000", "Tag": "EXTREMA",     "Name": "Suspensao EXTREMA"},
    {"H": "0.80", "S": "0.14", "D": "0.78", "Damage": "99999", "Tag": "DEUS",        "Name": "Suspensao DEUS"},
]

WINCH_STATS = [
    {"Len": "100", "Str": "20.0"},
]


# ============================================================
# MOD FUNCTIONS (copiadas do build_winrar_v6.py)
# ============================================================
def mod_engine(content, filename):
    content = re.sub(r'MaxDeltaAngVel="[^"]+"', 'MaxDeltaAngVel="0.001"', content)
    if "</EngineVariants>" not in content:
        return content
    tmpl = re.search(r'_template="(\w+)"', content)
    template = tmpl.group(1) if tmpl else "Engine"
    entries = []
    for stats in ENGINE_STATS:
        entries.append(
            '\t<Engine\r\n'
            '\t\t_template="' + template + '"\r\n'
            '\t\tCriticalDamageThreshold="0.99"\r\n'
            '\t\tDamageCapacity="' + stats['Damage'] + '"\r\n'
            '\t\tDamagedConsumptionModifier="1.0"\r\n'
            '\t\tEngineResponsiveness="' + stats['Resp'] + '"\r\n'
            '\t\tFuelConsumption="' + stats['Fuel'] + '"\r\n'
            '\t\tName="op_engine_' + stats['id'] + '"\r\n'
            '\t\tTorque="' + stats['Torque'] + '"\r\n'
            '\t\tDamagedMinTorqueMultiplier="1.0"\r\n'
            '\t\tDamagedMaxTorqueMultiplier="1.0"\r\n'
            '\t>\r\n'
            '\t\t<GameData\r\n'
            '\t\t\tPrice="100"\r\n'
            '\t\t\tUnlockByExploration="false"\r\n'
            '\t\t\tUnlockByRank="1"\r\n'
            '\t\t>\r\n'
            '\t\t\t<UiDesc\r\n'
            '\t\t\t\tUiDesc="UI_ENGINE_' + stats['Tag'] + '_DESC"\r\n'
            '\t\t\t\tUiIcon30x30=""\r\n'
            '\t\t\t\tUiIcon40x40=""\r\n'
            '\t\t\t\tUiName="UI_ENGINE_' + stats['Tag'] + '_NAME"\r\n'
            '\t\t\t/>\r\n'
            '\t\t</GameData>\r\n'
            '\t</Engine>')
    insert = "\r\n" + "\r\n".join(entries) + "\r\n"
    return content.replace("</EngineVariants>", insert + "</EngineVariants>")


def mod_gearbox(content, filename):
    if "</GearboxVariants>" not in content:
        return content
    mv = GB_STATS[0]["MaxVel"]
    dmg = GB_STATS[0]["Damage"]
    gears = []
    GEAR_COUNT = 8
    gear_speeds = [round(1.5 * (mv / 1.5) ** (g / (GEAR_COUNT - 1)), 2) for g in range(GEAR_COUNT)]
    for i, spd in enumerate(gear_speeds):
        fm = round(1.8 - (1.0 / max(len(gear_speeds) - 1, 1)) * i, 2)
        fm = max(fm, 0.7)
        gears.append('\t\t<Gear AngVel="' + str(spd) + '" FuelModifier="' + str(fm) + '" />')
    rv = 1.5
    hv = round(gear_speeds[-2] + (gear_speeds[-1] - gear_speeds[-2]) * 0.5, 1)
    gears_str = "\r\n".join(gears)
    entry = (
        '\t<Gearbox\r\n'
        '\t\tAWDConsumptionModifier="0.0"\r\n'
        '\t\tCriticalDamageThreshold="0.99"\r\n'
        '\t\tDamageCapacity="' + dmg + '"\r\n'
        '\t\tDamagedConsumptionModifier="1.0"\r\n'
        '\t\tFuelConsumption="1.0"\r\n'
        '\t\tIdleFuelModifier="0.1"\r\n'
        '\t\tName="op_gearbox_deus"\r\n'
        '\t\tMinBreakFreq="0.0"\r\n'
        '\t\tMaxBreakFreq="0.0"\r\n'
        '\t>\r\n'
        '\t\t<ReverseGear AngVel="' + str(rv) + '" FuelModifier="1.1" />\r\n'
        '\t\t<HighGear AngVel="' + str(hv) + '" FuelModifier="1.0" />\r\n'
        + gears_str + '\r\n'
        '\t\t<GameData\r\n'
        '\t\t\tPrice="100"\r\n'
        '\t\t\tUnlockByExploration="false"\r\n'
        '\t\t\tUnlockByRank="1"\r\n'
        '\t\t>\r\n'
        '\t\t\t<GearboxParams\r\n'
        '\t\t\t\tIsHighGearExists="true"\r\n'
        '\t\t\t\tIsLowerGearExists="true"\r\n'
        '\t\t\t\tIsLowerPlusGearExists="false"\r\n'
        '\t\t\t\tIsLowerMinusGearExists="false"\r\n'
        '\t\t\t/>\r\n'
        '\t\t\t<UiDesc\r\n'
        '\t\t\t\tUiDesc="UI_GEARBOX_DEUS_DESC"\r\n'
        '\t\t\t\tUiIcon30x30=""\r\n'
        '\t\t\t\tUiIcon40x40=""\r\n'
        '\t\t\t\tUiName="UI_GEARBOX_DEUS_NAME"\r\n'
        '\t\t\t/>\r\n'
        '\t\t</GameData>\r\n'
        '\t</Gearbox>')
    insert = "\r\n" + entry + "\r\n"
    return content.replace("</GearboxVariants>", insert + "</GearboxVariants>")


def mod_winch(content, filename):
    if "</WinchVariants>" not in content:
        return content
    stats = WINCH_STATS[0]
    entry = (
        '\t<Winch\r\n'
        '\t\tName="op_winch_deus"\r\n'
        '\t\tLength="' + stats['Len'] + '"\r\n'
        '\t\tStrengthMult="' + stats['Str'] + '"\r\n'
        '\t\tIsEngineIgnitionRequired="false"\r\n'
        '\t>\r\n'
        '\t\t<GameData\r\n'
        '\t\t\tPrice="100"\r\n'
        '\t\t\tUnlockByExploration="false"\r\n'
        '\t\t\tUnlockByRank="1"\r\n'
        '\t\t>\r\n'
        '\t\t\t<WinchParams\r\n'
        '\t\t\t/>\r\n'
        '\t\t\t<UiDesc\r\n'
        '\t\t\t\tUiDesc="UI_WINCH_DEUS_DESC"\r\n'
        '\t\t\t\tUiIcon30x30=""\r\n'
        '\t\t\t\tUiIcon40x40=""\r\n'
        '\t\t\t\tUiName="UI_WINCH_DEUS_NAME"\r\n'
        '\t\t\t/>\r\n'
        '\t\t</GameData>\r\n'
        '\t</Winch>')
    insert = "\r\n" + entry + "\r\n"
    return content.replace("</WinchVariants>", insert + "</WinchVariants>")


def mod_suspension(content, filename):
    if "</SuspensionSetVariants>" not in content:
        return content
    base = os.path.splitext(filename)[0]
    entries = []
    for i, stats in enumerate(SUSP_STATS):
        h = stats["H"]
        op_id = "op" + str(i + 1)
        tag = stats["Tag"]
        entries.append(
            '\t<SuspensionSet\r\n'
            '\t\t_template="Active"\r\n'
            '\t\tCriticalDamageThreshold="0.99"\r\n'
            '\t\tDamageCapacity="' + stats['Damage'] + '"\r\n'
            '\t\tBrokenWheelDamageMultiplier="0.01"\r\n'
            '\t\tDeviationDelta=".002"\r\n'
            '\t\tName="' + base + '_' + op_id + '"\r\n'
            '\t>\r\n'
            '\t\t<Suspension Height="' + h + '" Strength="' + stats['S'] + '" Damping="' + stats['D'] + '" WheelType="front" BrokenSuspensionMax="0.0" SuspensionMin="-' + h + '" SuspensionMax="0.3" DeviationMax="0.15" />\r\n'
            '\t\t<Suspension Height="' + h + '" Strength="' + stats['S'] + '" Damping="' + stats['D'] + '" WheelType="rear" BrokenSuspensionMax="0.0" SuspensionMin="-' + h + '" SuspensionMax="0.3" DeviationMax="0.15" />\r\n'
            '\t\t<GameData\r\n'
            '\t\t\tPrice="100"\r\n'
            '\t\t\tUnlockByExploration="false"\r\n'
            '\t\t\tUnlockByRank="1"\r\n'
            '\t\t>\r\n'
            '\t\t\t<UiDesc\r\n'
            '\t\t\t\tUiDesc="UI_SUSP_' + tag + '_DESC"\r\n'
            '\t\t\t\tUiIcon30x30=""\r\n'
            '\t\t\t\tUiIcon40x40=""\r\n'
            '\t\t\t\tUiName="UI_SUSP_' + tag + '_NAME"\r\n'
            '\t\t\t/>\r\n'
            '\t\t</GameData>\r\n'
            '\t</SuspensionSet>')
    insert = "\r\n" + "\r\n".join(entries) + "\r\n"
    return content.replace("</SuspensionSetVariants>", insert + "</SuspensionSetVariants>")


def mod_wheels(content, filename):
    if "</TruckTires>" not in content:
        return content

    file_id = filename.replace("wheels_", "").replace("wheel_", "").replace(".xml", "")
    parts = file_id.split("_")
    if len(parts) >= 2:
        file_tag = "".join(p[0] for p in parts if p) + parts[-1][1:] if len(parts[-1]) > 1 else "".join(p[0] for p in parts if p)
    else:
        file_tag = file_id[:8]

    # Aumentar Width 2.5x
    def widen(match):
        attr = match.group(1)
        val = float(match.group(2))
        new_val = round(val * 2.5, 3)
        return attr + '="' + str(new_val) + '"'
    content = re.sub(r'(Width(?:Rear)?)\s*=\s*"([0-9.]+)"', widen, content)

    # Pneus indestrutíveis
    content = re.sub(r'(<TruckWheels[^>]*?)DamageCapacity="[^"]+"', r'\1DamageCapacity="999999"', content)

    tire_pattern = re.compile(
        r'<TruckTire\s+([^>]*?)>\s*'
        r'(.*?)'
        r'</TruckTire>',
        re.DOTALL
    )
    existing_tires = tire_pattern.findall(content)
    if not existing_tires:
        return content

    seen_meshes = {}
    for attrs_str, inner in existing_tires:
        mesh_m = re.search(r'Mesh="([^"]+)"', attrs_str)
        tmpl_m = re.search(r'_template="([^"]+)"', attrs_str)
        name_m = re.search(r'Name="([^"]+)"', attrs_str)
        wf_tmpl_m = re.search(r'<WheelFriction[^>]*_template="([^"]+)"', inner)
        if mesh_m and name_m:
            mesh = mesh_m.group(1)
            if mesh not in seen_meshes:
                seen_meshes[mesh] = {
                    "template": tmpl_m.group(1) if tmpl_m else "Offroad",
                    "name": name_m.group(1),
                    "wf_template": wf_tmpl_m.group(1) if wf_tmpl_m else None,
                }

    entries = []
    for mesh, info in seen_meshes.items():
        safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', info["name"])
        op_name = "op_" + file_tag + "_" + safe_name + "_god"
        wf_tmpl_attr = ' _template="' + info["wf_template"] + '"' if info["wf_template"] else ''
        entries.append(
            '\t\t<TruckTire _template="' + info["template"] + '" Mesh="' + mesh + '" Name="' + op_name + '">\r\n'
            '\t\t\t<WheelFriction' + wf_tmpl_attr + ' BodyFriction="15.0" BodyFrictionAsphalt="15.0" SubstanceFriction="15.0" IsIgnoreIce="true" />\r\n'
            '\t\t\t<GameData\r\n'
            '\t\t\t\tPrice="100"\r\n'
            '\t\t\t\tUnlockByExploration="false"\r\n'
            '\t\t\t\tUnlockByRank="1"\r\n'
            '\t\t\t>\r\n'
            '\t\t\t\t<UiDesc UiDesc="UI_TIRE_DEUS_DESC" UiName="UI_TIRE_DEUS_NAME" />\r\n'
            '\t\t\t</GameData>\r\n'
            '\t\t</TruckTire>')

    insert = "\r\n" + "\r\n".join(entries) + "\r\n\t"
    return content.replace("</TruckTires>", insert + "</TruckTires>")


def mod_truck(content, filename):
    changed = False

    # DiffLockType -> Always
    m = re.search(r'DiffLockType="(\w+)"', content)
    if m and m.group(1) != "Always":
        content = content.replace('DiffLockType="' + m.group(1) + '"', 'DiffLockType="Always"')
        changed = True

    # Snorkel Origin Y -> 10.0
    def raise_snorkel(match):
        nonlocal changed
        full = match.group(0)
        origin_m = re.search(r'Origin="\(([^;]+);\s*([^;]+);\s*([^)]+)\)"', full)
        if origin_m:
            x = origin_m.group(1).strip()
            z = origin_m.group(3).strip()
            new_origin = 'Origin="(' + x + '; 10.0; ' + z + ')"'
            old_origin = 'Origin="(' + origin_m.group(1) + '; ' + origin_m.group(2).strip() + '; ' + origin_m.group(3) + ')"'
            if old_origin in full:
                new_full = full.replace(old_origin, new_origin)
                changed = True
                return new_full
        return full
    content = re.sub(r'<Snorkel[^/>]+/>', raise_snorkel, content)

    # Escalas maiores para rodas
    existing_cw = re.findall(r'<CompatibleWheels[^/]*/>', content)
    if existing_cw:
        scale_mults = [1.3, 1.45, 1.6]
        existing_combos = set()
        for cw in existing_cw:
            sm = re.search(r'Scale="([^"]+)"', cw)
            tm = re.search(r'Type="([^"]+)"', cw)
            if sm and tm:
                existing_combos.add((sm.group(1), tm.group(1)))

        new_entries = []
        seen_combos = set()
        for cw in existing_cw:
            scale_m = re.search(r'Scale="([^"]+)"', cw)
            type_m = re.search(r'Type="([^"]+)"', cw)
            if not scale_m or not type_m:
                continue
            orig_scale = float(scale_m.group(1))
            wtype = type_m.group(1)
            offsetz_m = re.search(r'OffsetZ="([^"]+)"', cw)
            rearoffz_m = re.search(r'RearOffsetZ="([^"]+)"', cw)

            for mult in scale_mults:
                new_scale = round(orig_scale * mult, 3)
                new_scale_str = str(new_scale)
                combo = (new_scale_str, wtype)
                if combo in existing_combos or combo in seen_combos:
                    continue
                seen_combos.add(combo)
                attrs = 'Scale="' + new_scale_str + '" Type="' + wtype + '"'
                if offsetz_m:
                    attrs = 'OffsetZ="' + offsetz_m.group(1) + '" ' + attrs
                if rearoffz_m:
                    attrs = 'RearOffsetZ="' + rearoffz_m.group(1) + '" ' + attrs
                new_entries.append('\t\t<CompatibleWheels ' + attrs + ' />')

        if new_entries:
            last_cw = existing_cw[-1]
            insert_text = last_cw + "\r\n" + "\r\n".join(new_entries)
            content = content.replace(last_cw, insert_text, 1)
            changed = True

    return content, changed


def get_op_strings():
    strs = []
    for stats in ENGINE_STATS:
        tag = stats["Tag"]
        strs.append('UI_ENGINE_' + tag + '_NAME\t\t\t\t"' + stats["Name"] + '"')
        strs.append('UI_ENGINE_' + tag + '_DESC\t\t\t\t"' + stats["Desc"] + '"')
    for stats in SUSP_STATS:
        tag = stats["Tag"]
        strs.append('UI_SUSP_' + tag + '_NAME\t\t\t\t"' + stats["Name"] + '"')
        strs.append('UI_SUSP_' + tag + '_DESC\t\t\t\t"Suspensao OP"')
    for prefix, items in [
        ("GEARBOX", [
            ("DEUS",       "Cambio DEUS"),
        ]),
        ("WINCH", [
            ("DEUS",       "Guincho DEUS"),
        ]),
        ("TIRE", [
            ("DEUS",       "Pneu DEUS"),
        ]),
    ]:
        for tag, name in items:
            strs.append("UI_" + prefix + "_" + tag + '_NAME\t\t\t\t"' + name + '"')
            strs.append("UI_" + prefix + "_" + tag + '_DESC\t\t\t\t"OP"')
    return "\r\n".join(strs) + "\r\n"


# ============================================================
# MAIN: Processar cada mod pak usando WinRAR (preserva estrutura zip)
# ============================================================
def process_mod_pak(pak_path, mod_name):
    """Processa um pak de mod extraindo, modificando e re-injetando com WinRAR.
    Retorna total de arquivos modificados ou None."""

    try:
        with zipfile.ZipFile(pak_path, "r") as zf:
            entries = zf.infolist()
    except Exception as e:
        print(f"  ERRO ao abrir: {e}")
        return None

    # Verificar se tem conteudo moddavel
    has_moddable = False
    for entry in entries:
        p = entry.filename
        if any(cat in p for cat in ["classes/engines/", "classes/gearboxes/", "classes/suspensions/",
                                      "classes/wheels/", "classes/winches/", "classes/trucks/"]):
            if p.endswith(".xml"):
                has_moddable = True
                break

    if not has_moddable:
        return None

    # Verificar se ja foi moddado
    with zipfile.ZipFile(pak_path, "r") as zf:
        for entry in entries:
            if entry.filename.endswith(".xml") and "classes/engines/" in entry.filename:
                try:
                    txt = zf.read(entry.filename).decode("utf-8", errors="replace")
                    if "op_engine_eco" in txt:
                        print(f"  JA MODDADO - pulando")
                        return None
                except:
                    pass
                break

    # Criar pasta temp para este mod
    mod_temp = os.path.join(TEMP_DIR, mod_name.replace(".pak", ""))
    if os.path.exists(mod_temp):
        shutil.rmtree(mod_temp)
    os.makedirs(mod_temp)

    counts = {"engines": 0, "gearboxes": 0, "suspensions": 0, "wheels": 0, "winches": 0, "trucks": 0, "strings": 0}

    with zipfile.ZipFile(pak_path, "r") as zf:
        for entry in entries:
            path = entry.filename
            fname = os.path.basename(path)
            modified = False
            new_data = None

            # Engines
            if "classes/engines/" in path and path.endswith(".xml"):
                raw = zf.read(path)
                text = raw.decode("utf-8", errors="replace")
                new_text = mod_engine(text, fname)
                if new_text != text:
                    new_data = new_text.encode("utf-8")
                    counts["engines"] += 1
                    modified = True

            # Gearboxes
            elif "classes/gearboxes/" in path and path.endswith(".xml"):
                raw = zf.read(path)
                text = raw.decode("utf-8", errors="replace")
                new_text = mod_gearbox(text, fname)
                if new_text != text:
                    new_data = new_text.encode("utf-8")
                    counts["gearboxes"] += 1
                    modified = True

            # Winches
            elif "classes/winches/" in path and path.endswith(".xml"):
                raw = zf.read(path)
                text = raw.decode("utf-8", errors="replace")
                new_text = mod_winch(text, fname)
                if new_text != text:
                    new_data = new_text.encode("utf-8")
                    counts["winches"] += 1
                    modified = True

            # Suspensions
            elif "classes/suspensions/" in path and path.endswith(".xml"):
                raw = zf.read(path)
                text = raw.decode("utf-8", errors="replace")
                new_text = mod_suspension(text, fname)
                if new_text != text:
                    new_data = new_text.encode("utf-8")
                    counts["suspensions"] += 1
                    modified = True

            # Wheels
            elif "classes/wheels/" in path and path.endswith(".xml"):
                raw = zf.read(path)
                text = raw.decode("utf-8", errors="replace")
                new_text = mod_wheels(text, fname)
                if new_text != text:
                    new_data = new_text.encode("utf-8")
                    counts["wheels"] += 1
                    modified = True

            # Trucks
            elif "classes/trucks/" in path and path.endswith(".xml"):
                raw = zf.read(path)
                text = raw.decode("utf-8", errors="replace")
                new_text, changed = mod_truck(text, fname)
                if changed:
                    new_data = new_text.encode("utf-8")
                    counts["trucks"] += 1
                    modified = True

            # Strings
            elif path.endswith(".str"):
                raw = zf.read(path)
                if raw[:2] == b'\xff\xfe':
                    text = raw[2:].decode("utf-16-le", errors="replace")
                else:
                    text = raw.decode("utf-16-le", errors="replace")
                op_text = get_op_strings()
                if not text.endswith("\r\n"):
                    text = text.rstrip("\r\n") + "\r\n"
                text = text + op_text
                new_data = b'\xff\xfe' + text.encode("utf-16-le")
                counts["strings"] += 1
                modified = True

            if modified and new_data:
                out_path = os.path.join(mod_temp, path.replace("/", os.sep))
                os.makedirs(os.path.dirname(out_path), exist_ok=True)
                with open(out_path, "wb") as f:
                    f.write(new_data)

    total = sum(counts.values())
    if total == 0:
        shutil.rmtree(mod_temp)
        return None

    # Injetar com WinRAR (preserva estrutura original do zip)
    cmd = [WINRAR, "a", "-afzip", "-o+", "-r", pak_path, "*"]
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=mod_temp)

    # Limpar temp
    shutil.rmtree(mod_temp)

    if result.returncode != 0:
        print(f"  ERRO WinRAR: {result.stderr[:200]}")
        return None

    details = ", ".join(f"{k}={v}" for k, v in counts.items() if v > 0)
    print(f"  OK: {total} arquivos ({details})")
    return total


def main():
    print("=" * 60)
    print("  SNOWRUNNER OP MOD - MODIO MODS")
    print("  Aplicando mods OP em todos os mods baixados")
    print("=" * 60)

    # Backup
    if not os.path.exists(BACKUP_DIR):
        os.makedirs(BACKUP_DIR)
        print(f"\n[BACKUP] Criando backups em {BACKUP_DIR}")
    else:
        print(f"\n[BACKUP] Pasta de backup ja existe: {BACKUP_DIR}")

    # Listar todos os paks de mods
    mod_paks = []
    for mod_id in sorted(os.listdir(MODIO_DIR)):
        mod_path = os.path.join(MODIO_DIR, mod_id)
        if not os.path.isdir(mod_path):
            continue
        for fname in os.listdir(mod_path):
            if fname == "pc.pak" or not fname.endswith(".pak"):
                continue
            pak_path = os.path.join(mod_path, fname)
            mod_paks.append((mod_id, fname, pak_path))

    print(f"\n[SCAN] Encontrados {len(mod_paks)} paks de mods")

    # Processar
    success = 0
    skipped = 0
    errors = 0

    for i, (mod_id, pak_name, pak_path) in enumerate(mod_paks, 1):
        print(f"\n[{i}/{len(mod_paks)}] {pak_name} (mod {mod_id})")

        # Backup se nao existe ainda
        bak_dir = os.path.join(BACKUP_DIR, mod_id)
        bak_path = os.path.join(bak_dir, pak_name)
        if not os.path.exists(bak_path):
            os.makedirs(bak_dir, exist_ok=True)
            shutil.copy2(pak_path, bak_path)
            print(f"  Backup: OK")

        result = process_mod_pak(pak_path, pak_name)
        if result is None:
            skipped += 1
        elif result > 0:
            success += 1
        else:
            errors += 1

    print("\n" + "=" * 60)
    print(f"  RESULTADO:")
    print(f"    Modificados:  {success}")
    print(f"    Pulados:      {skipped}")
    print(f"    Erros:        {errors}")
    print("=" * 60)


if __name__ == "__main__":
    main()
