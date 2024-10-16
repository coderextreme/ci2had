# ci2had
CoordinateInterpolator to HAnimDisplacer (ci2had)

# Quick Windows Powershell instructions:

Clone the repository, go to project folder, and launch FreeWRL 6.7.
You may wish to load the Git repository into your favorite IDE instead.

```powershell
git clone https://github.com/coderextreme/ci2had
cd ci2had
```

Launch FreeWRL with the file:  Replace \ with / if on MacOS or Linux.

```powershell
 & 'C:\Program Files (x86)\freeWRL\freeWRL.6.7\freeWRL.exe' -J DUK resources\Menu.x3d
```

Or open resources/Menu.x3d in FreeWRL Launcher.

# Future instructions

Download Node.js (for the future).  We'll assume that you've downloaded Git and cloned the https://github.com/coderextreme/ci2had repository.


Run:
```
cd ci2had
npm install
npm run start
```

This will start a web server and give you a link to visit.  CTRL-Click (left mouse button) to visit the link.  This works in Windows.  Maybe copy and paste.  Note that only FreeWRL currently implements HAnimDisplacers (had in ci2had). I have not tried Octaga.  Maybe some others will work.

Type CTRL-C in the terminal window to exit.


# Current instructions.

To Try Freewrl, download and find the path to FreeWRL and replace $PATH_TO_FREEWRL with the path you found, below, like
```
$PATH_TO_FREEWRL/freeWRL.exe -J DUK resources/Menu.x3d
```
becomes:
```
/c/Program\ Files\ \(x86\)/freeWRL/freeWRL.6.7/freeWRL.exe -J DUK resources/Menu.x3d
```
in Git bash.  You should be in your ci2had folder when you try this. (see cd command above, or start the command in your terminal in your IDE, like VS Code.

It may be easier to put $PATH_TO_FREEWRL in your PATH Environmental variables.
You may wish to set an environmental variable for FreeWRL.
Note that you will have to use \ as a folder separator for your PATH environmental variable addition in Windows.
Restat yoru terminal and type:
```
freeWRL.exe -J DUK resources/Menu.x3d
```
The correct command in PowerShell once you've changed folders to the ci2had folder is:
```
 & 'C:\Program Files (x86)\freeWRL\freeWRL.6.7\freeWRL.exe' -J DUK resources\Menu.x3d
 ```

Or open ci2had/resources/Menu.x3d in your FreeWRL launch window.

For an example that's really obvious, select:

FACS\_AU27(Jin)_Mouth_Stretch_Morpher_Output.x3d in the FreeWRL window that pops up once you've browsed to the file and selected Launch FreeWRL

