"""Build notebooks/04_arrowheads.ipynb (MSc Digital Scholarship 2026).

Usage:  python tools/build_04_arrowheads.py [output.ipynb]
Needs:  pip install nbformat
"""
import sys
import nbformat as nbf

cells = []
md = lambda s: cells.append(nbf.v4.new_markdown_cell(s.strip("\n")))
code = lambda s: cells.append(nbf.v4.new_code_cell(s.strip("\n")))

md(r"""
# How long is an arrowhead? Data from the Pitt Rivers Museum
*MSc Digital Scholarship 2026*

So far our data has been text. Today it's a **museum catalogue**: about 6,000 records of arrowheads and arrows
in the [Pitt Rivers Museum](https://www.prm.ox.ac.uk), exported from its collections database.

The Museum began in 1884 with the collection of General Pitt-Rivers, who arranged objects **by type**
(all the arrowheads together, from every continent) rather than by place, to show how he believed technologies developed.
A spreadsheet of arrowheads is, in a way, the same idea again. So as well as asking what the data tells us,
we'll ask what it was made *for*, and what it leaves out.

In this notebook we will:
1. Open the data, and see why the original spreadsheet was hard to open.
2. Find out how complete it is.
3. Get a **number**, the length, out of a piece of text.
4. Decide **what counts as an arrowhead**.
5. Tidy up messy categories.
6. Explore the data with interactive charts, and discuss what we see.

Cells with a **form** on the right (dropdowns, sliders, tick boxes) are for exploring: change a value, then run the cell again with **Shift + Enter**.
""")

md(r"""
## 1. Setup and the data

The original spreadsheets are on Canvas. The version we load here has been **slightly prepared**:
- Each record was a line of comma-separated text squashed into column A of the spreadsheet,
  and some long notes had spilled into the cells next to it. We put each record back together (Section 2 shows the problem).
- We removed some columns: internal research notes, database numbers, and names of later owners.

Everything else is as the Museum's database exported it, including the mess.
""")

code(r"""
import re
import csv
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px

DATA_URL = "https://raw.githubusercontent.com/davidderoure/msc-digital-scholarship-python-2026/main/data/pitt_rivers_arrowheads.csv"

arrows = pd.read_csv(DATA_URL, dtype=str, keep_default_na=False)    # read every cell as text; empty cells become ""
print(arrows.shape[0], "records,", arrows.shape[1], "columns")
arrows.head()
""")

md(r"""
`pd.read_csv` makes a **DataFrame**: a table, like a spreadsheet, with named columns.
We asked it to read everything as text (`dtype=str`), so that nothing is changed behind our backs: we'll decide ourselves what's a number.

The next cell shows the whole table so that you can browse it. In Colab you can sort by clicking a column name and filter with the funnel icon.
""")

code(r"""
try:
    from google.colab import data_table                 # an interactive table, only in Colab
    display(data_table.DataTable(arrows, num_rows_per_page=10))
except ImportError:
    display(arrows.head(20))
""")

md(r"""
> **Discussion.** Browse the table for a few minutes. Which columns would you use to answer a research question?
> Which ones are about the *objects*, and which are about the *Museum* (how and when it got them, how it records them)?
""")

md(r"""
## 2. Why was the spreadsheet hard to open?

The database exported each record as one line of **CSV** ("comma-separated values"). Commas separate the columns,
but a description can contain commas too, so any value with a comma inside is wrapped in quotation marks.
Splitting at every comma breaks it; Python's `csv` module follows the quotation marks:
""")

code(r"""
line = '1892.56.77,"Purchased 5 1892","Stone arrow head, tanged. Tang broken.","Max L = 41 mm"'

print(line.split(","))                    # wrong: 5 pieces, the description is cut in two
print(next(csv.reader([line])))           # right: 4 pieces
""")

md(r"""
> **Critical check.** Look at the original spreadsheet on Canvas. Each record is in column A, but the column headings are spread across 34 columns.
> And in about 90 records, long notes that contained line breaks were split into the cells next door.
> - What would happen if you sorted that spreadsheet by column B?
> - When you open data in Excel and save it again, what might change without your noticing? (Think about dates, leading zeros, long numbers, and accents.)
""")

md(r"""
## 3. How complete is the data?

An empty cell can mean "doesn't apply", "not known", or "nobody has entered it yet". Let's see how full each column is:
""")

code(r"""
filled = (arrows != "").mean().mul(100).round().sort_values()      # % of records with something in each column

filled.plot.barh(figsize=(7, 8), color="steelblue")
plt.xlabel("% of records with a value")
plt.title("How complete is each column?")
plt.show()
""")

md(r"""
> **Discussion.** Only about half the records have a `Dimension`, and fewer than one in eight has a `Weight`.
> Which objects do you think got measured, and by whom? Could the measured ones be different from the rest?
""")

md(r"""
## 4. Invisible separators

Look at the `Materials` column:
""")

code(r"""
example = arrows.loc[0, "Materials"]
print(repr(example))
""")

md(r"""
`_x001D_` is how Excel writes an **invisible character**: number 1D in hexadecimal (29 in decimal), called the *group separator*.
(Remember *Characters are numbers* in notebook 1.) The database uses it to keep **several values in one cell**:
an object can be made of more than one material, or belong to more than one class.
Let's split a cell into its values, and keep the first one, which is usually the main material:
""")

code(r"""
def values(cell):
    # all the values in a cell, without the separators and empty pieces
    return [v.strip() for v in cell.split("_x001D_") if v.strip()]

def first_value(cell):
    found = values(cell)
    return found[0] if found else ""

print(values(example))
print(first_value(example))

arrows["material"] = [first_value(cell) for cell in arrows["Materials"]]
arrows["process"] = [first_value(cell) for cell in arrows["Process"]]
arrows["material"].value_counts().head(15)
""")

md(r"""
> **Critical check.** "Stone", "Flint Stone" and "Chert Stone" are listed separately, though flint and chert *are* stone.
> Is "Stone" a material, or a sign that nobody identified the stone? And some materials end in `?`.
> How would you group these for a chart, and what would you lose?
""")

md(r"""
## 5. A number from a piece of text

The `Dimension` column is text, such as `Max L = 41 mm  Max W = 12 mm`. We want the **length** as a number.
A regular expression (notebook 1) can find it: an optional `Max `, then `L`, `=`, a number, and `mm`, at the start of the text.
""")

code(r"""
def length_mm(dimension):
    match = re.search(r"^\s*(?:Max )?L\s*=\s*([\d.]+)\s*mm", dimension)
    return float(match.group(1)) if match else None

print(length_mm("Max L = 41 mm  Max W = 12 mm"))
print(length_mm("L = 35 mm"))
print(length_mm("Max Diam = 9 mm"))

arrows["length"] = [length_mm(d) for d in arrows["Dimension"]]
print(arrows["length"].notna().sum(), "records have a length")
""")

md(r"""
Now **look at what didn't match**. Never trust a pattern until you've seen what it missed:
""")

code(r"""
missed = arrows[(arrows["Dimension"] != "") & arrows["length"].isna()]
missed["Dimension"].value_counts().head(10)
""")

md(r"""
> **Critical check.**
> - Some misses are typing variants, such as `Max l` (small L) or extra spaces. Can you change the pattern to catch them? (Hint: `[Ll]`, and `\s*` means "any number of spaces".)
> - `L [largest point] = 63 mm  L [smallest point] = 21 mm` describes a *group* of objects. Should it have a length? Which one?
> - Some records are for more than one object (see `No. of objects`). What does one length mean then?
> - **Try it with an AI.** Paste a few `Dimension` values into an AI and ask it for a Python function that extracts the length.
>   Run its function here and compare: does it match ours on all 6,000 records? Where do they disagree, and who is right?
""")

md(r"""
## 6. What counts as an arrowhead?

Here is every length. Hover over a dot to see what it is.
""")

code(r"""
measured = arrows[arrows["length"].notna()]
fig = px.strip(measured, x="length", hover_data=["Accession number", "Description"],
               title="Every measured object (mm)", height=300)
fig.show()
print("Shortest:", measured["length"].min(), "mm.  Longest:", measured["length"].max(), "mm.")
""")

md(r"""
The longest objects are not arrowheads at all: they are **whole arrows** and darts, some of them poisoned (look at `Hazardous Substances`).
Their length includes the shaft. So we need a **cut-off**. Choose one, and see how much it matters:
""")

code(r"""
CUT_OFF = 200  # @param {type:"slider", min:50, max:500, step:10}

heads = arrows[arrows["length"] <= CUT_OFF]
print(f"{len(heads)} of {len(measured)} measured objects are {CUT_OFF} mm or shorter.")
print(f"Median length: {heads['length'].median():.0f} mm.  Mean length: {heads['length'].mean():.1f} mm.")

plt.figure(figsize=(9, 3.5))
plt.hist(heads["length"], bins=60, color="steelblue")
plt.xlabel("length (mm)")
plt.ylabel("number of objects")
plt.title(f"Objects up to {CUT_OFF} mm")
plt.show()
""")

md(r"""
> **Critical check.**
> - Move the slider. Does the **median** change as much as the **mean**? Why? (Think back to sentence lengths: the average was pulled about by a few very long sentences.)
> - Is there a natural cut-off, a gap in the histogram? Or is any cut-off a decision you'd have to justify?
> - Should the decision be made on length at all? What else in the data could tell you whether something is an arrowhead?
""")

md(r"""
## 7. Messy categories

The column `Archaeology/Ethnography` says whether an object was excavated (archaeology)
or collected from living people (ethnography). Look at how it has been written:
""")

code(r"""
arrows["Archaeology/Ethnography"].value_counts()
""")

md(r"""
`"A"` and `"A "` (with a space) are different to Python, though not to a person. And what does `"A E"` mean: *both*, or *either*?
Here is one way of tidying it. Read it carefully, because it makes **decisions**:
""")

code(r"""
def a_or_e(code):
    code = code.upper().replace(" ", "")             # "a / e " -> "A/E"
    if code == "A":
        return "Archaeology"
    if code == "E":
        return "Ethnography"
    if "OR" in code or "?" in code:
        return "Uncertain (A or E)"
    if code:
        return "Both? (A and E)"                     # "AE", "A/E", "E A" ... we're guessing these mean both
    return "Not recorded"

arrows["archaeology or ethnography"] = [a_or_e(c) for c in arrows["Archaeology/Ethnography"]]
arrows["archaeology or ethnography"].value_counts()
""")

md(r"""
Places have a similar problem: a question mark records **uncertainty**, as in `N America?`. Should uncertain places be merged with certain ones?
""")

code(r"""
MERGE_UNCERTAIN = True  # @param {type:"boolean"}

def place(cell):
    value = first_value(cell)
    return value.rstrip("?").strip() if MERGE_UNCERTAIN else value

arrows["continent"] = [place(c) for c in arrows["Continent"]]
arrows["country"] = [place(c) for c in arrows["Country"]]
arrows["continent"].value_counts()
""")

md(r"""
> **Critical check.** Someone recorded that question mark on purpose. When we merge it away, the chart looks more certain than the catalogue is.
> When would merging be fair, and when would it mislead? Could a chart show the uncertainty instead?
""")

md(r"""
## 8. When did the arrowheads arrive?

An accession number starts with the year the Museum acquired the object: `1892.56.77` came in 1892.
(The `1884.` numbers are the founding gift from Pitt-Rivers himself.)
""")

code(r"""
arrows["year acquired"] = pd.to_numeric(arrows["Accession number"].str[:4], errors="coerce")
arrows["decade acquired"] = [f"{int(y) // 10 * 10}s" if pd.notna(y) else "" for y in arrows["year acquired"]]

by_decade = arrows["decade acquired"].value_counts().drop("", errors="ignore").sort_index()
by_decade.plot.bar(figsize=(10, 3.5), color="steelblue")
plt.ylabel("objects acquired")
plt.title("Arrowheads and arrows acquired by the Pitt Rivers Museum, by decade")
plt.show()
""")

md(r"""
> **Discussion.** Why might so many arrive in the 1880s, the 1910s–20s, the 1940s and the 1960s, and so few after 1970?
> A single large gift can make a peak: try finding which collections arrived in the 1960s.
> Think about who was collecting, where, and under what conditions (exploration, empire, archaeology as a discipline, and changing ethics of collecting).
> 36 records have no accession number. Look at their `Description`: some objects are *no longer in the Museum's collections*. What does that tell you about a catalogue?
""")

md(r"""
## 9. Explore

This is the main exploring cell. Choose what to group by, and how many objects a group needs before it's shown.
Every dot is an object: hover to see which. The table underneath gives the numbers.
""")

code(r"""
GROUP_BY = "continent"  # @param ["continent", "country", "material", "process", "archaeology or ethnography", "decade acquired"]
MIN_OBJECTS = 20  # @param {type:"slider", min:1, max:200, step:1}

heads = arrows[arrows["length"] <= CUT_OFF]               # uses the cut-off from Section 6
data = heads[heads[GROUP_BY] != ""]
sizes = data[GROUP_BY].value_counts()
data = data[data[GROUP_BY].isin(sizes[sizes >= MIN_OBJECTS].index)]

summary = data.groupby(GROUP_BY)["length"].agg(["count", "median", "mean"]).round(1).sort_values("median")
fig = px.box(data, x=GROUP_BY, y="length", points="all", category_orders={GROUP_BY: list(summary.index)},
             hover_data=["Accession number", "Description", "country"],
             title=f"Length of arrowheads (up to {CUT_OFF} mm) by {GROUP_BY}")
fig.update_layout(yaxis_title="length (mm)")
fig.show()
summary
""")

md(r"""
A **box plot**: the line in the box is the median, the box holds the middle half of the objects, and the whiskers reach out to the rest.

> **Discussion.** Pick one difference you can see, for instance between continents or materials, and discuss:
> - Is it about the **arrowheads** (how people made them, for what), or about the **collection** (who collected what, and where)?
> - How many objects is it based on? Would you trust it with 20? With 5?
> - Iron arrowheads are longer than flint ones. Is that about material, or about date and place?
""")

md(r"""
## 10. Who collected them?

`Field Collector` is the person who collected an object where it was made or found; `PRM Source` is who the Museum got it from.
They can be different people, decades apart.
""")

code(r"""
WHO = "Field Collector"  # @param ["Field Collector", "PRM Source"]

people = arrows[WHO].replace("", "Not recorded").value_counts().head(15)
people.sort_values().plot.barh(figsize=(8, 5), color="steelblue")
plt.xlabel("number of objects")
plt.title(f"Top 15: {WHO}")
plt.show()
""")

md(r"""
> **Discussion.** The biggest "collector" is *Unknown*, and many names come with a `?`. A few people account for a large share of the rest. Look up one or two of them.
> How does knowing who collected change how you read the charts above? And whose names are *not* in this catalogue at all?
""")

md(r"""
## 11. Your turn: ask an AI, then check

Write down a question about the arrowheads that the data could answer, for example:
*Are archaeological arrowheads longer or shorter than ethnographic ones?* or *Which countries have the most poisoned arrows?*

Ask an AI for Python code to answer it, telling it that the DataFrame is called `arrows` and listing the columns you think it needs
(including the ones we made: `length`, `material`, `continent`, `country`, `archaeology or ethnography`, `year acquired`).
Paste its code into the cell below and run it.
""")

code(r"""
# paste the AI's code here

""")

md(r"""
> **Critical check.** Did the AI use our cleaned columns or the original messy ones? Did it make a cut-off decision, or forget to?
> Check its answer against the explore cell in Section 9.

## Summary

- Opening a file is already interpretation: the structure of the spreadsheet hid the records.
- An empty cell, a `?` and a `_x001D_` all mean something, and cleaning has to decide what.
- Turning text into a number (`Max L = 41 mm` → 41) needs checking against what *didn't* match.
- "What counts as an arrowhead" changes every statistic, just as "what counts as a sentence" did.
- Patterns in a museum catalogue can be about the objects, or about the people who collected and catalogued them.

**Next:** the Bate Collection of musical instruments: a different catalogue with the same habits, plus dates that are words rather than numbers.
""")

nb = nbf.v4.new_notebook()
nb["cells"] = cells
nb["metadata"] = {"colab": {"provenance": []}, "kernelspec": {"display_name": "Python 3", "name": "python3"},
                  "language_info": {"name": "python"}}
out = sys.argv[1] if len(sys.argv) > 1 else "notebooks/04_arrowheads.ipynb"
nbf.write(nb, out)
print("Wrote", out)
