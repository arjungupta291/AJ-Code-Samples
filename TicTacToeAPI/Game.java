/** Class which manages the game setup and execution. */
package com.tttapi.start.resources;

import java.util.concurrent.atomic.AtomicInteger;

class Game {

	/** Simple mechanism for generating unique ID's. */
	private static AtomicInteger _uniqueId = new AtomicInteger();
	private String _id;
	/** The GameBoard object attached to instance of Game. */
	private GameBoard _gameBoard = new GameBoard();
	/** The two players in this game session. */
	Player _player0;
	Player _player1;
	/** Mechanism for easily rotating turns between players. */
	Player[] _selection = new Player[2];
	/** Tracks the player whose turn it is currently. */
	private int _currentTurnIndex = 0;
	/** Tracks if the current move results in a win for currentTurn. */
	private boolean _winner = false;
	/** Tracks if the board is full without a winner to establish a draw. */
	private boolean _fullBoard = false;
	/** Tracks if the game has ended so we know when to stop processing
	    turn requests for the current game object. */
	private boolean _hasFinished = false;

	/** Constructor which takes in an initial player and binds them to _gameBoard. */
	Game(Player player) {
		_id = String.valueOf(_uniqueId.getAndIncrement());
		_player0 = player;
		_selection[0] = _player0;
		_player0.bind(_gameBoard);
	}

	/** Getter for _id. */
	String getID() {
		return _id;
	}

	/** Getter for _gameBoard*/
	GameBoard getBoard() {
		return _gameBoard;
	}
	/** Adds another player to this Game and binds player to
	    _gameBoard. */
	String addPlayer(Player player) {
		if (_player0 != null && _player1 == null) {
			_player1 = player;
			_selection[1] = _player1;
			_player1.bind(_gameBoard);
			return (_player1.getName() + " has been added to Game.");
		} else {
			return ("There are already two players in this game.");
		}
	}

	/** Method to enforce turn taking for this Game. Instead of having a
	    traditional game loop, we need to be able to process all game state
	    information per function call to stay RESTful API compatible. */
	String takeTurn(String name, String coordinate) {
		/** Check if game has finished. */
		if (!_hasFinished) {
			/** Checks if there are two players in the game and then checks if 
			    player name provided matches player whose turn it is. */
			if (_selection[_currentTurnIndex] == null) {
				return ("There is only one player in this game. Add another to continue.\n");
			} else if (_selection[_currentTurnIndex].getName().equals(name)) {
				_winner = _selection[_currentTurnIndex].makeMove(coordinate);
				_fullBoard = _gameBoard.isFull();
				/** Checks if move resulted in winner. */
				if (_gameBoard.checkOccupied()) {
					return ("Move attempted in occupied square. Try Again.\n");
				} else if (_winner) {
					_hasFinished = true;
					return (name + " has won the Game.\n");
				/** Otherwise checks if board is full and game is a draw. */
				} else if (!_winner && _fullBoard) {
					_hasFinished = true;
					return ("Game has ended as a Draw.\n");
				/** If none of the above, alternates to other player's turn. */
				} else {
					_currentTurnIndex = 1 - _currentTurnIndex;
					return ("On to the Next Turn.\n");
				}
			/** Handles Wrong player taking a turn. */
			} else {
				return ("Wrong Player attempting to take turn.\n");
			}
		/** Handles trying to make a turn on a completed game. */
		} else {
			return ("This Game has Ended.\n");
		}
	}
}