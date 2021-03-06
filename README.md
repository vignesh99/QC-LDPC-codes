This repository contains the code for the animations in [QC-LDPC decoder blog post](https://vignesh99.github.io/2022-06-15-QC-LDPC-5G/)  

## Dependencies
The code has been implemented in python, and needs the following libraries :
* `pylab`
* [`manim`](https://pypi.org/project/manim/)
* [`networkx`](https://pypi.org/project/networkx/)
* [`manimnx`](https://pypi.org/project/manimnx/)

## File description
* `classes.py` : Contains the code for all the animations which are defined using manim classes
* `functions.py` : Contains the functions required to implement the above classes

## Execution
For example, to implement the animation class defined as 'OMS', the following command has to be executed :
```
manim classes.py OMS
```
You can find the animation video in the below path of the same directory
```
media/videos/classes/1080p60/OMS.mp4
```
