#!/bin/env python
# NOTE: This file was generated with AI!!
# And thus, is entered into the PUBLIC DOMAIN. As copyright
# does not extend to AI generated works. 



import json
import genanki
import html
import random
import argparse
import os

def load_quiz_data(filepath):
    """Loads the JSON data from a file."""
    print(f"Loading data from {filepath}...")
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: The file '{filepath}' was not found. Skipping.")
        return None
    except json.JSONDecodeError:
        print(f"Error: The file '{filepath}' contains invalid JSON. Skipping.")
        return None

def create_anki_deck(all_data, deck_name="Generated Quiz Deck"):
    """
    Parses a list of JSON data (from potentially multiple files) and creates a genanki Deck.
    """
    if not all_data:
        print("No valid quiz data provided to create a deck.")
        return None

    # 1. Generate unique IDs for the Model and the Deck
    model_id = random.randrange(1 << 30, 1 << 31)
    deck_id = random.randrange(1 << 30, 1 << 31)

    # 2. Define the Card Model (HTML/CSS structure)
    # The 'Question' field will now contain the question + all options for MC.
    # The 'Answer' field will contain the correct answer(s).
    # The 'ExtraInfo' is for the question type.
    my_model = genanki.Model(
        model_id,
        'Question with Options and Answer',
        fields=[
            {'name': 'Question'},
            {'name': 'Answer'},
            {'name': 'ExtraInfo'},
        ],
        templates=[
            {
                'name': 'Card 1',
                'qfmt': '<div class="question">{{Question}}</div><br><div class="type">({{ExtraInfo}})</div>',
                'afmt': '{{FrontSide}}<hr id="answer"><div class="answer_label">Correct Answer:</div><div class="answer_content">{{Answer}}</div>',
            },
        ],
        css="""
        .card {
            font-family: arial;
            font-size: 20px;
            text-align: center;
            color: black;
            background-color: white;
        }
        .question { font-weight: bold; }
        .type { font-size: 14px; color: #666; font-style: italic; }
        .options-list {
            list-style: none; /* Remove bullet points */
            padding: 0;
            margin-top: 15px;
            text-align: left;
            display: inline-block; /* Center the list itself */
        }
        .options-list li {
            margin-bottom: 5px;
            padding: 5px;
            border: 1px solid #eee;
            border-radius: 3px;
            background-color: #f9f9f9;
        }
        .answer_label {
            font-weight: bold;
            color: #008000; /* Green for correct answer label */
            margin-top: 10px;
        }
        .answer_content {
            color: #000080; /* Blue for the actual answer text */
            font-size: 22px;
            font-weight: bold;
        }
        """
    )

    # 3. Create the Deck
    my_deck = genanki.Deck(deck_id, deck_name)

    # 4. Iterate through questions and add them to the deck
    num_cards_added = 0
    for item in all_data:
        original_question_html = item.get('question_text', '')
        q_type_raw = item.get('question_type', '')
        answers = item.get('answers', [])

        # Find the correct answer(s) text
        correct_answer_texts = [ans['text'] for ans in answers if ans.get('is_correct')]

        if not correct_answer_texts:
            # print(f"Skipping question ID {item.get('id')}: No correct answer found.")
            continue # Skip to the next question if no correct answer

        formatted_answer_for_back = "<br>".join(correct_answer_texts)
        
        # Prepare the question for the front of the card
        question_for_front = original_question_html
        q_type_label = ""

        if q_type_raw == 'multiple_choice_question':
            q_type_label = "Multiple Choice"
            # Add all options to the question text for display on the front
            options_html = '<ul class="options-list">'
            for i, ans_option in enumerate(answers):
                options_html += f'<li>{chr(65 + i)}. {ans_option["text"]}</li>' # A, B, C...
            options_html += '</ul>'
            question_for_front += options_html
        elif q_type_raw == 'true_false_question':
            q_type_label = "True / False"
            # For True/False, we might want to explicitly show "True" and "False" as options
            # Or just rely on the question text and the explicit answer.
            # For now, let's keep it simple and just display the question and the type.
            # If you want explicit T/F options, we can add them here.
        else:
            q_type_label = "Question"

        note = genanki.Note(
            model=my_model,
            fields=[question_for_front, formatted_answer_for_back, q_type_label]
        )
        my_deck.add_note(note)
        num_cards_added += 1

    print(f"Added {num_cards_added} cards to the deck.")
    return my_deck

def main():
    parser = argparse.ArgumentParser(
        description="Generate Anki decks from one or more JSON quiz files."
    )
    parser.add_argument(
        'input_files',
        metavar='FILE',
        type=str,
        nargs='+', # This indicates one or more file arguments
        help='Path(s) to the JSON quiz file(s).'
    )
    parser.add_argument(
        '-o', '--output',
        metavar='OUTPUT_FILE',
        type=str,
        default='generated_anki_deck.apkg',
        help='Name of the output Anki package file (.apkg).'
    )
    parser.add_argument(
        '-d', '--deck-name',
        metavar='DECK_NAME',
        type=str,
        default='Generated Quiz Deck',
        help='Name of the Anki deck to be created.'
    )

    args = parser.parse_args()

    all_quiz_data = []
    for filepath in args.input_files:
        data = load_quiz_data(filepath)
        if data:
            all_quiz_data.extend(data)

    if all_quiz_data:
        print(f"\nCreating Anki deck '{args.deck_name}'...")
        deck = create_anki_deck(all_quiz_data, deck_name=args.deck_name)
        
        if deck:
            genanki.Package(deck).write_to_file(args.output)
            print(f"Successfully created '{args.output}'.")
        else:
            print("Failed to create Anki deck.")
    else:
        print("No valid data found across all input files. No Anki deck generated.")

if __name__ == "__main__":
    main()
