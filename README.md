# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/jackklika/solidaritytechtools/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                                 |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|----------------------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| solidaritytechtools/\_\_init\_\_.py                  |       20 |        0 |        2 |        0 |    100% |           |
| solidaritytechtools/client/base\_client.py           |      392 |      187 |       86 |        7 |     48% |202-204, 207, 209, 211, 223-224, 255, 290, 292, 294, 298, 311-314, 326-331, 336, 339, 344, 349, 356-359, 366-367, 372-375, 389-394, 401, 408, 416, 426-427, 430, 442-447, 450, 455-458, 461, 464, 469, 472, 482-487, 490, 493, 496, 499, 509-514, 519, 522, 534-540, 543, 554-559, 562-565, 568-569, 572-573, 578-579, 582, 589-592, 595, 598, 603, 606, 611-615, 618, 625-626, 629, 634, 641-642, 645, 648, 651, 659-660, 663, 669, 676-677, 680, 683, 690-693, 696, 699, 704, 709, 716-719, 722, 727-730, 733, 738-739, 742, 749-750, 753, 760-763, 766, 773-774, 783-786, 789, 792-793, 796, 801-804, 807, 812-815, 818-819, 824 |
| solidaritytechtools/client/models.py                 |      485 |        1 |       14 |        3 |     99% |124-\>132, 127, 130-\>125 |
| solidaritytechtools/export\_matching/\_\_init\_\_.py |        2 |        0 |        0 |        0 |    100% |           |
| solidaritytechtools/export\_matching/matching.py     |       39 |       19 |        8 |        0 |     43% |54-66, 82-88, 107-117 |
| solidaritytechtools/json\_export/\_\_init\_\_.py     |        0 |        0 |        0 |        0 |    100% |           |
| solidaritytechtools/json\_export/export.py           |       26 |       12 |        2 |        0 |     50% |27, 34-46, 62 |
| solidaritytechtools/json\_export/models.py           |       53 |        0 |        0 |        0 |    100% |           |
| solidaritytechtools/match\_persons/\_\_init\_\_.py   |        8 |        4 |        2 |        0 |     40% |     15-19 |
| solidaritytechtools/match\_persons/match\_persons.py |       14 |        0 |        2 |        0 |    100% |           |
| solidaritytechtools/matching/\_\_init\_\_.py         |        4 |        0 |        0 |        0 |    100% |           |
| solidaritytechtools/matching/adapters.py             |       38 |        2 |        4 |        0 |     95% |   46, 102 |
| solidaritytechtools/matching/index.py                |      107 |        5 |       40 |        4 |     94% |99, 137-138, 160, 162, 165-\>163 |
| solidaritytechtools/matching/keys.py                 |       54 |        2 |       24 |        4 |     92% |76-\>71, 78-\>71, 110, 112 |
| solidaritytechtools/services/\_\_init\_\_.py         |        0 |        0 |        0 |        0 |    100% |           |
| solidaritytechtools/services/users.py                |      109 |       15 |       34 |        6 |     83% |52, 57-\>62, 63, 92, 95-\>89, 101, 121-130, 165-\>168, 237-238 |
| solidaritytechtools/tools/\_\_init\_\_.py            |        0 |        0 |        0 |        0 |    100% |           |
| solidaritytechtools/tools/add\_traffic\_data.py      |      110 |        5 |       28 |        2 |     95% |266, 293, 299-301 |
| solidaritytechtools/utils/csv\_tools.py              |       41 |        2 |       18 |        3 |     92% |25, 48-\>46, 67 |
| solidaritytechtools/utils/emails.py                  |       21 |        2 |        8 |        2 |     86% |    35, 48 |
| solidaritytechtools/utils/membership.py              |       39 |        1 |        4 |        1 |     95% |        94 |
| solidaritytechtools/utils/normalize.py               |       23 |        0 |        8 |        0 |    100% |           |
| solidaritytechtools/utils/traffic\_score.py          |      205 |       40 |       60 |        9 |     75% |206, 211, 227-229, 244-246, 279, 308-318, 322-324, 339, 345, 431, 433, 435-\>429, 444, 474-484, 508-510, 530-532, 546 |
| **TOTAL**                                            | **1790** |  **297** |  **344** |   **41** | **80%** |           |


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