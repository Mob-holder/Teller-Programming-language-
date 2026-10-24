# Teller's rules and Grammars

Teller File extension - `.tt`
example - `main.tt`
Our Compiler - `https://teller-code-workshop.lovable.app`

# Grammars
 - **Start and End:** Always type `workspace.start` at the beginning and end it with `workspace.end`. 
- **Strings and variables:** You must use variables as `var` inside the scripts and also to print a variable just type the variable name inside the print text. And to connect the variable and the text inside print, check this example - `text.print("You currently have "__coins__" coins!")`. In this situation `__` is used to connect the words with each other and `"coins"` is a variable.
- **Array indexing:** Access items in an array list using square brackets inside double underscores, e.g., `__Weapons[1]__`.
- **Linking or connecting actions:** Use `:` instead of `and` to pipe or link actions on one line (supports both numbers and dynamic variables).
- **Memory block indexing:** If you do every step (like at the first step you made the variables and stored their info), then after this you'll have to type `block[1]` or `block[2]` according to the sequential count of the blocks.
- **Strict parameters and parentheses:** Use `(*)` when the word/parameter is required to be filled.

# Teller Rules and Cheat Sheet

# 1. HOW TO START AND END
workspace.start  =  Turns the code ON (must be on line 1)
workspace.end    =  Turns the code OFF (goes at the very end)

# 2. HOW TO SAVE INFORMATION
store.var        =  Opens your memory box for variables
var("coins")     =  Saves a number (like: var("coins") = 50)
var("name")      =  Saves a word (like: var("name") = "Ghost")

array.store      =  Opens your memory box for lists and collections
base("Weapons")  =  Saves a list of items (like: base("Weapons") = ["Sword", "Bow"])

# 3. SPECIAL TELLER SYMBOLS
:                =  Means "AND THEN". Chains 2 actions together on one line.
                    Example with numbers: load(coins) : add(20)
                    Example with dynamic variables: load(boss_hp) : sub(damage)

(*)              =  Means "REQUIRED". If left blank, it causes an error.
                    Example: string1(*)

__word__         =  Shows a saved variable inside your text.
                    Example: text.print("You have "__coins__" coins!")

__list[index]__  =  Shows an item from a list inside your text.
                    Example: text.print("Equipped: "__Weapons[1]__"")

block[1]         =  Marks Step 1 as finished in memory.
block[2]         =  Marks Step 2 as finished in memory.

# 4. MAKING CHOICES & LOGIC GATES
if ... then      =  Runs only if the condition is true.
or if ... then   =  Runs if the previous check failed but this condition is true.
else then        =  Default fallback when none of the conditions above matched.
end              =  Closes each conditional or function block.

Logic Gates inside conditions:
&                =  AND gate (Both conditions must be true)
                    Example: if Level > 10 & Coins >= 50 then
|                =  OR gate (Either condition can be true)
                    Example: if Rank == "Admin" | Rank == "Mod" then
!                =  NOT gate (Inverts condition / must not match)
                    Example: if !Role == "Banned" then

# 5. SHOWING TEXT ON SCREEN
system.console() =  Turns on the screen output.
output(text.string) = Sends your text to be printed.
text.print(...)  =  The actual words you want to show.

# 6. LOOPING 
do text.print("Hello, World!") [1,3] = Will print the text 3 times in the output.

# 7. FUNCTIONS & RETURN
Functions group reusable instructions and can return dynamic values.

store.function CalculateBonus(Coins)
    store.var {
        var("bonus") = 50
    }
    return bonus
end
block[1]

Player(Health)
block[2]

# 8. INPUT TEXTS & TYPES
To make any user able to answer questions in the output console, we use `input.console`.

A) Numerical Input:
Use `number.val` to cast user input into an actual mathematical number:
input.console("Enter damage amount:") {
    number.val = [damage]
}

B) String / Text Input:
Use `text.val` to save raw written text or names directly into a variable:
input.console("Enter your player name:") {
    text.val = [player_name]
}

--------------------------------------------------
SYMBOLS 
--------------------------------------------------
# 1. Calculation Symbols 

`+`  (Plus)            Adds numbers together
                        Example: 10 + 5  (equals 15)

`-`  (Minus)           Takes away numbers
                        Example: 10 - 5  (equals 5)

`*`  (Multiply)        Multiplies numbers (Times)
                        Example: 5 * 2   (equals 10)

`/`  (Divide)          Divides numbers into parts
                        Example: 10 / 2  (equals 5)

`=`  (Set / Equals)    Saves a value into a variable
                        Example: var("Coins") = 50

# 2. Comparison & Logic Symbols

`>`  (Greater Than)    Left side is bigger than right
                        Example: if Level > 10 then

`<`  (Less Than)       Left side is smaller than right
                        Example: if Level < 5 then

`>=` (Greater / Equal) Bigger than or exact match
                        Example: if Coins >= 100 then

`<=` (Less / Equal)    Smaller than or exact match
                        Example: if Health <= 0 then

`==` (Exact Match)     Checks if both sides are strictly identical
                        Example: if Name == "Ghost" then

`~=` (Not Equal)       Checks if both sides are different
                        Example: if Rank ~= "Admin" then

`&`  (Logical AND)     Both sides must be true
                        Example: if Level > 5 & Coins >= 20 then

`|`  (Logical OR)      At least one side must be true
                        Example: if Coins >= 100 | VIP == "true" then

`!`  (Logical NOT)     Inverts the condition
                        Example: if !Dead == "true" then

# 3. TELLER GRAMMAR SYMBOLS

`:`   (Link / Pipe)     Chains two actions on one line (values or variables)
                        Example: load(BossHP) : sub(damage)

`(*)` (Mandatory)       Field must be filled; cannot be blank
                        Example: string1(*)

`__`  (Double Under)    Wraps a saved variable or list index to display in text
                        Example: text.print("Level: "__Level__"!")

`#`   (Comment)         Notes for human eyes; the computer ignores it
                        Example: # This adds gold reward

`.`   (Dot Accessor)    Opens a tool inside a system
                        Example: system.console() or workspace.start

`""`  (Speech Marks)    Wraps plain words/text so it is not read as math
                        Example: "Hello player"

`()`  (Pouch)           Holds target names or inputs
                        Example: load(Coins)

`[]`  (Memory Slot)     Labels memory step checkpoints or list indices
                        Example: block[1] or __Weapons[1]__

`{}`  (Room / Scope)    Boxes grouped code together
                        Example: store.var { ... } or array.store { ... }

--------------------------------------------------
SAMPLE WORKING SCRIPT:
--------------------------------------------------

workspace.start

    # Step 1: Save base data and inventory
    store.var {
        var("boss_hp") = 100
        var("player") = "Ghost"
    }
    array.store {
        base("Weapons") = ["Sword", "Bow"]
    }
    block[1]

    # Step 2: Take damage input as a number
    input.console("Enter attack damage to deal:") {
        number.val = [damage]
    }
    block[2]

    # Step 3: Deal dynamic variable damage
    load(boss_hp) : sub(damage)
    block[3]

    # Step 4: Display combat results and equipped weapon
    system.console()
    output(text.string) {
        text.print("Player "__player__" attacked with "__Weapons[1]__"!")
        text.print("Remaining Boss HP: "__boss_hp__"")
    }
    block[4]

    # Step 5: Check health status with else fallback
    if boss_hp <= 0 then
        output(text.string) {
            text.print("Status: The boss has been eliminated!")
        }
    end
    else then
        output(text.string) {
            text.print("Status: The boss is still alive!")
        }
    end
    block[5]

workspace.end

Still in BETA version, more features coming soon!
