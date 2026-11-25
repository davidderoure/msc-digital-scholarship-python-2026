"""Build notebooks/05_bate_collection.ipynb (MSc Digital Scholarship 2026).

Usage:  python tools/build_05_bate.py [output.ipynb]
Needs:  pip install nbformat
"""
import sys
import nbformat as nbf

cells = []
md = lambda s: cells.append(nbf.v4.new_markdown_cell(s.strip("\n")))
code = lambda s: cells.append(nbf.v4.new_code_cell(s.strip("\n")))

md(r"""
# Reading a catalogue: the Bate Collection of musical instruments
*MSc Digital Scholarship 2026*

The [Bate Collection](https://www.bate.ox.ac.uk) in Oxford holds about 2,000 historical musical instruments,
mostly European woodwind, brass and percussion, and it lets students *play* many of them.
Its catalogue was exported from the same kind of database as the Pitt Rivers arrowheads, so the tools from the last notebook work again.

But this catalogue brings new problems:
1. A category written in 49 different ways.
2. **Dates that are words**: *c. 1910*, *second quarter 19th century*, *mediaeval*.
3. Lengths that don't mean what you'd expect.
4. Free-text answers to a question (*Is it playable?*) that we'd like to count.

As before, cells with a **form** are for exploring: change a value and run the cell again with **Shift + Enter**.
""")

md(r"""
## 1. Setup and the data

The original spreadsheet is on Canvas. For this version we removed the storage locations, the names of donors and previous owners,
and some long notes. Everything else is as exported.

The setup cell also brings back three tools from the arrowheads notebook: `values` and `first_value` for cells that hold several values
separated by `_x001D_`, and `length_mm`, now able to read a second way of writing dimensions.
""")

code(r"""
import re
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

DATA_URL = "https://raw.githubusercontent.com/davidderoure/msc-digital-scholarship-python-2026/main/data/bate_collection.csv"

bate = pd.read_csv(DATA_URL, dtype=str, keep_default_na=False)
print(bate.shape[0], "records,", bate.shape[1], "columns")


def values(cell):
    # all the values in a cell, without the separators and empty pieces
    return [v.strip() for v in cell.split("_x001D_") if v.strip()]

def first_value(cell):
    found = values(cell)
    return found[0] if found else ""

def length_mm(dimension):
    # "Max L = 564 mm ..." (as in the arrowheads), or "392mm x 50mm" (we assume the first number is the length)
    match = re.search(r"^\s*(?:Max L\s*[=:]\s*)?([\d.]+)\s*mm", dimension)
    return float(match.group(1)) if match else None

bate.head()
""")

code(r"""
try:
    from google.colab import data_table                 # an interactive table, only in Colab
    display(data_table.DataTable(bate, num_rows_per_page=10))
except ImportError:
    display(bate.head(20))
""")

md(r"""
> **Discussion.** Compare the columns with the arrowheads. This catalogue records `Playable`, `Mark` (makers' stamps) and `Acoustic Measure`;
> the arrowheads had `Hazardous Substances` and `Cultural Group`. What does each museum care about, and what does that tell you about what the catalogue is *for*?
""")

md(r"""
## 2. Is every record unique?

Each instrument should have its own `Number`. Let's check:
""")

code(r"""
print("Duplicated numbers:", bate["Number"].duplicated().sum())

numbers = bate["Number"].str.strip()                    # remove spaces and line breaks around the number
print("Duplicated after removing spaces:", numbers[numbers != ""].duplicated().sum())
print("Numbers with hidden spaces or line breaks:", [n for n in bate["Number"] if n != n.strip()])
""")

md(r"""
> **Critical check.** `"497"` and `"497\n"` look identical in a spreadsheet, but to Python they are different, so a duplicate was **hidden** until we stripped the spaces.
> What should a researcher do with duplicates: delete one, keep both, or ask the Museum?
""")

md(r"""
## 3. What kind of instrument? A category written 49 ways
""")

code(r"""
bate["Class"].value_counts()
""")

md(r"""
`Flutes`, `flutes` and `Flute` are the same thing. A first attempt at tidying: lower case, remove spaces at the ends, and remove a plural `s`.
""")

code(r"""
naive = bate["Class"].str.strip().str.lower().str.rstrip("s")
naive.value_counts()
""")

md(r"""
That helps, but look closely: **`bra`** (from *brass*) and **`accessorie`**. Removing a final *s* is a rule, and rules have exceptions.
Some differences aren't about spelling at all: *woodwind*, *aerophone* and *chordophone* come from different ways of **classifying** instruments
(the last two are from the Hornbostel–Sachs system, which classifies by how the sound is made).
So a person has to decide. Here is one set of decisions; read it and argue with it:
""")

code(r"""
CLASS_MAP = {
    "flute": "Flutes", "recorder": "Flutes",
    "reed instrument": "Reed instruments", "reedpipe": "Reed instruments", "double reed": "Reed instruments",
    "string instrument": "String instruments", "stringed instrument": "String instruments",
    "violin": "String instruments", "chordophone": "String instruments",
    "trumpet": "Brass", "horn": "Brass", "brass": "Brass", "brass instrument": "Brass",
    "percussion instrument": "Percussion", "percussion": "Percussion", "drum": "Percussion", "drm": "Percussion",
    "keyboard instrument": "Keyboard", "keyboard": "Keyboard",
    "chanot collection": "Chanot Collection",
    "electrophone": "Other instruments", "mechanical instrument": "Other instruments",
    "aerophone": "Other instruments", "woodwind": "Other instruments", "toy": "Other instruments",
    "tool": "Not instruments", "equipment": "Not instruments", "accessory": "Not instruments", "bow": "Not instruments",
    "picture": "Not instruments", "image": "Not instruments", "sculpture": "Not instruments", "document": "Not instruments",
    "miscellaneous non-instrument": "Not instruments",
}

def tidy_class(cell):
    c = cell.strip().lower()
    if c.endswith("ies"):
        c = c[:-3] + "y"                          # accessories -> accessory
    elif c.endswith("s") and not c.endswith("ss"):
        c = c[:-1]                                # flutes -> flute, but brass stays brass
    return CLASS_MAP.get(c, "Not recorded" if c == "" else c)

bate["family"] = [tidy_class(c) for c in bate["Class"]]
bate["family"].value_counts()
""")

md(r"""
> **Critical check.**
> - The **Chanot Collection** (576 records) is a violin-maker's workshop: templates, tools and parts, as well as instruments. Is it a "family" of instruments?
>   Look at `bate[bate["family"] == "Chanot Collection"]["Name"].value_counts()` to see what's in it.
> - Is a **bow** an instrument? Is a **toy** trumpet? Every count below depends on these decisions.
> - Where did *woodwind* go, and was that right? Which of these decisions would you want to write down in a paper's methods section?
""")

md(r"""
The `Name` column holds the instrument's name, sometimes with other names after `_x001D_`, and sometimes ending with `;`:
""")

code(r"""
INCLUDE_NON_INSTRUMENTS = False  # @param {type:"boolean"}

bate["name"] = [first_value(c).rstrip(";").strip() for c in bate["Name"]]
shown = bate if INCLUDE_NON_INSTRUMENTS else bate[~bate["family"].isin(["Chanot Collection", "Not instruments"])]

shown["name"].value_counts().head(20).sort_values().plot.barh(figsize=(8, 6), color="steelblue")
plt.xlabel("number in the collection")
plt.title("The 20 most common names" + ("" if INCLUDE_NON_INSTRUMENTS else " (instruments only)"))
plt.show()
""")

md(r"""
> **Critical check.** Even "instruments only" includes **Tool**, **Bow** and **Bassoon Part**: their `Class` puts them in an instrument family, but their `Name` says otherwise.
> When two columns disagree, which do you trust? Try `bate[bate["name"] == "Tool"][["Class", "Description"]].head(10)`.
""")

md(r"""
## 4. Length and pitch

Lengths are written two ways in this catalogue: `Max L = 564 mm` and `392mm x 50mm`. Our `length_mm` handles both, but it **assumes** the first number is the length.
""")

code(r"""
bate["length"] = [length_mm(d) for d in bate["Dimensions"]]
print(bate["length"].notna().sum(), "of", len(bate), "records have a length")

missed = bate[(bate["Dimensions"] != "") & bate["length"].isna()]
missed["Dimensions"].value_counts().head(10)
""")

md(r"""
For a wind instrument, a longer tube plays lower notes. Choose some instruments to compare (separate them with commas, and spell them as in the chart above):
""")

code(r"""
INSTRUMENTS = "Piccolo, Transverse Flute, Recorder, Oboe, Clarinet, Bassoon, Trumpet, Horn, Trombone"  # @param {type:"string"}

chosen = [name.strip() for name in INSTRUMENTS.split(",")]
data = bate[bate["name"].isin(chosen) & bate["length"].notna()]
order = list(data.groupby("name")["length"].median().sort_values().index)

fig = px.box(data, x="name", y="length", points="all", category_orders={"name": order},
             hover_data=["Number", "Description", "Maker", "Date"], title="Length by instrument (mm)")
fig.update_layout(xaxis_title="", yaxis_title="length (mm)")
fig.show()
data.groupby("name")["length"].agg(["count", "median", "min", "max"]).loc[order]
""")

md(r"""
> **Critical check.**
> - A piccolo is shorter than a flute and plays an octave higher: so far, so good. But a **horn** looks shorter than a clarinet,
>   though it plays much lower. Why? Hover over the dots and read the descriptions. (Its tube is coiled; a bassoon's is folded in half.)
> - So "length" here is the length of the **object**, not of the tube that makes the sound. Remember the arrowheads: was the length the head, or the whole arrow?
> - Hover over the shortest and longest recorders. Is one "recorder" a different thing from another (sopranino, bass, a toy)?
> - The catalogue also has an `Acoustic Measure` column: `bate["Acoustic Measure"].value_counts()`. How full is it, and could you use it?
""")

md(r"""
## 5. Dates that are words

This is the central problem of the notebook. Here are the most common ways the `Date` column is written:
""")

code(r"""
bate["Date"].replace("", "(empty)").value_counts().head(25)
""")

md(r"""
To count or plot instruments by date we need numbers. But *mid-19th century* isn't a year: it's a **range** of years.
So our function turns each date into a range, `(earliest, latest)`. Read the comments: every line is a decision.
""")

code(r"""
CENTURY_PARTS = {                     # which part of a century, in years from its start
    "first quarter": (0, 24), "second quarter": (25, 49), "third quarter": (50, 74), "last quarter": (75, 99),
    "first third": (0, 33), "first half": (0, 49), "second half": (50, 99),
    "early": (0, 33), "mid": (34, 66), "late": (67, 99),
}
CIRCA = 10                            # "c. 1850" means 1840 to 1860
OPEN_ENDED = 50                       # "pre 1900" means 1850 to 1900; "post 1900" means 1900 to 1950

def date_range(text):
    t = text.lower().replace("?", "").replace("prob.", "").replace("'", "")
    if "mediaeval" in t:
        return (1300, 1500) if "late" in t else (500, 1500)
    t = re.sub(r"\b(\d\d)(\d\d)\s*([-/])\s*(\d\d)\b", r"\1\2\3\1\4", t)     # "1840-60" -> "1840-1860"
    earliest, latest = [], []

    # centuries: "19th century", "late 18th", "second quarter 19th century", "21st century"
    for part, number in re.findall(r"(first quarter|second quarter|third quarter|last quarter|first third|"
                                   r"first half|second half|early|mid|late)?[\s-]*(\d{1,2})(?:st|nd|rd|th)\b", t):
        start = (int(number) - 1) * 100
        a, b = CENTURY_PARTS.get(part, (0, 99))
        earliest.append(start + a)
        latest.append(start + b)

    # years: "1755", "c. 1850", "1970s"
    for circa, year, decade in re.findall(r"(c\.?\s*)?(\d{4})(s?)", t):
        year = int(year)
        if decade:
            earliest.append(year); latest.append(year + 9)
        elif circa:
            earliest.append(year - CIRCA); latest.append(year + CIRCA)
        else:
            earliest.append(year); latest.append(year)

    if not earliest:
        return None
    if re.search(r"\b(pre|before)\b", t):
        return (min(earliest) - OPEN_ENDED, min(earliest))
    if re.search(r"\bpost\b", t):
        return (max(latest), max(latest) + OPEN_ENDED)
    return (min(earliest), max(latest))

for example in ["1755-1794", "c. 1910", "1970s", "mid-19th century", "second quarter 19th century",
                "late 18th-early 19th century", "pre 1900", "mediaeval", "u/k"]:
    print(f"{example:30} -> {date_range(example)}")
""")

md(r"""
Try a date of your own. Does the function do what *you* would do?
""")

code(r"""
PHRASE = "first half 20th century"  # @param {type:"string"}
print(PHRASE, "->", date_range(PHRASE))
""")

md(r"""
Now apply it to every record, and look at what it **couldn't** read:
""")

code(r"""
bate["date range"] = [date_range(d) for d in bate["Date"]]
dated = bate[bate["date range"].notna()].copy()
dated["earliest"] = [r[0] for r in dated["date range"]]
dated["latest"] = [r[1] for r in dated["date range"]]
dated["width"] = dated["latest"] - dated["earliest"]

print(len(dated), "of", (bate["Date"] != "").sum(), "dates could be read;", (bate["Date"] == "").sum(), "records have no date at all")
print("\nCould not read:", list(bate.loc[(bate["Date"] != "") & bate["date range"].isna(), "Date"].unique()))
print("\nHow precise are the dates? Width of the range, in years:")
print(dated["width"].describe().round())
""")

md(r"""
### Two ways to draw dates that are ranges

Suppose we want a chart of *how many instruments come from each decade*. An instrument dated *19th century* could belong to any decade from 1800 to 1890.
- **midpoint**: put each instrument in the decade in the middle of its range (*19th century* → 1850s). Simple, but it invents precision.
- **spread**: share each instrument out over all the decades in its range (*19th century* → a tenth in each decade). Honest, but blurrier.

Choose a method and a family, and compare:
""")

code(r"""
METHOD = "spread"  # @param ["midpoint", "spread"]
FAMILY = "all"  # @param ["all", "Flutes", "Reed instruments", "Brass", "String instruments", "Percussion", "Keyboard", "Chanot Collection"]
FROM_YEAR = 1650  # @param {type:"slider", min:1500, max:1900, step:50}

data = dated if FAMILY == "all" else dated[dated["family"] == FAMILY]
by_decade = {decade: 0.0 for decade in range(FROM_YEAR, 2030, 10)}
for start, end in zip(data["earliest"], data["latest"]):
    if METHOD == "midpoint":
        decade = (start + end) // 2 // 10 * 10
        if decade in by_decade:
            by_decade[decade] += 1
    else:
        years = range(start, end + 1)
        for year in years:
            if year // 10 * 10 in by_decade:
                by_decade[year // 10 * 10] += 1 / len(years)

plt.figure(figsize=(11, 3.5))
plt.bar(list(by_decade), list(by_decade.values()), width=9, color="steelblue")
plt.xlabel("decade")
plt.ylabel("instruments")
plt.title(f"{FAMILY} by decade ({METHOD}), {len(data)} dated records")
plt.show()
""")

md(r"""
> **Critical check.**
> - Switch between **midpoint** and **spread**. Where do the peaks come from with *midpoint*? (Look for decades ending in 50: *19th century* lands on the 1850s.)
> - Which chart would you put in an essay? Which would you trust? Could you show the uncertainty some other way?
> - Change `CIRCA` or `OPEN_ENDED` in the function above, run both cells again, and see how much the picture moves.
> - What about the ~1,200 instruments with no date at all? Are they likely to be a random sample of the collection?
""")

md(r"""
## 6. Where from, and who made them?
""")

code(r"""
MERGE_UNCERTAIN = True  # @param {type:"boolean"}

def place(cell):
    country = cell.split(",")[0].strip()                 # "UK, England, London" -> "UK"
    return country.rstrip("?").strip() if MERGE_UNCERTAIN else country

bate["country"] = [place(c) for c in bate["Provenance"]]
bate["country"].replace("", "(empty)").value_counts().head(15).sort_values().plot.barh(figsize=(7, 5), color="steelblue")
plt.xlabel("instruments")
plt.title("Where the instruments come from (top 15)")
plt.show()
""")

md(r"""
> **Critical check.** Look at the full list with `bate["country"].value_counts()`. *UK*, *England* and *London* all appear, as do *U.S.A.* and *USA*.
> How would you fix that? And what does it mean that more than half the collection is from the UK?
""")

code(r"""
def tidy_maker(cell):
    maker = cell.strip().rstrip("?").strip()
    if maker.lower() in ("", "anon", "anon.", "anonymous", "unknown"):
        return "Anonymous or unknown"
    return maker

bate["maker"] = [tidy_maker(m) for m in bate["Maker"]]
print("Anonymous or unknown:", (bate["maker"] == "Anonymous or unknown").sum(), "of", len(bate))
bate.loc[bate["maker"] != "Anonymous or unknown", "maker"].value_counts().head(20)
""")

md(r"""
> **Critical check.**
> - *Rudall Carte & Co.*, *Rudall, Carte & Co.* and *Rudall Carte* are one firm. Find other cases like this, and write a small dictionary (like `CLASS_MAP`) to merge them.
> - *Chanot* and *Joseph Chanot*: the same person, or a family business? Merging needs historical knowledge, not just code.
> - Nearly half the instruments are anonymous. Whose work is that, and what kinds of instrument are they?
""")

md(r"""
## 7. Is it playable? Counting free text

In 2012 someone examined each instrument and wrote down whether it could be played. Here's what they wrote:
""")

code(r"""
bate["Playable"].str.strip().str.lower().value_counts().head(25)
""")

code(r"""
def playable(text):
    t = text.strip().lower()
    if t in ("", "n/a"):
        return "not recorded"
    if t.startswith("yes") or t.startswith("probably yes"):
        return "yes"
    if t.startswith("no") or t.startswith("probably not"):
        return "no"
    return "maybe"

bate["playable"] = [playable(p) for p in bate["Playable"]]

families = bate[~bate["family"].isin(["Not instruments", "Not recorded"])]
table = pd.crosstab(families["family"], families["playable"], normalize="index").mul(100).round()
table = table[["yes", "maybe", "no", "not recorded"]].sort_values("yes")
fig = px.bar(table, orientation="h", title="Is it playable? (% of each family)",
             color_discrete_map={"yes": "seagreen", "maybe": "gold", "no": "indianred", "not recorded": "lightgrey"})
fig.update_layout(xaxis_title="%", yaxis_title="", legend_title="")
fig.show()
table
""")

md(r"""
> **Critical check.**
> - *Yes (but it's only a head)*, *possibly (needs reed)*, *would be if clean*: what did we lose by squashing these into yes / maybe / no?
> - Is "playable" a fact about the instrument, or a judgement by one person on one day?
> - Why might reed instruments so often be "maybe"? (Read some of the answers.)
""")

md(r"""
## 8. Two catalogues compared

Both catalogues come from Oxford museums, exported in the same way, with the same habits: `_x001D_` separators, `Max L = … mm`, `?` for uncertainty.
""")

code(r"""
print(f"Bate: {bate['length'].notna().mean():.0%} of records have a length; {(bate['Date'] != '').mean():.0%} have a date.")
print("Arrowheads (from the last notebook): 54% have a length; 27% have a 'Date made'.")
""")

md(r"""
> **Discussion.**
> - Why might a collection of musical instruments be measured and dated more completely than a collection of arrowheads?
> - The arrowheads were grouped by **type** across the world; the Bate instruments are mostly from **one tradition**. How does that change the questions you can ask?
> - In both catalogues, much of what we found was about the **people**: collectors, cataloguers, the person who decided what was playable. Is a catalogue a record of objects, or of a museum's history?
""")

md(r"""
## 9. Your turn: ask an AI, then check

Choose a question, for example: *Which makers have the most instruments in the collection, and when were they working?*
or *Are older instruments less often playable?*

Ask an AI for code, telling it the DataFrame is called `bate`, and naming the columns we made:
`family`, `name`, `length`, `date range`, `country`, `maker`, `playable` (and `dated`, a table of only the dated records with `earliest`, `latest` and `width`).
""")

code(r"""
# paste the AI's code here

""")

md(r"""
> **Critical check.** How did the AI handle the dates: midpoint, spread, or something else? Did it notice the records with no date?
> Did it use our tidy `family` and `maker` columns, or the messy originals?

## Summary

- The same database habits (`_x001D_`, `Max L = … mm`) appear in both catalogues, so tools can be reused, but every catalogue has its own exceptions.
- Tidying categories needs **rules** (lower case, plurals) and **decisions** (is a bow an instrument?). Write the decisions down.
- A date like *mid-19th century* is a **range**, and how you draw ranges changes the story.
- "Length" means the object, not the sound-making tube: always ask what a number measures.
- Free text can be counted, but counting throws away the qualifications that make it informative.
""")

nb = nbf.v4.new_notebook()
nb["cells"] = cells
nb["metadata"] = {"colab": {"provenance": []}, "kernelspec": {"display_name": "Python 3", "name": "python3"},
                  "language_info": {"name": "python"}}
out = sys.argv[1] if len(sys.argv) > 1 else "notebooks/05_bate_collection.ipynb"
nbf.write(nb, out)
print("Wrote", out)
