Visualizer for Nyan-cat Game
============================

How to start
------------

0. Vova's protocol: https://github.com/gelkin/multicast-lab/blob/master/nayn-protocol

1. Kostya's client: https://github.com/Martoon-00/nyan-cat-chase

2. This visualizer

3. Run them together through unix pipe.

------------------------

*Linux!!!*  
we have problems with successful connection between Windows and Linux clients in one net
and there is no time to solve it now

Visualizer dependencies
------------------------

1. **python3** (read full instructions below)

2. **Kivy** - framework for GUI
> http://kivy.org/docs/installation/installation-linux.html

It will be nice to have **PyCharm** - it may save some time for us.
> https://www.jetbrains.com/pycharm/download/#tabs_1=linux
> (nearly 130 MB)

Client part
-----------

1. Clone Kostya's repository:  
```git clone https://github.com/Martoon-00/nyan-cat-chase```  

2. IntelliJ IDEA -> Open project -> nyan-cat-chase  

3. Wait while it download all dependencies with Maven help.

4. Try run `HunterSillyPlayer`

Visualizer part
-------------------
0. ```sudo apt-get update```

1. Check python3 version  
```python3 --version``` must be 3.4

2. pip3  
  ```pip3 --version```  
  If not installed:  
  ```sudo apt-get install python3-pip```  
  Current version is 7.1.2 (at moment of writing)  
  To update it  
  ```sudo pip3 install --upgrade pip```  

3. Install Kivy through apt-get  
  (From here: http://kivy.org/docs/installation/installation-linux.html)  
  ```sudo add-apt-repository ppa:kivy-team/kivy```  
  ```sudo apt-get update```  
  ```sudo apt-get install python3-kivy```  
