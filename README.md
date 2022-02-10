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

🧪 Running tests
-----------------
The tests are placed in the tests folder. They can be ran from the root folder with the pytest command, as follows :

    python -m pytest tests

🔽 Installation and usage in production
----------------------------------------
To use this solution as a whole, 3 services have to be launched first :
- A **Message Broker**, to exchange informations between the ArXivParser CRON bot and the PDFExtractor workers 👉 For example : Redis    
- A **Backend Database** , to store the informations generated by this application 👉 For example : PostgreSQL
- A **Cooldown Manager**, to avoid overloading the ArXiv Open API

All of which have to be reachable and available : their URL have to be specified into the [config.toml file](https://github.com/will-afs/ArXivPDFExtractor/blob/main/settings/config.toml)

**Launching Redis**

    sudo docker run --name redis-arxivpdfextractor -d redis
    
By default, this command should make the service accessible at the address : redis://localhost:6379/0

**Installing PostgreSQL**

Refer to the PostgreSQL
[Installing PostgreSQL](https://www.postgresql.org/docs/12/installation.html) for example

**Installing CooldownManager**

    sudo docker run --name cooldownmanager -d williamafonso/cooldownmanager

For more informations, including to make a custom installation, please refer directly to [the project README.md](https://github.com/will-afs/CooldownManager)

**Next steps**
The next steps are then detailed for each one of the two programs.
See their respective README.md files to have more information on each :
- [ArXivParser README.md](https://github.com/will-afs/ArXivPDFExtractor/blob/main/src/arxivparser/README.md)
- [PDFExtractor README.md](https://github.com/will-afs/ArXivPDFExtractor/blob/main/src/pdfextractor/README.md)

It is possible to run all of these services on different machines, at the condition they can communicate over the TCP/IP network.
