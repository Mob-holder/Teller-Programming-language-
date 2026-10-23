# Teller's rules and Grammars

# Grammars
 - **Start and End:** Always type `workspace.start` at the beginning and end it with `workspace.end`. 
- **Strings and variables:** You must use variables as `var` inside the scripts and also to print a variable just type the variable name inside the print text. and to connect the variable and the text inside print, then check this example - text.print("You current have"__coins__ "coins !") in this situation __ is used to connect the words with each other and the "coin" is a variable.
- **Linking or connecting words outside of print:** use `:` instead of `and` or to link words. Think this word as `and`.
- **Memory block indexing:** If you do every steps. like at first step you made the variables and stored there info. then after this you'll have to type block[1] or block[2] according to the count of the blocks or the steps. 
- **Strict parameters and parentheses:** Use (*) when the word is required to be filled.

# Teller Rules and Cheat Sheet

1. HOW TO START AND END
workspace.start  =  Turns the code ON (must be on line 1)
workspace.end    =  Turns the code OFF (goes at the very end)

2. HOW TO SAVE INFORMATION
store.var        =  Opens your memory box
var("coins")     =  Saves a number (like: var("coins") = 50)
var("name")      =  Saves a word (like: var("name") = "Ghost")

3. SPECIAL TELLER SYMBOLS
:                =  Means "AND THEN". Chains 2 actions together on one line.
                    Example: load(coins) : add(20)

(*)              =  Means "REQUIRED". If left blank, it causes an error.
                    Example: string1(*)

__word__         =  Shows a saved variable inside your text.
                    Example: text.print("You have "__coins__" coins!")

block[1]         =  Marks Step 1 as finished in memory.
block[2]         =  Marks Step 2 as finished in memory.

4. MAKING CHOICES
if ... then      =  Runs only if the condition is true.
or if ... then   =  Runs if the first check failed.
end              =  Per block steps required per `end` at the end. Each `end` should be under the first `end's` end letter.

5. SHOWING TEXT ON SCREEN
system.console() =  Turns on the screen output.
output(text.string)     =  Sends your text to be printed.
text.print(...)  =  The actual words you want to show.
#                =  A human note. The computer ignores it.


--------------------------------------------------
SAMPLE WORKING SCRIPT:
--------------------------------------------------

workspace.start

    # Step 1: Save data
    store.var {
        var("coins") = 100
        var("player") = "Ghost"
    }
    block[1]

    # Step 2: Add 25 coins using the link (:)
    load(coins) : add(25)
    block[2]

    # Step 3: Print result
    system.console()
    output(text.string) {
        text.print("Welcome back "__player__", you have "__coins__" coins!")
    }
    block[3]

workspace.end


Still in BETA version, more features coming soon!