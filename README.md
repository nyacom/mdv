Mdview
=====================================================================
A yet another Markdown viewer.

Copyright
---------------------------------------------------------------------
Kazuei HIRONAKA <kzh@nyacom.net> 2015 &copy;

![nyacomlogo@width=100px](./nyacom.png)

Description
---------------------------------------------------------------------
A simple Markdown viewer written by Python.
see README_rendering_sample.pdf a rendering sample.

Usage
---------------------------------------------------------------------
#### On the mostly common environment..

    % ./mdview.py <something.md>

#### On the Debian/Ubuntu environment..

    % ./debian_run.sh <something.md>

Known issue
---------------------------------------------------------------------
+ Only well tested on Debian8

+ GUI implemented by wxPython + webview
 - The webview rendering engine is depending on the running environment.
 - Mostly Webkit on Linux (GTK) Trident on Windows.

+ apt provided libwxgtk-webview3.0 will not set vaild path on the Debian environment. (a bug?)
 - Use debian_run.sh is a temporary solution for this.
 - set BASE_PATH with your mdview.py installed location.

Key bindings
---------------------------------------------------------------------
|:---:|----------------------------|
| Key | Description                |
| r   | reload and regenerate HTML |
| j,k | vi like scroll down        |
| +,- | Zoom in/out                |
| p   | Show print window          |
| C-d | Page down                  |
| C-u | Page up                    |
| q   | Quit                       |

Supported syntax
=====================================================================

Text attributes
-----------------------------------------------------------

Example:

    This part will break line  
    this part will not break line
    this part will not break line
    
    This part will __bold__  
    This part will not__bold__
    
    This part will _italic_  
    This part will not_italic_
    
    This part will ~~strike~~
    
    This part is `code`

Rendering:

This part will break line  
this part will not break line
this part will not break line

This part will __bold__  
This part will not__bold__

This part will _italic_  
This part will not_italic_

This part will ~~strike~~

This part is `code`

Preview
-----------------------------------------------------------
Example:
    
    ```
    This is code block
     #include <stdio.h>
     int main() {
     	printf("Hello world\n");
     }
    ```
    
        This is also code block
        Hello can you see this?
    
     This is not code block
    
Rendering:
```
This is code block
 #include <stdio.h>
 int main() {
 	printf("Hello world\n");
 }
```

    This is also code block
    Hello can you see this?

 This is not code block


Quote
-----------------------------------------------------------
Example:

     > level1
     >> level2 
     >>> level3
     > > > level3
     > > > level3
     
     > level1
     >> level2
     
     ### List
     * hoge
     * geho
     
     
     * top
      * 2nd
      * 2nd
      * 2nd
     	* 3rd
     	* 3rd
     	+ this is _list_
     		1. numlist1
     		1. numlist2
     
     
      1. Number list is also available
      1. See like this


Rendering:

> level1
>> level2 
>>> level3
> > > level3
> > > level3

> level1
>> level2

List
-----------------------------------------------------------
Example:

     * hoge
     * geho
     
     
     * top
      * 2nd
      * 2nd
      * 2nd
     	* 3rd
     	* 3rd
     	+ this is _list_
     		1. numlist1
     		1. numlist2
     
     
      1. Number list is also available
      1. See like this

Rendering:

* hoge
* geho


* top
 * 2nd
 * 2nd
 * 2nd
	* 3rd
	* 3rd
	+ this is _list_
		1. numlist1
		1. numlist2


 1. Number list is also available
 1. See like this

Table
-----------------------------------------------------------

#### Valid table syntax

Example:

     | Header | Header |
     | Data1  | Data 2 |
     
     
     |:-------|:------:|
     | Data1  | Data 2 |
     
     
     | Header | Header |
     |:-------|:------:|
     | Data1  | Data 2 |
     | Data3  | Data 4 |

Rendering:

| Header | Header |
| Data1  | Data 2 |


|:-------|:------:|
| Data1  | Data 2 |


| Header | Header |
|:-------|:------:|
| Data1  | Data 2 |
| Data3  | Data 4 |

#### Invalid table syntax

| Data1  | Data 2 |

|:-------|:------:|
|:-------|:------:|


Images
-----------------------------------------------------------

#### left aligned image

    ![image](nyacom.png)

![image](nyacom.png)

#### centered image

    ![ image ](nyacom.png)

![ image ](nyacom.png)

#### right aligned image

    ![ image](nyacom.png)

![ image](nyacom.png)


#### Optional attribute

    ![ image@width=32px ](nyacom.png)

![ image@width=32px ](nyacom.png)


