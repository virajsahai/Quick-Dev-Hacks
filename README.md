# Quick-Dev-Hacks

#### These are some quick hacks about some problems that I have faced while developing software and that did not have any solution on Google search, stackoverflow etc.

## 1. Working with folder links on Edge

Edge by default doesn't open up folder links. The quick hack is to fix it is as follows-

- Create a Shortcut for that Folder.
- Create a link to that Shortcut instead.

### Note:

- In my case the webpage had to be used as autorun, so I had to make relative links (which BTW is not that simple, as a linux softlink, in Windows). This can be done by adding "%windir%\explorer.exe" (without quotes) in the target of the shortcut. For eg, %windir%\explorer.exe "..\Documentation\"
- Also, since I had to deal with IE support too (and it doesn't have JS support enabled by default), I had to creat a separate webpage for Edge.

##### For reference, see the EdgeFix directory in the repo.

## 2. Creating a scrollable frame in Tkinter

Tkinter has no support for adding scrollbar to frames. The hack is to-

- Create a Canvas and add scrollbars to it.
- Create frame in that Canvas and add your widgets etc.

##### For reference, see the TkinterFix directory in the repo.
