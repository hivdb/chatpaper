# Chat Paper

## How to use

0. prepare your data
    - save papers in `chatpaper/papers` folder
    - create markdown file for each paper including methods and results text
    - create or use existing `prompt_template` in `txt` format
    - update `questions.txt` to use your question list
1. update your Xcode to newest version
2. run `make init`
3. copy *.env.example* to *.env* and enter your openai key
4. run `make chat`, and have fun


## deps

- openai-cookbook apps file-q-and-a nextjs


## Ways to prepare the document

1. Get html page if possible
2. run script to get method and result sections
3. check auto fetched figures and tables
4. if the table is not right, try one of these
    - open pdf using word, convert word to html
    - open pdf using acrobat, select table export as html
    - copy table from pdf and paste to excel
    - the best option is directly get table from html file


## About Parse paper

Note: although there exists many kinds of tools to extract content from a PDF document, none of them can do it without introducing errors. Even more, none of them tools can be used to get a consensus result. So if we want to make sure the parsed content doesn't have errors, manually checking the result is necessary.
