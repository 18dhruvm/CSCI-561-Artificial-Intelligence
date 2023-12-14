import os
import copy
import time
import random
import time
START=time.time()

# Global Variable
INPUT_FILENAME = 'input.txt'
OUTPUT_FILENAME = 'output.txt'
BOARD_SIZE = 5
TIME_LIMIT=8.4
available_spaces=0
stepfile='stepfile.txt'
s=0

def write_steps():
    step_count=0
    try:
        with open(stepfile,'r') as file:
            step_count=int(file.read())
    except FileNotFoundError:
        with open(stepfile,'w') as file:
            file.write(str(0))
        step_count=1

    finally:
        step_count+=1
        with open(stepfile,'w') as file:
            file.write(str(step_count))
        if step_count==13:
            os.remove(stepfile)
        return step_count
        

# Function to read input file

def input_file_read():
  with open(INPUT_FILENAME, 'r') as F:
    my_colour = int(F.readline())

    previous_state = []
    for _ in range(BOARD_SIZE):
      row = F.readline().strip()
      row_values = [int(pos) for pos in row]
      previous_state.append(row_values)

    current_state = []
    for _ in range(BOARD_SIZE):
      row = F.readline().strip()
      row_values = [int(pos) for pos in row]
      current_state.append(row_values)

  return my_colour, previous_state, current_state

# Function to find neighbours

def neighbours(row,col):

  return [(r, c) for r, c in [(row - 1, col), (row + 1, col), (row, col - 1), (row, col + 1)]
          if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE]

# Function to create allies and check correctness

def detect_neighbor_ally(board,row,col):

  neighbors = neighbours(row,col)  # Detect neighbors
  group_allies = []
  for piece in neighbors:
    # Add to allies list if having the same color
    if board[piece[0]][piece[1]] == board[row][col]:
        group_allies.append(piece)
  return group_allies

def ally_dfs(current_state,i,j):
  stack = [(i, j)]  # stack for DFS serach
  ally_members = []  # record allies positions during the search
  while stack:
      piece = stack.pop()
      ally_members.append(piece)
      neighbor_allies = detect_neighbor_ally(current_state,piece[0], piece[1])
      for ally in neighbor_allies:
          if ally not in stack and ally not in ally_members:
              stack.append(ally)
  return ally_members

def check_Libs(current_state, row, col, stone_type):
  ally_members = ally_dfs(current_state,row,col)
  for member in ally_members:
    neighbors = neighbours(member[0], member[1])
    for piece in neighbors:
        # If there is empty space around a piece, it has liberty
        if current_state[piece[0]][piece[1]] == 0:
            return True
  # If none of the pieces in a allied group has an empty space, it has no liberty
  return False

# Function to check empty spaces or "0"

def empty_Spaces(current_state):
  empty_spaces = []
  for i in range(BOARD_SIZE):
    for j in range(BOARD_SIZE):
      if current_state[i][j] == 0:
        empty_spaces.append((i,j))

  return empty_spaces

# All liberties of every possible move

def all_Liberties(current_state, stone_colour):
  l=[]

  for i,j in empty_Spaces(current_state):
    copy4=copy.deepcopy(current_state)
    copy4[i][j] = stone_colour
    if check_Libs(copy4,i,j,stone_colour):
      l.append((i,j))

  return l

# Remove dead pieces

def find_died_pieces(current_state, piece_type):
    died_pieces = []

    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            # Check if there is a piece at this position:
            if current_state[i][j] == piece_type:
                # The piece die if it has no liberty
                if not check_Libs(current_state,i, j,piece_type):
                    died_pieces.append((i,j))
    return died_pieces

def remove_died_pieces(current_state, piece_type):
    died_pieces = find_died_pieces(current_state,piece_type)
    died_len= len(died_pieces)
    for piece in died_pieces:
        current_state[piece[0]][piece[1]] = 0

    return current_state,died_len

#Check KO situation

def KO_situation(previous_state,current_state):
  if empty_Spaces(current_state)==25:
    return False
  for i in range(BOARD_SIZE):
    for j in range(BOARD_SIZE):
      if previous_state[i][j] != current_state[i][j]:
        return False

  return True

# Function to find legal moves and avoid KO situation

def legal_Moves(current_state,previous_state,stone_colour):
  legal_moves=[]


  for (a,b) in empty_Spaces(current_state):
    copy1 = copy.deepcopy(current_state)
    copy1[a][b] = stone_colour
    copy2 = copy.deepcopy(copy1)
    copy1,d_score = remove_died_pieces(copy1, 3-stone_colour)
    liberties = check_Libs(copy1, a, b, stone_colour)
    if not liberties:
      copy1,d_score = remove_died_pieces(copy1, 3-stone_colour)
      liberties = check_Libs(copy1, a, b, stone_colour)
    if liberties:
      if KO_situation(previous_state, copy1):
        continue
      else:
        legal_moves.append((a,b))

  return legal_moves
'''
def remove_died_groups(current_state, piece_type):
    groups = []

    def dfs(row, col, group):
        group.add((row, col))
        for neighbor_row, neighbor_col in neighbours(row, col):
            if current_state[neighbor_row][neighbor_col] == piece_type and (neighbor_row, neighbor_col) not in group:
                dfs(neighbor_row, neighbor_col, group)

    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            if current_state[row][col] == piece_type:
                group = set()
                dfs(row, col, group)
                if not any(check_Libs(current_state, r, c, piece_type) for r, c in group):
                    groups.append(group)

    for group in groups:
        for row, col in group:
            current_state[row][col] = 0

    return current_state,len(groups)

# Updated function to check for capturing moves
def legal_Moves(current_state, previous_state, stone_colour):
    legal_moves = []

    for (a, b) in empty_Spaces(current_state):
        copy1 = copy.deepcopy(current_state)
        copy1[a][b] = stone_colour
        copy2 = copy.deepcopy(copy1)
        liberties = check_Libs(copy1, a, b, stone_colour)
        if not liberties:
            copy1,_ = remove_died_groups(copy1, 3 - stone_colour)
            liberties = check_Libs(copy1, a, b, stone_colour)
        if liberties:
            if KO_situation(previous_state, copy1):
                continue
            else:
                legal_moves.append((a, b))

    return legal_moves
'''
# Function to make a move

def next_Move(current_state, stone_colour, place):
  copy3 = copy.deepcopy(current_state)
  copy3[place[0]][place[1]] = stone_colour

  return copy3

# Function to evaluate move and give score
'''

def score(current_state, player,a):

  p1,p2,hp1,hp2 = 0,0,0,0
  for i in range(BOARD_SIZE):
    for j in range(BOARD_SIZE):
      if current_state[i][j]==player:
        p1 = p1 + 1
      elif current_state[i][j]==3-player:
        p2 = p2 + 1

  hp1 = len(all_Liberties(current_state,player))
  hp2 = len(all_Liberties(current_state,3-player))
    
  my_points = (p1+1*hp1) - (p2+1*hp2)# last submitted with 2hp1 1,0.9,0.45 try -a
  
  if my_color==player:
    return my_points

  else:
    return -my_points


'''
def calculate_euler_number(current_state, player):
    # Initialize counters for player and opponent patterns
    q1_side, q2_side, q3_side = 0, 0, 0
    q1_opponent_side, q2_opponent_side, q3_opponent_side = 0, 0, 0

    # Create a modified board with a border to simplify calculations
    modified_board = [[0] * (BOARD_SIZE + 2) for _ in range(BOARD_SIZE + 2)]
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            modified_board[i + 1][j + 1] = current_state[i][j]

    # Define patterns for player (side) and opponent
    player_stone = player
    opponent_stone = 3 - player
    patterns = {
        "Q1": [(player_stone, 0), (0, 0), (0, player_stone)],
        "Q2": [(player_stone, player_stone), (0, 0)],
        "Q3": [(player_stone, opponent_stone), (opponent_stone, player_stone)]
    }

    # Iterate over 2x2 subgrids on the modified board
    for i in range(1, BOARD_SIZE + 1):
        for j in range(1, BOARD_SIZE + 1):
            for pattern in patterns:
                match = True
                for x in range(2):
                    for y in range(2):
                        if modified_board[i + x][j + y] != patterns[pattern][x][y]:
                            match = False
                            break
                if match:
                    if pattern == "Q1":
                        q1_side += 1
                    elif pattern == "Q2":
                        q2_side += 1
                    elif pattern == "Q3":
                        q3_side += 1

    # Repeat the pattern matching for the opponent's stones
    for i in range(1, BOARD_SIZE + 1):
        for j in range(1, BOARD_SIZE + 1):
            for pattern in patterns:
                match = True
                for x in range(2):
                    for y in range(2):
                        if modified_board[i + x][j + y] != patterns[pattern][x][y]:
                            match = False
                            break
                if match:
                    if pattern == "Q1":
                        q1_opponent_side += 1
                    elif pattern == "Q2":
                        q2_opponent_side += 1
                    elif pattern == "Q3":
                        q3_opponent_side += 1

    # Calculate Euler number
    euler_number = ((q1_side - q3_side + 2 * q2_side) - (q1_opponent_side - q3_opponent_side + 2 * q2_opponent_side)) / 4

    return euler_number

# Update your existing score function to include Euler number
def score(current_state, player,a):
    p1, p2, hp1, hp2 = 0, 0, 0, 0
    cen_un=0
    edge_stones=0
    
    for i in range(BOARD_SIZE):
        for j in range(BOARD_SIZE):
            if current_state[i][j] == player:
                p1 += 1
                if (i==0 or i==5) and (j==5 or j==0):
                    edge_stones+=1
            elif current_state[i][j] == 3 - player:
                p2 += 1
            elif current_state[i][j] == 0 and 0<i<5 and 0<j<5:
                cen_un+=1
                
    
    hp1 = len(all_Liberties(current_state, player))
    hp2 = len(all_Liberties(current_state, 3 - player))
    
    # Calculate the Euler number
    euler = calculate_euler_number(current_state, player)
    my_points= min(max((hp1 - hp2), -8), 8) -4*euler + 5*(p1-p2) -9*edge_stones*(cen_un/9)
    my_points*=1
    '''
    if s<7:
        my_points = (1*p1 + 1 * hp1) - 1*(p2 + 1 * hp2) + 2*euler
    else:
        my_points = (1*p1 + 1 * hp1) - 1*(p2 + 1 * hp2) + 2*euler
    '''

    if my_color == player:
        if player+1==3:
            return my_points #- 2
        return my_points
    
    else:
        if player+1==3:
            return -my_points -3
        return -my_points



# MiniMax with alpha-beta pruning

def alpha_beta_maximize(current_state, previous_state, n, alpha, beta, stone_colour, START2,b):
    
  if n == 0 or time.time()-START2>=TIME_LIMIT:
    return score(current_state, stone_colour,b), None

  legal_possible_moves = legal_Moves(current_state, previous_state, stone_colour)
  random.shuffle(legal_possible_moves)

  if not legal_possible_moves:
    return 0, ['PASS']

  v =  -1000
  current_best_move = None

  for move in legal_possible_moves:
    next_state = next_Move(current_state, stone_colour, move)
    next_state, died_max = remove_died_pieces(next_state, 3 - stone_colour)
    abs_score = alpha_beta_minimize(next_state, current_state, n - 1, alpha, beta, 3 - stone_colour, START,died_max)
    if v < abs_score[0]:
      v = abs_score[0]
      alpha = max(alpha, v)
      current_best_move = [move]
    if alpha >= beta:
      break

  if current_best_move is None:
    return v, None

  return v, current_best_move

def alpha_beta_minimize(current_state, previous_state, n, alpha, beta, stone_colour,START4,c):

  if n == 0 or time.time()-START4>=TIME_LIMIT:
    return score(current_state, stone_colour,c), None

  legal_possible_moves = legal_Moves (current_state, previous_state, stone_colour)
  random.shuffle(legal_possible_moves)

  if not legal_possible_moves:
    return 0, ['PASS']

  v = 1000
  current_best_move = None

  for move in legal_possible_moves:
    next_state = next_Move(current_state, stone_colour, move)
    next_state, died_min = remove_died_pieces(next_state, 3 - stone_colour)
    abs_score = alpha_beta_maximize(next_state, current_state, n - 1, alpha, beta, 3 - stone_colour,START,died_min)
    if v > abs_score[0]:
      v = abs_score[0]
      beta = min(beta, v)
      current_best_move = [move]
    if alpha >= beta:
      break

  if current_best_move is None:
    return v, None

  return v, current_best_move


def alpha_beta_search(current_state, previous_state, n, alpha, beta, stone_colour, maximizing_player):
  if maximizing_player:
    
    return alpha_beta_maximize(current_state, previous_state, n, alpha, beta, stone_colour,START,0)
  else:
      return alpha_beta_minimize(current_state, previous_state, n, alpha, beta, stone_colour,START,0)

# Play the move according to alpha beta

def my_Chance(current_state,previous_state,stone_colour):

  my_move=[]
  
  #available_spaces = len(empty_Spaces(current_state)) #submitted
  available_spaces = len(legal_Moves(current_state, previous_state, stone_colour))
  if available_spaces==BOARD_SIZE*BOARD_SIZE and stone_colour==1:
    my_move.append((2,2))
  elif available_spaces==BOARD_SIZE*BOARD_SIZE - 1 and stone_colour==2:
    if current_state[2][2] == 0:
      my_move.append((2,2))
    else:
      my_move.append(random.choice(neighbours(BOARD_SIZE//2,BOARD_SIZE//2)))

  else:
    #my_move.append(alpha_beta_search(current_state,previous_state,4,-1000,1000,stone_colour,True)[1][0])
    
    if s<6:# and available_spaces >=20:
        #print("3")
        my_move.append(alpha_beta_search(current_state,previous_state,4,-1000,1000,stone_colour,True)[1][0])
    
    elif  10>s>=6 :#and 20>available_spaces >=14:    
        #print("4")
        my_move.append(alpha_beta_search(current_state,previous_state,4,-1000,1000,stone_colour,True)[1][0])
    elif  12>s>=10 :
        #print("6")
        my_move.append(alpha_beta_search(current_state,previous_state,2,-1000,1000,stone_colour,True)[1][0]) 
    else:
        my_move.append(alpha_beta_search(current_state,previous_state,1,-1000,1000,stone_colour,True)[1][0]) 
    '''
    elif 14>available_spaces >=8:
        #print("5")
        my_move.append(alpha_beta_search(current_state,previous_state,4,-1000,1000,stone_colour,True)[1][0]) 
    '''
    
    
  return my_move

# Function to write output file

def output_file_write(my_move):
  with open(OUTPUT_FILENAME, 'w') as F:
    if my_move=="PASS":
      F.write(my_move)
    else:
      F.write(str(my_move[0]) + "," + str(my_move[1]))

# Main

my_color, previous_state, current_state = input_file_read()
out = my_Chance(current_state, previous_state, my_color)[0]
s=write_steps()
print(s)
output_file_write(out)