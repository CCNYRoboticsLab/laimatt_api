# call_ODM_API
A python script that facilitates API calls to WebODM's Texture Map and Point Cloud features.
Author: Matthew Lai

## Commands
### Loading a folder of images
The console command to be used to load a folder of images, expressed as a path, to be processed by WebODM is as follows:
```curl -X POST -H "Content-Type: application/json" -d '{"input": "{path}/*.JPG"}' http://localhost:9000/task```
where ```{path}``` is the absolute path to the folder containing images. 

The output of this function is a JSON file titled ```data.json``` placed in the directory of the script by default.

```data.json``` contains:
- project_id: the id of the generated project.
- task_id: the id of the generated task.
- authentication: the authentication key to be used for all future API calls.

task_id will be ```-1``` if the path given was invalid.

### Retrieving a Point Cloud or a Texture Map
This command is intended to only be used after its respective task has been generated. 
Usage of this command also assumes that the respective task's ```data.json``` file is in the same working directory.

The console command to be used retrieve a Point Cloud is:
```curl -X GET -H "Content-Type: application/json" -d '{"input": "data.json", "request": "pointcloud"}' http://localhost:9000/getfile```


The console command to be used retrieve a Texture Map is:
```curl -X GET -H "Content-Type: application/json" -d '{"input": "data.json", "request": "texturemap"}' http://localhost:9000/getfile```

The output of this function is a JSON file titled ```filepath.json``` that, if successful, contains the absolute path to the file requested.

```filepath.json``` contains:
- error_code: the error code upon running the command, including success.
- webodm_status: the WebODM task status if it exists, a reference for which can be found [here](https://docs.webodm.org/#status-codes). Empty if the task does not exist. 
- path: the absolute path to the requested file or folder, empty on failure. 

Error Code Index:
Status | Code | Most Probable Cause
------- | ---- | -------
SUCCESS | 0 | Command executed successfully.
NO_PROJECT | 1 | No Project ID, likely because the image loading command failed. 
NO_TASK | 2 | The task does not exist, potentially because it was cancelled externally.
NO_FILE | 3 | The requested file was not found, likely either because the file was never generated, or because the task itself has not yet completed. Refer to the [webodm_status]((https://docs.webodm.org/#status-codes)) value accompanying this error code.
NO_JSON | 4 | An invalid ```data.json``` was provided.

To test this code, run ```call_ODM_API.py``` to open up the port, and run the commands in a separate terminal.