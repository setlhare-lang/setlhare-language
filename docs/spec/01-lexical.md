# Lexical Structure

> **Status:** Draft · v0.1 milestone

## 1. Source encoding

Source files are UTF-8. The file extension is `.sl`. A byte-order mark, if
present, is ignored.

## 2. Whitespace

The characters U+0020 (space), U+0009 (tab), U+000A (LF), and U+000D (CR)
are whitespace. Whitespace separates tokens; it is otherwise insignificant.

Setlhare is **not** indentation-sensitive.

## 3. Comments

```
LineComment   = "//" { any-char-except-newline }
BlockComment  = "/*" { any-char } "*/"      // may nest
DocComment    = "///" { any-char-except-newline }  // attached to following item
```

## 4. Identifiers

```
Identifier    = ( letter | "_" ) { letter | digit | "_" }
```

Identifiers are case-sensitive. The convention is `snake_case` for values
and functions, `PascalCase` for types, `SCREAMING_SNAKE_CASE` for constants.

## 5. Keywords

Reserved (cannot be used as identifiers):

```
actor   as      break   const   continue  else    enum    false
fn      for     func    if      import    in      let     loop
match   module  mut     new     on        or      pub     return
self    spawn   struct  trait   true      type    use     while
```

(TODO: confirm final keyword set during v0.1 spec freeze.)

## 6. Literals

```
IntLit    = digit { digit | "_" }                  // 1, 1_000_000
HexLit    = "0x" hexdigit { hexdigit | "_" }
BinLit    = "0b" ("0"|"1") { "0"|"1"|"_" }
OctLit    = "0o" octdigit { octdigit | "_" }
FloatLit  = digit { digit | "_" } "." digit { digit | "_" } [ Exp ]
          | digit { digit | "_" } Exp
Exp       = ("e" | "E") [ "+" | "-" ] digit { digit }

StringLit = '"' { string-char | "\\" escape | "#{" expr "}" } '"'
CharLit   = "'" ( char | "\\" escape ) "'"
BoolLit   = "true" | "false"
```

String interpolation `#{expr}` produces a `str` by formatting `expr`'s
`Display` implementation.

## 7. Operators and punctuation

```
+  -  *  /  %  **        // arithmetic
== != <  <= >  >=        // comparison
&& ||  !                 // logical
&  |  ^  ~  <<  >>       // bitwise
=  :=  +=  -=  *=  /=    // assignment
->  =>  ..  ..=  ?  @    // misc
(  )  [  ]  {  }         // grouping
,  ;  :  ::  .           // separators
```

(TODO: pin down precedence table — needed before parser frozen.)
