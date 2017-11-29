# Quick-Dev-Hacks

#### These are some quick hacks about some problems that I have faced while developing software and that did not have any solution on Google.

## Working with folder links on Edge

Edge by default doesn't open up folder links. The quick hack is to fix it is as follows-

- Create a Shortcut for that Folder.
- Create a link to that Shortcut instead.

### Note:

- In my case the webpage had to was used as autorun, so I had to make relative links (which BTW is not that simple in Windows). This can be done by adding "%windir%\explorer.exe" (without quotes) in the target of the shortcut. For eg, %windir%\explorer.exe "..\Documentation\"
