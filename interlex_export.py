#!/usr/bin/env python
from io          import StringIO
from collections import namedtuple
from itertools   import chain
from argparse    import ArgumentParser
import csv

from construct import Struct, Array, OptionalGreedyRange, PascalString, ULInt8, ULInt16, ULInt32, SLInt32, Enum, Terminator

InterlexEntry = namedtuple('InterlexEntry', [
    'word',
    'part_of_speech',
    'notes',
    'translation',
    'counter',
    'penalty_points',
    'file_description',
])

InterlexMetadata = namedtuple('InterlexMetadata', [
    'input_file_path',
    'program_and_version',
    'description',
    'author',
    'comments',
    'foreign_language_id',
    'foreign_language_name',
    'foreign_language_variety',
    'native_language_id',
    'native_language_name',
    'native_language_variety',
    'word_count',
    'questions_attempted',
    'questions_answered_correctly',
])

LanguageInfo = namedtuple('LanguageInfo', [
    'name',
    'variety',
    'codepage',
])

# TODO: Allow selecting the dialect and the delimiter on the command line
CSV_DIALECT   = 'excel'
CSV_DELIMITER = ','

# TODO: Allow selecting metadata encoding on the command line.
# I think it's user's current system codepage but I'm not sure.
METADATA_ENCODING = 'windows-1250'

# TODO: The list is not exhaustive. Interlex supports more. Add them.
# These are just the CP-1250 and CP-1252 languages.
# Code page numbers taken from http://www.science.co.il/Language/Locale-codes.asp
LANGUAGES = {
    1078:  LanguageInfo('Afrikaans',  None,                 'windows-1252'),
    1052:  LanguageInfo('Albanian',   None,                 'windows-1250'),
    1069:  LanguageInfo('Basque',     None,                 'windows-1252'),
    1027:  LanguageInfo('Catalan',    None,                 'windows-1252'),
    1050:  LanguageInfo('Croatian',   None,                 'windows-1250'),
    1029:  LanguageInfo('Czech',      None,                 'windows-1250'),
    1030:  LanguageInfo('Danish',     None,                 'windows-1252'),
    2067:  LanguageInfo('Dutch',      'Belgian',            'windows-1252'),
    1043:  LanguageInfo('Dutch',      'Standard',           'windows-1252'),
    3081:  LanguageInfo('English',    'Australian',         'windows-1252'),
    4105:  LanguageInfo('English',    'Canadian',           'windows-1252'),
    9225:  LanguageInfo('English',    'Caribbean',          'windows-1252'),
    6153:  LanguageInfo('English',    'Ireland',            'windows-1252'),
    8201:  LanguageInfo('English',    'Jamaica',            'windows-1252'),
    5129:  LanguageInfo('English',    'New Zealand',        'windows-1252'),
    7177:  LanguageInfo('English',    'South Africa',       'windows-1252'),
    2057:  LanguageInfo('English',    'United Kingdom',     'windows-1252'),
    1033:  LanguageInfo('English',    'United States',      'windows-1252'),
    1035:  LanguageInfo('Finnish',    None,                 'windows-1252'),
    2060:  LanguageInfo('French',     'Belgian',            'windows-1252'),
    3084:  LanguageInfo('French',     'Candadian',          'windows-1252'),
    5132:  LanguageInfo('French',     'Luxembourg',         'windows-1252'),
    1036:  LanguageInfo('French',     'Standard',           'windows-1252'),
    4108:  LanguageInfo('French',     'Swiss',              'windows-1252'),
    3079:  LanguageInfo('German',     'Austrian',           'windows-1252'),
    5127:  LanguageInfo('German',     'Liechtenstein',      'windows-1252'),
    4103:  LanguageInfo('German',     'Luxembourg',         'windows-1252'),
    1031:  LanguageInfo('German',     'Standard',           'windows-1252'),
    2055:  LanguageInfo('German',     'Swiss',              'windows-1252'),
    1038:  LanguageInfo('Hungarian',  None,                 'windows-1250'),
    1039:  LanguageInfo('Icelandic',  None,                 'windows-1252'),
    1057:  LanguageInfo('Indonesian', None,                 'windows-1252'),
    1040:  LanguageInfo('Italian',    'Standard',           'windows-1252'),
    2064:  LanguageInfo('Italian',    'Swiss',              'windows-1252'),
    1044:  LanguageInfo('Norwegian',  'Bokmal',             'windows-1252'),
    2068:  LanguageInfo('Norwegian',  'Nynorsk',            'windows-1252'),
    1045:  LanguageInfo('Polish',     None,                 'windows-1250'),
    1046:  LanguageInfo('Portugese',  'Brazilian',          'windows-1252'),
    2070:  LanguageInfo('Portugese',  'Standard',           'windows-1252'),
    1048:  LanguageInfo('Romanian',   None,                 'windows-1250'),
    2074:  LanguageInfo('Serbian',    'Latin',              'windows-1250'),
    1051:  LanguageInfo('Slovak',     None,                 'windows-1250'),
    1060:  LanguageInfo('Slovenian',  None,                 'windows-1250'),
    11274: LanguageInfo('Spanish',    'Argentina',          'windows-1252'),
    16394: LanguageInfo('Spanish',    'Bolivia',            'windows-1252'),
    13322: LanguageInfo('Spanish',    'Chile',              'windows-1252'),
    9226:  LanguageInfo('Spanish',    'Colombia',           'windows-1252'),
    5130:  LanguageInfo('Spanish',    'Costa Rica',         'windows-1252'),
    7178:  LanguageInfo('Spanish',    'Dominican Republic', 'windows-1252'),
    12298: LanguageInfo('Spanish',    'Ecuador',            'windows-1252'),
    17418: LanguageInfo('Spanish',    'El Salvador',        'windows-1252'),
    4106:  LanguageInfo('Spanish',    'Guatemala',          'windows-1252'),
    18442: LanguageInfo('Spanish',    'Honduras',           'windows-1252'),
    3082:  LanguageInfo('Spanish',    'International Sort', 'windows-1252'),
    2058:  LanguageInfo('Spanish',    'Mexico',             'windows-1252'),
    19466: LanguageInfo('Spanish',    'Nicaragua',          'windows-1252'),
    6154:  LanguageInfo('Spanish',    'Panama',             'windows-1252'),
    15370: LanguageInfo('Spanish',    'Paraguay',           'windows-1252'),
    10250: LanguageInfo('Spanish',    'Peru',               'windows-1252'),
    20490: LanguageInfo('Spanish',    'Puerto Rico',        'windows-1252'),
    1034:  LanguageInfo('Spanish',    'Traditional Sort',   'windows-1252'),
    14346: LanguageInfo('Spanish',    'Uruguay',            'windows-1252'),
    8202:  LanguageInfo('Spanish',    'Venezuela',          'windows-1252'),
    1053:  LanguageInfo('Swedish',    None,                 'windows-1252'),
}
assert len(set(LANGUAGES.values())) == len(LANGUAGES.values())

def build_interlex_format():
    return Struct('interlex23',
        PascalString('program_and_version', length_field = ULInt8('length')),
        ULInt16('foreign_language_id'),
        ULInt16('native_language_id'),
        ULInt32('questions_attempted'),
        ULInt32('questions_answered_correctly'),
        PascalString('description', length_field = ULInt16('length')),
        PascalString('author',      length_field = ULInt16('length')),
        PascalString('comments',    length_field = ULInt16('length')),
        # I have no idea what this is. It was always all zeros in my tests.
        Array(10, ULInt8('unknown')),
        ULInt32('word_count'),
        Array(
            lambda ctx: ctx.word_count,
            Struct('entry',
                PascalString('word',           length_field = ULInt16('length')),
                PascalString('part_of_speech', length_field = ULInt16('length')),
                PascalString('notes',          length_field = ULInt16('length')),
                PascalString('translation',    length_field = ULInt16('length')),
                # Every time a word gets tested, this field is set to the last value of the counter and the counter
                # is incremented. I think the purpose is to store the order in which the questions were last asked.
                # Suprisingly, the value of the counter is remembered if you restart the program - it's not the highest
                # of the values assigned to words.
                # It's size is at least 2 bytes. It's most likely a 32-bit int.
                SLInt32('counter'),
                # I have never seen value other than zero in this field. It being a 32-bit int is just my guess.
                SLInt32('unknown'),
                # -1 seems to indicate that the word has been learnt (displayed as greyed out in the UI)
                SLInt32('penalty_points'),
            ),
        ),
        Terminator,
    )

def parse(input_file_path, file_format):
    with open(input_file_path, 'rb') as input_file:
        return file_format.parse(input_file.read())

def prepare_data_for_export(input_file_path, parsed_file):
    metadata = InterlexMetadata(
        input_file_path              = input_file_path,
        program_and_version          = parsed_file.program_and_version.decode(METADATA_ENCODING),
        description                  = parsed_file.description.decode(METADATA_ENCODING),
        author                       = parsed_file.author.decode(METADATA_ENCODING),
        comments                     = parsed_file.comments.decode(METADATA_ENCODING),
        foreign_language_id          = parsed_file.foreign_language_id,
        foreign_language_name        = LANGUAGES[parsed_file.foreign_language_id].name,
        foreign_language_variety     = LANGUAGES[parsed_file.foreign_language_id].variety,
        native_language_id           = parsed_file.native_language_id,
        native_language_name         = LANGUAGES[parsed_file.native_language_id].name,
        native_language_variety      = LANGUAGES[parsed_file.native_language_id].variety,
        word_count                   = parsed_file.word_count,
        questions_attempted          = parsed_file.questions_attempted,
        questions_answered_correctly = parsed_file.questions_answered_correctly,
    )

    foreign_encoding = LANGUAGES[parsed_file.native_language_id].codepage
    native_encoding  = LANGUAGES[parsed_file.native_language_id].codepage

    entries = [
        InterlexEntry(
            word             = entry.word.decode(foreign_encoding),
            part_of_speech   = entry.part_of_speech.decode(native_encoding),
            notes            = entry.notes.decode(native_encoding),
            translation      = entry.translation.decode(native_encoding),
            counter          = entry.counter,
            penalty_points   = entry.penalty_points,
            file_description = metadata.description,
        )
        for entry in parsed_file.entry
    ]

    return (metadata, entries)

def print_metadata(metadata):
    def language_label(language, variety):
        if variety is None:
            return language

        return '{} ({})'.format(language, variety)

    print("File:                  {} ({})".format(metadata.input_file_path, metadata.program_and_version))
    print("Description:           {}".format(metadata.description))
    print("Author:                {}".format(metadata.author))
    print("Foreign language:      {}".format(language_label(metadata.foreign_language_name, metadata.foreign_language_variety)))
    print("Native language:       {}".format(language_label(metadata.native_language_name, metadata.native_language_variety)))
    print("Words:                 {}".format(metadata.word_count))
    print("Answers (correct/all): {}/{}".format(metadata.questions_answered_correctly, metadata.questions_attempted))
    print("Comments:              {}".format(metadata.comments))

def generate_csv(entries, include_header):
    assert all(isinstance(entry, InterlexEntry) for entry in entries)

    csv_output = StringIO()
    writer     = csv.writer(csv_output, dialect = CSV_DIALECT, delimiter = CSV_DELIMITER)

    if include_header:
        header = InterlexEntry._fields
        writer.writerow(header)

    for entry in entries:
        writer.writerow(entry)

    return csv_output.getvalue()

def save_file(output_file_name, content):
    with open(output_file_name, 'wb') as output_file:
        output_file.write(content.encode('utf-8'))

def parse_command_line():
    parser = ArgumentParser(description = "An utility for exporting data from Interlex binary format")

    parser.add_argument(
        help     = "Input files (.ilx format)",
        dest     = 'input_file_paths',
        action   = 'store',
        nargs    = '+',
        type     = str,
    )
    parser.add_argument('-o', '--output',
        help     = "Output file name (.csv format)",
        dest     = 'output_file_path',
        action   = 'store',
        type     = str,
        required = True,
    )
    parser.add_argument('--no-header',
        help     = "Don't include header in the CSV file",
        dest     = 'include_csv_header',
        action   = 'store_false',
    )

    return parser.parse_args()

if __name__ == '__main__':
    command_line_options = parse_command_line()

    file_format = build_interlex_format()

    entry_sets = []
    for input_file_path in command_line_options.input_file_paths:
        parsed_file       = parse(input_file_path, file_format)
        metadata, entries = prepare_data_for_export(input_file_path, parsed_file)

        print_metadata(metadata)
        print()

        entry_sets.append(entries)

    all_entries = list(chain(*entry_sets))
    print("Saving all {} entries in {}".format(len(all_entries), command_line_options.output_file_path))
    save_file(command_line_options.output_file_path, generate_csv(all_entries, include_header = command_line_options.include_csv_header))
