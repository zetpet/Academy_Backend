"""
This main module contain realization Hangman game.
The game reads a list of words from a file, select random word,
and allow the user to guess the word letter by letter.
"""
import os
import random
from functools import wraps
from pathlib import Path
from typing import Any, Callable, Protocol

from dotenv import load_dotenv

load_dotenv()
attempts_left = int(os.getenv("ATTEMPTS_LEFT") or 10)

current_file_path = Path(__file__)
words_file_path = current_file_path.with_name("words.txt")


class CallableWithCalls(Protocol):
    """Protocol for objects called as functions, with an additional 'calls' attribute"""

    def __call__(self, *args: Any, **kwds: Any) -> tuple[list[str], int]:  # type: ignore
        calls: int


def profiler(func: Callable[..., Any]) -> CallableWithCalls:
    """Decorator to count the number of calls to the function

    :param func: callable

    :returns: callable: The decorated function

    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> tuple[list[str], int]:
        """Wrapper function increments the call count and calls the original

        :param args: Variable length argument list
        :param kwargs: Arbitrary keyword arguments

        :returns: Tuple[List[str], int]: Result of the original function

        """
        wrapper.calls += 1  # type: ignore
        return func(*args, **kwargs)

    wrapper.calls = 0  # type: ignore
    return wrapper


class WordStorage:
    """Class for storing words

    :param file_path: The path to the file from which words are loaded

    :attribute words: List of words loaded from the given file path

    :method load_words: Loads and returns a list of words from the given file path
    :method get_random_word: Returns a randomly selected word from the list of words

    """

    def __init__(self, file_path: Path) -> None:
        self.words = self.load_words(file_path)

    def load_words(self, file_path: Path) -> list[str]:
        """Load words from the provided file path

        :param file_path: Path to the file containing words
        :returns: List of words from the file
        """
        return [line.strip() for line in file_path.read_text(encoding="utf-8").splitlines()]

    def get_random_word(self) -> str:
        """Fetch a random word from the stored words

        :returns: A random word
        """
        return random.choice(self.words)


class User:
    """Class for user actions

    :method get_info: Fetches and returns user input
    :method send_message: Prints the given message to the console

    """

    @staticmethod
    def get_info() -> str:
        """Fetch a character input from the user

        :returns: The input character from the user
        """
        char = input("guess a character: ").strip()
        if len(char) != 1 or not char.isalpha():
            raise ValueError("Pls enter single char")
        return char.lower()

    @staticmethod
    def send_message(message: str) -> None:
        """Display a message to the user

        :param message: The message to be displayed

        """
        print(message)


class Game:
    """Class representing the Hangman game's logic and flow

    :param word_base: An instance of WordStorage class
    :param user_story: An instance of User class
    :param attempts: The number of initial attempts allowed for the player

    :attribute word: Random word selected for the game
    :attribute current_word: List representing the current state of the word being guessed
    :attribute attempts_left: Number of attempts left for the user
    :attribute user_story: Instance of User class to manage user interactions

    :method play: Starts and manages the game until the word is guessed or no attempts remain
    :method make_guesses: Processes the user's guess and updates the game state

    """

    def __init__(self, word_base: WordStorage, user_story: User, attempts: int) -> None:
        self.word = word_base.get_random_word()
        self.current_word = ["_" for _ in range(len(self.word))]
        self.attempts_left = attempts
        self.user_story = user_story

    def play(self) -> None:
        """Begin the game and manage the game flow"""
        self.user_story.send_message("Start guessing...")
        while self.attempts_left > 0 and "_" in self.current_word:
            self.user_story.send_message(" ".join(self.current_word))
            try:
                char = self.user_story.get_info()
                self.make_guesses(char)
            except ValueError as error:
                self.user_story.send_message(str(error))

            if "_" not in self.current_word:
                self.user_story.send_message(f"The word was: {self.word}\nYou won")
                break

            if self.attempts_left == 0:
                self.user_story.send_message("You lost")
                break
        self.user_story.send_message(f"Game took {Game.make_guesses.calls} steps")  # type: ignore

    @profiler
    def make_guesses(self, char: str) -> None:
        """Process the user's guess and update the game state

        If the guessed character is in the word, update the current_word representation
        Otherwise, decrement the number of attempts left and notify the user

        :param char: The character guessed by the user
        """
        if char in self.word:
            for index, letter in enumerate(self.word):
                if letter == char:
                    self.current_word[index] = char
        else:
            self.attempts_left -= 1
            self.user_story.send_message(f"You have {self.attempts_left} more guesses")


if __name__ == "__main__":
    word_repo = WordStorage(words_file_path)
    user = User()
    game = Game(word_repo, user, attempts_left)
    game.play()
