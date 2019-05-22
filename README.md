MoscowFlatRentPrediction
========================
As you may guessed, this case contains the implementation of a model for predicting the price of renting an apartment in Moscow. The repository contains all the steps from web-scrapping, data extraction to model creation.

### Install

This project requires Python 3.7 and the following Python libraries installed: 
* Numpy
* Sklearn
* Pandas
* Matplotlib
* Seaborn
* bs4
* Scipy

If you complete this project in Python 3.x, you will have to update the code in various
places including all relevant print statements. 

You will also need to have software installed to run and execute an iPython Notebook

I recommend you to install Anaconda, i pre-packaged
Python distribution that contains all of the necessary libraries and software for this project.
You can download it there:
    <https://www.anaconda.com/distribution/>

### Description

There are three files in this repository:

1. web_scrap_html.py - file contains an algorithm for founding html pages with rental ads. After founding it downloads found 
pages in folder.
2. html_parse.py - contain parser, which extracts data in format csv and saves into folder.
3. EDA.ipynb - notebook with full data analysis with beautiful visualizations and graphs. It contain all steps of feature 
extraction, 
feature engineering and feature selection. There appled basic machine learning concepts on data collected for flatting prices
in the Moscow to predict the selling price of a new flat. You can first explore the data to obtain
important features and descriptive statistics about the dataset. You can analyze performance 
for varying learning algorithms. Finally, you can test this optimal model and compare the predicted 
selling price to your statistics.

Files must installed in the same order.
