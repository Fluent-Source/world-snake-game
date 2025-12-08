# Snake Game Around the World

A small game that implements the classic Snake with custom maps.

Made as a fun project to show off Fluent Source in Python.

## Getting Started

This project uses [Python](https://www.python.org/) and [uv](https://docs.astral.sh/uv/). To run the game on your computer:
1. `git clone` the project and enter it's directory.
2. run `uv install` to install dependencies.
3. Activate the venv (the command differs depending on platform).
4. run `python main.py`.

### Controlls

- Movement: WASD / Arrow Keys
- Select: Enter
- Retrun to menu: esc

The level can be selected by pressing left or right.

## Custom Maps

I likely won't look at PRs, but if you want to add your own custom maps, the following must be done:

1. Create a new folder for the map name under `levels`. Inside the `levels` folder.
2. Add `background.png` for the background. The png should be a around a 9:8 ratio, but it will scale the image to match the window .
3. Add a `map.txt` for the walls and game logic. Maps must be 36x32 characters. 
    1. `.` is a space that the snake and fruit can be on.
    2. `#` is a wall space.
    3. `x` is an out of bounds cell. It looks like a `.` space but acts like a `#` space.
4. Optional: Add the folling four csv files: `right.csv`, `down-right.csv`, `up-right.csv`,`down.csv`.
    1. If your map has walls that should be removed, you can add cordinates to the appropriate csv to remove the specified wall.
5. Add the name of the file to `levels/levels.txt`, your map should then be selectable from the level select using left / right.

### Notes:
- `map.txt` and the csv files can be edited and will update while the game is running for ease of development.
- A grid can also be enalbed through the config file to make filling out the csv files easier.
- To adjust additional properties, such as the color of walls, the snake, you must manually update the config file.

## Assets
- All background maps are from [OpenStreetMap](https://www.openstreetmap.org/)
- [Snake and Fruit](https://opengameart.org/content/snake-game-assets) licenced under CC0 by Clear_code.