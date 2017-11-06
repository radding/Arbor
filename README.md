# The Arbor programming language

Arbor is meant to be a pure functional language. 

This is a language created for me, and anyone else, to play with [web assembly](http://webassembly.org/) or language construction. This compiler is written in python to be explicitly more accessible to everyone.

Arbor was first described in my blog post: [Completely Useless Fun Project: Building A New Programming Language](http://yoseph.tech/completely-useless-fun-project-build-a-new-programming-language/). I like challenges and I think this would be a fun one!

If you would like to contribute, I will make a list of issues, you can pick one and work on it. First I need to implement a test suite though, so I would give it a bit.

## Design

### Typing and Assignment
The first thing I wanted was Python like Typing; basically dynamically, but strongly typed. This means an expression like this: `'x' + 1` is invalid and will throw an error, but these two statements are valid: `x = 1; x = 'dd';`. However, to maintain safety, I will also like optional parameter type checking. If you define a functions like so: `(a:int, b:string)` then you would expect a to always be an int and string to always be a string. 

The second thing I decided on was that everything must be assigned. In order to make the language simpler to implement, I did away with any special keywords to define a function. Unlike in Python, JavaScript, or C/C++ a function is inherently anonymous, unless assigned to a variable. The way to define a function would be: `() -> <function body>`. In order to keep that function around you would need to do something like: `foo = () -> <function body>`. Of course, this runs the risk of a programmer accidentally overwriting their function.

To make the language "safer", I decided that every variable had to be declared before you use it. This prevents a programmer,especially one with atrocious spelling like me, from accidentally declaring a variable because of a spelling error in one place. For right now, the only two keywords to define a variable is `let` and `const`. I decided on `const` because it is pretty self explanatory that the variable is constant. Plus C/C++ and Javascript use the `const` keyword, so I think it would be pretty easy for most developers to pick it up. 

The choice of `let` has really nothing to do  with javascript, all though maybe it does a bit. I choose the keyword `let` to more closely align with "math speak" (i.e `let x be a value in universe`). I also chose let because it corresponds to a [lambda abstraction](https://en.wikipedia.org/wiki/Let_expression#Definition){:target="_blank"} and [lambda calculus](https://en.wikipedia.org/wiki/Lambda_calculus){:target='_blank'} is really the foundation of all pure functional languages.

I'm still torn about providing type declarations, such as `int`, `float`, `char`, and `array` because I don't see them as completely necessary. It may be nice to have if for no other reason than it makes the language easier to read. At the same time however, since the type can be inferred from what you are assigning a variable to, and function definitions provide optional type checking, I don't know if this is absolutely necessary. I am leaning towards no, but If I do add support for type declarations, it will be with the `let` keyword, not instead of. 

### Functions Definitions
I also liked the [JavaScript arrow function](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Functions/Arrow_functions){:target="_blank"} syntax (this is part of the reason why arbor has `->` to define functions), and especially the behaviour where a single line means return and a function body means do this whole function body. But at the same time I like Python's no curly brace syntax. So what I did was do something that a lot of other languages do: I defined an end statement. So in Arbor, you would define a function two ways: 

    let foo = (a, b, c) -> a + b + c;

or 

    let foo = (a, b, c) -> 
        return a + b + c;
    done;

Another thing I like about python is the way you can implement default parameters. In arbor it will be done similarly: 

    (a = 1, b = 2) -> a + b;

One thing that a lot of people complain about in Python, and this also trips up people coming from languages such as Java or C/C++, is that you can pass in any type into a function. This could cause issue where you expect a string, but instead receive an int, causing your application to crash. All though this is something you're unit tests should catch, I also wanted to "fix" this with compile time type checking. Plus I think this makes the language that much more descriptive in my mind. If you want type checking and defaults, I think it should look like this: 

    (a:int, b:int = 2) -> a + b;

Taking another principle from Python is packing and unpacking of variables in functions. Similarly to `function(...args)` in es6, python allows you to define lift over params as such: `def foo(a, *args)`. Arbor will do something similar: `foo = (a, b, *args) -> ...`. Then you can call this function like so: `foo(1, 2, 3, 4, 5, 6)`.
And like Python, I also want Arbor to support named leftover variables: `def foo(a, b, **kwargs)`, in arbor would be: `foo = (a, b **kwargs) -> ...`. Where `kwargs` is a dictionary. 

And finally variable unpacking. Python has this really neat concept called unpacking if you have a function definition like 

    def foo(a, b, c, d, e, f, g):
        pass

you can call that function like this: 

    arr = [1, 2, 3, 4, 5, 6, 7]
    foo(*arr)

    # or

    vals = {
        "a": 1,
        "b": 2,
        "c": 3,
        "d": 4,
        "e", 5,
        "f": 6,
        "g": 7 
    }
    foo(**arr)

With default parameters, any parameter not in the dict or array will be the default. I want Arbor to support this exactly the same way:

    foo = (a, b, c, d, e, f, g) -> null;
    arr  = [1, 2, 3, 4, 5, 6, 7];
    foo(*arr)

    // and

    dict = {
        a: 1,
        b: 2,
        c: 3,
        d: 4,
        e: 5,
        f: 6, 
        g: 6,
    }
    foo(**dict)

### Control and flow
In true functional programming fasion, I decided to do away with loops. Instead all loops should be implemented using recursion constructs. Additionally, built in functions such as `forEach`, `map`, `filter`, `fold` or `reduce` will be implemented in order to make implementing loop behaviour easier. 

Additionally, as well as having traditional control flow, `if`, `else`, `else if` statements, I will also have haskell like predicates. These could be similar enough to case statements in Elm. These would look like this:

    (a, b) -> 
        : a > b -> 
            if (a != b)
                return "greater than"
        : a < b -> "less than";
        : true -> "equal to";
    done;

This should be functionally equivalent to 

    (a, b) -> 
        if (a > b): 
            return "greater than";
        else if (a < b):
            return "less than";
        else: 
            return "equal to";
        done;
    done;

And finally, ternary operators. I really like ternary operators. They are elegant and makes code easier to read for small stuff. However, I think JavaScript's and C/C++'s ternary operator leaves something to be desired. I really like Python's ternary operator and that is exactly how ternaries in Arbor should work: `value if <condition> else other value`. 

### Data and Types
The only data types I want to include in Arbor are Integers, Floats, chars, Arrays, and Dictionaries. A string keyword will be available, but, like C/C++, it is really just an array of chars. Arbor will also provide `true` and `false` keywords that is really just 1 and 0 integers. Arbor should have a typedef operator that allows developers to define their own types. This would be similar to how C defines structs:

    Person = type {
        name: string,
        age: int,
        favorites: array
    }

This defines a type so that you can do things like 

    person = instantiate(Person);
    person.name = "yoseph";
    person.age = 22;
    person.favorites = ["programming", "Arbor"]

or 
    
    person = instantiate(Person, name="yoseph", age="22", favorites);

Functions are also first order citizens so that you can pass them as functions or in new types. Types can also refer to themselves, making the type composable and building complex structures like a tree.

## Tooling and the compiler

I haven't decide much on the tooling for Arbor. I know I will implement some standard function like `instantiate` or `new` (haven't decided to be honest), `forEach`, `map`, `reduce`, `filter`, and `resize`. But these may be just standard library stuff, I'm not sure if they will be built ins. 

The one big decision I made in regards to the compiler, and I know I'm going to get shit for this, is that I will implement it in Python initially. This is an experimental language and I only really care about the end result being amazing. I don't much care for the speed of the compiler. Perhaps in the future I will try to implement it in C/C++ or some other language, but not right now. 

The other reason I chose python for my compiler is that it is easy people to set up. Lex and Bison, which every other compiler how to post uses, are frankly a pain to set up, especially for beginners. The lexing and parsing library I use is called [ply](http://www.dabeaz.com/ply/){:target="_blank"} It is a great library that is easy to install (`pip install ply`) and easy to use. Take a look at their documentation and see how easy it is to use!

I really want to make building a programming language less scary. For this, I would need to make the compiler as accessible to beginners as possible, and of course Python is an extremely easy to read and easy to pick up language. 

Another big decision I made, and I will talk about this a bit next week, is that I am going to use an LLVM web assembly backend for actually compiling down into Wasm. This decision was made because LLVM is an incredibly optimized compiler. By only creating the frontend of the compiler, I only have to worry about optimizing the frontend output code, and letting LLVM handle the final optimizations. Additionally, this will also make Arbor easier to port to a new target, such as x86 or ARM. 

The last thing I am going to do is work on the run time. While web assembly is cool, it is still missing some things like the ability to manipulate the DOM. I would have to implement an Arbor to Javascript bridge in order to fully realize the power of Wasm. 

## Running on your machine
Simply run: `pip install -r requirements.txt` I recommend doing this in a [virtual environment](http://docs.python-guide.org/en/latest/dev/virtualenvs/).

The arbor shell script is for the compiler and the `examples/` contain useless although semantically correct Arbor source code to test the compiler.

## Contributing
Not much here yet. I will think about contribution guidelines and think about it later. 
