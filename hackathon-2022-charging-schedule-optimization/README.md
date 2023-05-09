# Arcadia 2022 Hackathon: DER Charging Schedule Optimization

In this repository, we include some code for optimizing charging schedules, mostly using [linear programming](https://en.wikipedia.org/wiki/Linear_programming) with the [PuLP Python library](https://coin-or.github.io/pulp/#).

See demos [here](./residential_solver.ipynb) and [here](./commercial_solver.ipynb)!

## Installation

1. Install [pipenv](https://pipenv.pypa.io/en/latest/) with, e.g., `pip install --user pipenv`
1. Install packages using `pipenv install`
1. Run Python files, e.g. using `pipenv run python residential_solver.py`
1. Start a notebook server, e.g. using `pipenv run jupyter-lab`

## Guide
Google doc with our Hackathon ideas and more explanation of the opimization set-up (objective function, constraints, assumptions, etc)
https://docs.google.com/document/d/1qNlUHRh8pa8_cz_eTn5-fZ_MdFsRKTPb5BOUYAHIj5M/edit?usp=sharing
