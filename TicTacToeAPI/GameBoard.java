/** This is our board class which represents the Tic Tac Toe
    Surface. Consult ReadMe for explanation on design strategy. */
package com.tttapi.start.resources;

import java.util.HashMap;

class GameBoard {

	/** Number of rows on our board. */
	private static int _numRows = 3;
	/** Number of columns on our board. */
	private static int _numColumns = 3;
	/** Representation of surface as 2D Array. */
	private String[][] _board;
	/** Representation of Win Possibilites with Key corresponding to 
	    start position of row/column/diagonal and value corresponding
	    to an array containing score of X player at index 0 and score
	    of O player at index 1. */
	private HashMap<String, int[]> _winTracker = new HashMap<String, int[]>();
	/** Tells us if last move was in an occupied square. */
	private boolean _isOccupied = false;

	/** Constructor which initializes the playing board and sets 
 	    it to empty. Also enters the winning start positions into
 	    _winTracker HashMap and intializes scores of each player to 0. */
	GameBoard() {
 		this._board = new String[_numRows][_numColumns];
 		for (int i = 0; i < _numRows; i++) {
 			for (int j = 0; j < _numColumns; j++) {
 				_board[i][j] = " ";
 			}
 		}
 		/** Column start positions. */
 		_winTracker.put("1", new int[] {0, 0});
 		_winTracker.put("2", new int[] {0, 0});
 		_winTracker.put("3", new int[] {0, 0});
 		/** Row start positions. */
 		_winTracker.put("A", new int[] {0, 0});
 		_winTracker.put("B", new int[] {0, 0});
 		_winTracker.put("C", new int[] {0, 0});
 		/** Diagonal start positions. */
 		_winTracker.put("A1", new int[] {0, 0});
 		_winTracker.put("A3", new int[] {0, 0});
 	}

 	/** Prints the representation of the GameBoard to the terminal. */
	String printBoard() {
 		return ("   1   2   3" + "\n" +
		 		"A  " + _board[0][0] + " | " + _board[0][1] + " | " + _board[0][2] + "\n" +
		 		"  -----------" + "\n" +
		 		"B  " + _board[1][0] + " | " + _board[1][1] + " | " + _board[1][2] + "\n" +
		 		"  -----------" + "\n" +
		 		"C  " + _board[2][0] + " | " + _board[2][1] + " | " + _board[2][2]);
 	}

	/** Determines the corresponding _winTracker index (0 or 1) given
	    a player on this board. */
	int getPlayerIndex(Player player) {
 		if (player.getPiece().equals("X"))
 			return 0;
 		else
 			return 1;
 	}

 	/** Checks if game score for player represented by given
 	    INDEX and starting at given board POSITION is enough
 	    to win, i.e. score = 3. */
 	boolean checkScore(Player player, String position) {
 		int index = getPlayerIndex(player);
 		return (_winTracker.get(position)[index] == 3);
 	}

 	/** Checks game score for player represented by given
 	    INDEX across all given conditions. */
	boolean testWinner(Player player, String[] positions) {
 		for (String position : positions) {
 			if (checkScore(player, position))
 				return true;
 		}
 		return false;
 	}

 	/** Checks if last move was attempted in an already occupied square. */
 	boolean checkOccupied() {
 		return _isOccupied;
 	}

 	/** Checks if the Board is currently full. */
	boolean isFull() {
 		for (int i = 0; i < _numRows; i++) {
 			for (int j = 0; j < _numColumns; j++) {
 				if (_board[i][j].equals(" "))
 					return false;
 			}
 		}
 		return true;
 	}

 	/** Makes a move on board for PLAYER, putting X or O at COORDINATE
 	    if chosen spot is empty. Then checks if the current move results
 	    in a win for PLAYER and returns True if player has won. */
	boolean registerMove(Player player, String coordinate) {
		/** Array Index of current player in relation to _winTracker. */
		int winIndex = getPlayerIndex(player);
		/** Start positions to check for winner based on current move. */
		String[] positionsToCheck = null;
		/** Check the position of desired move, make move if position
		    is empty, update player game scores in _winTracker, and
		    sets positions needed to be checked for winning move. Otherwise
		    sets _isOccupied to true to explain that player tried to fill in
		    already filled square. */
 		switch(coordinate) {
 			case "A1":
 				if (_board[0][0].equals(" ")) {
 					_board[0][0] = player.getPiece();
 					_winTracker.get("A")[winIndex]++;
 					_winTracker.get("1")[winIndex]++;
 					_winTracker.get("A1")[winIndex]++;
 					positionsToCheck = new String[] {"A", "1", "A1"};
 					_isOccupied = false;
 				} else {
 					_isOccupied = true;
 				}
 				break;
 			case "A2":
 				if (_board[0][1].equals(" ")) {
 					_board[0][1] = player.getPiece();
 					_winTracker.get("A")[winIndex]++;
 					_winTracker.get("2")[winIndex]++;
 					positionsToCheck = new String[] {"A", "2"};
 					_isOccupied = false;
 				} else {
 					_isOccupied = true;
 				}
 				break;
 			case "A3":
 				if (_board[0][2].equals(" ")) {
 					_board[0][2] = player.getPiece();
 					_winTracker.get("A")[winIndex]++;
 					_winTracker.get("3")[winIndex]++;
 					_winTracker.get("A3")[winIndex]++;
 					positionsToCheck = new String[] {"A", "3", "A3"};
 					_isOccupied = false;
 				} else {
 					_isOccupied = true;
 				}
 				break;
 			case "B1":
 				if (_board[1][0].equals(" ")) {
 					_board[1][0] = player.getPiece();
 					_winTracker.get("B")[winIndex]++;
 					_winTracker.get("1")[winIndex]++;
 					positionsToCheck = new String[] {"B", "1"};
 					_isOccupied = false;
 				} else {
 					_isOccupied = true;
 				}
 				break;
 			case "B2":
 				if (_board[1][1].equals(" ")) {
 					_board[1][1] = player.getPiece();
 					_winTracker.get("B")[winIndex]++;
 					_winTracker.get("2")[winIndex]++;
 					_winTracker.get("A1")[winIndex]++;
 					_winTracker.get("A3")[winIndex]++;
 					positionsToCheck = new String[] {"B", "2", "A1", "A3"};
 					_isOccupied = false;
 				} else {
 					_isOccupied = true;
 				}
 				break;
 			case "B3":
 				if (_board[1][2].equals(" ")) {
 					_board[1][2] = player.getPiece();
 					_winTracker.get("B")[winIndex]++;
 					_winTracker.get("3")[winIndex]++;
 					positionsToCheck = new String[] {"B", "3",};
 					_isOccupied = false;
 				} else {
 					_isOccupied = true;
 				}
 				break;
 			case "C1":
 				if (_board[2][0].equals(" ")) {
 					_board[2][0] = player.getPiece();
 					_winTracker.get("C")[winIndex]++;
 					_winTracker.get("1")[winIndex]++;
 					_winTracker.get("A3")[winIndex]++;
 					positionsToCheck = new String[] {"C", "1", "A3"};
 					_isOccupied = false;
 				} else {
 					_isOccupied = true;
 				}
 				break;
 			case "C2":
 				if (_board[2][1].equals(" ")) {
 					_board[2][1] = player.getPiece();
 					_winTracker.get("C")[winIndex]++;
 					_winTracker.get("2")[winIndex]++;
 					positionsToCheck = new String[] {"C", "2"};
 					_isOccupied = false;
 				} else {
 					_isOccupied = true;
 				}
 				break;
 			case "C3":
 				if (_board[2][2].equals(" ")) {
 					_board[2][2] = player.getPiece();
 					_winTracker.get("C")[winIndex]++;
 					_winTracker.get("3")[winIndex]++;
 					_winTracker.get("A1")[winIndex]++;
 					positionsToCheck = new String[] {"C", "3", "A1"};
 					_isOccupied = false;
 				} else {
 					_isOccupied = true;
 				}
 				break;
 			default:
 			
 		}
 		/** If player enters valid input, checks if move results in win. */
 		if (positionsToCheck != null)
 			return testWinner(player, positionsToCheck);
 		return false;
	}
}