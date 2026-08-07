# Repository Coverage

[Full report](https://htmlpreview.github.io/?https://github.com/jackklika/solidaritytechtools/blob/python-coverage-comment-action-data/htmlcov/index.html)

| Name                                                 |    Stmts |     Miss |   Branch |   BrPart |   Cover |   Missing |
|----------------------------------------------------- | -------: | -------: | -------: | -------: | ------: | --------: |
| solidaritytechtools/\_\_init\_\_.py                  |        8 |        0 |        0 |        0 |    100% |           |
| solidaritytechtools/client/base\_client.py           |      367 |      208 |       80 |        4 |     38% |129, 132, 146-148, 151, 153, 155, 159, 167-168, 196-198, 201-203, 206, 209-211, 216, 230-237, 240, 243, 246, 253-256, 268-273, 278, 281, 286, 291, 298-301, 308-309, 314-317, 331-336, 343, 350, 358, 368-369, 372, 384-389, 392, 397-400, 403, 406, 411, 414, 424-429, 432, 435, 438, 441, 451-456, 461, 464, 476-482, 485, 496-501, 504-507, 510-511, 514-515, 520-521, 524, 531-534, 537, 540, 545, 548, 553-557, 560, 567-568, 571, 576, 583-584, 587, 590, 593, 596, 601-602, 605, 611, 618-619, 622, 625, 632-635, 638, 641, 646, 651, 658-661, 664, 669-672, 675, 680-681, 684, 691-692, 695, 702-705, 708, 715-716, 725-728, 731, 734-735, 738, 743-746, 749, 754-757, 760-761, 766 |
| solidaritytechtools/client/models.py                 |      456 |        0 |        0 |        0 |    100% |           |
| solidaritytechtools/json\_export/\_\_init\_\_.py     |        0 |        0 |        0 |        0 |    100% |           |
| solidaritytechtools/json\_export/export.py           |       26 |       12 |        2 |        0 |     50% |27, 34-46, 62 |
| solidaritytechtools/json\_export/models.py           |       53 |        0 |        0 |        0 |    100% |           |
| solidaritytechtools/match\_persons/\_\_init\_\_.py   |        0 |        0 |        0 |        0 |    100% |           |
| solidaritytechtools/match\_persons/match\_persons.py |       93 |       69 |       42 |        0 |     18% |28-35, 39-41, 45-47, 62-133, 154-155, 165-172, 182-193 |
| solidaritytechtools/services/\_\_init\_\_.py         |        0 |        0 |        0 |        0 |    100% |           |
| solidaritytechtools/services/users.py                |      106 |       13 |       34 |        6 |     84% |52, 57-\>62, 63, 92, 95-\>89, 101, 121-130, 165-\>168 |
| solidaritytechtools/tools/\_\_init\_\_.py            |        0 |        0 |        0 |        0 |    100% |           |
| solidaritytechtools/tools/add\_traffic\_data.py      |      116 |        5 |       30 |        2 |     95% |278, 305, 311-313 |
| solidaritytechtools/utils/csv\_tools.py              |       41 |        2 |       18 |        3 |     92% |25, 48-\>46, 67 |
| solidaritytechtools/utils/emails.py                  |       21 |        2 |        8 |        2 |     86% |    35, 48 |
| solidaritytechtools/utils/traffic\_score.py          |      205 |       76 |       60 |        4 |     54% |206, 211, 227-229, 244-246, 279, 288, 299-303, 308-318, 322-324, 339, 345, 415-445, 472-491, 508-510, 530-532, 546 |
| **TOTAL**                                            | **1492** |  **387** |  **274** |   **21** | **68%** |           |


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