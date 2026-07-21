// Class -> spec names, and the canonical spec slug the backend files references under.
// Slugs are class-qualified ("<class>-<spec>", lowercased, spaces -> "-") so specs that
// share a name across classes (Restoration, Frost, Holy, Protection) never collide.
//
// Keys match WarcraftLogs `masterData.actors.subType` (the class), which is the value
// the /api/report endpoint returns as `class_name`. Two-word classes are unspaced in
// WCL (e.g. "DeathKnight", "DemonHunter").

export const SPECS_BY_CLASS: Record<string, string[]> = {
  DeathKnight: ["Blood", "Frost", "Unholy"],
  DemonHunter: ["Havoc", "Vengeance"],
  Druid: ["Balance", "Feral", "Guardian", "Restoration"],
  Evoker: ["Devastation", "Preservation", "Augmentation"],
  Hunter: ["Beast Mastery", "Marksmanship", "Survival"],
  Mage: ["Arcane", "Fire", "Frost"],
  Monk: ["Brewmaster", "Mistweaver", "Windwalker"],
  Paladin: ["Holy", "Protection", "Retribution"],
  Priest: ["Discipline", "Holy", "Shadow"],
  Rogue: ["Assassination", "Outlaw", "Subtlety"],
  Shaman: ["Elemental", "Enhancement", "Restoration"],
  Warlock: ["Affliction", "Demonology", "Destruction"],
  Warrior: ["Arms", "Fury", "Protection"],
};

export function specSlug(className: string, specName: string): string {
  return `${className}-${specName}`.toLowerCase().replace(/ /g, "-");
}
