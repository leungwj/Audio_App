import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { useState } from "react";
import styles from "../styles/Home.module.css";

function Square({ value, onSquareClick }) {
    // const [value, setValue] = useState(null); // creates a state variable (value) and a function to update it (setValue)
    // useState takes in one argument, the initial value of the state variable

    // value: stores the value, default is null
    // setValue: callable function that updates the value

    return (
        <button
            className="square"
            onClick={onSquareClick}
        >
            {value}
        </button>
    );
}

function Board({ xIsNext, squares, onPlay }) {

    // this function can access vars and functions defined in the outer/parent function (e.g., Board)
    function handleClick(i) {
        if (squares[i] || calculateWinner(squares)) return; // if the square is already filled or the game is over, return early

        const nextSquares = squares.slice(); // copy the squares array instead of modifying the original array, this allows components to compare the current state with the previous state, and determine if the component needs to re-render
        nextSquares[i] = xIsNext ? 'X' : 'O';

        // setSquares(nextSquares); // update the squares array, will re-render the component that use squares sate (board) and its child components because the state has changed
        // setXIsNext(!xIsNext)
        onPlay(nextSquares); // call the onPlay function with the updated squares array
    }

    const winner = calculateWinner(squares); // check if there is a winner
    let status;
    if (winner) {
        status = `Winner: ${winner}`;
    } else {
        status = `Next player: ${xIsNext ? 'X' : 'O'}`;
    }

    return (
        // if you're passing a function as a prop, do not use () as that will call the function immediately
        // anonymous function can be used as a prop instead, which invokes handleClick(0) when the button is clicked.
        <>
            <div className="status">{status}</div>
            <div className="board-row">
                <Square value={squares[0]} onSquareClick={ () => handleClick(0) } />
                <Square value={squares[1]} onSquareClick={ () => handleClick(1) } />
                <Square value={squares[2]} onSquareClick={ () => handleClick(2) } />
            </div>
            <div className="board-row">
                <Square value={squares[3]} onSquareClick={ () => handleClick(3) } />
                <Square value={squares[4]} onSquareClick={ () => handleClick(4) } />
                <Square value={squares[5]} onSquareClick={ () => handleClick(5) } />
            </div>
            <div className="board-row">
                <Square value={squares[6]} onSquareClick={ () => handleClick(6) } />
                <Square value={squares[7]} onSquareClick={ () => handleClick(7) } />
                <Square value={squares[8]} onSquareClick={ () => handleClick(8) } />
            </div>
        </>
    );
}

function calculateWinner(squares) {
    const lines = [
        [0, 1, 2],
        [3, 4, 5],
        [6, 7, 8],
        [0, 3, 6],
        [1, 4, 7],
        [2, 5, 8],
        [0, 4, 8],
        [2, 4, 6],
    ];

    for (let i = 0; i < lines.length; i++) {
        const [a, b, c] = lines[i];
        // check for not null, then check if a === b === c
        if (squares[a] && squares[a] === squares[b] && squares[a] === squares[c]) {
            return squares[a];
        }
    }

    return null;
}

function Game() {
    const [history, setHistory] = useState([Array(9).fill(null)]);
    const [currentMove, setCurrentMove] = useState(0);
    const xIsNext = currentMove % 2 === 0;
    const currentSquares = history[currentMove];

    function handlePlay(nextSquares) { // to update the game
        const nextHistory = [...history.slice(0, currentMove+1), nextSquares]; // creates a new array that contains all the items in history, then append nextSquares
        setHistory(nextHistory); // update the history
        setCurrentMove(nextHistory.length - 1); // update the current move
    }

    function jumpTo(nextMove) {
        setCurrentMove(nextMove);
    }

    // in the tuple, the first element is the array, and the second element is the index
    const moves = history.map((squares, move) => {
        let description;
        if (move > 0) {
            description = `Go to move #${move}`;
        }
        else{
            description = `Go to game start`;
        }

        return (
            <li key={move}>
                <button onClick={() => jumpTo(move)}>{description}</button>
            </li>
        );
    });

    return (
        <div className="game">
            <div className="game-board">
                <Board xIsNext={xIsNext} squares={currentSquares} onPlay={handlePlay} />
            </div>
            <div className="game-info">
                <ol>{moves}</ol>
            </div>
        </div>
    );
}