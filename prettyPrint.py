import argparse
import json
import math

# https://www.reddit.com/r/smashbros/comments/237zsv/formula_for_hitlag_in_melee/
def hitlag(damage, element, attacker, crouchCancel=False):
    if attacker:
        c = 1.0
        e = 1.0
    else: # character being hit
        c = 2/3 if crouchCancel else 1.0
        e = 1.5 if element == "electric" else 1.0
    return math.floor(c * math.floor(e * math.floor(3.0 + damage/3.0)))

def shieldstun(damage):
    return math.floor((damage + 4.45) / 2.235)

def printHitbox(hitbox):
    s = "dmg: {}".format(hitbox["damage"])
    if hitbox["shield_damage"] > 0:
        s += ", shield dmg: {}".format(hitbox["shield_damage"])

    s += ", angle: {}, BK: {}, KS: {}, WDKB: {}".format(
        hitbox["angle"], hitbox["base_kb"], hitbox["kb_growth"], hitbox["weight_dep_kb"])

    if hitbox["element"] != "normal":
        s += ", element: {}".format(hitbox["element"])

    clang = hitbox["hitbox_interaction"] >= 2
    s += ", {}clang".format("" if clang else "no ")

    rebound = hitbox["hitbox_interaction"] == 3
    s += ", {}rebound".format("" if rebound else "no ")

    if not (hitbox["hit_grounded"] and hitbox["hit_airborne"]):
        if hitbox["hit_grounded"]:
            s += ", only hits grounded"
        elif hitbox["hit_airborne"]:
            s += ", only hits airborne"
        else:
            s += ", hits nothing"
    print(s)

    hitlagAtk = hitlag(hitbox["damage"], hitbox["element"], attacker=True)
    hitlagDef = hitlag(hitbox["damage"], hitbox["element"], attacker=False)
    if hitlagAtk != hitlagDef:
        s = "hit lag (attacker): {}, hit lag (defender): {}".format(hitlagAtk, hitlagDef)
    else:
        s = "hit lag: {}".format(hitlagAtk)
    s += ", shield stun: {}".format(shieldstun(hitbox["damage"]))
    print(s)

def frameRangeString(start, end):
    if start == end:
        return str(start)
    else:
        return "{}-{}".format(start, end)

def printAttackSummary(summary):
    if summary == None:
        quit("Attack does not exist.")

    print("Total Frames:", summary["totalFrames"])
    print("IASA: ", summary["iasa"])
    if "landingLag" in summary:
        print("Auto-Cancel: <{}, >{}".format(summary["autoCancelBefore"], summary["autoCancelAfter"]))
        print("Landing Lag:", summary["landingLag"])
        print("L-cancelled:", summary["lcancelledLandingLag"])

    # throw
    if "throw" in summary:
        throw = summary["throw"]
        print()
        print("Throw:")

        s = "dmg: {}, angle: {}, BK: {}, KS: {}, WDKB: {}".format(throw["damage"],
            throw["angle"], throw["base_kb"], throw["kb_growth"], throw["weight_dep_kb"])

        if throw["element"] != "normal":
            s += ", element: {}".format(throw["element"])

        print(s)

    hitboxGuidToName = lambda x: chr(ord("A") + x)

    print()
    if "hitboxes" in summary: # grouped hitboxes
        hitFrames = summary["hitFrames"]
        sameHitboxesForAllHitframes = \
            all(hitFrame["hitboxes"] == hitFrames[0]["hitboxes"] for hitFrame in hitFrames)
        if sameHitboxesForAllHitframes:
            hitFrameStr = ", ".join(frameRangeString(hitFrame["start"], hitFrame["end"]) for hitFrame in hitFrames)
            print("Hit Frames: " + hitFrameStr)
        else:
            print("Hit Frames:")
            for hitFrame in hitFrames:
                translatedHitboxes = map(hitboxGuidToName, hitFrame["hitboxes"])
                print("{}: {}".format(
                    frameRangeString(hitFrame["start"], hitFrame["end"]),
                    ", ".join(translatedHitboxes)))

        for i, hitbox in enumerate(summary["hitboxes"]):
            print()
            # No need for color names/headlines if only one hitbox group
            if len(summary["hitboxes"]) > 1:
                print("Hitbox {}".format(hitboxGuidToName(i)))
            printHitbox(hitbox)
    else: # --fullhitboxes
        print("Hit Frames:")
        for hitFrame in summary["hitFrames"]:
            print(frameRangeString(hitFrame["start"], hitFrame["end"]) + ":")
            for hitbox in hitFrame["hitboxes"]:
                print("id: {}, bone: {}, size: {:.3f}, x: {:.3f}, y: {:.3f}, z: {:.3f}".format(
                    hitbox["id"], hitbox["bone"], hitbox["size"], hitbox["x"], hitbox["y"], hitbox["z"]))
                printHitbox(hitbox)
                print()

def main():
    parser = argparse.ArgumentParser(description="Print framedata JSON files nicely.")
    parser.add_argument("jsonfile", help="The JSON file with the framedata generated by generateFrameData.py")
    parser.add_argument("subaction", help="The subaction/move to analyze. Must be present in the JSON file.")
    args = parser.parse_args()

    with open(args.jsonfile) as inFile:
        frameData = json.load(inFile)

    if args.subaction not in frameData:
        quit("'{}' does not exist in '{}'".format(args.subaction, args.jsonfile))

    printAttackSummary(frameData[args.subaction])

if __name__ == "__main__":
    main()
