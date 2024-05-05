import os
import requests
import io
from pathlib import Path
from contextlib import contextmanager
import genanki
from typing import NamedTuple

UniqueDeckId = 2478910111517

def get_input_data():
    header_columns = []
    with open('./input/input_data.dsv', mode='r') as file:
        first_line = True
        for line in file:
            columns = line.strip().split("|")
            if first_line:
                first_line = False
                header_columns = columns
                continue
            yield [c.replace('"', "") for c in columns]

def download_mp3(tag: str, url: str, path: Path) -> Path:
    tag_path = path.joinpath(tag)
    if tag_path.exists():
        return tag_path

    response = requests.get(url)
    if response.status_code != 200:
        return None
    
    with open(tag_path, 'wb') as f:
        f.write(response.content)

    return tag_path


class AnkiContext(NamedTuple):
    deck: genanki.Deck
    package: genanki.Package
    model: genanki.Model

@contextmanager
def anki_factory(deck_id: int, deck_name: str) -> tuple[genanki.Deck, genanki.Package]:
    deck = genanki.Deck(deck_id=deck_id, name=deck_name)
    package = genanki.Package(deck)
    model = genanki.Model(
        1091735104,
        name="alphabet",
        fields=[
            {'name': 'Letter'},
            {'name': 'Sound'},
            {'name': 'Audio'},                                  # ADD THIS
        ],
        templates=[
            {
            'name': 'Card 1',
            'qfmt': '{{Letter}}<br>',              # AND THIS
            'afmt': '{{FrontSide}}<hr id="answer">{{Sound}}{{Audio}}',
            },
        ]
    )

    deck.add_model(model)

    yield AnkiContext(deck, package, model)

    output_folder = Path("output")
    output_folder.mkdir(parents=True, exist_ok=True)
    package.write_to_file(str(output_folder.joinpath(f'{deck_name}.apkg')))

def main():
    media_folder = Path("media")
    media_folder.mkdir(parents=True, exist_ok=True)
    media = []
    with anki_factory(UniqueDeckId, 'italian-alphabet') as anki_context:
        for data in get_input_data():
            print(data)
            mp3_file_name = f'{data[0]}-audio.mp3'
            mp3 = download_mp3(mp3_file_name, data[2], media_folder)
            if mp3 is not None:
                media.append(mp3)

            anki_context.deck.add_note(
                genanki.Note(
                    model=anki_context.model,
                    fields=[
                        data[0],
                        data[1].replace('"', ""),
                        mp3_file_name
                    ]
                )
            )
        
        anki_context.package.media_files = [str(m) for m in media]
