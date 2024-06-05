import sys
import time
import requests
import glob

url = "http://localhost:8000/api/token-auth/"
data = {
    "username": "laimatt",
    "password": "WA30Bj4Tam20"
}
response = requests.post(url, data=data)
print(response.json())
headers = {'Authorization': 'JWT {}'.format(response.json()['token'])}

url = "http://localhost:8000/api/projects/"
data  = {
    "name": "test"
}
response = requests.post(url, headers=headers, data=data)
print(response.json())
project_id = response.json()['id']


# images = glob.glob('/home/roboticslab/Downloads/OneDrive_2024-02-03/NYCSpan8-9/raw/images/*.JPG')
images = glob.glob('/home/roboticslab/Developer/laimatt_API/images/*.JPG')
files = []
for image_path in images:
    files.append(('images', (image_path, open(image_path, 'rb'), 'image/png')))

# print(files)

url = "http://localhost:8000/api/projects/" + str(project_id) + "/tasks/"
response = requests.post(url, headers = headers, files=files)
task_id = response.json()['id']
print(task_id)

while True:
    res = requests.get('http://localhost:8000/api/projects/{}/tasks/{}/'.format(project_id, task_id), 
                headers=headers).json()
    
    print(res['status'])
    time.sleep(3)

    if res['status'] == 40:
        print("Task has completed!")
        break
    elif res['status'] == 50:
        print("Task failed: {}".format(res))
        sys.exit(1)
    else:
        print("Processing, hold on...")
        time.sleep(3)

res = requests.get("http://localhost:8000/api/projects/{}/tasks/{}/download/orthophoto.tif".format(project_id, task_id), 
                        headers=headers,
                        stream=True)
with open("orthophoto.tif", 'wb') as f:
    for chunk in res.iter_content(chunk_size=1024): 
        if chunk:
            f.write(chunk)
print("Saved ./orthophoto.tif")