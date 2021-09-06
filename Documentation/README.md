# Introduction
We provide the instructions for 

# Prerequisites

In order to edit and run the code, you will need the followings:
* PyCharm - preferred IDE
* Anaconda - for installing the Python environment
* Anaconda Jupyter Notebooks - as secondary IDE, and environment to show the results
Note: for instructions about how to install a Conda environment, read the section
*Setup Anaconda environment*


## Software to install
Additionally, you will have to have installed:
* Ghostscript - it is used on background by Wand, to extract images from PDFs.
* Tesseract - it is used on background by pytesseract, for OCR
Both of these might be installed before / during / after installation of corresponding 
Python libraries, just make sure they match and paths are recognized

Add to your installation:
* MongoDBCompass (https://www.mongodb.com/try/download/compass)

# Setup Anaconda environment

From `https://www.anaconda.com/distribution/` choose Python 3.7 version and download 64-Bit Graphical Installer (462 MB)

## Optional, change the default directory for your Anaconda

Open an Anaconda Prompt: press Windows key, type Anaconda Prompt (and open it as Administrator)

### Generate config file

`jupyter notebook --generate-config`

Edit `jupyter_notebook_config.py` in `.username\\.jupyter` folder:

Look for  c.NotebookApp.notebook_dir and edit:
`c.NotebookApp.notebook_dir = <path_to_your_working_directory>`

Example:
`c.NotebookApp.notebook_dir = C:\\workspace`

## Install environment

In Anaconda prompt, run:

`conda create -n endava_workshop python=3.7 numpy scipy matplotlib pillow  jupyter seaborn opencv spacy luigi pymongo`

## Activate environment
`conda activate endava_workshop`

## Additional packages installation using conda install
`conda install -c conda-forge spacy`

## Install using pip install
pip install requirements.txt

## List packages installed in an environment

conda list -n endava_workshop

## Deactivate current environment

conda deactivate endava_workshop

# Python modules installation

A requirements.txt file is provided. Activate your Conda environment with:
`conda activate endava_workshop` and run `pip install` in the Anaconda prompt.

For configuration of Python environment, follow the instructions below:

`pip install requirements.txt`

# Initialize storage

You will have to initialize 2 type of storage:
* MongoDB database and collection
* Binary storage on your local disk

## Initialize MongoDB

Open Compass (MongoDB client) and:
 * Create a database with your username. Ex: gpreda
 * Create a collection with the name `extract`.
 Go in the code to storage/mongo_db.py and set:
 
```
mongo_client = MongoClient("mongodb://localhost:27017/")
mongo_db = mongo_client["gpreda"] # set your own database, on your local MongoDB env
mongo_collection = mongo_db["extract"]
```

## Initialize the binary storage

In storage/binary_storage.py set the path for your local storage:

Example:

`root_folder = "C:\\D\\workspace\\endava_projects\\DSCapacityDevelopment\\data"`

In the `root_folder` you will need to have 2 folders:

* input - here you will add the files to be processed
* documents - here will be saved the files ingested and results of pre-processing and 
processing will be stored.

# Run application

To run the application, you can either start luigi:

`python -m luigi --module run Extract  --local-scheduler`

or run the function  (from `test_ingest_process_extract_and_plot_output.ipynb`:
`run_workflow("Invoice_28092018-171040.pdf")`

# Visualize results

You can visualize the results in two ways:

* Execute the command:
`run_workflow("Invoice_28092018-171040.pdf")` from the Notebook `test_ingest_process_extract_and_plot_output.ipynb`; 
this will display the pages

* Inspect the document associated with the ingested file in MongoDB (using Compass) to 
see the extracted attributes specified in MongoDB.

