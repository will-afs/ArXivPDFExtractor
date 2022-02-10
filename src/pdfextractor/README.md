🔽 Custom installation and usage in production
-----------------------------------------------

!! (no guarantee on the functionnality yet) !!
 
In a terminal, run the following command :

    git clone https://github.com/will-afs/ArXivPDFExtractor.git
    
Then build the Docker image :

    sudo docker build --tag pdfextractor .

You can now run the Docker image as a container :

    docker run pdfextractor
    
