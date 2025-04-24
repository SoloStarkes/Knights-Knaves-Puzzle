from flask import Flask, jsonify, request, send_from_directory
from Puzzle_Generator import PuzzleGenerator
import os

app = Flask(__name__, static_url_path='', static_folder='static')
puzzle_generator = PuzzleGenerator()

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/generate_puzzle')
def generate_puzzle():
    difficulty = request.args.get('difficulty', 'easy')
    
    if difficulty == 'easy':
        puzzle = puzzle_generator.easy()
    elif difficulty == 'medium':
        puzzle = puzzle_generator.medium()
    else:
        puzzle = puzzle_generator.hard()
    
    # Create solver for the puzzle
    from Puzzle_Generator import Solver
    solver = Solver(puzzle)
    solver.solve()
    
    # Format the puzzle data for JSON response
    puzzle_data = {
        'islanders': [i.name for i in puzzle.islanders],
        'statements': [s.full_statement() for s in puzzle.statements],
        'knights': puzzle.knight_names(),
        'knaves': puzzle.knave_names(),
        'reasoning': solver.reasoning
    }
    
    return jsonify(puzzle_data)

if __name__ == '__main__':
    # Create static folder if it doesn't exist
    if not os.path.exists('static'):
        os.makedirs('static')
    app.run(host='0.0.0.0', port=5000) 
