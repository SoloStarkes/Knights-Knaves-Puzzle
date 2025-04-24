from flask import Flask, jsonify, request, render_template
from Puzzle_Generator import PuzzleGenerator, Solver
import os

app = Flask(__name__, static_url_path='/static', static_folder='static', template_folder='templates')
puzzle_generator = PuzzleGenerator()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_puzzle')
def generate_puzzle():
    difficulty = request.args.get('difficulty', 'easy')
    
    if difficulty == 'easy':
        puzzle = puzzle_generator.easy()
    elif difficulty == 'medium':
        puzzle = puzzle_generator.medium()
    else:
        puzzle = puzzle_generator.hard()
    
    solver = Solver(puzzle)
    solver.solve()
    
    puzzle_data = {
        'islanders': [i.name for i in puzzle.islanders],
        'statements': [s.full_statement() for s in puzzle.statements],
        'knights': puzzle.knight_names(),
        'knaves': puzzle.knave_names(),
        'reasoning': solver.reasoning
    }
    
    return jsonify(puzzle_data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
