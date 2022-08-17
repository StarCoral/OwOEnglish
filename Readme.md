# OWO English

## Introduction

This is NTHU NLP final project.  
  
It is difficult for students to spell long words.
If we can segment long word properly, student can easily memory its meaning and spelling.  

## Develop

+ Logic 
    + python
+ Web 
    + Flask
    + Jinja2
    + Bootstrap
    + HTML
    + CSS
## How to segment loooooong word

+ Example: `Antidisestablishmentarianism`
+ Ground truth: `Anti-dis-establish-ment-arian-ism`
+ How about consider as
```
Anti-[disestablishmentarian]-ism
Anti-dis-[establishment]-arian-ism
anti-dis-establish-ment-arian-ism 
```
+ By this observation, we can segment long word by recursive method.


## Demo
1. MainPage
![](https://i.imgur.com/xT1K3Kp.png)
2. Search `Antidisestablishmentarianism`
![](https://i.imgur.com/AX2AdVs.png)
3. Search `pencil`
![](https://i.imgur.com/gEim0XE.png)
