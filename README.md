# AutoCaz (FaceOver)

AutoCaz is a webserver that captures frames from a OBS source and runs facial recogniton on them, and outputs a transparent webpage on which the faces can be overlayed with other images.

## Installer

Pre-compiled version is even more experimental than the application, so it may or may not work.
It was built with ```python -m nuitka --follow-imports --standalone autocaz.py``` with all the requirements and MS VS C++ installed.
It will probably throw some antivirus / trust messages as it's not signed with authenticode or anything.

The version for Windows 64bit is here.... 



but it might be better to with the source and set up a python environment ....

## Build yourself

Windows Note: Windows is a ball ache, and will need Visual Studio C++ developer to compile the face recognizer... 
Yeah, it's 5GB, but can be uninstalled once AutoCaz is working.

Download Visual Studio Free: 
https://visualstudio.microsoft.com/thank-you-downloading-visual-studio/?sku=Community&channel=Release&version=VS2022&source=VSLandingPage&passive=false&cid=2030

Select only "Desktop development with C++" and install.

(close and re-open VS code and terminals for PATH setting to take effect terminals)

Note: Untested, but this is possibly avoidable if you have Windows Linux Subsystem 2 (WSL2) setup and just follow the steps below.

**Steps**

1. Download the AutoCaz source and extract into a folder of your choice.

2. Install Python:

Download and install the latest version of Python from the official website: https://www.python.org/downloads/

Set up a virtual environment (optional, but recommended):

To create an isolated environment for your project, open a terminal or command prompt and run the following commands:

```bash
cd /home/hip/autocaz # (or cd c:\some\folder\you\unzipped\to)
python -m venv autocaz_env
```

Then everytime to start the virtual environment: 

Linux
```bash
$ source autocaz_env/bin/activate
```

Windows
```bash
C:\> autocaz_env\Scripts\activate
```

3. Install necessary libraries and packages:

```bash
pip install wheel

# Windows will need this, not required for linux
pip install cmake

pip install -r requirements.txt
```

It will take some time for this to complete while the facial recogniton library is compiled.
```
  Building wheels for collected packages: dlib
  Building wheel for dlib (setup.py) ... \-|/
```


4. You will need OBS (Open Broadcaster Software - https://obsproject.com/) installed, running and configured to accept WebSocket connections.

5. Edit the `config.ini` file:

```ini

[OBS]
# configuration for OBS WebSocket connection
obs_ip = localhost
obs_port = 4455
obs_password = testing123
# don't touch
obs_last_source = Cooker28
obs_res_index = 4

[WEB]
# the overlay page is served from here
webserver_port = 5000
webserver_name = 127.0.0.1

# don't touch any other settings :)
# they record the UI settings
```

## Running

1. Start OBS.

2. Start AutoCaz from a terminal:

```bash
cd c:\some\folder\you\unzipped\to
autocaz_env\Scripts\activate
python autocaz.py
```
3. Create a Browser Source in OBS called AutoCaz or similar, set it to the same dimensions as the stream output.
   Source should be http://localhost:5000/ or whatever port you configured.


![image](https://imgur.com/uxOhIlW.png)


## Using 

This is the tricky part LUL.

1. Make sure OBS is running before starting AutoCaz

2. Select a OBS source from the drop down box, eg.  Guru Project Matilda.   (Note: known issue, sometimes crashes when changing between sources, so pick the right one). Leave the resolution lower to increase the facial detection speed, increase to improve detections.

3. Check the "Run Face Recognition" box to start. Face recognition is a slow process, the whole GUI slows down too.  Expect 2-3 FPS 

4. You should see faces with black boxes around them for unknown people.  Click the black box of the person you want to recognize.  It will be added to the Catalog as "Unknown".

5. You can then Name the person, and click Save Person.

6. You can select an image (transparent png and animated gif work well) to place over that persons face, using the Overlay Image button. Press Save.  Then use the offset and scale controls to position it in realtime, then save when happy.

7. Adjust the Threshold setting to lower for a stricter face match to the catalog, higher is less strict.  There is usually a sweet spot to be found for different sources.

8. If you are not getting any detections, increase the Resolution (slows down) or lower the recogntion threshold (higher value 0 is very strong, 1 is very loose)

**Tips:** 

* Stop face detection while editing the catalog and getting setup, when setup and running properly, you should not need to use the UI much except tweaking the threshold. 

* Don't store too many or faces which are not needed, it will impact comparison performance. 

* It's only designed for front on faces mostly, and not a fan of glasses, hats and beanies some times. Your millage may vary.  You may need to manually Caz in desperate times.

* If it crashes... check task manager / top for any hung python processess and kill them, the capture might still be going.

