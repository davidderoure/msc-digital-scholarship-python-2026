# Python for Digital Scholarship

*MSc Digital Scholarship 2026*

Teaching materials for an introduction to Python for humanities students with no programming background.
We learn by working with real texts: concordances, sentence length and burstiness, in English and other languages, and we visualise the results.
Throughout, we use generative AI to help write code, and we practise checking what it gives us.

## Notebooks

Click **Open in Colab** to open a notebook in Google Colab. Then use **File → Save a copy in Drive**, so that you have your own copy to work in and your changes are saved.

| | Notebook | What it covers |
|---|---|---|
| [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/davidderoure/msc-digital-scholarship-python-2026/blob/main/notebooks/00_python_warmup.ipynb) | [00 · Warm-up: talking to Python](notebooks/00_python_warmup.ipynb) | Variables, functions, methods, lists, list comprehensions, error messages, and a concordance of *Pride and Prejudice* |
| [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/davidderoure/msc-digital-scholarship-python-2026/blob/main/notebooks/01_sentence_length.ipynb) | [01 · How long is a sentence?](notebooks/01_sentence_length.ipynb) | Three ways to split sentences, what counts as a word, characters and encoding (UTF-8, accents), other languages, and average sentence length in a whole novel, with a plot of the class's AI results |
| [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/davidderoure/msc-digital-scholarship-python-2026/blob/main/notebooks/02_burstiness.ipynb) | [02 · Burstiness: beyond the average](notebooks/02_burstiness.ipynb) | Simple measures of variation in sentence length, four novels compared, what the measures can't see, your own texts in any language, and a class style map |
| [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/davidderoure/msc-digital-scholarship-python-2026/blob/main/notebooks/03_ai_imitations.ipynb) | [03 · Can an AI write like Austen?](notebooks/03_ai_imitations.ipynb) | Comparing AI-written imitations with the original novels fairly, in English and French or a novel of your choice; the same data in different charts; memorisation and copying; copyright and text and data mining |

You can also download a notebook and open it in Colab with **File → Upload notebook**, or in Jupyter on your own computer.

## Other materials

- [Python syntax slides](slides/python_syntax_slides.pptx) ([PDF](slides/python_syntax_slides.pdf))
- [Python cheat sheet](cheatsheet/python_cheat_sheet.pdf) ([editable PowerPoint](cheatsheet/python_cheat_sheet.pptx))
- [Class sheet templates](templates/) for collecting passages in notebook 03: [`class_passages.csv`](templates/class_passages.csv) for the shared spreadsheet,
  and [`novel_titles.csv`](templates/novel_titles.csv) with the exact titles for a dropdown
- [Tools](tools/) for teachers: the Python scripts that build the syntax slides and notebook 02

## Your data and Colab

Colab is not covered by the University's agreement for Google Workspace, and its terms may allow what you put into it to be used to train AI models.
Only use public-domain texts, such as the Project Gutenberg books in these notebooks, or your own writing that you'd be happy to make public.
Never put unpublished research, interview data, restricted archival material or personal information into Colab.
The same applies to anything you add to a GitHub repository.

## Licence

The text, slides and cheat sheet are licensed under [CC BY 4.0](LICENSE). The code is licensed under the [MIT licence](LICENSE-CODE).
The novels used in the notebooks are downloaded from [Project Gutenberg](https://www.gutenberg.org) when the notebooks run, and are not part of this repository.
