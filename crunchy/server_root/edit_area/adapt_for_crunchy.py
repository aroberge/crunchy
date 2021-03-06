'''
adapt_for_crunchy.py

by Andre Roberge; feel free to adapt to your own use.

This program takes the "full" version of EditArea (edit_area_full.js)
and adapts it for use with crunchy.  It has been designed for
and tested with EditArea 0.7.2.2.

EditArea comes in various "versions", each with its own strength and
weaknesses.  Unfortunately, the only readable version that works
with crunchy is the "full" version, which is a single file (approx 100kb)
with comments and extra spaces removed - making it nearly impossible
to read, and edit.

adapt_for_crunchy inserts some line breaks to make edit_area_full
easier to read.  It also performs some changes such as changing
the minimum height and adding larger font sizes as options for
displaying on "slides".

adapt_for_crunchy is *not* optimized for speed.  Still, it takes very
little time to run (of the order of 1 second) and speed improvements
would most likely come at the expense of code readability and
flexibility.   Since it is intended to be run "once" by crunchy developpers
(Andre and Johannes) prior to including EditArea in the crunchy distribution,
it would be a waste of effort to change this code for the sake of making
it more efficient.
'''
QUOTE = "'"
DQUOTE = '"'

def break_into_lines(text):
    """
       Breaks the text into lines; a new line begins after a semi-colon
       (not inside a string).

       By uncommenting a few lines of code, it is possible to have strings
       begin on a new line.  This was thought to be useful in making the
       code easier to read, but proved unnecessary so far.
    """
    in_string = False
    all_lines = []
    for line in text:
        new_line = []
        for char in line:
            if in_string:
                new_line.append(char)
                if char == '\\':
                    if escaped:
                        escaped = False
                    else:
                        escaped = True
                elif char == open_quote and not escaped:
                    in_string = False
                    escaped = False
                    # If desired, it is also possible to have strings start
                    # on a new line; to do so, uncomment this code
                    # and the corresponding one below.
                    #total_line = ''.join(new_line)
                    #all_lines.append(total_line)
                    #new_line = []
                elif escaped:
                    escaped = False
            elif char in [QUOTE, DQUOTE]:
                in_string = True
                escaped = False
                open_quote = char
                # If desired, it is also possible to have strings start
                # on a new line; to do so, uncomment this code
                # and the corresponding one above.
                #total_line = ''.join(new_line)
                #all_lines.append(total_line)
                #new_line = []
                new_line.append(char)
            elif char == ';':
                # complete line
                new_line.append(char)
                total_line = ''.join(new_line)
                all_lines.append(total_line)
                new_line = []
            else:
                new_line.append(char)
        total_line = ''.join(new_line)
        if total_line != '\n':
            all_lines.append(total_line)
    return all_lines

def add_font_choices(text):
    """
       Adds larger font size choices, mostly to use when displaying
       EditArea on a 'slide'.  This was motivated by the desire to
       demonstrate Crunchy (and EditArea) at Pycon 2007.
    """

    ### note: this does not do anything with the latest version of editarea
    ## the best way is to edit by hand after running adapt_for_crunchy.

    font_choice = "\"<option value='%d'>%d pt</option>\" +"
    font14 = font_choice%(14, 14)
    font17 = font_choice%(17, 17)
    font20 = font_choice%(20, 20)
    font24 = font_choice%(24, 24)
    font28 = font_choice%(28, 28)
    font32 = font_choice%(32, 32)
    font36 = font_choice%(36, 36)
    for index, line in enumerate(text):
        if font14 in line:
            line = line.replace(font14, font14+font17+font20+font24+font28+
            font32+font36)
            text[index] = line
            return
    return

all_text = open("edit_area_full.js", "rb").readlines()
new_text = break_into_lines(all_text)
##change_minimum_size(new_text)
add_font_choices(new_text)

out = open("edit_area_crunchy.js", "wb")
code = '\n'.join(new_text)
out.write(code)
out.close()
