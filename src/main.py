from server import *
import json
from chess import *

from datetime import datetime
import os

class GameHandler():
    def __init__(self):
        self.start_game()

    def start_game(self):
        # Save game
        starting_date = datetime.today().strftime("%Y-%m-%d")
        starting_time = datetime.today().strftime("%H-%M-%S")
        starting_fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

        self._game = Game(starting_date, starting_time, starting_fen, "*", [])

    # send data to update board and info box
    def on_api_get(self, handler, *args):
        handler.send_response(200)
        handler.send_header("Content-type", "application/json")
        handler.end_headers()
        
        response = self._game.get_current_pos().get_JSON()
       
        handler.wfile.write(bytes(response, "utf-8"))

    # on move made by player
    def on_api_post(self, handler, *args):
        request = json.loads(handler.rfile.read1().decode("utf-8"))
        
        self._game.add_move(request['from'], request['to'], int(request['result']))

        if self._game.ended():
            # Write game to file
            date_and_time = self._game.get_date_time() + ".json"
            dirname = os.path.dirname(__file__)
            filename = date_and_time
            path = os.path.join(dirname, '../games/' + filename)
            self._game.write_to_file(path)
            self.start_game()

        handler.send_response(200)
        handler.send_header("Content-type", "application/json")
        handler.end_headers()

class PastGameHandler():
    def on_api_get(self, handler, query, params):
        if query == "":
            handler.send_response(400)
            handler.end_headers()

        handler.send_response(200)
        handler.send_header("Content-type", "application/json")
        handler.end_headers()

        game_id = query.split("=")[1] + ".json"

        dirname = os.path.dirname(__file__)
        path = os.path.join(dirname, '../games/' + game_id)
       
        game = json.loads(Game.read_from_file(path).get_JSON())
        
        for i in range(len(game['positions'])):
            fen = game['positions'][i]
            pos = Position.get_position(fen)
            game['positions'][i] = json.loads(pos.get_JSON())["board"]

        handler.wfile.write(bytes(json.dumps(game), "utf-8"))

    def on_api_post(self, handler, query, params):
        pass

class ArchiveHandler():
    # returns a reverse chronologically sorted list of previous games
    # %Y-%m-%d-%H-%M-%S
    def get_previous_games(self):
        games = []
            
        for file in listdir("../games/"):
            game_id = file.split(".")[0]

            game = Game.read_from_file("../games/" + game_id + ".json")
            games.append(game)

        # Bubble sort
        n = len(games)
        swapped = True
        while swapped and n >= 0:
            swapped = False
            for i in range(n-1):
                if games[i].get_date_time().replace("-", "") > games[i+1].get_date_time().replace("-", ""):
                    temp = games[i]
                    games[i] = games[i+1]
                    games[i+1] = temp
                    swapped = True
                n -= 1

        return games
    
    def on_api_get(self, handler, *args):
        handler.send_response(200)
        handler.send_header("Content-type", "application/json")
        handler.end_headers()

        games = self.get_previous_games()

        game_ids = [x.get_date_time() for x in games]
        
        response = json.dumps({ "games": (game_ids) })
                                
        handler.wfile.write(bytes(response, "utf-8"))
        
    def on_api_post(self, handler, *args):
        pass

if __name__ == "__main__":
    server = WebServer(("localhost", 8080), RequestHandler)
    print("Server started")

    # Serves all the .svg files in the ./svgs/ directory
    # Only chess piece svgs should be in this dir
    for file in listdir("./svgs/"):
        server.add_handler(ResourceHandler(f"/{file}", f"./svgs/{file}", "image/svg+xml"))
    
    server.add_handler(ResourceHandler("/board.css", "./styles/board.css", "text/css"))
    server.add_handler(ResourceHandler("/info.css", "./styles/info.css", "text/css"))
    server.add_handler(ResourceHandler("/main-page.css", "./styles/main-page.css", "text/css"))
    server.add_handler(ResourceHandler("/game-page.css", "./styles/game-page.css", "text/css"))
    server.add_handler(ResourceHandler("/games-page.css", "./styles/games-page.css", "text/css"))
    server.add_handler(ResourceHandler("/navbar.css", "./styles/navbar.css", "text/css"))
    server.add_handler(ResourceHandler("/buttons.css", "./styles/buttons.css", "text/css"))
    server.add_handler(ResourceHandler("/games.css", "./styles/games.css", "text/css"))
    server.add_handler(ResourceHandler("/global.css", "./styles/global.css", "text/css"))

    server.add_handler(ResourceHandler("/board.js", "./scripts/board.js", "text/javascript"))
    server.add_handler(ResourceHandler("/main-page.js", "./scripts/main-page.js", "text/javascript"))
    server.add_handler(ResourceHandler("/info.js", "./scripts/info.js", "text/javascript"))
    server.add_handler(ResourceHandler("/game-page.js", "./scripts/game-page.js", "text/javascript"))
    server.add_handler(ResourceHandler("/games-page.js", "./scripts/games-page.js", "text/javascript"))
    server.add_handler(ResourceHandler("/buttons.js", "./scripts/buttons.js", "text/javascript"))
    server.add_handler(ResourceHandler("/games.js", "./scripts/games.js", "text/javascript"))

    game_handler = GameHandler()
    server.add_handler(APIHandler("/api/board", game_handler.on_api_get, game_handler.on_api_post))

    past_game_handler = PastGameHandler()
    server.add_handler(APIHandler("/api/game", past_game_handler.on_api_get, past_game_handler.on_api_post))
    
    archive_handler = ArchiveHandler()
    server.add_handler(APIHandler("/api/games", archive_handler.on_api_get, archive_handler.on_api_post))
   
    server.add_handler(WebPageHandler("/", "./pages/main-page.html",
                                        ["/global.css", "/board.css", "/info.css", 
                                         "/main-page.css", "/navbar.css", "/buttons.css"],
                                        ["/board.js", "/info.js", "/main-page.js", 
                                         "/buttons.js"]))

    server.add_handler(WebPageHandler("/game", "./pages/game-page.html",
                                        ["/board.css", "/info.css", "/game-page.css",
                                         "/navbar.css", "/buttons.css", "/global.css"], 
                                        ["/board.js", "/info.js", "/game-page.js",
                                         "/buttons.js"]))

    server.add_handler(WebPageHandler("/games", "./pages/games-page.html", 
                                        ["/navbar.css", "/games-page.css", "/games.css",
                                         "/global.css"], 
                                        ["/games-page.js", "/games.js"]))

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass

    server.server_close()
