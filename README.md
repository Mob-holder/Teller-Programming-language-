# Teller's rules and Grammars

Teller File extension - `.tt`
example - `main.tt`
Our Compiler - `https://teller-code-workshop.lovable.app`

# Grammars
 - **Start and End:** Always type `workspace.start` at the beginning and end it with `workspace.end`. 
- **Strings and variables:** You must use variables as `var` inside the scripts and also to print a variable just type the variable name inside the print text. and to connect the variable and the text inside print, then check this example - text.print("You current have"__coins__ "coins !") in this situation __ is used to connect the words with each other and the "coin" is a variable.
- **Linking or connecting words outside of print:** use `:` instead of `and` or to link words. Think this word as `and`.
- **Memory block indexing:** If you do every steps. like at first step you made the variables and stored there info. then after this you'll have to type block[1] or block[2] according to the count of the blocks or the steps. 
- **Strict parameters and parentheses:** Use (*) when the word is required to be filled.

# Teller Rules and Cheat Sheet

# 1. HOW TO START AND END
workspace.start  =  Turns the code ON (must be on line 1)
workspace.end    =  Turns the code OFF (goes at the very end)

# 2. HOW TO SAVE INFORMATION
store.var        =  Opens your memory box
var("coins")     =  Saves a number (like: var("coins") = 50)
var("name")      =  Saves a word (like: var("name") = "Ghost")
var("dmg")       =  Picks random number in range (like: var("dmg") = pick(1, 20))
var("coins") += 10   = In-place addition shorthand
var("hp") -= 5       = In-place subtraction shorthand

array.store {
base("Weapons") = ["Sword", "Bow"]
}
Weapons.store("Axe")  = Adds an item to the array
Weapons.remove(1)     = Removes item at slot 1

# 3. SPECIAL TELLER SYMBOLS
:                =  Means "AND THEN". Chains 2 actions together on one line.
                    Example with numbers: load(coins) : add(20)
                    Example with variables: load(boss_hp) : sub(damage)

(*)              =  Means "REQUIRED". If left blank, it causes an error.
                    Example: string1(*)

__word__         =  Shows a saved variable inside your text.
                    Example: text.print("You have "__coins__" coins!")

__Weapons[1]__   =  Shows slot item from array inside text.
                    Example: text.print("Your slot 1 has "__Weapons[1]__"!")

__Player.hp__    =  Shows entity property inside text.
                    Example: text.print("Health: "__Player.hp__"")

block[1]         =  Marks Step 1 as finished in memory.
block[2]         =  Marks Step 2 as finished in memory.

## ... ##        =  Multi-line comment block (ignored by compiler)

# 4. MAKING CHOICES
if ... then      =  Runs only if the condition is true.
or if ... then   =  Runs if the first check failed.
else then        =  Default fallback when none of the conditions above matched.
end              =  Per block steps required per `end` at the end. Each `end` should be under the first `end's` end letter.

Logic Gates:
&                =  AND gate (Both conditions must be true, e.g. if Level > 5 & Coins >= 20 then)
|                =  OR gate (Either condition can be true, e.g. if Rank == "Admin" | Rank == "Mod" then)
!                =  NOT gate (Inverts condition, e.g. if !Role == "Banned" then)

# 5. SHOWING TEXT ON SCREEN
system.console() =  Turns on the screen output.
output(text.string)     =  Sends your text to be printed.
text.print(...)  =  The actual words you want to show.

text.print("Critical Damage!") {
    load.color("red")
    load.sfx("slash.mp3")
}

# 6. LOOPING 
do text.print("Hello, World!") [1,3] = Will print the text 3 times in the output 

repeat.until boss_hp <= 0 {
    var("dmg") = pick(1, 20)
    var("boss_hp") -= dmg
}

# 7. FUNCTIONS
Functions are like a magical spell.
store.function Player(Health, Age)
store.var {
var.("Health") = 100
var.("Age") = 18
}
return Health
end
  block[1]
Player(Health) 
end
  block[2]
         workspace.end

# 8. INPUT TEXTS
To make any user able to answer the questions in the output console, we use `input.console`
input.console("Enter your age") 

Now to make the number a actual mathematical value we use `number.val`
input.console("Enter your age") # Example - I answered with 17 then
input.console("7") {
number.val [7]
}

The system gave me a interactive question asking for my name. So I entered 17, so now Teller don't know the is it a mathematical value? so if we just type 7+10 then It'll print 710 only. so by typing number.val we'll now able to add 7 with 10 with the result being "17".
Example -

input.console("17") {
number.val [17] : 17+3
text.print("You'll turn" __input.console__ "next year!")
}

For raw word/string input:
input.console("Enter your name:") {
    text.val = [player_name]
}

# 9. ENTITIES & GAME MECHANICS
create Player {
hp = 100
mana = 50
def = 15
}

create Goblin {
hp = 30
dmg = 8
}

goto("DeepCave") = Jumps directly to a target scene or location
delay(s2) = Pauses execution for 2 seconds

event.store("save_slot_1") = Saves game state and variables to memory
event.load("save_slot_1")  = Restores saved game state from memory

--------------------------------------------------
SYMBOLS 
--------------------------------------------------
# 1. Calculation Symbols 

`+`  (Plus)            Adds numbers together
                        Example: 10 + 5  (equals 15)

  `-`   (Minus)           Takes away numbers
                        Example: 10 - 5  (equals 5)

  `*`  (Multiply)        Multiplies numbers (Times)
                        Example: 5 * 2   (equals 10)

  `/`  (Divide)          Divides numbers into parts
                        Example: 10 / 2  (equals 5)

  `=`   (Set / Equals)    Saves a value into a variable
                        Example: var("Coins") = 50

  `+=`  (Add Assign)      Adds to existing variable
                        Example: var("Coins") += 20

  `-=`  (Sub Assign)      Subtracts from existing variable
                        Example: var("Health") -= 15

# 2. Comparison & Gate Symbols

 `>`   (Greater Than)    Left side is bigger than right
                        Example: if Level `>` 10 then

  `<`   (Less Than)       Left side is smaller than right
                        Example: if Level `<` 5 then

  `>=`  (Greater / Equal) Bigger than or exact match
                        Example: if Coins `>=` 100 then

  `<=`  (Less / Equal)    Smaller than or exact match
                        Example: if Health <= 0 then

  `==`  (Exact Match)     Checks if both sides are strictly identical
                        Example: if Name `==` "Ghost" then

  `~=` (Not Equal)       Checks if both sides are different
                        Example: if Rank `~=` "Admin" then

  `&`   (AND)             Both conditions must match
                        Example: if Level > 5 & Coins >= 20 then

  `|`   (OR)              At least one condition matches
                        Example: if Rank == "Admin" | Rank == "Mod" then

  `!`   (NOT)             Inverts check
                        Example: if !Role == "Banned" then

# 3. TELLER GRAMMAT SYMBOLS

 `:`   (Link / And)      Chains two actions on one line
                        Example: load(Coins) : add(25)

  `(*)` (Mandatory)       Field must be filled; cannot be blank
                        Example: string1(*)

  `__`  (Double Under)    Wraps a saved variable to display in text
                        Example: text.print("Level: "__Level__"!")

  `#`   (Comment)         Notes for human eyes; the computer ignores it
                        Example: # This adds gold reward

  `##`  (Multi Comment)   Block comments for multiple lines
                        Example: ## notes ##

  `.`   (Dot Accessor)    Opens a tool inside a system
                        Example: system.console() or workspace.start

  `""`  (Speech Marks)    Wraps plain words/text so it is not read as math
                        Example: "Hello player"

  `()`  (Pouch)           Holds target names or inputs
                        Example: load(Coins)

  `[]`  (Memory Slot)     Labels memory step checkpoints or array index
                        Example: block[1] or __Weapons[1]__

  `{}`  (Room / Scope)    Boxes grouped code together
                        Example: store.var { ... }
--------------------------------------------------
SAMPLE WORKING SCRIPT:
--------------------------------------------------

workspace.start

    create Player {
        hp = 100
        mana = 30
        equipped = "Silver Sword"
    }

    create Boss {
        hp = 80
        name = "Dungeon Golem"
    }

    array.store {
        base("Weapons") = ["Silver Sword", "Longbow"]
    }
    block[1]

    event.store("checkpoint_1")
    block[2]

    repeat.until Boss.hp <= 0 {
        var("player_dmg") = pick(15, 25)
        var("Boss.hp") -= player_dmg
        
        system.console()
        output(text.string) {
            text.print("You swing "__Player.equipped__" for "__player_dmg__" damage!") {
                load.color("red")
                load.sfx("slash.mp3")
            }
        }
        
        delay(s1)

        if Boss.hp > 0 then
            var("boss_dmg") = pick(5, 15)
            var("Player.hp") -= boss_dmg
            output(text.string) {
                text.print("The "__Boss.name__" strikes back dealing "__boss_dmg__" damage!")
            }
            delay(s1)
        end
        else then
            output(text.string) {
                text.print("VICTORY! The "__Boss.name__" crumbles into stone!") {
                    load.color("green")
                }
            }
            Weapons.store("Golem Core")
        end
    }
    block[3]

    output(text.string) {
        text.print("Loot secured! Pocket slot 3 contains: "__Weapons[3]__"")
    }

    delay(s2)
    goto("DeepCave")
    block[4]

workspace.end


Still in BETA version, more features coming soon!
