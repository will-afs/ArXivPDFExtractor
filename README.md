# <img src="https://github.com/will-afs/AdvancedAcademicProject/blob/main/doc/ArXivParser.png" width="30"> <img src="https://github.com/will-afs/AdvancedAcademicProject/blob/main/doc/PDFExtractor.png" width="30"> ArXivPDFExtractor
Populate a database with data extracted from scientific articles (PDFs) available on ArXiv.org

This is a sub-project of the [AdvancedAcademicProject](https://github.com/will-afs/AdvancedAcademicProject/)

It contains two programs :

- [<img src="https://github.com/will-afs/AdvancedAcademicProject/blob/main/doc/ArXivParser.png" width="30"> ArXivParser](https://github.com/will-afs/ArXivPDFExtractor/src/ArXivParser) (involved in step 1)
- [<img src="https://github.com/will-afs/AdvancedAcademicProject/blob/main/doc/PDFExtractor.png" width="30"> PDFExtractor](https://github.com/will-afs/ArXivPDFExtractor/src/PDFExtractor) (involved in step 2)

🤖 **Step 1**

<img src="https://github.com/will-afs/AdvancedAcademicProject/blob/main/doc/Step%201.JPG" width="700">

⛏️ **Step 2**

<img src="https://github.com/will-afs/AdvancedAcademicProject/blob/main/doc/Step%202.JPG" width="700">

⚙️ Configuration
-----------------
The project configuration holds in the [config.toml file](https://github.com/will-afs/ArXivPDFExtractor/blob/main/settings/config.toml).

🔽 Installation and usage in production
----------------------------------------
*Note : It is possible to run all of the services mentionned below on different machines*

To use this solution as a whole, 3 services have to be launched first :
- A **Message Broker**, to exchange informations between the ArXivParser CRON bot and the PDFExtractor workers 👉 For example : Redis    
- A **Cooldown Manager**, to avoid overloading the ArXiv Open API
- A **PDF Extractor**, to extract data from PDFs remotely, in AWS Lambda functions

All of which have to be reachable and available : their URL have to be specified into the [config.toml file](https://github.com/will-afs/ArXivPDFExtractor/blob/main/settings/config.toml)

**Launching CooldownManager**

    sudo docker run --name cooldownmanager -d -p 80:80 williamafonso/cooldownmanager

For more informations, including how to make a custom installation, please refer directly to [the project README.md](https://github.com/will-afs/CooldownManager)

**Launching Redis**

Please refer to the procedure explained in [the meta project README.md](https://github.com/will-afs/AdvancedAcademicProject/)

** Launching PDFExtractor**

Please refer to the procedure explained in [the project README.md](https://github.com/will-afs/PDFExtractor/)

**Launching the project applications**
Clone the project on your machine:

    git clone https://github.com/will-afs/ArXivPDFExtractor/

Go into the cloned repository (stay at the root), and add the repository path to your Python environment variables:

    export PYTHONPATH=$(pwd)

Launch ArXivParser

    python3 src/arxivparser/core/arxiv_parser.py
   
(in a future version)

    sudo docker run --name williamafonso/arxivparser

For more informations, including custom installation and launch, please refer directly to their respective README.md files :
- [ArXivParser README.md](https://github.com/will-afs/ArXivPDFExtractor/blob/main/src/arxivparser/README.md)
- [PDFExtractor README.md](https://github.com/will-afs/ArXivPDFExtractor/blob/main/src/pdfextractor/README.md)

🧪 Running tests
-----------------
The tests are placed in the tests folder. They can be ran from the root folder with the pytest command, as follows :

    python -m pytest tests
