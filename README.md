# <img src="https://github.com/will-afs/AdvancedAcademicProject/blob/main/doc/ArXivParser.png" width="30"> <img src="https://github.com/will-afs/AdvancedAcademicProject/blob/main/doc/PDFExtractor.png" width="30"> ArXivPDFExtractor
Process scientific articles (PDFs) available on ArXiv.org

<img src="https://github.com/will-afs/AdvancedAcademicProject/blob/main/doc/ArXivPDFExtractor%20architecture.JPG" width="700">

This is a sub-project of the [AdvancedAcademicProject](https://github.com/will-afs/AdvancedAcademicProject/]

⚙️ Configuration
-----------------
The project configuration holds in the [config.toml file](https://github.com/will-afs/ArXivPDFExtractor/blob/main/settings/config.toml).

🔽 Installation and usage in production
----------------------------------------
*Note : It is possible to run all of the services mentionned below on different machines*

To use this solution as a whole, 3 services have to be launched first :
- [<img src="https://github.com/will-afs/AdvancedAcademicProject/blob/main/doc/CooldownManager.png" width="30"> Cooldown Manager](https://github.com/will-afs/CooldownManager), to avoid overloading the ArXiv Open API
- [<img src="https://github.com/will-afs/PDFExtractor/blob/main/doc/img/pickaxe.png" width="30">  PDF Extractor](https://github.com/will-afs/PDFExtractor), to extract data from PDFs remotely, in AWS Lambda functions
- [<img src="" width="30">  Redis Task Queue](), to store the result of ArXiv PDFs extraction (JSON) as a task, in a task queue

All of which have to be reachable and available : their URL have to be specified into the [config.toml file](https://github.com/will-afs/ArXivPDFExtractor/blob/main/settings/config.toml)

**Launching CooldownManager**

    sudo docker run --name cooldownmanager -d -p 80:80 williamafonso/cooldownmanager

For more informations, including how to make a custom installation, please refer directly to [the project README.md](https://github.com/will-afs/CooldownManager)

**Launching Redis**

Please refer to the procedure explained in [the meta project README.md](https://github.com/will-afs/AdvancedAcademicProject/)

**Launching PDFExtractor**

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
