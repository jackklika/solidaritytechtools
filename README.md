# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/jackklika/solidaritytechtools/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                                 |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|----------------------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| solidaritytechtools/\_\_init\_\_.py                  |        7 |        0 |        0 |        0 |    100% |           |
| solidaritytechtools/client/base\_client.py           |      366 |      208 |       80 |        4 |     38% |127, 130, 144-146, 149, 151, 153, 157, 165-166, 194-196, 199-201, 204, 207-209, 214, 228-235, 238, 241, 244, 251-254, 266-271, 276, 279, 284, 289, 296-299, 306-307, 312-315, 329-334, 341, 348, 356, 366-367, 370, 382-387, 390, 395-398, 401, 404, 409, 412, 422-427, 430, 433, 436, 439, 449-454, 459, 462, 474-480, 483, 494-499, 502-505, 508-509, 512-513, 518-519, 522, 529-532, 535, 538, 543, 546, 551-555, 558, 565-566, 569, 574, 581-582, 585, 588, 591, 594, 599-600, 603, 609, 616-617, 620, 623, 630-633, 636, 639, 644, 649, 656-659, 662, 667-670, 673, 678-679, 682, 689-690, 693, 700-703, 706, 713-714, 723-726, 729, 732-733, 736, 741-744, 747, 752-755, 758-759, 764 |
| solidaritytechtools/client/models.py                 |      277 |        0 |        0 |        0 |    100% |           |
| solidaritytechtools/json\_export/\_\_init\_\_.py     |        0 |        0 |        0 |        0 |    100% |           |
| solidaritytechtools/json\_export/export.py           |       26 |       12 |        2 |        0 |     50% |27, 34-46, 62 |
| solidaritytechtools/json\_export/models.py           |       38 |        0 |        0 |        0 |    100% |           |
| solidaritytechtools/match\_persons/\_\_init\_\_.py   |        0 |        0 |        0 |        0 |    100% |           |
| solidaritytechtools/match\_persons/match\_persons.py |       90 |       69 |       42 |        0 |     16% |26-33, 37-39, 43-45, 60-131, 152-153, 163-170, 180-191 |
| solidaritytechtools/services/\_\_init\_\_.py         |        0 |        0 |        0 |        0 |    100% |           |
| solidaritytechtools/services/users.py                |      105 |       13 |       34 |        6 |     83% |50, 55-\>60, 61, 90, 93-\>87, 99, 119-128, 163-\>166 |
| solidaritytechtools/tools/\_\_init\_\_.py            |        0 |        0 |        0 |        0 |    100% |           |
| solidaritytechtools/tools/add\_traffic\_data.py      |      106 |        5 |       30 |        2 |     95% |276, 303, 309-311 |
| solidaritytechtools/utils/csv\_tools.py              |       40 |        2 |       18 |        3 |     91% |23, 46-\>44, 65 |
| solidaritytechtools/utils/emails.py                  |       20 |        2 |        8 |        2 |     86% |    33, 46 |
| solidaritytechtools/utils/traffic\_score.py          |      205 |       76 |       60 |        4 |     54% |206, 211, 227-229, 244-246, 279, 288, 299-303, 308-318, 322-324, 339, 345, 415-445, 472-491, 508-510, 530-532, 546 |
| **TOTAL**                                            | **1280** |  **387** |  **274** |   **21** | **64%** |           |


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