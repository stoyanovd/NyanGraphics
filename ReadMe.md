Visualizer for Nyan-cat Game
============================

How to start
------------

0. Vova's protocol: https://github.com/gelkin/multicast-lab/blob/master/nayn-protocol

1. Kostya's client: https://github.com/Martoon-00/nyan-cat-chase

2. This visualizer

3. Run them together through unix pipe.

------------------------

**Linux!!!**  
You must have Linux!  
we have problems with successful connection between Windows and Linux clients in one net
and there is no time to solve it now


Client (Kostya's) part
-----------

1. Clone Kostya's repository:  
```git clone https://github.com/Martoon-00/nyan-cat-chase```  

2. IntelliJ IDEA -> Open project -> nyan-cat-chase  

3. Wait while it download all dependencies with Maven help.

4. Try run `HunterSillyPlayer`

Visualizer (Dima's) part
-------------------
0. ```sudo apt-get update```

1. ```python3 --version``` must be 3.4

2. ```pip3 --version```  must be 7.1.2  
  To install:  
  ```sudo apt-get install python3-pip```    
  To update it  
  ```sudo pip3 install --upgrade pip```  

3. **PyCharm** - sth will be easier with it  
  Community Edition will be enough (nearly 130 MB)  
  https://www.jetbrains.com/pycharm/download/#tabs_1=linux  

3. Install **Kivy** through apt-get  
  (From here: http://kivy.org/docs/installation/installation-linux.html)  
  ```sudo add-apt-repository ppa:kivy-team/kivy```  
  ```sudo apt-get update```  
  ```sudo apt-get install python3-kivy```  
