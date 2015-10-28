/** Class which manages the game setup and execution. */

package TicTacToe;

class Game {

	/** The GameBoard object attached to instance of Game. */
	GameBoard _gameBoard;
	/** The two players in this game session. */
	Player _player0;
	Player _player1;
	/** Mechanism for easily rotating turns between players. */
	Player[] _selection = new Player[] {_player0, _player1};
	/** Tracks the player whose turn it is currently. */
	int _currentTurnIndex = 0;
	/** Tracks if the current move results in a win for currentTurn. */
	boolean _winner = false;
	/** Tracks if the board is full without a winner to establish a draw. */
	boolean _fullBoard = false;
	/** Tracks if the game has ended so we know when to stop processing
	    turn requests for the current game object. */
	boolean _hasFinished = false;

	Game(GameBoard board, Player player) {
		this._gameBoard = board;
		this._player0 = player;
		_player0.bind(_gameBoard);
	}

	/** Adds another player to this Game and binds player to
	    _gameBoard. */
	void addPlayer(Player player) {
		if (_player0 != null && _player1 == null) {
			_player1 = player;
			_player1.bind(_gameBoard);
		} else {
			System.out.println("There are already two players in this game.");
		}
	}

	/** Method to enforce turn taking for this Game. Instead of having a
	    traditional game loop, we need to be able to process all game state
	    information per function call to stay RESTful API compatible. */
	void takeTurn(String name, String coordinate) {
		/** Check if game has finished. */
		if (!_hasFinished) {
			/** Check if player name provided matches player whose turn it is. */
			if (_selection[_currentTurnIndex].getName().equals(name)) {
				_winner = _selection[_currentTurnIndex].makeMove(coordinate);
				_fullBoard = _gameBoard.isFull();
				/** Checks if move resulted in winner. */
				if (_winner) {
					_hasFinished = true;
					System.out.println(name + " has won the Game.");
				/** Otherwise checks if board is full and game is a draw. */
				} else if (!_winner && _fullBoard) {
					_hasFinished = true;
					System.out.println("Game has ended as a Draw.");
				/** If none of the above, alternates to other player's turn. */
				} else {
					_currentTurnIndex = 1 - _currentTurnIndex;
				}
			/** Handles Wrong player taking a turn. */
			} else {
				System.out.println("Wrong Player attempting to take turn.");
			}
		/** Handles trying to make a turn on a completed game. */
		} else {
			System.out.println("This Game has Ended.");
		}
	}
}