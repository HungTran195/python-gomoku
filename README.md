# caro-game
### Quick demo:

(Archieve) https://nogamesnolife.herokuapp.com/

![Alt Text](https://github.com/QuocHung52/python-gomoku/blob/af92d2bd07197c8859a87cb20e9def82c10b8b8d/game/static/game/images/screenshot.png) 

### Installing

To run this project, you should start by having Python installed on your computer. 
It's advised you create a virtual environment to store your project dependencies separately. You can install virtualenv with

```
pip install virtualenv
```

Clone or download this repository. In a terminal, just run the following command in the base directory of this project to create `venv` folder in the project directory

```
virtualenv venv
```

Then activate the virtual environment:

```
source venv/bin/activate
```
Now you can install all the project dependencies in this new environment with no impact on your system:

```
pip install -r requirements.txt
```
To run project use command:
```
python manage.py runserver
```
Now open your web browser and go to the url: http://127.0.0.1:8000/ (this is the default server of django)
