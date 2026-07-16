import random
from src.logic.solver import solve, is_valid

def generate_full_board():
    board = [[0 for _ in range(9)] for _ in range(9)]
    fill_diagonal_blocks(board)
    solve(board)
    return board

def fill_diagonal_blocks(board):
    for i in range(0, 9, 3):
        fill_block(board, i, i)

def fill_block(board, row, col):
    nums = list(range(1, 10))
    random.shuffle(nums)
    
    index = 0
    for i in range(3):
        for j in range(3):
            board[row + i][col + j] = nums[index]
            index += 1

def remove_numbers(board, difficulty):
    puzzle = [row[:] for row in board]

    if difficulty == 'easy':
        cells_to_remove = 35
    elif difficulty == 'medium':
        cells_to_remove = 45
    elif difficulty == 'hard':
        cells_to_remove = 55
    else:
        cells_to_remove = 40
    
    all_positions = [(r, c) for r in range(9) for c in range(9)]
    random.shuffle(all_positions)

    removed = 0
    for row, col in all_positions:
        if removed >= cells_to_remove:
            break
        
        backup = puzzle[row][col]
        puzzle[row][col] = 0

        if is_valid(puzzle, backup, (row, col)):
            removed += 1
        else:
            puzzle[row][col] = backup

    return puzzle

def generate_sudoku(difficulty='medium'):
    solution = generate_full_board()
    puzzle = remove_numbers(solution, difficulty)
    return puzzle, solution