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

**Launching ArXivParser**

    sudo docker run --name williamafonso/arxivparser
    
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

🐋 Containerizing the application 
----------------------------------
To build a Docker image:

    sudo docker build --tag arxivparser .

Or if you want to be able to push it later to your DockerHub:

    sudo docker build --tag <your_docker_username>/arxivparser .

Pushing the Docker image to your registry:

    sudo docker push <your_docker_user_name>/arxivparser

Running a Docker image:

    sudo docker run --name arxivparser
    

☁️ Deploying on EC2
--------------------
Create an AWS EC2 instance (ideally Ubuntu Server 20.04 LTS) - keep your KeyPair.pem file safe !

Configure a VPC and a Security Group so that the machine is reachable via SSH and HTTP
    
By default, permissions on the keypair.pem file are too open and must be restricted:

    chmod 600 <path_to_your_key_pair>

You should now be able to connect to your EC2 instance:

    sudo ssh -i <path_to_your_key_pair> ubuntu@<ec2_instance_public_ipv4>

Once connected, deploy and run the service as a container, as specified above
