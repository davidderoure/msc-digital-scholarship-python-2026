"""Build notebooks/02_burstiness.ipynb (MSc Digital Scholarship 2026).

Usage:  python tools/build_02_burstiness.py [output.ipynb]
Needs:  pip install nbformat
"""
import sys
import nbformat as nbf

cells = []
md = lambda s: cells.append(nbf.v4.new_markdown_cell(s.strip("\n")))
code = lambda s: cells.append(nbf.v4.new_code_cell(s.strip("\n")))

md(r"""
# Burstiness: beyond the average
*MSc Digital Scholarship 2026*

Last time we measured **average sentence length**. But two writers can have exactly the same average
and still sound completely different. One writes steadily, sentence after sentence of similar length.
Another writes a long, winding sentence full of clauses and qualifications, and then stops. Short. Like that.

**Burstiness** is an attempt to put a number on that difference. In this notebook we will:
1. See why an average hides this.
2. Measure it in simple ways that you can check by hand.
3. Apply them to four novels, and to texts of your own.
4. Ask what the measures *can't* see, and what people mean by "burstiness".

The formula usually called the "burstiness index" is in an optional section at the end, for anyone who wants it.

As before: **Shift + Enter** runs a cell, run from the top, and look out for the **Critical check** boxes.
""")

md(r"""
## 0. Setup: tools from last time

Each Colab notebook starts fresh, so this cell recreates the tools we built in the last notebook:
downloading a Gutenberg book, removing the licence text, finding words, and splitting into sentences.
You don't need to read it closely. Just run it.

Two changes since last time, following the *Other languages* section of the last notebook:
- `words_in` now finds letters in **any alphabet**, including accented letters such as *é*, so it works for French or Spanish as well as English.
  In Chinese, each character counts as one word, because written Chinese has no spaces between words.
- `sentence_lengths` takes a `language`, which tells NLTK which sentence splitter to use: `"english"`, `"french"`, `"spanish"` and so on.
  For languages NLTK doesn't know, such as Chinese or Hindi, it splits at punctuation instead, and prints a warning.
""")

code(r"""
import re
import random
import statistics
import urllib.request

import nltk
import regex
import pandas as pd
import matplotlib.pyplot as plt
from nltk.tokenize import sent_tokenize

nltk.download('punkt', quiet=True)
nltk.download('punkt_tab', quiet=True)


def get_gutenberg(book_id):
    url = f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt"
    raw = urllib.request.urlopen(url).read().decode("utf-8")
    return raw.replace("\r\n", "\n")

def strip_gutenberg(raw):
    start = raw.find("*** START OF")
    start = raw.find("\n", start) + 1
    end = raw.find("*** END OF")
    return raw[start:end].strip()

def words_in(text):
    # each Chinese character counts as one word; otherwise letters in any alphabet (with their accents),
    # optionally joined by an apostrophe or hyphen
    return regex.findall(r"\p{Han}|[\p{L}\p{M}]+(?:['’-][\p{L}\p{M}]+)*", text)

warned = set()                                 # languages we have already warned about

def split_sentences(text, language="english"):
    try:
        return sent_tokenize(text, language=language)
    except LookupError:                        # NLTK has no model for this language: use a pattern instead
        if language not in warned:
            warned.add(language)
            print(f"No NLTK sentence model for '{language}': splitting at . ! ? 。 ！ ？ । instead.")
            print("  That's expected for languages such as Chinese or Hindi. Otherwise, check the language")
            print("  is spelled in English and lower case, e.g. 'french', 'spanish', 'german'.")
        return [s for s in re.split(r'(?<=[.!?。！？।])\s*', text) if s.strip()]

def sentence_lengths(text, language="english"):
    return [len(words_in(s)) for s in split_sentences(text, language)]

print("Ready.")
""")

# ── 1. Same average, different feel ───────────────────────────────────────
md(r"""
## 1. Same average, different feel

Here are three imaginary writers. Each list is the length (in words) of eight sentences in a row.
""")

code(r"""
metronome = [12, 13, 12, 11, 12, 13, 12, 11]
varied    = [3, 25, 4, 30, 2, 20, 5, 7]
extreme   = [1, 2, 1, 60, 2, 1, 3, 26]

print("metronome:", statistics.mean(metronome))
print("varied:   ", statistics.mean(varied))
print("extreme:  ", statistics.mean(extreme))
""")

md(r"""
All three have an average of exactly 12 words per sentence. If average sentence length were all we measured,
these writers would look identical. Let's draw them:
""")

code(r"""
fig, axes = plt.subplots(1, 3, figsize=(12, 3), sharey=True)
for ax, name, lengths in zip(axes, ["metronome", "varied", "extreme"], [metronome, varied, extreme]):
    ax.bar(range(1, 9), lengths, color="steelblue")
    ax.axhline(12, color="black", linestyle="--", linewidth=1)   # the average
    ax.set_title(name)
    ax.set_xlabel("sentence number")
axes[0].set_ylabel("words")
plt.show()
""")

md(r"""
> **Discussion.** Can you think of real writers, or genres, that resemble each of these three?
> Would a reader *notice* the difference between them? Would they notice it in a single paragraph, or only over a chapter?
""")

# ── 2. Short and long sentences ───────────────────────────────────────────
md(r"""
## 2. First measure: how many very short and very long sentences?

The simplest way to describe variety is to **count**. What share of the sentences are very short, and what share are very long?
We have to decide what "very short" and "very long" mean. Here they are set as **fewer than 10 words** and **more than 40 words**.

The function uses a list comprehension with `if` to keep only the short (or long) sentences, then counts them with `len`.
""")

code(r"""
SHORT = 10     # fewer words than this counts as "short"
LONG = 40      # more words than this counts as "long"

def percent_short(lengths, short=SHORT):
    return round(100 * len([x for x in lengths if x < short]) / len(lengths))

def percent_long(lengths, long=LONG):
    return round(100 * len([x for x in lengths if x > long]) / len(lengths))

for name, lengths in [("metronome", metronome), ("varied", varied), ("extreme", extreme)]:
    print(f"{name:10} {percent_short(lengths):3}% short   {percent_long(lengths):3}% long")
""")

md(r"""
> **Critical check.**
> - Count the short and long sentences in each list by hand. Do you agree with the percentages?
> - The thresholds of 10 and 40 words are **a decision**, not a fact. Change `SHORT` and `LONG` and run the cell again. Do the writers keep the same order?
> - A writer whose sentences are all longer will automatically have more "long" sentences. One fix is to set the thresholds relative to each writer's own average,
>   such as *less than half the average* and *more than twice the average*. Try `SHORT = 6` and `LONG = 24` for these three writers, whose average is 12.
""")

# ── 3. Typical distance from the average ──────────────────────────────────
md(r"""
## 3. Second measure: how far is a typical sentence from the average?

Counting short and long sentences ignores everything in between. A measure that uses **every** sentence:
1. Work out the average length.
2. For each sentence, find how many words it is **away from the average**, ignoring whether it's longer or shorter. (`abs` gives the distance without a minus sign.)
3. Average those distances.

Here it is by hand for the `varied` writer:
""")

code(r"""
avg = statistics.mean(varied)
distances = [abs(x - avg) for x in varied]

print("lengths:  ", varied)
print("distances:", distances)
print("typical distance from the average:", statistics.mean(distances), "words")
""")

md(r"""
So a typical sentence by this writer is about 10 words longer or shorter than average. As a function:
""")

code(r"""
def typical_distance(lengths):
    avg = statistics.mean(lengths)
    return statistics.mean([abs(x - avg) for x in lengths])

for name, lengths in [("metronome", metronome), ("varied", varied), ("extreme", extreme)]:
    print(f"{name:10} {typical_distance(lengths):5.2f} words")
""")

md(r"""
### A problem of scale
Suppose a fourth writer writes exactly like `varied`, but every sentence is **twice as long**.
Is this writer more varied? Or just *wordier*?
""")

code(r"""
wordy = [2 * x for x in varied]      # double every length
print(wordy)
print("average:", statistics.mean(wordy), "   typical distance:", typical_distance(wordy), "words")
""")

md(r"""
The typical distance doubled too. So writers with longer sentences tend to get bigger distances, even when the *pattern* of long and short is the same.
The fix is to **divide by the average**, which gives the typical distance as a proportion of the average. We'll call this the **variation**:
""")

code(r"""
def variation(lengths):
    return typical_distance(lengths) / statistics.mean(lengths)

for name, lengths in [("metronome", metronome), ("varied", varied), ("extreme", extreme), ("wordy", wordy)]:
    print(f"{name:10} variation = {variation(lengths):.2f}")
""")

md(r"""
**How to read it:** a variation of 0.81 means that a typical sentence is about 81% longer or shorter than the average.
0 would mean every sentence is exactly the same length.

> **Critical check.**
> - Do these values put the writers in the order you expected from the bar charts in Section 1?
> - Why do `varied` and `wordy` get the same variation?
> - Statisticians call this measure the *mean absolute deviation*, divided by the mean. You may also meet the *standard deviation*, which does a similar job in a more complicated way: see the optional Section 9.
""")

# ── 4. Four novels ────────────────────────────────────────────────────────
md(r"""
## 4. Four novels

Now we download four novels, keep the length of every sentence, and measure each one.
The results go into a **dictionary**: a set of labelled values, written with curly brackets `{ }`, which pandas turns into a row of a table.
This takes a minute.
""")

code(r"""
books = {
    "Pride and Prejudice": 1342,
    "Emma": 158,
    "A Tale of Two Cities": 98,
    "Frankenstein": 84,
}

book_lengths = {}
for title, book_id in books.items():
    book_lengths[title] = sentence_lengths(strip_gutenberg(get_gutenberg(book_id)))

def profile(title, lengths):
    return {
        "title": title,
        "sentences": len(lengths),
        "mean": round(statistics.mean(lengths), 1),
        "median": statistics.median(lengths),
        "% short": percent_short(lengths),
        "% long": percent_long(lengths),
        "variation": round(variation(lengths), 2),
    }

novels = pd.DataFrame([profile(title, lengths) for title, lengths in book_lengths.items()])
novels
""")

md(r"""
> **Critical check.**
> - Which novel is the most even? Do the two measures of variety (the percentages, and the variation) agree?
> - The two Austen novels: are they closer to each other than to the other two authors?
> - Which differences are big enough to mean something? We have one number per novel, so we don't know yet how much
>   it would vary between, say, different chapters of the same book. (Section 7 comes back to this.)
""")

md(r"""
### Seeing the rhythm
A number summarises; a picture lets you look. Here are the first 150 sentences of two novels.
""")

code(r"""
pp = book_lengths["Pride and Prejudice"]
fr = book_lengths["Frankenstein"]

fig, axes = plt.subplots(2, 1, figsize=(12, 5), sharex=True, sharey=True)
axes[0].bar(range(150), pp[:150], color="steelblue")
axes[0].set_title("Pride and Prejudice: first 150 sentences")
axes[1].bar(range(150), fr[:150], color="darkorange")
axes[1].set_title("Frankenstein: first 150 sentences")
axes[1].set_xlabel("sentence number")
plt.show()
""")

md(r"""
> **Critical check.** What text are these 150 sentences actually from? (Remember the preface in *Pride and Prejudice*, and
> *Frankenstein* opens with letters.) Try `pp[3000:3150]` instead to look at a passage from the middle of the novel.
""")

# ── 5. Cleaning ───────────────────────────────────────────────────────────
md(r"""
## 5. How much does cleaning matter?

Last time we found "sentences" that were really chapter headings, stray numbers, or exclamations like "Oh!".
Let's see what happens to the variation if we leave out every "sentence" shorter than 3 words.
""")

code(r"""
def drop_short(lengths, minimum=3):
    return [x for x in lengths if x >= minimum]

print("Pride and Prejudice")
print("  all sentences:  variation =", round(variation(pp), 2))
print("  3+ words only:  variation =", round(variation(drop_short(pp)), 2))
""")

md(r"""
> **Critical check.** "Oh!" and "Impossible!" are real sentences, part of Austen's style, not errors.
> A chapter heading is not. A rule like "drop anything under 3 words" can't tell them apart.
> Try changing `minimum` to 1, 5 and 10. How much does the variation move? How does that compare with the differences *between novels* in Section 4?
""")

# ── 6. Order ──────────────────────────────────────────────────────────────
md(r"""
## 6. What these measures can't see: order

Here is something important. Shuffle the sentences of a novel into a random order.
The writing would be nonsense, and its rhythm destroyed. What happens to the variation?
""")

code(r"""
random.seed(1)               # so everyone gets the same "random" shuffle
shuffled = pp.copy()
random.shuffle(shuffled)

print("original order:", round(variation(pp), 2))
print("shuffled:      ", round(variation(shuffled), 2))
""")

md(r"""
Exactly the same. The percentages and the variation only depend on *which* lengths occur, not *in what order*.
So they measure how varied the sentence lengths are, **not** the rhythm of short-after-long that we described in the introduction.

One way to capture order: look at how much the length **jumps from one sentence to the next**, on average.
`zip(lengths, lengths[1:])` pairs each sentence with the one after it.
""")

code(r"""
def average_jump(lengths):
    jumps = [abs(b - a) for a, b in zip(lengths, lengths[1:])]   # each sentence compared with the next one
    return statistics.mean(jumps)

print("original order:", round(average_jump(pp), 1), "words")
print("shuffled:      ", round(average_jump(shuffled), 1), "words")
""")

md(r"""
> **Critical check.**
> - If Austen deliberately alternated long and short sentences, would the original order give a **bigger** or **smaller** jump than the shuffle?
> - Which do you actually see? What might cause neighbouring sentences to be more alike than chance? (Think about stretches of quick dialogue versus long passages of narration.)
> - Try it for Frankenstein (`fr`). Same pattern?
> - Here, the *comparison with a shuffled version* does the real work. A number on its own ("the length jumps by about 15 words") means little; a number compared with "what you'd expect if order didn't matter" means much more.
""")

# ── 7. Short texts ────────────────────────────────────────────────────────
md(r"""
## 7. How reliable is a score from a short text?

Novels give us thousands of sentences. But people often want to measure a short piece: an essay, a letter, a paragraph
someone suspects was written by AI. Here we take ten random runs of 15 consecutive sentences from *Pride and Prejudice*,
all by the same author, and measure each:
""")

code(r"""
random.seed(2)
for i in range(10):
    start = random.randrange(len(pp) - 15)
    chunk = pp[start:start + 15]
    print(f"sentences {start:5}-{start + 15:5}:  variation = {variation(chunk):.2f}")
""")

md(r"""
> **Critical check.** Same author, same novel. How much does the variation change from passage to passage?
> Compare that spread with the differences between the four novels in Section 4.
> What does this tell you about using these measures to judge who (or what) wrote a single short passage?
""")

# ── 8. Your own texts ─────────────────────────────────────────────────────
md(r"""
## 8. Your own texts

Now measure a text of your own choosing. It could be:
- a public-domain text from your field, or in another language;
- your own writing that you'd be happy to make public;
- a passage generated by an AI.

Don't paste anything unpublished, restricted or personal (see *Your data and Colab* at the top of the warm-up notebook).
Set `LANGUAGE` to the language of your text, **in English and lower case**: `"french"`, not `"français"`. NLTK's splitter knows English, French, Spanish, German, Italian, Russian and several more;
for other languages, such as Chinese, it splits at punctuation instead.
""")

code(r'''
LANGUAGE = "english"

my_text = """
Paste your text here. Replace all of this text. Keep the three quotation marks at each end.
"""

lengths = sentence_lengths(my_text, LANGUAGE)
print("sentences:", len(lengths))
print("lengths:  ", lengths)
print()
print("mean:     ", round(statistics.mean(lengths), 1), "words")
print("% short:  ", percent_short(lengths))
print("% long:   ", percent_long(lengths))
print("variation:", round(variation(lengths), 2))
''')

md(r"""
> **Critical check.** Look at the list of lengths before you believe the averages. Are there any zero-word or one-word "sentences"
> (headings, numbers, stray punctuation)? How many sentences does your text have, and what did Section 7 say about short texts?
""")

md(r"""
### Putting the class's results on one picture

So that nobody has to share their actual text, we share only the **numbers**. Add one line per text below:
a short label, what kind of text it is (`"own writing"`, `"published"` or `"AI"`), and its mean and variation from the cell above.
Or, if your lecturer has set up a shared sheet, paste its link (published as CSV, with columns `label`, `kind`, `mean` and `variation`).
""")

code(r"""
class_results = [
    # {"label": "my essay", "kind": "own writing", "mean": 18.2, "variation": 0.55},    <- examples only: replace with real results
    # {"label": "ChatGPT as Austen", "kind": "AI", "mean": 24.0, "variation": 0.40},
]

CLASS_SHEET_URL = ""      # or a published CSV link with columns: label, kind, mean, variation

if CLASS_SHEET_URL:
    class_results = pd.read_csv(CLASS_SHEET_URL).to_dict("records")

results = pd.DataFrame(class_results, columns=["label", "kind", "mean", "variation"])
results
""")

md(r"""
The picture below is a simple **style map**. Each text is a point: further right means longer sentences on average,
higher up means more varied sentence lengths. The four novels are shown in grey for comparison.
""")

code(r"""
STYLES = {                     # colour and marker for each kind of text
    "own writing": ("#1f77b4", "o"),
    "published":   ("#2ca02c", "s"),
    "AI":          ("#ff7f0e", "^"),
}

def plot_style_map(results, novels):
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.scatter(novels["mean"], novels["variation"], s=60, color="lightgray", edgecolor="gray", zorder=2)
    for _, row in novels.iterrows():
        ax.annotate(row["title"], (row["mean"], row["variation"]), xytext=(6, 4),
                    textcoords="offset points", fontsize=9, color="dimgray")
    for kind, (colour, marker) in STYLES.items():
        these = results[results["kind"] == kind]
        if len(these):
            ax.scatter(these["mean"], these["variation"], s=80, color=colour, marker=marker,
                       edgecolor="white", linewidth=1.5, label=f"{kind} ({len(these)})", zorder=3)
    others = results[~results["kind"].isin(STYLES)]
    if len(others):
        print("Not plotted (kind not recognised):", list(others["label"]))
    ax.set_xlabel("mean sentence length (words)")
    ax.set_ylabel("variation (typical distance from the average ÷ average)")
    ax.grid(color="lightgray", linewidth=0.5)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    if len(results):
        ax.legend(frameon=False)
    else:
        print("No class results yet: add some to class_results above, run that cell, then this one.")
    plt.tight_layout()
    plt.show()

plot_style_map(results, novels)
""")

md(r"""
> **Discussion.**
> - Where do the AI texts sit compared with the novels and with people's own writing? Do they cluster together?
> - Are any texts far from everything else? Look at the text itself: is it the writing, or something in the data (a list, a poem, a lot of headings)?
> - Texts in other languages: is it fair to compare their sentence lengths with English ones? What counts as a word differs between languages (think of French *l'homme* or Chinese).
> - Which points would you trust least, given Section 7?
""")

# ── 9. Optional: standard deviation and the burstiness index ─────────────
md(r"""
## 9. Going further (optional): the standard deviation and the burstiness index

You'll meet these in statistics, and in writing about AI detection. They do a similar job to our variation measure, with more mathematics.

### The standard deviation
The **standard deviation** is another way of saying "how far a typical sentence is from the average". Instead of averaging the distances,
it **squares** them, averages the squares, and takes the **square root** at the end. Squaring gives extra weight to the sentences that are very far from the average.
(There are two versions in Python, `stdev` and `pstdev`; we use `pstdev`. For long texts the difference is tiny.)
""")

code(r"""
avg = statistics.mean(varied)
squares = [(x - avg) ** 2 for x in varied]

print("by hand:   ", round(statistics.mean(squares) ** 0.5, 2))
print("statistics:", round(statistics.pstdev(varied), 2))
print("compare our typical distance:", typical_distance(varied))
""")

md(r"""
### The burstiness index
A widely used **burstiness index** was proposed by the physicists Goh and Barabási (2008), who were studying
the timing of events such as emails being sent, earthquakes and heartbeats. Some events come in bursts, with long quiet gaps in between.

With **σ** (sigma) for the standard deviation and **μ** (mu) for the mean:

$$B = \frac{\sigma - \mu}{\sigma + \mu}$$

It always lies between **−1** and **+1**:
- **−1**: perfectly regular (every value the same).
- **0**: the standard deviation equals the mean. In Goh and Barabási's setting, this is what events happening *completely at random* look like.
- **+1**: extremely bursty.
""")

code(r"""
def burstiness(lengths):
    mu = statistics.mean(lengths)
    sigma = statistics.pstdev(lengths)
    return (sigma - mu) / (sigma + mu)

for name, lengths in [("metronome", metronome), ("varied", varied), ("extreme", extreme), ("wordy", wordy)]:
    print(f"{name:10} variation = {variation(lengths):.2f}   B = {burstiness(lengths):6.3f}")

print()
for title, lengths in book_lengths.items():
    print(f"{title:22} variation = {variation(lengths):.2f}   B = {burstiness(lengths):6.3f}")
""")

md(r"""
> **Critical check.**
> - Do B and our variation put the writers and the novels in the same order?
> - B was designed for the **gaps between events in time**. We're applying it to **sentence lengths**.
>   Does "0 means random" still mean anything for sentences? What would a "random" sentence length even be?
>   Borrowing a measure from another field is common, and often useful, but its built-in assumptions come along with it.
""")

# ── 10. Burstiness and AI ────────────────────────────────────────────────
md(r"""
## 10. "Burstiness" and generative AI

You may already have met the word *burstiness* in discussions of **detecting AI-written text**: the claim that human writing is
"burstier" than AI writing. Be careful: different people use the same word for **different measurements**.
Some AI-detection tools use it for variation in how *predictable* each sentence is to a language model, not for sentence length at all.
Whenever you see the word, ask: *burstiness of what, measured how, compared with what?*

### Exercise: interrogate an AI
1. Ask an AI assistant: *"What is burstiness in text, and how do I calculate it in Python?"*
2. Paste its code into a new cell. Run it on `metronome`, `varied` and `extreme`. Does it rank them sensibly? Does it agree with our `variation` function, or with `burstiness` from Section 9? If not, is it measuring something different, or is one of them wrong?
3. Ask it where its definition comes from. If it gives a reference, **check that the reference exists** and says what the AI claims it says.
4. Ask it whether human writing is burstier than AI writing. What evidence does it offer? Is that evidence about sentence length, or something else?
""")

md(r"""
## Summary

| Measure | What it captures | Blind spot |
|---|---|---|
| Mean sentence length | How long sentences are on average | Says nothing about variety |
| % short and % long | How often sentences are very short or very long | Depends on where you set the thresholds |
| Variation (typical distance ÷ average) | How varied the lengths are, for any average length | Ignores order; unstable on short texts |
| Average jump between neighbours (vs. shuffled) | Something about rhythm and order | Still only about length, not content |
| Standard deviation, burstiness B (optional) | Variety, giving extra weight to extremes | Harder to explain; B's "0" was designed for another field |

**Next:** we put several of these measures together, for several authors, and ask whether they can tell writers apart.
""")

nb = nbf.v4.new_notebook()
nb.cells = cells
nb.metadata = {
    "colab": {"provenance": [], "toc_visible": True},
    "kernelspec": {"name": "python3", "display_name": "Python 3"},
    "language_info": {"name": "python"},
}
out = sys.argv[1] if len(sys.argv) > 1 else "notebooks/02_burstiness.ipynb"
nbf.write(nb, out)
print("wrote", out)
