# ANSI Escape Codes

ANSI (American National Standards Institute) Escape Code can be used to control the output of the text in a terminal, such as color, font, cursor position and so on. 

Here are some common ANSI escape codes:

```
Text Formatting:

\033[0m - Reset / Normal
\033[1m - Bold or increased intensity
\033[4m - Underline
\033[5m - Blink
\033[7m - Reverse video (invert the foreground and background colors)
\033[8m - Conceal (not widely supported)

Foreground (Text) Colors:

\033[30m - Black
\033[31m - Red
\033[32m - Green
\033[33m - Yellow
\033[34m - Blue
\033[35m - Magenta
\033[36m - Cyan
\033[37m - White

Background Colors:

\033[40m - Black
\033[41m - Red
\033[42m - Green
\033[43m - Yellow
\033[44m - Blue
\033[45m - Magenta
\033[46m - Cyan
\033[47m - White

Cursor Movements:

\033[#;#H or \033[#;#f - Moves the cursor to line #, column #
\033[#A - Moves the cursor up # lines
\033[#B - Moves the cursor down # lines
\033[#C - Moves the cursor forward # spaces
\033[#D - Moves the cursor backward # spaces

Clean Screen:
\033[2J - Clear entire screen
\033[0J - Clear to end of screen
\033[1J - Clear to beginning of screen
\033[2K - Clear entire line
\033[0K - Clear to end of line
\033[1K - Clear to beginning of line
```

Here is a function output a colorfull loading progress. But not all the terminals support all the ANSI escape codes.

```C
#include <stdio.h>
#include<unistd.h>

int main() {
    // Define the total number of blocks
    char loading[4] = {'|', '/', '-', '\\'};
    printf("Loading: ");
    for (int i = 0; i < 100; i++) {
        // set color
        printf("\033[%dm", i%7 + 30);
        // delete the last character
        printf("\033[1D\033[1P");
        // print the next character
        printf("%c", loading[i % 4]);
        fflush(stdout);
        usleep(200000); // Sleep for 200 milliseconds
    }
    printf("\b Done!\n");
    return 0;
}
```