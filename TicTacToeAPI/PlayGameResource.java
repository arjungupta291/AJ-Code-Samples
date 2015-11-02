package com.tttapi.start.resources;
import java.util.HashMap;

import com.tttapi.start.resources.Player;
import com.tttapi.start.resources.GameBoard;
import com.tttapi.start.resources.Game;

import javax.ws.rs.GET;
import javax.ws.rs.POST;
import javax.ws.rs.PUT;
import javax.ws.rs.DELETE;
import javax.ws.rs.Path;
import javax.ws.rs.Produces;
import javax.ws.rs.Consumes;
import javax.ws.rs.QueryParam;
import javax.ws.rs.PathParam;
import javax.ws.rs.core.MediaType;
import javax.ws.rs.core.Response;;
import java.util.concurrent.atomic.AtomicLong;

@Path("/game")
@Produces(MediaType.TEXT_PLAIN)
@Consumes(MediaType.TEXT_PLAIN)
public class PlayGameResource {

	/** Makeshift database object to store Game objects. */
	private HashMap<String,Game> _database = new HashMap<String,Game>();

	/** API POST method to create a new game with the first player.
	    The player to create the game always gets assigned piece X.
	    NAME is passed in the URL to be associated with first player. */
	@POST
	@Path("/create_game/{name}")
	public String createGame(@PathParam("name") String name) {
		String firstPiece = "X";
		Player player0 = new Player(name, firstPiece);
		Game game0 = new Game(player0);
		_database.put(game0.getID(), game0);
		return ("\nHTTP Status: 201 Created\n\n" + "Your New Game ID is " + game0.getID() + "\n" +
				"Current Board View: " + "\n\n" + game0.getBoard().printBoard() + "\n");
	}

	/** API PUT method to add player to existing game. URL takes
	    paramters ID, which is the Game ID you will be told of upon 
	    creation of game, and NAME, which is the name of the second
	    player. Adds specified player to specified Game. */
	@PUT
	@Path("/add_player/{id}/{name}")
	public String addPlayer(@PathParam("id") String id, @PathParam("name") String name) {
		Game selectedGame = _database.get(id);
		Player player1 = new Player(name, "O");
		return ("\n" + selectedGame.addPlayer(player1) + " to Game " + id + ".\n");
	}

	/** API PUT method to take a turn. URL takes parameters, Game ID,
	    NAME of player whose current turn it is, and COORDINATE on grid
	    as shown. Note that player turn order is enforced so taking turns
	    out of order will result in notification and nothing happening.
	    Other possible notifications include game being won, a resulting draw,
	    a move being attempted in an occupied square (current user can redo
	    turn in this case), the game having already concluded, or, if everything
		occurs according to the rules, on to the next turn. */
	@PUT
	@Path("/make_move/{id}/{name}/{coordinate}")
	public String makeMove(@PathParam("id") String id, 
						   @PathParam("name") String name, @PathParam("coordinate") String coordinate) {
		Game selectedGame = _database.get(id);
		return ("\n" + selectedGame.takeTurn(name, coordinate) + "\n" + 
			    selectedGame.getBoard().printBoard() + "\n");
	}

	/** API GET method to view current board status of game identified
	    by ID. */
	@GET
	@Path("/view_board/{id}")
	public String viewBoard(@PathParam("id") String id) {
		if (_database.size() == 0) {
			return ("\nThere are no current active Games.\n");
		} else if (_database.get(id) == null) {
			return ("\nThere is no Game with the ID you have provided.\n");
		} else {
			Game selectedGame = _database.get(id);
			return ("\nGame Board number " + id + ":\n" + selectedGame.getBoard().printBoard() + "\n");
		}
	}

	/** API DELETE method to remove game object from makeshift database. */
	@DELETE
	@Path("/delete_game/{id}")
	public String deleteGame(@PathParam("id") String id) {
		if (_database.size() == 0) {
			return ("\nThere are no current active Games to delete.\n");
		} else if (_database.get(id) == null) {
			return ("\nThere is no Game with the ID you have provided.\n");
		} else {
			_database.remove(id);
			return ("\n" + "Game Number " + id + " deleted.\n");
		}
	}
}