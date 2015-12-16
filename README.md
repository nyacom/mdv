Mdview
=====================================================================
MeowkDown viewer  
A yet another Markdown viewer for cats.

Copyright
---------------------------------------------------------------------
![nyacomlogo@width=100px](./nyacom.png)

Kazuei HIRONAKA <kzh@nyacom.net> 2015 &copy;

Usage
---------------------------------------------------------------------
#### On the mostly common environment..

    % ./mdview.py <something good.md>

#### On the Debian/Ubuntu environment..

    % ./debian_run.sh <something good.md>

Shortcut
---------------------------------------------------------------------
|:---:|----------------------------|
| Key | Description                |
| r   | reload and regenerate HTML |
| j,k | vi like scroll down        |
| +,- | Zoom in/out                |
| p   | Show printer window        |

Supported syntax
---------------------------------------------------------------------
### Text attributes

This part will break line  
this part will not break line
this part will not break line

This part will __bold__  
This part will not__bold__

This part will _italic_  
This part will not_italic_

This part will ~~strike~~

This part is `code`

### Preview

This is code block

``` 
 #include <stdio.h>
 int main() {
 	printf("Hello world\n");
 }
```

    This is also code block
    Hello can you see this?

 This is not code block


### Quote
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

### Table

#### Valid table syntax

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



