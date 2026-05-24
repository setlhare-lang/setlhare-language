# Syntax (EBNF)

> **Status:** Draft skeleton · v0.1 milestone · The canonical grammar

This file is the source of truth for Setlhare's grammar. The
hand-written parser in `setlhare/parser/` and the tree-sitter grammar in
`grammar/tree-sitter-setlhare/` must both conform to it.

```ebnf
(* ====== Top level ====== *)
Module       = { Item } ;
Item         = Import
             | FuncDecl
             | StructDecl
             | EnumDecl
             | TraitDecl
             | ImplBlock
             | ActorDecl
             | ConstDecl
             | TypeAlias ;

Import       = "import" ModulePath [ "as" Ident ] ;
ModulePath   = Ident { "::" Ident } ;

(* ====== Declarations ====== *)
FuncDecl     = [ "pub" ] "func" Ident [ Generics ] "(" [ Params ] ")"
               [ "->" Type ] FuncBody ;
FuncBody     = Block | "=>" Expr ;
Params       = Param { "," Param } ;
Param        = Ident ":" Type ;

StructDecl   = [ "pub" ] "struct" Ident [ Generics ] "{" { Field "," } "}" ;
Field        = [ "pub" ] Ident ":" Type ;

EnumDecl     = [ "pub" ] "enum" Ident [ Generics ] "{" { Variant "," } "}" ;
Variant      = Ident [ "(" Type { "," Type } ")" | "{" { Field "," } "}" ] ;

TraitDecl    = [ "pub" ] "trait" Ident [ Generics ] "{" { TraitItem } "}" ;
TraitItem    = FuncSig ";" | FuncDecl ;
ImplBlock    = "impl" [ Generics ] Type [ "for" Type ] "{" { FuncDecl } "}" ;

ActorDecl    = "actor" Ident "{" { ActorItem } "}" ;
ActorItem    = StateDecl | MessageHandler ;
StateDecl    = "state" Ident ":" Type [ "=" Expr ] ;
MessageHandler = "on" Ident "(" [ Params ] ")" [ "->" Type ] Block ;

ConstDecl    = [ "pub" ] "const" Ident ":" Type "=" Expr ";" ;
TypeAlias    = [ "pub" ] "type" Ident [ Generics ] "=" Type ";" ;

(* ====== Generics ====== *)
Generics     = "<" TypeParam { "," TypeParam } ">" ;
TypeParam    = Ident [ ":" TraitBound { "+" TraitBound } ] ;
TraitBound   = Type ;

(* ====== Types ====== *)
Type         = Ident [ "::" Ident ]* [ Generics ]
             | "(" Type { "," Type } ")"
             | "[" Type "]"
             | "&" [ "mut" ] Type
             | "?" Type ;

(* ====== Statements / blocks ====== *)
Block        = "{" { Stmt } [ Expr ] "}" ;
Stmt         = LetStmt | AssignStmt | ExprStmt | ReturnStmt | LoopStmt ;
LetStmt      = ( "let" [ "mut" ] Ident [ ":" Type ] "=" Expr ";" )
             | ( Ident ":=" Expr ";" ) ;
AssignStmt   = LValue ( "=" | "+=" | "-=" | "*=" | "/=" ) Expr ";" ;
ExprStmt     = Expr ";" ;
ReturnStmt   = "return" [ Expr ] ";" ;
LoopStmt     = "while" Expr Block
             | "for" Pattern "in" Expr Block
             | "loop" Block ;

(* ====== Expressions (operator precedence in §1.6) ====== *)
Expr         = (* see precedence table *) ;
Pattern      = (* see types.md §3 *) ;
```

## Operator precedence (highest first)

| Prec | Operators                          | Associativity |
|------|------------------------------------|---------------|
| 14   | `.`  `::`  `(...)` `[...]`         | left  |
| 13   | unary `-`  `!`  `~`  `&` `&mut` `*` | right |
| 12   | `**`                                | right |
| 11   | `*` `/` `%`                         | left  |
| 10   | `+` `-`                             | left  |
| 9    | `<<` `>>`                           | left  |
| 8    | `&`                                 | left  |
| 7    | `^`                                 | left  |
| 6    | `\|`                                | left  |
| 5    | `==` `!=` `<` `<=` `>` `>=`         | none  |
| 4    | `&&`                                | left  |
| 3    | `\|\|`                              | left  |
| 2    | `..` `..=`                          | none  |
| 1    | `?`                                 | postfix |

(TODO: confirm during v0.1 freeze.)
