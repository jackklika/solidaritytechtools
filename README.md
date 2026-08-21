# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/jackklika/solidaritytechtools/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                                 |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|----------------------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| solidaritytechtools/\_\_init\_\_.py                  |       11 |        0 |        0 |        0 |    100% |           |
| solidaritytechtools/client/base\_client.py           |      367 |      192 |       80 |        7 |     43% |148-150, 153, 155, 157, 169-170, 198-200, 203-\>205, 208, 234, 236, 238, 242, 245, 255-258, 270-275, 280, 283, 288, 293, 300-303, 310-311, 316-319, 333-338, 345, 352, 360, 370-371, 374, 386-391, 394, 399-402, 405, 408, 413, 416, 426-431, 434, 437, 440, 443, 453-458, 463, 466, 478-484, 487, 498-503, 506-509, 512-513, 516-517, 522-523, 526, 533-536, 539, 542, 547, 550, 555-559, 562, 569-570, 573, 578, 585-586, 589, 592, 595, 598, 603-604, 607, 613, 620-621, 624, 627, 634-637, 640, 643, 648, 653, 660-663, 666, 671-674, 677, 682-683, 686, 693-694, 697, 704-707, 710, 717-718, 727-730, 733, 736-737, 740, 745-748, 751, 756-759, 762-763, 768 |
| solidaritytechtools/client/models.py                 |      485 |        1 |       14 |        3 |     99% |124-\>132, 127, 130-\>125 |
| solidaritytechtools/json\_export/\_\_init\_\_.py     |        0 |        0 |        0 |        0 |    100% |           |
| solidaritytechtools/json\_export/export.py           |       26 |       12 |        2 |        0 |     50% |27, 34-46, 62 |
| solidaritytechtools/json\_export/models.py           |       53 |        0 |        0 |        0 |    100% |           |
| solidaritytechtools/match\_persons/\_\_init\_\_.py   |        0 |        0 |        0 |        0 |    100% |           |
| solidaritytechtools/match\_persons/match\_persons.py |       43 |       22 |        8 |        0 |     41% |43-55, 76-77, 87-94, 104-115 |
| solidaritytechtools/matching/\_\_init\_\_.py         |        4 |        0 |        0 |        0 |    100% |           |
| solidaritytechtools/matching/adapters.py             |       38 |        2 |        4 |        0 |     95% |   46, 102 |
| solidaritytechtools/matching/index.py                |      107 |        5 |       40 |        4 |     94% |99, 137-138, 160, 162, 165-\>163 |
| solidaritytechtools/matching/keys.py                 |       54 |        2 |       24 |        4 |     92% |76-\>71, 78-\>71, 110, 112 |
| solidaritytechtools/services/\_\_init\_\_.py         |        0 |        0 |        0 |        0 |    100% |           |
| solidaritytechtools/services/users.py                |      106 |       13 |       34 |        6 |     84% |52, 57-\>62, 63, 92, 95-\>89, 101, 121-130, 165-\>168 |
| solidaritytechtools/tools/\_\_init\_\_.py            |        0 |        0 |        0 |        0 |    100% |           |
| solidaritytechtools/tools/add\_traffic\_data.py      |      110 |        5 |       28 |        2 |     95% |266, 293, 299-301 |
| solidaritytechtools/utils/csv\_tools.py              |       41 |        2 |       18 |        3 |     92% |25, 48-\>46, 67 |
| solidaritytechtools/utils/emails.py                  |       21 |        2 |        8 |        2 |     86% |    35, 48 |
| solidaritytechtools/utils/membership.py              |       39 |        1 |        4 |        1 |     95% |        94 |
| solidaritytechtools/utils/normalize.py               |       23 |        0 |        8 |        0 |    100% |           |
| solidaritytechtools/utils/traffic\_score.py          |      205 |       40 |       60 |        9 |     75% |206, 211, 227-229, 244-246, 279, 308-318, 322-324, 339, 345, 431, 433, 435-\>429, 444, 474-484, 508-510, 530-532, 546 |
| **TOTAL**                                            | **1733** |  **299** |  **332** |   **41** | **79%** |           |


## Setup coverage badge

Below are examples of the badges you can use in your main branch `README` file.

### Direct image

[![Coverage badge](https://raw.githubusercontent.com/jackklika/solidaritytechtools/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/jackklika/solidaritytechtools/blob/python-coverage-comment-action-data/htmlcov/index.html)

This is the one to use if your repository is private or if you don't want to customize anything.

### [Shields.io](https://shields.io) Json Endpoint

[![Coverage badge](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/jackklika/solidaritytechtools/python-coverage-comment-action-data/endpoint.json)](https://htmlpreview.github.io/?https://github.com/jackklika/solidaritytechtools/blob/python-coverage-comment-action-data/htmlcov/index.html)

Using this one will allow you to [customize](https://shields.io/endpoint) the look of your badge.
It won't work with private repositories. It won't be refreshed more than once per five minutes.

### [Shields.io](https://shields.io) Dynamic Badge

[![Coverage badge](https://img.shields.io/badge/dynamic/json?color=brightgreen&label=coverage&query=%24.message&url=https%3A%2F%2Fraw.githubusercontent.com%2Fjackklika%2Fsolidaritytechtools%2Fpython-coverage-comment-action-data%2Fendpoint.json)](https://htmlpreview.github.io/?https://github.com/jackklika/solidaritytechtools/blob/python-coverage-comment-action-data/htmlcov/index.html)

This one will always be the same color. It won't work for private repos. I'm not even sure why we included it.

## What is that?

This branch is part of the
[python-coverage-comment-action](https://github.com/marketplace/actions/python-coverage-comment)
GitHub Action. All the files in this branch are automatically generated and may be
overwritten at any moment.