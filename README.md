# <img src="https://github.com/will-afs/AdvancedAcademicProject/blob/main/doc/Icons/ArXivParser.png" width="30"> ArXivParser
Process scientific articles (PDFs) available on ArXiv.org

<img src="https://github.com/will-afs/AdvancedAcademicProject/blob/main/doc/Deployment%20architecture/ArXivPDFExtractor/ArXivPDFExtractor%20architecture.png" width="700">

This is a sub-project of the [AdvancedAcademicProject](https://github.com/will-afs/AdvancedAcademicProject/)

⚙️ Configuration
-----------------

The project configuration holds in the [config.toml file](https://github.com/will-afs/ArXivPDFExtractor/blob/main/settings/config.toml)

🔽 Installation and usage in production
----------------------------------------
*Note : It is possible to run all of the services mentionned below on different machines*

To use this solution as a whole, some services have to be launched first :
- [<img src="https://github.com/will-afs/AdvancedAcademicProject/blob/main/doc/Icons/PDFExtractor.png" width="30">  PDF Extractor](https://github.com/will-afs/PDFExtractor), to extract data from PDFs remotely, in AWS Lambda functions
- [<img src="https://github.com/will-afs/AdvancedAcademicProject/blob/main/doc/Icons/Redis.png" width="30">  Redis](), to store the result of ArXiv PDFs extraction (JSON) as a task, in a task queue

All of which have to be reachable and available : the services must be running and accessible from ArXivParser. For that, their URL have to be specified into the [config.toml file](https://github.com/will-afs/ArXivPDFExtractor/blob/main/settings/config.toml)

*Note: for now, the redis task queue does not need to be instanciated. Instead, the resulting macrostructure.json file is stored in the results folder.*
    
**Launching ArXivParser**

Follow the "Developing and running tests" section above, and then, run:

    python src.core.arxiv_parser.py
    
🧪 Developing and running tests
--------------------------------
Clone the project on your machine:

    git clone https://github.com/will-afs/ArXivPDFExtractor/

Go into the cloned repository (stay at the root) - it will be the working directory:

    cd ArXivPDFExtractor

Add the working directory to the Python PATH environment variable:

    export PYTHONPATH=$(pwd)
    
Create a virtual environment:

    python3 -m venv .venv

Activate the virtual environment:
    
    source .venv/bin/activate
    
Install the dependencies:
    
    pip install -r requirements.txt
    
The unit tests are placed in the tests folder. They can be ran from the root folder with the pytest command, as follows :

    python -m pytest tests 

☁️ Deploying on EC2
--------------------
Create an AWS EC2 instance (ideally Ubuntu Server 20.04 LTS) - keep your KeyPair.pem file safe !

Configure a VPC and a Security Group so that the machine is reachable via SSH and HTTP
    
By default, permissions on the keypair.pem file are too open and must be restricted:

    chmod 600 <path_to_your_key_pair>

You should now be able to connect to your EC2 instance:

    sudo ssh -i <path_to_your_key_pair> ubuntu@<ec2_instance_public_ipv4>

Once connected, deploy and run the service as a container, or as specified above
