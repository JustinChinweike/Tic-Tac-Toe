#Tic-Tac-Toe-AI is a Python-based implementation of the classic Tic-Tac-Toe game featuring an AI opponent using the minimax algorithm. It supports three different interfaces:

 . Console (play in the terminal)

 . GUI (play using a Tkinter-based graphical interface)

 . Browser (play directly in a web browser via PyScript)


## Game Engine Library

The game logic is encapsulated in a reusable library, allowing seamless integration across multiple front ends without code duplication.



## Game Front Ends


### Browser Front End

Play tic-tac-toe in your web browser through PyScript:
```
$ python -m browser
```
This command starts a local HTTP server and opens the game in your default web browser.


### Console Front End

Play tic-tac-toe in the terminal:

```
$ python -m console
```

You can optionally set one or both players to a human player (`human`), a computer player making random moves (`random`), or an unbeatable minimax computer player (`minimax`), as well as change the starting player:

```
$ python -m console -X minimax -O random --starting O
```

Where:

human - Human player

random - AI that makes random moves

minimax - AI that uses the minimax algorithm

--starting O - Specifies the starting player (X or O)



### Window Front End

Play tic-tac-toe against a minimax computer player in a GUI application built with Tkinter:


$ python -m window

To change the players, who are currently hard-coded, you'll need to edit the following fragment of the front end's code:

```python
def game_loop(window: Window, events: Queue) -> None:
    player1 = WindowPlayer(Mark("X"), events)
    player2 = MinimaxComputerPlayer(Mark("O"))
    starting_mark = Mark("X")
    TicTacToe(player1, player2, WindowRenderer(window)).play(starting_mark)
```

