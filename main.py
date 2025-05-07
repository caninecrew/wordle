from src.game import WordleGame
from src.word_list import WordList
import random

def find_word():
    """
    Function to find a word from the word list.
    """

    word_list = WordList()
    with open("data/words.txt", "r") as file:
        for line in file:
            word_list.append(line.strip())

    return random.choice(word_list)  # Randomly select a word from the list and return it

def play_game():
    """
    Main function to play the Wordle game.
    """
    game = WordleGame(find_word())  # Initialize the game with a word

    print("Welcome to Wordle!")
    print("You have 6 attempts to guess the word.")
    print(f"The word is {len(game.word)} letters long. Good luck!")
    print("Type 'exit' to quit the game at any time.")
    print()
    print("After each guess, you'll see:")
    print("[A] - Correct letter in the correct position")
    print("(A) - Correct letter in the wrong position")
    print("A - Letter not in word")

    while not game.game_over:
        guess = input("\nEnter your guess: ").strip() # Get user input and strip whitespace

        is_valid, result, game_over = game.make_guess(guess) # Make a guess and get the result

        if not is_valid:
            print("Invalid guess. Please try again.")
            continue

        game.display_guess(result) # Display the result of the guess

        if game_over:
            if result[0][1] == 'correct':
                print(f"\nCongratulations! You've guessed the word '{game.word}'!")
            else:
                print(f"\nGame over! The correct word was '{game.word}'. Better luck next time!")

if __name__ == "__main__":
    play_game()  # Start the game when the script is run directly

