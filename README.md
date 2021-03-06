![Tests](https://github.com/akinwilson/nate-web-service/actions/workflows/Tests.yml/badge.svg)
# **Nate web service application**
This repo contains the associated code to the nate backend challenge. 

# **Overview**
The web service has been implemented using [fastAPI](https://fastapi.tiangolo.com/); a python library for developing APIs. The testing of the API is being performed with [pytest](https://docs.pytest.org/en/7.1.x/). [Github action ](https://github.com/features/actions) is being utilised along with [tox](https://tox.wiki/en/latest/) for automating the testing process across multiple python versions. 

Please use either of the following python releases: **3.8**, **3.9** or **3.10**, as these are the releases the tests have run against and passed

## **Running locally**
It is recommended that you perform the following python-related commands from a [virtual envrionment](https://docs.python.org/3/tutorial/venv.html). 


### 1) **Installing development requirments.txt and extractor package service locally via pip**

Run the following commands from your terminal:

  *(**Note**: the assumption is that you are running a linux-based operating system. If you are not, the commands may syntactically differ for other operating systems)*

`pip install -r requirements_dev.txt`

*This will install the development requirements needed for testing*

`pip install -e ./`

where `./` indicates the root directory. 

This will install the `extractor` pip package to your local environment. The flag `-e` is for *editable* mode. This is for development purposes, and allows you to edit the logic and have updates automatically registered by the python package locally.

### 2) **Running tests and docker container building script**
Execute the script:

`./build_container.sh`

**NOTE**:
you will need the docker client to be able to run this script.

This script will do the two following things:
1. Run the tests. This requires the `extractor` package to have been installed, hence why the above step needs to be done. The package, defined in the `/app` directory, is called `extractor` and will be installed via the command `pip install -e ./`
    
2. Build the docker image with the name `nate-web-server:latest`. The dockerfile copies the html test coverage report into the dockerfile, this report is a product of running the tests. Hence to avoid any mistakes in the final built image, I would suggest just running the script `./build_container.sh`.

### 3) **Run container and visit the swagger UI endpoint**
Finally, run this command from your terminal:

`docker run --env-file ./.env --network host nate-web-server:latest`

This will run the container attached your host machine's network. 

The `.env` file contains configuration details of [gunicorn](https://gunicorn.org/);  Python Web Server Gateway Interface HTTP server.

 In essence, this a process controller for [uvicorn](https://www.uvicorn.org/); an asynchronous server gateway interface web server implementation for Python and the server that is actually running the fastAPI application. More on this later, as the the number of workers (as determined inside `.env` file) of the gunicorn server will determine the performance of the application under load. 

After spinning up the docker container via the above script, in your browsers head to the url:

`http://0.0.0.0:8080/docs`

Here you can test out the API through an easy-to-use UI.

There is an example of the API post request body and so on. 

For the coverage report of the run tests, head to:

`http://0.0.0.0:8080/report`

Please review some of the comments I have left inside the code. These are basically regarding the security concerns of reporting the tests like this( visible via an endpoint; I would never normally do this, and have just done it for the sake of easy-of-use of this repo)


# **Optimization of application**
## **Code-specific considerations**

### **API design**

Currently, the API only serves one vocab construction at a time. That is, a post request is made, the extraction is performed, and the response is sent back on a **per url basis**. 

It would be beneficial to allow a user to supply a **list** of URLs in the post requests, and have the server complete the vocabulary extraction on the entire list, sending back a word occorance per supplied URL, in one response. This would avoid the additional incurred processing time associated with transfering the data, on a per URL basis, over the network.

This can be achieved using [background tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/) and implementing the associated method in the code. The workflow would be as follows:

**client**: **post** request: bulk extraction &#8594; **server** 

*server schedules the job, saves input data to disk, and associates uuid to it*


**client** &#8592; accepted response **server**

*reponse contains uuid of job. Client can use uuid to get partial job completion on the fly* 

...*server processes job, saving to disk*...


**client**: bulk extraction response  &#8592;  **server**


 ...*on job completetion, server loads the processed extraction from disk* ...

*Response contains constructed vocab per url*

### **Infrastructure-specific considerations**

The sorting of the constructed vocabulary is a CPU-bound task. Hence, you want to utilise as many virtual-cores of your node as possible, without affecting the overall all processing time, to parallelise this sorting operation. 

The number of virtual cores is determined in the `.env` file, passed to the [gunicorn](https://gunicorn.org/) server initialisation script `start_server.sh` via environment variables of the `dockerfile`. 

Feel free to edit the `.env` file to your local machine's cpu count, and rebuilding the container. 


The trival solution is to simply use

`NUM_WORKERS = 2 x no_of_cores_of_host_cpu + 1`

as the number of workers for the gunicorn server. But the complexity arises when, for example, 8 cpu-bound docker containers are hosted, and continuously underload, on one node.
<br>
<br>
<br>
<br>
*Interlude*

*(**Note**: 8 is the maximum amount of containers hostable per docker host and this is also why a *pod* in Kubernetes can run a max of 8 containers.)*
<br>
<br>
<br>
<br>
<br>
<br>
 Furthermore, each process managed by gunicorn server can have multiple threads. So this is an optimization problem, both in terms of cost of provisioned infrastructure and therewith number of accessible and configurable workers and threads. 

In a production setting, you should benchmark various configurations (combinations of cores and number of threads) of the gunicorn and uvicorn server to find which configuration gives you the best performance, for the expected load and given underlying hardware infrastructure. 
