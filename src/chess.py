import json

class Square():
    def __init__(self, algebraic):
        self._algebraic = algebraic            
        self._row = int(algebraic[1]) - 1
        self._col = ord(algebraic[0]) - 97
        self._piece = ""

    def get_algebraic(self):
        return self._algebraic

    def get_row(self):
        return self._row

    def get_col(self):
        return self._col

    def get_piece(self):
        return self._piece

    def set_piece(self, piece):
        self._piece = piece

    @staticmethod
    def from_row_col(row, col):
        return chr(97 + col) + str(row + 1)

class Position():
    def __init__(self, board, whites_move, castling, en_passent_target, halfmoves, fullmoves):
        self._board = board
        self._whites_move = whites_move
        self._castling = castling
        self._en_passent_target = en_passent_target
        self._halfmoves = halfmoves
        self._fullmoves = fullmoves
   
    def get_board(self):
        return self._board

    def is_whites_move(self):
        return self._whites_move

    # row and col as would be in algebraic notation except not
    def __get_square(self, row, col):
        return self._board[7 - row][col].get_piece()

    def __get_square_instance(self, row, col):
        return self._board[7 - row][col]

    def __get_square_by_algebraic(self, algebraic):
        row = int(algebraic[1]) - 1
        col = ord(algebraic[0]) - 97
        return self._board[7 - row][col]
  
    def __set_square(self, row, col, piece):
        self._board[7 - row][col].set_piece(piece)
    
    # start and end are squares
    def __get_pieces_on_row(self, start, end, include_end = False, get_empty = False):
        pieces = []

        row = start.get_row()

        if row != end.get_row():
            raise Exception("Not on same row")

        step = 1 if start.get_col() < end.get_col() else -1

        col = start.get_col() + step
        end_col = end.get_col()

        while col != end_col + (step if include_end else 0):
            piece = self.__get_square_instance(row, col)
            
            if get_empty:
                pieces.append(piece)
            elif piece.get_piece() != "":
                pieces.append(piece)

            col += step    

        return pieces

    def __get_pieces_on_col(self, start, end, include_end = False, get_empty = False):
        pieces = []

        col = start.get_col()

        if col != end.get_col():
            raise Exception("Not on same col")

        step = 1 if start.get_row() < end.get_row() else -1

        row = start.get_row() + step
        end_row = end.get_row()

        while row != end_row + (step if include_end else 0):
            piece = self.__get_square_instance(row, col)
            
            if get_empty:
                pieces.append(piece)
            elif piece.get_piece() != "":
                pieces.append(piece)

            row += step    

        return pieces 

    def __square_lies_on_diagonal(self, start, square):
        start_row = start.get_row()
        start_col = start.get_col()

        normalized_square_row = square.get_row() - start_row
        normalized_square_col = square.get_col() - start_col

        if abs(normalized_square_row) != abs(normalized_square_col):
            return False

        return True

    def __get_pieces_on_diagonal(self, start, end, include_end = False, get_empty = False):
        pieces = []

        start_row = start.get_row()
        start_col = start.get_col()

        end_row = end.get_row()
        end_col = end.get_col()

        if abs(start_row - end_row) != abs(start_col - end_col):
            raise Exception("Not on same diagonal")

        up_step = 1 if start_row < end_row else -1
        right_step = 1 if start_col < end_col else -1

        row = start_row + up_step
        col = start_col + right_step
        
        while row != end_row + (up_step if include_end else 0) and col != end_col + (right_step if include_end else 0):
            piece = self.__get_square_instance(row, col)

            if get_empty:
                pieces.append(piece)
            elif piece.get_piece() != "":
                pieces.append(piece)

            row += up_step
            col += right_step
    
        return pieces

    def __get_king_square(self, white):
        for i in range(8):
            for j in range(8):
                piece = self.__get_square(i, j)
                
                if (white and piece == "K") or (not white and piece == "k"):
                    return self.__get_square_instance(i, j)
    
        raise Exception("No king on board")

    def __get_edge_square_from_diagonal(self, start, up, right):
        up_step = 1 if up else -1
        right_step = 1 if right else -1

        up_limit = 7 if up else 0
        right_limit = 7 if right else 0

        row = start.get_row()
        col = start.get_col()

        while row != up_limit and col != right_limit:
            row += up_step
            col += right_step

        return self.__get_square_instance(row, col)

    # given a king square, it will return an array with forbidden king squares, and pinned pieces
    # for a potential move, if checking pieces array has entries then move is illegal
    def __get_king_threats(self, king_square, white):
        straights = []
        
        straights.append(self.__get_pieces_on_col(king_square, self.__get_square_instance(7, king_square.get_col()), True))
        straights.append(self.__get_pieces_on_col(king_square, self.__get_square_instance(0, king_square.get_col()), True))
        straights.append(self.__get_pieces_on_row(king_square, self.__get_square_instance(king_square.get_row(), 7), True))
        straights.append(self.__get_pieces_on_row(king_square, self.__get_square_instance(king_square.get_row(), 0), True))

        diagonals = []     

        diagonals.append(self.__get_pieces_on_diagonal(king_square, self.__get_edge_square_from_diagonal(king_square, True, True), True))
        diagonals.append(self.__get_pieces_on_diagonal(king_square, self.__get_edge_square_from_diagonal(king_square, False, True), True))
        diagonals.append(self.__get_pieces_on_diagonal(king_square, self.__get_edge_square_from_diagonal(king_square, False, False), True))
        diagonals.append(self.__get_pieces_on_diagonal(king_square, self.__get_edge_square_from_diagonal(king_square, True, False), True))

        checking_pieces = []
        pinned_pieces = [] # 2d array of pinned piece, and attacking piece

        for line in straights:
            to_check_index = 0
            check_for_pin = False

            skip = False

            if len(line) != 0:
                # if first piece in line is own king
                if line[0].get_piece() == ("K" if white else "k"):
                    to_check_index = 1

                    if len(line) == 1:
                        skip = True

                if not skip:
                    p = line[to_check_index]
                    piece = p.get_piece()

                    enemy_queen = "q" if white else "Q"
                    enemy_rook = "r" if white else "R"

                    # if to_check_index is own piece, check if piece after is queen or rook
                    if (piece == piece.upper() and white) or (piece == piece.lower() and not white):
                        if len(line) > to_check_index + 1:
                            if line[to_check_index + 1].get_piece() == enemy_queen or line[to_check_index + 1].get_piece() == enemy_rook:
                                pinned_pieces.append([line[to_check_index + 1], p])
                    elif piece == enemy_queen or piece == enemy_rook:
                        checking_pieces.append(p)
               
        for line in diagonals:
            to_check_index = 0
            check_for_pin = False

            skip = False

            if len(line) != 0:
                # if first piece in line is own king
                if line[0].get_piece() == ("K" if white else "k"):
                    to_check_index = 1

                    if len(line) == 1:
                        skip = True

                if not skip:
                    p = line[to_check_index]
                    piece = p.get_piece()

                    enemy_queen = "q" if white else "Q"
                    enemy_bishop = "b" if white else "B"

                    # if to_check_index is own piece, check if piece after is queen or rook
                    if (piece == piece.upper() and white) or (piece == piece.lower() and not white):
                        if len(line) > to_check_index + 1:
                            if line[to_check_index + 1].get_piece() == enemy_queen or line[to_check_index + 1].get_piece() == enemy_bishop:
                                pinned_pieces.append([line[to_check_index + 1], p])
                    elif piece == enemy_queen or piece == enemy_bishop:
                        checking_pieces.append(p)

        # By this point all pinned pieces are found

        # if straight/diag checking pieces arrays have length, then king must be in check
        # return length of both arrays combined - this is the number of axis from which the king is being checked

        in_check = False

        if len(checking_pieces) != 0:
            in_check = True

        # Check if king is/would be in check from pawn, knight, or king - no pinning here
        
        # for pawn - if pawn is in front of king_square and 1 to left or right then it is checking
        pawn_row = king_square.get_row() + (1 if white else -1)
        enemy_pawn = "p" if white else "P"

        if king_square.get_col() + 1 < 8 and pawn_row >= 0 and pawn_row < 8:
            if self.__get_square(pawn_row, king_square.get_col() + 1) == enemy_pawn:
                checking_pieces.append(self.__get_square_instance(pawn_row, king_square.get_col() + 1))
                in_check = True
        
        if king_square.get_col() - 1 >= 0 and pawn_row >= 0 and pawn_row < 8:
            if self.__get_square(pawn_row, king_square.get_col() - 1) == enemy_pawn:
                checking_pieces.append(self.__get_square_instance(pawn_row, king_square.get_col() - 1))
                in_check = True

        # for knight
        # if 2 away on row and 1 away on col or 2 away on col and 1 away on row is enemy knight then sqr is forbidden
        enemy_knight = "n" if white else "N"

        for i in range(4):
            rel_row = 2
            rel_col = 1

            if i > 1:
                rel_row *= -1
            
            if i % 2 != 0:
                rel_col *= -1

            row = king_square.get_row() + rel_row
            col = king_square.get_col() + rel_col

            if row >= 0 and row < 8 and col >= 0 and col < 8:
                if self.__get_square(row, col) == enemy_knight:
                    checking_pieces.append(self.__get_square_instance(row, col)) 
                    in_check = True

            row = king_square.get_row() + rel_col
            col = king_square.get_col() + rel_row

            if row >= 0 and row < 8 and col >= 0 and col < 8:
                if self.__get_square(row, col) == enemy_knight:
                    checking_pieces.append(self.__get_square_instance(row, col))
                    in_check = True

        # for king
        enemy_king = self.__get_king_square(not white)

        if abs(enemy_king.get_row() - king_square.get_row()) <= 1 and abs(enemy_king.get_col() - king_square.get_col()) <= 1:
            checking_pieces.append(enemy_king) 
            in_check = True

        return in_check, checking_pieces, pinned_pieces

    def __number_legal_king_moves(self, white):
        king_square = self.__get_king_square(white)
        legal_squares = 0

        # for i in rows (-1, 0, 1)
        #   for j in cols (-1, 0, 1)
        #       if 0,0 skip
        #       if square is not in check - this will account for enemy piece that could be captured
        #               and square is not occupied with same color piece
        #           then add 1 to counter  

        for i in range(-1, 2, 1):
            for j in range(-1, 2, 1):
                if i != 0 or j != 0:
                    row = king_square.get_row() + i
                    col = king_square.get_col() + j
                    
                    if row > 0 and row < 8 and col > 0 and col < 8:
                        sqr = self.__get_square_instance(row, col)
                        in_check, checking_axises, pinned_pieces = self.__get_king_threats(sqr, white)
                        occupied = (sqr.get_piece().upper() == sqr.get_piece()) if white else (sqr.get_piece().lower() == sqr.get_piece())

                        if sqr.get_piece() == "":
                            occupied = False

                        if not in_check and not occupied:
                            legal_squares += 1

        return legal_squares

    def __get_all_squares_between(self, sqr1, sqr2, include_end = False):
        if sqr1.get_row() == sqr2.get_row():
            return self.__get_pieces_on_row(sqr1, sqr2, include_end, True)
        elif sqr1.get_col() == sqr2.get_col():
            return self.__get_pieces_on_col(sqr1, sqr2, include_end, True)
        elif self.__square_lies_on_diagonal(sqr1, sqr2):
            return self.__get_pieces_on_diagonal(sqr1, sqr2, include_end, True)
        else:
            raise Exception("u goofed")

    # Returns -1 if illegal, and move has not been applied to position
    # Returns 0 if move has been applied to position
    # Returns 1 if game end (who just played wins)
    # Returns 2 if draw
    # Returns 3 if game end (who just played loses)
    def do_move(self, fromm, to):
        from_square = self.__get_square_by_algebraic(fromm)
        to_square = self.__get_square_by_algebraic(to)

        from_piece = from_square.get_piece()
        to_piece = to_square.get_piece()

        capture = to_square.get_piece() != ""

        # Check if player's turn
        if (from_piece == from_piece.upper()) != self._whites_move:
            return -1

        # Check if moving pieces to the same square
        if fromm == to:
            return -1

        # Check if capturing own pieces
        if to_piece != "" and ((from_piece == from_piece.upper()) == (to_piece == to_piece.upper())):
            return -1

        king_square = self.__get_king_square(self._whites_move)

        in_check, checking_pieces, pinned_pieces = self.__get_king_threats(king_square, self._whites_move)

        # if checking from multiple axises then must be king move 
        if in_check:
            if len(checking_pieces) > 1:
                if from_piece.upper() != "K":
                    return -1

        # Check if piece is unmovable - though it should still be able to move on line of attack
        for i in pinned_pieces:
            pinned = i[0]
            attacker = i[1]

            # if moving piece is pinned
            if pinned.get_algebraic() == from_square.get_algebraic():
                if pinned.get_row() == attacker.get_row():
                    if to_square.get_row() != attacker.get_row():
                        return -1
                elif pinned.get_col() == attacker.get_col():
                    if to_square.get_col() != attacker.get_col():
                        return -1
                elif not self.__square_lies_on_diagonal(attacker, to_square):
                        return -1

        result = -1

        match from_piece.upper():
            case "K":
                result = self.__do_king_move(fromm, to)
            case "P":
                result = self.__do_pawn_move(fromm, to)
            case "R":
                result = self.__do_rook_move(fromm, to)
            case "N":
                result = self.__do_knight_move(fromm, to)
            case "B":
                result = self.__do_bishop_move(fromm, to)
            case "Q":
                result = self.__do_queen_move(fromm, to)
                
        if self.__is_checkmate(self._whites_move):
            return 3

        if self.__is_stalemate(self._whites_move):
            return 2

        return result

    def __is_checkmate(self, white):
        king_square = self.__get_king_square(white)
        in_check, checking_pieces, pinned_pieces = self.__get_king_threats(king_square, white)
       
        if not in_check:
            return False

        if len(checking_pieces) > 1:
            # must be king move - if king cannot move then mate
            if self.__number_legal_king_moves(white) == 0:
                return True

        else:
            # if king is only piece - checkmate
            own_piece_counter = 0 # does not incl king
            for i in range(len(self._board)):
                for j in range(len(self._board[i])):
                    piece = self._board[i][j].get_piece()

                    if (piece.upper() == piece and white) or (piece.lower() == piece and not white):
                        if piece.upper() != "K":
                            own_piece_counter += 1
            
            if own_piece_counter == 0:
                return True

            # if king cannot be moved then the only option is to block the attack or capture the attacker 
            if self.__number_legal_king_moves(white) == 0:
                # checking piece must be captured or blocked
                #   __get_king_threats can be used to check if piece can be captured or attack blocked - checking pieces are pieces that can capture
                #       loop thru checking piece - make sure none are pinned or if capturing piece is king that capturing is legal
                #       if capturing piece is pinned to attacking piece then not mate
                checking_piece = checking_pieces[0]

                # can piece that is checking king be captured
                can_capture, pieces_that_can_capture, pnd = self.__get_king_threats(checking_piece, not white)

                can_be_captured = False

                if can_capture: 
                    #   check if checking piece can be captured using __get_king_threats
                    #       for each checking piece check if it is pinned using get_king_threats
                    #       if pinned by another piece then ignore
                    #       if no piece can capture checking piece (ie all pieces attacking checking piece are pinned or no pieces attacking)
                    #       then checking piece must be blocked
                    for i in pieces_that_can_capture:
                        if i.get_piece().upper() != "K" and not any(i == p for p in pinned_pieces):
                            return False

                mate = True

                # piece must be blocked
                if not can_be_captured:
                    if checking_piece.get_piece().upper() == "P" or checking_piece.get_piece().upper() == "N":
                        return True # pawns and knights cannot be blocked

                    # do above process for square
                    # if no piece can move there then go to next square
                    # if no piece can move to block then mate                        
                    for i in self.__get_all_squares_between(king_square, checking_piece):
                        can_capture_i, pieces_that_can_capture_i, b = self.__get_king_threats(i, not white)
                        if can_capture_i:
                            for j in pieces_that_can_capture_i:
                                # piece must not be king, or diagonal pawn
                                if not j.get_piece().upper() == "K":
                                    skip = False
                                    if j.get_piece().upper() == "P":
                                        if j.get_row() != i.get_row():
                                            skip = True

                                    if not skip and not any(j in p for p in pinned_pieces):
                                        mate = False
               
                if mate:
                    return True
                    
            # legal moves exist
            return False

    def __is_stalemate(self, white):
        own_pieces = []

        # get an array of own pieces 
        for i in range(len(self._board)):
            for j in range(len(self._board[i])):
                sqr = self._board[i][j]
                if (sqr.get_piece().upper() == sqr.get_piece() if white else sqr.get_piece().lower() == sqr.get_piece()):
                    if sqr.get_piece() != "":
                        own_pieces.append(sqr)

        # if king is only piece and cannot move then stalemate
        if len(own_pieces) == 1 and self.__number_legal_king_moves(white) == 0:
            return True

        # if king can move then not stalemate
        if self.__number_legal_king_moves(white) != 0:
            return False

        king_square = self.__get_king_square(white)

        in_check, checking_pieces, pinned_pieces = self.__get_king_threats(king_square, white)

        for piece in own_pieces:
            # piece cannot move if pinned to king, unless the pinning piece can be captured
            for pinned_piece in pinned_pieces:
                if piece.get_algebraic() == pinned_piece[0].get_algebraic():
                    c, ch, chp = self.__get_king_threats(pinned_piece[1], not white)
                    if c:
                        return False # pinning piece can be captured

            # if piece is pawn
            #   if directly ahead is free then not stalemate
            #   if can capture - en passent or otherwise then not stalemate
            #   check if can capture en passent
            if piece.get_piece().upper() == "P": # check that pawn is not pinned
                travel_dir = 1 if white else -1
                
                row = piece.get_row()
                col = piece.get_col()

                # pawn will never be on last row - it would just promote
                if self.__get_square(row + travel_dir, col) == "":
                    return False
                
                if col + 1 < 8:
                    if self.__get_square(row + travel_dir, col + 1) == "":
                        return False

                if col - 1 >= 0:
                    if self.__get_square(row + travel_dir, col - 1) == "":
                        return False

                # if can capture en passent target square then legal move exists
                if self._en_passent_target != "-":
                    target_sqr = self.__get_square_by_algebraic(self._en_passent_target)
                    if target_sqr.get_row() == row and abs(row - target_sqr.get_row()) == 1:
                        return False

        return True

    def __do_king_move(self, fromm, to):
        from_square = self.__get_square_by_algebraic(fromm)
        to_square = self.__get_square_by_algebraic(to)

        from_piece = from_square.get_piece()
        to_piece = to_square.get_piece()

        capture = to_square.get_piece() != ""

        row_diff = abs(to_square.get_row() - from_square.get_row())
        col_diff = abs(to_square.get_col() - from_square.get_col())

        # For castling
        initial_row = 0 if self._whites_move else 7

        if from_square.get_row() == initial_row and col_diff > 1:
            kingside = to_square.get_col() > 4 

            if kingside:
                if ("K" if self._whites_move else "k") not in self._castling:
                    return -1
            else: # queenside
                if ("Q" if self._whites_move else "q") not in self._castling:
                    return -1

            rook_sqr = self.__get_square_instance(initial_row, 7 if kingside else 0)

            pieces = self.__get_pieces_on_row(from_square, rook_sqr)

            if len(pieces) != 0:
                return -1 

            # check not castling thru check or in check
            # for kingside cols are 4, 5, 6
            # for queenside cols are 4, 3, 2
            end = 6 if kingside else 2
            step = 1 if kingside else -1
            
            for i in range(4, end + step, step):
                sqr = self.__get_square_instance(initial_row, i)
                in_check, checking_pieces, pinned_pieces = self.__get_king_threats(sqr, self._whites_move)
                
                if in_check:
                    return -1

            # do move
            rook_to_col = 5 if kingside else 3
            king_to_col = 6 if kingside else 2
            
            rook_sqr.set_piece("")
            from_square.set_piece("")
            
            self.__get_square_instance(initial_row, rook_to_col).set_piece("R" if self._whites_move else "r")
            self.__get_square_instance(initial_row, king_to_col).set_piece("K" if self._whites_move else "k")

            # update self._castling
            self._castling = self._castling.replace("K" if self._whites_move else "k", "")
            self._castling = self._castling.replace("Q" if self._whites_move else "q", "")

            if self._castling == "":
                self._castling = "-"

            self._whites_move = not self._whites_move
        
            if self._whites_move:
                self._fullmoves += 1

            self._halfmoves += 1

            if self._halfmoves == 50:
                return 1

            self._en_passent_target = "-"

            return 0

        if row_diff > 1 or col_diff > 1:
            return -1

        in_check, checking_pieces, pinned_pieces = self.__get_king_threats(to_square, self._whites_move)

        # Check if moving to forbidden square
        if in_check:
            return -1

        to_square.set_piece(from_piece)
        from_square.set_piece("")
        
        self._castling = self._castling.replace("K" if self._whites_move else "k", "")
        self._castling = self._castling.replace("Q" if self._whites_move else "k", "")

        self._whites_move = not self._whites_move
        
        if self._whites_move:
            self._fullmoves += 1
           
        if capture:
            self._halfmoves = 0
        else:
            self._halfmoves += 1
            
        if self._halfmoves == 50:
            return 1
        
        self._en_passent_target = "-" 

        return 0

    def __do_pawn_move(self, fromm, to):
        from_square = self.__get_square_by_algebraic(fromm)
        to_square = self.__get_square_by_algebraic(to)

        from_piece = from_square.get_piece()
        to_piece = to_square.get_piece()

        capture = to_square.get_piece() != ""
        
        is_white = from_piece == from_piece.upper()
        
        on_starting_square = from_square.get_row() == 1 if is_white else from_square.get_row() == 6
            
        squares_forward = abs(to_square.get_row() - from_square.get_row())
      
        en_passent_set = False

        if capture or self._en_passent_target == to:
            # Must be 1 square behind attacking square
            if is_white:
                if to_square.get_row() - from_square.get_row() != 1:
                    return -1
            else:
                if to_square.get_row() - from_square.get_row() != -1:
                    return -1
            
            # Must be 1 away from to col, not on to col
            if abs(from_square.get_col() - to_square.get_col()) != 1:
                return -1
            
            # If target square is en passent then remove pawn
            if self._en_passent_target == to:
                en_passent_square = self.__get_square_by_algebraic(self._en_passent_target)
                self.__set_square(from_square.get_row(), en_passent_square.get_col(), "")
        else:
            if to_square.get_col() != from_square.get_col():
                return -1
            
            if on_starting_square:
                if not (squares_forward == 1 or squares_forward == 2):
                    return -1
                elif squares_forward == 2:
                    row = (to_square.get_row() - 1) if is_white else (to_square.get_row() + 1)

                    if self.__get_square(row, to_square.get_col()) != "":
                        return -1

                    self._en_passent_target = Square.from_row_col(row, to_square.get_col())
                    en_passent_set = True
            else:
                if squares_forward != 1:
                    return -1         

        to_square.set_piece(from_piece)
        from_square.set_piece("")

        king_square = self.__get_king_square(self._whites_move)
        
        in_check, checking_pieces, pinned_pieces = self.__get_king_threats(king_square, self._whites_move)

        # Check if king would be in check
        if in_check:
            to_square.set_piece(to_piece)
            from_square.set_piece(from_piece)
            return -1

        if en_passent_set == False:
            self._en_passent_target = "-"

        # Promote pawns to queens if at the end of the board
        if is_white and to_square.get_row() == 7:
            to_square.set_piece("Q")
        elif not is_white and to_square.get_row() == 0:
            to_square.set_piece("q")

        self._whites_move = not self._whites_move
        
        if self._whites_move:
            self._fullmoves += 1
            
        self._halfmoves = 0

        return 0

    def __do_rook_move(self, fromm, to):
        from_square = self.__get_square_by_algebraic(fromm)
        to_square = self.__get_square_by_algebraic(to)

        from_piece = from_square.get_piece()
        to_piece = to_square.get_piece()

        capture = to_square.get_piece() != ""
        
        same_row = from_square.get_row() == to_square.get_row()
        same_col = from_square.get_col() == to_square.get_col()
        
        line = []

        # Check row/col for obstructions
        if same_row:
            line = self.__get_pieces_on_row(from_square, to_square)
        elif same_col:
             line = self.__get_pieces_on_col(from_square, to_square)
        else:
            return -1

        if len(line) != 0:
            return -1

        to_square.set_piece(from_piece)
        from_square.set_piece("")

        king_square = self.__get_king_square(self._whites_move)
        
        in_check, checking_pieces, pinned_pieces = self.__get_king_threats(king_square, self._whites_move)

        # Check if king would be in check
        if in_check:
            to_square.set_piece(to_piece)

            from_square.set_piece(from_piece)
            return -1

        # updated castling legality (cannot castle after moving rook) 
        if from_square.get_col() > 4:
            self._castling = self._castling.replace("K" if self._whites_move else "k", "")
        else:
            self._castling = self._castling.replace("Q" if self._whites_move else "k", "")

        if self._castling == "":
            self._castling = "-"

        self._whites_move = not self._whites_move
        
        if self._whites_move:
            self._fullmoves += 1
            
        if capture:
            self._halfmoves = 0
        else:
            self._halfmoves += 1
            
        if self._halfmoves == 50:
            return 1

        self._en_passent_target = "-" 

        return 0

    def __do_knight_move(self, fromm, to):
        from_square = self.__get_square_by_algebraic(fromm)
        to_square = self.__get_square_by_algebraic(to)

        from_piece = from_square.get_piece()
        to_piece = to_square.get_piece()

        capture = to_square.get_piece() != ""

        if abs(from_square.get_row() - to_square.get_row()) == 2:
            if abs(from_square.get_col() - to_square.get_col()) != 1:
                return -1
        elif abs(from_square.get_col() - to_square.get_col()) == 2:
            if abs(from_square.get_row() - to_square.get_row()) != 1:
                return -1
        else:
            return -1

        to_square.set_piece(from_piece)
        from_square.set_piece("")

        king_square = self.__get_king_square(self._whites_move)
        
        in_check, checking_pieces, pinned_pieces = self.__get_king_threats(king_square, self._whites_move)

        # Check if king would be in check
        if in_check:
            to_square.set_piece(to_piece)
            from_square.set_piece(from_piece)
            return -1

        self._whites_move = not self._whites_move

        if self._whites_move:
            self._fullmoves += 1

        if capture:
            self._halfmoves = 0
        else:
            self._halfmoves += 1

        if self._halfmoves == 50:
            return 1

        self._en_passent_target = "-" 

        return 0

    def __do_bishop_move(self, fromm, to):
        from_square = self.__get_square_by_algebraic(fromm)
        to_square = self.__get_square_by_algebraic(to)

        from_piece = from_square.get_piece()
        to_piece = to_square.get_piece()

        capture = to_square.get_piece() != ""

        if not self.__square_lies_on_diagonal(from_square, to_square):
            return -1

        if len(self.__get_pieces_on_diagonal(from_square, to_square)) != 0:
            return -1

        to_square.set_piece(from_piece)
        from_square.set_piece("")

        king_square = self.__get_king_square(self._whites_move)
        
        in_check, checking_pieces, pinned_pieces = self.__get_king_threats(king_square, self._whites_move)

        # Check if king would be in check
        if in_check:

            to_square.set_piece(to_piece)
            from_square.set_piece(from_piece)
            return -1

        self._whites_move = not self._whites_move
        
        if self._whites_move:
            self._fullmoves += 1

        if capture:
            self._halfmoves = 0
        else:
            self._halfmoves += 1

        if self._halfmoves == 50:
            return 1

        self._en_passent_target = "-" 

        return 0

    def __do_queen_move(self, fromm, to):
        from_square = self.__get_square_by_algebraic(fromm)
        to_square = self.__get_square_by_algebraic(to)

        from_piece = from_square.get_piece()
        to_piece = to_square.get_piece()

        capture = to_square.get_piece() != ""

        same_row = from_square.get_row() == to_square.get_row()
        same_col = from_square.get_col() == to_square.get_col()

        line = []

        # Check if lies on row, col, or diagonal - if not then illegal
        # Check for obstruction on row, col, or diagonal
        if self.__square_lies_on_diagonal(from_square, to_square):
            line = self.__get_pieces_on_diagonal(from_square, to_square)
        elif same_row:
            line = self.__get_pieces_on_row(from_square, to_square)
        elif same_col:
            line = self.__get_pieces_on_col(from_square, to_square)
        else:
            return -1

        if len(line) != 0:
            return -1

        to_square.set_piece(from_piece)
        from_square.set_piece("")

        king_square = self.__get_king_square(self._whites_move)
        
        in_check, checking_pieces, pinned_pieces = self.__get_king_threats(king_square, self._whites_move)

        # Check if king would be in check
        if in_check:
            to_square.set_piece(to_piece)
            from_square.set_piece(from_piece)
            return -1

        self._whites_move = not self._whites_move
        
        if self._whites_move:
            self._fullmoves += 1

        if capture:
            self._halfmoves = 0
        else:
            self._halfmoves += 1
            
        if self._halfmoves == 50:
            return 1            

        self._en_passent_target = "-" 

        return 0

    def get_FEN(self):
        board = ""
        for i in range(len(self._board)):
            row = self._board[i]
            empty_counter = 0
            for j in range(len(self._board[i])):
                square = self._board[i][j].get_piece()

                if square == "":
                    empty_counter += 1
               
                # Also test more
                if (empty_counter > 0 and square != "") or j == 7:
                    if not (empty_counter == 0): 
                        board += str(empty_counter) 
                        empty_counter = 0
                
                board += square
            board += "/"
        
        board = board[:-1]
        
        move = "w" if self._whites_move else "b"
        
        return f"{board} {move} {self._castling} {self._en_passent_target} {self._halfmoves} {self._fullmoves}"
        
    def get_JSON(self):
        board = ([[self._board[i][j].get_piece() for j in range(len(self._board[i]))] for i in range(len(self._board))])
        move = "w" if self._whites_move else "b"

        return json.dumps({ 
                           'board': board,
                           'whitesMove': move,
                           'castling': self._castling,
                           'enPassentTarget': self._en_passent_target,
                           'halfmoves': self._halfmoves,
                           'fullmoves': self._fullmoves
                           })

    @staticmethod
    def get_position(fen):
        parts = fen.split(" ")

        #print(f"fen is {fen}")

        # Turn board string into 2d array
        rows = parts[0].split("/")
        board = [[Square for i in range(8)] for j in range(8)]

        for row in range(8):
            for col in range(8):
                board[7 - row][col] = Square(chr(97 + col) + str(row + 1))

        for i in range(len(rows)):
            index = 0
            relative_index = 0
    
            while index < len(rows[i]):
                char = rows[i][index]

                if char.isdigit():
                    relative_index += int(char)
                else:
                    board[i][relative_index].set_piece(char)
                    relative_index += 1

                index += 1

        whites_move = parts[1] == "w"

        castling = parts[2]

        en_passent_target = parts[3]

        halfmoves = int(parts[4])

        fullmoves = int(parts[5])

        return Position(board, whites_move, castling, en_passent_target, halfmoves, fullmoves)


class Game():
    def __init__(self, starting_date, starting_time, starting_fen, result = "*", positions = []):
        self._date = starting_date
        self._result = result
        self._time = starting_time
        self._fen = starting_fen

        self._current_pos = Position.get_position(starting_fen)
        self._current_fullmove = 1
        self._positions = positions
        
    def get_starting_date(self):
        return self._date
        
    def get_starting_time(self):
        return self._time

    def ended(self):
        return self._result != "*"

    def get_date_time(self):
        return self._date + "-" + self._time

    # Move in algebraic
    def add_move(self, fromm, to, result_int = 0):
        if self.ended():
            raise Exception("Trying to play move in completed game")

        # Apply move to position
        if result_int == 0:
            result_int = self._current_pos.do_move(fromm, to)
        
        if result_int != -1:
            self._positions.append(self._current_pos.get_FEN())

        if result_int == 1:
            self._result = "1-0" if self._current_pos.is_whites_move() else "0-1"
        elif result_int == 2:
            self._result = "1/2-1/2"
        elif result_int == 3:
            self._result = "0-1" if self._current_pos.is_whites_move() else "1-0"
        
    def get_JSON(self):
        return json.dumps({
                'date': self._date,
                'time': self._time,
                'fen': self._fen,
                'result': self._result,
                'positions': ([self._positions[i] for i in range(len(self._positions))])
            })

    def write_to_file(self, path):
        file = open(path, 'w')
        file.write(self.get_JSON())
        file.close()

    @staticmethod
    def read_from_file(path):
        with open(path, 'r') as file:
            json_object = json.load(file)

            date = json_object['date']
            time = json_object['time']
            fen = json_object['fen']
            result = json_object['result']
            positions = json_object['positions']

            return Game(date, time, fen, result, positions)

    def get_current_pos(self):
        return self._current_pos

