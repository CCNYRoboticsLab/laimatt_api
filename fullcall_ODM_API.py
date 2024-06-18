from flask import Flask, request, jsonify
import requests
import glob
import json
import time

SUCCESS = 0
NO_IMAGES = -1
NO_PROJECT = 1
NO_TASK = 2
NO_FILE = 3
NO_JSON = 4

app = Flask(__name__)
def create_task(input_data):
    token = authenticate()
    headers = {'Authorization': 'JWT {}'.format(token)}
    
    images = glob.glob(input_data)
    print(images)
        
    files = []
    for image_path in images:
        files.append(('images', (image_path, open(image_path, 'rb'), 'image/png')))
    if len(files) < 2:
        json_data = {
            "task_id": "",
            "project_id": NO_IMAGES, 
            "authentication": token
        }
        with open("data.json", "w") as json_file:
            json.dump(json_data, json_file)
        print("INSERT INTO whole_data (status) VALUES (1)")
        # SQLid = cursor.execute("SELECT LAST_INSERT_ID()"
        return json_data

    projecturl = "http://localhost:8000/api/projects/"
    data  = {
        "name": "API_Call"
    }
    project_id = requests.post(projecturl, headers=headers, data=data).json()['id']

    taskurl = "http://localhost:8000/api/projects/" + str(project_id) + "/tasks/"
    task_id = requests.post(taskurl, headers = headers, files=files).json()['id']

    while True:
        res = requests.get('http://localhost:8000/api/projects/{}/tasks/{}/'.format(project_id, task_id), 
                    headers={'Authorization': 'JWT {}'.format(token)}).json()

        if res['status'] == 40:
            print("Task has completed!")
            print("INSERT INTO whole_data (status) VALUES (4)")
            # SQLid = cursor.execute("SELECT LAST_INSERT_ID()"  
            break
        elif res['status'] == 30:
            print("Task failed: {}".format(res))
            print("INSERT INTO whole_data (status) VALUES (2)")
            exit
        else:
            print("Processing, hold on...")
            print("INSERT INTO whole_data (status) VALUES (3)")
            time.sleep(30)

    json_data = {
        "task_id": task_id,
        "project_id": project_id, 
        "authentication": token
    }
    with open("data.json", "w") as json_file:
        json.dump(json_data, json_file)

    
    return json_data

def authenticate():
    url = "http://localhost:8000/api/token-auth/"
    data = {
        "username": "authentication",
        "password": "authkeyword"
    }
    response = requests.post(url, data=data)
    return response.json()['token']

def filePathJSON(status, task, path):
    data = {
        "error_code": status,
        "webodm_status": task, 
        "path": path
    }
    
    with open("filepath.json", "w") as json_file:
        json.dump(data, json_file)
        
    return data
    
def getFilePath(json_file, request_type):  
    try:  
        with open(json_file, 'r') as file:
            json_data = json.load(file)
    except:
        return filePathJSON(NO_JSON, "", "")
    if json_data['project_id'] is NO_IMAGES:
        return filePathJSON(NO_PROJECT, "", "")
        
        
    headers = {'Authorization': 'JWT {}'.format(json_data['authentication'])}
    project_id = json_data['project_id']
    task_id = json_data['task_id']

    task = requests.get('http://localhost:8000/api/projects/{}/tasks/{}'.format(project_id, task_id), 
            headers=headers).json()
    print(task)
    
    try:
        available_assets = task['available_assets']
    except:
        return filePathJSON(NO_TASK, "", "")
        
    available_assets = task['available_assets']
    
    if request_type == "texturemap":
        if "textured_model.zip" in available_assets:
            path = '/var/lib/docker/volumes/webodm_appmedia/_data/project/{}/task/{}/assets/odm_texturing'.format(project_id, task_id)
            return filePathJSON(SUCCESS, task['status'], path)
        else:
            return filePathJSON(NO_FILE, task['status'], "")
    else:
        if "georeferenced_model.laz" in available_assets:
            path = '/var/lib/docker/volumes/webodm_appmedia/_data/project/{}/task/{}/assets/odm_georeferencing/odm_georeferenced_model.laz'.format(project_id, task_id)
            return filePathJSON(SUCCESS, task['status'], path)
        else:
            return filePathJSON(NO_FILE, task['status'], "")  

# API endpoint
@app.route('/task', methods=['POST'])
def task_api():
    data = request.get_json()
    input_data = data['input']
    processed_data = create_task(input_data)

    return processed_data

@app.route('/getfile', methods=['GET'])
def getFile_api():
    data = request.get_json()
    input_data = data['input']
    request_type = data['request']
    print(request_type)
    output = getFilePath(input_data, request_type)
    return output if output else "Not available"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=2000, debug=True)