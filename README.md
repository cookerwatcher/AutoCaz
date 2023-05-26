# AutoCaz (FaceOver)


AutoCaz is a webserver that captures frames from a OBS source and runs facial recogniton on them, and outputs a transparent webpage on which the faces can be overlayed with other images.

## Installer

Pre-compiled (PyInstaller) version for Windows 64bit is here....

or....

## Build yourself

Windows Note: Windows is a real ballache, and will need Visual Studio C++ developer bullshit to compile the face recognizer... 
Yeah, it's 10GB, but can be uninstalled once AutoCaz is working.

Download Visual Studio Free: 
https://visualstudio.microsoft.com/thank-you-downloading-visual-studio/?sku=Community&channel=Release&version=VS2022&source=VSLandingPage&passive=false&cid=2030

Select only "Desktop development with C++" and install.


Alternatively you might be able to just use WSL and follow the linux instructions.

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

5. Edit the config.ini file:

```ini
# configuration for OBS WebSocket connection

[OBS]
OBS_IP = localhost
OBS_PORT = 4455
OBS_PASSWORD = testing123

# configuration for inbuilt webserver for FaceOver

[WEB]
WEBSERVER_PORT = 5000
```

## Running

1. Start OBS.

2. Start AutoCaz:

```bash
cd /home/hip/autocaz # (or cd c:\some\folder\you\unzipped\to)
python autocaz.py
```

![image](https://imgur.com/uxOhIlW.png)

3. Create a Browser Source in OBS called AutoCaz or similar, set it to the same dimensions as the stream output.
   Source should be http://localhost:5000/ or whatever port you configured.


## Using 

This is the tricky part LUL.

1. Make sure OBS is running before starting AutoCaz

2. Select a OBS source from the drop down box, eg.  Guru Project Matilda.   (Note: known issue, sometimes crashes when changing between sources, so pick the right one).

Leave the resolution lower to increase the facial detection speed, increase to improve detections.

3. Check the "Run Face Recognition" box to start.   Face recognition is a slow process, the whole GUI slows down too.  Expect 2-3 FPS 

4. You should see faces with black boxes around them for unknown people.  Click the black box of the person you want to recognize.

(Note: known issue, the UI is slow, hold the mouse button down longer than you think is necessary for a click).

It will be added to the Catalog as "Unknown"

5. You can then Name the person, and click Save.
You can select an image to place over that person, using the Overlay Image button. Press Save.
Then use the offset and scale controls to position it in realtime, then save when happy.

6. Adjust the Threshold setting to lower for a stricter face match to the catalog, higher is less strict.  There is usually a sweet spot.

7. If you are not getting any detections, increase the Resolution (slows down) or lower the threshold (higher value)

**Tips:** 

* The UI can be slow as balls.  Stop face detection while editing the catalog and getting setup, when setup and running properly, you should not need to use the UI much except tweaking the threshold. 

* It's only good for front on faces mostly, and not a fan of glasses.  You may need to manually Caz sometimes as usual.

* If it crashes... check task manager / top for any hung python processess and kill them, the capture might still be going and fill up your ram.
* It's pretty reliable except for changing sources, so try to pick the correct source the first time and avoid changing or quit first.

