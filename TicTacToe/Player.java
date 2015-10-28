/** Class to represent a player in our game of 
    Tic Tac Toe. */

package TicTacToe;

class Player {

	/** Name of player. */
	private String _name;
	/** The Piece which instance of player will use (X or O). */
	private String _gamePiece;
	/** The GameBoard which player is bound to. */
	private GameBoard _myBoard;

	/** Constructor to bind player to BOARD and PIECE. */
	Player(String name, String piece) {
		this._name = name;
		this._gamePiece = piece;
	}

	/** Returns player gamePiece (X or O). */
	String getPiece() {
		return _gamePiece;
	}

	/** Returns player name. */
	String getName() {
		return _name;
	}

	/** Binds this Player to a GameBoard. */
	void bind(GameBoard board) {
		_myBoard = board;
	}

	/** Makes a move for current player on _myBoard.
	    Returns true if current move wins the game for player. */
	boolean makeMove(String coordinate) {
		return _myBoard.registerMove(this, coordinate);
	}
}